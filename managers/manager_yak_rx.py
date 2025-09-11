# managers/manager_yak_rx.py
#
# This manager processes the response from an SCPI query and publishes
# the parsed output values to MQTT.

import os
import inspect
from workers.worker_logging import debug_log, console_log
import json

# --- Global Scope Variables ---
current_version = "20250909.225412.7"
current_file = f"{os.path.basename(__file__)}"

class YakRxManager:
    """
    Processes responses from the instrument and publishes outputs to MQTT.
    """
    def __init__(self, mqtt_controller):
        self.mqtt_util = mqtt_controller

    def process_response(self, path_parts, command_details, response):
        """
        Parses the response and publishes the results to MQTT topics.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🐐🐐📡 The agent reports back! Response from device: '{response}'",
            file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
        )
        
        outputs = command_details["scpi_outputs"]
        response_parts = response.split(';')

        output_keys = list(outputs.keys())
        for i, key in enumerate(output_keys):
            if i < len(response_parts):
                output_topic = f"OPEN-AIR/repository/yak/{path_parts[1]}/{'/'.join(path_parts[2:-1])}/scpi_outputs/{key}/value"
                self.mqtt_util.publish_message(topic=output_topic, subtopic="", value=response_parts[i])
                debug_log(
                    message=f"🐐🐐🐐💾 Publishing output data. Topic: '{output_topic}', Value: '{response_parts[i]}'",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )