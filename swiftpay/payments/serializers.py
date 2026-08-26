from decimal import Decimal
from rest_framework import serializers
from swiftpay.payments.models import Payment

class PaymentCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
    currency = serializers.CharField(max_length=3, default='INR')
    webhook_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)


class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'merchant_id', 'amount', 'currency', 'status', 'idempotency_key', 'created_at', 'updated_at']


