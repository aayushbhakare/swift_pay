from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from swiftpay.authentication.authentication import APIKeyAuthentication
from django.db import transaction
from swiftpay.merchants.models import Merchant
from swiftpay.payments.models import Payment
from swiftpay.payments.serializers import PaymentCreateSerializer, PaymentDetailSerializer
from swiftpay.payments.services import process_payment_creation, process_payment_capture
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404


from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class PaymentPagination(PageNumberPagination):
    page_size = 10

class PaymentListCreateAPIView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication, APIKeyAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = PaymentPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {'status': ['exact'], 'amount': ['gte', 'lte'], 'created_at': ['gte', 'lte']}
    ordering_fields = ['amount', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PaymentCreateSerializer
        return PaymentDetailSerializer

    def get_queryset(self):
        try:
            merchant = getattr(self.request, 'merchant', self.request.user.merchant)
        except Merchant.DoesNotExist:
            raise PermissionDenied("No merchant associated with this user.")
        return Payment.objects.filter(merchant=merchant)

    def list(self, request, *args, **kwargs):
        if request.query_params.get('export') == 'csv':
            import csv
            from django.http import HttpResponse
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="payments_export.csv"'
            writer = csv.writer(response)
            writer.writerow(['ID', 'Date', 'Amount', 'Currency', 'Status', 'Idempotency Key'])
            for payment in self.filter_queryset(self.get_queryset()):
                writer.writerow([
                    str(payment.id), payment.created_at.isoformat(), str(payment.amount),
                    payment.currency, payment.status, payment.idempotency_key or ''
                ])
            return response
        
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        try:
            merchant = getattr(request, 'merchant', request.user.merchant)
        except Merchant.DoesNotExist:
            return Response({"error": "No merchant associated with this user."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment = process_payment_creation(
            merchant=merchant,
            amount=serializer.validated_data['amount'],
            currency=serializer.validated_data.get('currency', 'INR'),
            idempotency_key=request.META.get('HTTP_IDEMPOTENCY_KEY') or request.headers.get('Idempotency-Key'),
            webhook_url=serializer.validated_data.get('webhook_url')
        )
        return Response(PaymentDetailSerializer(payment).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@authentication_classes([JWTAuthentication, APIKeyAuthentication])
@permission_classes([IsAuthenticated])

def capture_payment(request, payment_id):
    try:
        merchant = getattr(request, 'merchant', request.user.merchant)
    except Merchant.DoesNotExist:
        return Response({"error": "No merchant associated with this user."}, status=status.HTTP_403_FORBIDDEN)

    payment = get_object_or_404(Payment, id=payment_id, merchant=merchant)

    try:
        updated_payment = process_payment_capture(payment)
        return Response(PaymentDetailSerializer(updated_payment).data, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment(request, payment_id):
    try:
        merchant = request.user.merchant
    except Merchant.DoesNotExist:
        return Response({"error": "No merchant associated with this user."}, status=status.HTTP_403_FORBIDDEN)

    payment = get_object_or_404(Payment, id=payment_id, merchant=merchant)
    return Response(PaymentDetailSerializer(payment).data, status=status.HTTP_200_OK)

