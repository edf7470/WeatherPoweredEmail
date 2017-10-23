# WeatherPoweredEmail
Klaviyo code challenge!

## Running the Weather App:
\WeatherPoweredEmail\mysite>python manage.py runserver

In an internet browser, enter: http://127.0.0.1:8000/weather/

## Wunderground API key - Time Limitations:
Because the Wunderground key being used only allows 10 API calls per minute, 
the application calls 'sleep' for 7 seconds after each API call as to not exceed the limit. 
This is why the weather app is so slow. 

To upgrade the application to use a better Wunderground key, and allow for less waiting 
time between API calls, edit the settings.py value WUNDERGROUND_KEY

## Good vs Bad Weather Logic:
Looking at emailbody.txt, I decided that the weather conditions (rainy/snowy/sunny) were more 
important than the temperature difference, in regards to the decision about how nice the day is. 

My reasoning for this decision is based on the following scenarios:
- If it is raining/snowing/sleet, it doesn't really matter the temperature out. It's a "bad weather day."
- If it is a winter day in upstate NY, it's cold out regardless of the average temperature, but if it's sunny out, it's still a "good weather day."

A possibly better way to classify days as "good weather days" or "bad weather days" would be based on the individual's personal 
preference, and/or seasonal circumstances. 
- If someone doesn't like the heat, any summer day is "too hot."
- In southern CA, a summer day that is 5 degrees hotter than the average might actually be considered a "bad weather day" because of the undearable heat. 

Given these circumstances, 5 degrees warmer than the average would be considered a "good weather day" in the winter, but a "bad weather day" in the summer.

## Weather App Automated Tests:
To run the Weather app automated test suite (It will take a few minutes to complete), execute the command:
\WeatherPoweredEmail\mysite>python manage.py test weather

## Django Management Command:
To generate newsletters and send them out as emails:

\WeatherPoweredEmail\mysite>python manage.py sendemails

To generate newsletters and send them out as emails, with data printed, choose any combination 
of the 'print' options (--print_all includes address, weather, newsletter:

\WeatherPoweredEmail\mysite>python manage.py sendemails [--print_address] [--print_weather] [--print_newsletter] [--print_all]
 
To generate and view newsletters for subscribers, but don't send the emails out:

\WeatherPoweredEmail\mysite>python manage.py sendemails --no_send --print_all





