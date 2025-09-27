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
# Version 20250926.223100.1

import os
import inspect
import json
import pathlib
import threading
import time

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility

# --- Global Scope Variables ---
current_version = "20250926.223100.1"
current_version_hash = (20250926 * 223100 * 1)
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
# --- FIX: Corrected the wildcard to represent the entire topic level ---
TOPIC_DEVICE_FREQ_WILDCARD = f"{TOPIC_MARKERS_ROOT}/+/FREQ_MHZ"

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
        
        # For collecting results from NAB command
        self.received_peaks = {}
        self.peaks_received_event = threading.Event()
        self.peaks_lock = threading.Lock()

        self._setup_subscriptions()

    def _setup_subscriptions(self):
        # Subscribes to all topics required for operation.
        self.mqtt_util.add_subscriber(TOPIC_START_STOP, self._handle_start_stop)
        self.mqtt_util.add_subscriber(TOPIC_TOTAL_DEVICES, self._on_marker_data_update)
        self.mqtt_util.add_subscriber(TOPIC_MIN_FREQ, self._on_marker_data_update)
        self.mqtt_util.add_subscriber(TOPIC_MAX_FREQ, self._on_marker_data_update)
        self.mqtt_util.add_subscriber(TOPIC_DEVICE_FREQ_WILDCARD, self._on_marker_data_update)
        self.mqtt_util.add_subscriber(TOPIC_MARKER_NAB_OUTPUT_WILDCARD, self._on_marker_peak_value_received)
        console_log("✅ Go-Getter is now listening for commands and marker data.")

    def _on_marker_data_update(self, topic, payload):
        # Callback to update internal state from the markers repository.
        try:
            value = json.loads(payload).get("value")
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

    def _on_marker_peak_value_received(self, topic, payload):
        # Callback that collects peak values after a NAB command.
        try:
            with self.peaks_lock:
                marker_id = topic.split('/')[-2] # e.g., "Marker_1"
                peak_value = json.loads(payload).get("value")
                self.received_peaks[marker_id] = float(peak_value)
                # If we have collected all 6 peaks, signal the event
                if len(self.received_peaks) >= 6:
                    self.peaks_received_event.set()
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            console_log(f"🟡 Warning: Could not process peak value from topic '{topic}': {e}")

    def _handle_start_stop(self, topic, payload):
        # Starts or stops the main processing loop in a separate thread.
        try:
            is_start_command = str(json.loads(payload).get("value")).lower() == 'true'

            if is_start_command and (self.processing_thread is None or not self.processing_thread.is_alive()):
                console_log("🟢 START command received. Beginning marker peak acquisition loop.")
                self.stop_event.clear()
                self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
                self.processing_thread.start()
            elif not is_start_command:
                console_log("🔴 STOP command received. Halting marker peak acquisition loop.")
                self.stop_event.set()
                if self.processing_thread and self.processing_thread.is_alive():
                    self.processing_thread.join(timeout=.1) # Wait for thread to finish
                self.processing_thread = None

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            console_log(f"❌ Error processing start/stop command: {e}")

    def _processing_loop(self):
        # The main logic loop that runs in a thread.
        console_log("✅ Peak Hunter loop started.")
        

        # --- Step 1: Set the instrument to the full frequency span of all markers ---
        console_log(f"Setting instrument span from {self.min_frequency_mhz} MHz to {self.max_frequency_mhz} MHz.")
        self.mqtt_util.publish_message(TOPIC_FREQ_START_INPUT, "", self.min_frequency_mhz * HZ_TO_MHZ)
        self.mqtt_util.publish_message(TOPIC_FREQ_STOP_INPUT, "", self.max_frequency_mhz * HZ_TO_MHZ)
        self.mqtt_util.publish_message(TOPIC_FREQ_TRIGGER, "", True, retain=False)
        
        self.mqtt_util.publish_message(TOPIC_FREQ_TRIGGER, "", False, retain=False)
        

        # --- Step 2: Loop through markers in batches of 6 ---
        device_ids = sorted(self.marker_frequencies.keys())

        for i in range(0, len(device_ids), 6):
            if self.stop_event.is_set():
                console_log("Loop terminated by STOP command.")
                break

            batch_ids = device_ids[i:i+6]
            console_log(f"Processing batch: {', '.join(batch_ids)}")

            # --- 2a. Place Markers ---
            for j, device_id in enumerate(batch_ids, 1):
                marker_topic = f"{TOPIC_MARKER_PLACE_BASE}/marker_{j}_freq_hz/value"
                freq_hz = int(self.marker_frequencies.get(device_id, 0) * HZ_TO_MHZ)
                self.mqtt_util.publish_message(marker_topic, "", freq_hz)
            
            # --- FIX: Added a delay to allow MQTT messages to be processed before triggering ---
    

            # --- 2b. Trigger Place Markers ---
            self.mqtt_util.publish_message(TOPIC_MARKER_PLACE_TRIGGER, "", True, retain=False)
        
            self.mqtt_util.publish_message(TOPIC_MARKER_PLACE_TRIGGER, "", False, retain=False)
        

            # --- 2c. Clear old results and trigger NAB to collect values ---
            with self.peaks_lock:
                self.received_peaks.clear()
            self.peaks_received_event.clear()
            self.mqtt_util.publish_message(TOPIC_MARKER_NAB_TRIGGER, "", True, retain=False)

            self.mqtt_util.publish_message(TOPIC_MARKER_NAB_TRIGGER, "", False, retain=False)
            
            # --- 2d. Wait for peak values to be received ---
            event_was_set = self.peaks_received_event.wait(timeout=0.1) # 5 second timeout
            
            if not event_was_set:
                console_log(f"🟡 Timeout waiting for peak values for batch starting with {batch_ids[0]}.")
                continue

            # --- 2e. Update Peak values in the repository ---
            with self.peaks_lock:
                for j, device_id in enumerate(batch_ids, 1):
                    marker_id = f"Marker_{j}"
                    if marker_id in self.received_peaks:
                        peak_value = self.received_peaks[marker_id]
                        peak_topic = f"{TOPIC_MARKERS_ROOT}/{device_id}/Peak"
                        self.mqtt_util.publish_message(peak_topic, "", peak_value, retain=True)
                console_log(f"✅ Updated peak values for batch: {', '.join(batch_ids)}")

            

        console_log("✅ Peak Hunter loop finished a full pass.")
        # If still running, loop will restart after a brief pause
        if not self.stop_event.is_set():

            self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
            self.processing_thread.start()

