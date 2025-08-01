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
#
#
# Version 1.1 (Updated with user-provided Google Maps API Key)

import requests
import inspect
import time
from datetime import datetime
import json # Import json for pretty printing debug output

# Assuming debug_print is available globally or passed in
try:
    from utils.utils_instrument_control import debug_print
except ImportError:
    def debug_print(message, file=None, function=None, console_print_func=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = f"[{file.split('/')[-1]}:{function}] " if file and function else ""
        full_message = f"🚫🐛 [{timestamp}] {prefix}{message}"
        if console_print_func:
            console_print_func(full_message)
        else:
            print(full_message)

# !!! IMPORTANT: Replace with your actual Google Maps API Key !!!
# Obtain one from Google Cloud Console (enable Geocoding API)
GOOGLE_MAPS_API_KEY = "AIzaSyCWVcIVLzbzOCobtzxmI-juPwnm_18x9i0"


def get_location_from_google_maps(query_text, console_print_func=None):
    # This function descriotion tells me what this function does
    # Queries the Google Maps Geocoding API to retrieve structured location
    # information (city, province/state, street address) based on a text query
    # such as a postal code or a general address string.
    #
    # Inputs to this function
    #   query_text (str): The postal code, zip code, or address string to look up.
    #   console_print_func (function, optional): A function to print messages
    #                                            to the application's console output.
    #                                            Defaults to standard print if not provided.
    #
    # Process of this function
    #   1. Sets up the Google Maps Geocoding API endpoint and parameters, including the API key.
    #   2. Prints a debug message indicating the start of the API call.
    #   3. Makes an HTTP GET request to the Google Maps Geocoding API.
    #   4. Checks the HTTP response status code and 'status' field in the JSON response.
    #   5. Parses the JSON response from the API.
    #   6. If results are found, it iterates through the 'address_components' to extract
    #      the city, administrative area level 1 (province/state), and street address.
    #   7. Constructs the full street address from available components.
    #   8. If any of the desired components are still None/empty, it prints the full
    #      raw result for debugging.
    #   9. Returns the extracted city, province, and street address.
    #   10. Includes robust error handling for API call failures, JSON decoding issues,
    #       and cases where no results are found or API status is not 'OK'.
    #
    # Outputs of this function
    #   tuple: A tuple containing (city, province, street_address) as strings.
    #          Returns (None, None, None) if the lookup fails or no data is found.
    #
    # (2025-07-30) Change: Updated with user-provided Google Maps API key.
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__

    if console_print_func is None:
        console_print_func = print

    if not GOOGLE_MAPS_API_KEY or GOOGLE_MAPS_API_KEY == "YOUR_GOOGLE_MAPS_API_KEY_HERE":
        console_print_func("❌ Google Maps API Key is missing or not set. Please update GOOGLE_MAPS_API_KEY in the file.")
        debug_print("Google Maps API Key missing.", file=current_file, function=current_function, console_print_func=console_print_func)
        return None, None, None

    GOOGLE_MAPS_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": query_text,
        "key": GOOGLE_MAPS_API_KEY
    }

    debug_print(f"Attempting Google Maps lookup for: '{query_text}'",
                file=current_file, function=current_function, console_print_func=console_print_func)
    
    try:
        response = requests.get(GOOGLE_MAPS_URL, params=params, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        
        data = response.json()

        if data['status'] == 'OK' and data['results']:
            first_result = data['results'][0]
            address_components = first_result.get('address_components', [])

            city = None
            province = None
            street_name = None
            house_number = None

            for component in address_components:
                types = component.get('types', [])
                if 'locality' in types:
                    city = component.get('long_name')
                elif 'administrative_area_level_1' in types: # e.g., Ontario, California
                    province = component.get('long_name')
                elif 'route' in types: # Street name
                    street_name = component.get('long_name')
                elif 'street_number' in types:
                    house_number = component.get('long_name')
                elif 'postal_code' in types:
                    # We could also get postal code here, but we're querying by it
                    pass

            street_address = ""
            if house_number and street_name:
                street_address = f"{house_number} {street_name}"
            elif street_name:
                street_address = street_name
            
            # If any are still None, print the full result for debugging
            if city is None or province is None or street_address == "":
                console_print_func(f"⚠️ Partial or no specific location data found for '{query_text}'.")
                console_print_func(f"🚫🐛 Google Maps raw result details: {json.dumps(first_result, indent=2)}")
                debug_print(f"Partial/No specific Google Maps results for '{query_text}'. Raw result: {json.dumps(first_result)}",
                            file=current_file, function=current_function, console_print_func=console_print_func)
                # Still return what we have, even if partial
                return city, province, street_address
            else:
                debug_print(f"Google Maps lookup successful for '{query_text}'. Result: City='{city}', Province='{province}', Street='{street_address}'",
                            file=current_file, function=current_function, console_print_func=console_print_func)
                return city, province, street_address
        else:
            status = data.get('status', 'UNKNOWN_STATUS')
            error_message = data.get('error_message', 'No results or API error.')
            console_print_func(f"⚠️ Google Maps API returned status '{status}' for '{query_text}': {error_message}")
            debug_print(f"Google Maps API status: {status}, Error: {error_message}",
                        file=current_file, function=current_function, console_print_func=console_print_func)
            return None, None, None

    except requests.exceptions.HTTPError as http_err:
        console_print_func(f"❌ HTTP error during Google Maps lookup for '{query_text}': {http_err}")
        debug_print(f"HTTPError: {http_err}",
                    file=current_file, function=current_function, console_print_func=console_print_func)
    except requests.exceptions.ConnectionError as conn_err:
        console_print_func(f"❌ Connection error during Google Maps lookup for '{query_text}'. Check your internet connection: {conn_err}")
        debug_print(f"ConnectionError: {conn_err}",
                    file=current_file, function=current_function, console_print_func=console_print_func)
    except requests.exceptions.Timeout as timeout_err:
        console_print_func(f"❌ Timeout error during Google Maps lookup for '{query_text}'. The server took too long to respond: {timeout_err}")
        debug_print(f"TimeoutError: {timeout_err}",
                    file=current_file, function=current_function, console_print_func=console_print_func)
    except requests.exceptions.RequestException as req_err:
        console_print_func(f"❌ An unexpected error occurred during Google Maps lookup for '{query_text}': {req_err}")
        debug_print(f"RequestException: {req_err}",
                    file=current_file, function=current_function, console_print_func=console_print_func)
    except Exception as e:
        console_print_func(f"❌ An error occurred processing Google Maps response for '{query_text}': {e}")
        debug_print(f"General Error: {e}",
                    file=current_file, function=current_function, console_print_func=console_print_func)
    
    return None, None, None

# Example Usage (for testing purposes, you can uncomment this)
if __name__ == "__main__":
    # Remember to set your GOOGLE_MAPS_API_KEY above for these examples to work!

    print("\n--- Testing L1N 9N8 (Whitby, Ontario) with Google Maps ---")
    city, province, street = get_location_from_google_maps("L1N 9N8")
    print(f"L1N 9N8 -> City: {city}, Province: {province}, Street: {street}")

    print("\n--- Testing L1N 6S1 (Whitby, Ontario) with Google Maps ---")
    city, province, street = get_location_from_google_maps("L1N 6S1")
    print(f"L1N 6S1 -> City: {city}, Province: {province}, Street: {street}")

    print("\n--- Testing 10001 (New York, NY) with Google Maps ---")
    city, province, street = get_location_from_google_maps("10001")
    print(f"10001 -> City: {city}, State: {province}, Street: {street}")

    print("\n--- Testing Full Address with Google Maps ---")
    city, province, street = get_location_from_google_maps("1600 Amphitheatre Parkway, Mountain View, CA")
    print(f"1600 Amphitheatre Parkway -> City: {city}, State: {province}, Street: {street}")

    print("\n--- Testing Invalid Query with Google Maps ---")
    city, province, street = get_location_from_google_maps("NOTALOCATION123")
    print(f"NOTALOCATION123 -> City: {city}, Province: {province}, Street: {street}")
