# managers/manager_yakety_yak.py
#
# This manager listens for MQTT messages containing SCPI command details,
# constructs the final command string, and passes it to the ScpiDispatcher for execution.
# This file also includes the high-level API functions for issuing commands, effectively
# combining the previous `Yak` agent with the manager.
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
# Version 20250907.011500.12
# FIXED: The _on_repo_message function now correctly identifies and forwards trigger payloads
# to a dedicated _on_trigger function, creating a clean separation between data storage and command execution.
# UPDATED: The _on_repo_message now explicitly ignores trigger payloads.

import os
import inspect
import json
import re

# --- Utility and Manager Imports ---
from workers.worker_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility
from managers.manager_visa_dispatch_scpi import ScpiDispatcher

# --- Global Scope Variables (as per Protocol 4.4) ---
current_version = "20250907.011500.12"
current_version_hash = (20250907 * 11500 * 12)
current_file = f"{os.path.basename(__file__)}"


class YaketyYakManager:
    """
    Orchestrates SCPI command execution by listening to MQTT topics,
    processing command templates, and dispatching commands via the integrated Yak API.
    """
    def __init__(self, mqtt_controller, dispatcher_instance, app_instance):
        # Initializes the YaketyYak manager.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🐐🐐🟢 Entering {current_function_name}. The Yakety Yak manager is coming to life! My creation awakens!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            self.mqtt_util = mqtt_controller
            self.dispatcher = dispatcher_instance
            self.app_instance = app_instance
            self.command_repo = {}

            debug_log(
                message=f"🐐🐐🐐🔵 The manager's components are being wired up: mqtt_util={mqtt_controller}, dispatcher={dispatcher_instance}, app={app_instance}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

            # Subscribe to the repository to build the command structure
            repo_topic = "OPEN-AIR/repository/yak/#"
            self.mqtt_util.add_subscriber(
                topic_filter=repo_topic,
                callback_func=self._on_repo_message
            )
            debug_log(
                message=f"🐐🐐🐐🔍 I've set a trap! Listening for command blueprints on topic '{repo_topic}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

            # Subscribe to GUI actions to trigger commands
            action_topic = "OPEN-AIR/actions/yak/#"
            self.mqtt_util.add_subscriber(
                topic_filter=action_topic,
                callback_func=self._on_action_message
            )
            
            # FIXED: Subscribe to the specific trigger topic from the repository to separate it from other repository data
            self.mqtt_util.add_subscriber(
                topic_filter="OPEN-AIR/repository/yak/+/+/+/+/+/+/trigger",
                callback_func=self._on_trigger
            )
            self.mqtt_util.add_subscriber(
                topic_filter="OPEN-AIR/repository/yak/+/+/+/+/+/+/+/trigger",
                callback_func=self._on_trigger
            )
            self.mqtt_util.add_subscriber(
                topic_filter="OPEN-AIR/repository/yak/+/+/+/+/+/+/+/+/trigger",
                callback_func=self._on_trigger
            )
            
            debug_log(
                message=f"🐐🐐🐐📡 My ears are twitching! Awaiting GUI action commands on topic '{action_topic}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

            console_log("✅ Success! The YaketyYak Manager has initialized and is listening.")
            debug_log(
                message=f"🐐🐐🐐✅ It's ALIVE! The manager is fully operational and awaiting instructions.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🐐🐐🐐🔴 The manager's brain has short-circuited during initialization! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    # FIXED: The _on_repo_message now acts as a router, forwarding trigger events and storing other data.
    def _on_repo_message(self, topic, payload):
        # Dynamically builds the internal command repository from MQTT messages.
        current_function_name = inspect.currentframe().f_code.co_name
        
        # FIXED: Check if the message is a trigger and forward it to the trigger handler
        if topic.endswith('/trigger'):
            self._on_trigger(topic, payload)
            return

        try:
            parts = topic.split('/')[2:] # Skip OPEN-AIR/repository
            current_level = self.command_repo
            for part in parts[:-1]:
                current_level = current_level.setdefault(part, {})
            
            try:
                parsed_payload = json.loads(payload)
                if isinstance(parsed_payload, dict) and 'value' in parsed_payload:
                    value = parsed_payload['value']
                else:
                    value = parsed_payload
            except (json.JSONDecodeError, TypeError):
                value = payload

            current_level[parts[-1]] = value
            
            debug_log(
                message=f"🐐🐐🐐💾 Storing repository data. Topic segment: '{parts[-1]}', Value: '{value}'",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )

        except (json.JSONDecodeError, IndexError) as e:
            console_log(f"Could not parse repository message for topic {topic}: {e}")
            debug_log(
                message=f"🐐🐐🐐🔴 Blast it! The repository message was gibberish. Topic: '{topic}', Error: {e}",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )


    def _on_action_message(self, topic, payload):
        # This function is now the listener for commands published to the /actions topic.
        # This function does not handle triggers published to the /repository topic.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🐐🐐⚡️ Action stations! A command has arrived! Topic: '{topic}', Payload: '{payload}'",
            file=current_file, version=current_version, function=current_function_name,
            console_print_func=console_log
        )
        if not topic.endswith('/trigger'):
            return

        try:
            payload_data = json.loads(payload)
            if str(payload_data.get('value')).lower() != 'true':
                return
            
            parts = topic.split('/')[3:-3] 
            yak_type = parts[0]
            command_path_list = parts[1:]
            command_path = ".".join(command_path_list)

            debug_log(
                message=f"🐐🐐🐐🔵 Command analysis complete. Type is '{yak_type}', Path is '{command_path}'.",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )

            command_details = self.command_repo.get("yak", {}).get(yak_type, {})
            for part in command_path_list:
                command_details = command_details.get(part, {})

            if not command_details:
                console_log(f"❌ Could not find command details for topic: {topic}")
                debug_log(
                    message=f"🐐🐐🐐🟡 Aborting! The command blueprints for '{topic}' are missing from my glorious repository!",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
                return

            model = self.dispatcher.get_model()
            manufacturer = self.dispatcher.get_manufacturer()
            
            scpi_details = command_details.get("scpi_details", {})
            scpi_template = None
            
            if manufacturer in scpi_details and model in scpi_details[manufacturer]:
                scpi_template_details = scpi_details[manufacturer][model]
                scpi_template = scpi_template_details.get("SCPI_value")
                
            if not scpi_template and "generic_maker" in scpi_details and "generic_model" in scpi_details["generic_maker"]:
                scpi_template_details = scpi_details["generic_maker"]["generic_model"]
                scpi_template = scpi_template_details.get("SCPI_value")

            if not scpi_template:
                console_log(f"❌ Could not find SCPI command template for device {manufacturer} {model} or a generic one.")
                debug_log(
                    message=f"🐐🐐🐐🔴 Failure! No SCPI template could be found at all. The experiment cannot proceed.",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
                return

            command_string = scpi_template
            input_values = payload_data.get('scpi_inputs', {})
            for key, value in input_values.items():
                command_string = command_string.replace(f"<{key}>", str(value))
            command_string = re.sub(r'<[^>]+>', '', command_string).strip()

            if yak_type.lower() in ['get', 'nab']:
                debug_log(
                    message=f"🐐🐐🐐🚀 Engaging the '{yak_type}' API! Dispatching query command now!",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
                response = self.dispatcher.query_safe(command_string)
            else:
                debug_log(
                    message=f"🐐🐐🐐🚀 Engaging the '{yak_type}' API! Dispatching write command now!",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
                response = self.dispatcher.write_safe(command_string)
            
            debug_log(
                message=f"🐐🐐🐐📡 The agent reports back! Response from device: '{response}'",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )

            if response not in ["PASSED", "FAILED", None] and "scpi_outputs" in command_details:
                outputs = command_details["scpi_outputs"]
                response_parts = response.split(';')

                output_keys = list(outputs.keys())
                for i, key in enumerate(output_keys):
                    if i < len(response_parts):
                        output_topic = f"OPEN-AIR/repository/yak/{yak_type}/{'/'.join(command_path_list)}/scpi_outputs/{key}/value"
                        self.mqtt_util.publish_message(topic=output_topic, subtopic="", value=response_parts[i])
                        debug_log(
                            message=f"🐐🐐🐐💾 Publishing output data. Topic: '{output_topic}', Value: '{response_parts[i]}'",
                            file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                        )
            console_log("✅ Success! Yak command processed and response handled.")
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🐐🐐🐐🔴 The manager's logic has become a tangled mess! The error be: {e}",
                file=current_file, version=current_version, function=current_function_name,
                console_print_func=console_log
            )

    def _on_trigger(self, topic, payload):
        # A new function to process trigger messages published to the repository.
        current_function_name = inspect.currentframe().f_code.co_name
        
        try:
            payload_data = json.loads(payload)
            if str(payload_data.get('value')).lower() != 'true':
                return
            
            # Extract the command path from the topic
            parts = topic.split('/')[3:-3] 
            yak_type = parts[0]
            command_path_list = parts[1:]
            
            # Now, simulate a call to the action handler using the original topic format
            # and the payload from the repository data.
            action_topic = "OPEN-AIR/actions/yak/" + "/".join(parts) + "/trigger"
            
            # The payload of a trigger from the repository should not be a complex JSON,
            # so we look up the repository data for the command.
            repo_path_list = topic.split('/')[2:-1]
            command_data = self.command_repo
            for part in repo_path_list:
                command_data = command_data.get(part, {})
            
            self._on_action_message(action_topic, json.dumps({"value": "true", "scpi_inputs": command_data.get("scpi_inputs", {})} ))
            
        except Exception as e:
            debug_log(
                message=f"🐐🐐🐐🔴 Trigger handler failed. The error be: {e}",
                file=current_file, version=current_version, function=current_function_name,
                console_print_func=console_log
            )


    # --- Integrated Yak API Functions ---
    def YakBeg(self, dispatcher: ScpiDispatcher, command_string: str):
        # Executes a 'BEG' (Begin) VISA command.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐 🟢 Entering {current_function_name} with command: {command_string}",
            file=current_file, version=current_version, function=current_function_name,
            console_print_func=self.dispatcher._print_to_gui_console
        )
        try:
            response = dispatcher.query_safe(command=command_string)
            if response is not None:
                return response
            else:
                return "FAILED"
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            return "FAILED"

    def YakRig(self, dispatcher: ScpiDispatcher, command_string: str):
        # Executes a 'RIG' VISA command.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐 🟢 Entering {current_function_name} with command: {command_string}",
            file=current_file, version=current_version, function=current_function_name,
            console_print_func=self.dispatcher._print_to_gui_console
        )
        try:
            if dispatcher.write_safe(command=command_string):
                return "PASSED"
            else:
                return "FAILED"
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            return "FAILED"

    def YakDo(self, dispatcher: ScpiDispatcher, command_string: str):
        # Executes a 'DO' VISA command.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐 🟢 Entering {current_function_name} with command: {command_string}",
            file=current_file, version=current_version, function=current_function_name,
            console_print_func=self.dispatcher._print_to_gui_console
        )
        try:
            if dispatcher.write_safe(command=command_string):
                return "PASSED"
            else:
                return "FAILED"
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            return "FAILED"

    def YakGet(self, dispatcher: ScpiDispatcher, command_string: str):
        # Executes a 'GET' VISA command.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐 🟢 Entering {current_function_name} with command: {command_string}",
            file=current_file, version=current_version, function=current_function_name,
            console_print_func=self.dispatcher._print_to_gui_console
        )
        try:
            response = dispatcher.query_safe(command=command_string)
            if response is not None:
                return response
            else:
                return "FAILED"
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            return "FAILED"

    # ADDED: YakNab function
    def YakNab(self, dispatcher: ScpiDispatcher, command_string: str):
        # Executes a 'NAB' (multi-query) VISA command.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐 🟢 Entering {current_function_name} with command: {command_string}",
            file=current_file, version=current_version, function=current_function_name,
            console_print_func=self.dispatcher._print_to_gui_console
        )
        try:
            response = dispatcher.query_safe(command=command_string)
            if response is not None:
                return response
            else:
                return "FAILED"
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            return "FAILED"

    def YakSet(self, dispatcher: ScpiDispatcher, command_string: str):
        # Executes a 'SET' VISA command.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐 🟢 Entering {current_function_name} with command: {command_string}",
            file=current_file, version=current_version, function=current_function_name,
            console_print_func=self.dispatcher._print_to_gui_console
        )
        try:
            if dispatcher.write_safe(command=command_string):
                return "PASSED"
            else:
                return "FAILED"
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            return "FAILED"