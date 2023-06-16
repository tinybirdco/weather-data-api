import sys
import requests
import threading
import time
import os
import argparse
from dotenv import load_dotenv

class SuccessCounter:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            self.count += 1

def make_request(tinybird_api_endpoint, headers, params, success_counter):
    try:
        response = requests.get(tinybird_api_endpoint, headers=headers, params=params)
        response.raise_for_status()  # Raises an exception if the response status code indicates an error
        # Process the response or perform any required actions here
        #print(response.status_code)
        success_counter.increment()  # Increment the success counter
        if success_counter.count % 100 == 0:
            print(f"{success_counter.count} successful requests have been made.")

    except requests.exceptions.RequestException as e:
        # Handle any request-related exceptions (e.g., connection error, timeout)
        print(f"An error occurred: {e}")
    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors (e.g., 404, 500)
        print(f"HTTP error occurred: {e}")
    except Exception as e:
        # Handle any other unexpected exceptions
        print(f"An unexpected error occurred: {e}")

def main():
    # Load Tinybird authentication token from local environment.
    dotenv_path = os.path.join(os.path.dirname(__file__), '../config', '.env')
    load_dotenv(dotenv_path)
    tinybird_token = os.environ.get('TINYBIRD_TOKEN')

    # Create a success counter
    success_counter = SuccessCounter()

    headers = {"Authorization": f"Bearer {tinybird_token}"}

    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description="Command-line arguments for the script.")
    parser.add_argument("--rpm", type=int, default=100, help="Number of requests per minute (default: 100)")
    parser.add_argument("endpoint", nargs="?", help="Endpoint for the API URL")
    args = parser.parse_args()
    # Number of requests to make per minute. This determines the delay between creating a new request thread.
    REQUESTS_PER_MINUTE = args.rpm
    ENDPOINT = args.endpoint

    # Validate the endpoint argument
    if ENDPOINT is None:
        parser.error("Endpoint argument is required. Please provide a valid endpoint.")
        sys.exit(1)

    # Calculate the delay between each request in seconds
    delay = 60 / REQUESTS_PER_MINUTE

    # Construct the API endpoint URL using the provided endpoint argument
    tinybird_api_endpoint = f"https://api.tinybird.co/v0/pipes/{ENDPOINT}.json"

    # Set any API query parameters.
    sensor_type = 'all'
    max_results = 1000
    params = {"sensor_type": sensor_type, "max_results": max_results}

    print(f"Making {REQUESTS_PER_MINUTE} requests per minute (rpm) to {ENDPOINT} ")

    # Loop to make requests
    while True:
        # Create a new thread for each request
        threading.Thread(target=make_request, args=(tinybird_api_endpoint, headers, params, success_counter)).start()

        # Wait for the delay before making the next request
        time.sleep(delay)

if __name__ == "__main__":
    main()
