# workers/worker_marker_csv_to_json_mqtt.py
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251129  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 1 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


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
# Version 20251005.220127.2

import os
import inspect
import csv
import json
import pathlib
from collections import defaultdict

# --- Module Imports ---
from display.logger import debug_log, console_log, log_visa_command
from workers.mqtt.worker_mqtt_controller_util import MqttControllerUtility
from workers.utils.worker_project_paths import MARKERS_JSON_PATH, MARKERS_CSV_PATH # NEW: Import paths


# --- Global Scope Variables ---
current_version = "20251005.220127.2"
current_version_hash = (20251005 * 220127 * 2)
current_file = f"{os.path.basename(__file__)}"
Local_Debug_Enable = True

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
    
    MODIFIED: Uses the new nested structure with an 'IDENTITY' blob.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    if Local_Debug_Enable:
        debug_log(
            message=f"🛠️🟢 Initiating device-centric CSV to JSON conversion and MQTT publish. Applying new nested structure.",
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
                    # Now relies on the canonical 'FREQ_MHZ' key from file_handling worker
                    freq_str = row.get("FREQ_MHZ")
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
            json_state["min_frequency_mhz"] = round(min_freq, 6)
            json_state["max_frequency_mhz"] = round(max_freq, 6)
            json_state["span_mhz"] = round(span_mhz, 6)
            
            # Second pass: build the device dictionaries
            for i, row in enumerate(reader, 1):
                device_key = f"Device-{i:03d}"
                
                # --- NEW STRUCTURE IMPLEMENTATION ---
                json_state[device_key] = {
                    "IDENTITY": {
                        "Name": row.get("NAME", ""),
                        "Device": row.get("DEVICE", ""),
                        "Zone": row.get("ZONE", ""),
                        "Group": row.get("GROUP", ""),
                        "FREQ_MHZ": row.get("FREQ_MHZ") or "null",
                    },
                    "Peak": row.get("PEAK", "nan"),
                    # Removing the "active" and "selected" fields as requested
                }
                # --- END NEW STRUCTURE IMPLEMENTATION ---

        console_log("✅ Successfully read CSV and generated nested JSON structure with summary data.")
    except Exception as e:
        console_log(f"❌ Error processing CSV file: {e}")
        if Local_Debug_Enable:
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
        if Local_Debug_Enable:
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
        # This will remove all the old topics (Device-001/Name, Device-001/active, etc.)
        mqtt_util.purge_branch(MQTT_BASE_TOPIC)
        console_log(f"Cleared old data under topic: {MQTT_BASE_TOPIC}/#")

        # Now, publish the new, complete structure recursively.
        _publish_recursive(mqtt_util, MQTT_BASE_TOPIC, json_state)
        
        console_log("✅ Successfully published the full marker set to MQTT.")
    except Exception as e:
        console_log(f"❌ Error publishing to MQTT: {e}")
        if Local_Debug_Enable:
            debug_log(
                message=f"❌🔴 The message pigeons have flown astray! The error be: {e}",
                file=current_file,
                version=current_version,
                function=current_function_name,
                console_print_func=console_log
            )