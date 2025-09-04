# managers/manager_yakety_yak.py
#
# This manager listens for MQTT messages containing SCPI command details,
# constructs the final command string, and passes it to the YaketyYak agent for execution.
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
# Version 20250904.011523.1

import os
import inspect
import json
import re

# --- Utility, Agent, and Manager Imports ---
from workers.worker_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility
from managers.manager_visa_dispatch_scpi import ScpiDispatcher
import agents.agent_YaketyYak as YakAgent

# --- Global Scope Variables (as per Protocol 4.4) ---
current_version = "20250904.011523.1"
current_version_hash = (20250904 * 11523 * 1)
current_file = f"{os.path.basename(__file__)}"


class YaketyYakManager:
    """
    Orchestrates SCPI command execution by listening to MQTT topics,
    processing command templates, and interacting with the YaketyYak agent.
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

    def _on_repo_message(self, topic, payload):
        # Dynamically builds the internal command repository from MQTT messages.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🐐🐐📥 Incoming repository data! Topic='{topic}', Payload='{payload}'. Let's see what secrets it holds!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            parts = topic.split('/')[2:] # Skip OPEN-AIR/repository
            debug_log(
                message=f"🐐🐐🐐🔵 Dissecting topic into parts: {parts}",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )
            current_level = self.command_repo
            for part in parts[:-1]:
                current_level = current_level.setdefault(part, {})
                debug_log(
                    message=f"🐐🐐🐐🔍 Traversing repository structure. Current level: '{part}'.",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
            
            # The final part of the topic is the key for the payload value
            value = json.loads(payload).get('value', payload)
            current_level[parts[-1]] = value
            debug_log(
                message=f"🐐🐐🐐💾 Storing value '{value}' at key '{parts[-1]}'. The repository grows stronger!",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )

        except (json.JSONDecodeError, IndexError) as e:
            console_log(f"Could not parse repository message for topic {topic}: {e}")
            debug_log(
                message=f"🐐🐐🐐🔴 Blast it! The repository message was gibberish. Topic: '{topic}', Error: {e}",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )


    def _on_action_message(self, topic, payload):
        # Handles incoming command execution requests from the GUI.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🐐🐐⚡️ Action stations! A command has arrived! Topic: '{topic}', Payload: '{payload}'",
            file=current_file, version=current_version, function=current_function_name,
            console_print_func=console_log
        )
        try:
            parts = topic.split('/')[2:] # Skip OPEN-AIR/actions
            yak_type = parts[0]
            debug_log(
                message=f"🐐🐐🐐🔵 Command analysis complete. Type is '{yak_type}', Path is '{parts}'.",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )
            
            # Traverse the command repo to find the command details
            command_details = self.command_repo
            for part in parts:
                command_details = command_details.get(part, {})
            debug_log(
                message=f"🐐🐐🐐🔍 Found command details in repository: {json.dumps(command_details, indent=2)}",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )

            if not command_details:
                console_log(f"❌ Could not find command details for topic: {topic}")
                debug_log(
                    message=f"🐐🐐🐐🟡 Aborting! The command blueprints for '{topic}' are missing from my glorious repository!",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
                return

            # Determine device model and get SCPI command string
            model = self.app_instance.connected_instrument_model.get()
            manufacturer = self.app_instance.connected_instrument_manufacturer.get()
            debug_log(
                message=f"🐐🐐🐐🔍 Consulting the archives for device: Manufacturer='{manufacturer}', Model='{model}'.",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )
            
            scpi_details = command_details.get("scpi_button_details", {})
            scpi_template = scpi_details.get(manufacturer, {}).get(model, {}).get("value")
            if not scpi_template:
                debug_log(
                    message=f"🐐🐐🐐🟡 No specific template found for '{model}'. Reverting to the generic blueprint.",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
                scpi_template = scpi_details.get("generic_maker", {}).get("generic_model", {}).get("value")

            if not scpi_template:
                console_log(f"❌ Could not find SCPI command template for device {manufacturer} {model}.")
                debug_log(
                    message=f"🐐🐐🐐🔴 Failure! No SCPI template could be found at all. The experiment cannot proceed.",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
                return

            debug_log(
                message=f"🐐🐐🐐📜 Found SCPI template: '{scpi_template}'",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )

            # Substitute input values into the command string
            input_values = json.loads(payload)
            command_string = scpi_template
            debug_log(
                message=f"🐐🐐🐐🔧 Preparing to assemble the final command. Inputs received: {input_values}",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )
            for key, value in input_values.items():
                command_string = command_string.replace(f"<{key}>", str(value))
            
            # Remove any un-substituted placeholders
            command_string = re.sub(r'<[^>]+>', '', command_string).strip()
            debug_log(
                message=f"🐐🐐🐐✨ Command assembled! The final incantation is: '{command_string}'",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )

            # Call the appropriate agent function
            agent_function = getattr(YakAgent, yak_type, None)
            if not agent_function:
                console_log(f"❌ Invalid Yak type in topic: {yak_type}")
                debug_log(
                    message=f"🐐🐐🐐🔴 A grave miscalculation! The Yak type '{yak_type}' is unknown to science!",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
                return

            debug_log(
                message=f"🐐🐐🐐🚀 Engaging the '{yak_type}' agent! Dispatching command now!",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )
            response = agent_function(dispatcher=self.dispatcher, command_string=command_string)
            debug_log(
                message=f"🐐🐐🐐📡 The agent reports back! Response from device: '{response}'",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )

            # Process and publish outputs
            if response not in ["PASSED", "FAILED", None] and "scpi_outputs" in command_details:
                debug_log(
                    message=f"🐐🐐🐐📊 Response contains data! Preparing to parse and publish the results.",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
                outputs = command_details["scpi_outputs"]
                response_parts = response.split(';')
                
                output_keys = list(outputs.keys())
                for i, key in enumerate(output_keys):
                    if i < len(response_parts):
                        output_topic = f"OPEN-AIR/repository/yak/{'/'.join(parts)}/scpi_outputs/{key}/value"
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