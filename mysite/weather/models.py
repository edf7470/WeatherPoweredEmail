from django.db import models
import datetime
import time
import math
import csv
import os
from wundergroundhelper import service

TRACK_API_CALLS = False


GOOD = 'good'
BAD = 'bad'
NEUTRAL = 'neutral'

# Dictionary of wunderground API weather specific condition mapped to 'simple' version (GOOD or BAD)
weather_simple = {
    'sleet': BAD,
    'rain': BAD,
    'light rain': BAD,
    'snow': BAD,
    'sunny': GOOD,
}


# Helper function to catch weather conditions not included in the weather_simple Dictionary, and set to NEUTRAL.
def simplify_api_weather(w_value):
    # Get simplified version from Dictionary
    w_simple = weather_simple.get(w_value)
    # If weather condition wasn't included in Dictionary, set to NEUTRAL
    if w_simple is None:
        w_simple = NEUTRAL
    return w_simple


# Helper function to use temperature comparisons and return GOOD/BAD/NEUTRAL
def simplify_api_temp(current_temp, current_date, location_breakdown):
    if TRACK_API_CALLS:
        print('simplify_api_temp')
    average_temp = service.get_average_weather_for_date(current_date, location_breakdown)
    temp_diff = math.fabs(current_temp - average_temp)
    if (current_temp < average_temp) & (temp_diff >= 5):
        # temperature is colder than average, return BAD
        return BAD
    elif (current_temp > average_temp) & (temp_diff >= 5):
        # temperature is hotter than average, return GOOD
        return GOOD
    else:
        return NEUTRAL


TOP_100_CITIES = []


def get_choices_array():
    if len(TOP_100_CITIES) > 1:
        return tuple(TOP_100_CITIES)
    else:
        # generate list to convert to tuple
        TOP_100_CITIES.clear()
        TOP_100_CITIES.append(('', 'Where do you live?'))
        full_path = os.path.dirname(os.path.realpath(__file__)) + '\static\weather\cities.csv'
        with open(os.path.abspath(full_path), 'r') as cities_file:
            reader = csv.reader(cities_file)
            for row in reader:
                new_item = (row[0]+','+row[1], row[3]+' - '+row[2])
                TOP_100_CITIES.append(new_item)
        return tuple(TOP_100_CITIES)


class Subscription(models.Model):
    email_address = models.EmailField(verbose_name="Email Address")
    location = models.CharField(max_length=20, choices=get_choices_array())

    def __str__(self):
        return self.email_address

    def get_location_breakdown(self):
        location_parts = self.location.split(',')
        state = location_parts[0]
        city = location_parts[1]
        return [state,city]

    def get_weather_conditions(self):
        if TRACK_API_CALLS:
            print('get_weather_conditions')
        conditions_json = service.get_api_conditions(self.get_location_breakdown())
        if conditions_json is None:
            # fail-safe for bad json data. set weather & temp (simple) to NEUTRAL, weather & temp (value) to None
            w_simple = NEUTRAL
            t_simple = NEUTRAL
            w_value = None
            t_value = None
        else:
            # find 'weather' value in json response
            w_value = conditions_json['current_observation']['weather'].lower()
            w_simple = simplify_api_weather(w_value)
            # find 'temp_f' (temperature fahrenheit) value in json response
            t_value = conditions_json['current_observation']['temp_f']
            current_date = datetime.datetime.now().date()
            t_simple = simplify_api_temp(t_value, current_date, self.get_location_breakdown())
        # return weather (string)(GOOD/BAD/NEUTRAL) and temperature (number/None)
        return [w_simple, t_simple, w_value, t_value]




