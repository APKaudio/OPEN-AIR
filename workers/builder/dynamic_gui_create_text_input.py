# workers/builder/dynamic_gui_create_text_input.py

import tkinter as tk
from tkinter import ttk

class TextInputCreatorMixin:
    def _create_text_input(self, parent_frame, label, config, path):
        """Creates a text input widget."""
        frame = ttk.Frame(parent_frame)
        frame.pack(fill=tk.X, padx=10, pady=5)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.LEFT, padx=(0, 10))

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
            # This is where you would add logic to publish the value
            # For example, using self.mqtt_util.publish(...)
            pass

        text_var.trace("w", _on_text_change)

        self.topic_widgets[path] = {
            "widget": entry,
            "variable": text_var
        }

        # Add logic to handle incoming MQTT messages to update the text input
        def _update_text(value):
            try:
                text_var.set(str(value))
            except (ValueError, TypeError):
                pass # Or log an error

        self.mqtt_callbacks[path] = _update_text
