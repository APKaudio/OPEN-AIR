# workers/builder/dynamic_gui_create_gui_actuator.py
#
# This file (dynamic_gui_create_gui_actuator.py) provides the GuiActuatorCreatorMixin class for creating simple actuator buttons in the GUI.
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
import tkinter as tk
from tkinter import ttk
import inspect
import json

# --- Module Imports ---
from workers.logger.logger import debug_log, console_log, log_visa_command


Local_Debug_Enable = True

# The wrapper functions debug_log and console_log_switch are removed
# as the core debug_log and console_log now directly handle Local_Debug_Enable.


# --- Global Scope Variables ---
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2
TOPIC_DELIMITER = "/"


class GuiActuatorCreatorMixin:
    """
    A mixin class that provides the functionality for creating a simple
    actuator button widget that triggers an action.
    """
    def _create_gui_actuator(self, parent_frame, label, config, path):
        # Creates a button that acts as a simple actuator.
        current_function_name = inspect.currentframe().f_code.co_name
        
        # A trigger path is used to differentiate the trigger from other state values.
        trigger_path = path + "/trigger"
        
        if Local_Debug_Enable:
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

            button_text = config.get('label', config.get('label_active', config.get('label_inactive', label)))

            button = ttk.Button(
                sub_frame,
                text=button_text,
                style='Custom.TButton' 
            )
            button.pack(side=tk.LEFT, padx=DEFAULT_PAD_X)

            def on_press(event):
                # FIXED: The actuator now correctly publishes to the "actions" topic.
                action_path = trigger_path.replace("repository", "actions")

                if Local_Debug_Enable:
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

                if Local_Debug_Enable:
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
            if Local_Debug_Enable:
                debug_log(
                    message=f"🛠️🟢 Exiting '{current_function_name}'. Actuator button '{label}' created.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
            return sub_frame

        except Exception as e:
            console_log(f"❌ Error in {current_function_name} for '{label}': {e}")
            if Local_Debug_Enable:
                debug_log(
                    message=f"🛠️🔴 Arrr, the code be capsized! The actuator button creation has failed! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=current_function_name,
                    console_print_func=console_log
                )
            return None