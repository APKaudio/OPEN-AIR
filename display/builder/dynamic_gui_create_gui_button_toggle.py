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
# Version 20250828.215819.4

import os
import tkinter as tk
from tkinter import ttk
from workers.worker_logging import debug_log, console_log
import inspect

# --- Global Scope Variables ---
current_version = "20250828.215819.4"
current_version_hash = (20250828 * 215819 * 4)
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
            on_text = config.get('options', {}).get('ON', {}).get('label', 'ON')
            off_text = config.get('options', {}).get('OFF', {}).get('label', 'OFF')
            on_value = config.get('options', {}).get('ON', {}).get('value', True)
            off_value = config.get('options', {}).get('OFF', {}).get('value', False)

            initial_state = config.get('options', {}).get('ON', {}).get('selected', False)
            button_var = tk.BooleanVar(value=initial_state)

            def toggle_state_and_publish():
                current_state = button_var.get()
                new_state = not current_state
                button_var.set(new_state)

                value_to_publish = on_value if new_state else off_value

                # CORRECTED: Use the standardized transmit method, as intended by the new architecture.
                self._transmit_command(relative_topic=f"{path}/state", payload=value_to_publish)

            button = ttk.Button(parent_frame, text=on_text if initial_state else off_text, command=toggle_state_and_publish)
            button.pack(fill=tk.X, expand=True)

            def update_button_state():
                if button_var.get():
                    button.configure(text=on_text, style="Selected.TButton")
                else:
                    button.configure(text=off_text, style="TButton")

            update_button_state()
            self.topic_widgets[f"{path}/state"] = (button_var, update_button_state)

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