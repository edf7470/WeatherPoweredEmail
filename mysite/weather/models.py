from django.db import models
from mysite import settings
import requests
import datetime
import time
import math
import csv
import os
from . import static
# from django.static.loader import render_to_string
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage


TRACK_API_CALLS = False



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


# Helper function to use temperature comparisons and return GOOD/BAD/NEUTRAL
def simplify_api_temp(current_temp, current_date, location_breakdown):
    if TRACK_API_CALLS:
        print('simplify_api_temp')
    average_temp = get_average_weather_for_date(current_date, location_breakdown)
    temp_diff = math.fabs(current_temp - average_temp)
    if (current_temp < average_temp) & (temp_diff >= 5):
        # temperature is colder than average, return BAD
        return BAD
    elif (current_temp > average_temp) & (temp_diff >= 5):
        # temperature is hotter than average, return GOOD
        return GOOD
    else:
        return NEUTRAL


# Use api_call whenever sending get request to Wunderground. Time delay included to ensure staying within limit (10 calls per minute)
def api_call(feature, location_breakdown, extra_data):
    if TRACK_API_CALLS:
        print('api_call')
    if feature is 'history':
        yyyymmdd = extra_data
        r = requests.get('http://api.wunderground.com/api/' + settings.WUNDERGROUND_HISTORY_KEY +
                     '/history_' + yyyymmdd + '/q/' + location_breakdown[0] + '/' + location_breakdown[1] + '.json')
    elif feature is 'conditions':
        r = requests.get('http://api.wunderground.com/api/' + settings.WUNDERGROUND_KEY +
                     '/conditions/q/' + location_breakdown[0] + '/' + location_breakdown[1] + '.json')
    else:
        return None
    # delay 7 seconds per API call, as to not exceed Wunderground's API call limit (10 calls per minute)
    time.sleep(7)
    if TRACK_API_CALLS:
        print('*')
    response_json = r.json()
    return response_json


# Make Wunderground API call to get weather conditions, check that received json data is good, return json or None
def get_api_conditions(location_breakdown):
    if TRACK_API_CALLS:
        print('get_api_conditions')
    conditions_json = api_call('conditions', location_breakdown, '')
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


# Make Wunderground API call to get weather history, check that received json data is good, return json or None
def get_api_history(yyyymmdd, location_breakdown):
    if TRACK_API_CALLS:
        print('get_api_history')
    # check that input is formatted correctly. If not, return None
    if len(yyyymmdd) != 8:
        return None
    # send API get request for history
    history_json = api_call('history', location_breakdown, yyyymmdd)
    try:
        # ensure that the received message is formatted correctly
        test = history_json['history']['dailysummary'][0]['meantempi']
    except KeyError:
        # API return data was bad, possibly due to bad location input. Return None instead of json data.
        history_json = None
    return history_json


# Returns the average temperature (imperial) for the given date and location over the past 5 years (if accessible), else return None
def get_average_weather_for_date(date, location_breakdown):
    if TRACK_API_CALLS:
        print('get_average_weather_for_date')
    year = date.year
    month = date.month
    day = date.day
    running_sum = 0
    year_count = 0
    i = 0
    while i < 5:
        yyyymmdd = ''
        yyyymmdd = yyyymmdd + (year - (1+i)).__str__()
        if month < 10:
            yyyymmdd = yyyymmdd + '0' + month.__str__()
        else:
            yyyymmdd = yyyymmdd + month.__str__()
        if day < 10:
            yyyymmdd = yyyymmdd + '0' + day.__str__()
        else:
            yyyymmdd = yyyymmdd + day.__str__()

        # check that date is formatted correctly. if not, don't call the API. skip this year addition.
        if len(yyyymmdd) != 8:
            history_json = None
        else:
            history_json = get_api_history(yyyymmdd, location_breakdown)
        if history_json is not None:
            temperature = history_json['history']['dailysummary'][0]['meantempi']
            running_sum += float(temperature)
            year_count += 1
        i += 1

    if year_count == 0:
        return None
    else:
        # Calculate average temperature
        average = running_sum/year_count
        return average


TOP_100_CITIES = []


def get_choices_array():
    if len(TOP_100_CITIES) > 1:
        return tuple(TOP_100_CITIES)
    else:
        print("Remaking Top Cities List")
        # generate list to convert to tuple
        TOP_100_CITIES.clear()
        TOP_100_CITIES.append(('', 'Where do you live?'))
        with open(os.path.expanduser(r'C:\Users\filme\PycharmProjects\WeatherPoweredEmail\mysite\weather\static\weather\cities.csv'), 'r') as cities_file:
        #with open(os.path.abspath(r'\mysite\weather\static\weather\cities.csv'), 'r') as cities_file:
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
        conditions_json = get_api_conditions(self.get_location_breakdown())
        if conditions_json is None:
            # fail-safe for bad json data. set weather to NEUTRAL, temperature to NEUTRAL
            w_simple = NEUTRAL
            t_simple = NEUTRAL
        else:
            # find 'weather' value in json response
            weather_api = conditions_json['current_observation']['weather'].lower()
            w_simple = simplify_api_weather(weather_api)
            # find 'temp_f' (temperature fahrenheit) value in json response
            temperature = conditions_json['current_observation']['temp_f']
            current_date = datetime.datetime.now().date()
            t_simple = simplify_api_temp(temperature, current_date, self.get_location_breakdown())
        # return weather (string)(GOOD/BAD/NEUTRAL) and temperature (number/None)
        return [w_simple, t_simple]




