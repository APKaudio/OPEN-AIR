# workers/worker_active_marker_tune_and_collect.py
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251129  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 1 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


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
# Version 20251006.225130.6

import os
import inspect
import json
import pathlib
import threading
import time

# --- Module Imports ---
from workers.worker_active_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility


# --- Global Scope Variables ---
current_version = "20251006.225130.6"
# The hash calculation drops the leading zero from the hour (e.g., 083015 becomes 83015).
current_version_hash = (20251006 * 225130 * 6)
current_file = f"{os.path.basename(__file__)}"
HZ_TO_MHZ = 1_000_000
Local_Debug_Enable = False

def debug_log_switch(message, file, version, function, console_print_func):
    if Local_Debug_Enable:
        debug_log(message, file, version, function, console_print_func)

def console_log_switch(message):
    if Local_Debug_Enable:
        console_log(message)


# --- NEW CONSTANT: Frequency Buffer (in MHz) ---
BUFFER_START_STOP_MHZ = 0.1

# --- MQTT Topic Constants (UPDATED FOR /IDENTITY NESTING) ---
# Control Topics
TOPIC_START_STOP = "OPEN-AIR/configuration/Start-Stop-Pause/Buttons/options/START/selected"

# Marker Repository Topics
TOPIC_MARKERS_ROOT = "OPEN-AIR/repository/markers"
TOPIC_TOTAL_DEVICES = f"{TOPIC_MARKERS_ROOT}/total_devices"
TOPIC_MIN_FREQ = f"{TOPIC_MARKERS_ROOT}/min_frequency_mhz"
TOPIC_MAX_FREQ = f"{TOPIC_MARKERS_ROOT}/max_frequency_mhz"

# FIX: Update topic to search for frequency inside the /IDENTITY node
TOPIC_DEVICE_FREQ_WILDCARD = f"{TOPIC_MARKERS_ROOT}/+/IDENTITY/FREQ_MHZ"


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
        if Local_Debug_Enable:
            debug_log_switch(
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
        
        # New variables to track frequency state for conditional updates
        self.last_min_freq = None
        self.last_max_freq = None
        self.first_run = True

        # For flow control signaling
        self.peaks_received_event = threading.Event() 

        self._setup_subscriptions()

    def _setup_subscriptions(self):
        # Subscribes to all topics required for operation.
        self.mqtt_util.add_subscriber(TOPIC_START_STOP, self._handle_start_stop)
        self.mqtt_util.add_subscriber(TOPIC_TOTAL_DEVICES, self._on_marker_data_update)
        self.mqtt_util.add_subscriber(TOPIC_MIN_FREQ, self._on_marker_data_update)
        self.mqtt_util.add_subscriber(TOPIC_MAX_FREQ, self._on_marker_data_update)
        # FIX: Subscribes to the new wildcard topic for marker frequency
        self.mqtt_util.add_subscriber(TOPIC_DEVICE_FREQ_WILDCARD, self._on_marker_data_update)
        
        # Subscribe to the NAB outputs directly to set the flow control event.
        # FIXED: This method was missing but is now the target of the NAB outputs.
        self.mqtt_util.add_subscriber(TOPIC_MARKER_NAB_OUTPUT_WILDCARD, self._on_peak_update_for_event_set)
        
        console_log_switch("✅ Go-Getter is now listening for commands and marker data.")


    def _on_peak_update_for_event_set(self, topic, payload):
        """
        A placeholder method to satisfy the subscription. In a non-mock setup,
        this would signal a threading event to continue the main processing loop.
        """
        self.peaks_received_event.set()
        
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
            # FIX: Check if the topic structure matches a device frequency update inside /IDENTITY
            elif topic.endswith("/IDENTITY/FREQ_MHZ"):
                topic_parts = topic.split('/')
                # The Device-XXX ID is the third part from the end: .../Device-XXX/IDENTITY/FREQ_MHZ
                if len(topic_parts) >= 4 and topic_parts[-3].startswith("Device-"):
                    device_id = topic_parts[-3]
                    self.marker_frequencies[device_id] = float(value)
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            console_log_switch(f"🟡 Warning: Could not process marker data update from topic '{topic}': {e}")

    def _handle_start_stop(self, topic, payload):
        # Starts or stops the main processing loop in a separate thread.
        try:
            # Safely extract boolean value
            try:
                is_start_command = str(json.loads(payload).get("value")).lower() == 'true'
            except (json.JSONDecodeError, AttributeError):
                is_start_command = str(payload).lower() == 'true'

            if is_start_command and (self.processing_thread is None or not self.processing_thread.is_alive()):
                console_log_switch("🟢 START command received. Beginning marker peak acquisition loop.")
                self.stop_event.clear()
                # Reset first run flag when starting a new sequence
                self.first_run = True
                self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
                self.processing_thread.start()
            elif not is_start_command:
                console_log_switch("🔴 STOP command received. Halting marker peak acquisition loop.")
                self.stop_event.set()
                if self.processing_thread and self.processing_thread.is_alive():
                    # Give the thread a moment to self-terminate gracefully
                    self.processing_thread.join(timeout=0.5) 
                self.processing_thread = None

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            console_log(f"❌ Error processing start/stop command: {e}")

    
    def _place_markers_for_batch(self, batch_ids):
        """
        MODULAR FUNCTION: Sets the frequency of up to 6 markers and triggers the 
        placement command.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        # --- 1. Place Markers: Publish each marker's frequency (in Hz) ---
        for j, device_id in enumerate(batch_ids, 1):
            marker_topic = f"{TOPIC_MARKER_PLACE_BASE}/marker_{j}_freq_hz/value"
            freq_mhz = self.marker_frequencies.get(device_id, 0)
            freq_hz = int(freq_mhz * HZ_TO_MHZ)
            
            self.mqtt_util.publish_message(topic=marker_topic, subtopic="", value=freq_hz, retain=True)
            
            if Local_Debug_Enable:
                debug_log_switch(
                    message=f"🐐🔵 Place Marker {j}: {device_id} sent {freq_mhz} MHz ({freq_hz} Hz).",
                    file=current_file, version=current_version, function=current_function_name,
                    console_print_func=console_log
                )
        
        time.sleep(0.2) # Short delay to let the place markers inputs set

        # --- 2. Trigger Place Markers command to set them on device ---
        self.mqtt_util.publish_message(TOPIC_MARKER_PLACE_TRIGGER, "", True, retain=False)
        self.mqtt_util.publish_message(TOPIC_MARKER_PLACE_TRIGGER, "", False, retain=False)
        
        # --- 3. CRITICAL FIX: Add recovery sleep to allow the crash to clear ---
        console_log_switch("🟠 Recovering after Marker Placement to clear potential downstream crash...")
        time.sleep(0.3) # Allow 4 seconds for the internal exception/crash to resolve
        
    def _query_markers_for_batch(self, batch_ids):
        """
        NEW FUNCTION: Triggers the NAB query to read the marker peak values.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        # --- 1. Trigger NAB to collect current peaks ---
        console_log_switch("🔵 Sending NAB query to retrieve current peak markers...")
        self.mqtt_util.publish_message(TOPIC_MARKER_NAB_TRIGGER, "", True, retain=False)
        self.mqtt_util.publish_message(TOPIC_MARKER_NAB_TRIGGER, "", False, retain=False)
        
        # --- 2. Flow Control: Wait for NAB query and publishing to complete ---
        console_log_switch("🟠 Waiting for NAB query and publishing to complete...")
        time.sleep(0.2) # A minimal, safe wait to ensure messages hit the system.

        console_log_switch(f"✅ Peak retrieval process initiated for batch: {', '.join(batch_ids)}.")
        
    def _set_instrument_frequency_span(self):
        """
        Sets the instrument to the full frequency span of all markers, 
        but only if the min/max frequency has changed or if it's the first run.
        """
        current_function_name = inspect.currentframe().f_code.co_name

        if (self.min_frequency_mhz == self.last_min_freq and
            self.max_frequency_mhz == self.last_max_freq and
            not self.first_run):
            
            if Local_Debug_Enable:
                debug_log_switch(
                    message="🛠️🟡 Min/Max frequencies unchanged. Skipping span update.",
                    file=current_file, version=current_version, function=current_function_name,
                    console_print_func=console_log
                )
            return

        # Update last known state
        self.last_min_freq = self.min_frequency_mhz
        self.last_max_freq = self.max_frequency_mhz
    
        # --- APPLY THE BUFFER HERE ---
        # Add buffer to the maximum frequency
        new_max_freq = self.max_frequency_mhz + BUFFER_START_STOP_MHZ
        # Subtract buffer from the minimum frequency (ensuring it doesn't go below zero)
        new_min_freq = max(0, self.min_frequency_mhz - BUFFER_START_STOP_MHZ)
        
        console_log_switch(f"🔵 Setting instrument span from {new_min_freq} MHz to {new_max_freq} MHz (with {BUFFER_START_STOP_MHZ} MHz buffer).")
        self.mqtt_util.publish_message(TOPIC_FREQ_START_INPUT, "", int(new_min_freq * HZ_TO_MHZ), retain=True)
        self.mqtt_util.publish_message(TOPIC_FREQ_STOP_INPUT, "", int(new_max_freq * HZ_TO_MHZ), retain=True)
        self.mqtt_util.publish_message(TOPIC_FREQ_TRIGGER, "", True, retain=False)
        self.mqtt_util.publish_message(TOPIC_FREQ_TRIGGER, "", False, retain=False)
        time.sleep(0.1) # Short delay to let the frequency rig command process
        
        self.first_run = False
        console_log_switch("✅ Instrument span set successfully.")
        


    def _processing_loop(self):
        # The main logic loop that runs in a thread.
        console_log_switch("✅ Peak Hunter loop started.")
        
        # --- Loop Control: Check the stop event first ---
        while not self.stop_event.is_set():
            # NOTE: Removed redundant check on TOPIC_START_STOP as stop_event handles thread control.
            
            # --- Step 1: Set the instrument to the full frequency span of all markers (Conditional) ---
            self._set_instrument_frequency_span()
            
            # --- Step 2: Loop through markers in batches of 6 ---
            device_ids = sorted(self.marker_frequencies.keys())

            for i in range(0, len(device_ids), 6):
                if self.stop_event.is_set():
                    console_log_switch("Loop terminated by STOP command during batch processing.")
                    break

                batch_ids = device_ids[i:i+6]
                
                # Use the dedicated modular function to handle marker placement
                self._place_markers_for_batch(batch_ids=batch_ids)

                # --- DELAY as requested ---
                time.sleep(0.5)
                
                # Use the dedicated modular function to query the batch
                self._query_markers_for_batch(batch_ids=batch_ids)

                # --- Confirmation log and flow control ---
                console_log_switch(f"✅ Batch {i//6 + 1} processed. Continuing to next batch.")


            console_log_switch("✅ Peak Hunter loop finished a full pass.")
            


# --- TUNING HELPER FUNCTIONS (Moved from worker_marker_tune_to_marker.py) ---

def Push_Marker_to_Center_Freq(mqtt_controller, marker_data):
    """
    Publishes MQTT messages to set the instrument's center frequency and span
    based on a selected marker, and then triggers the SCPI command.
    """
    current_function = inspect.currentframe().f_code.co_name
    if Local_Debug_Enable:
        debug_log_switch(
            message="🛠️🟢 Received request to tune to marker. Processing data...",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )

    try:
        # Define the MQTT topics as constants
        CENTER_FREQ_TOPIC = "OPEN-AIR/repository/yak/Frequency/beg/Beg_freq_center_span/scpi_inputs/center_freq/value"
        SPAN_FREQ_TOPIC = "OPEN-AIR/repository/yak/Frequency/beg/Beg_freq_center_span/scpi_inputs/span_freq/value"
        TRIGGER_TOPIC = "OPEN-AIR/repository/yak/Frequency/beg/Beg_freq_center_span/scpi_details/generic_model/trigger"
        
        DEFAULT_SPAN_HZ = 1000000 # 1 MHz
        
        freq_mhz = marker_data.get('FREQ_MHZ', None)
        if freq_mhz is None:
            if Local_Debug_Enable:
                debug_log_switch(
                    message="❌🔴 Error: Marker data is missing the 'FREQ_MHZ' key.",
                    file=current_file,
                    version=current_version,
                    function=f"{current_function}",
                    console_print_func=console_log
                )
            console_log("❌ Failed to tune: Marker data is incomplete.")
            return

        try:
            freq_mhz = float(freq_mhz)
            # FIX: Convert to integer for HZ value
            center_freq_hz = int(freq_mhz * HZ_TO_MHZ)
        except (ValueError, TypeError) as e:
            if Local_Debug_Enable:
                debug_log_switch(
                    message=f"❌🔴 Error converting frequency to float: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{current_function}",
                    console_print_func=console_log
                )
            console_log("❌ Failed to tune: Invalid frequency value.")
            return

        if Local_Debug_Enable:
            debug_log_switch(
                message=f"🔍 Freq from marker: {freq_mhz} MHz -> {center_freq_hz} Hz. Setting Span to {DEFAULT_SPAN_HZ} Hz.",
                file=current_file,
                version=current_version,
                function=f"{current_function}",
                console_print_func=console_log
            )
        
        # FIX: Ensure all values published are integers
        mqtt_controller.publish_message(topic=CENTER_FREQ_TOPIC, subtopic="", value=center_freq_hz)
        console_log_switch(f"✅ Set CENTER_FREQ to {center_freq_hz} Hz.")
        
        mqtt_controller.publish_message(topic=SPAN_FREQ_TOPIC, subtopic="", value=int(DEFAULT_SPAN_HZ))
        console_log_switch(f"✅ Set SPAN_FREQ to {int(DEFAULT_SPAN_HZ)} Hz.")
        
        mqtt_controller.publish_message(topic=TRIGGER_TOPIC, subtopic="", value=True)
        if Local_Debug_Enable:
            debug_log_switch(
                message="🛠️🔵 Trigger set to True. Awaiting instrument response.",
                file=current_file,
                version=current_version,
                function=f"{current_function}",
                console_print_func=console_log
            )
        
        mqtt_controller.publish_message(topic=TRIGGER_TOPIC, subtopic="", value=False)
        if Local_Debug_Enable:
            debug_log_switch(
                message="🛠️🔵 Trigger reset to False. Command sequence complete.",
                file=current_file,
                version=current_version,
                function=f"{current_function}",
                console_print_func=console_log
            )
        
        console_log_switch("✅ Tuning command sequence complete.")

    except Exception as e:
        if Local_Debug_Enable:
            debug_log_switch(
                message=f"❌🔴 Critical error during marker tuning: {e}",
                file=current_file,
                version=current_version,
                function=f"{current_function}",
                console_print_func=console_log
            )
        console_log(f"❌ An error occurred while tuning to the marker: {e}")

def Push_Marker_to_Start_Stop_Freq(mqtt_controller, marker_data, buffer=1e6):
    """
    Calculates start and stop frequencies based on a marker frequency and a buffer,
    then publishes the values and triggers the SCPI command.
    """
    current_function = inspect.currentframe().f_code.co_name
    if Local_Debug_Enable:
        debug_log_switch(
            message=f"🛠️🟢 Received request to tune with a buffer. Buffer is {buffer} Hz. Processing data...",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )

    try:
        # Define the MQTT topics as constants
        START_FREQ_TOPIC = "OPEN-AIR/repository/yak/Frequency/beg/Beg_freq_start_stop/scpi_inputs/start_freq/value"
        STOP_FREQ_TOPIC = "OPEN-AIR/repository/yak/Frequency/beg/Beg_freq_start_stop/scpi_inputs/stop_freq/value"
        START_STOP_TRIGGER_TOPIC = "OPEN-AIR/repository/yak/Frequency/beg/Beg_freq_start_stop/scpi_details/generic_model/trigger"
        
        freq_mhz = marker_data.get('FREQ_MHZ', None)
        if freq_mhz is None:
            if Local_Debug_Enable:
                debug_log_switch(
                    message="❌🔴 Error: Marker data is missing the 'FREQ_MHZ' key.",
                    file=current_file,
                    version=current_version,
                    function=f"{current_function}",
                    console_print_func=console_log
                )
            console_log("❌ Failed to tune: Marker data is incomplete.")
            return

        try:
            freq_mhz = float(freq_mhz)
            center_freq_hz = freq_mhz * HZ_TO_MHZ
        except (ValueError, TypeError) as e:
            if Local_Debug_Enable:
                debug_log_switch(
                    message=f"❌🔴 Error converting frequency to float: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{current_function}",
                    console_print_func=console_log
                )
            console_log("❌ Failed to tune: Invalid frequency value.")
            return

        # Calculate start and stop frequencies
        # FIX: Convert to integer for HZ value
        start_freq_hz = int(center_freq_hz - buffer)
        stop_freq_hz = int(center_freq_hz + buffer)

        if Local_Debug_Enable:
            debug_log_switch(
                message=f"🔍 Calculated range: Start={start_freq_hz} Hz, Stop={stop_freq_hz} Hz.",
                file=current_file,
                version=current_version,
                function=f"{current_function}",
                console_print_func=console_log
            )
        
        # Publish start frequency
        mqtt_controller.publish_message(topic=START_FREQ_TOPIC, subtopic="", value=start_freq_hz)
        console_log_switch(f"✅ Set START_FREQ to {start_freq_hz} Hz.")
        
        # Publish stop frequency
        mqtt_controller.publish_message(topic=STOP_FREQ_TOPIC, subtopic="", value=stop_freq_hz)
        console_log_switch(f"✅ Set STOP_FREQ to {stop_freq_hz} Hz.")
        
        # Trigger SCPI command
        mqtt_controller.publish_message(topic=START_STOP_TRIGGER_TOPIC, subtopic="", value=True)
        if Local_Debug_Enable:
            debug_log_switch(
                message="🛠️🔵 Trigger set to True. Awaiting instrument response.",
                file=current_file,
                version=current_version,
                function=f"{current_function}",
                console_print_func=console_log
            )
        
        # Reset the trigger
        mqtt_controller.publish_message(topic=START_STOP_TRIGGER_TOPIC, subtopic="", value=False)
        if Local_Debug_Enable:
            debug_log_switch(
                message="🛠️🔵 Trigger reset to False. Command sequence complete.",
                file=current_file,
                version=current_version,
                function=f"{current_function}",
                console_print_func=console_log
            )
        
        console_log_switch("✅ Tuning command sequence complete.")

    except Exception as e:
        if Local_Debug_Enable:
            debug_log_switch(
                message=f"❌🔴 Critical error during marker tuning with buffer: {e}",
                file=current_file,
                version=current_version,
                function=f"{current_function}",
                console_print_func=console_log
            )
        console_log(f"❌ An error occurred while tuning to the marker with a buffer: {e}")