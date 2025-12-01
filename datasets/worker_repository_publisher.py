# OPEN-AIR/datasets/worker_repository_publisher.py
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
# Version 20251013.221941.5
# UPDATED: The main function now exclusively publishes files that start with the prefix 'repository_'.
# FIXED: The recursive publishing logic is updated to handle list of dictionary objects by publishing the inner content as a single JSON blob to prevent excessive nesting.

import os
import json
import sys
import inspect
import pathlib
import time
from workers.worker_mqtt_controller_util import MqttControllerUtility

# --- Module Imports ---
from workers.worker_active_logging import debug_log, console_log
from display.styling.style import THEMES, DEFAULT_THEME

Local_Debug_Enable = False # This flag is checked by the updated debug_log and console_log functions

# --- Global Scope Variables ---
CURRENT_DATE = 20251013
CURRENT_TIME = 221941
REVISION_NUMBER = 5
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME * REVISION_NUMBER)
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")

def publish_recursive(mqtt_util, base_topic, data):
    """
    Recursively publishes nested dictionary and list data to the MQTT broker.
    It constructs the topic using meaningful names from the JSON data.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    
    if isinstance(data, dict):
        for key, value in data.items():
            clean_key = key.replace(' ', '_').replace('/', '_')
            new_topic = f"{base_topic}/{clean_key}"

            # --- NEW: Check for JSON string value (for monolithic publishing) ---
            if isinstance(value, str):
                try:
                    # Attempt to load the value as a dictionary (e.g., preset blob)
                    json_value = json.loads(value)
                    if isinstance(json_value, dict):
                        # If it is a dictionary (like the monolithic preset data), 
                        # publish the entire content as a flat JSON string and STOP recursion.
                        mqtt_util.publish_message(topic=new_topic, subtopic="", value=value, retain=True)
                        console_log(f"Published monolithic topic: '{new_topic}'")
                        continue
                except (json.JSONDecodeError, TypeError):
                    # Not a JSON string or not a dict, proceed with normal recursion
                    pass
            # --- END NEW CHECK ---


            # If the value is a dictionary and contains metadata, publish the metadata
            if isinstance(value, dict) and any(k in value for k in ["type", "AES70", "description"]):
                for sub_key, sub_value in value.items():
                    # Only publish the metadata, not the nested children yet
                    if sub_key not in ["fields"]:
                        publish_recursive(mqtt_util, f"{new_topic}/{sub_key}", sub_value)
                # Now, check for nested fields and recurse
                if "fields" in value:
                    publish_recursive(mqtt_util, f"{new_topic}/fields", value["fields"])
                
            # Check for a descriptive name within the current dictionary
            elif isinstance(value, dict) and "name" in value:
                clean_name = value['name'].replace(' ', '_').replace('/', '_')
                publish_recursive(mqtt_util, f"{base_topic}/{clean_key}/{clean_name}", value)
            elif isinstance(value, dict) and "model" in value:
                clean_model = value['model'].replace(' ', '_').replace('/', '_')
                publish_recursive(mqtt_util, f"{base_topic}/{clean_key}/{clean_model}", value)
            elif isinstance(value, dict) and "range" in value:
                clean_range = value['range'].replace(' ', '_').replace('/', '_')
                publish_recursive(mqtt_util, f"{base_topic}/{clean_key}/{clean_range}", value)
            else:
                publish_recursive(mqtt_util, new_topic, value)
    
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                # We expect the structure to be [{"KEY": {DATA}}]
                item_key = next(iter(item.keys()))
                item_value = item[item_key]

                new_topic = f"{base_topic}/{item_key}"
                
                # Publish the inner content as a JSON string to keep it monolithic and stop recursion here
                mqtt_util.publish_message(topic=new_topic, subtopic="", value=json.dumps(item_value), retain=True)
                console_log(f"Published monolithic topic: '{new_topic}'")
            else:
                # If the list contains simple values, continue recursion
                new_topic = f"{base_topic}"
                publish_recursive(mqtt_util, new_topic, item)
                
    else:
        cleaned_topic = base_topic.replace("#", "").replace("+", "")
        mqtt_util.publish_message(topic=cleaned_topic, subtopic="", value=json.dumps(data), retain=True)
        console_log(f"Published topic: '{cleaned_topic}' with value: '{json.dumps(data)}'")

def main(mqtt_util: MqttControllerUtility):
    """
    Publishes the contents of JSON files that start with 'repository_' in the current
    directory to the MQTT broker, flattening the JSON structure into detailed topics.
    
    Args:
        mqtt_util: An instance of MqttControllerUtility passed from the main application.
    """
    current_function_name = inspect.currentframe().f_code.co_name

    debug_log(
        message="🖥️🟢 Entering 'main' to publish JSON repository files.",
        file=current_file,
        version=current_version,
        function=f"repository_publisher.{current_function_name}",
        console_print_func=console_log
    )
    
    try:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        
        # MODIFIED: Filter for files starting with 'repository_' and ending with '.json'
        json_files = [f for f in os.listdir(current_directory) if f.startswith('repository_') and f.endswith('.json')]
            
        if not json_files:
            console_log("No JSON files starting with 'repository_' found in the current directory.")
            return

        console_log(f"Found {len(json_files)} 'repository_' JSON file(s) to publish. Publishing recursively...")

        for file_name in json_files:
            file_path = os.path.join(current_directory, file_name)
            
            base_name = os.path.splitext(os.path.basename(file_name))[0]
            if base_name.startswith("repository_"):
                base_name = base_name.replace("repository_", "", 1)
            
            base_name_clean = base_name.replace(' ', '_')
            
            topic_levels = base_name_clean.split('_')
            
            file_topic_path = "/".join(topic_levels)
            
            root_topic = f"OPEN-AIR/repository/{file_topic_path}"
            
            try:
                debug_log(
                    message=f"🔍🔵 Processing file: '{file_name}'",
                    file=current_file,
                    version=current_version,
                    function=f"repository_publisher.{current_function_name}",
                    console_print_func=console_log
                )
                with open(file_path, 'r') as f:
                    data = json.load(f)

                mqtt_util.publish_message(topic=f"{root_topic}/#", subtopic="", value="", retain=True)
                
                publish_recursive(mqtt_util, root_topic, data)
                console_log(f"✅ Finished processing file: '{file_name}'")

            except json.JSONDecodeError:
                console_log(f"Error: Could not decode JSON from file '{file_name}'. Skipping.")
            except Exception as e:
                console_log(f"An unexpected error occurred while processing '{file_name}': {e}")
            

    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        debug_log(
            message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
            file=current_file,
            version=current_version,
            function=f"repository_publisher.{current_function_name}",
            console_print_func=console_log
        )

if __name__ == "__main__":
    # This block would typically be called from a main application script
    # For standalone testing, you'd need to mock MqttControllerUtility
    console_log("This script is designed to be imported as a module. Exiting.")
