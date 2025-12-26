# workers/builder/dynamic_gui_create_custom_fader.py
#
# A vertical fader widget that adapts to the system theme.
# Version 20251223.214500.ThemeFix

import tkinter as tk
from tkinter import ttk
import math
from workers.mqtt.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      
from workers.logger.logger import  debug_logger
from workers.utils.log_utils import _get_log_args 
from workers.styling.style import THEMES, DEFAULT_THEME
import os

class CustomFaderCreatorMixin:
    def _create_custom_fader(self, parent_frame, label, config, path):
        """Creates a custom fader widget."""
        current_function_name = "_create_custom_fader"
        if app_constants.global_settings['debug_enabled']:
            debug_logger(
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
            width = config.get("width", 60)
            height = config.get("height", 200)
            min_val = config.get("min", 0)
            max_val = config.get("max", 100)
            value_default = float(config.get("value_default", 75)) # Ensure float

            fader_value_var = tk.DoubleVar(value=value_default)

            # Force canvas to match theme background so it blends in
            canvas = tk.Canvas(frame, width=width, height=height, bg=bg_color, highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True)

            def update_fader_visuals(*args):
                current_fader_val = fader_value_var.get()
                self._draw_fader(canvas, canvas.winfo_width(), canvas.winfo_height(), 
                                 current_fader_val, min_val, max_val, secondary_color, accent_color)
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(
                        message=f"⚡ fluxing... Custom Fader '{label}' updated visually to {current_fader_val} from MQTT.",
                        **_get_log_args()
                    )

            fader_value_var.trace_add("write", update_fader_visuals)
            
            # Initial draw based on default value
            update_fader_visuals()

            # Interaction
            def on_drag(event):
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(
                        message=f"➡️ Custom Fader '{label}' on_drag event triggered (y={event.y}).",
                        **_get_log_args()
                    )
                # Map Y position to Value
                h = canvas.winfo_height()
                y = max(10, min(h-10, event.y))
                norm = 1 - ((y - 10) / (h - 20)) # 0.0 to 1.0
                new_val = min_val + (norm * (max_val - min_val))
                
                # Update the StringVar, which will trigger the trace for visual update
                if fader_value_var.get() != new_val: # Only update if value changed to prevent unnecessary MQTT messages
                    fader_value_var.set(new_val)
                    self._transmit_command(widget_name=path, value=new_val)

            canvas.bind("<B1-Motion>", on_drag)
            canvas.bind("<Button-1>", on_drag)
            
            # Handle Resize
            canvas.bind("<Configure>", lambda e: update_fader_visuals()) # Redraw on resize

            # Register the StringVar with the StateMirrorEngine for MQTT updates
            if path and self.state_mirror_engine:
                self.state_mirror_engine.register_widget(path, fader_value_var, self.tab_name)
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(
                        message=f"🔬 Widget '{label}' ({path}) registered with StateMirrorEngine (DoubleVar: {fader_value_var.get()}).",
                        **_get_log_args()
                    )

            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"✅ SUCCESS! The custom fader for '{label}' has been meticulously carved!",
                    **_get_log_args()
                )
            return frame
        except Exception as e:
            debug_logger(message=f"💥 KABOOM! The custom fader for '{label}' melted! Error: {e}")
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
        cap_width = width * 0.7 # Make cap width 70% of the canvas width
        cap_height = 30
        canvas.create_rectangle(
            cx - cap_width/2, y_pos - cap_height/2, 
            cx + cap_width/2, y_pos + cap_height/2, 
            fill=handle_col, outline=track_col
        )
        # Main center line on the cap
        line_length_half = cap_width * 0.4 # Roughly 80% of current cap_width
        canvas.create_line(cx - line_length_half, y_pos, cx + line_length_half, y_pos, fill=track_col, width=2)

        # Additional smaller lines above and below
        small_line_length_half = line_length_half * 0.6 # 60% of the main line's half length
        line_offset = 6 # Vertical offset for the small lines

        canvas.create_line(cx - small_line_length_half, y_pos - line_offset, cx + small_line_length_half, y_pos - line_offset, fill=track_col, width=1)
        canvas.create_line(cx - small_line_length_half, y_pos + line_offset, cx + small_line_length_half, y_pos + line_offset, fill=track_col, width=1)