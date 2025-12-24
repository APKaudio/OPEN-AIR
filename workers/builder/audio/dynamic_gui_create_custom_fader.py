# workers/builder/dynamic_gui_create_custom_fader.py
#
# A vertical fader widget that adapts to the system theme.
# Version 20251223.214500.ThemeFix

import tkinter as tk
from tkinter import ttk
import math
import workers.setup.app_constants as app_constants
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
from workers.styling.style import THEMES, DEFAULT_THEME
import os

class CustomFaderCreatorMixin:
    def _create_custom_fader(self, parent_frame, label, config, path):
        """Creates a custom fader widget."""
        current_function_name = "_create_custom_fader"
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🔬⚡️ Entering '{current_function_name}' to sculpt a custom fader for '{label}'.",
                **_get_log_args()
            )

        # Theme Resolution
        colors = THEMES.get(DEFAULT_THEME, THEMES["dark"])
        bg_color = colors.get("bg", "#2b2b2b")
        accent_color = colors.get("accent", "#33A1FD")
        secondary_color = colors.get("secondary", "#444444")
        handle_color = colors.get("fg", "#dcdcdc")

        frame = ttk.Frame(parent_frame)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.TOP, pady=(0, 5))

        try:
            # Layout logic handles size, but we need defaults for the canvas
            width = config.get("width", 40)
            height = config.get("height", 200)
            min_val = config.get("min", 0)
            max_val = config.get("max", 100)
            value_default = config.get("value_default", 75)

            # Force canvas to match theme background so it blends in
            canvas = tk.Canvas(frame, width=width, height=height, bg=bg_color, highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True)

            self._draw_fader(canvas, width, height, value_default, min_val, max_val, secondary_color, accent_color)

            # Interaction
            def on_drag(event):
                # Map Y position to Value
                # Y=0 is Top (Max), Y=Height is Bottom (Min)
                h = canvas.winfo_height()
                y = max(10, min(h-10, event.y))
                norm = 1 - ((y - 10) / (h - 20)) # 0.0 to 1.0
                new_val = min_val + (norm * (max_val - min_val))
                
                self._draw_fader(canvas, canvas.winfo_width(), h, new_val, min_val, max_val, secondary_color, accent_color)
                # self._transmit_command(path, new_val)

            canvas.bind("<B1-Motion>", on_drag)
            canvas.bind("<Button-1>", on_drag)
            
            # Handle Resize
            canvas.bind("<Configure>", lambda e: self._draw_fader(canvas, e.width, e.height, value_default, min_val, max_val, secondary_color, accent_color))

            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"✅ SUCCESS! The custom fader for '{label}' has been meticulously carved!",
                    **_get_log_args()
                )
            return frame
        except Exception as e:
            debug_log(message=f"💥 KABOOM! The custom fader for '{label}' melted! Error: {e}")
            return None


    def _draw_fader(self, canvas, width, height, value, min_val, max_val, track_col, handle_col):
        canvas.delete("all")
        
        # Center Line
        cx = width / 2
        
        # Track (Groove)
        canvas.create_line(cx, 10, cx, height-10, fill=track_col, width=4, capstyle=tk.ROUND)
        
        # Calculate Handle Y
        norm_val = (value - min_val) / (max_val - min_val) if max_val > min_val else 0
        # 1.0 is Top (10px), 0.0 is Bottom (height-10)
        y_pos = (height - 20) * (1 - norm_val) + 10
        
        # Handle (Fader Cap)
        # Make it look like a real fader cap
        cap_width = 20
        cap_height = 30
        canvas.create_rectangle(
            cx - cap_width/2, y_pos - cap_height/2, 
            cx + cap_width/2, y_pos + cap_height/2, 
            fill=handle_col, outline=track_col
        )
        # Little line on the cap
        canvas.create_line(cx - 8, y_pos, cx + 8, y_pos, fill=track_col, width=2)