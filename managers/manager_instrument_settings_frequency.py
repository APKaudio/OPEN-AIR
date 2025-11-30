# managers/manager_instrument_settings_frequency.py
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251129  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 1 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


# A manager for frequency-related settings, ensuring that center, span, start, and stop
# frequencies remain synchronized based on user-driven changes.
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
# Version 20251014.224313.1
# FIXED: Removed the call to the non-existent `get_retained_value` method.
# FIXED: Implemented an internal dictionary to track the locked state of controls, preventing feedback loops.
# FIXED: All published float values are now rounded to three decimal places for consistent precision.
# FIXED: Added validation to ensure start and stop frequencies are not negative.
# ADDED: Implemented full two-way synchronization with the YAK repository (SCPI device).

import os
import inspect
import json 
import time # Added for delays in triggering YAK commands

# Assume these are imported from a central logging utility and MQTT controller
from workers.worker_active_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility

# --- Global Scope Variables ---
current_version = "20251014.224313.1"
# Hash calculated based on YYYYMMDD * HHMMSS * Revision (20251014 * 224313 * 1)
current_version_hash = (20251014 * 224313 * 1)
current_file = f"{os.path.basename(__file__)}"
Local_Debug_Enable = False


class FrequencySettingsManager:
    """
    Manages the logic and synchronization of all frequency-related settings.
    """
    
    # --- CONSTANTS FOR YAK/SCPI COMMANDS (Protocol 4.1) ---
    HZ_TO_MHZ = 1_000_000
    YAK_BASE = "OPEN-AIR/repository/yak/Frequency"
    YAK_UPDATE_TOPIC = f"{YAK_BASE}/nab/NAB_Frequency_settings/scpi_details/generic_model/trigger"
    
    YAK_CENTER_INPUT = f"{YAK_BASE}/set/set_center_freq_MHz/scpi_inputs/hz_value/value"
    YAK_CENTER_TRIGGER = f"{YAK_BASE}/set/set_center_freq_MHz/scpi_details/generic_model/trigger"

    YAK_SPAN_INPUT = f"{YAK_BASE}/set/set_span_freq_MHz/scpi_inputs/hz_value/value"
    YAK_SPAN_TRIGGER = f"{YAK_BASE}/set/set_span_freq_MHz/scpi_details/generic_model/trigger"

    YAK_START_INPUT = f"{YAK_BASE}/set/set_start_freq_MHz/scpi_inputs/hz_value/value"
    YAK_START_TRIGGER = f"{YAK_BASE}/set/set_start_freq_MHz/scpi_details/generic_model/trigger"

    YAK_STOP_INPUT = f"{YAK_BASE}/set/set_stop_freq_MHz/scpi_inputs/hz_value/value"
    YAK_STOP_TRIGGER = f"{YAK_BASE}/set/set_stop_freq_MHz/scpi_details/generic_model/trigger"
    
    YAK_NAB_OUTPUTS = {
        "start_freq/value": "Settings/fields/start_freq_MHz/value",
        "stop_freq/value": "Settings/fields/stop_freq_MHz/value",
        "center_freq/value": "Settings/fields/center_freq_MHz/value",
        "span_freq/value": "Settings/fields/span_freq_MHz/value",
    }
    
    # --- END CONSTANTS ---

    def __init__(self, mqtt_controller: MqttControllerUtility):
        # Initializes the manager and subscribes to relevant topics.
        current_function_name = inspect.currentframe().f_code.co_name
        
        self.mqtt_controller = mqtt_controller
        self.base_topic = "OPEN-AIR/configuration/instrument/frequency"
        
        # Internal state variables to track current values
        self.center_freq = None
        self.span_freq = None
        self.start_freq = None
        self.stop_freq = None
        
        # Dictionary to store preset values dynamically
        self.preset_values = {}
        
        # NEW: A dictionary to track the locked state of controls.
        self._locked_state = {
            f"{self.base_topic}/Settings/fields/center_freq_MHz/value": False,
            f"{self.base_topic}/Settings/fields/span_freq_MHz/value": False,
            f"{self.base_topic}/Settings/fields/start_freq_MHz/value": False,
            f"{self.base_topic}/Settings/fields/stop_freq_MHz/value": False,
        }
        
        if Local_Debug_Enable:
            debug_log(
                message=f"🛠️🟢 Initializing FrequencySettingsManager and setting up subscriptions.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
        
        self._subscribe_to_topics()

    def _subscribe_to_topics(self):
        # Subscribes to all necessary frequency and preset topics.
        current_function_name = inspect.currentframe().f_code.co_name
        
        topic_list = [
            f"{self.base_topic}/Settings/fields/center_freq_MHz/value",
            f"{self.base_topic}/Settings/fields/span_freq_MHz/value",
            f"{self.base_topic}/Settings/fields/start_freq_MHz/value",
            f"{self.base_topic}/Settings/fields/stop_freq_MHz/value",
        ]
        
        for topic in topic_list:
            self.mqtt_controller.add_subscriber(topic_filter=topic, callback_func=self._on_message)
            if Local_Debug_Enable:
                debug_log(
                    message=f"🔍 Subscribed to '{topic}'.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
            
        # ALSO SUBSCRIBE TO YAK REPOSITORY OUTPUTS (for the UPDATE ALL function)
        for yak_suffix in self.YAK_NAB_OUTPUTS.keys():
            yak_topic = f"{self.YAK_BASE}/nab/NAB_Frequency_settings/scpi_outputs/{yak_suffix}"
            self.mqtt_controller.add_subscriber(topic_filter=yak_topic, callback_func=self._on_message)
            if Local_Debug_Enable:
                debug_log(
                    message=f"🔍 Subscribed to YAK output '{yak_topic}'.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )


    def _publish_to_yak_and_trigger(self, value_mhz, input_topic, trigger_topic):
        # Publishes the value (converted to Hz) to the YAK repository and triggers the SCPI command.
        current_function_name = inspect.currentframe().f_code.co_name
        
        try:
            value_hz = int(round(float(value_mhz) * self.HZ_TO_MHZ))
            
            # 1. Publish the value (Hz) to the YAK input topic
            self.mqtt_controller.publish_message(
                topic=input_topic,
                subtopic="",
                value=value_hz,
                retain=True # Retain the input value
            )

            # 2. Trigger the SCPI command (True then False)
            self.mqtt_controller.publish_message(
                topic=trigger_topic,
                subtopic="",
                value=True,
                retain=False
            )
            # Short delay to allow the trigger to be processed by the manager.
            time.sleep(0.01)
            self.mqtt_controller.publish_message(
                topic=trigger_topic,
                subtopic="",
                value=False,
                retain=False
            )
            
            if Local_Debug_Enable:
                debug_log(
                    message=f"🐐✅ YAK command dispatched. Sent {value_hz} Hz to {input_topic}.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
            
            # 3. Call the master update function to re-synchronize all 4 values.
            self._update_all_from_device()

        except Exception as e:
            console_log(f"❌ Error dispatching YAK command: {e}")
            if Local_Debug_Enable:
                debug_log(
                    message=f"🛠️🔴 YAK dispatch failed! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )

    def _update_all_from_device(self):
        # Implements the 'UPDATE ALL' logic by querying the device for the four values.
        current_function_name = inspect.currentframe().f_code.co_name
        if Local_Debug_Enable:
            debug_log(
                message=f"🐐🟢 Triggering NAB_Frequency_settings to synchronize all 4 frequency values.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
        
        # 1. Trigger the NAB command (True then False)
        self.mqtt_controller.publish_message(
            topic=self.YAK_UPDATE_TOPIC,
            subtopic="",
            value=True,
            retain=False
        )
        time.sleep(0.01) # Short delay
        self.mqtt_controller.publish_message(
            topic=self.YAK_UPDATE_TOPIC,
            subtopic="",
            value=False,
            retain=False
        )
        
        console_log("✅ UPDATE ALL command sent to refresh frequency values from device.")
    

    def _on_message(self, topic, payload):
        # The main message processing callback.
        current_function_name = inspect.currentframe().f_code.co_name
        
        # Handle incoming YAK repository updates first (for the UPDATE ALL function)
        if topic.startswith(f"{self.YAK_BASE}/nab/NAB_Frequency_settings/scpi_outputs"):
            self._process_yak_output(topic, payload)
            return

        # NEW: Check the internal lock state before processing.
        if self._locked_state.get(topic, False):
            if Local_Debug_Enable:
                debug_log(
                    message=f"🟡 Message on locked topic '{topic}' received. Ignoring to prevent loop.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
            # Unlock the topic immediately after receiving the message.
            self._locked_state[topic] = False
            return
            
        if Local_Debug_Enable:
            debug_log(
                message=f"🛠️🔵 Received message on topic '{topic}' with payload '{payload}'. Executing synchronization logic.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
        
        try:
            # --- REVISION: Robustly handle payload parsing and cleaning (fixes 'could not convert string to float: "500"')
            try:
                # 1. Try to load as JSON and extract 'value' key (common for structured payloads)
                parsed_payload = json.loads(payload)
                value_str = parsed_payload.get('value', payload)
            except (json.JSONDecodeError, TypeError):
                # 2. If not JSON, use the raw payload
                value_str = payload

            # 3. Clean the string: strip whitespace, double quotes, and single quotes.
            value = str(value_str).strip().strip('"').strip("'")
            # --- END REVISION ---


            # Update local state variables and check for changes before triggering updates.
            if "center_freq_MHz/value" in topic:
                new_val = float(value)
                if self.center_freq is None or abs(self.center_freq - new_val) > 0.001:
                    self.center_freq = new_val
                    self._update_start_stop_from_center_span()
                    # Trigger YAK command for Center
                    self._publish_to_yak_and_trigger(new_val, self.YAK_CENTER_INPUT, self.YAK_CENTER_TRIGGER)
            elif "span_freq_MHz/value" in topic:
                new_val = float(value)
                if self.span_freq is None or abs(self.span_freq - new_val) > 0.001:
                    self.span_freq = new_val
                    self._update_start_stop_from_center_span()
                    # Trigger YAK command for Span
                    self._publish_to_yak_and_trigger(new_val, self.YAK_SPAN_INPUT, self.YAK_SPAN_TRIGGER)
            elif "start_freq_MHz/value" in topic:
                new_val = float(value)
                if self.start_freq is None or abs(self.start_freq - new_val) > 0.001:
                    self.start_freq = new_val
                    self._update_center_and_span_from_start_stop()
                    # Trigger YAK command for Start
                    self._publish_to_yak_and_trigger(new_val, self.YAK_START_INPUT, self.YAK_START_TRIGGER)
            elif "stop_freq_MHz/value" in topic:
                new_val = float(value)
                if self.stop_freq is None or abs(self.stop_freq - new_val) > 0.001:
                    self.stop_freq = new_val
                    self._update_center_and_span_from_start_stop()
                    # Trigger YAK command for Stop
                    self._publish_to_yak_and_trigger(new_val, self.YAK_STOP_INPUT, self.YAK_STOP_TRIGGER)
            elif "Presets/fields/SPAN/options" in topic:
                if topic.endswith("/value"):
                    option_number = int(topic.split('/')[-2])
                    self.preset_values[option_number] = float(value)
                    if Local_Debug_Enable:
                        debug_log(
                            message=f"💾 Saved preset value: Option {option_number} is {value} MHz.",
                            file=current_file,
                            version=current_version,
                            function=f"{self.__class__.__name__}.{current_function_name}",
                            console_print_func=console_log
                        )
                elif topic.endswith("/selected") and str(value).lower() == 'true':
                    self._update_span_from_preset(topic=topic)
            
            console_log("✅ Celebration of success! The frequency settings did synchronize!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            if Local_Debug_Enable:
                debug_log(
                    message=f"🛠️🔴 Arrr, the code be capsized! The frequency logic has failed! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )

    def _process_yak_output(self, topic, payload):
        # Processes the output from the NAB_Frequency_settings query.
        current_function_name = inspect.currentframe().f_code.co_name
        
        try:
            # 1. Determine which GUI topic corresponds to this YAK output topic
            yak_suffix = topic.split('/scpi_outputs/')[1]
            gui_suffix = self.YAK_NAB_OUTPUTS.get(yak_suffix)
            
            if not gui_suffix:
                if Local_Debug_Enable:
                    debug_log(
                        message=f"🟡 Unknown YAK output suffix: {yak_suffix}. Ignoring.",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}",
                        console_print_func=console_log
                    )
                return

            # 2. Extract the value from the payload (which is Hz from YAK)
            # --- REVISION: Robustly handle payload parsing and cleaning (fixes YAK output errors)
            try:
                # 1. Try to load as JSON and extract 'value' key (YAK's usual format)
                parsed_payload = json.loads(payload)
                value_str = parsed_payload.get('value', payload)
            except (json.JSONDecodeError, ValueError, TypeError):
                # 2. If not JSON, use the raw payload
                value_str = payload

            # 3. Clean the string: strip quotes, backslashes, and whitespace.
            cleaned_value = str(value_str).strip().strip('"').strip("'").strip('\\').strip()
            
            value_hz = float(cleaned_value)
            # --- END REVISION ---
                
            value_mhz = value_hz / self.HZ_TO_MHZ
            
            # 3. Set the lock before publishing back to GUI (to prevent feedback loop)
            full_gui_topic = f"{self.base_topic}/{gui_suffix}"
            self._locked_state[full_gui_topic] = True
            
            # 4. Publish the updated value (in MHz) back to the GUI topic
            self._publish_update(topic_suffix=gui_suffix, value=value_mhz)
            
            if Local_Debug_Enable:
                debug_log(
                    message=f"🐐✅ YAK output processed. Synced {gui_suffix} with {value_mhz} MHz.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
            
        except Exception as e:
            console_log(f"❌ Error processing YAK output for {topic}: {e}")
            if Local_Debug_Enable:
                debug_log(
                    message=f"🛠️🔴 NAB synchronization failed! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
            
    def _update_start_stop_from_center_span(self):
        # Recalculates start and stop frequencies based on center and span.
        current_function_name = inspect.currentframe().f_code.co_name
        
        if self.center_freq is not None and self.span_freq is not None:
            if self.span_freq <= 0:
                console_log(f"❌ Error: Frequency span cannot be zero or negative. Value received: {self.span_freq}")
                if Local_Debug_Enable:
                    debug_log(f"🟡 Warning! Invalid span value ({self.span_freq}) received. Ignoring update.",
                              file=current_file,
                              version=current_version,
                              function=f"{self.__class__.__name__}.{current_function_name}",
                              console_print_func=console_log)
                return

            new_start = round(self.center_freq - (self.span_freq / 2.0), 3)
            new_stop = round(self.center_freq + (self.span_freq / 2.0), 3)
            
            # NEW: Set internal lock before publishing.
            self._locked_state[f"{self.base_topic}/Settings/fields/start_freq_MHz/value"] = True
            self._locked_state[f"{self.base_topic}/Settings/fields/stop_freq_MHz/value"] = True

            self._publish_update(topic_suffix="Settings/fields/start_freq_MHz/value", value=new_start)
            self._publish_update(topic_suffix="Settings/fields/stop_freq_MHz/value", value=new_stop)
            
            if Local_Debug_Enable:
                debug_log(
                    message=f"🔁 Recalculated start/stop from center/span. Start: {new_start}, Stop: {new_stop}.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )

    def _update_center_and_span_from_start_stop(self):
        # Recalculates center and span frequencies based on start and stop.
        current_function_name = inspect.currentframe().f_code.co_name
        
        if self.start_freq is not None and self.stop_freq is not None:
            if self.start_freq < 0 or self.stop_freq < 0:
                console_log(f"❌ Error: Start and stop frequencies cannot be negative. Start: {self.start_freq}, Stop: {self.stop_freq}.")
                if Local_Debug_Enable:
                    debug_log(f"🟡 Warning! Invalid negative frequency values received. Ignoring update.",
                              file=current_file,
                              version=current_version,
                              function=f"{self.__class__.__name__}.{current_function_name}",
                              console_print_func=console_log)
                return
            
            if self.stop_freq < self.start_freq:
                console_log(f"❌ Error: Stop frequency ({self.stop_freq}) cannot be less than start frequency ({self.start_freq}).")
                if Local_Debug_Enable:
                    debug_log(f"🟡 Warning! Invalid start/stop combination received. Ignoring update.",
                              file=current_file,
                              version=current_version,
                              function=f"{self.__class__.__name__}.{current_function_name}",
                              console_print_func=console_log)
                return
                
            new_span = round(self.stop_freq - self.start_freq, 3)
            new_center = round(self.start_freq + (new_span / 2.0), 3)
            
            # NEW: Set internal lock before publishing.
            self._locked_state[f"{self.base_topic}/Settings/fields/span_freq_MHz/value"] = True
            self._locked_state[f"{self.base_topic}/Settings/fields/center_freq_MHz/value"] = True

            self._publish_update(topic_suffix="Settings/fields/span_freq_MHz/value", value=new_span)
            self._publish_update(topic_suffix="Settings/fields/center_freq_MHz/value", value=new_center)
            
            if Local_Debug_Enable:
                debug_log(
                    message=f"🔁 Recalculated center/span from start/stop. Center: {new_center}, Span: {new_span}.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
            
   

    def _publish_update(self, topic_suffix, value):
        # Publishes a message to the specified topic.
        current_function_name = inspect.currentframe().f_code.co_name
        
        full_topic = f"{self.base_topic}/{topic_suffix}"
        
        rounded_value = round(value, 3)
        
        if Local_Debug_Enable:
            debug_log(
                message=f"💾 Publishing new value '{rounded_value}' to topic '{full_topic}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
        
        self.mqtt_controller.publish_message(
            topic=full_topic,
            subtopic="",
            value=rounded_value,
            retain=False
        )