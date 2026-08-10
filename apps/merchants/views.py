from rest_framework.decorators import api_view

from rest_framework.response import Response

from apps.merchants.models import Merchant, MerchantBalance



@api_view(['GET'])

def get_merchant_balance(request):

    api_key = request.META.get('HTTP_X_MERCHANT_KEY')

    merchant = None

    if api_key:

        merchant = Merchant.objects.filter(api_key=api_key).first()

    if not merchant:

        return Response({"error": "Unauthorized: Invalid or missing X-Merchant-Key header."}, status=401)



    balance, _ = MerchantBalance.objects.get_or_create(merchant=merchant)

    return Response({

        "merchant_id": str(merchant.id),

        "merchant_name": merchant.name,

        "available_balance": str(balance.available_balance),

        "pending_balance": str(balance.pending_balance),

        "currency": balance.currency,

        "last_updated_at": balance.last_updated_at.isoformat()

    })

