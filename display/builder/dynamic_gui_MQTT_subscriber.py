# display/builder/dynamic_gui_MQTT_subscriber.py
#
# A mixin for DynamicGuiBuilder that handles MQTT subscription and message processing.
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
# Version 20250827.194400.1

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import paho.mqtt.client as mqtt

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from display.styling.style import THEMES, DEFAULT_THEME


# --- Global Scope Variables ---
current_version = "20250827.194400.1"
current_version_hash = (20250827 * 194400 * 1)
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
TOPIC_DELIMITER = "/"


class MqttSubscriberMixin:
    def __init__(self, parent_frame, mqtt_util, config):
        """
        Initializes the MQTT subscription mixin.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🟢 Initializing the '{self.__class__.__name__}' MQTT subscriber mixin.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=config.get('log_to_gui_console', console_log)
        )
        self.mqtt_util = mqtt_util
        self.base_topic = config.get("base_topic")

        if self.base_topic:
            # We subscribe to the specific base topic and a wildcard to get all child topics.
            full_topic = f"{self.base_topic}{TOPIC_DELIMITER}#"
            self.mqtt_util.add_subscriber(topic_filter=full_topic, callback_func=self._on_mqtt_message)
        
            # New Debugging Information
            debug_log(
                message=f"🛠️🟢 Subscribed to MQTT topic: '{full_topic}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=config.get('log_to_gui_console', console_log)
            )

    def _on_mqtt_message(self, topic, payload):
        # The main callback function that processes incoming MQTT messages.
        try:
            if topic.startswith(self.base_topic):
                relative_topic = topic[len(self.base_topic):].strip(TOPIC_DELIMITER)
                if not relative_topic:
                    return

                path_parts = relative_topic.split(TOPIC_DELIMITER)
                self._update_nested_dict(path_parts, payload)
                
                self.after(0, self._update_widget_value, relative_topic, payload)

        except Exception as e:
            console_log(f"❌ Error updating widget for topic '{relative_topic}': {e}")