from decimal import Decimal
from django.db import transaction
from swiftpay.merchants.models import Merchant, MerchantBalance
from swiftpay.payments.models import Payment, PaymentStatus
from swiftpay.webhooks.models import WebhookOutbox, OutboxStatus
import uuid

def process_payment_creation(merchant: Merchant, amount: Decimal, currency: str, idempotency_key: str = None):
    with transaction.atomic():
        payment = Payment.objects.create(
            merchant=merchant,
            amount=amount,
            currency=currency,
            status=PaymentStatus.INITIATED,
            idempotency_key=idempotency_key
        )
        
        balance, _ = MerchantBalance.objects.select_for_update().get_or_create(merchant=merchant)
        balance.pending_balance += amount
        balance.save()
        
        target_url = merchant.webhook_url or "https://webhook.site/mock-endpoint"
        outbox_id = uuid.uuid4()
        outbox_item = WebhookOutbox.objects.create(
            id=outbox_id,
            merchant=merchant,
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

        return payment

def process_payment_capture(payment: Payment):
    with transaction.atomic():
        locked_payment = Payment.objects.select_for_update().get(id=payment.id)
        if locked_payment.status not in [PaymentStatus.INITIATED, PaymentStatus.AUTHORIZED]:
            raise ValueError(f"Payment cannot be captured from status {locked_payment.status}")
            
        locked_payment.status = PaymentStatus.CAPTURED
        locked_payment.save()
        
        payment.status = PaymentStatus.CAPTURED 

        balance = MerchantBalance.objects.select_for_update().get(merchant=payment.merchant)
        balance.pending_balance -= payment.amount
        balance.available_balance += payment.amount
        balance.save()
        
        target_url = payment.merchant.webhook_url or "https://webhook.site/mock-endpoint"
        outbox_id = uuid.uuid4()
        outbox_item = WebhookOutbox.objects.create(
            id=outbox_id,
            merchant=payment.merchant,
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

        return payment

def process_payment_fail(payment: Payment, reason: str = "Failed"):
    with transaction.atomic():
        locked_payment = Payment.objects.select_for_update().get(id=payment.id)
        if locked_payment.status not in [PaymentStatus.INITIATED, PaymentStatus.AUTHORIZED]:
            raise ValueError(f"Payment cannot be failed from status {locked_payment.status}")
            
        locked_payment.status = PaymentStatus.FAILED
        locked_payment.save()
        
        payment.status = PaymentStatus.FAILED 

        balance = MerchantBalance.objects.select_for_update().get(merchant=payment.merchant)
        balance.pending_balance -= payment.amount
        balance.save()
        
        target_url = payment.merchant.webhook_url or "https://webhook.site/mock-endpoint"
        outbox_id = uuid.uuid4()
        outbox_item = WebhookOutbox.objects.create(
            id=outbox_id,
            merchant=payment.merchant,
            event_type="payment.failed",
            target_url=target_url,
            payload={
                "event_id": str(outbox_id),
                "event": "payment.failed",
                "payment_id": str(payment.id),
                "amount": str(payment.amount),
                "currency": payment.currency,
                "status": payment.status,
                "reason": reason
            },
            status=OutboxStatus.PENDING
        )

        return payment
