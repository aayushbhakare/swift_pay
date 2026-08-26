from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from swiftpay.merchants.models import Merchant

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_MERCHANT_KEY')
        if not api_key:
            return None
        
        merchant = Merchant.lookup_by_api_key(api_key)
        if not merchant:
            raise AuthenticationFailed('Invalid API Key')
        
        
        if merchant.user:
            request.merchant = merchant
            return (merchant.user, api_key)
        
        raise AuthenticationFailed('API Key not associated with a user')
