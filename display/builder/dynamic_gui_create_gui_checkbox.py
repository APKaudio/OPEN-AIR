# display/builder/dynamic_gui_create_checkbox.py
#
# A mixin class for the DynamicGuiBuilder that handles creating a checkbox widget.
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
# FIXED: The toggle_and_publish function now passes the raw boolean value instead of a JSON string to prevent double-encoding during MQTT transmission.

import os
import tkinter as tk
from tkinter import ttk
import inspect
import json

# --- Module Imports ---
from workers.worker_active_logging import debug_log, console_log


Local_Debug_Enable = False

# The wrapper functions debug_log_switch and console_log_switch are removed
# as the core debug_log and console_log now directly handle Local_Debug_Enable.


# --- Global Scope Variables ---
current_version = "20251127.000000.1"
current_version_hash = (20251127 * 0 * 1)
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2

class GuiCheckboxCreatorMixin:
    """
    A mixin class that provides the functionality for creating a
    checkbox widget.
    """
    def _create_gui_checkbox(self, parent_frame, label, config, path):
        # Creates a checkbox widget.
        current_function_name = inspect.currentframe().f_code.co_name

        debug_log(
            message=f"🛠️🟢 Entering '{current_function_name}' to create a checkbox for '{label}'.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            # We use a BooleanVar to track the state of the checkbox.
            initial_value = bool(config.get('value', False))
            state_var = tk.BooleanVar(value=initial_value)

            def get_label_text():
                current_state = state_var.get()
                # Use label_active/label_inactive if they exist, otherwise fall back to the main label.
                if current_state:
                    return config.get('label_active', config.get('label', ''))
                else:
                    return config.get('label_inactive', config.get('label', ''))
            
            def update_label():
                # Manually update the checkbox text
                checkbox.config(text=get_label_text())

            def toggle_and_publish():
                # Flips the state and publishes the change via MQTT.
                new_state = state_var.get()
                # Pass raw boolean instead of JSON string
                payload = new_state
                debug_log(
                    message=f"GUI ACTION: Publishing state change for '{label}' to path '{path}' with value '{new_state}'.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
                self._transmit_command(relative_topic=path, payload=payload)
                # Update the label after the state change
                update_label()

            # Create the checkbox button with an initial label.
            checkbox = ttk.Checkbutton(
                parent_frame,
                text=get_label_text(),
                variable=state_var,
                command=toggle_and_publish
            )
            checkbox.pack(side=tk.LEFT, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
            
            # Store the widget and its state variable for external updates.
            if path:
                self.topic_widgets[path] = (state_var, checkbox)

            console_log(f"✅ Celebration of success! The checkbox '{label}' did appear.")
            return checkbox

        except Exception as e:
            console_log(f"❌ Error in {current_function_name} for '{label}': {e}")
            debug_log(
                message=f"🛠️🔴 Arrr, the code be capsized! The checkbox creation has failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            return None