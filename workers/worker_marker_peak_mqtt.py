# workers/worker_marker_peak_hunter.py
#
# This module reads a CSV file, converts it to a structured JSON format,
# saves the JSON, and publishes the entire structure to an MQTT topic.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250926.223500.1

import os
import inspect
import csv
import json
import pathlib
from collections import defaultdict

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility

# --- Global Scope Variables ---
current_version = "20250926.223500.1"
current_version_hash = (20250926 * 223500 * 1)
current_file = f"{os.path.basename(__file__)}"
MARKERS_JSON_PATH = pathlib.Path("DATA/MARKERS.json")
MARKERS_CSV_PATH = pathlib.Path("DATA/MARKERS.csv")
MQTT_BASE_TOPIC = "OPEN-AIR/repository/markers"


def _publish_recursive(mqtt_util, base_topic, data):
    """
    A simple recursive function to publish all parts of a nested dictionary.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            new_topic = f"{base_topic}/{key}"
            _publish_recursive(mqtt_util, new_topic, value)
    else:
        # When we hit a final value, publish it.
        mqtt_util.publish_message(topic=base_topic, subtopic="", value=str(data), retain=True)


def csv_to_json_and_publish(mqtt_util: MqttControllerUtility):
    """
    Reads MARKERS.csv, calculates summary data (total, min/max freq, span), converts
    to a flat device-centric JSON structure, saves it, and publishes to MQTT.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(
        message=f"🛠️🟢 Initiating device-centric CSV to JSON conversion and MQTT publish.",
        file=current_file,
        version=current_version,
        function=current_function_name,
        console_print_func=console_log
    )

    if not MARKERS_CSV_PATH.is_file():
        console_log(f"❌ {MARKERS_CSV_PATH} not found. Aborting operation.")
        return

    # --- Step 1: Read CSV and generate the flat JSON structure ---
    json_state = {}
    try:
        with open(MARKERS_CSV_PATH, mode='r', newline='', encoding='utf-8') as csvfile:
            # Read all data into a list to process it multiple times
            reader = list(csv.DictReader(csvfile))
            
            total_devices = len(reader)
            min_freq = float('inf')
            max_freq = float('-inf')

            # First pass: calculate min/max frequencies
            for row in reader:
                try:
                    # --- FIX: Check for 'FREQ', 'FREQ (MHZ)', and 'FREQ_MHZ' ---
                    freq_str = row.get("FREQ") or row.get("FREQ (MHZ)") or row.get("FREQ_MHZ")
                    if freq_str:
                        freq = float(freq_str)
                        if freq < min_freq:
                            min_freq = freq
                        if freq > max_freq:
                            max_freq = freq
                except (ValueError, TypeError):
                    # Ignore rows with non-numeric frequencies for min/max calculation
                    continue
            
            # Handle case where no valid frequencies were found
            if min_freq == float('inf'): min_freq = 0
            if max_freq == float('-inf'): max_freq = 0

            # Calculate the span
            span_mhz = max_freq - min_freq

            # Add summary data to the root of the JSON state
            json_state["total_devices"] = total_devices
            json_state["min_frequency_mhz"] = min_freq
            json_state["max_frequency_mhz"] = max_freq
            json_state["span_mhz"] = span_mhz
            
            # Second pass: build the device dictionaries
            for i, row in enumerate(reader, 1):
                device_key = f"Device-{i:03d}"
                # The new flat structure as requested
                json_state[device_key] = {
                    "Name": row.get("NAME", ""),
                    "Device": row.get("DEVICE", ""),
                    "Zone": row.get("ZONE", ""),
                    "Group": row.get("GROUP", ""),
                    # --- FIX: Check for all possible frequency headers here as well ---
                    "FREQ_MHZ": row.get("FREQ") or row.get("FREQ (MHZ)") or row.get("FREQ_MHZ") or "null",
                    "Peak": row.get("PEAK", "null"),
                    "active": "True",
                    "selected": "false" 
                }
        console_log("✅ Successfully read CSV and generated flat JSON structure with summary data.")
    except Exception as e:
        console_log(f"❌ Error processing CSV file: {e}")
        debug_log(
            message=f"❌🔴 The CSV-to-JSON contraption has malfunctioned! The error be: {e}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )
        return

    # --- Step 2: Save the generated structure to MARKERS.json ---
    try:
        # Ensure the DATA directory exists
        MARKERS_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(MARKERS_JSON_PATH, 'w') as f:
            json.dump(json_state, f, indent=4)
        console_log(f"✅ Saved generated structure to {MARKERS_JSON_PATH}.")
    except Exception as e:
        console_log(f"❌ Error saving to {MARKERS_JSON_PATH}: {e}")
        debug_log(
            message=f"❌🔴 The enchanted scroll refuses to be written! The error be: {e}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )
        return

    # --- Step 3: Publish the entire structure to MQTT ---
    try:
        # First, clear any old data under the base topic by publishing a null, retained message.
        mqtt_util.publish_message(topic=f"{MQTT_BASE_TOPIC}/#", subtopic="", value=None, retain=True)
        console_log(f"Cleared old data under topic: {MQTT_BASE_TOPIC}/#")

        # Now, publish the new, complete structure recursively.
        _publish_recursive(mqtt_util, MQTT_BASE_TOPIC, json_state)
        
        console_log("✅ Successfully published the full marker set to MQTT.")
    except Exception as e:
        console_log(f"❌ Error publishing to MQTT: {e}")
        debug_log(
            message=f"❌🔴 The message pigeons have flown astray! The error be: {e}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )

