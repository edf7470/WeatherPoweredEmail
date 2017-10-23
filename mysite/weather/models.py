from django.db import models
#from wundergroundhelper import service
#from weather.service import simplify_api_weather, simplify_api_temp, GOOD, BAD, NEUTRAL
#from weather import service
import weather.service
import wundergroundhelper.service
import datetime

TRACK_API_CALLS = False


class Subscription(models.Model):
    email_address = models.EmailField(verbose_name="Email Address")
    location = models.CharField(max_length=20, choices=weather.service.get_choices_array())

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
        conditions_json = wundergroundhelper.service.get_api_conditions(self.get_location_breakdown())
        if conditions_json is None:
            # fail-safe for bad json data. set weather & temp (simple) to NEUTRAL, weather & temp (value) to None
            w_simple = weather.service.NEUTRAL
            t_simple = weather.service.NEUTRAL
            w_value = None
            t_value = None
        else:
            # find 'weather' value in json response
            w_value = conditions_json['current_observation']['weather'].lower()
            w_simple = weather.service.simplify_api_weather(w_value)
            # find 'temp_f' (temperature fahrenheit) value in json response
            t_value = conditions_json['current_observation']['temp_f']
            current_date = datetime.datetime.now().date()
            t_simple = weather.service.simplify_api_temp(t_value, current_date, self.get_location_breakdown())
        # return weather (string)(GOOD/BAD/NEUTRAL) and temperature (number/None)
        return [w_simple, t_simple, w_value, t_value]




