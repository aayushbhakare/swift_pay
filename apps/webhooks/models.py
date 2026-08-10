import uuid

from django.db import models

from django.utils import timezone



class OutboxStatus(models.TextChoices):

    PENDING = 'PENDING', 'Pending'

    PROCESSING = 'PROCESSING', 'Processing'

    DELIVERED = 'DELIVERED', 'Delivered'

    FAILED = 'FAILED', 'Failed'



class WebhookOutbox(models.Model):

    """
    Transactional Outbox Table:
    Enables reliable webhook delivery by inserting webhook intent in the exact same DB transaction
    as the payment event update.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    event_type = models.CharField(max_length=100)

    target_url = models.URLField()

    payload = models.JSONField()

    status = models.CharField(max_length=20, choices=OutboxStatus.choices, default=OutboxStatus.PENDING, db_index=True)

    retry_count = models.IntegerField(default=0)

    max_retries = models.IntegerField(default=5)

    next_retry_at = models.DateTimeField(default=timezone.now, db_index=True)

    processing_since = models.DateTimeField(null=True, blank=True, db_index=True)

    last_error = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)



    class Meta:

        ordering = ['created_at']



    def __str__(self):

        return f"OutboxEvent {self.event_type} -> {self.target_url} ({self.status})"

