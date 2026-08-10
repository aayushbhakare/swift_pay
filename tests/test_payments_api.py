import pytest

from rest_framework.test import APIClient

from apps.merchants.models import Merchant



@pytest.mark.django_db

def test_merchant_authentication_rejects_invalid_keys():

    client = APIClient()

    payload = {"amount": "100.00", "currency": "USD"}



    

    res1 = client.post('/api/v1/payments/', data=payload, format='json')

    assert res1.status_code == 401



    

    client.credentials(HTTP_X_MERCHANT_KEY="invalid_key_999")

    res2 = client.post('/api/v1/payments/', data=payload, format='json')

    assert res2.status_code == 401



    

    Merchant.objects.create(name="Valid Merchant", api_key="valid_key_123")

    client.credentials(HTTP_X_MERCHANT_KEY="valid_key_123")

    res3 = client.post('/api/v1/payments/', data=payload, format='json')

    assert res3.status_code == 201



@pytest.mark.django_db

def test_payments_api_flow_and_idempotency():

    merchant = Merchant.objects.create(name="Test Merchant", api_key="mch_sec_999")

    client = APIClient()

    client.credentials(HTTP_X_MERCHANT_KEY="mch_sec_999")



    

    idempotency_key = "idempotency_unique_12345"

    payload = {

        "amount": "250.00",

        "currency": "USD"

    }



    res1 = client.post('/api/v1/payments/', data=payload, HTTP_IDEMPOTENCY_KEY=idempotency_key, format='json')

    assert res1.status_code == 201

    payment_id = res1.data['id']

    assert res1.data['status'] == 'INITIATED'



    

    from apps.ledger.models import PaymentEvent

    assert PaymentEvent.objects.filter(payment_id=payment_id).count() == 1



    

    res2 = client.post('/api/v1/payments/', data=payload, HTTP_IDEMPOTENCY_KEY=idempotency_key, format='json')

    assert res2.status_code == 200

    assert res2.data['id'] == payment_id

    

    

    assert res1.data == res2.data



    

    assert PaymentEvent.objects.filter(payment_id=payment_id).count() == 1



    

    res_cap = client.post(f'/api/v1/payments/{payment_id}/capture/', format='json')

    assert res_cap.status_code == 200

    assert res_cap.data['status'] == 'CAPTURED'



    

    res_bal = client.get('/api/v1/merchants/balance/')

    assert res_bal.status_code == 200

    assert res_bal.data['available_balance'] == "250.00"

