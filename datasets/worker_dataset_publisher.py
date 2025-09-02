# OPEN-AIR/datasets/worker_dataset_publisher.py
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
# Version 20250901.215800.2

import os
import json
import sys
import inspect
import pathlib
import time
from workers.worker_mqtt_controller_util import MqttControllerUtility

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from display.styling.style import THEMES, DEFAULT_THEME

# --- Global Scope Variables ---
CURRENT_DATE = 20250901
CURRENT_TIME = 215800
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
            # Clean the key for a valid topic path
            clean_key = key.replace(' ', '_').replace('/', '_')

            # Check for a descriptive name within the current dictionary
            if isinstance(value, dict) and "name" in value:
                clean_name = value['name'].replace(' ', '_').replace('/', '_')
                new_topic = f"{base_topic}/{clean_key}/{clean_name}"
            elif isinstance(value, dict) and "model" in value:
                clean_model = value['model'].replace(' ', '_').replace('/', '_')
                new_topic = f"{base_topic}/{clean_key}/{clean_model}"
            elif isinstance(value, dict) and "range" in value:
                clean_range = value['range'].replace(' ', '_').replace('/', '_')
                new_topic = f"{base_topic}/{clean_key}/{clean_range}"
            else:
                new_topic = f"{base_topic}/{clean_key}"
            
            # This is the line that caused the error. The recursive call was building the topic incorrectly.
            # We now call it without the extra slash to avoid the wildcard issue.
            publish_recursive(mqtt_util, new_topic, value)

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                # We assume the unique identifier is the first key in the dictionary.
                item_key = next(iter(item.keys()))
                item_value = item[item_key]

                # We check if the item is a dictionary and has a descriptive name for the topic.
                if isinstance(item_value, dict) and 'name' in item_value:
                    item_name = item_value['name'].replace(' ', '_').replace('/', '_')
                    new_topic = f"{base_topic}/{item_name}"
                elif isinstance(item_value, dict) and 'range' in item_value:
                    item_name = item_value['range'].replace(' ', '_').replace('/', '_')
                    new_topic = f"{base_topic}/{item_name}"
                elif isinstance(item_value, dict) and 'DEVICE' in item_value:
                    item_name = item_value['DEVICE'].replace(' ', '_').replace('/', '_')
                    new_topic = f"{base_topic}/{item_name}"
                elif isinstance(item_value, dict) and 'PRESET' in item_value:
                    item_name = item_value['PRESET'].replace(' ', '_').replace('/', '_')
                    new_topic = f"{base_topic}/{item_name}"
                else:
                    # Fallback to a generic topic if no descriptive key is found.
                    new_topic = f"{base_topic}/{item_key}"

                publish_recursive(mqtt_util, new_topic, item)
            else:
                new_topic = f"{base_topic}"
                publish_recursive(mqtt_util, new_topic, item)
                
    else:
        # This is a primitive value (string, number, boolean), so publish it.
        # This is where the fix is implemented. The topic is cleaned before publishing.
        cleaned_topic = base_topic.replace("#", "").replace("+", "")
        mqtt_util.publish_message(topic=cleaned_topic, subtopic="", value=json.dumps(data))
        console_log(f"Published topic: '{cleaned_topic}' with value: '{json.dumps(data)}'")

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
        
        # Add the nested directory for the sub-app
        sub_app_path = os.path.join(current_directory, 'SUB APP - CSV to json APP')
        if os.path.isdir(sub_app_path):
            sub_app_files = [os.path.join('SUB APP - CSV to json APP', f) for f in os.listdir(sub_app_path) if f.endswith('.json')]
            json_files.extend(sub_app_files)
            
        if not json_files:
            console_log("No JSON files found in the current directory.")
            return

        console_log(f"Found {len(json_files)} JSON file(s) to publish. Publishing recursively...")

        for file_name in json_files:
            file_path = os.path.join(current_directory, file_name)
            
            # Remove the ".json" extension and any "dataset_" prefix.
            base_name = os.path.splitext(os.path.basename(file_name))[0]
            if base_name.startswith("dataset_"):
                base_name = base_name.replace("dataset_", "", 1)
            
            # Replace spaces in the filename with underscores
            base_name_clean = base_name.replace(' ', '_')
            
            # Split the remaining name by underscores to create topic hierarchy
            topic_levels = base_name_clean.split('_')
            
            # Join the levels with a forward slash to form the topic
            file_topic_path = "/".join(topic_levels)
            
            root_topic = f"OPEN-AIR/{file_topic_path}"
            
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

                # Send a preliminary message to clear previous retained messages on this topic.
                mqtt_util.publish_message(topic=f"{root_topic}/#", subtopic="", value="", retain=True)
                
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

if __name__ == "__main__":
    # This block would typically be called from a main application script
    # For standalone testing, you'd need to mock MqttControllerUtility
    print("This script is designed to be imported as a module. Exiting.")