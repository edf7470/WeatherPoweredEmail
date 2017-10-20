from django.core.management.base import BaseCommand, CommandError
from weather.models import Subscription


class Command(BaseCommand):
    help = 'Send emails out to all subscribers'

    def add_arguments(self, parser):
        # parser.add_argument('poll_id', nargs='+', type=int)
        parser.add_argument(
            '--print_addresses',
            action='store_true',
            dest='print_addresses',
            default=False,
            help='Print all subscription email addresses',
        )
        parser.add_argument(
            '--print_generated_newsletter',
            action='store_true',
            dest='print_generated_newsletter',
            default=False,
            help='Print all generated newsletters with relative email addresses',
        )

    def handle(self, *args, **options):
        subs = Subscription.objects.all()
        if options['print_addresses']:
            for sub in subs:
                self.stdout.write(sub.email_address)
            self.stdout.write('Printed all Email Addresses!')
        elif options['print_generated_newsletter']:
            for sub in subs:
                # self.stdout.write(sub.email_address)
                self.stdout.write(sub.generate_newsletter(), ending='\n-----\n')
            self.stdout.write('Printed all Newsletters!')
