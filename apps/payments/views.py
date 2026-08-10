import json

from django.core.serializers.json import DjangoJSONEncoder

from rest_framework.decorators import api_view

from rest_framework.response import Response

from rest_framework import status

from apps.merchants.models import Merchant

from apps.payments.models import Payment, IdempotencyRecord

from apps.payments.serializers import PaymentCreateSerializer, PaymentDetailSerializer

from apps.payments.services import process_payment_creation, process_payment_capture



@api_view(['POST'])

def create_payment(request):

    api_key = request.META.get('HTTP_X_MERCHANT_KEY')

    merchant = None

    if api_key:

        merchant = Merchant.objects.filter(api_key=api_key).first()

    if not merchant:

        return Response({"error": "Unauthorized: Invalid or missing X-Merchant-Key header."}, status=status.HTTP_401_UNAUTHORIZED)



    idempotency_key = request.META.get('HTTP_IDEMPOTENCY_KEY') or request.headers.get('Idempotency-Key')



    

    if idempotency_key:

        existing_rec = IdempotencyRecord.objects.filter(merchant=merchant, key=idempotency_key).first()

        if existing_rec:

            return Response(existing_rec.response_body, status=existing_rec.status_code)



    serializer = PaymentCreateSerializer(data=request.data)

    if not serializer.is_valid():

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    amount = serializer.validated_data['amount']

    currency = serializer.validated_data.get('currency', 'USD')



    payment, _ = process_payment_creation(

        merchant=merchant,

        amount=amount,

        currency=currency,

        idempotency_key=idempotency_key

    )



    raw_response_data = PaymentDetailSerializer(payment).data

    

    clean_json_data = json.loads(json.dumps(raw_response_data, cls=DjangoJSONEncoder))

    status_code = status.HTTP_201_CREATED



    if idempotency_key:

        IdempotencyRecord.objects.create(

            merchant=merchant,

            key=idempotency_key,

            response_body=clean_json_data,

            status_code=200

        )



    return Response(clean_json_data, status=status_code)



@api_view(['POST'])

def capture_payment(request, payment_id):

    try:

        payment = Payment.objects.get(id=payment_id)

    except Payment.DoesNotExist:

        return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)



    updated_payment, _ = process_payment_capture(payment)

    return Response(PaymentDetailSerializer(updated_payment).data, status=status.HTTP_200_OK)



@api_view(['GET'])

def get_payment(request, payment_id):

    try:

        payment = Payment.objects.get(id=payment_id)

        return Response(PaymentDetailSerializer(payment).data, status=status.HTTP_200_OK)

    except Payment.DoesNotExist:

        return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

