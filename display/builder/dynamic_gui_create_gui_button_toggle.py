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
# Version 20250828.235500.3

import os
import tkinter as tk
from tkinter import ttk
from workers.worker_logging import debug_log, console_log
import inspect

# --- Global Scope Variables ---
current_version = "20250828.235500.3"
current_version_hash = (20250828 * 235500 * 3)
current_file = f"{os.path.basename(__file__)}"

class GuiButtonToggleCreatorMixin:
    def _create_gui_button_toggle(self, parent_frame, label, config, path):
        # A one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name

        debug_log(
            message=f"🛠️🟢 Entering '{current_function_name}' to conjure a button widget for '{label}'.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            options_map = config.get('options', {})
            on_text = options_map.get('ON', {}).get('label', 'ON')
            off_text = options_map.get('OFF', {}).get('label', 'OFF')

            # Determine initial state based on the 'selected' key in ON/OFF options
            # If both are selected, default to ON. If neither, default to OFF.
            if options_map.get('ON', {}).get('selected', False):
                initial_state_key = 'ON'
            elif options_map.get('OFF', {}).get('selected', False):
                initial_state_key = 'OFF'
            else:
                initial_state_key = 'OFF'

            button_var = tk.StringVar(value=initial_state_key)

            def update_button_state():
                state = button_var.get()
                if state == 'ON':
                    button.configure(text=on_text, style="Selected.TButton")
                else:
                    button.configure(text=off_text, style="TButton")

            def toggle_state_and_publish():
                current_state_key = button_var.get()
                new_state_key = 'OFF' if current_state_key == 'ON' else 'ON'

                # Deselect the previous option by publishing a 'false' payload.
                old_path = f"{path}/options/{current_state_key}/selected"
                self._transmit_command(relative_topic=old_path, payload='false')

                # Select the new option by publishing a 'true' payload.
                new_path = f"{path}/options/{new_state_key}/selected"
                self._transmit_command(relative_topic=new_path, payload='true')

            button = ttk.Button(parent_frame, text=on_text if initial_state_key == 'ON' else off_text, command=toggle_state_and_publish)
            button.pack(fill=tk.X, expand=True)
            
            # This is the corrected update logic for the toggle button.
            self.topic_widgets[f"{path}/options/ON/selected"] = (button_var, update_button_state)
            self.topic_widgets[f"{path}/options/OFF/selected"] = (button_var, update_button_state)

            update_button_state()
            
            console_log("✅ Celebration of success! the " + label + " did toggle its function")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🛠️🔴 Arrr, the code be capsized! The toggle button creation has failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=current_function_name,
                console_print_func=console_log
            )