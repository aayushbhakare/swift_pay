from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from swiftpay.payments.models import Payment
from swiftpay.payments.services import process_payment_capture, process_payment_fail
import uuid

@api_view(['GET'])
@permission_classes([AllowAny])
def get_checkout_payment(request, payment_id):
    try:
        payment = Payment.objects.select_related('merchant').get(id=payment_id)
    except (Payment.DoesNotExist, ValidationError):
        return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "id": str(payment.id),
        "amount": str(payment.amount),
        "currency": payment.currency,
        "status": payment.status,
        "merchant_name": payment.merchant.name,
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def process_checkout_payment(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
    except (Payment.DoesNotExist, ValidationError):
        return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

    action = request.data.get('action')
    if action not in ['capture', 'fail']:
        return Response({"error": "Invalid action. Use 'capture' or 'fail'."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if action == 'capture':
            updated_payment = process_payment_capture(payment)
            return Response({"status": updated_payment.status, "message": "Payment captured successfully"}, status=status.HTTP_200_OK)
        elif action == 'fail':
            updated_payment = process_payment_fail(payment, reason="Customer declined via Checkout")
            return Response({"status": updated_payment.status, "message": "Payment declined successfully"}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
