
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from swiftpay.merchants.models import Merchant

def setup_merchant_account(username, email, name):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': name,
        }
    )
    if created:
        user.set_unusable_password()
        user.save()

    merchant, _ = Merchant.objects.get_or_create(
        user=user,
        defaults={
            'name': name,
        }
    )
    return user, merchant, created

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_auth_config(request):
    return Response({
        "google_client_id": settings.GOOGLE_OAUTH_CLIENT_ID
    })

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def google_login(request):
    
    token = request.data.get('id_token')
    if not token:
        return Response(
            {"error": "id_token is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verify the Google ID token
    try:
        idinfo = google_id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_OAUTH_CLIENT_ID
        )
    except ValueError:
        return Response(
            {"error": "Invalid or expired Google token"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Check issuer
    if idinfo.get('iss') not in ('accounts.google.com', 'https://accounts.google.com'):
        return Response(
            {"error": "Invalid token issuer"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    email = idinfo.get('email')
    name = idinfo.get('name', email.split('@')[0])

    if not email:
        return Response(
            {"error": "Email not available in token"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Find or create User + Merchant
    user, merchant, created = setup_merchant_account(
        username=email,
        email=email,
        name=name
    )

    # Issue JWT pair
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'merchant_id': str(merchant.id),
        'merchant_name': merchant.name,
        'email': email,
        'is_new_user': created,
    }, status=status.HTTP_200_OK)

import random
from django.core.cache import cache

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def register_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    business_name = request.data.get('business_name')
    
    if not email or not password or not business_name:
        return Response({"error": "Email, password, and business name are required"}, status=status.HTTP_400_BAD_REQUEST)
        
    if User.objects.filter(username=email).exists():
        return Response({"error": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
    user = User.objects.create_user(username=email, email=email, password=password, first_name=business_name)
    merchant, _ = Merchant.objects.get_or_create(user=user, defaults={'name': business_name})
    
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'merchant_id': str(merchant.id),
        'merchant_name': merchant.name,
    }, status=status.HTTP_201_CREATED)

class MerchantTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        merchant = getattr(self.user, 'merchant', None)
        data['merchant_id'] = str(merchant.id) if merchant else None
        data['merchant_name'] = merchant.name if merchant else None
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MerchantTokenObtainPairSerializer

def normalize_phone(phone: str) -> str:
    import re
    digits = re.sub(r'\D', '', phone or '')
    if not digits:
        raise ValueError("Valid phone number is required")
    return f"+91{digits}" if len(digits) == 10 else f"+{digits}"

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_otp(request):
    try:
        phone = normalize_phone(request.data.get('phone'))
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    otp = str(random.randint(100000, 999999))
    
    # Store OTP in cache for 5 minutes
    cache_key = f'otp_{phone}'
    cache.set(cache_key, otp, timeout=300)
    
    via_whatsapp = str(request.data.get('via_whatsapp', '')).lower() == 'true'
    
    from django.conf import settings
    from twilio.rest import Client
    
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message_body = f"Your SwiftPay OTP is {otp}. Do not share this with anyone."
        if via_whatsapp:
            from_str = f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}"
            to_str = f"whatsapp:{phone}" if not phone.startswith('whatsapp:') else phone
            client.messages.create(body=message_body, from_=from_str, to=to_str)
        else:
            client.messages.create(body=message_body, from_=settings.TWILIO_FROM_NUMBER, to=phone)
    except Exception as e:
        if settings.DEBUG:
            import logging
            logging.getLogger('swiftpay.authentication').info(f"FALLBACK: SMS DELIVERED | TO: {phone} | MESSAGE: Your SwiftPay OTP is {otp}")
        else:
            return Response({"error": "Failed to send OTP. Please check the provided number and try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_phone_otp(request):
    try:
        phone = normalize_phone(request.data.get('phone'))
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    otp = request.data.get('otp')
    if not otp:
        return Response({"error": "OTP is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Verify OTP against cache
    cache_key = f'otp_{phone}'
    cached_otp = cache.get(cache_key)
    
    if not cached_otp or str(cached_otp) != str(otp):
        return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_401_UNAUTHORIZED)
        
    # Clear the OTP from cache
    cache.delete(cache_key)

    merchant = request.user.merchant
    
    if Merchant.objects.filter(phone_number=phone).exclude(id=merchant.id).exists():
        return Response({"error": "This phone number is already registered to another user"}, status=status.HTTP_400_BAD_REQUEST)

    merchant.phone_number = phone
    merchant.phone_verified = True
    merchant.save()

    return Response({
        "message": "Phone number verified successfully"
    }, status=status.HTTP_200_OK)
