from decimal import Decimal

from django.db import transaction

from apps.merchants.models import Merchant

from apps.payments.models import Payment, PaymentStatus

from apps.ledger.models import PaymentEvent, EventType

from apps.ledger.services import project_payment_event

from apps.webhooks.models import WebhookOutbox, OutboxStatus

import uuid



def process_payment_creation(merchant: Merchant, amount: Decimal, currency: str, idempotency_key: str = None):

    """
    Atomic Payment Creation Service:
    Creates Payment record, appends PaymentInitiated event to append-only Event Store,
    projects event to CQRS MerchantBalance read model, and writes Transactional Outbox record.
    """

    with transaction.atomic():

        payment = Payment.objects.create(

            merchant=merchant,

            amount=amount,

            currency=currency,

            status=PaymentStatus.INITIATED,

            idempotency_key=idempotency_key

        )



        

        evt = PaymentEvent.objects.create(

            merchant=merchant,

            payment_id=str(payment.id),

            event_type=EventType.PAYMENT_INITIATED,

            amount=amount,

            currency=currency,

            payload={"payment_id": str(payment.id), "status": payment.status}

        )



        

        project_payment_event(evt)



        

        target_url = merchant.webhook_url or "https://webhook.site/mock-endpoint"

        outbox_id = uuid.uuid4()

        outbox_item = WebhookOutbox.objects.create(

            id=outbox_id,

            event_type="payment.initiated",

            target_url=target_url,

            payload={

                "event_id": str(outbox_id),

                "event": "payment.initiated",

                "payment_id": str(payment.id),

                "amount": str(payment.amount),

                "currency": payment.currency,

                "status": payment.status

            },

            status=OutboxStatus.PENDING

        )



        return payment, outbox_item



def process_payment_capture(payment: Payment):

    """
    Atomic Payment Capture Service:
    Updates Payment status to CAPTURED, appends PaymentCaptured event,
    projects to CQRS Read Model, and writes Transactional Outbox record.
    """

    with transaction.atomic():

        payment.status = PaymentStatus.CAPTURED

        payment.save()



        

        evt = PaymentEvent.objects.create(

            merchant=payment.merchant,

            payment_id=str(payment.id),

            event_type=EventType.PAYMENT_CAPTURED,

            amount=payment.amount,

            currency=payment.currency,

            payload={"payment_id": str(payment.id), "status": payment.status}

        )



        

        project_payment_event(evt)



        

        target_url = payment.merchant.webhook_url or "https://webhook.site/mock-endpoint"

        outbox_id = uuid.uuid4()

        outbox_item = WebhookOutbox.objects.create(

            id=outbox_id,

            event_type="payment.captured",

            target_url=target_url,

            payload={

                "event_id": str(outbox_id),

                "event": "payment.captured",

                "payment_id": str(payment.id),

                "amount": str(payment.amount),

                "currency": payment.currency,

                "status": payment.status

            },

            status=OutboxStatus.PENDING

        )



        return payment, outbox_item

