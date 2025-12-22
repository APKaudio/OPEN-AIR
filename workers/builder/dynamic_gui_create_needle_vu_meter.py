# workers/builder/dynamic_gui_create_needle_vu_meter.py

import tkinter as tk
from tkinter import ttk
import math
import workers.setup.app_constants as app_constants
from workers.logger.logger import debug_log, console_log
import os

class NeedleVUMeterCreatorMixin:
    def _create_needle_vu_meter(self, parent_frame, label, config, path):
        """Creates a needle-style VU meter widget."""
        current_function_name = "_create_needle_vu_meter"
        if app_constants.Local_Debug_Enable:
            debug_log(message=f"Creating needle VU meter for {label}", file=os.path.basename(__file__), function=current_function_name)

        frame = ttk.Frame(parent_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.TOP, pady=(0, 5))

        try:
            size = config.get("size", 150)
            min_val = config.get("min", -20.0)
            max_val = config.get("max", 3.0)
            red_zone_start = config.get("upper_range", 0.0)
            value_default = config.get("value_default", -20)

            canvas = tk.Canvas(frame, width=size, height=size/2 + 20)
            canvas.pack()

            self._draw_needle_vu_meter(canvas, size, value_default, min_val, max_val, red_zone_start)
            
            self.topic_widgets[path] = {
                "widget": canvas,
                "size": size,
                "min": min_val,
                "max": max_val,
                "red_zone_start": red_zone_start
            }

            def _update_needle(value):
                try:
                    float_value = float(value)
                    self._draw_needle_vu_meter(canvas, size, float_value, min_val, max_val, red_zone_start)
                except (ValueError, TypeError) as e:
                    if app_constants.Local_Debug_Enable:
                        debug_log(message=f"🔴 ERROR in _update_needle: {e}", file=os.path.basename(__file__), function=current_function_name, console_print_func=console_log)
            
            # self.mqtt_callbacks[path] = _update_needle
        except Exception as e:
            console_log(f"🔴 ERROR creating needle VU meter: {e}")
            if app_constants.Local_Debug_Enable:
                debug_log(message=f"🔴 ERROR creating needle VU meter: {e}", file=os.path.basename(__file__), function=current_function_name, console_print_func=console_log)


    def _draw_needle_vu_meter(self, canvas, size, value, min_val, max_val, red_zone_start):
        canvas.delete("all")
        width = size
        height = size / 2

        # Draw the arc
        canvas.create_arc(10, 10, width - 10, width - 10, start=0, extent=180, style=tk.ARC, outline="gray", width=2)

        # Draw the red zone
        red_start_angle = ((red_zone_start - min_val) / (max_val - min_val)) * 180
        canvas.create_arc(10, 10, width - 10, width - 10, start=0, extent=180 - red_start_angle, style=tk.ARC, outline="red", width=4)

        # Draw the needle
        if value < min_val: value = min_val
        if value > max_val: value = max_val
        angle = (1 - (value - min_val) / (max_val - min_val)) * math.pi
        
        center_x = width / 2
        center_y = height + 10
        
        needle_len = height - 10
        x = center_x + needle_len * math.cos(angle)
        y = center_y - needle_len * math.sin(angle)
        
        canvas.create_line(center_x, center_y, x, y, width=2, fill="blue")
        canvas.create_oval(center_x - 5, center_y - 5, center_x + 5, center_y + 5, fill="black")