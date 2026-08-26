import pytest
from django.contrib.auth.models import User
from django.test import Client
from swiftpay.merchants.models import Merchant
from rest_framework_simplejwt.tokens import RefreshToken

@pytest.fixture
def api_client():
    return Client()

@pytest.mark.django_db
def test_update_merchant_profile_with_new_fields(api_client):
    user = User.objects.create(username='test@example.com', email='test@example.com')
    merchant = Merchant.objects.create(user=user, name='Test Merchant')
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    payload = {
        "business_name": "New Legal Name",
        "trading_name": "Swift Trade",
        "entity_type": "private_limited",
        "pan": "ABCDE1234F",
        "gst": "22AAAAA0000A1Z5",
        "bank_name": "HDFC Bank",
        "account_holder_name": "John Doe",
        "account_number": "1234567890",
        "ifsc_code": "HDFC0001234",
        "business_address": "123 Tech Park"
    }
    
    response = api_client.patch(
        '/api/v1/merchants/profile/', 
        data=payload,
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['business_name'] == "New Legal Name"
    assert data['trading_name'] == "Swift Trade"
    assert data['pan'] == "ABCDE1234F"
    
    merchant.refresh_from_db()
    assert merchant.name == "New Legal Name"
    assert merchant.trading_name == "Swift Trade"
    assert merchant.entity_type == "private_limited"
    assert merchant.pan == "ABCDE1234F"
    assert merchant.gst == "22AAAAA0000A1Z5"
    assert merchant.bank_name == "HDFC Bank"
    assert merchant.account_holder_name == "John Doe"
    assert merchant.account_number == "1234567890"
    assert merchant.ifsc_code == "HDFC0001234"
    assert merchant.business_address == "123 Tech Park"
