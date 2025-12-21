# workers/builder/dynamic_gui_create_inc_dec_buttons.py

import tkinter as tk
from tkinter import ttk

class IncDecButtonsCreatorMixin:
    def _create_inc_dec_buttons(self, parent_frame, label, config, path):
        """Creates increment/decrement buttons."""
        frame = ttk.Frame(parent_frame)
        frame.pack(fill=tk.X, padx=10, pady=5)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.LEFT, padx=(0, 10))

        # Initial value and range (optional, can be used for boundary checks)
        value_default = config.get("value_default", 0)
        increment_amount = config.get("increment", 1)

        current_value = tk.IntVar(value=value_default)
        
        value_display = ttk.Label(frame, textvariable=current_value)
        value_display.pack(side=tk.RIGHT, padx=(10, 0))

        def _increment():
            new_value = current_value.get() + increment_amount
            current_value.set(new_value)
            # self.mqtt_util.publish(path, new_value) # MQTT publish

        def _decrement():
            new_value = current_value.get() - increment_amount
            current_value.set(new_value)
            # self.mqtt_util.publish(path, new_value) # MQTT publish

        dec_button = ttk.Button(frame, text="⬇", command=_decrement)
        dec_button.pack(side=tk.RIGHT)

        inc_button = ttk.Button(frame, text="⬆", command=_increment)
        inc_button.pack(side=tk.RIGHT, padx=(5, 0))

        self.topic_widgets[path] = {
            "widget": frame,
            "variable": current_value
        }

        def _update_value(value):
            try:
                current_value.set(int(value))
            except (ValueError, TypeError):
                pass
        
        # self.mqtt_callbacks[path] = _update_value
