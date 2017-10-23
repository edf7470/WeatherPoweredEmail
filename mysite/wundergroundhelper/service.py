from mysite import settings
import requests
import time


# api_call() is the only method that sends get request to Wunderground.
# Time delay included to ensure staying within limit
#   (10 calls per minute - Developer key - 6.01 second delay)
#   (100 calls per minute - Drizzle key - 0.61 second delay)
#   (1000 calls per mintute - Shower key - 0.07 second delay)
# Do not call this function directly. Use either get_api_history() or get_api_conditions()
def api_call(feature, location_breakdown, extra_data):
    if feature is 'history':
        yyyymmdd = extra_data
        r = requests.get('http://api.wunderground.com/api/' + settings.WUNDERGROUND_KEY +
                     '/history_' + yyyymmdd + '/q/' + location_breakdown[0] + '/' + location_breakdown[1] + '.json')
    elif feature is 'conditions':
        r = requests.get('http://api.wunderground.com/api/' + settings.WUNDERGROUND_KEY +
                     '/conditions/q/' + location_breakdown[0] + '/' + location_breakdown[1] + '.json')
    else:
        return None
    # delay per API call, as to not exceed Wunderground's API call limit per minute
    if settings.WUNDERGROUND_KEY_LEVEL == 'Downpour':
        time.sleep(0.01)
    if settings.WUNDERGROUND_KEY_LEVEL == 'Shower':
        time.sleep(0.07)
    elif settings.WUNDERGROUND_KEY_LEVEL == 'Drizzle':
        time.sleep(0.61)
    else:
        # 'Developer' - free plan
        time.sleep(6.01)
    response_json = r.json()
    return response_json


# Make Wunderground API call to get weather conditions, check that received json data is good, return json or None
# Uses api_call()
def get_api_conditions(location_breakdown):
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
# Uses api_call()
def get_api_history(yyyymmdd, location_breakdown):
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
# Makes ~5 API calls, so execution can be time consuming. Minimize use of this function whenever possible.
def get_average_weather_for_date(date, location_breakdown):
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
