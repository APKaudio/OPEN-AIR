# workers/builder/dynamic_gui_create_needle_vu_meter.py
#
# A needle-style VU Meter that respects the global theme configuration.
# Version 20251223.220000.ThemeFix

import tkinter as tk
from tkinter import ttk
import math
import workers.setup.app_constants as app_constants
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
from display.styling.style import THEMES, DEFAULT_THEME
import os

class NeedleVUMeterCreatorMixin:
    def _create_needle_vu_meter(self, parent_frame, label, config, path):
        """Creates a needle-style VU meter widget."""
        current_function_name = "_create_needle_vu_meter"
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🔬⚡️ Entering '{current_function_name}' to calibrate a themed needle VU meter for '{label}'.",
                **_get_log_args()
            )

        # Theme Resolution
        colors = THEMES.get(DEFAULT_THEME, THEMES["dark"])
        bg_color = colors.get("bg", "#2b2b2b")
        fg_color = colors.get("fg", "#dcdcdc")
        accent_color = colors.get("accent", "#33A1FD")
        secondary_color = colors.get("secondary", "#444444")
        danger_color = "#FF4500"  # Consistent Danger Red

        frame = ttk.Frame(parent_frame)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.TOP, pady=(0, 5))

        try:
            size = config.get("size", 150)
            min_val = config.get("min", -20.0)
            max_val = config.get("max", 3.0)
            red_zone_start = config.get("upper_range", 0.0)
            value_default = config.get("value_default", -20)

            # Canvas with Theme Background
            canvas = tk.Canvas(frame, width=size, height=size/2 + 20, bg=bg_color, highlightthickness=0)
            canvas.pack()

            # Pass theme colors to the draw function
            self._draw_needle_vu_meter(
                canvas, size, value_default, min_val, max_val, red_zone_start,
                accent_color, secondary_color, fg_color, danger_color
            )
            
            self.topic_widgets[path] = {
                "widget": canvas,
                "size": size,
                "min": min_val,
                "max": max_val,
                "red_zone_start": red_zone_start,
                "colors": (accent_color, secondary_color, fg_color, danger_color)
            }

            def _update_needle(value):
                try:
                    float_value = float(value)
                    self._draw_needle_vu_meter(
                        canvas, size, float_value, min_val, max_val, red_zone_start,
                        accent_color, secondary_color, fg_color, danger_color
                    )
                except (ValueError, TypeError) as e:
                    if app_constants.LOCAL_DEBUG_ENABLE:
                        debug_log(message=f"🔴 ERROR in _update_needle: {e}", file=os.path.basename(__file__), function=current_function_name)
            
            # Handle Resize
            canvas.bind("<Configure>", lambda e: self._draw_needle_vu_meter(
                canvas, size, value_default, min_val, max_val, red_zone_start,
                accent_color, secondary_color, fg_color, danger_color
            ))

            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"✅ SUCCESS! The themed needle VU meter for '{label}' is twitching with life!",
                    **_get_log_args()
                )
            return frame

        except Exception as e:
            debug_log(message=f"💥 KABOOM! The needle VU meter for '{label}' has flatlined! Error: {e}")
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"💥 KABOOM! The needle VU meter for '{label}' has flatlined! Error: {e}",
                    **_get_log_args()
                )
            return None


    def _draw_needle_vu_meter(self, canvas, size, value, min_val, max_val, red_zone_start, accent, secondary, fg, danger):
        canvas.delete("all")
        width = size
        height = size / 2

        # 1. Main Arc (The Track) - Uses Secondary Theme Color
        canvas.create_arc(10, 10, width - 10, width - 10, start=0, extent=180, style=tk.ARC, outline=secondary, width=2)

        # 2. Red Zone - Uses Danger Color
        red_start_angle = ((red_zone_start - min_val) / (max_val - min_val)) * 180
        canvas.create_arc(10, 10, width - 10, width - 10, start=0, extent=180 - red_start_angle, style=tk.ARC, outline=danger, width=4)

        # 3. The Needle Calculation
        if value < min_val: value = min_val
        if value > max_val: value = max_val
        
        # Invert angle logic so min is Left (180) and max is Right (0)
        angle = (1 - (value - min_val) / (max_val - min_val)) * math.pi
        
        center_x = width / 2
        center_y = height + 10
        
        needle_len = height - 15
        x = center_x + needle_len * math.cos(angle)
        y = center_y - needle_len * math.sin(angle) # Canvas Y is inverted
        
        # 4. Draw Needle (Accent Color)
        canvas.create_line(center_x, center_y, x, y, width=3, fill=accent, capstyle=tk.ROUND)
        
        # 5. Draw Pivot (Foreground Color)
        canvas.create_oval(center_x - 5, center_y - 5, center_x + 5, center_y + 5, fill=fg, outline=secondary)