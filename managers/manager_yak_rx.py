# managers/manager_yak_rx.py
#
# This manager processes the response from an SCPI query and publishes
# the parsed output values to MQTT.

import os
import inspect
from workers.worker_active_logging import debug_log, console_log
import json

# --- Global Scope Variables ---
current_version = "20250914.225930.4"
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

        outputs = command_details.get("scpi_outputs", {})
        debug_log(
            message=f"ℹ️ YakRxManager received a response from the device.",
            file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
        )
        debug_log(
            message=f"ℹ️ Path Parts: {path_parts}",
            file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
        )
        debug_log(
            message=f"ℹ️ Command Details: {json.dumps(outputs, indent=2)}",
            file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
        )
        debug_log(
            message=f"ℹ️ Raw Response: {response}",
            file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
        )
        
        try:
            # Split the response into individual parts
            response_parts = response.split(';')
            output_keys = list(outputs.keys())

            if len(response_parts) != len(output_keys):
                debug_log(
                    message=f"❌🔴 Mismatched response length! Expected {len(output_keys)} parts, but received {len(response_parts)}.",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
                return

            # FIX: Correctly rebuild the base topic by joining the initial path parts
            # and appending 'scpi_outputs'. The trigger path is intentionally long, 
            # so we truncate it to the command node level, which is the 4th index.
            base_output_topic_parts = ['OPEN-AIR', 'repository'] + path_parts[:4] + ['scpi_outputs']
            base_output_topic = '/'.join(base_output_topic_parts)
            
            # Match and publish each part of the response
            for i, key in enumerate(output_keys):
                raw_value = response_parts[i]
                
                # Construct the full topic for the specific output value
                output_topic = f"{base_output_topic}/{key}/value"
                
                # Publish the value to the MQTT topic
                self.mqtt_util.publish_message(
                    topic=output_topic,
                    subtopic="",
                    value=raw_value,
                    retain=True
                )
                debug_log(
                    message=f"💾 Published to '{output_topic}' with value: '{raw_value}'.",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
            
            console_log("✅ Response processed and all output values published to MQTT.")

        except Exception as e:
            console_log(f"❌ Error processing response: {e}")
            debug_log(
                message=f"❌🔴 The response processing has been shipwrecked! The error be: {e}",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )