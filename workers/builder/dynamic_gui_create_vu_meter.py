# workers/builder/dynamic_gui_create_vu_meter.py

import tkinter as tk
from tkinter import ttk
import math

class VUMeterCreatorMixin:
    def _create_vu_meter(self, parent_frame, label, config, path):
        """Creates a VU meter widget."""
        frame = ttk.Frame(parent_frame)
        frame.pack(fill=tk.X, padx=10, pady=5)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.TOP, pady=(0, 5))

        min_val = config.get("min", -20.0)
        max_val = config.get("max", 3.0)
        red_zone_start = config.get("upper_range", 0.0)
        width = config.get("width", 200)
        height = config.get("height", 20)

        canvas = tk.Canvas(frame, width=width, height=height, bg='gray')
        canvas.pack()

        # Draw the background
        red_zone_x = (red_zone_start - min_val) / (max_val - min_val) * width
        canvas.create_rectangle(0, 0, red_zone_x, height, fill='green', outline='')
        canvas.create_rectangle(red_zone_x, 0, width, height, fill='red', outline='')
        
        # The indicator
        indicator = canvas.create_rectangle(0, 0, 5, height, fill='yellow', outline='')
        
        self.topic_widgets[path] = {
            "widget": canvas,
            "indicator": indicator,
            "min": min_val,
            "max": max_val,
            "width": width
        }

        def _update_vu(value):
            try:
                float_value = float(value)
                if float_value < min_val:
                    float_value = min_val
                if float_value > max_val:
                    float_value = max_val
                
                x_pos = (float_value - min_val) / (max_val - min_val) * width
                canvas.coords(indicator, x_pos - 2.5, 0, x_pos + 2.5, height)

            except (ValueError, TypeError):
                pass # Or log an error

        # self.mqtt_callbacks[path] = _update_vu
