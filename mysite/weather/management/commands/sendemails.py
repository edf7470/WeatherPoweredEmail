from django.core.management.base import BaseCommand, CommandError
from weather.models import Subscription
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
import json


class Command(BaseCommand):
    help = 'Send emails out to all subscribers'

    def add_arguments(self, parser):
        # parser.add_argument('poll_id', nargs='+', type=int)
        parser.add_argument(
            '--print_address',
            action='store_true',
            dest='print_address',
            default=False,
            help='Print all subscribers\' email addresses',
        )
        parser.add_argument(
            '--print_newsletter',
            action='store_true',
            dest='print_newsletter',
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
        parser.add_argument(
            '--print_weather',
            action='store_true',
            dest='print_weather',
            default=False,
            help='Print weather data from subscribers\' locations',
        )

    def handle(self, *args, **options):
        subs = Subscription.objects.all()
        if options['print_address']:
            self.stdout.write('- Printing all Email Addresses.')
            i = 0
            for sub in subs:
                self.stdout.write(sub.email_address)
                i += 1
            self.stdout.write('- Printed ' + i.__str__() + ' Email Addresses.')

        elif options['print_weather']:
            self.stdout.write('- Printing all Weather Data.')
            i = 0
            for sub in subs:
                weather_conditions = sub.get_weather_conditions()
                self.stdout.write(sub.email_address)
                self.stdout.write('Weather: ' + weather_conditions[0])
                self.stdout.write('Temperature: ' + weather_conditions[1].__str__(), ending='\n-----\n')
                i += 1
            self.stdout.write('- Printed ' + i.__str__() + ' subscribers\' Weather Data.')

        elif options['print_newsletter']:
            self.stdout.write('- Printing all Newsletters.')
            i = 0
            for sub in subs:
                weather = sub.get_weather_conditions()[0]
                context = {
                    'sub': sub,
                    'weather': weather,
                }
                content = render_to_string('weather/emailbody.txt', context)
                self.stdout.write(content, ending='\n-----\n')
                i += 1
            self.stdout.write('- Printed ' + i.__str__() + ' Newsletters.')

        elif options['send_email']:
            # messagelist represents the list of tuples that hold (subject, content, from_address, to_address) used forsending an email to a subscriber.
            messagelist = list()
            for sub in subs:
                subject = 'Its a DEALS kinda day!'
                weather = 'sunny'
                context = {
                    'weather': weather,
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
