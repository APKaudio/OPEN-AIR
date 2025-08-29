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
# Version 20250829.130545.2
# FIXED: The toggle button now publishes separate messages to the explicit 'selected' keys within its 'options' dictionary. This prevents the parent configuration dictionary from being overwritten and resolves the data corruption issue.

import os
import tkinter as tk
from tkinter import ttk
from workers.worker_logging import debug_log, console_log
import inspect
import json

# --- Global Scope Variables ---
current_version = "20250829.130545.2"
# Hash: (20250829 * 130545 * 2)
current_version_hash = (20250829 * 130545 * 2)
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
            on_text = on_config.get('label', 'ON')
            off_text = off_config.get('label', 'OFF')

            # Determine initial state from config, defaulting to false if unspecified.
            # The `path` variable already points directly to the 'value' key's topic.
            # is_on = str(config.get('value', 'false')).lower() in ['true', 'yes', '1']
            is_on = options_map.get('ON', {}).get('selected', False)
            
            state_var = tk.BooleanVar(value=is_on)
            
            button = ttk.Button(parent_frame, text=on_text if is_on else off_text)
            button.pack(fill=tk.X, expand=True, padx=5, pady=2)

            def update_button_state():
                # Updates the button's appearance based on its current state.
                current_state = state_var.get()
                if current_state: # State is ON
                    button.config(text=on_text, style='Selected.TButton')
                else: # State is OFF
                    button.config(text=off_text, style='TButton')

            def toggle_state_and_publish():
                # Flips the state, updates the button, and publishes the new state.
                new_state = not state_var.get()
                state_var.set(new_state)
                update_button_state()
                
                # --- START OF FIX: Correctly publish to nested topics. ---
                # Deselect the previous option (or publish the new "off" state)
                off_path = f"{path}{TOPIC_DELIMITER}options{TOPIC_DELIMITER}OFF{TOPIC_DELIMITER}selected"
                self._transmit_command(relative_topic=off_path, payload=str(not new_state).lower())
                
                # Select the new option (or publish the new "on" state)
                on_path = f"{path}{TOPIC_DELIMITER}options{TOPIC_DELIMITER}ON{TOPIC_DELIMITER}selected"
                self._transmit_command(relative_topic=on_path, payload=str(new_state).lower())
                # --- END OF FIX ---
                
                # The path is the single, canonical topic for this widget's value.
                # We extract the relative path from the full base_topic path.
                # relative_publish_path = path 

                debug_log(
                    message=f"GUI ACTION: Publishing state change for '{label}' with new state '{new_state}'.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
                # self._transmit_command(relative_topic=relative_publish_path, payload=publish_payload)

            button.config(command=toggle_state_and_publish)
            update_button_state() # Set initial text and style
            
            # The widget now subscribes to ONLY ONE topic for its state.
            self.topic_widgets[path] = (state_var, update_button_state)

            console_log("✅ Celebration of success! the " + label + " did toggle its function with robust, new logic!")
            return button

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🛠️🔴 Arrr, the code be capsized! The toggle button creation has failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            return None