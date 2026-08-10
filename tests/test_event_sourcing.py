import pytest

from decimal import Decimal

from apps.merchants.models import Merchant, MerchantBalance

from apps.ledger.models import PaymentEvent, EventType

from apps.ledger.services import project_payment_event



@pytest.mark.django_db

def test_payment_events_update_merchant_balance_cqrs_read_model():

    merchant = Merchant.objects.create(name="Acme Corp", api_key="mch_test_123")

    balance = MerchantBalance.objects.create(merchant=merchant, available_balance=Decimal("0.00"), pending_balance=Decimal("0.00"))



    

    evt_init = PaymentEvent.objects.create(

        merchant=merchant,

        payment_id="pay_001",

        event_type=EventType.PAYMENT_INITIATED,

        amount=Decimal("100.00"),

        currency="USD"

    )

    project_payment_event(evt_init)

    balance.refresh_from_db()

    assert balance.pending_balance == Decimal("100.00")

    assert balance.available_balance == Decimal("0.00")



    

    evt_cap = PaymentEvent.objects.create(

        merchant=merchant,

        payment_id="pay_001",

        event_type=EventType.PAYMENT_CAPTURED,

        amount=Decimal("100.00"),

        currency="USD"

    )

    project_payment_event(evt_cap)

    balance.refresh_from_db()

    assert balance.pending_balance == Decimal("0.00")

    assert balance.available_balance == Decimal("100.00")



    

    evt_settle = PaymentEvent.objects.create(

        merchant=merchant,

        payment_id="pay_001",

        event_type=EventType.PAYMENT_SETTLED,

        amount=Decimal("100.00"),

        currency="USD"

    )

    project_payment_event(evt_settle)

    balance.refresh_from_db()

    assert balance.available_balance == Decimal("0.00")



import concurrent.futures

from django.db import connection



@pytest.mark.django_db(transaction=True)

def test_concurrent_payment_events_no_lost_updates():

    merchant = Merchant.objects.create(name="Concurrent Corp", api_key="mch_conc_123")

    MerchantBalance.objects.create(merchant=merchant, available_balance=Decimal("0.00"), pending_balance=Decimal("0.00"))



    def process_event(i):

        

        

        

        evt = PaymentEvent.objects.create(

            merchant=merchant,

            payment_id=f"pay_conc_{i}",

            event_type=EventType.PAYMENT_INITIATED,

            amount=Decimal("10.00"),

            currency="USD"

        )

        project_payment_event(evt)

        connection.close()



    

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        futures = [executor.submit(process_event, i) for i in range(20)]

        concurrent.futures.wait(futures)



    

    balance = MerchantBalance.objects.get(merchant=merchant)

    

    

    assert balance.pending_balance == Decimal("200.00")

