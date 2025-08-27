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
# Version 20250827.171501.1

import os
import tkinter as tk
from tkinter import ttk
from workers.worker_logging import debug_log, console_log
import inspect

# --- Global Scope Variables ---
current_version = "20250827.171501.1"
current_version_hash = (20250827 * 171501 * 1)
current_file = f"{os.path.basename(__file__)}"

class GuiButtonToggleCreatorMixin:
    def _create_gui_button_toggle(self, parent_frame, label, config, path):
        # A one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        
        # FIX: The debug_log call has been corrected to use global variables
        # and remove the problematic 'self.current_class_name' attribute access.
        debug_log(
            message=f"🛠️🟢 Entering {current_function_name} to conjure a button widget for '{label}'.",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )
        try:
            initial_value = config.get("value", False)
            on_value = config.get("on_value", True)
            off_value = config.get("off_value", False)
            on_text = config.get("on_text", "ON")
            off_text = config.get("off_text", "OFF")
            
            frame = ttk.Frame(parent_frame, style="TFrame")
            frame.pack(fill=tk.X, expand=True, pady=2, padx=5)

            label_widget = ttk.Label(frame, text=label)
            label_widget.pack(side=tk.LEFT, padx=(0, 10))

            button_var = tk.BooleanVar(value=initial_value)
            button = ttk.Button(frame, text=off_text, command=lambda: toggle_command(button_var.get()))
            button.pack(side=tk.LEFT, fill=tk.X, expand=True)

            def update_button_state():
                # A brief, one-sentence description of the function's purpose.
                try:
                    state = button_var.get()
                    if state == on_value:
                        button.configure(text=on_text, style="Selected.TButton")
                    else:
                        button.configure(text=off_text, style="TButton")
                except Exception as e:
                    console_log(f"❌ Error updating button state: {e}")
            
            def toggle_command(current_state):
                # A brief, one-sentence description of the function's purpose.
                try:
                    new_state = not current_state
                    button_var.set(new_state)
                    
                    value_to_publish = on_value if new_state else off_value
                    self.mqtt_util.publish_message(
                        topic=path, 
                        subtopic="state",
                        value=value_to_publish
                    )
                except Exception as e:
                    console_log(f"❌ Error in toggle_command: {e}")

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