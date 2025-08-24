# worker/dataset_publisher.py
#
# A script to read and publish JSON datasets from the local directory to an MQTT broker.
# This version includes enhanced logging and versioning to aid in debugging and tracking.
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
# Version 20250823.201500.2
#
# This file works in conjunction with gui_prototype.py and other modules
# within the larger project structure.

import os
import json
import sys
import inspect
import pathlib
import time
from workers.mqtt_controller_util import MqttControllerUtility

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from display.styling.style import THEMES, DEFAULT_THEME

# --- Global Scope Variables ---
CURRENT_DATE = 20250823
CURRENT_TIME = 2015
REVISION_NUMBER = 2
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME * REVISION_NUMBER)
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")

def publish_recursive(mqtt_util, base_topic, data):
    """
    Recursively publishes nested dictionary and list data to the MQTT broker.
    It constructs the topic using meaningful names from the JSON data.
    """
    current_function_name = inspect.currentframe().f_code.co_name

    if isinstance(data, dict):
        for key, value in data.items():
            # Check for a descriptive name within the current dictionary
            if isinstance(value, dict) and "name" in value:
                new_topic = f"{base_topic}/{key}/{value['name']}"
            elif isinstance(value, dict) and "model" in value:
                new_topic = f"{base_topic}/{key}/{value['model']}"
            elif isinstance(value, dict) and "range" in value:
                new_topic = f"{base_topic}/{key}/{value['range']}"
            else:
                new_topic = f"{base_topic}/{key}"
            
            publish_recursive(mqtt_util, new_topic, value)

    elif isinstance(data, list):
        for item in data:
            # For list items that are dictionaries, find a descriptive key
            if isinstance(item, dict):
                if "name" in item:
                    item_name = item["name"].replace(" ", "_").replace("/", "_")
                    new_topic = f"{base_topic}/{item_name}"
                elif "model" in item:
                    item_name = item["model"].replace(" ", "_").replace("/", "_")
                    new_topic = f"{base_topic}/{item_name}"
                elif "range" in item:
                    item_name = item["range"].replace(" ", "_").replace("/", "_")
                    new_topic = f"{base_topic}/{item_name}"
                else:
                    # Fallback to a generic, numbered topic if no descriptive key is found
                    new_topic = f"{base_topic}/list_item"
                
                publish_recursive(mqtt_util, new_topic, item)
            else:
                # Handle non-dictionary list items (e.g., strings or numbers)
                new_topic = f"{base_topic}/item"
                publish_recursive(mqtt_util, new_topic, item)
                
    else:
        # This is a primitive value (string, number, boolean), so publish it.
        mqtt_util.publish_message(topic=base_topic, subtopic="", value=json.dumps(data))
        console_log(f"Published topic: '{base_topic}' with value: '{json.dumps(data)}'")

def main(mqtt_util: MqttControllerUtility):
    """
    Publishes the contents of JSON files in the current directory to the MQTT broker,
    flattening the JSON structure into detailed topics using meaningful names.
    
    Args:
        mqtt_util: An instance of MqttControllerUtility passed from the main application.
    """
    current_function_name = inspect.currentframe().f_code.co_name

    debug_log(
        message="🖥️🟢 Entering 'main' to publish JSON datasets.",
        file=current_file,
        version=current_version,
        function=f"dataset_publisher.{current_function_name}",
        console_print_func=console_log
    )
    
    try:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        json_files = [f for f in os.listdir(current_directory) if f.endswith('.json')]

        if not json_files:
            console_log("No JSON files found in the current directory.")
            return

        console_log(f"Found {len(json_files)} JSON file(s) to publish. Publishing recursively...")

        for file_name in json_files:
            file_path = os.path.join(current_directory, file_name)
            root_topic = f"datasets/{os.path.splitext(file_name)[0]}"

            try:
                debug_log(
                    message=f"🔍🔵 Processing file: '{file_name}'",
                    file=current_file,
                    version=current_version,
                    function=f"dataset_publisher.{current_function_name}",
                    console_print_func=console_log
                )
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                publish_recursive(mqtt_util, root_topic, data)
                console_log(f"✅ Finished processing file: '{file_name}'")

            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from file '{file_name}'. Skipping.")
            except Exception as e:
                print(f"An unexpected error occurred while processing '{file_name}': {e}")
            

    
    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        debug_log(
            message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
            file=current_file,
            version=current_version,
            function=f"dataset_publisher.{current_function_name}",
            console_print_func=console_log
        )