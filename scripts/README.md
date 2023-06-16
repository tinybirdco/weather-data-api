# ``get_and_send_data.py``

Gets data from OpenWeatherMap and posts it to Tinybird via its Events API. 

+ This version is designed to be ran by a scheduler. So, it will run once and quit. 
+ OpenWeatherData details:
  + Requesting fresh weather data every ten minutes.
  + For each run, a list of ~175 US Cities is looped through, and a ``report`` object is constructed from the OpenWeatherMap JSON response.
+ Tinybird details:
  + Each ``report`` is individually posted to the ``incoming_weather_data`` Data Source using the Tinybird Events API.  
+ These URLs are hardcoded:
  + ``http://api.openweathermap.org/data/2.5/weather``
  + ``https://api.tinybird.co/v0/events?name=incoming_weather_data`` 
+ Looks up ``TINYBIRD_TOKEN`` and ``OPENWEATHERMAP_TOKEN`` environmental variables from a ``./config/.env`` file. 
+ There are no command-line arguments.


# ``exercise_api.py``

A tool for testing the weather API. Can be configured to make as many AI requests as you want, can default to 10 requests per minute. 

+ Looks up TINYBIRD_TOKEN environmental variable from a ``./config/.env`` file. 
+ Supports two command-line arguments:

```python
parser.add_argument("--rpm", type=int, default=100, help="Number of requests per minute (default: 10)")
parser.add_argument("endpoint", nargs="?", help="Endpoint for the API URL")
```







