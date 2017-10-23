from django.test import TestCase
from django.template.loader import render_to_string
from weather import models
from .models import Subscription
import datetime


class SubscriptionModelTests(TestCase):

    # Test simplify_api_weather()
    def test_simplify_api_weather_bad(self):
        self.assertEqual(models.simplify_api_weather('sleet'), 'bad', "Sleet should classify as BAD weather.")

    def test_simplify_api_weather_good(self):
        self.assertEqual(models.simplify_api_weather('sunny'), 'good', "Sunny should classify as GOOD weather.")

    def test_simplify_api_weather_neutral(self):
        self.assertEqual(models.simplify_api_weather('partlycloudy'), 'neutral', "Partly Cloudy should classify as NEUTRAL weather.")

    # Test get_location_breakdown()
    def test_get_location_breakdown(self):
        sub = Subscription(email_address='somethingA@gmail.com', location='IL,Chicago')
        location_breakdown = sub.get_location_breakdown()
        expected = ['IL','Chicago']
        self.assertListEqual(location_breakdown, expected, "Good location data should return a list: ['IL', 'Chicago']")

    # Test get_api_conditions()
    def test_get_api_conditions_good_input(self):
        sub = Subscription(email_address='somethingB@gmail.com', location='CA,San_Francisco')
        location_breakdown = sub.get_location_breakdown()
        conditions_json = models.get_api_conditions(location_breakdown)
        display_location_full = conditions_json['current_observation']['display_location']['full']
        self.assertEqual(display_location_full, 'San Francisco, CA', "API call didn't receive expected response.")

    def test_get_api_conditions_bad_state_input_SanFrancisco(self):
        # receives no 'current_observation' item in json
        sub = Subscription(email_address='somethingC@gmail.com', location='XX,San_Francisco')
        location_breakdown = sub.get_location_breakdown()
        conditions_json = models.get_api_conditions(location_breakdown)
        self.assertEqual(conditions_json, None, "Get Conditions should have returned None for a bad location input.")

    def test_get_api_conditions_bad_state_input_NewYork(self):
        # receives a 'current_observation' item in json, but not for correct location
        sub = Subscription(email_address='somethingF@gmail.com', location='XX,New_York')
        location_breakdown = sub.get_location_breakdown()
        conditions_json = models.get_api_conditions(location_breakdown)
        self.assertEqual(conditions_json, None, "Get Conditions should have returned None for a bad location input.")

    def test_get_api_conditions_bad_city_input(self):
        sub = Subscription(email_address='somethingD@gmail.com', location='CA,abcdefg')
        location_breakdown = sub.get_location_breakdown()
        conditions_json = models.get_api_conditions(location_breakdown)
        self.assertEqual(conditions_json, None, "Get Conditions should have returned None for a bad location input.")

    def test_get_api_conditions_bad_both_input_abcdefg(self):
        sub = Subscription(email_address='somethingE@gmail.com', location='XX,abcdefg')
        location_breakdown = sub.get_location_breakdown()
        conditions_json = models.get_api_conditions(location_breakdown)
        self.assertEqual(conditions_json, None, "Get Conditions should have returned None for a bad location input.")

    # Test Subscription.get_weather_conditions()
    def test_get_weather_conditions(self):
        # tested
        sub = Subscription(email_address='somethingG@gmail.com', location='NY,New_York')
        test_weather_conditions = sub.get_weather_conditions()
        # expected
        c_json = models.get_api_conditions(sub.get_location_breakdown())
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

    # Test get_api_history()
    # history - 1
    def test_get_api_history_good_input(self):
        YYYYMMDD = '20161021'
        sub = Subscription(email_address='somethingI@gmail.com', location='TX,Dallas')
        location_breakdown = sub.get_location_breakdown()
        history_json = models.get_api_history(YYYYMMDD, location_breakdown)
        self.assertEqual('64',history_json['history']['dailysummary'][0]['meantempi'])

    # history - 1
    def test_get_api_history_bad_date_input(self):
        YYYYMMDD = '2016102'
        sub = Subscription(email_address='somethingJ@gmail.com', location='TX,Dallas')
        location_breakdown = sub.get_location_breakdown()
        history_json = models.get_api_history(YYYYMMDD, location_breakdown)
        self.assertEqual(None,history_json)

    # Test get_average_weather_for_date()
    # history - 5
    def test_get_average_weather_for_date(self):
        sub = Subscription(email_address='somethingK@gmail.com', location='NY,New_York')
        location_breakdown = sub.get_location_breakdown()
        date = datetime.date(2017, 10, 21)
        tested = models.get_average_weather_for_date(date, location_breakdown)
        expected = 61.2;
        self.assertEqual(tested, expected, "Average temperature not correctly calculated.")

    # history - 0 (possibly more)
    def test_get_average_weather_for_date_bad_date_input(self):
        sub = Subscription(email_address='somethingL@gmail.com', location='NY,New_York')
        location_breakdown = sub.get_location_breakdown()
        date = datetime.date(201, 10, 21)
        tested = models.get_average_weather_for_date(date, location_breakdown)
        expected = None;
        self.assertEqual(tested, expected, "Average temperature not correctly calculated.")

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








