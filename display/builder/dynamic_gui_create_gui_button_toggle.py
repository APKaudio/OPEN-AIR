# display/builder/dynamic_gui_create_gui_button_toggle.py
#
# A mixin class for creating a toggle button widget that updates state via MQTT.
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
# FIXED: The button styles have been corrected to match the user's request,
# using the 'Selected' style for the ON state, and relying on the central style map.

import os
import tkinter as tk
from tkinter import ttk
from workers.worker_active_logging import debug_log, console_log
import inspect
import json


Local_Debug_Enable = False

# The wrapper functions debug_log_switch and console_log_switch are removed
# as the core debug_log and console_log now directly handle Local_Debug_Enable.


# --- Global Scope Variables ---
current_version = "20251127.000000.1"
current_version_hash = 20251127 * 0 * 1
current_file = f"{os.path.basename(__file__)}"

TOPIC_DELIMITER = "/"

class GuiButtonToggleCreatorMixin:
    def _create_gui_button_toggle(self, parent_frame, label, config, path):
        # Creates a single button that toggles between two states (e.g., ON/OFF).
        current_function_name = inspect.currentframe().f_code.co_name

        debug_log(
            message=f"🛠️🟢 Entering '{current_function_name}' to conjure a button widget for '{label}' on path '{path}'.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            options_map = config.get('options', {})
            on_config = options_map.get('ON', {})
            off_config = options_map.get('OFF', {})
            on_text = on_config.get('label_active', 'ON')
            off_text = off_config.get('label_inactive', 'OFF')

            is_on = options_map.get('ON', {}).get('selected', False)
            
            state_var = tk.BooleanVar(value=is_on)
            
            button = ttk.Button(parent_frame, text=on_text if is_on else off_text)
            button.pack(side=tk.LEFT, padx=5, pady=2)

            def update_button_state():
                # Updates the button's appearance based on its current state.
                current_state = state_var.get()
                if current_state:  # Correct logic: The button is ON, so use the 'Selected' style.
                    button.config(text=on_text, style='Custom.Selected.TButton')
                else: # The button is OFF, so use the default 'TButton' style.
                    button.config(text=off_text, style='Custom.TButton')

            def toggle_state_and_publish():
                # Flips the state, updates the button, and publishes the new state.
                new_state = not state_var.get()
                state_var.set(new_state)
                update_button_state()
                
                # Deselect the previous option (or publish the new "off" state)
                off_path = f"{path}{TOPIC_DELIMITER}options{TOPIC_DELIMITER}OFF{TOPIC_DELIMITER}selected"
                self._transmit_command(relative_topic=off_path, payload=str(not new_state).lower())
                
                # Select the new option (or publish the new "on" state)
                on_path = f"{path}{TOPIC_DELIMITER}options{TOPIC_DELIMITER}ON{TOPIC_DELIMITER}selected"
                self._transmit_command(relative_topic=on_path, payload=str(new_state).lower())
                
                debug_log(
                    message=f"GUI ACTION: Publishing state change for '{label}' with new state '{new_state}'.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )

            button.config(command=toggle_state_and_publish)
            update_button_state() # Set initial text and style
            
            self.topic_widgets[path] = (state_var, update_button_state)

            console_log("✅ Celebration of success! the " + label + " did toggle its function with robust, new logic!")
            return button

        except Exception as e:
            console_log(f"❌ Error in {current_function_name} for '{label}': {e}")
            debug_log(
                message=f"🛠️🔴 Arrr, the code be capsized! The toggle button creation has failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            return None