from django.db import models
import requests
from mysite import settings


# Array of tuples lists the "Location" options
TOP_100_CITIES = (
    ("New York, NY", 'NY'),
    ("Chicago", 'CH'),
    ("Dallas, TX", 'DA'),
    ("LosAngeles, CA", 'LA'),
)


class Subscription(models.Model):
    email_address = models.EmailField(verbose_name="Email Address")
    location = models.CharField(max_length=20, choices=TOP_100_CITIES)

    def __str__(self):
        return self.email_address

    #def generate_newsletter(self):
    #    return "Hello " + self.email_address + ",\nNice day out today in " + self.location + "! Enjoy a discount, on us."
    def get_weather_conditions(self):
        state = 'NY'
        city = 'New_York'
        # use python requests to send GET request to wunderground API
        r = requests.get('http://api.wunderground.com/api/' + settings.WUNDERGROUND_KEY + '/conditions/q/' + state + '/' + city + '.json')
        conditions = r.json()
        weather = conditions['current_observation']['weather'].lower()
        temperature = conditions['current_observation']['temp_f']
        return [weather, temperature]


