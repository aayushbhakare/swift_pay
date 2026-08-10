from decimal import Decimal

from django.db import transaction

from apps.merchants.models import MerchantBalance

from apps.ledger.models import PaymentEvent, EventType



def project_payment_event(event: PaymentEvent):

    """
    CQRS Projection Handler: Applies append-only payment events to the MerchantBalance read model.
    Uses select_for_update for pessimistic lock to ensure consistency under high concurrency.
    """

    with transaction.atomic():

        balance, _ = MerchantBalance.objects.select_for_update().get_or_create(

            merchant=event.merchant,

            defaults={'currency': event.currency, 'available_balance': Decimal('0.00'), 'pending_balance': Decimal('0.00')}

        )



        amount = Decimal(str(event.amount))

        pending = Decimal(str(balance.pending_balance))

        available = Decimal(str(balance.available_balance))



        if event.event_type == EventType.PAYMENT_INITIATED:

            balance.pending_balance = pending + amount

        elif event.event_type == EventType.PAYMENT_CAPTURED:

            if pending >= amount:

                balance.pending_balance = pending - amount

            balance.available_balance = available + amount

        elif event.event_type == EventType.PAYMENT_FAILED:

            if pending >= amount:

                balance.pending_balance = pending - amount

        elif event.event_type == EventType.PAYMENT_SETTLED:

            if available >= amount:

                balance.available_balance = available - amount



        balance.save()

        return balance

