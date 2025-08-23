import os
import json
import sys
from workers.mqtt_controller_util import MqttControllerUtility

def publish_recursive(mqtt_util, base_topic, data):
    """
    Recursively publishes nested dictionary and list data to the MQTT broker.
    It constructs the topic using meaningful names from the JSON data.
    """
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
        print(f"Published topic: '{base_topic}' with value: '{json.dumps(data)}'")

def main(mqtt_util: MqttControllerUtility):
    """
    Publishes the contents of JSON files in the current directory to the MQTT broker,
    flattening the JSON structure into detailed topics using meaningful names.
    
    Args:
        mqtt_util: An instance of MqttControllerUtility passed from the main application.
    """
    
    current_directory = os.path.dirname(os.path.abspath(__file__))
    json_files = [f for f in os.listdir(current_directory) if f.endswith('.json')]

    if not json_files:
        print("No JSON files found in the current directory.")
        return

    print(f"Found {len(json_files)} JSON file(s) to publish. Publishing recursively...")

    for file_name in json_files:
        file_path = os.path.join(current_directory, file_name)
        root_topic = f"datasets/{os.path.splitext(file_name)[0]}"

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            publish_recursive(mqtt_util, root_topic, data)

        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from file '{file_name}'. Skipping.")
        except Exception as e:
            print(f"An unexpected error occurred while processing '{file_name}': {e}")