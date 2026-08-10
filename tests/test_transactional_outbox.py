import pytest

import requests

from decimal import Decimal

from unittest.mock import patch, MagicMock

from apps.merchants.models import Merchant

from apps.webhooks.models import WebhookOutbox, OutboxStatus

from apps.webhooks.worker import process_outbox_events

from apps.payments.services import process_payment_creation



@pytest.mark.django_db

def test_transactional_outbox_creation_and_worker_delivery():

    merchant = Merchant.objects.create(name="SwiftPay Test", webhook_url="https://merchant.example.com/webhook")



    payment, outbox_item = process_payment_creation(

        merchant=merchant,

        amount=Decimal("50.00"),

        currency="USD",

        idempotency_key="idempotency_key_outbox_test"

    )



    assert WebhookOutbox.objects.filter(id=outbox_item.id).exists()

    outbox = WebhookOutbox.objects.get(id=outbox_item.id)

    assert outbox.status == OutboxStatus.PENDING



    

    with patch("requests.post") as mock_post:

        mock_post.return_value = MagicMock(status_code=200)

        process_outbox_events()



    outbox.refresh_from_db()

    assert outbox.status == OutboxStatus.DELIVERED

    assert mock_post.called





import concurrent.futures

import threading

from django.db import connection



@pytest.mark.django_db(transaction=True)

def test_concurrent_worker_passes_deliver_webhook_exactly_once():

    """
    Two concurrent worker invocations process the same pending outbox row.
    Because of select_for_update(skip_locked=True), only one should actually
    deliver the webhook. The merchant endpoint must receive exactly ONE call.
    """

    merchant = Merchant.objects.create(

        name="Concurrent Webhook Test",

        webhook_url="https://merchant.example.com/webhook"

    )



    payment, outbox_item = process_payment_creation(

        merchant=merchant,

        amount=Decimal("75.00"),

        currency="USD",

        idempotency_key="idempotency_key_concurrent_webhook"

    )



    assert WebhookOutbox.objects.get(id=outbox_item.id).status == OutboxStatus.PENDING



    

    call_count = 0

    call_lock = threading.Lock()



    def counting_post(*args, **kwargs):

        nonlocal call_count

        with call_lock:

            call_count += 1

        

        mock_resp = MagicMock(status_code=200, text="OK")

        return mock_resp



    def run_worker():

        process_outbox_events()

        connection.close()



    

    

    

    with patch("apps.webhooks.worker.requests.post", side_effect=counting_post):

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:

            f1 = executor.submit(run_worker)

            f2 = executor.submit(run_worker)

            concurrent.futures.wait([f1, f2])



    

    assert call_count == 1, f"Expected exactly 1 webhook delivery, got {call_count}"



    outbox_item.refresh_from_db()

    assert outbox_item.status == OutboxStatus.DELIVERED



from datetime import timedelta

from django.utils import timezone



@pytest.mark.django_db

def test_worker_crash_recovery_reclaims_stuck_processing_rows():

    """
    If a worker crashes while a row is in PROCESSING, it should be reclaimed
    and retried if processing_since is older than the timeout (5 minutes).
    """

    merchant = Merchant.objects.create(

        name="Crash Recovery Test", 

        webhook_url="https://merchant.example.com/webhook"

    )

    payment, outbox_item = process_payment_creation(

        merchant=merchant, 

        amount=Decimal("100.00"), 

        currency="USD", 

        idempotency_key="idempotency_key_crash_test"

    )



    

    outbox_item.status = OutboxStatus.PROCESSING

    outbox_item.processing_since = timezone.now() - timedelta(minutes=6)

    outbox_item.save()



    with patch("apps.webhooks.worker.requests.post") as mock_post:

        mock_post.return_value = MagicMock(status_code=200)

        process_outbox_events()



    outbox_item.refresh_from_db()

    assert outbox_item.status == OutboxStatus.DELIVERED

    assert mock_post.called



@pytest.mark.django_db

def test_webhook_payload_contains_stable_event_id_across_retries():

    merchant = Merchant.objects.create(name="Idempotency Webhook Test", webhook_url="https://merchant.example.com/webhook")

    

    payment, outbox_item = process_payment_creation(

        merchant=merchant, amount=Decimal("150.00"), currency="USD", idempotency_key="webhook_idempotency_key"

    )

    

    

    assert 'event_id' in outbox_item.payload

    event_id = outbox_item.payload['event_id']

    assert event_id == str(outbox_item.id)

    

    

    with patch("apps.webhooks.worker.requests.post") as mock_post:

        mock_post.return_value = MagicMock(status_code=500, text="Internal Server Error")

        process_outbox_events()

        

    outbox_item.refresh_from_db()

    assert outbox_item.status == OutboxStatus.FAILED

    assert outbox_item.retry_count == 1

    

    

    outbox_item.next_retry_at = timezone.now() - timedelta(minutes=1)

    outbox_item.save()

    

    

    with patch("apps.webhooks.worker.requests.post") as mock_post:

        mock_post.return_value = MagicMock(status_code=200, text="OK")

        process_outbox_events()

        

    

    call_kwargs = mock_post.call_args.kwargs

    delivered_payload = call_kwargs['json']

    

    

    assert 'event_id' in delivered_payload

    assert delivered_payload['event_id'] == event_id

