from django.test import TestCase
from weather.models import Subscription
from wundergroundhelper import service
import datetime


class WundergroundHelperServiceTests(TestCase):

    # Test get_api_conditions()
    def test_get_api_conditions_good_input(self):
        sub = Subscription(email_address='somethingB@gmail.com', location='CA,San_Francisco')
        location_breakdown = sub.get_location_breakdown()
        conditions_json = service.get_api_conditions(location_breakdown)
        display_location_full = conditions_json['current_observation']['display_location']['full']
        self.assertEqual(display_location_full, 'San Francisco, CA', "API call didn't receive expected response.")

    def test_get_api_conditions_bad_state_input_SanFrancisco(self):
        # receives no 'current_observation' item in json
        sub = Subscription(email_address='somethingC@gmail.com', location='XX,San_Francisco')
        location_breakdown = sub.get_location_breakdown()
        conditions_json = service.get_api_conditions(location_breakdown)
        self.assertEqual(conditions_json, None, "Get Conditions should have returned None for a bad location input.")

    def test_get_api_conditions_bad_state_input_NewYork(self):
        # receives a 'current_observation' item in json, but not for correct location
        sub = Subscription(email_address='somethingF@gmail.com', location='XX,New_York')
        location_breakdown = sub.get_location_breakdown()
        conditions_json = service.get_api_conditions(location_breakdown)
        self.assertEqual(conditions_json, None, "Get Conditions should have returned None for a bad location input.")

    def test_get_api_conditions_bad_city_input(self):
        sub = Subscription(email_address='somethingD@gmail.com', location='CA,abcdefg')
        location_breakdown = sub.get_location_breakdown()
        conditions_json = service.get_api_conditions(location_breakdown)
        self.assertEqual(conditions_json, None, "Get Conditions should have returned None for a bad location input.")

    def test_get_api_conditions_bad_both_input_abcdefg(self):
        sub = Subscription(email_address='somethingE@gmail.com', location='XX,abcdefg')
        location_breakdown = sub.get_location_breakdown()
        conditions_json = service.get_api_conditions(location_breakdown)
        self.assertEqual(conditions_json, None, "Get Conditions should have returned None for a bad location input.")

    # Test get_api_history()
    def test_get_api_history_good_input(self):
        yyyymmdd = '20161021'
        sub = Subscription(email_address='somethingI@gmail.com', location='TX,Dallas')
        location_breakdown = sub.get_location_breakdown()
        history_json = service.get_api_history(yyyymmdd, location_breakdown)
        self.assertEqual('64',history_json['history']['dailysummary'][0]['meantempi'])

    def test_get_api_history_bad_date_input(self):
        yyyymmdd = '2016102'
        sub = Subscription(email_address='somethingJ@gmail.com', location='TX,Dallas')
        location_breakdown = sub.get_location_breakdown()
        history_json = service.get_api_history(yyyymmdd, location_breakdown)
        self.assertEqual(None,history_json)

    # Test get_average_weather_for_date()
    def test_get_average_weather_for_date(self):
        sub = Subscription(email_address='somethingK@gmail.com', location='NY,New_York')
        location_breakdown = sub.get_location_breakdown()
        date = datetime.date(2017, 10, 21)
        tested = service.get_average_weather_for_date(date, location_breakdown)
        expected = 61.2;
        self.assertEqual(tested, expected, "Average temperature not correctly calculated.")

    def test_get_average_weather_for_date_bad_date_input(self):
        sub = Subscription(email_address='somethingL@gmail.com', location='NY,New_York')
        location_breakdown = sub.get_location_breakdown()
        date = datetime.date(201, 10, 21)
        tested = service.get_average_weather_for_date(date, location_breakdown)
        expected = None;
        self.assertEqual(tested, expected, "Average temperature not correctly calculated.")
