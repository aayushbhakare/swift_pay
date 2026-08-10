import logging

import requests

from datetime import timedelta

from django.utils import timezone

from django.db import transaction

from django.db.models import Q

from apps.webhooks.models import WebhookOutbox, OutboxStatus



logger = logging.getLogger('apps.webhooks')



def process_outbox_events():

    """
    Background Outbox Delivery Worker:
    Fetches PENDING or retryable FAILED webhook events and dispatches HTTP POST payloads.
    Uses select_for_update(skip_locked=True) to atomically claim each row, preventing
    duplicate delivery when multiple worker instances run concurrently.
    Uses exponential backoff on delivery failure.
    """

    now = timezone.now()

    stuck_timeout = now - timedelta(minutes=5)



    

    

    eligible_ids = list(

        WebhookOutbox.objects.filter(

            Q(status__in=[OutboxStatus.PENDING, OutboxStatus.FAILED], next_retry_at__lte=now, retry_count__lt=5) |

            Q(status=OutboxStatus.PROCESSING, processing_since__lt=stuck_timeout)

        ).values_list('id', flat=True)[:50]

    )



    for event_id in eligible_ids:

        

        

        

        with transaction.atomic():

            event = (

                WebhookOutbox.objects

                .select_for_update(skip_locked=True)

                .filter(id=event_id)

                .filter(

                    Q(status__in=[OutboxStatus.PENDING, OutboxStatus.FAILED]) |

                    Q(status=OutboxStatus.PROCESSING, processing_since__lt=stuck_timeout)

                )

                .first()

            )

            if event is None:

                

                continue



            

            event.status = OutboxStatus.PROCESSING

            event.processing_since = timezone.now()

            event.save(update_fields=['status', 'processing_since'])



        

        

        try:

            logger.info(f"Delivering Webhook {event.id} ({event.event_type}) to {event.target_url}")

            response = requests.post(

                event.target_url,

                json=event.payload,

                headers={"Content-Type": "application/json", "X-Webhook-Event": event.event_type},

                timeout=5

            )

            if response.status_code in [200, 201, 202, 204]:

                event.status = OutboxStatus.DELIVERED

                event.last_error = None

                event.processing_since = None

                event.save(update_fields=['status', 'last_error', 'processing_since'])

                logger.info(f"Webhook {event.id} delivered successfully.")

            else:

                handle_failure(event, f"HTTP Status {response.status_code}: {response.text}")

        except Exception as exc:

            handle_failure(event, str(exc))



def handle_failure(event: WebhookOutbox, error_msg: str):

    event.retry_count += 1

    event.last_error = error_msg

    if event.retry_count >= event.max_retries:

        event.status = OutboxStatus.FAILED

        logger.error(f"Webhook {event.id} failed permanently after {event.retry_count} attempts.")

    else:

        event.status = OutboxStatus.FAILED

        

        backoff_seconds = 2 ** event.retry_count

        event.next_retry_at = timezone.now() + timedelta(seconds=backoff_seconds)

        logger.warning(f"Webhook {event.id} failed. Retrying in {backoff_seconds}s (Attempt {event.retry_count}).")

    event.processing_since = None

    event.save(update_fields=['retry_count', 'last_error', 'status', 'next_retry_at', 'processing_since'])



