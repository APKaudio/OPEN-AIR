# workers/builder/dynamic_gui_create_knob.py
#
# A Tkinter Canvas-based Rotary Knob that respects the global theme.
# Version 20251223.214500.ThemeFix

import tkinter as tk
from tkinter import ttk
import math
from workers.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      
from workers.logger.logger import  debug_logger
from workers.utils.log_utils import _get_log_args 
from workers.styling.style import THEMES, DEFAULT_THEME
import os

class KnobCreatorMixin:
    def _create_knob(self, parent_frame, label, config, path, base_mqtt_topic_from_path, state_mirror_engine, subscriber_router):
        """Creates a rotary knob widget."""
        current_function_name = "_create_knob"
        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"🔬⚡️ Entering '{current_function_name}' to forge a themed knob for '{label}'.",
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
            min_val = config.get("min", 0)
            max_val = config.get("max", 100)
            value_default = float(config.get("value_default", 0)) # Ensure float

            knob_value_var = tk.DoubleVar(value=value_default)

            # Canvas with Theme Background
            canvas = tk.Canvas(frame, width=width, height=height, bg=bg_color, highlightthickness=0)
            canvas.pack()

            # Value Label (initially based on default value var)
            value_label = ttk.Label(frame, text=f"{int(knob_value_var.get())}", font=("Helvetica", 8))
            value_label.pack(side=tk.BOTTOM)

            def update_knob_visuals(*args):
                current_knob_val = knob_value_var.get()
                value_label.config(text=f"{int(current_knob_val)}")
                self._draw_knob(canvas, width, height, current_knob_val, min_val, max_val, fg_color, accent_color, secondary_color)
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(
                        message=f"⚡ fluxing... Knob '{label}' updated visually to {current_knob_val} from MQTT.",
                        **_get_log_args()
                    )

            knob_value_var.trace_add("write", update_knob_visuals)
            
            # Initial draw based on default value
            update_knob_visuals()

            # Drag Interaction
            def on_drag(event):
                delta = 0
                if hasattr(self, '_last_drag_y_knob'): # Use a unique name to avoid conflicts
                    delta = self._last_drag_y_knob - event.y
                self._last_drag_y_knob = event.y
                
                new_val = knob_value_var.get() + (delta * (max_val - min_val) / 100)
                new_val = max(min_val, min(max_val, new_val))
                
                # Update the StringVar, which will trigger the trace for visual update
                if knob_value_var.get() != new_val: # Only update if value changed to prevent unnecessary MQTT messages
                    knob_value_var.set(new_val)
                    state_mirror_engine.broadcast_gui_change_to_mqtt(path) # Use state_mirror_engine directly

            def on_click(event):
                self._last_drag_y_knob = event.y # Initialize drag start position

            canvas.bind("<Button-1>", on_click)
            canvas.bind("<B1-Motion>", on_drag)

            # Register the StringVar with the StateMirrorEngine for MQTT updates
            if path:
                state_mirror_engine.register_widget(path, knob_value_var, base_mqtt_topic_from_path, config)
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(
                        message=f"🔬 Widget '{label}' ({path}) registered with StateMirrorEngine (DoubleVar: {knob_value_var.get()}).",
                        **_get_log_args()
                    )
                # Broadcast initial state
                state_mirror_engine.broadcast_gui_change_to_mqtt(path)

            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"✅ SUCCESS! The themed knob '{label}' is calibrated!",
                    **_get_log_args()
                )
            return frame

        except Exception as e:
            debug_logger(message=f"❌ The knob '{label}' shattered! Error: {e}")
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