import time

import logging

from django.core.management.base import BaseCommand

from apps.webhooks.worker import process_outbox_events



logger = logging.getLogger('apps.webhooks')



class Command(BaseCommand):

    help = 'Runs the Transactional Outbox Worker process to deliver pending webhooks'



    def add_arguments(self, parser):

        parser.add_argument(

            '--daemon',

            action='store_true',

            help='Run outbox worker continuously as a daemon process'

        )

        parser.add_argument(

            '--interval',

            type=int,

            default=3,

            help='Poll interval in seconds when running in daemon mode (default: 3s)'

        )



    def handle(self, *args, **options):

        is_daemon = options['daemon']

        interval = options['interval']



        if is_daemon:

            self.stdout.write(self.style.SUCCESS(f"Starting SwiftPay Outbox Worker in daemon mode (polling every {interval}s)..."))

            while True:

                try:

                    process_outbox_events()

                except Exception as exc:

                    logger.error(f"Outbox worker encountered error: {exc}")

                time.sleep(interval)

        else:

            self.stdout.write(self.style.SUCCESS("Processing pending outbox webhook events..."))

            process_outbox_events()

            self.stdout.write(self.style.SUCCESS("Outbox process completed."))

