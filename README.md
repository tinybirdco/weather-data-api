# weather-data-api
A demo to illustrate how to go from an API design to implementing (and hosting) it on Tinybird. 

While this example focuses on publishing weather data, the underlying concepts should apply to an other data domain.

## Getting started 

### Set up accounts

+ Go to [OpenWeatherMap](https://openweathermap.org/) and create a [free](https://openweathermap.org/price#weather) account for the "Current Weather and Forecasts" API.
  + Generate an API key. An environmental variable will be set to this key value. 
+ Go to [Tinybird](http://tinybird.co) and create an account with the forever-free Build tier.
  + Reference your Admin Token or create a User Token with read permissions. An environmental variable will be set to this key value.
 
### Create Data Source and build Pipe
+ In Tinybird, create ``incoming_weather_data`` Data Source and ``reports`` Pipe.

### Start up near-real-time weather data feed
+ Set up Python script to load near-real-time OpenWeatherMap data into Tinybird.
  + Configure ./config/.env with the OpenWeatherMap and Tinybird tokens. 
  + Run the ./scripts/get_and_send_data.py script. This script is designed to be used with a 'scheduler', so runs once and quits.
    * Set up scheduler to run script every ten minutes. 
 
For a more details 'recipe' for building your own instance of this weather API, see [this section](). 

## Details

### Weather report data schema

The incoming data feed emits weather `report` objects with the following structure:

```json
{
	"timestamp": "2023-05-04 18:07:08",
	"site_name": "New York City",
	"temp_f": 52.12,
	"precip": 0.0,
	"humidity": 79,
	"pressure": 1017,
	"wind_speed": 10.36,
	"wind_dir": 190,
	"clouds": 100,
	"description": "overcast clouds"
}
```

### Creating Data Source

This Events API request creates a new `incoming_weather_data` Data Source by referencing a `report` JSON object:

```curl
curl \
      -X POST 'https://api.tinybird.co/v0/events?name=incoming_weather_data' \
      -H "Authorization: Bearer {TOKEN}" \
      -d $' {"timestamp": "2023-05-01 12:45:53","site_name": "New York City","temp_f": 59.65,"precip": 0.0,"humidity": 41,"pressure": 994,"wind_speed": 21.85,"wind_dir": 240,"clouds": 100,"description": "overcast clouds"}'
```
## API Endpoint design

### Endpoints 
* One `/reports.json` endpoint that returns weather `report` JSON objects. Out-of-the-box, CSV, Ndjson, and Parquet formats are also available. 

### Query parameters 

The ‘reports’ API Endpoint will support the following query parameters:

* ```start_time``` and ```end_time``` for defining a period of interest. Timestamps are formatted with the “YYYY-MM-DD HH:mm:ss” pattern and are in Coordinated Universal Time (UTC). 
  * If these request parameters are not included, the endpoint will return data from the previous 24 hours. 
  * If end_time is not included in the request, it defaults to the time of the request (i.e. ‘now’). 
  * If only an end_time is included, the start_time will default to 24 hours before the end_time. 
	
* ```city``` for selecting a single city of interest. If not included in the request, data from the entire US will be returned. Values for this parameter are case insensitive.

* ```sensor_type``` for selecting a single type of weather data to return. The following values are supported: temp, precip, wind, humidity, pressure, and clouds. If not used, all weather data types are reported. When ‘wind’ is selected, both speed and direction are returned. 
	
* ```max_results``` for limiting the amount of reports to return in the response. The default value is 1000. 


## Example endpoint requests
To help illustrate how the API Endpoint should work, below are some example requests. The root URL for all of these examples is https://api.tinybird.co/v0/pipes/reports.json. In these examples, just the /reports.json portion is referenced along with the query parameters.

* Requesting the 1,000 most recent reports from all cities since yesterday:  
[/reports.json](https://api.tinybird.co/v0/pipes/reports.json?token=p.eyJ1IjogIjIzYjc5ZGVlLWFmNmItNDNjNS1hNWViLTkzYjNjNzE3ZTdiOCIsICJpZCI6ICJmNWZlYjg3ZS0wM2Q0LTRhN2MtODEwNy00ZDEzZThmNjgxNjMifQ.1i32I7ZMUm6pvZ_DEyu-XasBKKx1XYTEHzF8k4eRAzchttps://api.tinybird.co/v0/pipes/reports.json?max_results=1000&sensor_type=all&token=p.eyJ1IjogIjIzYjc5ZGVlLWFmNmItNDNjNS1hNWViLTkzYjNjNzE3ZTdiOCIsICJpZCI6ICJmNWZlYjg3ZS0wM2Q0LTRhN2MtODEwNy00ZDEzZThmNjgxNjMifQ.1i32I7ZMUm6pvZ_DEyu-XasBKKx1XYTEHzF8k4eRAzc)
* Due to defaults this is equivalent to:  
[/reports.json?max_results=1000&sensor_type=all]([/reports.json?max_results=1000&sensor_type=all](https://api.tinybird.co/v0/pipes/reports.json?max_results=1000&sensor_type=all&token=p.eyJ1IjogIjIzYjc5ZGVlLWFmNmItNDNjNS1hNWViLTkzYjNjNzE3ZTdiOCIsICJpZCI6ICJmNWZlYjg3ZS0wM2Q0LTRhN2MtODEwNy00ZDEzZThmNjgxNjMifQ.1i32I7ZMUm6pvZ_DEyu-XasBKKx1XYTEHzF8k4eRAzchttps://api.tinybird.co/v0/pipes/reports.json?max_results=1000&sensor_type=all&token=p.eyJ1IjogIjIzYjc5ZGVlLWFmNmItNDNjNS1hNWViLTkzYjNjNzE3ZTdiOCIsICJpZCI6ICJmNWZlYjg3ZS0wM2Q0LTRhN2MtODEwNy00ZDEzZThmNjgxNjMifQ.1i32I7ZMUm6pvZ_DEyu-XasBKKx1XYTEHzF8k4eRAzc))

* Requesting reports from the first week of June 2023:  
[/reports.json?start_time=2023-06-01 00:00:00&end_time=2023-06-08 00:00:00](https://api.tinybird.co/v0/pipes/reports.json?start_time=2023-06-01%2000:00:00&end_time=2023-06-08%2000:00:00&token=p.eyJ1IjogIjIzYjc5ZGVlLWFmNmItNDNjNS1hNWViLTkzYjNjNzE3ZTdiOCIsICJpZCI6ICJmNWZlYjg3ZS0wM2Q0LTRhN2MtODEwNy00ZDEzZThmNjgxNjMifQ.1i32I7ZMUm6pvZ_DEyu-XasBKKx1XYTEHzF8k4eRAzchttps://api.tinybird.co/v0/pipes/reports.json?max_results=1000&sensor_type=all&token=p.eyJ1IjogIjIzYjc5ZGVlLWFmNmItNDNjNS1hNWViLTkzYjNjNzE3ZTdiOCIsICJpZCI6ICJmNWZlYjg3ZS0wM2Q0LTRhN2MtODEwNy00ZDEzZThmNjgxNjMifQ.1i32I7ZMUm6pvZ_DEyu-XasBKKx1XYTEHzF8k4eRAzc)

* Requesting full reports from Minneapolis since yesterday:  
[/reports.json?city=minneapolis](https://api.tinybird.co/v0/pipes/reports.json?city=minneapolis&token=p.eyJ1IjogIjIzYjc5ZGVlLWFmNmItNDNjNS1hNWViLTkzYjNjNzE3ZTdiOCIsICJpZCI6ICJmNWZlYjg3ZS0wM2Q0LTRhN2MtODEwNy00ZDEzZThmNjgxNjMifQ.1i32I7ZMUm6pvZ_DEyu-XasBKKx1XYTEHzF8k4eRAzchttps://api.tinybird.co/v0/pipes/reports.json?max_results=1000&sensor_type=all&token=p.eyJ1IjogIjIzYjc5ZGVlLWFmNmItNDNjNS1hNWViLTkzYjNjNzE3ZTdiOCIsICJpZCI6ICJmNWZlYjg3ZS0wM2Q0LTRhN2MtODEwNy00ZDEzZThmNjgxNjMifQ.1i32I7ZMUm6pvZ_DEyu-XasBKKx1XYTEHzF8k4eRAzc)

* Requesting the 1,000 most recent temperatures, over the past day, from all cities:  
[/reports.json?sensor_type=temp](https://api.tinybird.co/v0/pipes/reports.json?sensor_type=temp&token=p.eyJ1IjogIjIzYjc5ZGVlLWFmNmItNDNjNS1hNWViLTkzYjNjNzE3ZTdiOCIsICJpZCI6ICJmNWZlYjg3ZS0wM2Q0LTRhN2MtODEwNy00ZDEzZThmNjgxNjMifQ.1i32I7ZMUm6pvZ_DEyu-XasBKKx1XYTEHzF8k4eRAzchttps://api.tinybird.co/v0/pipes/reports.json?max_results=1000&sensor_type=all&token=p.eyJ1IjogIjIzYjc5ZGVlLWFmNmItNDNjNS1hNWViLTkzYjNjNzE3ZTdiOCIsICJpZCI6ICJmNWZlYjg3ZS0wM2Q0LTRhN2MtODEwNy00ZDEzZThmNjgxNjMifQ.1i32I7ZMUm6pvZ_DEyu-XasBKKx1XYTEHzF8k4eRAzc)

* Request the 100 most recent weather reports from across the US:  
[/reports.json?max_results=100](https://api.tinybird.co/v0/pipes/reports.json?max_results=100&token=p.eyJ1IjogIjIzYjc5ZGVlLWFmNmItNDNjNS1hNWViLTkzYjNjNzE3ZTdiOCIsICJpZCI6ICJmNWZlYjg3ZS0wM2Q0LTRhN2MtODEwNy00ZDEzZThmNjgxNjMifQ.1i32I7ZMUm6pvZ_DEyu-XasBKKx1XYTEHzF8k4eRAzchttps://api.tinybird.co/v0/pipes/reports.json?max_results=1000&sensor_type=all&token=p.eyJ1IjogIjIzYjc5ZGVlLWFmNmItNDNjNS1hNWViLTkzYjNjNzE3ZTdiOCIsICJpZCI6ICJmNWZlYjg3ZS0wM2Q0LTRhN2MtODEwNy00ZDEzZThmNjgxNjMifQ.1i32I7ZMUm6pvZ_DEyu-XasBKKx1XYTEHzF8k4eRAzc)

* Request temperature data for the city of Houston, and for June 16, 2023, midnight to midnight local time (CDT). 
[/reports.json?city=houston&sensor_type=temp&start_time=2023-06-03 05:00:00&end_time=2023-06-04 05:00:00](https://api.tinybird.co/v0/pipes/reports.json?city=houston&sensor_type=temp&start_time=2023-06-16%2006:00:00&end_time=2023-06-17%2006:00:00&token=p.eyJ1IjogIjIzYjc5ZGVlLWFmNmItNDNjNS1hNWViLTkzYjNjNzE3ZTdiOCIsICJpZCI6ICJmNWZlYjg3ZS0wM2Q0LTRhN2MtODEwNy00ZDEzZThmNjgxNjMifQ.1i32I7ZMUm6pvZ_DEyu-XasBKKx1XYTEHzF8k4eRAzchttps://api.tinybird.co/v0/pipes/reports.json?max_results=1000&sensor_type=all&token=p.eyJ1IjogIjIzYjc5ZGVlLWFmNmItNDNjNS1hNWViLTkzYjNjNzE3ZTdiOCIsICJpZCI6ICJmNWZlYjg3ZS0wM2Q0LTRhN2MtODEwNy00ZDEzZThmNjgxNjMifQ.1i32I7ZMUm6pvZ_DEyu-XasBKKx1XYTEHzF8k4eRAzc)

## Recipe for replicating this demo

* Set up accounts
  * OpenWeatherMap
  * Tinybird
	
* Establishing data feed
  * Create Tinybird Data Source referencing report JSON object
  * Set-up, configure and deploy the “get_and_post_data” Python script. 
		
* Build Tinybird Pipe 
  * With CLI
    + Push provided Pipe file to your Workspace
  * With UI
    + Create ‘reports’ Pipe
    + Create Nodes 

* Publish and test API Endpoint

