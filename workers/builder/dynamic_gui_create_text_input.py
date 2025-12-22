# workers/builder/dynamic_gui_create_text_input.py

import tkinter as tk
from tkinter import ttk
import workers.setup.app_constants as app_constants
from workers.logger.logger import debug_log, console_log
import os

class TextInputCreatorMixin:
    def _create_text_input(self, parent_frame, label, config, path):
        """Creates a text input widget."""
        current_function_name = "_create_text_input"
        if app_constants.Local_Debug_Enable:
            debug_log(message=f"Creating text input for {label}", file=os.path.basename(__file__), function=current_function_name)

        frame = ttk.Frame(parent_frame)
        frame.pack(fill=tk.X, padx=10, pady=5)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.LEFT, padx=(0, 10))

        try:
            text_var = tk.StringVar()
            text_var.set(config.get("value_default", ""))
            
            entry = ttk.Entry(
                frame,
                textvariable=text_var
            )
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # This widget can both be controlled and be a controller
            # When the user types, it can publish the value to an MQTT topic
            def _on_text_change(*args):
                try:
                    # This is where you would add logic to publish the value
                    # For example, using self.mqtt_util.publish(...)
                    if app_constants.Local_Debug_Enable:
                        debug_log(message=f"Text changed for {label}: {text_var.get()}", file=os.path.basename(__file__), function="_on_text_change")
                except Exception as e:
                    if app_constants.Local_Debug_Enable:
                        debug_log(message=f"🔴 ERROR in _on_text_change: {e}", file=os.path.basename(__file__), function="_on_text_change", console_print_func=console_log)


            text_var.trace("w", _on_text_change)

            self.topic_widgets[path] = {
                "widget": entry,
                "variable": text_var
            }

            # Add logic to handle incoming MQTT messages to update the text input
            def _update_text(value):
                try:
                    text_var.set(str(value))
                except (ValueError, TypeError) as e:
                    if app_constants.Local_Debug_Enable:
                        debug_log(message=f"🔴 ERROR in _update_text: {e}", file=os.path.basename(__file__), function=current_function_name, console_print_func=console_log)

            # self.mqtt_callbacks[path] = _update_text
        except Exception as e:
            console_log(f"🔴 ERROR creating text input: {e}")
            if app_constants.Local_Debug_Enable:
                debug_log(message=f"🔴 ERROR creating text input: {e}", file=os.path.basename(__file__), function=current_function_name, console_print_func=console_log)