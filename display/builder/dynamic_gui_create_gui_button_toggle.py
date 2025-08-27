# display/builder/dynamic_gui_create_gui_button_toggle.py
#
# A mixin class for the DynamicGuiBuilder that handles the creation of a two-state toggle button.
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
# Version 20250827.153037.17

import os
import tkinter as tk
from tkinter import ttk

# --- Module Imports ---
from workers.worker_logging import console_log

# --- Global Scope Variables ---
current_version = "20250827.153037.17"
current_version_hash = (20250827 * 153037 * 17)
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2

class GuiButtonToggleCreatorMixin:
    """
    A mixin class that provides the functionality for creating a
    single button that toggles between two states.
    """
    def _create_gui_button_toggle(self, parent_frame, label, config, path):
        # This function creates a single button that toggles between two states (e.g., ON/OFF).
        try:
            sub_frame = ttk.Frame(parent_frame)
            sub_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

            options = config.get('options', {})
            on_config = options.get('ON', {})
            off_config = options.get('OFF', {})

            is_on = str(on_config.get('selected', 'false')).lower() in ['true', 'yes']
            
            state_var = tk.BooleanVar(value=is_on)
            
            button = ttk.Button(sub_frame)
            button.pack(fill=tk.X, expand=True)

            def update_button_state():
                # Updates the button's appearance based on its current state.
                current_state = state_var.get()
                if current_state: # State is ON
                    button.config(text=on_config.get('label', 'ON'), style='Selected.TButton')
                else: # State is OFF
                    button.config(text=off_config.get('label', 'OFF'), style='TButton')

            def toggle_command():
                # Flips the state, updates the button, and publishes the change.
                new_state = not state_var.get()
                state_var.set(new_state)
                update_button_state()
                publish_value = 'ON' if new_state else 'OFF'
                
                # Log the action to the GUI logger before sending.
                self._log_to_gui(f"GUI ACTION: Publishing to '{path}' with value '{publish_value}'")
                self.mqtt_util.publish_message(subtopic=path, value=publish_value)

            button.config(command=toggle_command)
            update_button_state() # Set initial text and style

            # Store the state variable and update function for live updates.
            if path:
                self.topic_widgets[path] = (state_var, update_button_state)
            
            return sub_frame

        except Exception as e:
            console_log(f"❌ Error in _create_gui_button_toggle for '{label}': {e}")
            return None