# managers/manager_instrument_settings_markers.py
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251129  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 1 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


# A manager for marker-related settings.
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
# Version 20251124.150000.1

import os
import inspect
import json

from workers.worker_active_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility

# --- Global Scope Variables ---
current_version = "20251124.150000.1"
current_version_hash = (20251124 * 150000 * 1)
current_file = f"{os.path.basename(__file__)}"
Local_Debug_Enable = False

def debug_log_switch(message, file, version, function, console_print_func):
    if Local_Debug_Enable:
        debug_log(message, file, version, function, console_print_func)

def console_log_switch(message):
    if Local_Debug_Enable:
        console_log(message)


class MarkersSettingsManager:
    """
    Manages the logic and synchronization of all marker-related settings.
    """

    def __init__(self, mqtt_controller: MqttControllerUtility):
        # Initializes the manager and subscribes to relevant topics.
        current_function_name = inspect.currentframe().f_code.co_name
        
        self.mqtt_controller = mqtt_controller
        self.base_topic = "OPEN-AIR/configuration/instrument/marker"
        
        if Local_Debug_Enable:
            debug_log_switch(
                message=f"🛠️🟢 Initializing MarkersSettingsManager and setting up subscriptions.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
        
        self._subscribe_to_topics()

    def _subscribe_to_topics(self):
        # Subscribes to all necessary marker topics.
        current_function_name = inspect.currentframe().f_code.co_name
        
        # Example topic subscription
        topic = f"{self.base_topic}/#"
        self.mqtt_controller.add_subscriber(topic_filter=topic, callback_func=self._on_message)
        if Local_Debug_Enable:
            debug_log_switch(
                message=f"🔍 Subscribed to '{topic}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _on_message(self, topic, payload):
        # The main message processing callback.
        current_function_name = inspect.currentframe().f_code.co_name
        
        if Local_Debug_Enable:
            debug_log_switch(
                message=f"🛠️🔵 Received message on topic '{topic}' with payload '{payload}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
        
        try:
            # Placeholder for marker logic
            if Local_Debug_Enable:
                console_log_switch(f"✅ Marker setting updated on topic: {topic}")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            if Local_Debug_Enable:
                debug_log_switch(
                    message=f"🛠️🔴 Arrr, the code be capsized! The marker logic has failed! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )