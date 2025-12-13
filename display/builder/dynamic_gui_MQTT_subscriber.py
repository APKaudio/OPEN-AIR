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
# Version 20251127.000000.1

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import paho.mqtt.client as mqtt

# --- Module Imports ---
from workers.active.worker_active_logging import debug_log, console_log
from display.styling.style import THEMES, DEFAULT_THEME


# --- Global Scope Variables ---
current_version = "20251127.000000.1"
current_version_hash = (20251127 * 0 * 1)
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
TOPIC_DELIMITER = "/"

Local_Debug_Enable = True


class MqttSubscriberMixin:
    """
    A mixin for the DynamicGuiBuilder to handle MQTT subscription and message processing.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # This instance variable will be set in the DynamicGuiBuilder's __init__
        self.mqtt_util = None

    def _on_receive_command_message(self, topic, payload):
        # The main callback function that processes incoming MQTT messages.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🖥️🔵 Entering _on_receive_command_message() for topic: '{topic}' with payload: '{payload}'.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            if topic.startswith(self.base_topic):
                relative_topic = topic[len(self.base_topic):].strip(TOPIC_DELIMITER)
                
                if not relative_topic:
                    # Case 1: The full configuration JSON is received on the base topic.
                    try:
                        full_config = json.loads(payload)
                        if isinstance(full_config, dict):
                            self.config_data = full_config
                            # Note: _rebuild_gui is NOT called here by design, as local JSON is authoritative.
                            debug_log(
                                message=f"🖥️🔵 Full config received for base topic '{self.base_topic}'. Config data updated, but GUI not auto-rebuilt (local JSON is authoritative).",
                                file=current_file,
                                version=current_version,
                                function=f"{self.__class__.__name__}.{current_function_name}",
                                console_print_func=console_log
                            )
                            return
                    except (json.JSONDecodeError, TypeError):
                        pass

                # Case 2: An incremental update is received on a subtopic.
                path_parts = relative_topic.split(TOPIC_DELIMITER)
                self._update_nested_dict(path_parts, payload)
                
                # Only update the widget if the GUI has already been built.
                if self.gui_built:
                    self.after(0, self._update_widget_value, relative_topic, payload)

            debug_log(
                message=f"🖥️🔵 Exiting _on_receive_command_message() for topic: '{topic}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized in _on_receive_command_message! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )


def log_to_gui(builder_instance, message):
    """
    Appends a message to the GUI log text widget if it exists.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    
    debug_log(
        message=f"🔍🔵 Entering '{current_function_name}'. Inspecting log entry of length {len(message)}. Preparing to write to GUI.",
        file=current_file,
        version=current_version,
        function=current_function_name,
        console_print_func=console_log
    )
    
    try:
        if hasattr(builder_instance, 'log_text'):
            builder_instance.log_text.configure(state='normal')
            builder_instance.log_text.insert(tk.END, message + "\n\n")
            builder_instance.log_text.configure(state='disabled')
            builder_instance.log_text.see(tk.END)
            
        console_log("✅ Celebration of success! The log message did save to the GUI!")
        debug_log(
            message=f"🔍🔵 Exiting '{current_function_name}'. Log message written to GUI.",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )
            
    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        debug_log(
            message=f"❌🔴 Arrr, the code be capsized! The logging to GUI has failed! The error be: {e}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )