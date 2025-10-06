# workers/worker_preset_from_device.py
#
# A worker module to handle the logic for querying, parsing, and presenting
# presets stored on the connected instrument via MQTT.
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
# Version 20250918.002319.2

import os
import inspect
import datetime
import json
import re
import threading
import time

# --- Module Imports ---
from workers.worker_mqtt_controller_util import MqttControllerUtility
from workers.worker_active_logging import debug_log, console_log

# --- Global Scope Variables (as per your instructions) ---
current_date = datetime.datetime.now().strftime("%Y%m%d")
current_time = datetime.datetime.now().strftime("%H%M%S")
current_version = f"{current_date}.{current_time}.2"
current_version_hash = (int(current_date) * int(current_time) * 2)
current_file = f"{os.path.basename(__file__)}"

# --- MQTT Topic Constants (No Magic Numbers) ---
ROOT_TOPIC = "OPEN-AIR/repository/yak/Memory"
NAB_TRIGGER_TOPIC = f"{ROOT_TOPIC}/Nab/Nab_Preset_Catalog/scpi_details/N9342CN/trigger"
NAB_OUTPUT_TOPIC = f"{ROOT_TOPIC}/Nab/Nab_Preset_Catalog/scpi_outputs/preset_catalog_list/value"
SET_FILENAME_TOPIC = f"{ROOT_TOPIC}/Set/Set_Store_Preset/scpi_inputs/preset_fileName/value"
SET_TRIGGER_TOPIC = f"{ROOT_TOPIC}/Set/Set_Store_Preset/scpi_details/N9342CN/trigger"

# --- NEW: MQTT Topic for publishing presets ---
PRESET_REPOSITORY_TOPIC = "OPEN-AIR/repository/presets"

class PresetFromDeviceWorker:
    """
    A worker class that manages preset operations on the device via MQTT.
    """
    def __init__(self, mqtt_util: MqttControllerUtility):
        """
        Initializes the worker and subscribes to the necessary topic.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        self.mqtt_util = mqtt_util
        self.last_preset_list = None
        self.preset_list_event = threading.Event()

        debug_log(
            message=f"🛠️🟢 Initializing preset worker and subscribing to root topic.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        # Subscribe to the master topic and all its sub-levels
        self.mqtt_util.add_subscriber(topic_filter=f"{ROOT_TOPIC}/#", callback_func=self._on_mqtt_message)
    

    def _on_mqtt_message(self, topic, payload):
        """
        A private callback to capture the preset list when it arrives from the device.
        """
        if topic == NAB_OUTPUT_TOPIC:
            self.last_preset_list = payload
            self.preset_list_event.set()
            console_log("✅ A new preset catalog has been received! Time to parse the data.")
            
            valid_presets = self.parse_presets_from_device(self.last_preset_list)
            if valid_presets:
                # Call the new function to publish the presets
                self.publish_presets_to_repository(valid_presets)
        
    def get_presets_from_device(self):
        """
        Triggers the device to query its presets. This function is non-blocking.
        The result is handled by the _on_mqtt_message callback.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🟢 Triggering device to send preset catalog.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # Set the trigger to true
            self.preset_list_event.clear()
            self.mqtt_util.publish_message(topic=NAB_TRIGGER_TOPIC, subtopic="", value=True, retain=False)
            
            # Set the trigger to false immediately afterwards, before waiting
            self.mqtt_util.publish_message(topic=NAB_TRIGGER_TOPIC, subtopic="", value=False, retain=False)

            console_log("✅ TRIGGER sent. Awaiting preset catalog response...")
            return True

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            self.mqtt_util.publish_message(topic=NAB_TRIGGER_TOPIC, subtopic="", value=False, retain=False)
            return False

    def parse_presets_from_device(self, raw_preset_string: str) -> list:
        """
        Parses a raw, comma-separated string of preset data and returns a list
        of valid filenames ending in '.STA'.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🟢 Parsing raw preset string for valid '.STA' files.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        if not raw_preset_string:
            return []
            
        # The first three values are not filenames, so we skip them.
        parts = raw_preset_string.strip().split(',')
        if len(parts) <= 3:
            console_log("❌ Invalid preset string format. Too few parts.")
            return []

        # We start at index 3 and increment by 4 to get each filename
        valid_presets = []
        for i in range(3, len(parts), 4):
            filename = parts[i].strip()
            if filename.upper().endswith(".STA"):
                valid_presets.append(filename)
                
        console_log(f"✅ Found {len(valid_presets)} valid presets.")
        return valid_presets

    def publish_presets_to_repository(self, preset_list: list):
        """
        Takes a list of preset filenames and publishes each attribute to a unique topic.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🟢 Publishing {len(preset_list)} presets to repository.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        for i, filename in enumerate(preset_list):
            if i >= 25:
                break
                
            preset_key = f"PRESET_{100 + i:03d}"
            
            # Create a dictionary for the current preset's data
            preset_data = {
                "Active": True,
                "FileName": filename,
                "NickName": filename,
                "Start": "",
                "Stop": "",
                "Center": "",
                "Span": "",
                "RBW": "",
                "VBW": "",
                "RefLevel": "",
                "Attenuation": "",
                "MaxHold": "",
                "HighSens": "",
                "PreAmp": "",
                "Trace1Mode": "",
                "Trace2Mode": "",
                "Trace3Mode": "",
                "Trace4Mode": "",

            }
            
            # Publish each key-value pair individually
            for key, value in preset_data.items():
                self.mqtt_util.publish_message(
                    topic=f"{PRESET_REPOSITORY_TOPIC}/{preset_key}/{key}",
                    subtopic="",
                    value=value,
                    retain=True
                )
            
        console_log(f"✅ Successfully published {i + 1} presets to the repository.")


    def present_presets_from_device(self, preset_filename: str):
        """
        Sets the specified preset filename and triggers the device to store it.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🟢 Pushing preset filename '{preset_filename}' to device and triggering save.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # 1. Push the filename value via MQTT
            self.mqtt_util.publish_message(topic=SET_FILENAME_TOPIC, subtopic="", value=preset_filename, retain=False)
            
            # 2. Trigger the action to set the preset to 'true'
            self.mqtt_util.publish_message(topic=SET_TRIGGER_TOPIC, subtopic="", value=True, retain=False)

            # 3. Trigger the action to set the preset to 'false' afterwards
            self.mqtt_util.publish_message(topic=SET_TRIGGER_TOPIC, subtopic="", value=False, retain=False)
            
            console_log("✅ Preset filename sent and save triggered.")
            return True

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            return False

if __name__ == "__main__":
    # This block is for demonstrating the worker's functionality
    # outside of the main application.

    class MockMqttUtil:
        def __init__(self):
            self.subscribers = {}
        def add_subscriber(self, topic_filter, callback_func):
            self.subscribers[topic_filter] = callback_func
        def publish_message(self, topic, subtopic, value, retain=False):
            full_topic = f"{topic}/{subtopic}" if subtopic else topic
            print(f"Mock publish: {full_topic} -> {value}")
            if full_topic == NAB_OUTPUT_TOPIC:
                self.subscribers[full_topic](full_topic, value)

    # Mock the MQTT utility and instantiate the worker
    mock_mqtt_util = MockMqttUtil()
    worker = PresetFromDeviceWorker(mqtt_util=mock_mqtt_util)
    
    # Example 1: Get presets from device
    print("\n--- Testing Get_presets_from_device ---")
    mock_response_string = "0,0,0,Preset1.STA,0,0,0,0,Preset2.STA,0,0,0,0,Preset3.STA,0,0,0,0,InvalidFile.txt,0,0,0"
    
    presets_list_str = worker.get_presets_from_device()
    
    if presets_list_str:
        # Manually trigger the message
        worker._on_mqtt_message(NAB_OUTPUT_TOPIC, mock_response_string)
        
        # Example 2: Parse the presets
        print("\n--- Testing Parse_presets_from_device ---")
        valid_presets = worker.parse_presets_from_device(presets_list_str)
        print(f"Valid Presets: {valid_presets}")
        
        # Example 3: Present a single preset to device
        if valid_presets:
            print("\n--- Testing Present_presents_from_device ---")
            worker.present_presets_from_device(valid_presets[0])