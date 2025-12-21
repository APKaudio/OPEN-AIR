# workers/builder/dynamic_gui_create_fader.py

import tkinter as tk
from tkinter import ttk

class FaderCreatorMixin:
    def _create_fader(self, parent_frame, label, config, path):
        """Creates a fader widget."""
        frame = ttk.Frame(parent_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.TOP, pady=(0, 5))

        orient = config.get("orientation", "vertical")
        
        scale = ttk.Scale(
            frame,
            from_=config.get("min", 0),
            to=config.get("max", 100),
            orient=orient,
            value=config.get("value_default", 0)
        )
        
        if orient == "vertical":
            scale.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        else:
            scale.pack(side=tk.TOP, fill=tk.X, expand=True)

        value_label = ttk.Label(frame, text=f"{scale.get():.2f}")
        if orient == "vertical":
            value_label.pack(side=tk.BOTTOM, pady=(5,0))
        else:
            value_label.pack(side=tk.RIGHT, padx=(10,0))


        def _on_scale_move(value):
            value_label.config(text=f"{float(value):.2f}")
            # Here you would add logic to publish the value via MQTT
            # self.mqtt_util.publish(path, value)

        scale.config(command=_on_scale_move)

        self.topic_widgets[path] = {
            "widget": scale,
            "value_label": value_label
        }

        def _update_fader(value):
            try:
                float_value = float(value)
                scale.set(float_value)
                value_label.config(text=f"{float_value:.2f}")
            except (ValueError, TypeError):
                pass # Or log an error

        # self.mqtt_callbacks[path] = _update_fader
