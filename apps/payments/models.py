import uuid

from django.db import models

from apps.merchants.models import Merchant



class PaymentStatus(models.TextChoices):

    INITIATED = 'INITIATED', 'Initiated'

    AUTHORIZED = 'AUTHORIZED', 'Authorized'

    CAPTURED = 'CAPTURED', 'Captured'

    FAILED = 'FAILED', 'Failed'



class Payment(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='payments')

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    currency = models.CharField(max_length=3, default='USD')

    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.INITIATED, db_index=True)

    idempotency_key = models.CharField(max_length=255, blank=True, null=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):

        return f"Payment {self.id} (${self.amount} {self.currency}) - {self.status}"



class IdempotencyRecord(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)

    key = models.CharField(max_length=255, db_index=True)

    response_body = models.JSONField()

    status_code = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)



    class Meta:

        unique_together = ('merchant', 'key')



    def __str__(self):

        return f"IdempotencyRecord {self.key} -> Code {self.status_code}"

