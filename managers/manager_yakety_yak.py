# managers/manager_yakety_yak.py
#
# This manager listens for MQTT messages containing SCPI command details,
# constructs the final command string, and passes it to the ScpiDispatcher for execution.
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
# Version 20250909.225412.6

import os
import inspect
import json
import re
import pathlib
import time

# --- Utility and Manager Imports ---
from workers.worker_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility
from managers.manager_visa_dispatch_scpi import ScpiDispatcher

# --- Global Scope Variables (as per Protocol 4.4) ---
current_version = "20250909.225412.6"
current_version_hash = (20250909 * 225412 * 6)
current_file = f"{os.path.basename(__file__)}"
YAKETY_YAK_REPO_PATH = pathlib.Path("DATA/YAKETYYAK.json")


class YaketyYakManager:
    """
    Orchestrates SCPI command execution by listening to MQTT topics,
    processing command templates, and dispatching commands.
    """
    def __init__(self, mqtt_controller, dispatcher_instance, app_instance):
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

            self._load_repo_from_file()

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

            action_topic = "OPEN-AIR/actions/yak/#"
            self.mqtt_util.add_subscriber(
                topic_filter=action_topic,
                callback_func=self._on_action_message
            )

            # OLD RIGID SUBSCRIPTION REMOVED: 
            # self.mqtt_util.add_subscriber(
            #     topic_filter="OPEN-AIR/repository/yak/+/+/+/+/+/+/+/+/trigger",
            #     callback_func=self._on_trigger
            # )

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

    def _load_repo_from_file(self):
        """Loads the command repository from a local JSON file if it exists."""
        current_function_name = inspect.currentframe().f_code.co_name
        if YAKETY_YAK_REPO_PATH.is_file():
            try:
                with open(YAKETY_YAK_REPO_PATH, 'r') as f:
                    self.command_repo = json.load(f)
                debug_log(
                    message=f"🐐🐐🐐💾 Loaded command repository from local file '{YAKETY_YAK_REPO_PATH}'.",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
            except Exception as e:
                debug_log(
                    message=f"🐐🐐🐐🟡 Failed to load local repository file. The error be: {e}. Starting with an empty repository.",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
                self.command_repo = {}
        else:
            debug_log(
                message=f"🐐🐐🐐🟡 Local repository file not found at '{YAKETY_YAK_REPO_PATH}'. Will build from MQTT.",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )

    def _save_repo_to_file(self):
        """Saves the current command repository to a local JSON file."""
        current_function_name = inspect.currentframe().f_code.co_name
        try:
            YAKETY_YAK_REPO_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(YAKETY_YAK_REPO_PATH, 'w') as f:
                json.dump(self.command_repo, f, indent=4)
            debug_log(
                message=f"🐐🐐🐐💾 Saved current command repository to '{YAKETY_YAK_REPO_PATH}'.",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )
        except Exception as e:
            debug_log(
                message=f"🐐🐐🐐🔴 Failed to save local repository file. The error be: {e}",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )

    def _on_repo_message(self, topic, payload):
        """Dynamically builds the internal command repository from MQTT messages."""
        current_function_name = inspect.currentframe().f_code.co_name

        # NEW LOGIC: Check if the message is a trigger and process it accordingly.
        if topic.endswith('/trigger'):
            self._process_trigger_message(topic, payload)
            return

        try:
            # Parse the topic to get the path parts, starting after "OPEN-AIR/repository/".
            parts = topic.replace("OPEN-AIR/repository/", "").split('/')
            
            # Traverse the dictionary, creating nested dictionaries as needed.
            current_level = self.command_repo
            for part in parts[:-1]:
                cleaned_part = part.replace(" ", "_").replace("/", "_")
                # Check if the key exists and if its value is a dictionary. If not, create a new dictionary.
                if cleaned_part not in current_level or not isinstance(current_level[cleaned_part], dict):
                    debug_log(
                        message=f"🐐🐐🐐🟡 Inconsistent topic path detected. Overwriting node '{cleaned_part}' with a new dictionary to continue.",
                        file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                    )
                    current_level[cleaned_part] = {}
                current_level = current_level[cleaned_part]
            
            try:
                # Attempt to load the payload as JSON, falling back to a plain string.
                parsed_payload = json.loads(payload)
                value = parsed_payload.get('value', payload)
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        pass
            except (json.JSONDecodeError, TypeError):
                value = payload
            
            # The final part of the topic path becomes the key.
            final_key = parts[-1].replace(" ", "_")
            current_level[final_key] = value
            
            debug_log(
                message=f"🐐🐐🐐💾 Storing repository data. Topic segment: '{final_key}', Value: '{value}'",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )
            # Save the updated repository to a local file.
            self._save_repo_to_file()

        except (json.JSONDecodeError, IndexError) as e:
            console_log(f"❌ Could not parse repository message for topic {topic}: {e}")
            debug_log(
                message=f"🐐🐐🐐🔴 Blast it! The repository message was gibberish. Topic: '{topic}', Error: {e}",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )

    def _on_action_message(self, topic, payload):
        """Processes commands published to the /actions topic."""
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

            # Get the command type (e.g., 'beg', 'rig', 'set') and path from the topic.
            path_parts = topic.split('/')[3:]
            yak_command_type = path_parts[0]
            top_level_key = yak_command_type.upper() + "_COMMANDS"
            command_path_list = path_parts[1:-1]

            # Traverse the dictionary using the cleaned path parts.
            current_dict = self.command_repo.get('yak', {}).get(yak_command_type, {}).get(top_level_key, {})
            for part in command_path_list:
                cleaned_part = part.replace(" ", "_").replace("/", "_")
                current_dict = current_dict.get(cleaned_part, {})
            
            command_details = current_dict

            if not command_details:
                console_log(f"❌ Could not find command details for topic: {topic}")
                debug_log(
                    message=f"🐐🐐🐐🟡 Aborting! The command blueprints for '{topic}' are missing from my glorious repository!",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
                return

            debug_log(
                message=f"🐐🐐🐐✅ Found command details: {json.dumps(command_details, indent=2)}",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )
            
            # Retrieve the manufacturer and model from the dispatcher.
            model = self.dispatcher.get_model()
            manufacturer = self.dispatcher.get_manufacturer()
            
            # Find the correct SCPI template, preferring device-specific over generic.
            scpi_template = None
            scpi_details = command_details.get("scpi_details", {})
            
            # First, try to find a device-specific command.
            if manufacturer in scpi_details and model in scpi_details[manufacturer]:
                scpi_template = scpi_details[manufacturer][model].get("SCPI_value")
            
            # If not found, try the generic wildcard command.
            if not scpi_template and "generic_maker" in scpi_details and "generic_model" in scpi_details["generic_maker"]:
                scpi_template = scpi_details["generic_maker"]["generic_model"].get("SCPI_value")
            
            if not scpi_template:
                if 'trigger' in command_details:
                    command_string = command_details['trigger']
                else:
                    console_log(f"❌ Could not find SCPI command template for device {manufacturer} {model} or a generic one.")
                    debug_log(
                        message=f"🐐🐐🐐🔴 Failure! No SCPI template could be found at all. The experiment cannot proceed.",
                        file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                    )
                    return
            else:
                command_string = scpi_template

            input_values = payload_data.get('scpi_inputs', {})
            if input_values:
                debug_log(
                    message=f"🐐🐐🐐🔍 Found input parameters to substitute: {list(input_values.keys())}",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
                for key, details in input_values.items():
                    placeholder = f"<{key}>"
                    value_to_substitute = details.get('value', '')
                    if placeholder in command_string:
                        command_string = command_string.replace(placeholder, str(value_to_substitute))
            
            # Clean up any remaining placeholders that might not have been matched.
            command_string = re.sub(r'<[^>]+>', '', command_string).strip()

            debug_log(
                message=f"🐐🐐🐐📝 Final SCPI command string ready for dispatch: '{command_string}'",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )

            # Dispatch the command based on its type.
            if yak_command_type.lower() in ['get', 'nab', 'beg']:
                debug_log(
                    message=f"🐐🐐🐐🚀 Engaging the '{yak_command_type}' API! Dispatching query command now!",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
                response = self.dispatcher.query_safe(command_string)
            else:
                debug_log(
                    message=f"🐐🐐🐐🚀 Engaging the '{yak_command_type}' API! Dispatching write command now!",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
                response = self.dispatcher.write_safe(command_string)
            
            debug_log(
                message=f"🐐🐐🐐📡 The agent reports back! Response from device: '{response}'",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )

            # Handle outputs and publish them back to MQTT.
            if response not in ["PASSED", "FAILED", None] and "scpi_outputs" in command_details:
                outputs = command_details["scpi_outputs"]
                response_parts = response.split(';')

                output_keys = list(outputs.keys())
                for i, key in enumerate(output_keys):
                    if i < len(response_parts):
                        # Construct the output topic based on the original request path
                        output_topic = f"OPEN-AIR/repository/yak/{yak_command_type}/{'/'.join(command_path_list)}/scpi_outputs/{key}/value"
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
            
    def _process_trigger_message(self, topic, payload):
        """Processes triggers from the repository topic."""
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🐐🐐⚡️ Found a trigger in the repository topic! Redirecting to action handler.",
            file=current_file, version=current_version, function=current_function_name,
            console_print_func=console_log
        )
        try:
            # Reconstruct the topic path for the action handler
            action_path_parts = topic.split('/')
            action_path_parts[2] = 'actions' # Change 'repository' to 'actions'
            action_topic = "/".join(action_path_parts)
            
            # The payload for the action message needs to include the input values if any
            repo_path_list = topic.split('/')[2:-1]
            command_data = self.command_repo
            for part in repo_path_list:
                command_data = command_data.get(part.replace(" ", "_"), {})

            self._on_action_message(action_topic, json.dumps({"value": "true", "scpi_inputs": command_data.get("scpi_inputs", {})} ))
            
        except Exception as e:
            debug_log(
                message=f"🐐🐐🐐🔴 Trigger redirection failed. The error be: {e}",
                file=current_file, version=current_version, function=current_function_name,
                console_print_func=console_log
            )