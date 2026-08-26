from rest_framework import serializers
from swiftpay.merchants.models import Merchant

class MerchantProfileUpdateSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source='name', max_length=255, required=False, allow_null=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone_number = serializers.CharField(read_only=True)
    phone_verified = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Merchant
        fields = [
            'business_name',
            'email',
            'phone_number',
            'phone_verified',
            'trading_name',
            'entity_type',
            'pan',
            'gst',
            'bank_name',
            'account_holder_name',
            'account_number',
            'ifsc_code',
            'business_address',
            'webhook_url'
        ]
