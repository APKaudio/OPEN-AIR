# workers/worker_marker_peak_hunter.py
#
# This module contains the logic for finding peaks within a frequency range and
# publishing them to the MQTT broker, operating within the framework's defined protocols.
# It uses a series of functions to handle data processing, peak detection, and communication.
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
# Version 20250922.232530.10

import os
import inspect
import csv
import json
import numpy as np
from scipy.signal import find_peaks
import pathlib
import re
from collections import defaultdict
import threading
import time
import paho.mqtt.client as mqtt
import copy

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility

# --- Global Scope Variables ---
current_version = "20250922.232530.10"
current_version_hash = (20250922 * 232530 * 10)
current_file = f"{os.path.basename(__file__)}"
MARKERS_JSON_PATH = pathlib.Path("DATA/MARKERS.json")
MARKERS_CSV_PATH = pathlib.Path("DATA/MARKERS.csv")
MQTT_BASE_TOPIC = "OPEN-AIR/repository/markers"
HZ_TO_MHZ = 1_000_000


def _generate_pre_publish_state() -> dict:
    """
    Reads the MARKERS.csv file and generates a nested dictionary representing
    the desired final state for the MQTT repository.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(
        message=f"🛠️🔵 Generating 'pre-publish' state from CSV data.",
        file=current_file,
        version=current_version,
        function=current_function_name,
        console_print_func=console_log
    )
    
    if not MARKERS_CSV_PATH.is_file():
        return {}

    state = {}
    try:
        with open(MARKERS_CSV_PATH, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            
            zone_groups = defaultdict(lambda: defaultdict(list))
            for row in reader:
                zone = row.get("ZONE", "unknown_zone")
                group = row.get("GROUP", "unknown_group")
                zone_groups[zone][group].append(row)

            for zone_index, (zone_name, groups) in enumerate(zone_groups.items(), 1):
                zone_key = f"zone-{zone_index:02d}"
                state[zone_key] = {"name": zone_name, "selected": "false", "groups": {}}

                for group_index, (group_name, devices) in enumerate(groups.items(), 1):
                    group_key = f"group-{group_index:02d}"
                    state[zone_key]["groups"][group_key] = {"name": group_name, "selected": "false", "devices": {}}
                    
                    for device_index, device_row in enumerate(devices, 1):
                        device_key = f"device-{device_index:02d}"
                        state[zone_key]["groups"][group_key]["devices"][device_key] = {
                            "active": "True",
                            "name": device_row.get("NAME", ""),
                            "freq_mhz": device_row.get("FREQ (MHZ)", "null"),
                            "peak": device_row.get("PEAK", "null"),
                            "selected": "false"
                        }
    except Exception as e:
        console_log(f"❌ Error reading CSV file: {e}")
        return {}
        
    return state


def _calculate_delta_and_publish(old_state: dict, new_state: dict, mqtt_util: MqttControllerUtility):
    """
    Compares two state dictionaries, identifies the delta, and publishes changes to MQTT.
    
    This function has been corrected to explicitly publish `null` payloads for deleted
    topics, ensuring they are properly removed from the broker's retained message store.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(
        message=f"🛠️🔵 Calculating delta and publishing changes to MQTT.",
        file=current_file,
        version=current_version,
        function=current_function_name,
        console_print_func=console_log
    )
    
    # Identify and clear deleted nodes
    for old_zone_key, old_zone_val in old_state.items():
        if old_zone_key not in new_state:
            mqtt_util.publish_message(topic=f"{MQTT_BASE_TOPIC}/{old_zone_key}/#", subtopic="", value=None, retain=True)
            debug_log(f"Cleared deleted zone: {old_zone_key}", file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
            continue
            
        for old_group_key, old_group_val in old_zone_val.get("groups", {}).items():
            if old_group_key not in new_state.get(old_zone_key, {}).get("groups", {}):
                mqtt_util.publish_message(topic=f"{MQTT_BASE_TOPIC}/{old_zone_key}/{old_group_key}/#", subtopic="", value=None, retain=True)
                debug_log(f"Cleared deleted group: {old_zone_key}/{old_group_key}", file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
                continue
                
            for old_device_key, _ in old_group_val.get("devices", {}).items():
                if old_device_key not in new_state.get(old_zone_key, {}).get("groups", {}).get(old_group_key, {}).get("devices", {}):
                    mqtt_util.publish_message(topic=f"{MQTT_BASE_TOPIC}/{old_zone_key}/{old_group_key}/{old_device_key}/#", subtopic="", value=None, retain=True)
                    debug_log(f"Cleared deleted device: {old_zone_key}/{old_group_key}/{old_device_key}", file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
                    
    # Identify new or updated nodes and publish
    for new_zone_key, new_zone_val in new_state.items():
        old_zone_val = old_state.get(new_zone_key, {})
        zone_topic = f"{MQTT_BASE_TOPIC}/{new_zone_key}"

        if new_zone_val.get("name") != old_zone_val.get("name"):
            mqtt_util.publish_message(topic=f"{zone_topic}/name", subtopic="", value=new_zone_val.get("name"), retain=True)
        if new_zone_val.get("selected") != old_zone_val.get("selected"):
            mqtt_util.publish_message(topic=f"{zone_topic}/selected", subtopic="", value=new_zone_val.get("selected"), retain=True)
        
        for new_group_key, new_group_val in new_zone_val.get("groups", {}).items():
            old_group_val = old_zone_val.get("groups", {}).get(new_group_key, {})
            group_topic = f"{zone_topic}/{new_group_key}"

            if new_group_val.get("name") != old_group_val.get("name"):
                mqtt_util.publish_message(topic=f"{group_topic}/name", subtopic="", value=new_group_val.get("name"), retain=True)
            if new_group_val.get("selected") != old_group_val.get("selected"):
                mqtt_util.publish_message(topic=f"{group_topic}/selected", subtopic="", value=new_group_val.get("selected"), retain=True)

            for new_device_key, new_device_val in new_group_val.get("devices", {}).items():
                old_device_val = old_group_val.get("devices", {}).get(new_device_key, {})
                device_topic = f"{group_topic}/{new_device_key}"

                for field, value in new_device_val.items():
                    if value != old_device_val.get(field):
                        mqtt_util.publish_message(topic=f"{device_topic}/{field}", subtopic="", value=value, retain=True)

    console_log("✅ All changes published to MQTT.")


def Peak_hunter_CSV_to_MQTT(mqtt_util: MqttControllerUtility):
    """
    Reads data from the MARKERS.csv file, computes the delta against the last
    published state (MARKERS.json), and publishes only the changes to MQTT.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(
        message=f"🛠️🟢 Starting delta-based CSV to MQTT conversion for {MARKERS_CSV_PATH}.",
        file=current_file,
        version=current_version,
        function=current_function_name,
        console_print_func=console_log
    )

    try:
        # Step 1: Load the old state from the JSON file
        old_state = {}
        if MARKERS_JSON_PATH.is_file():
            with open(MARKERS_JSON_PATH, 'r') as f:
                old_state = json.load(f)
        
        # Step 2: Generate the new "pre-publish" state from the CSV
        new_state = _generate_pre_publish_state()

        # Step 3: Calculate the delta and publish changes to MQTT
        _calculate_delta_and_publish(old_state, new_state, mqtt_util)

        # Step 4: Save the new state to the JSON file for the next run
        with open(MARKERS_JSON_PATH, 'w') as f:
            json.dump(new_state, f, indent=4)
            
        console_log("✅ Finished processing and publishing marker data.")
    
    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        debug_log(
            message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )


def Peak_hunter_focus_area(peak_data: list, start_freq: float, stop_freq: float) -> list:
    """
    Filters a list of peak dictionaries to a specified frequency range.
    
    Args:
        peak_data (list): A list of dictionaries, where each dictionary represents a peak
                          and contains a 'frequency' key.
        start_freq (float): The lower bound of the frequency range in MHz.
        stop_freq (float): The upper bound of the frequency range in MHz.
        
    Returns:
        list: A new list containing only the peaks within the specified range.
    """
    current_function_name = inspect.currentframe().f_code.co_name

    debug_log(
        message=f"🛠️🔵 Filtering peak list to focus area: {start_freq} MHz to {stop_freq} MHz.",
        file=current_file,
        version=current_version,
        function=current_function_name,
        console_print_func=console_log
    )
    
    try:
        filtered_peaks = [
            peak for peak in peak_data
            if start_freq <= peak.get('frequency', 0) <= stop_freq
        ]
        
        console_log(f"✅ Filtered down to {len(filtered_peaks)} peaks in the specified area.")
        return filtered_peaks

    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        debug_log(
            message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )
        return []


def Peak_hunter_querry_list_of_peaks(peak_list: list, mqtt_util: MqttControllerUtility):
    """
    Constructs and sends an SCPI query to retrieve amplitude data for a list of peaks.
    
    Args:
        peak_list (list): A list of dictionaries, where each dictionary represents a peak.
        mqtt_util (MqttControllerUtility): The MQTT utility for publishing commands.
    """
    current_function_name = inspect.currentframe().f_code.co_name

    debug_log(
        message=f"🛠️🔵 Constructing and sending a query for a list of {len(peak_list)} peaks.",
        file=current_file,
        version=current_version,
        function=current_function_name,
        console_print_func=console_log
    )
    
    try:
        if not peak_list:
            console_log("🟡 Peak list is empty. No query to send.")
            return

        # Build the SCPI query string
        queries = []
        for peak in peak_list:
            freq_hz = int(float(peak.get('frequency', 0)) * HZ_TO_MHZ)
            queries.append(f":CALCulate:MARKer:X {freq_hz};:CALCulate:MARKer:Y?")
        
        full_query = ';'.join(queries)

        # The topic for the SCPI query is a generalized path to the translator's command.
        query_topic = "OPEN-AIR/actions/scpi/query/generic"
        
        # Publish the command to the translator
        mqtt_util.publish_message(
            topic=query_topic,
            subtopic="",
            value=full_query
        )
        
        console_log(f"✅ SCPI query for {len(peak_list)} peaks dispatched.")

    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        debug_log(
            message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )

def Peak_hunter_mqtt_publish_peaks(peak_list: list, mqtt_util: MqttControllerUtility):
    """
    Publishes a list of peaks to a structured MQTT topic.
    
    Args:
        peak_list (list): A list of dictionaries, where each dictionary represents a peak.
        mqtt_util (MqttControllerUtility): The MQTT utility for publishing.
    """
    current_function_name = inspect.currentframe().f_code.co_name

    debug_log(
        message=f"🛠️🟢 Publishing a list of {len(peak_list)} peaks to the MQTT broker.",
        file=current_file,
        version=current_version,
        function=current_function_name,
        console_print_func=console_log
    )
    
    try:
        if not peak_list:
            console_log("🟡 No peaks to publish.")
            return

        base_topic = "OPEN-AIR/peaks/current_session"
        
        for i, peak in enumerate(peak_list):
            topic = f"{base_topic}/peak_{i+1}"
            payload = json.dumps(peak)
            
            mqtt_util.publish_message(
                topic=topic,
                subtopic="",
                value=payload,
                retain=True
            )
            
        console_log(f"✅ Published {len(peak_list)} peaks to MQTT.")

    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        debug_log(
            message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )