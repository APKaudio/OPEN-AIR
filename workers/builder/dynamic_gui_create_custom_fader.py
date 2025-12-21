# workers/builder/dynamic_gui_create_custom_fader.py

import tkinter as tk
from tkinter import ttk
import math

class CustomFaderCreatorMixin:
    def _create_custom_fader(self, parent_frame, label, config, path):
        """Creates a custom fader widget."""
        frame = ttk.Frame(parent_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.TOP, pady=(0, 5))

        width = config.get("width", 50)
        height = config.get("height", 200)
        min_val = config.get("min", 0)
        max_val = config.get("max", 100)
        value_default = config.get("value_default", 75)

        canvas = tk.Canvas(frame, width=width, height=height)
        canvas.pack()

        self._draw_fader(canvas, width, height, value_default, min_val, max_val)

        value_label = ttk.Label(frame, text=f"{value_default}")
        value_label.pack()

        def _on_drag(event):
            y = event.y
            if y < 0: y = 0
            if y > height: y = height
            
            value = max_val - (y / height) * (max_val - min_val)
            
            self._draw_fader(canvas, width, height, value, min_val, max_val)
            value_label.config(text=f"{int(value)}")
            # MQTT publish logic would go here

        canvas.bind("<B1-Motion>", _on_drag)

        self.topic_widgets[path] = {
            "widget": canvas,
            "value_label": value_label,
            "width": width,
            "height": height,
            "min": min_val,
            "max": max_val
        }

        def _update_fader(value):
            try:
                float_value = float(value)
                self._draw_fader(canvas, width, height, float_value, min_val, max_val)
                value_label.config(text=f"{int(float_value)}")
            except (ValueError, TypeError):
                pass
        
        # self.mqtt_callbacks[path] = _update_fader

    def _draw_fader(self, canvas, width, height, value, min_val, max_val):
        canvas.delete("all")
        # Fader track
        canvas.create_rectangle(width/2 - 2, 10, width/2 + 2, height - 10, fill="gray")
        
        # Fader handle
        y_pos = (max_val - value) / (max_val - min_val) * (height - 20) + 10
        canvas.create_rectangle(5, y_pos - 5, width - 5, y_pos + 5, fill="blue")

