# display/builder/dynamic_gui_create_gui_actuator.py
#
# A mixin class for the DynamicGuiBuilder that handles creating a simple actuator button.
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
# FIXED: Actuator buttons now correctly publish to the 'actions' topic instead of the 'repository' topic.

import os
import tkinter as tk
from tkinter import ttk
import inspect
import json

# --- Module Imports ---
from workers.active.worker_active_logging import debug_log, console_log


Local_Debug_Enable = True

# The wrapper functions debug_log_switch and console_log_switch are removed
# as the core debug_log and console_log now directly handle Local_Debug_Enable.


# --- Global Scope Variables ---
current_version = "20251127.000000.1"
current_version_hash = 20251127 * 0 * 1
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2
TOPIC_DELIMITER = "/"


class GuiActuatorCreatorMixin:
    """
    A mixin class that provides the functionality for creating a simple
    actuator button widget that triggers an action via MQTT.
    """
    def _create_gui_actuator(self, parent_frame, label, config, path):
        # Creates a button that acts as a simple actuator.
        current_function_name = inspect.currentframe().f_code.co_name
        
        # A trigger path is used to differentiate the trigger from other state values.
        trigger_path = path + "/trigger"
        
        debug_log(
            message=f"🛠️🟢 Entering {current_function_name} to conjure an actuator button for '{label}'.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # Create a frame to hold the label and button
            sub_frame = ttk.Frame(parent_frame)
            sub_frame.pack(side=tk.LEFT, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

            button_text = config.get('label', label)

            button = ttk.Button(
                sub_frame,
                text=button_text,
                style='Custom.TButton' 
            )
            button.pack(side=tk.LEFT, padx=DEFAULT_PAD_X)

            def on_press(event):
                # FIXED: The actuator now correctly publishes to the "actions" topic.
                action_path = trigger_path.replace("repository", "actions")

                debug_log(
                    message=f"GUI ACTION: Publishing actuator command to '{action_path}' with value 'true'",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
                self._transmit_command(relative_topic=action_path, payload=True, retain=False)

            def on_release(event):
                # FIXED: The actuator now correctly publishes to the "actions" topic.
                action_path = trigger_path.replace("repository", "actions")

                debug_log(
                    message=f"GUI ACTION: Publishing actuator command release to '{action_path}' with value 'false'",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
                self._transmit_command(relative_topic=action_path, payload=False, retain=False)

            button.bind("<ButtonPress-1>", on_press)
            button.bind("<ButtonRelease-1>", on_release)

            if path:
                self.topic_widgets[path] = button

            console_log(f"✅ Celebration of success! The actuator button '{label}' did appear.")
            return sub_frame

        except Exception as e:
            console_log(f"❌ Error in {current_function_name} for '{label}': {e}")
            debug_log(
                message=f"🛠️🔴 Arrr, the code be capsized! The actuator button creation has failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=current_function_name,
                console_print_func=console_log
            )
            return None