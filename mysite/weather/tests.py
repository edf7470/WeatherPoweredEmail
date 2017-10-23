from django.test import TestCase
from django.template.loader import render_to_string
from weather import models
from .models import Subscription
import datetime
from wundergroundhelper import service


class SubscriptionModelTests(TestCase):

    # Test simplify_api_weather()
    def test_simplify_api_weather_bad(self):
        self.assertEqual(models.simplify_api_weather('sleet'), 'bad', "Sleet should classify as BAD weather.")

    def test_simplify_api_weather_good(self):
        self.assertEqual(models.simplify_api_weather('sunny'), 'good', "Sunny should classify as GOOD weather.")

    def test_simplify_api_weather_neutral(self):
        self.assertEqual(models.simplify_api_weather('partlycloudy'), 'neutral', "Partly Cloudy should classify as NEUTRAL weather.")

    # Test Subscription.get_location_breakdown()
    def test_get_location_breakdown(self):
        sub = Subscription(email_address='somethingA@gmail.com', location='IL,Chicago')
        location_breakdown = sub.get_location_breakdown()
        expected = ['IL','Chicago']
        self.assertListEqual(location_breakdown, expected, "Good location data should return a list: ['IL', 'Chicago']")



    # Test Subscription.get_weather_conditions()
    def test_get_weather_conditions(self):
        # tested
        sub = Subscription(email_address='somethingG@gmail.com', location='NY,New_York')
        test_weather_conditions = sub.get_weather_conditions()
        # expected
        c_json = service.get_api_conditions(sub.get_location_breakdown())
        if c_json is None:
            # fail-safe for bad json data. set weather to NEUTRAL, temperature to None
            w_simple = 'neutral'
            t_simple = None
        else:
            # find 'weather' value in json response
            weather_api = c_json['current_observation']['weather'].lower()
            w_simple = models.simplify_api_weather(weather_api)
            # find 'temp_f' (temperature fahrenheit) value in json response
            temperature = c_json['current_observation']['temp_f']
            current_date = datetime.datetime.now().date()
            t_simple = models.simplify_api_temp(temperature, current_date, sub.get_location_breakdown())
        expected = [w_simple, t_simple, weather_api, temperature]
        self.assertAlmostEqual(test_weather_conditions[3],expected[3],delta=1)
        self.assertEqual(test_weather_conditions[0], expected[0])
        self.assertEqual(test_weather_conditions[1], expected[1])
        self.assertEqual(test_weather_conditions[2], expected[2])

    def test_get_weather_conditions_bad_state_input(self):
        sub = Subscription(email_address='somethingH@gmail.com', location='XX,New_York')
        weather_conditions = sub.get_weather_conditions()
        expected = ['neutral', 'neutral', None, None]
        self.assertListEqual(weather_conditions, expected, "Bad location input should return a list: ['neutral', 'neutral', None, None]")


    # Test simplify_api_temp()
    def test_simplify_api_temp_bad(self):
        current_temp = 10
        current_date = datetime.date(2016, 7, 1)
        sub = Subscription(email_address='somethingM@gmail.com', location='NY,New_York')
        location_breakdown = sub.get_location_breakdown()
        t_simple = models.simplify_api_temp(current_temp, current_date, location_breakdown)
        self.assertEqual(t_simple, 'bad')

    def test_simplify_api_temp_good(self):
        current_temp = 100
        current_date = datetime.date(2016, 1, 1)
        sub = Subscription(email_address='somethingN@gmail.com', location='NY,New_York')
        location_breakdown = sub.get_location_breakdown()
        t_simple = models.simplify_api_temp(current_temp, current_date, location_breakdown)
        self.assertEqual(t_simple, 'good')

    # Test emailsubject.txt
    def test_emailsubject_txt_bad_bad(self):
        weather_conditions = ['bad', 'bad']
        subject_context = {
            'weather': weather_conditions[0],
            'temp': weather_conditions[1],
        }
        subject = render_to_string('weather/emailsubject.txt', subject_context).strip()
        self.assertTrue('Not so nice out?' in subject)

    def test_emailsubject_txt_bad_good(self):
        weather_conditions = ['bad', 'good']
        subject_context = {
            'weather': weather_conditions[0],
            'temp': weather_conditions[1],
        }
        subject = render_to_string('weather/emailsubject.txt', subject_context).strip()
        self.assertTrue('Not so nice out?' in subject)

    def test_emailsubject_txt_bad_neutral(self):
        weather_conditions = ['bad', 'neutral']
        subject_context = {
            'weather': weather_conditions[0],
            'temp': weather_conditions[1],
        }
        subject = render_to_string('weather/emailsubject.txt', subject_context).strip()
        self.assertTrue('Not so nice out?' in subject)

    def test_emailsubject_txt_good_good(self):
        weather_conditions = ['good', 'good']
        subject_context = {
            'weather': weather_conditions[0],
            'temp': weather_conditions[1],
        }
        subject = render_to_string('weather/emailsubject.txt', subject_context).strip()
        self.assertTrue('It\'s nice out!' in subject)

    def test_emailsubject_txt_good_bad(self):
        weather_conditions = ['good', 'bad']
        subject_context = {
            'weather': weather_conditions[0],
            'temp': weather_conditions[1],
        }
        subject = render_to_string('weather/emailsubject.txt', subject_context).strip()
        self.assertTrue('It\'s nice out!' in subject)


    def test_emailsubject_txt_good_neutral(self):
        weather_conditions = ['good', 'neutral']
        subject_context = {
            'weather': weather_conditions[0],
            'temp': weather_conditions[1],
        }
        subject = render_to_string('weather/emailsubject.txt', subject_context).strip()
        self.assertTrue('It\'s nice out!' in subject)

    def test_emailsubject_txt_neutral_neutral(self):
        weather_conditions = ['neutral', 'neutral']
        subject_context = {
            'weather': weather_conditions[0],
            'temp': weather_conditions[1],
        }
        subject = render_to_string('weather/emailsubject.txt', subject_context).strip()
        self.assertTrue('Not so nice out?' not in subject)
        self.assertTrue('It\'s nice out!' not in subject)

    def test_emailsubject_txt_neutral_bad(self):
        weather_conditions = ['neutral', 'bad']
        subject_context = {
            'weather': weather_conditions[0],
            'temp': weather_conditions[1],
        }
        subject = render_to_string('weather/emailsubject.txt', subject_context).strip()
        self.assertTrue('Not so nice out?' in subject)

    def test_emailsubject_txt_neutral_good(self):
        weather_conditions = ['neutral', 'good']
        subject_context = {
            'weather': weather_conditions[0],
            'temp': weather_conditions[1],
        }
        subject = render_to_string('weather/emailsubject.txt', subject_context).strip()
        self.assertTrue('It\'s nice out!' in subject)








