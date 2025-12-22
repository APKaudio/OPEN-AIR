# managers/manager_yakety_yak.py
#
# This file (manager_yakety_yak.py) listens for MQTT messages and dynamically builds and updates a local JSON repository based on the incoming topic and payload data.
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
import json
import pathlib
import re

# --- Utility and Manager Imports ---
from workers.logger.logger import debug_log, console_log, log_visa_command
from workers.mqtt.worker_mqtt_controller_util import MqttControllerUtility
from managers.connection.manager_visa_dispatch_scpi import ScpiDispatcher
from managers.yak_manager.yak_trigger_handler import handle_yak_trigger
# FIXED: Re-import YAKETY_YAK_REPO_PATH after circular dependency fix
from workers.utils.worker_project_paths import YAKETY_YAK_REPO_PATH 


Local_Debug_Enable = False





current_file = f"{os.path.basename(__file__)}"
# DELETED: YAKETY_YAK_REPO_PATH is now imported from worker_project_paths.py
repo_topic_filter = "OPEN-AIR/yak/#"
save_action_topic = "OPEN-AIR/actions/yak/save/trigger"


class YaketyYakManager:
    """
    Manages the creation and updating of the YAK command repository via MQTT.
    """
    def __init__(self, mqtt_controller: MqttControllerUtility, dispatcher_instance: ScpiDispatcher, app_instance):
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.Local_Debug_Enable: 
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
            
            # FIXED: Ensure the repository folder exists before trying to load or save.
            if not YAKETY_YAK_REPO_PATH.parent.exists():
                YAKETY_YAK_REPO_PATH.parent.mkdir(parents=True, exist_ok=True)
                
            self.repo_memory = self._load_repo_from_file()

            # Subscribe to the master topic for all repository commands
            self.mqtt_util.add_subscriber(
                topic_filter=repo_topic_filter,
                callback_func=self.YAK_LISTEN_TO_MQTT
            )
            if app_constants.Local_Debug_Enable: 
                debug_log(
                    message=f"🐐🐐🐐🔍 I've set a trap! Listening for all repository messages on topic '{repo_topic_filter}'.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )

            # Subscribe to the explicit save topic
            self.mqtt_util.add_subscriber(
                topic_filter=save_action_topic,
                callback_func=self.YAK_SAVE_REPOSITORY
            )
            if app_constants.Local_Debug_Enable: 
                debug_log(
                    message=f"🐐🐐🐐💾 A new trap is set! Listening for an explicit save command on topic '{save_action_topic}'.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
            
            console_log("✅ The YaketyYak Manager has initialized and is listening for commands.")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            if app_constants.Local_Debug_Enable: 
                debug_log(
                    message=f"🐐🐐🐐🔴 Initialization failed! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )

    def _load_repo_from_file(self):
        """
        Loads the repository from the JSON file into memory on initialization.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        # The check for directory existence is now in __init__
        
        if YAKETY_YAK_REPO_PATH.is_file() and YAKETY_YAK_REPO_PATH.stat().st_size > 0:
            try:
                # Use the imported path constant
                with open(YAKETY_YAK_REPO_PATH, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                if app_constants.Local_Debug_Enable: 
                    debug_log(
                        message=f"🐐🐐🐐🟡 Failed to decode JSON from file. Creating an empty repository. The error be: {e}",
                        file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                    )
                return {}
        else:
            return {}

    def _save_repo_to_file(self):
        """
        Writes the current in-memory repository to the JSON file.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.Local_Debug_Enable: 
            debug_log(
                # UPDATED: Use the imported path constant
                message=f"🐐🐐🐐💾 Writing the current repository to '{YAKETY_YAK_REPO_PATH}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
        try:
            # Ensure the parent directory exists (already checked in __init__, but good to be safe)
            if not YAKETY_YAK_REPO_PATH.parent.exists():
                YAKETY_YAK_REPO_PATH.parent.mkdir(parents=True, exist_ok=True)

            # UPDATED: Use the imported path constant
            with open(YAKETY_YAK_REPO_PATH, 'w') as f:
                json.dump(self.repo_memory, f, indent=4)
            
            console_log("✅ Repository saved successfully!")
            return True
        except Exception as e:
            console_log(f"❌ Error saving repository to file: {e}")
            if app_constants.Local_Debug_Enable: 
                debug_log(
                    message=f"🐐🐐🐐🔴 The quill broke! Failed to save the repository! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
        return False

    def YAK_LISTEN_TO_MQTT(self, topic, payload):
        """
        Processes incoming MQTT messages and updates the in-memory repository.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.Local_Debug_Enable: 
            debug_log(
                message=f"🐐🐐🐐⚡️ An announcement has arrived! Topic: '{topic}', Payload: '{payload}'",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

        try:
            # Attempt to parse payload as JSON
            try:
                parsed_payload = json.loads(payload)
            except json.JSONDecodeError:
                # If it's not valid JSON, treat it as an empty dictionary for the check.
                # However, if the intent is to store the raw string, we'll use 'payload' directly later.
                parsed_payload = payload # Store raw payload if not JSON
                
            # Check for a "trigger" in the topic AND the value being explicitly True
            if "trigger" in topic.lower() and isinstance(parsed_payload, dict) and parsed_payload.get('value', False) is True:
                if app_constants.Local_Debug_Enable: 
                    debug_log(
                        message="🐐🐐🐐🟢 Trigger event detected with a 'true' value. Initiating command orchestration!",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}",
                        console_print_func=console_log
                    )
                handle_yak_trigger(self, topic, payload)

            # Deconstruct the topic to form the nested path in our repository
            path_parts = topic.replace("OPEN-AIR/repository/", "").split('/')
            
            current_node = self.repo_memory
            for part in path_parts[:-1]:
                # Sanitize part for use as a dictionary key
                part = re.sub(r'[^a-zA-Z0-9_]', '', part)
                # Ensure current_node[part] is always a dictionary, even if it was previously a non-dict value
                if part not in current_node or not isinstance(current_node[part], dict):
                    current_node[part] = {}
                current_node = current_node[part]
           
            last_key = path_parts[-1]
            
            # Determine the value to be stored in the repository
            if isinstance(parsed_payload, dict) and 'value' in parsed_payload:
                value_to_store = parsed_payload['value']
            elif isinstance(parsed_payload, dict): # If it's a parsed dict but no 'value' key, store the whole dict
                value_to_store = parsed_payload
            else: # If parsing failed or it was a simple string (not JSON), use the raw payload
                value_to_store = payload
            
            # REFINEMENT: Remove leading and trailing double quotes if they exist if it's a string
            if isinstance(value_to_store, str) and value_to_store.startswith('"') and value_to_store.endswith('"'):
                value_to_store = value_to_store.strip('"')

            # Update the in-memory dictionary
            current_node[last_key] = value_to_store
            
            # NOW THE AUTOMATIC SAVE OCCURS HERE
            self._save_repo_to_file()
            
            console_log(f"✅ Repository updated in memory and saved to file from message on topic: {topic}")
        
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            if app_constants.Local_Debug_Enable: 
                debug_log(
                    message=f"🐐🐐🐐🔴 A fatal error occurred while processing the MQTT message! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
            
    def YAK_SAVE_REPOSITORY(self, topic, payload):
        """
        Saves the current in-memory repository to a local JSON file.
        This is an explicit action triggered by an MQTT command.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.Local_Debug_Enable: 
            debug_log(
                # UPDATED: Use the imported path constant
                message=f"🐐🐐🐐💾 An explicit save command has been received! Writing the current repository to '{YAKETY_YAK_REPO_PATH}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
        try:
            data = json.loads(payload)
            if str(data.get("value")).lower() == 'true':
                self._save_repo_to_file()
        except Exception as e:
            console_log(f"❌ Error saving repository to file: {e}")
            if app_constants.Local_Debug_Enable: 
                debug_log(
                    message=f"🐐🐐🐐🔴 The quill broke! Failed to save the repository! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )