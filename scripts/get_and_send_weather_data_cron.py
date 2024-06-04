import requests
import json
import datetime
import time
import os
import csv
import numpy as np
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.', '.env')
load_dotenv(dotenv_path)

# Load in a CSV list of US cities (currently, about 185 US cities, ranked by population).
with open('./cities.csv', 'r') as f:
    cities = f.read()
# Let's get these into an array.   
cities = cities.split(',')
cities = [s.strip() for s in cities]
cities = np.array(cities)

# Set the OpenWeatherMap API endpoint and load the API key from the local environment (.env). 
openweathermap_url = "http://api.openweathermap.org/data/2.5/weather"
openweathermap_token = os.environ.get('OPENWEATHERMAP_TOKEN')

# Set the Tinybird Events API endpoint and load the API token from the local environment (.env). 
tinybird_url = "https://api.tinybird.co/v0/events?name=incoming_weather_data"
tinybird_token = os.environ.get('TINYBIRD_TOKEN')

locations = []

# This script is called by a cron job. 
# Just run once, looping thru the city names, then quit.
# Loop through each city and get its weather data
for city in cities:
    # Set query parameters for the API request. 
    params = {"q": city, "appid": openweathermap_token, "units": "imperial"} #<-- 'units' should be configurable. #Config

    # Make the API request and get the JSON response
    response = requests.get(openweathermap_url, params=params)
    weather_data = response.json()
    #print(weather_data) 

    # "dt" is the timestamp of the weather snapshot and the number of seconds that have elapsed since January 1, 1970, at 00:00:00 UTC.
    # So, format the timestamp as "%Y-%m-%d %H:%M:%S"
    timestamp = weather_data["dt"]
    dt_object = datetime.datetime.fromtimestamp(timestamp) 
    dt_string = dt_object.strftime("%Y-%m-%d %H:%M:%S")

    # As usual, the 'precip' has some 'special' attributes... OpenWeatherMap does not include this attribute if there is no rain. 
    # In this case, we are after a full time-series, where no zero rain is wanted to have a non-null field.
    # So, default to 0.0.
    precip = 0.0
    if "rain" in weather_data:
        precip = weather_data["rain"]["1h"]

    # Format the weather data as a JSON object. 
    # This is where we are cherry-picking the data we are interested in. 
    # This pre-defines the starting schema used in Tinybird. May be better to cast a wider net and pare down what isn't 
    # wanted later in the Pipes ;) 
    
    print(weather_data["name"])
    print(weather_data["timezone"])
    print(weather_data["coord"]["lon"])
    print(weather_data["coord"]["lat"])

    location_metadata = {
        "site_name": city,
        "site_name_owm": weather_data["name"],
        "lat": weather_data["coord"]["lat"],
        "long": weather_data["coord"]["lon"],
        "timezone": weather_data["timezone"]
    }

    locations.append(location_metadata)
    
    data = {
        "timestamp": dt_string,
        "site_name": city,
        "temp_f": weather_data["main"]["temp"],
        "precip": precip,
        "humidity": weather_data["main"]["humidity"],
        "pressure": weather_data["main"]["pressure"],
        "wind_speed": weather_data["wind"]["speed"],
        "wind_dir": weather_data["wind"]["deg"],
        "clouds": weather_data["clouds"]["all"],
        "description": weather_data["weather"][0]["description"]
    }

    json_data = json.dumps(data)
    
    # Send the JSON object to the Tinybird Events API
    #headers = {"Authorization": f"Bearer {tinybird_token}", "Content-Type": "application/json"}
    #response = requests.post(tinybird_url, headers=headers, data=json_data)
    
    print(f"{json_data}") # This is a prototype afterall ;) 
    
    # Waiting until next request to weather API. In seconds:
    time.sleep(0.25) 



# Specify the file name for the CSV
csv_file_name = "location_data.csv"

# Specify the column headers
fieldnames = ["site_name", "site_name_owm", "lat", "long", "timezone"]

# Open the CSV file in write mode
with open(csv_file_name, mode='w', newline='') as csvfile:
    # Create a CSV writer
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write the headers to the CSV file
    writer.writeheader()

    # Loop through the locations array and write each location's data to the CSV file
    for location in locations:
        writer.writerow({
            "site_name": location["site_name"],
            "lat": location["lat"],
            "long": location["long"],
            "timezone": location["timezone"]
        })

print(f"CSV file '{csv_file_name}' has been created.")
