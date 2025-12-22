# managers/yak_manager/manager_yak_rx.py
#
# This file (manager_yak_rx.py) processes the response from an SCPI query and publishes the parsed output values to MQTT.
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

import os
import inspect
from workers.logger.logger import debug_log, console_log, log_visa_command
import json


Local_Debug_Enable = True





current_file = f"{os.path.basename(__file__)}"

class YakRxManager:
    """
    Processes responses from the instrument and publishes outputs to MQTT.
    """
    def __init__(self, mqtt_controller):
        self.mqtt_util = mqtt_controller
        self.NAB_BANDWIDTH_TRIGGER_PATH = ['yak', 'Bandwidth', 'nab', 'NAB_bandwidth_settings', 'scpi_details', 'generic_model', 'trigger']

    def process_response(self, path_parts, command_details, response):
        """
        Parses the response and publishes the results to MQTT topics.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        if Local_Debug_Enable:
            debug_log(
                message=f"🐐🐐🐐📡 The agent reports back! Response from device: '{response}'",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )

        outputs = command_details.get("scpi_outputs", {})
        if Local_Debug_Enable:
            debug_log(
                message=f"ℹ️ YakRxManager received a response from the device.",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )
        if Local_Debug_Enable:
            debug_log(
                message=f"ℹ️ Path Parts: {path_parts}",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )
        if Local_Debug_Enable:
            debug_log(
                message=f"ℹ️ Command Details: {json.dumps(outputs, indent=2)}",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )
        if Local_Debug_Enable:
            debug_log(
                message=f"ℹ️ Raw Response: {response}",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )
        
        try:
            # Split the response into individual parts
            response_parts = [p.strip() for p in response.split(';')]
            output_keys = list(outputs.keys())
            
            # --- START FIX: Order Correction for NAB_bandwidth_settings ---
            
            # Check if this is the specific command with the known key swap issue
            if path_parts == self.NAB_BANDWIDTH_TRIGGER_PATH and len(output_keys) >= 5:
                if Local_Debug_Enable:
                    debug_log(
                        message=f"🔍🔵 Detected NAB_bandwidth_settings command with key order issue. Keys before fix: {output_keys}",
                        file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                    )
                
                # Check the order of the 4th and 5th items in the output_keys list
                # Based on the device response, the order is: ..., Continuous_Mode_On, Sweep_Time_s
                # The current YAK metadata order is likely: ..., Sweep_Time_s, Continuous_Mode_On
                
                # The assumption is that output_keys[3] is 'Sweep_Time_s' and output_keys[4] is 'Continuous_Mode_On'
                # if the original YAK metadata was incorrectly specified.
                
                # Since the device sends: [..., VBW_Auto_On, Continuous_Mode_On, Sweep_Time_s]
                # We force the key list to match this order, assuming the metadata stores them as:
                # 0, 1, 2, 4, 3 (for continuous and sweep time)
                
                if output_keys[3].endswith("Time_s") and output_keys[4].endswith("On"):
                    # This indicates the keys are likely SWAPPED in the metadata relative to the SCPI response order.
                    
                    # Create a corrected key list
                    temp_keys = list(output_keys)
                    
                    # Swap keys at index 3 (Continuous_Mode_On) and 4 (Sweep_Time_s) to match device response order
                    # The device gives: [..., val3, val4, val5]
                    # We assume YAK metadata gives: [..., key3, key4, key5]
                    # If key4 and key5 are the ones swapped, we swap them back in the list
                    
                    # NOTE: Since the key definitions in the metadata are fixed, and the SCPI output order is fixed:
                    # SCPI Order (Response Parts Index): 3 = Continuous_Mode_On, 4 = Sweep_Time_s
                    # The YAK metadata is misaligned.
                    
                    # Let's verify what keys are at the incorrect indices and swap them to match the SCPI order
                    
                    # Expected Key at Index 3 (Response Part 4): Continuous_Mode_On/value
                    # Expected Key at Index 4 (Response Part 5): Sweep_Time_s/value

                    key_at_index_3 = output_keys[3]
                    key_at_index_4 = output_keys[4]

                    if key_at_index_3.startswith("Sweep_Time_s") and key_at_index_4.startswith("Continuous_Mode_On"):
                         # SWAP REQUIRED: Swap the 4th and 5th keys in the list to match SCPI order
                        temp_keys[3], temp_keys[4] = temp_keys[4], temp_keys[3]
                        output_keys = temp_keys
                        if Local_Debug_Enable:
                            debug_log(
                                message=f"🛠️🟡 Corrected YAK key swap. Keys after fix: {output_keys}",
                                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                            )
                    
            # --- END FIX ---


            if len(response_parts) != len(output_keys):
                if Local_Debug_Enable:
                    debug_log(
                        message=f"❌🔴 Mismatched response length after potential correction! Expected {len(output_keys)} parts, but received {len(response_parts)}.",
                        file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                    )
                return

            # FIX: Correctly rebuild the base topic by joining the initial path parts
            # The base output topic should be constructed up to '/scpi_outputs'
            # path_parts looks like: ['yak', 'Bandwidth', 'nab', 'NAB_bandwidth_settings', 'scpi_details', 'generic_model', 'trigger']
            # We want: OPEN-AIR/repository/yak/Bandwidth/nab/NAB_bandwidth_settings/scpi_outputs
            base_output_topic_parts = ['OPEN-AIR', 'yak'] + path_parts[:4] + ['scpi_outputs']
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
                if Local_Debug_Enable:
                    debug_log(
                        message=f"💾 Published to '{output_topic}' with value: '{raw_value}'.",
                        file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                    )
            
            console_log("✅ Response processed and all output values published to MQTT.")

        except Exception as e:
            console_log(f"❌ Error processing response: {e}")
            if Local_Debug_Enable:
                debug_log(
                    message=f"❌🔴 The response processing has been shipwrecked! The error be: {e}",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )