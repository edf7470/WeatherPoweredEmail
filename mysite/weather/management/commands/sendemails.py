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
            '--print_all',
            action='store_true',
            dest='print_all',
            default=False,
            help='Print address, newsletter, weather.',
        )
        parser.add_argument(
            '--print_address',
            action='store_true',
            dest='print_address',
            default=False,
            help='Print all subscribers\' email addresses.',
        )
        parser.add_argument(
            '--print_newsletter',
            action='store_true',
            dest='print_newsletter',
            default=False,
            help='Print all generated newsletters.',
        )
        parser.add_argument(
            '--print_weather',
            action='store_true',
            dest='print_weather',
            default=False,
            help='Print weather data (weather condition & temperature) from subscribers\' locations.',
        )
        parser.add_argument(
            '--no_send',
            action='store_true',
            dest='no_send',
            default=False,
            help='Print data, without sending emails out.',
        )

    def handle(self, *args, **options):
        print_formatting = True
        if options['print_all']:
            options['print_address'] = True
            options['print_weather'] = True
            options['print_newsletter'] = True

        if not options['print_all'] and not options['print_address'] and not options['print_weather'] and not options['print_newsletter']:
            print_formatting = False

        if not options['no_send']:
            messagelist = list()
        if print_formatting:
            self.stdout.write('----------------------------------')
        i = 0
        subs = Subscription.objects.all()
        for sub in subs:
            weather_conditions = sub.get_weather_conditions()
            context = {
                'sub': sub,
                'weather': weather_conditions,
            }
            content = render_to_string('weather/emailbody.txt', context)
            subject_context = {
                'weather': weather_conditions,
            }
            subject = render_to_string('weather/emailsubject.txt', subject_context).strip()
            if options['print_address']:
                # email address
                self.stdout.write('Email Address: ' + sub.email_address)
            if options['print_weather']:
                # weather
                self.stdout.write('Weather: ' + weather_conditions[0])
                self.stdout.write('Temperature: ' + weather_conditions[1].__str__())
            if options['print_newsletter']:
                # Newsletter
                self.stdout.write('Newsletter:')
                self.stdout.write('Content:')
                self.stdout.write(content)
                self.stdout.write('Subject:')
                self.stdout.write(subject)
            if not options['no_send']:
                # send email
                from_address = 'weatherDeals@test.com'
                to_addresses = [sub.email_address]
                message = (subject, content, from_address, to_addresses)
                messagelist.append(message)
                self.stdout.write('Prepared email to: ' + sub.email_address)
            if print_formatting:
                self.stdout.write('----------------------------------')
            i += 1
        if not options['no_send']:
            datatuple = tuple(messagelist)
            i = send_mass_mail(datatuple, fail_silently=False)
            self.stdout.write('Successfully sent ' + i.__str__() + ' emails.')
        elif print_formatting:
            self.stdout.write('Printed data for ' + i.__str__() + ' Subscriptions.')
