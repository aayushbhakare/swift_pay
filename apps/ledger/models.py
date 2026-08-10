import uuid

from django.db import models

from apps.merchants.models import Merchant



class EventType(models.TextChoices):

    PAYMENT_INITIATED = 'PaymentInitiated', 'Payment Initiated'

    PAYMENT_AUTHORIZED = 'PaymentAuthorized', 'Payment Authorized'

    PAYMENT_CAPTURED = 'PaymentCaptured', 'Payment Captured'

    PAYMENT_FAILED = 'PaymentFailed', 'Payment Failed'

    PAYMENT_SETTLED = 'PaymentSettled', 'Payment Settled'



class PaymentEvent(models.Model):

    """
    Append-Only Event Store (Write Model)
    Events are immutable records of historical facts that occurred in the system.
    """

    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    payment_id = models.CharField(max_length=255, db_index=True)

    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='ledger_events')

    event_type = models.CharField(max_length=50, choices=EventType.choices, db_index=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    currency = models.CharField(max_length=3, default='USD')

    payload = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)



    class Meta:

        ordering = ['created_at']



    def __str__(self):

        return f"[{self.event_type}] Payment:{self.payment_id} Amount:{self.amount} {self.currency}"

