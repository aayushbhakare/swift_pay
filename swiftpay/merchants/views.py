from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from swiftpay.merchants.models import Merchant, MerchantBalance
from swiftpay.merchants.serializers import MerchantProfileUpdateSerializer

from rest_framework.authtoken.models import Token

from swiftpay.merchants.models import ApiKey
import uuid
import secrets

from django.contrib.auth.hashers import make_password

def _issue_key_pair(merchant):
    if not merchant.user:
        raise ValueError("Merchant has no associated user")
    
    key_id = f"key_{uuid.uuid4().hex[:16]}"
    key_secret = f"sk_live_{secrets.token_hex(24)}"
    
    ApiKey.objects.update_or_create(
        merchant=merchant,
        defaults={'key_id': key_id, 'key_secret': make_password(key_secret)}
    )
    
    return key_id, key_secret

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_merchant_balance(request):
    try:
        merchant = request.user.merchant
    except Merchant.DoesNotExist:
        return Response({"error": "No merchant associated with this user."}, status=status.HTTP_403_FORBIDDEN)

    balance, _ = MerchantBalance.objects.get_or_create(merchant=merchant)
    return Response({
        "merchant_id": str(merchant.id),
        "merchant_name": merchant.name,
        "available_balance": str(balance.available_balance),
        "pending_balance": str(balance.pending_balance),
        "currency": balance.currency,
        "last_updated_at": balance.last_updated_at.isoformat()
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_api_key(request):
    try:
        merchant = request.user.merchant
    except Merchant.DoesNotExist:
        return Response({"error": "No merchant associated with this user."}, status=status.HTTP_403_FORBIDDEN)

    if not merchant.is_profile_complete():
        return Response({"error": "Profile incomplete. Please fill out Business Name, PAN, Bank Details, and IFSC code first."}, status=status.HTTP_400_BAD_REQUEST)

    key_id, key_secret = _issue_key_pair(merchant)
    return Response({"key_id": key_id, "key_secret": key_secret}, status=status.HTTP_201_CREATED)

from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

class MerchantProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MerchantProfileUpdateSerializer

    def get_object(self):
        try:
            return self.request.user.merchant
        except Merchant.DoesNotExist:
            raise PermissionDenied("No merchant associated with this user.")
