# workers/builder/dynamic_gui_create_knob.py
#
# A Standard Rotary Knob (Min -> Max) with Mouse Wheel & Reset support.
# Version 20251223.223000.Interactive

import tkinter as tk
from tkinter import ttk
import math
import workers.setup.app_constants as app_constants
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
from workers.styling.style import THEMES, DEFAULT_THEME
import os

class KnobCreatorMixin:
    def _create_knob(self, parent_frame, label, config, path):
        """Creates a standard rotary knob (starts at min, goes to value)."""
        current_function_name = "_create_knob"
        
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
            min_val = config.get("min", 0)
            max_val = config.get("max", 100)
            value_default = config.get("value_default", min_val)
            step = config.get("step", 1) # Scroll step size

            canvas = tk.Canvas(frame, width=width, height=height, bg=bg_color, highlightthickness=0)
            canvas.pack()

            # Store state in the widget for callbacks
            state = {
                "value": value_default,
                "last_y": 0
            }

            def update_knob(new_val):
                # Clamp
                new_val = max(min_val, min(max_val, new_val))
                state["value"] = new_val
                
                # Redraw
                self._draw_knob(canvas, width, height, new_val, min_val, max_val, fg_color, accent_color, secondary_color)
                value_label.config(text=f"{int(new_val)}")
                # self._transmit_command(path, new_val)

            # Draw initial
            self._draw_knob(canvas, width, height, value_default, min_val, max_val, fg_color, accent_color, secondary_color)

            value_label = ttk.Label(frame, text=str(value_default), font=("Helvetica", 8))
            value_label.pack(side=tk.BOTTOM)

            self.topic_widgets[path] = (value_label, canvas)

            # --- Interactions ---
            
            def on_click(event):
                # Check for CTRL key (Reset)
                if event.state & 4: # 4 is Control mask on most systems
                    update_knob(value_default)
                    return
                state["last_y"] = event.y

            def on_drag(event):
                delta = state["last_y"] - event.y
                state["last_y"] = event.y
                # Sensitivity: Full height = full range
                change = (delta / 100.0) * (max_val - min_val)
                update_knob(state["value"] + change)

            def on_scroll(event):
                # Windows/Mac: event.delta. Linux: Button-4/5
                delta = 0
                if event.num == 5 or event.delta < 0:
                    delta = -step
                elif event.num == 4 or event.delta > 0:
                    delta = step
                
                update_knob(state["value"] + delta)

            canvas.bind("<Button-1>", on_click)
            canvas.bind("<B1-Motion>", on_drag)
            
            # Scroll Bindings (Platform Agnostic)
            canvas.bind("<MouseWheel>", on_scroll) # Windows/Mac
            canvas.bind("<Button-4>", on_scroll)   # Linux Up
            canvas.bind("<Button-5>", on_scroll)   # Linux Down

            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(message=f"✅ Knob '{label}' ready. Ctrl+Click resets.", **_get_log_args())
            
            return frame

        except Exception as e:
            debug_log(message=f"💥 KABOOM! Knob error: {e}")
            return None

    def _draw_knob(self, canvas, width, height, value, min_val, max_val, fg, accent, secondary):
        canvas.delete("all")
        cx, cy = width / 2, height / 2
        radius = min(width, height) / 2 - 5

        # Track (240 to -60 degrees = 300 span)
        # Tkinter Angles: 0=3pm, 90=12pm, 180=9pm, 270=6pm
        # 8pm is approx 240 deg. 4pm is -60 (or 300)
        start_angle = 240
        extent = -300 
        
        canvas.create_arc(5, 5, width-5, height-5, start=start_angle, extent=extent, style=tk.ARC, outline=secondary, width=4)

        # Value Arc
        norm_val = (value - min_val) / (max_val - min_val) if max_val > min_val else 0
        val_extent = extent * norm_val
        canvas.create_arc(5, 5, width-5, height-5, start=start_angle, extent=val_extent, style=tk.ARC, outline=accent, width=4)

        # Pointer
        angle_rad = math.radians(start_angle + val_extent)
        px = cx + radius * math.cos(angle_rad)
        py = cy - radius * math.sin(angle_rad)
        canvas.create_line(cx, cy, px, py, fill=fg, width=2, capstyle=tk.ROUND)