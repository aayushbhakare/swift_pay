import uuid
from django.db import models
from swiftpay.merchants.models import Merchant

class PaymentStatus(models.TextChoices):
    INITIATED = 'INITIATED', 'Initiated'
    AUTHORIZED = 'AUTHORIZED', 'Authorized'
    CAPTURED = 'CAPTURED', 'Captured'
    SETTLED = 'SETTLED', 'Settled'
    FAILED = 'FAILED', 'Failed'

class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.INITIATED, db_index=True)
    idempotency_key = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    webhook_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} (${self.amount} {self.currency}) - {self.status}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['merchant', 'idempotency_key'],
                name='unique_merchant_idempotency_key'
            )
        ]
