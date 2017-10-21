from django.core.management.base import BaseCommand, CommandError
from weather.models import Subscription
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string


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
        parser.add_argument(
            '--send_email',
            action='store_true',
            dest='send_email',
            default=False,
            help='Send email to all subscribers',
        )

    def handle(self, *args, **options):
        subs = Subscription.objects.all()
        if options['print_addresses']:
            for sub in subs:
                self.stdout.write(sub.email_address)
            self.stdout.write('Printed all Email Addresses!')
        elif options['print_generated_newsletter']:
            i = 0
            for sub in subs:
                self.stdout.write(sub.generate_newsletter(), ending='\n-----\n')
                i += 1
            self.stdout.write('Printed ' + i.__str__() + ' Newsletters.')

        # messagelist represents the list of tuples that hold (subject, content, from_address, to_address) used forsending an email to a subscriber.
        messagelist = list()
        for sub in subs:
            subject = 'ELEVEN-Its a DEALS kinda day!'
            context = {
                'sub': sub
            }
            content = render_to_string('weather/emailbody.txt', context)
            #content = sub.generate_newsletter()
            from_address = 'weatherDeals@test.com'
            to_addresses = [sub.email_address]
            message = (subject, content, from_address, to_addresses)
            messagelist.append(message)
            self.stdout.write('Prepared email to: ' + sub.email_address)
        datatuple = tuple(messagelist)
        i = send_mass_mail(datatuple, fail_silently=False)
        self.stdout.write('Successfully sent ' + i.__str__() + ' emails.')
