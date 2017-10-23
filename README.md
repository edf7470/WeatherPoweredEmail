# WeatherPoweredEmail
Klaviyo code challenge!

## Wunderground API key - Time Limitations:
Because the Wunderground key being used only allows 10 API calls per minute, 
the application calls 'sleep' for 7 seconds after each API call as to not exceed the limit. 
This is why the weather app is so slow. 

To upgrade the application to use a better Wunderground key, and allow for less waiting 
time between API calls, edit the settings.py value WUNDERGROUND_KEY


