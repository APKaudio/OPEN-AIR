# managers/frequency_manager/frequency_callbacks.py
#
# This file (frequency_callbacks.py) handles MQTT message callbacks and logic for frequency settings within the frequency manager.
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251213  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 44 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


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


import json
import os
import inspect

from workers.logger.logger import debug_log, console_log, log_visa_command
from workers.mqtt.worker_mqtt_controller_util import MqttControllerUtility
from .frequency_state import FrequencyState
from .frequency_yak_communicator import FrequencyYakCommunicator

# --- Global Scope Variables ---
current_file = f"{os.path.basename(__file__)}"
Local_Debug_Enable = False





class FrequencyCallbacks:
    """Handles MQTT message callbacks and logic for frequency settings."""

    def __init__(self, mqtt_controller: MqttControllerUtility, state: FrequencyState, yak_communicator: FrequencyYakCommunicator):
        self.mqtt_controller = mqtt_controller
        self.state = state
        self.yak_communicator = yak_communicator
        self.base_topic = self.state.base_topic

    def subscribe_to_topics(self):
        current_function_name = inspect.currentframe().f_code.co_name
        
        topic_list = [
            f"{self.base_topic}/Settings/fields/center_freq_MHz/value",
            f"{self.base_topic}/Settings/fields/span_freq_MHz/value",
            f"{self.base_topic}/Settings/fields/start_freq_MHz/value",
            f"{self.base_topic}/Settings/fields/stop_freq_MHz/value",
        ]
        
        for topic in topic_list:
            self.mqtt_controller.add_subscriber(topic_filter=topic, callback_func=self.on_message)
            if app_constants.Local_Debug_Enable: 
                debug_log(
                    message=f"🔍 Subscribed to '{topic}'.",
                    file=current_file,
                    version="N/A",
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
            
        for yak_suffix in self.yak_communicator.YAK_NAB_OUTPUTS.keys():
            yak_topic = f"{self.yak_communicator.YAK_BASE}/nab/NAB_Frequency_settings/scpi_outputs/{yak_suffix}"
            self.mqtt_controller.add_subscriber(topic_filter=yak_topic, callback_func=self.on_message)
            if app_constants.Local_Debug_Enable: 
                debug_log(
                    message=f"🔍 Subscribed to YAK output '{yak_topic}'.",
                    file=current_file,
                    version="N/A",
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )

    def on_message(self, topic, payload):
        current_function_name = inspect.currentframe().f_code.co_name
        
        if topic.startswith(f"{self.yak_communicator.YAK_BASE}/nab/NAB_Frequency_settings/scpi_outputs"):
            self.yak_communicator.process_yak_output(topic, payload)
            return

        if self.state._locked_state.get(topic, False):
            if app_constants.Local_Debug_Enable: 
                debug_log(
                    message=f"🟡 Message on locked topic '{topic}' received. Ignoring to prevent loop.",
                    file=current_file,
                    version="N/A",
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
            self.state._locked_state[topic] = False
            return
            
        if app_constants.Local_Debug_Enable: 
            debug_log(
                message=f"🟢️️️🔵 Received message on topic '{topic}' with payload '{payload}'. Executing synchronization logic.",
                file=current_file,
                version="N/A",
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
        
        try:
            try:
                parsed_payload = json.loads(payload)
                value_str = parsed_payload.get('value', payload)
            except (json.JSONDecodeError, TypeError):
                value_str = payload

            value = str(value_str).strip().strip('"').strip("'")

            if "center_freq_MHz/value" in topic:
                new_val = float(value)
                if self.state.center_freq is None or abs(self.state.center_freq - new_val) > 0.001:
                    self.state.center_freq = new_val
                    self._update_start_stop_from_center_span()
                    self.yak_communicator.publish_to_yak_and_trigger(new_val, self.yak_communicator.YAK_CENTER_INPUT, self.yak_communicator.YAK_CENTER_TRIGGER)
            elif "span_freq_MHz/value" in topic:
                new_val = float(value)
                if self.state.span_freq is None or abs(self.state.span_freq - new_val) > 0.001:
                    self.state.span_freq = new_val
                    self._update_start_stop_from_center_span()
                    self.yak_communicator.publish_to_yak_and_trigger(new_val, self.yak_communicator.YAK_SPAN_INPUT, self.yak_communicator.YAK_SPAN_TRIGGER)
            elif "start_freq_MHz/value" in topic:
                new_val = float(value)
                if self.state.start_freq is None or abs(self.state.start_freq - new_val) > 0.001:
                    self.state.start_freq = new_val
                    self._update_center_and_span_from_start_stop()
                    self.yak_communicator.publish_to_yak_and_trigger(new_val, self.yak_communicator.YAK_START_INPUT, self.yak_communicator.YAK_START_TRIGGER)
            elif "stop_freq_MHz/value" in topic:
                new_val = float(value)
                if self.state.stop_freq is None or abs(self.state.stop_freq - new_val) > 0.001:
                    self.state.stop_freq = new_val
                    self._update_center_and_span_from_start_stop()
                    self.yak_communicator.publish_to_yak_and_trigger(new_val, self.yak_communicator.YAK_STOP_INPUT, self.yak_communicator.YAK_STOP_TRIGGER)
            
            console_log("✅ The frequency settings did synchronize!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            if app_constants.Local_Debug_Enable: 
                debug_log(
                    message=f"🟢️️️🔴 Arrr, the code be capsized! The frequency logic has failed! The error be: {e}",
                    file=current_file,
                    version="N/A",
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )

    def _update_start_stop_from_center_span(self):
        current_function_name = inspect.currentframe().f_code.co_name
        
        if self.state.center_freq is not None and self.state.span_freq is not None:
            if self.state.span_freq <= 0:
                console_log(f"❌ Error: Frequency span cannot be zero or negative. Value received: {self.state.span_freq}")
                if app_constants.Local_Debug_Enable: 
                    debug_log(f"🟡 Warning! Invalid span value ({self.state.span_freq}) received. Ignoring update.",
                                  file=current_file,
                                  version="N/A",
                                  function=f"{self.__class__.__name__}.{current_function_name}",
                                  console_print_func=console_log)
                return

            new_start = round(self.state.center_freq - (self.state.span_freq / 2.0), 3)
            new_stop = round(self.state.center_freq + (self.state.span_freq / 2.0), 3)
            
            self.state._locked_state[f"{self.base_topic}/Settings/fields/start_freq_MHz/value"] = True
            self.state._locked_state[f"{self.base_topic}/Settings/fields/stop_freq_MHz/value"] = True

            self.state.start_freq = new_start
            self.state.stop_freq = new_stop

            if app_constants.Local_Debug_Enable: 
                debug_log(
                    message=f"🔁 Recalculated start/stop from center/span. Start: {new_start}, Stop: {new_stop}.",
                    file=current_file,
                    version="N/A",
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )

    def _update_center_and_span_from_start_stop(self):
        current_function_name = inspect.currentframe().f_code.co_name
        
        if self.state.start_freq is not None and self.state.stop_freq is not None:
            if self.state.start_freq < 0 or self.state.stop_freq < 0:
                console_log(f"❌ Error: Start and stop frequencies cannot be negative. Start: {self.state.start_freq}, Stop: {self.state.stop_freq}.")
                if app_constants.Local_Debug_Enable: 
                    debug_log(f"🟡 Warning! Invalid negative frequency values received. Ignoring update.",
                                  file=current_file,
                                  version="N/A",
                                  function=f"{self.__class__.__name__}.{current_function_name}",
                                  console_print_func=console_log)
                return
            
            if self.state.stop_freq < self.state.start_freq:
                console_log(f"❌ Error: Stop frequency ({self.state.stop_freq}) cannot be less than start frequency ({self.state.start_freq}).")
                if app_constants.Local_Debug_Enable: 
                    debug_log(f"🟡 Warning! Invalid start/stop combination received. Ignoring update.",
                                  file=current_file,
                                  version="N/A",
                                  function=f"{self.__class__.__name__}.{current_function_name}",
                                  console_print_func=console_log)
                return
                
            new_span = round(self.state.stop_freq - self.state.start_freq, 3)
            new_center = round(self.state.start_freq + (new_span / 2.0), 3)
            
            self.state._locked_state[f"{self.base_topic}/Settings/fields/span_freq_MHz/value"] = True
            self.state._locked_state[f"{self.base_topic}/Settings/fields/center_freq_MHz/value"] = True

            self.state.span_freq = new_span
            self.state.center_freq = new_center

            if app_constants.Local_Debug_Enable: 
                debug_log(
                    message=f"🔁 Recalculated center/span from start/stop. Center: {new_center}, Span: {new_span}.",
                    file=current_file,
                    version="N/A",
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )