# workers/worker_marker_go_getter.py
#
# This worker listens for a start command and then continuously loops through all
# markers from the repository, gets their peak values from the instrument, and
# updates the repository with the new peak data.
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
# Version 20250928.214000.6
# MODIFIED: Removed the brittle threading.Event (peaks_received_event) logic that caused timeouts.
# MODIFIED: Replaced the event wait with a simple time.sleep(1.0) to ensure the NAB query has time to complete.
# MODIFIED: Removed the redundant _on_peak_update_for_event_set function.

import os
import inspect
import json
import pathlib
import threading
import time

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility
from workers.worker_marker_peak_publisher import MarkerPeakPublisher # NEW IMPORT

# --- Global Scope Variables ---
current_version = "20250928.214000.6"
current_version_hash = (20250928 * 214000 * 6)
current_file = f"{os.path.basename(__file__)}"
HZ_TO_MHZ = 1_000_000

# --- MQTT Topic Constants ---
# Control Topics
TOPIC_START_STOP = "OPEN-AIR/configuration/start-stop-pause/Buttons/options/START/selected"

# Marker Repository Topics
TOPIC_MARKERS_ROOT = "OPEN-AIR/repository/markers"
TOPIC_TOTAL_DEVICES = f"{TOPIC_MARKERS_ROOT}/total_devices"
TOPIC_MIN_FREQ = f"{TOPIC_MARKERS_ROOT}/min_frequency_mhz"
TOPIC_MAX_FREQ = f"{TOPIC_MARKERS_ROOT}/max_frequency_mhz"
TOPIC_DEVICE_FREQ_WILDCARD = f"{TOPIC_MARKERS_ROOT}/+/FREQ_MHZ"
TOPIC_DEVICE_PEAK_WILDCARD = f"{TOPIC_MARKERS_ROOT}/+/Peak"

# YAK Frequency Topics
TOPIC_FREQ_START_INPUT = "OPEN-AIR/repository/yak/Frequency/rig/Rig_freq_start_stop/scpi_inputs/start_freq/value"
TOPIC_FREQ_STOP_INPUT = "OPEN-AIR/repository/yak/Frequency/rig/Rig_freq_start_stop/scpi_inputs/stop_freq/value"
TOPIC_FREQ_TRIGGER = "OPEN-AIR/repository/yak/Frequency/rig/Rig_freq_start_stop/scpi_details/generic_model/trigger"

# YAK Marker Placement Topics
TOPIC_MARKER_PLACE_BASE = "OPEN-AIR/repository/yak/Markers/beg/Beg_Place_All_markers/scpi_inputs"
TOPIC_MARKER_PLACE_TRIGGER = "OPEN-AIR/repository/yak/Markers/beg/Beg_Place_All_markers/scpi_details/generic_model/trigger"

# YAK Marker Value Retrieval (NAB) Topics
TOPIC_MARKER_NAB_TRIGGER = "OPEN-AIR/repository/yak/Markers/nab/NAB_all_marker_settings/scpi_details/generic_model/trigger"
TOPIC_MARKER_NAB_OUTPUT_WILDCARD = "OPEN-AIR/repository/yak/Markers/nab/NAB_all_marker_settings/scpi_outputs/Marker_*/value"


class MarkerGoGetterWorker:
    """
    A worker that, when started, continuously fetches peak values for all markers.
    """
    def __init__(self, mqtt_util: MqttControllerUtility):
        # Initializes the worker, sets up state variables, and subscribes to topics.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🟢 Initializing the tireless Marker Go-Getter!",
            file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        self.mqtt_util = mqtt_util
        self.processing_thread = None
        self.stop_event = threading.Event()

        # State variables populated by MQTT
        self.total_devices = 0
        self.min_frequency_mhz = 0.0
        self.max_frequency_mhz = 0.0
        self.marker_frequencies = {}
        
        # REMOVED: self.peaks_received_event is no longer needed for flow control.

        self._setup_subscriptions()

    def _setup_subscriptions(self):
        # Subscribes to all topics required for operation.
        self.mqtt_util.add_subscriber(TOPIC_START_STOP, self._handle_start_stop)
        self.mqtt_util.add_subscriber(TOPIC_TOTAL_DEVICES, self._on_marker_data_update)
        self.mqtt_util.add_subscriber(TOPIC_MIN_FREQ, self._on_marker_data_update)
        self.mqtt_util.add_subscriber(TOPIC_MAX_FREQ, self._on_marker_data_update)
        self.mqtt_util.add_subscriber(TOPIC_DEVICE_FREQ_WILDCARD, self._on_marker_data_update)
        
        # NOTE: The explicit _on_peak_update_for_event_set is now unnecessary and removed.
        
        console_log("✅ Go-Getter is now listening for commands and marker data.")
        
    def _on_marker_data_update(self, topic, payload):
        # Callback to update internal state from the markers repository.
        try:
            # Safely attempt to extract value from a potential JSON payload
            try:
                value = json.loads(payload).get("value")
            except (json.JSONDecodeError, AttributeError):
                value = payload # Fallback to raw payload if not a JSON object

            if topic == TOPIC_TOTAL_DEVICES:
                self.total_devices = int(value)
            elif topic == TOPIC_MIN_FREQ:
                self.min_frequency_mhz = float(value)
            elif topic == TOPIC_MAX_FREQ:
                self.max_frequency_mhz = float(value)
            elif topic.endswith("/FREQ_MHZ"):
                # Check if the topic structure matches a device frequency update
                topic_parts = topic.split('/')
                if len(topic_parts) > 2 and topic_parts[-2].startswith("Device-"):
                    device_id = topic_parts[-2]
                    self.marker_frequencies[device_id] = float(value)
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            console_log(f"🟡 Warning: Could not process marker data update from topic '{topic}': {e}")

    def _handle_start_stop(self, topic, payload):
        # Starts or stops the main processing loop in a separate thread.
        try:
            # Safely extract boolean value
            try:
                is_start_command = str(json.loads(payload).get("value")).lower() == 'true'
            except (json.JSONDecodeError, AttributeError):
                is_start_command = str(payload).lower() == 'true'

            if is_start_command and (self.processing_thread is None or not self.processing_thread.is_alive()):
                console_log("🟢 START command received. Beginning marker peak acquisition loop.")
                self.stop_event.clear()
                self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
                self.processing_thread.start()
            elif not is_start_command:
                console_log("🔴 STOP command received. Halting marker peak acquisition loop.")
                self.stop_event.set()
                if self.processing_thread and self.processing_thread.is_alive():
                    # Give the thread a moment to self-terminate gracefully
                    self.processing_thread.join(timeout=0.5) 
                self.processing_thread = None

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            console_log(f"❌ Error processing start/stop command: {e}")

    def _processing_loop(self):
        # The main logic loop that runs in a thread.
        console_log("✅ Peak Hunter loop started.")
        
        # --- Step 1: Set the instrument to the full frequency span of all markers ---
        console_log(f"🔵 Setting instrument span from {self.min_frequency_mhz} MHz to {self.max_frequency_mhz} MHz.")
        self.mqtt_util.publish_message(TOPIC_FREQ_START_INPUT, "", int(self.min_frequency_mhz * HZ_TO_MHZ), retain=True)
        self.mqtt_util.publish_message(TOPIC_FREQ_STOP_INPUT, "", int(self.max_frequency_mhz * HZ_TO_MHZ), retain=True)
        self.mqtt_util.publish_message(TOPIC_FREQ_TRIGGER, "", True, retain=False)
        self.mqtt_util.publish_message(TOPIC_FREQ_TRIGGER, "", False, retain=False)
        time.sleep(0.1) # Short delay to let the frequency rig command process

        # --- Step 2: Loop through markers in batches of 6 ---
        device_ids = sorted(self.marker_frequencies.keys())

        for i in range(0, len(device_ids), 6):
            if self.stop_event.is_set():
                console_log("Loop terminated by STOP command.")
                break

            batch_ids = device_ids[i:i+6]
            
            # --- NEW: Instantiate the Peak Publisher for the current batch's context ---
            starting_device_id = batch_ids[0]
            
            # 1. Instantiate the passive Peak Publisher to set up subscriptions for this batch
            # This instance will handle the NAB output and republishing for this batch only.
            MarkerPeakPublisher(
                mqtt_util=self.mqtt_util,
                starting_device_id=starting_device_id
            )
            
            console_log(f"🔵 Processing batch starting with {starting_device_id}. {len(batch_ids)} markers sent.")

            # --- 2a. Place Markers: Publish each marker's frequency (in Hz) ---
            for j, device_id in enumerate(batch_ids, 1):
                marker_topic = f"{TOPIC_MARKER_PLACE_BASE}/marker_{j}_freq_hz/value"
                freq_mhz = self.marker_frequencies.get(device_id, 0)
                freq_hz = int(freq_mhz * HZ_TO_MHZ)
                
                self.mqtt_util.publish_message(marker_topic, "", freq_hz, retain=True)
                
                debug_log(
                    message=f"🐐🔵 Place Marker {j}: {device_id} sent {freq_mhz} MHz ({freq_hz} Hz).",
                    file=current_file, version=current_version, function=inspect.currentframe().f_code.co_name,
                    console_print_func=console_log
                )
            
            time.sleep(0.1) # Short delay to let the place markers inputs set

            # --- 2b. Trigger Place Markers command to set them on device ---
            self.mqtt_util.publish_message(TOPIC_MARKER_PLACE_TRIGGER, "", True, retain=False)
            self.mqtt_util.publish_message(TOPIC_MARKER_PLACE_TRIGGER, "", False, retain=False)
            
            # --- CRITICAL FIX: Add recovery sleep to allow the crash to clear ---
            console_log("🟠 Recovering after Marker Placement to clear potential downstream crash...")
            time.sleep(4.0) # Allow 4 seconds for the internal exception/crash to resolve
            
            # --- 2c. Trigger NAB to collect current peaks ---
            console_log("🔵 Sending NAB query to retrieve current peak markers...")
            self.mqtt_util.publish_message(TOPIC_MARKER_NAB_TRIGGER, "", True, retain=False)
            self.mqtt_util.publish_message(TOPIC_MARKER_NAB_TRIGGER, "", False, retain=False)
            
            # --- 2d. Flow Control: Wait for NAB query and publishing to complete ---
            console_log("🟠 Waiting for NAB query and publishing to complete...")
            time.sleep(1.0) # A minimal, safe wait to ensure messages hit the system.

            # --- 2e. Confirmation log ---
            console_log(f"✅ Peak retrieval process initiated for batch: {', '.join(batch_ids)}. Continuing to next batch.")


        console_log("✅ Peak Hunter loop finished a full pass.")
        # If still running, loop will restart after a brief pause
        if not self.stop_event.is_set():
            time.sleep(5)
            self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
            self.processing_thread.start()