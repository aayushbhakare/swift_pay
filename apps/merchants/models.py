import uuid

from decimal import Decimal

from django.db import models



class Merchant(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)

    api_key = models.CharField(max_length=255, unique=True, db_index=True)

    webhook_url = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):

        return f"{self.name} ({self.id})"



class MerchantBalance(models.Model):

    """
    CQRS Read Model: Updated strictly via projections from the append-only Event Store.
    Serves fast read queries without computing aggregate events on every request.
    """

    merchant = models.OneToOneField(Merchant, on_delete=models.CASCADE, related_name='balance')

    available_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    pending_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    currency = models.CharField(max_length=3, default='USD')

    last_updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):

        return f"Balance for {self.merchant.name}: Available=${self.available_balance}, Pending=${self.pending_balance}"

