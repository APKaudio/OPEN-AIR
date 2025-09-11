# managers/manager_yakety_yak.py
#
# This manager listens for MQTT messages and orchestrates the command
# execution by delegating tasks to specialized sub-managers.

import os
import inspect
import json
import pathlib

# --- Utility and Manager Imports ---
from workers.worker_logging import debug_log, console_log
from managers.manager_yak_inputs import YakInputsManager
from managers.manager_yak_tx import YakTxManager
from managers.manager_yak_rx import YakRxManager

# --- Global Scope Variables (as per Protocol 4.4) ---
current_version = "20250910.224800.0"
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
            
            # Initialize the specialized managers
            self.inputs_manager = YakInputsManager()
            self.tx_manager = YakTxManager(dispatcher_instance)
            self.rx_manager = YakRxManager(mqtt_controller)

            debug_log(
                message=f"🐐🐐🐐🔵 The manager's components are being wired up: mqtt_util={mqtt_controller}, dispatcher={dispatcher_instance}, app={app_instance}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
            # This topic is for updating the *entire* repository
            repo_update_topic = "OPEN-AIR/repository/yak/update"
            self.mqtt_util.add_subscriber(
                topic_filter=repo_update_topic,
                callback_func=self._on_repo_update
            )
            debug_log(
                message=f"🐐🐐🐐🔍 I've set a trap! Listening for command blueprint updates on topic '{repo_update_topic}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

            # This is the dedicated topic for command execution
            action_topic = "OPEN-AIR/actions/yak/#"
            self.mqtt_util.add_subscriber(
                topic_filter=action_topic,
                callback_func=self._on_action_message
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

    def _on_repo_update(self, topic, payload):
        """
        Dynamically rebuilds the entire command repository from a complete JSON payload.
        This is for a full repository sync, not for individual updates.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(f"🐐🐐🐐🟢 Entering {current_function_name}. Processing MQTT message for repository update. | Topic: '{topic}'", file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
        
        # This will now process the full JSON payload to rebuild the repository
        self.inputs_manager.update_repo_from_json(payload)
        
        debug_log(f"🐐🐐🐐✅ Exiting {current_function_name} after delegating repository update.", file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)

    def _on_action_message(self, topic, payload):
        """
        Processes command actions published to the /actions topic.
        This function now reads from the in-memory repository, it does not write to it.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🐐🐐⚡️ Action stations! A command has arrived! Topic: '{topic}', Payload: '{payload}'",
            file=current_file, version=current_version, function=current_function_name,
            console_print_func=console_log
        )
        if not topic.endswith('/trigger'):
            debug_log(f"🐐🐐🐐🟡 Ignoring non-trigger message on action topic: {topic}", file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
            return

        try:
            payload_data = json.loads(payload)
            if str(payload_data.get('value')).lower() != 'true':
                debug_log(f"🐐🐐🐐🟡 Ignoring 'false' trigger payload. | Value: {payload_data.get('value')}", file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
                return

            # Correctly deconstruct topic path by removing the root prefix
            debug_log(f"🐐🐐🐐🔍 Deconstructing topic path: '{topic}'", file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
            path_parts = topic.replace("OPEN-AIR/actions/", "").split('/')
            
            yak_command_type = path_parts[1]
            
            # Delegate to the inputs manager to prepare the command
            command_string, command_details = self.inputs_manager.prepare_command(path_parts, payload_data)
            if not command_string:
                console_log(f"❌ Could not prepare command for topic: {topic}")
                return

            # Delegate to the transmission manager to send the command
            response = self.tx_manager.execute_command(yak_command_type, command_string)
            
            # Delegate to the reception manager to handle the response
            if response not in ["PASSED", "FAILED", None] and "scpi_outputs" in command_details:
                self.rx_manager.process_response(path_parts, command_details, response)

            console_log("✅ Success! Yak command processed and response handled.")
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🐐🐐🐐🔴 The manager's logic has become a tangled mess! The error be: {e}",
                file=current_file, version=current_version, function=current_function_name,
                console_print_func=console_log
            )