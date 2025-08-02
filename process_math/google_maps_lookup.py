# process_math/google_maps_lookup.py
#
# This file contains a Python function for performing geocoding lookups
# using the Google Maps Geocoding API, converting a text query (e.g., postal code)
# into structured address components like city, province, and street address.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
# Version 20250802.0105.1 (Refactored debug_print to debug_log; updated imports and flair.)

current_version = "20250802.0105.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 105 * 1 # Example hash, adjust as needed

import requests
import inspect
import time
from datetime import datetime
import json # Import json for pretty printing debug output

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log # Added for console_print_func

# IMPORTANT: Replace with your actual Google Maps API Key
# This key should ideally be loaded from a secure configuration or environment variable.
# For this example, it's hardcoded for demonstration purposes.
# GOOGLE_MAPS_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY" # Placeholder

def get_location_from_google_maps(query, google_maps_api_key, console_print_func=None):
    """
    Function Description:
    Performs a geocoding lookup using the Google Maps Geocoding API for a given query
    (e.g., postal code, address) and extracts city, province/state, and street address.

    Inputs:
    - query (str): The postal code or address string to look up.
    - google_maps_api_key (str): Your Google Maps API Key.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Prints a debug message.
    2. Constructs the API URL with the query and API key.
    3. Sends an HTTP GET request to the Google Maps Geocoding API.
    4. Parses the JSON response.
    5. Extracts city, province/state, and street address from the results.
    6. Handles various error scenarios (API key missing, request errors, no results).
    7. Logs success or failure.

    Outputs of this function:
    - tuple: (city, province, street) as strings, or (None, None, None) if lookup fails.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Performing Google Maps lookup for query: '{query}'. Getting location data!",
                file=current_file, version=current_version, function=current_function)

    if not google_maps_api_key:
        console_print_func("❌ Google Maps API Key is missing. Cannot perform lookup. Please configure it!")
        debug_log("Google Maps API Key is missing. Lookup aborted!",
                    file=current_file, version=current_version, function=current_function)
        return None, None, None

    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": query,
        "key": google_maps_api_key
    }

    try:
        debug_log(f"Sending request to Google Maps API for query: '{query}'...",
                    file=current_file, version=current_version, function=current_function)
        response = requests.get(base_url, params=params)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        data = response.json()
        debug_log(f"Received response from Google Maps API. Status: {data.get('status')}. Data acquired!",
                    file=current_file, version=current_version, function=current_function)
        debug_log(f"Full API response (first 500 chars): {json.dumps(data, indent=2)[:500]}...",
                    file=current_file, version=current_version, function=current_function)

        if data["status"] == "OK" and data["results"]:
            result = data["results"][0]
            city = None
            province = None
            street_address = None

            for component in result["address_components"]:
                if "locality" in component["types"]:
                    city = component["long_name"]
                if "administrative_area_level_1" in component["types"]:
                    province = component["long_name"]
                if "route" in component["types"]:
                    street_address = component["long_name"]
                if "street_number" in component["types"] and street_address:
                    street_address = component["long_name"] + " " + street_address
                elif "street_number" in component["types"]:
                    street_address = component["long_name"] # In case route is not present

            console_print_func(f"✅ Location found for '{query}': City: {city}, Province: {province}, Street: {street_address}. Success!")
            debug_log(f"Location found: City='{city}', Province='{province}', Street='{street_address}'. Data parsed!",
                        file=current_file, version=current_version, function=current_function)
            return city, province, street_address
        elif data["status"] == "ZERO_RESULTS":
            console_print_func(f"ℹ️ No location found for '{query}'. Try a different query. No results!")
            debug_log(f"Google Maps API returned ZERO_RESULTS for query: '{query}'. Nothing found!",
                        file=current_file, version=current_version, function=current_function)
            return None, None, None
        else:
            error_msg = f"❌ Google Maps API error for '{query}': {data['status']}. Message: {data.get('error_message', 'No error message provided')}. API problem!"
            console_print_func(error_msg)
            debug_log(error_msg,
                        file=current_file, version=current_version, function=current_function)
            return None, None, None

    except requests.exceptions.RequestException as e:
        error_msg = f"❌ Network or HTTP error during Google Maps lookup for '{query}': {e}. Check your internet connection!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=current_file, version=current_version, function=current_function)
        return None, None, None
    except json.JSONDecodeError as e:
        error_msg = f"❌ JSON decoding error from Google Maps API response for '{query}': {e}. Bad data format!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=current_file, version=current_version, function=current_function)
        return None, None, None
    except Exception as e:
        error_msg = f"❌ An unexpected error occurred during Google Maps lookup for '{query}': {e}. General problem!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=current_file, version=current_version, function=current_function)
        return None, None, None

# Example Usage (for testing purposes, you can uncomment this)
if __name__ == "__main__":
    # Remember to set your GOOGLE_MAPS_API_KEY above for these examples to work!
    # For testing, you can temporarily hardcode it here or pass it from an environment variable.
    # Example:
    # GOOGLE_MAPS_API_KEY_TEST = "YOUR_ACTUAL_API_KEY_HERE"

    # print("\n--- Testing L1N 9N8 (Whitby, Ontario) with Google Maps ---")
    # city, province, street = get_location_from_google_maps("", GOOGLE_MAPS_API_KEY_TEST)
    # print(f"L1N 9N8 -> City: {city}, Province: {province}, Street: {street}")

    # print("\n--- Testing L1N 6S1 (Whitby, Ontario) with Google Maps ---")
    # city, province, street = get_location_from_google_maps("", GOOGLE_MAPS_API_KEY_TEST)
    # print(f"L1N 6S1 -> City: {city}, Province: {province}, Street: {street}")

    # print("\n--- Testing 10001 (New York, NY) with Google Maps ---")
    # city, province, street = get_location_from_google_maps("10001", GOOGLE_MAPS_API_KEY_TEST)
    # print(f"10001 -> City: {city}, State: {province}, Street: {street}")

    # print("\n--- Testing Full Address with Google Maps ---")
    # city, province, street = get_location_from_google_maps("1600 Amphitheatre Parkway, Mountain View, CA", GOOGLE_MAPS_API_KEY_TEST)
    # print(f"1600 Amphitheatre Parkway, Mountain View, CA -> City: {city}, State: {province}, Street: {street}")

    # print("\n--- Testing Invalid Query ---")
    # city, province, street = get_location_from_google_maps("ASDFGHJKL", GOOGLE_MAPS_API_KEY_TEST)
    # print(f"ASDFGHJKL -> City: {city}, Province: {province}, Street: {street}")

    # print("\n--- Testing with Missing API Key (should show error) ---")
    # city, province, street = get_location_from_google_maps("L1N 9N8", "")
    # print(f"Missing API Key Test -> City: {city}, Province: {province}, Street: {street}")
    pass
