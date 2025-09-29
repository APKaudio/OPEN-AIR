# workers/worker_marker_peak_publisher.py
#
# This worker listens to the immediate output of the NAB marker command (Marker_1/value, etc.)
# and republishes the received peak value to the final markers repository location.
# It is instantiated with the starting device ID of the current batch to correctly map outputs.
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
# Version 20250928.220600.3
# FIXED: Increased critical sleep delay to 1.0s to ensure the MQTT client processes 
#        the new wildcard subscription before YakRxManager starts publishing.
# MODIFIED: Added verbose debug logging to confirm subscription registration and activation times.

import os
import inspect
import json
import threading
import re
import time # CRITICAL IMPORT

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility

# --- Global Scope Variables ---
current_version = "20250928.220600.3"
current_version_hash = (20250928 * 220600 * 3)
current_file = f"{os.path.basename(__file__)}"

# --- MQTT Topic Constants ---
TOPIC_MARKERS_ROOT = "OPEN-AIR/repository/markers"
TOPIC_MARKER_NAB_OUTPUT_WILDCARD = "OPEN-AIR/repository/yak/Markers/nab/NAB_all_marker_settings/scpi_outputs/Marker_*/value"
NUMBER_OF_MARKERS = 6


class MarkerPeakPublisher:
    """
    Handles subscriptions to the immediate NAB marker output and republishes the values 
    to the correct final Device-ID/Peak topics based on a provided starting device ID.
    """
    def __init__(self, mqtt_util: MqttControllerUtility, starting_device_id: str):
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🛠️🟢 Initializing Peak Publisher for batch starting with {starting_device_id}. STARTING MAP GENERATION.",
            file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        self.mqtt_util = mqtt_util
        self.starting_device_id = starting_device_id
        
        self.marker_to_device_map = self._generate_device_map(starting_device_id)
        debug_log(
            message=f"🛠️🔍 Generated Map: {self.marker_to_device_map}",
            file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        # 1. Register Subscription
        self._setup_subscriptions()
        debug_log(
            message=f"🛠️🟠 Subscription requested. Waiting 1.0s for MQTT client to process wildcard filter...",
            file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        # 2. CRITICAL FIX: Allow 1.0s for subscription to become active
        time.sleep(1.0) 

        console_log(f"✅ Peak Publisher for {starting_device_id} is active and ready to catch peak values.")

    def _generate_device_map(self, start_id: str) -> dict:
        """
        Calculates the next 5 device IDs and maps Marker_1..Marker_6 to them.
        Assumes ID format is 'Device-###'.
        """
        device_map = {}
        # Extract the number from the starting device ID (e.g., 025 from Device-025)
        match = re.search(r'Device-(\d+)', start_id)
        if not match:
            console_log(f"❌ Error: Invalid starting Device ID format: {start_id}")
            return {}

        start_num = int(match.group(1))
        
        for i in range(NUMBER_OF_MARKERS):
            current_num = start_num + i
            # Format the number back to three digits (e.g., 025)
            device_id = f"Device-{current_num:03d}"
            marker_key = f"Marker_{i + 1}"
            device_map[marker_key] = device_id
        
        return device_map
    
    def _setup_subscriptions(self):
        """
        Subscribes to the specific NAB Marker outputs.
        """
        # We subscribe to the wildcard and rely on the callback to handle the topic match.
        self.mqtt_util.add_subscriber(TOPIC_MARKER_NAB_OUTPUT_WILDCARD, self._on_nab_output_and_republish_peak)

    def _on_nab_output_and_republish_peak(self, topic, payload):
        """
        Listens to the NAB query results (Marker_X/value), logs the result, 
        and republishes the peak value to the final Device-ID/Peak topic.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        try:
            # 1. Extract Marker ID and Peak Value
            marker_id = topic.split('/')[-2] # e.g., "Marker_1"
            
            # Safely extract peak value
            try:
                # Value is stored as a JSON string by YakRxManager
                peak_value = json.loads(payload).get("value")
            except (json.JSONDecodeError, AttributeError):
                peak_value = payload # Fallback to raw payload
            
            float_peak_value = float(peak_value)

            # 2. Republishing - Publish to the final repo path
            device_id = self.marker_to_device_map.get(marker_id)
            if device_id:
                final_peak_topic = f"{TOPIC_MARKERS_ROOT}/{device_id}/Peak"
                self.mqtt_util.publish_message(final_peak_topic, "", float_peak_value, retain=True)
                
                debug_log(
                    message=f"🐐💾 REPUBLISH SUCCESS: {device_id} ({marker_id}) peak: {float_peak_value} dBm. Final Topic: {final_peak_topic}",
                    file=current_file, version=current_version, function=current_function_name,
                    console_print_func=console_log
                )
            else:
                debug_log(
                    message=f"🐐🟡 REPUBLISH WARNING: Peak received for {marker_id} but no Device-ID found in batch map.",
                    file=current_file, version=current_version, function=current_function_name,
                    console_print_func=console_log
                )

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            console_log(f"❌ Error processing peak value from topic '{topic}': {e}")
            debug_log(
                message=f"🐐🔴 Repackaging Failed in Publisher: Error: {e}",
                file=current_file, version=current_version, function=current_function_name,
                console_print_func=console_log
            )