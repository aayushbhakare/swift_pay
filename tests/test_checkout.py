import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from swiftpay.merchants.models import Merchant, MerchantBalance
from swiftpay.payments.models import Payment, PaymentStatus
from decimal import Decimal

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def merchant():
    user = User.objects.create(username='merchant@example.com')
    merchant = Merchant.objects.create(user=user, name='Checkout Test Merchant')
    MerchantBalance.objects.create(merchant=merchant)
    return merchant

@pytest.fixture
def payment(merchant):
    return Payment.objects.create(
        merchant=merchant,
        amount=Decimal('100.00'),
        currency='INR'
    )

@pytest.mark.django_db
def test_get_checkout_payment(api_client, payment):
    response = api_client.get(f'/api/v1/payments/checkout/{payment.id}/')
    assert response.status_code == 200
    assert response.data['amount'] == '100.00'
    assert response.data['merchant_name'] == 'Checkout Test Merchant'
    assert response.data['status'] == PaymentStatus.INITIATED

@pytest.mark.django_db
def test_process_checkout_payment_capture(api_client, payment):
    response = api_client.post(
        f'/api/v1/payments/checkout/{payment.id}/process/',
        data={'action': 'capture'},
        format='json'
    )
    assert response.status_code == 200
    assert response.data['status'] == PaymentStatus.CAPTURED
    
    payment.refresh_from_db()
    assert payment.status == PaymentStatus.CAPTURED
    
    balance = MerchantBalance.objects.get(merchant=payment.merchant)
    assert balance.available_balance == Decimal('100.00')

@pytest.mark.django_db
def test_process_checkout_payment_fail(api_client, payment):
    response = api_client.post(
        f'/api/v1/payments/checkout/{payment.id}/process/',
        data={'action': 'fail'},
        format='json'
    )
    assert response.status_code == 200
    assert response.data['status'] == PaymentStatus.FAILED
    
    payment.refresh_from_db()
    assert payment.status == PaymentStatus.FAILED
