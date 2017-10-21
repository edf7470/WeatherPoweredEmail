from django.utils import timezone
from django.test import TestCase
from weather import models
from .models import Subscription


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
            weather = 'neutral'
            temperature = None
        else:
            # find 'weather' value in json response
            weather_api = c_json['current_observation']['weather'].lower()
            weather = models.simplify_api_weather(weather_api)
            # find 'temp_f' (temperature fahrenheit) value in json response
            temperature = c_json['current_observation']['temp_f']
        expected = [weather, temperature]
        self.assertListEqual(test_weather_conditions, expected, "Good location input should return [weather, temperature]")

    def test_get_weather_conditions_bad_state_input(self):
        sub = Subscription(email_address='somethingG@gmail.com', location='XX,New_York')
        weather_conditions = sub.get_weather_conditions()
        expected = ['neutral', None]
        self.assertListEqual(weather_conditions, expected, "Bad location input should return a list: ['neutral', None]")









