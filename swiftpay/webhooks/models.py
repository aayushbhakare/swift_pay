import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from swiftpay.merchants.models import Merchant

class OutboxStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    PROCESSING = 'PROCESSING', _('Processing')
    DELIVERED = 'DELIVERED', _('Delivered')
    FAILED = 'FAILED', _('Failed')

class WebhookOutbox(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='webhooks')
    event_type = models.CharField(max_length=255)
    payload = models.JSONField()
    target_url = models.URLField(max_length=1000)
    
    status = models.CharField(
        max_length=20,
        choices=OutboxStatus.choices,
        default=OutboxStatus.PENDING
    )
    
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=5)
    next_retry_at = models.DateTimeField(auto_now_add=True)
    
    last_error = models.TextField(blank=True, null=True)
    processing_since = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'swiftpay_webhook_outbox'
        indexes = [
            models.Index(fields=['status', 'next_retry_at']),
        ]

    def __str__(self):
        return f"Webhook {self.id} for {self.merchant} ({self.status})"
