# managers/frequency_manager/frequency_callbacks.py

import json
import os
import inspect

from workers.worker_active_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility
from .frequency_state import FrequencyState
from .frequency_yak_communicator import FrequencyYakCommunicator

# --- Global Scope Variables ---
current_file = f"{os.path.basename(__file__)}"
Local_Debug_Enable = False

def debug_log_switch(message, file, version, function, console_print_func):
    if Local_Debug_Enable:
        debug_log(message, file, version, function, console_print_func)

def console_log_switch(message):
    if Local_Debug_Enable:
        console_log(message)


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
            debug_log_switch(
                message=f"🔍 Subscribed to '{topic}'.",
                file=current_file,
                version="N/A",
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
        for yak_suffix in self.yak_communicator.YAK_NAB_OUTPUTS.keys():
            yak_topic = f"{self.yak_communicator.YAK_BASE}/nab/NAB_Frequency_settings/scpi_outputs/{yak_suffix}"
            self.mqtt_controller.add_subscriber(topic_filter=yak_topic, callback_func=self.on_message)
            debug_log_switch(
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
            debug_log_switch(
                message=f"🟡 Message on locked topic '{topic}' received. Ignoring to prevent loop.",
                file=current_file,
                version="N/A",
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            self.state._locked_state[topic] = False
            return
            
        debug_log_switch(
            message=f"🛠️🔵 Received message on topic '{topic}' with payload '{payload}'. Executing synchronization logic.",
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
            
            console_log_switch("✅ Celebration of success! The frequency settings did synchronize!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log_switch(
                message=f"🛠️🔴 Arrr, the code be capsized! The frequency logic has failed! The error be: {e}",
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
                debug_log_switch(f"🟡 Warning! Invalid span value ({self.state.span_freq}) received. Ignoring update.",
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

            debug_log_switch(
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
                debug_log_switch(f"🟡 Warning! Invalid negative frequency values received. Ignoring update.",
                              file=current_file,
                              version="N/A",
                              function=f"{self.__class__.__name__}.{current_function_name}",
                              console_print_func=console_log)
                return
            
            if self.state.stop_freq < self.state.start_freq:
                console_log(f"❌ Error: Stop frequency ({self.state.stop_freq}) cannot be less than start frequency ({self.state.start_freq}).")
                debug_log_switch(f"🟡 Warning! Invalid start/stop combination received. Ignoring update.",
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

            debug_log_switch(
                message=f"🔁 Recalculated center/span from start/stop. Center: {new_center}, Span: {new_span}.",
                file=current_file,
                version="N/A",
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
