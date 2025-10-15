# managers/manager_settings_frequency.py
#
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
# Version 20250901.221341.10
# FIXED: Removed the call to the non-existent `get_retained_value` method.
# FIXED: Implemented an internal dictionary to track the locked state of controls, preventing feedback loops.
# FIXED: All published float values are now rounded to three decimal places for consistent precision.
# FIXED: Added validation to ensure start and stop frequencies are not negative.

import os
import inspect
import json 

# Assume these are imported from a central logging utility and MQTT controller
from workers.worker_active_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility

# --- Global Scope Variables ---
current_version = "20250901.221341.10"
current_version_hash = (20250901 * 221341 * 10)
current_file = f"{os.path.basename(__file__)}"


class MarkersSettingsManager:
    """
    Manages the logic and synchronization of all frequency-related settings.
    """

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
            debug_log(
                message=f"🔍 Subscribed to '{topic}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _on_message(self, topic, payload):
        # The main message processing callback.
        current_function_name = inspect.currentframe().f_code.co_name
        
        # NEW: Check the internal lock state before processing.
        if self._locked_state.get(topic, False):
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
            
        debug_log(
            message=f"🛠️🔵 Received message on topic '{topic}' with payload '{payload}'. Executing synchronization logic.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            try:
                parsed_payload = json.loads(payload)
                value = parsed_payload.get('value', payload)
            except json.JSONDecodeError:
                value = payload


            # Update local state variables and check for changes before triggering updates.
            if "center_freq_MHz/value" in topic:
                new_val = float(value)
                if self.center_freq is None or abs(self.center_freq - new_val) > 0.001:
                    self.center_freq = new_val
                    self._update_start_stop_from_center_span()
            elif "span_freq_MHz/value" in topic:
                new_val = float(value)
                if self.span_freq is None or abs(self.span_freq - new_val) > 0.001:
                    self.span_freq = new_val
                    self._update_start_stop_from_center_span()
            elif "start_freq_MHz/value" in topic:
                new_val = float(value)
                if self.start_freq is None or abs(self.start_freq - new_val) > 0.001:
                    self.start_freq = new_val
                    self._update_center_and_span_from_start_stop()
            elif "stop_freq_MHz/value" in topic:
                new_val = float(value)
                if self.stop_freq is None or abs(self.stop_freq - new_val) > 0.001:
                    self.stop_freq = new_val
                    self._update_center_and_span_from_start_stop()
            elif "Presets/fields/SPAN/options" in topic:
                if topic.endswith("/value"):
                    option_number = int(topic.split('/')[-2])
                    self.preset_values[option_number] = float(value)
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
            debug_log(
                message=f"🛠️🔴 Arrr, the code be capsized! The frequency logic has failed! The error be: {e}",
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
                debug_log(f"🟡 Warning! Invalid negative frequency values received. Ignoring update.",
                          file=current_file,
                          version=current_version,
                          function=f"{self.__class__.__name__}.{current_function_name}",
                          console_print_func=console_log)
                return
            
            if self.stop_freq < self.start_freq:
                console_log(f"❌ Error: Stop frequency ({self.stop_freq}) cannot be less than start frequency ({self.start_freq}).")
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