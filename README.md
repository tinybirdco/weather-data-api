# weather-data-api
A demo to illustrate how to go from an API design to implementing (and hosting) it on Tinybird. 

While this example focuses on publishing weather data, the underlying concepts should apply to an other data domain.

There are a lot of moving pieces, but here is a general outline of the resources provided:
* Python script for getting weather data from OpenWeatherMap and posting it to a Tinybird Data Source.
* How-tos for creating a ``incoming_weather_data`` Data Source and a ``reports`` Pipe. 
* Python script for making requests to the weather API ``reports`` endpoint.  

## Getting started 

You can start by making a clone or fork of this repository. 

Next, you will need to create Tinybird and OpenWeatherMap accounts, create a Tinybird Data Source and Pipe, then crank up your weather data feed. When all that is in place, you will be all set to launch your own weather API.

### Set up accounts

+ Go to [OpenWeatherMap](https://openweathermap.org/) and create a [free](https://openweathermap.org/price#weather) account for the "Current Weather and Forecasts" API.
  + Generate an API key. An environmental variable will be set to this key value. 
+ Go to [Tinybird](http://tinybird.co) and create an account with the forever-free Build tier.
  + Reference your Admin Token or create a User Token with read permissions. An environmental variable will be set to this key value.
 
### Create Data Source and build Pipe
+ In Tinybird, create ``incoming_weather_data`` Data Source and ``reports`` Pipe.
  + See below for details on creating these. When it comes to creating the Pipe, the Tinybird command-line interface (CLI) comes highly recommended. With it you can automate the process by pushing a provide Pipe definition file, rather than manually building the Pipe in the user interface (UI) by setting up three Nodes.  	

### Start up near-real-time weather data feed
+ Set up Python script to load near-real-time OpenWeatherMap data into Tinybird.
  + Configure ./config/.env with the OpenWeatherMap and Tinybird tokens. 
  + Run the ./scripts/get_and_send_data.py script. This script is designed to be used with a 'scheduler', so runs once and quits.
    * Set up scheduler to run script every ten minutes. 
 
When you are ready to build, this [checklist]() may help for rolling out your instance.

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
## API design

### API Endpoints 
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

## Nodes 

The ``reports`` Pipe is has three Nodes:

+ Node 1: Filtering by the city and time period of interest
+ Node 2: Selecting the sensor report type
+ Node 3: Applying the ‘max results’ parameter to limit the number of report objects in the response

These Nodes are designed to be applied in this order, and the final Node is used to generate API Endpoint responses. 

### Node 1 named ``city_and_period_of_interest``

Applying ``city``, ``start_time``, and ``end_time`` query parameters. This is a case where we pull in every field (SELECT \*) and do not take this opportunity to drop fields. The fields arriving via the Event API have already been curated by a Python script. 

```sql
%
SELECT *
FROM incoming_weather_data
WHERE
    1=1
     {% if defined(city) %}
        AND lowerUTF8(site_name) LIKE lowerUTF8({{ String(city, description="Name of US City to get data for. Data is available for the 175 most populated cities in the US. Optional and defaults to all cities.") }})
     {% end %}
     {% if defined(start_time) and defined(end_time) %}
         AND toDateTime(timestamp) BETWEEN {{ DateTime(start_time, description="'YYYY-MM-DD HH:mm:ss'. UTC. Optional and defaults to 24 hours ago. Defines the start of the period of interest. ") }} AND {{ DateTime(end_time, description="'YYYY-MM-DD HH:mm:ss'. UTC. Optional and defaults to time of request. Defines the end of the period of interest.") }}
     {% end %}
     {% if not defined(start_time) and not defined(end_time) %}
        AND toDateTime(timestamp) BETWEEN addDays(now(),-1) AND now()
     {% end %}
     {% if defined(start_time) and not defined(end_time) %}
         AND toDateTime(timestamp) BETWEEN {{ DateTime(start_time) }} AND now()
     {% end %}
     {% if not defined(start_time) and defined(end_time) %}
         AND toDateTime(timestamp) BETWEEN addDays(toDateTime({{DateTime(end_time)}}),-1) AND {{ DateTime(end_time) }}
     {% end %}
ORDER BY timestamp DESC
```
### Node 2 named ``select_sensor_type``

Here we support the ``sensor_type`` query parameter. When used, just that data type is selected, along with the timestamp and site_name attributes. Note that 'wind' is a special case and two data types are returned (speed and direction). "Special cases" often result in confusion and 'special' code, so this should be updated to have separate wind_dir and wind_vel as sensor_type otpions. 

```sql
%
WITH
{{ String(sensor_type, 'all', description="Type of weather data to return. Default is all types. Available types: 'temp', 'precip', 'wind', 'humidity', 'pressure', and 'clouds'. Wind returns both velocity and direction paramters. Units: temperature (F), precip (inches per hour), wind (mph and degrees) humidity (%), pressure (hPa), clouds (% coverage), ")}}

SELECT
    timestamp,
    site_name,
    {% if defined(sensor_type) and sensor_type == 'temp' %} temp_f
    {% elif defined(sensor_type) and sensor_type == 'precip' %} precip
    {% elif defined(sensor_type) and sensor_type == 'wind' %} wind_speed, wind_dir
    {% elif defined(sensor_type) and sensor_type == 'humidity' %} humidity
    {% elif defined(sensor_type) and sensor_type == 'pressure' %} pressure
    {% elif defined(sensor_type) and sensor_type == 'clouds' %} clouds
    {% else %}
        temp_f, precip, wind_speed, wind_dir, humidity, pressure, clouds, description
    {% end %} 
FROM city_and_period_of_interest
```

### Node 3 named ``endpoint``

Here we apply the ``max_results`` parameter. The naming here follows a convention of marking the Node you want to publish as an API with the name ``endpoint``. You can use whatever name you want. 

```sql
%
SELECT * 
FROM select_sensor_type
ORDER BY timestamp DESC
LIMIT {{ Int32(max_results, 1000, description="The maximum number of reports to return per response. Defaults to 1000.") }}

```

## Checklist for replicating this demo

- [ ] Set up accounts
  - [ ] OpenWeatherMap
  - [ ] Tinybird
	
- [ ] Establishing data feed
  - [ ] Create Tinybird Data Source referencing report JSON object
  - [ ] Set-up, configure and deploy the “get_and_post_data” Python script. 
		
- [] Build Tinybird Pipe 
  * With CLI
    - [ ] Push provided Pipe file to your Workspace
  * With UI
    - [ ] Create ‘reports’ Pipe
    - [ ] Create Nodes 

- [ ] Publish and test API Endpoint


## Next steps? 

Some ways to iterate the weather data API Endpoint: 

- [ ] Add sensor types of ``wind_vel`` and ``wind_dir``.
- [ ] Enable selecting a comma-delimited list of City names.
- [ ] Parameterize number of days set start_time with (not a query parameter, but a configurable Pipe setting.
- [ ] Enable selecting a comma-delimited list of City names.
- [ ] Enable selecting a comma-delimited list of sensor types.
- [ ] Add geographic metadata:
  - [ ] Capture OpenWeatherMap geo metadata for current set of cities. 
  - [ ] Enable data retrieval by geographic area, such as US States.
  - [ ] Design an endpoint to serve up site metadata, including geographic metadata to support filtering by location. 





 



