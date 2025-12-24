# workers/builder/dynamic_gui_create_panner.py
#
# A "Pan" style knob that centers at 0 and draws arcs Left or Right.
# Version 20251223.223000.New

import tkinter as tk
from tkinter import ttk
import math
import workers.setup.app_constants as app_constants
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
from workers.styling.style import THEMES, DEFAULT_THEME
import os

class PannerCreatorMixin:
    def _create_panner(self, parent_frame, label, config, path):
        """Creates a Pan knob (Center 0, Left/Right arcs)."""
        current_function_name = "_create_panner"
        
        # Theme Resolution
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
            min_val = config.get("min", -100) # Default Pan Range
            max_val = config.get("max", 100)
            value_default = config.get("value_default", 0) # Default Center
            step = config.get("step", 1)

            canvas = tk.Canvas(frame, width=width, height=height, bg=bg_color, highlightthickness=0)
            canvas.pack()

            state = { "value": value_default, "last_y": 0 }

            def update_panner(new_val):
                new_val = max(min_val, min(max_val, new_val))
                state["value"] = new_val
                
                self._draw_panner(canvas, width, height, new_val, min_val, max_val, fg_color, accent_color, secondary_color)
                value_label.config(text=f"{int(new_val)}")

            # Initial Draw
            self._draw_panner(canvas, width, height, value_default, min_val, max_val, fg_color, accent_color, secondary_color)

            value_label = ttk.Label(frame, text=str(value_default), font=("Helvetica", 8))
            value_label.pack(side=tk.BOTTOM)

            self.topic_widgets[path] = (value_label, canvas)

            # --- Interactions ---
            def on_click(event):
                if event.state & 4: # CTRL
                    update_panner(value_default)
                    return
                state["last_y"] = event.y

            def on_drag(event):
                delta = state["last_y"] - event.y
                state["last_y"] = event.y
                change = (delta / 100.0) * (max_val - min_val)
                update_panner(state["value"] + change)

            def on_scroll(event):
                delta = 0
                if event.num == 5 or event.delta < 0: delta = -step
                elif event.num == 4 or event.delta > 0: delta = step
                update_panner(state["value"] + delta)

            canvas.bind("<Button-1>", on_click)
            canvas.bind("<B1-Motion>", on_drag)
            canvas.bind("<MouseWheel>", on_scroll)
            canvas.bind("<Button-4>", on_scroll)
            canvas.bind("<Button-5>", on_scroll)

            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(message=f"✅ Panner '{label}' initialized.", **_get_log_args())
            
            return frame

        except Exception as e:
            debug_log(message=f"💥 Panner Error: {e}")
            return None

    def _draw_panner(self, canvas, width, height, value, min_val, max_val, fg, accent, secondary):
        canvas.delete("all")
        cx, cy = width / 2, height / 2
        radius = min(width, height) / 2 - 5

        # Background Arc (Same 300 degree span: 240 to -60)
        # However, for visual clarity, let's keep the track static
        canvas.create_arc(5, 5, width-5, height-5, start=240, extent=-300, style=tk.ARC, outline=secondary, width=4)

        # Center Tick (12 o'clock = 90 degrees)
        canvas.create_line(cx, cy-radius+5, cx, cy-radius-2, fill=secondary, width=2)

        # Value Arc
        # Center is 90 degrees.
        # Max Right (max_val) is -60 degrees. (Span 150 deg CW)
        # Max Left (min_val) is 240 degrees. (Span 150 deg CCW)
        
        start_angle = 90
        extent = 0
        
        if value > 0:
            # Drawing Clockwise (Negative extent)
            # 0 -> 0, Max -> -150
            ratio = value / max_val
            extent = ratio * -150
        elif value < 0:
            # Drawing Counter-Clockwise (Positive extent)
            # 0 -> 0, Min -> +150
            ratio = abs(value) / abs(min_val)
            extent = ratio * 150
            
        if abs(extent) > 1: # Only draw if distinct from center
            canvas.create_arc(5, 5, width-5, height-5, start=start_angle, extent=extent, style=tk.ARC, outline=accent, width=4)

        # Pointer
        angle_rad = math.radians(start_angle + extent)
        px = cx + radius * math.cos(angle_rad)
        py = cy - radius * math.sin(angle_rad)
        canvas.create_line(cx, cy, px, py, fill=fg, width=2, capstyle=tk.ROUND)