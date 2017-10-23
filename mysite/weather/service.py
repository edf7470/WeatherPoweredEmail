import wundergroundhelper.service
import math
import os
import csv

TOP_100_CITIES = []

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
    average_temp = wundergroundhelper.service.get_average_weather_for_date(current_date, location_breakdown)
    temp_diff = math.fabs(current_temp - average_temp)
    if (current_temp < average_temp) & (temp_diff >= 5):
        # temperature is colder than average, return BAD
        return BAD
    elif (current_temp > average_temp) & (temp_diff >= 5):
        # temperature is hotter than average, return GOOD
        return GOOD
    else:
        return NEUTRAL


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
