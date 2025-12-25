# workers/builder/dynamic_gui_create_panner.py
#
# A Tkinter Canvas-based Panner that respects the global theme.
# Version 20251223.214500.ThemeFix

import tkinter as tk
from tkinter import ttk
import math
from workers.mqtt.setup.config_reader import app_constants
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
from workers.styling.style import THEMES, DEFAULT_THEME
import os

class PannerCreatorMixin:
    def _create_panner(self, parent_frame, label, config, path):
        """Creates a rotary panner widget."""
        current_function_name = "_create_panner"
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🔬⚡️ Entering '{current_function_name}' to forge a themed panner for '{label}'.",
                **_get_log_args()
            )

        # Resolve Theme Colors
        colors = THEMES.get(DEFAULT_THEME, THEMES["dark"])
        bg_color = colors.get("bg", "#2b2b2b")
        fg_color = colors.get("fg", "#dcdcdc")
        accent_color = colors.get("accent", "#33A1FD")
        secondary_color = colors.get("secondary", "#444444")

        frame = ttk.Frame(parent_frame)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.TOP, pady=(0, 5))

        try:
            width = config.get("width", 50)
            height = config.get("height", 50)
            min_val = config.get("min", -100)
            max_val = config.get("max", 100)
            value_default = config.get("value_default", 0)

            # Canvas with Theme Background
            canvas = tk.Canvas(frame, width=width, height=height, bg=bg_color, highlightthickness=0)
            canvas.pack()

            self._draw_knob(canvas, width, height, value_default, min_val, max_val, fg_color, accent_color, secondary_color)

            # Value Label
            value_label = ttk.Label(frame, text=str(value_default), font=("Helvetica", 8))
            value_label.pack(side=tk.BOTTOM)

            self.topic_widgets[path] = (value_label, canvas)

            # Drag Interaction
            def on_drag(event):
                # Calculate angle from center
                dx = event.x - width / 2
                dy = height / 2 - event.y # Invert Y for standard cartesian
                angle = math.degrees(math.atan2(dy, dx))
                
                # Normalize angle (0-180 is top half, -180 to 0 is bottom)
                # This is a simple approximation; a real knob needs start/end angle limits
                if angle < 0: angle += 360
                
                # Map angle to value (Simplified 0-100 logic for demo)
                # For better control, use delta-y dragging:
                delta = 0
                if hasattr(self, '_last_drag_y'):
                    delta = self._last_drag_y - event.y
                self._last_drag_y = event.y
                
                current_val = float(value_label.cget("text"))
                new_val = current_val + (delta * (max_val - min_val) / 100)
                new_val = max(min_val, min(max_val, new_val))
                
                value_label.config(text=f"{int(new_val)}")
                self._draw_knob(canvas, width, height, new_val, min_val, max_val, fg_color, accent_color, secondary_color)
                
                self._transmit_command(widget_name=path, value=new_val)

            def on_click(event):
                self._last_drag_y = event.y

            canvas.bind("<Button-1>", on_click)
            canvas.bind("<B1-Motion>", on_drag)

            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"✅ SUCCESS! The themed panner '{label}' is calibrated!",
                    **_get_log_args()
                )
            return frame

        except Exception as e:
            debug_log(message=f"💥 KABOOM! The panner '{label}' shattered! Error: {e}")
            return None

    def _draw_knob(self, canvas, width, height, value, min_val, max_val, fg, accent, secondary):
        canvas.delete("all")
        cx, cy = width / 2, height / 2
        radius = min(width, height) / 2 - 5

        # 1. Background Arc (The Track)
        start_angle = 240
        extent = -300 # 300 degrees total travel
        canvas.create_arc(5, 5, width-5, height-5, start=start_angle, extent=extent, style=tk.ARC, outline=secondary, width=4)

        # 2. Value Arc (The Active Level)
        # Normalize value 0.0 to 1.0
        norm_val = (value - min_val) / (max_val - min_val) if max_val > min_val else 0
        val_extent = extent * norm_val
        canvas.create_arc(5, 5, width-5, height-5, start=start_angle, extent=val_extent, style=tk.ARC, outline=accent, width=4)

        # 3. The Pointer Line
        angle_rad = math.radians(start_angle + val_extent)
        px = cx + radius * math.cos(angle_rad)
        py = cy - radius * math.sin(angle_rad) # Canvas Y is inverted
        canvas.create_line(cx, cy, px, py, fill=fg, width=2, capstyle=tk.ROUND)