# managers/yak_manager/manager_yak_rx.py
#
# This file (manager_yak_rx.py) processes the response from an SCPI query and publishes the parsed output values to MQTT.
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

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
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
from workers.utils.log_utils import _get_log_args
import json


LOCAL_DEBUG_ENABLE = False

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
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"🐐🐐🐐📡 The agent reports back! Response from device: '{response}'",
                **_get_log_args()


            )

        outputs = command_details.get("scpi_outputs", {})
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"ℹ️ YakRxManager received a response from the device.",
                **_get_log_args()


            )        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"ℹ️ Path Parts: {path_parts}",
                **_get_log_args()


            )
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"ℹ️ Command Details: {json.dumps(outputs, indent=2)}",
                **_get_log_args()


            )
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"ℹ️ Raw Response: {response}",
                **_get_log_args()


            )
        
        try:
            # Split the response into individual parts
            response_parts = [p.strip() for p in response.split(';')]
            output_keys = list(outputs.keys())
            
            # --- START FIX: Order Correction for NAB_bandwidth_settings ---
            
            # Check if this is the specific command with the known key swap issue
            if path_parts == self.NAB_BANDWIDTH_TRIGGER_PATH and len(output_keys) >= 5:
                if app_constants.LOCAL_DEBUG_ENABLE: 
                    debug_log(
                        message=f"🔍🔵 Detected NAB_bandwidth_settings command with key order issue. Keys before fix: {output_keys}",
                        **_get_log_args()


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
                        if app_constants.LOCAL_DEBUG_ENABLE: 
                            debug_log(
                                message=f"🟢️️️🟡 Corrected YAK key swap. Keys after fix: {output_keys}",
                                **_get_log_args()


                            )
                    
            # --- END FIX ---


            if len(response_parts) != len(output_keys):
                if app_constants.LOCAL_DEBUG_ENABLE: 
                    debug_log(
                        message=f"❌🔴 Mismatched response length after potential correction! Expected {len(output_keys)} parts, but received {len(response_parts)}.",
                        **_get_log_args()


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
                if app_constants.LOCAL_DEBUG_ENABLE: 
                    debug_log(
                        message=f"💾 Published to '{output_topic}' with value: '{raw_value}'.",
                        **_get_log_args()


                    )
            
            debug_log(message="✅ Response processed and all output values published to MQTT.", **_get_log_args())

        except Exception as e:
            debug_log(message=f"❌ Error processing response: {e}")
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"❌🔴 The response processing has been shipwrecked! The error be: {e}",
                    **_get_log_args()


                )