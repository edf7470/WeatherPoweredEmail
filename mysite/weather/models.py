from django.db import models
import requests
from mysite import settings


# Array of tuples lists the "Location" options
TOP_100_CITIES = (
    ("NY,New_York", 'New York, NY'),
    ("IL,Chicago", 'Chicago, IL'),
    ("TX,Dallas", 'Dallas, TX'),
    ("CA,Los_Angeles", 'Los Angeles, CA'),
)

GOOD = 'good'
BAD = 'bad'
NEUTRAL = 'neutral'

# Dictionary of wunderground API weather specific condition mapped to 'simple' version (GOOD or BAD)
weather_simple = {
    'sleet': BAD,
    'rain': BAD,
    'snow': BAD,
    'sunny': GOOD,
}


# Helper function to catch weather conditions not included in the weather_simple Dictionary, and set to NEUTRAL.
def simplify_api_weather(weather_api):
    # Get simplified version from Dictionary
    w_simple = weather_simple.get(weather_api)
    # If weather condition wasn't included in Dictionary, set to NEUTRAL
    if w_simple is None:
        w_simple = NEUTRAL
    return w_simple


# Make Wunderground API call to get weather conditions, check that received json data is good, return json or None
def get_api_conditions(location_breakdown):
    r = requests.get('http://api.wunderground.com/api/' + settings.WUNDERGROUND_KEY +
                     '/conditions/q/' + location_breakdown[0] + '/' + location_breakdown[1] + '.json')
    conditions_json = r.json()
    try:
        # Check that all parts of the Subscription location's city name are part of the returned json data
        json_city_name = conditions_json['current_observation']['display_location']['full']
        city_name_part_list = location_breakdown[1].split('_')
        for city_name_part in city_name_part_list:
            if city_name_part not in json_city_name:
                conditions_json = None
    except KeyError:
        # API return data was bad, possibly due to bad location input. Return None instead of json data.
        conditions_json = None
    return conditions_json


class Subscription(models.Model):
    email_address = models.EmailField(verbose_name="Email Address")
    location = models.CharField(max_length=20, choices=TOP_100_CITIES)

    def __str__(self):
        return self.email_address

    def get_location_breakdown(self):
        location_parts = self.location.split(',')
        state = location_parts[0]
        city = location_parts[1]
        return [state,city]

    def get_weather_conditions(self):
        conditions_json = get_api_conditions(self.get_location_breakdown())
        if conditions_json is None:
            # fail-safe for bad json data. set weather to NEUTRAL, temperature to None
            weather = NEUTRAL
            temperature = None
        else:
            # find 'weather' value in json response
            weather_api = conditions_json['current_observation']['weather'].lower()
            weather = simplify_api_weather(weather_api)
            # find 'temp_f' (temperature fahrenheit) value in json response
            temperature = conditions_json['current_observation']['temp_f']
        # return weather (string)(GOOD/BAD/NEUTRAL) and temperature (number/None)
        return [weather, temperature]




