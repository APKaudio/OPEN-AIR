# workers/builder/dynamic_gui_create_knob.py

import tkinter as tk
from tkinter import ttk
import math
import workers.setup.app_constants as app_constants
from workers.logger.logger import debug_log
import os

class KnobCreatorMixin:
    def _create_knob(self, parent_frame, label, config, path):
        """Creates a knob widget."""
        current_function_name = "_create_knob"
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🔬⚡️ Entering '{current_function_name}' to dial in a knob for '{label}'.",
                file=os.path.basename(__file__),
                version=app_constants.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}"
                


            )

        frame = ttk.Frame(parent_frame)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.TOP, pady=(0, 5))

        try:
            size = config.get("size", 100)
            min_val = config.get("min", 0)
            max_val = config.get("max", 100)
            value_default = config.get("value_default", 50)

            canvas = tk.Canvas(frame, width=size, height=size)
            canvas.pack()

            self._draw_knob(canvas, size, value_default, min_val, max_val)

            value_label = ttk.Label(frame, text=f"{value_default}")
            value_label.pack()

            def _on_drag(event):
                try:
                    # Simple angle calculation
                    angle = math.atan2(event.y - size / 2, event.x - size / 2) + math.pi / 2
                    if angle < 0:
                        angle += 2 * math.pi
                    
                    # Map angle to value
                    value = (angle / (2 * math.pi)) * (max_val - min_val) + min_val
                    
                    self._draw_knob(canvas, size, value, min_val, max_val)
                    value_label.config(text=f"{int(value)}")
                    # MQTT publish logic would go here
                except Exception as e:
                    if app_constants.LOCAL_DEBUG_ENABLE:
                        debug_log(message=f"🔴 ERROR in _on_drag: {e}", file=os.path.basename(__file__), function=current_function_name 

)

                
            canvas.bind("<B1-Motion>", _on_drag)

            self.topic_widgets[path] = {
                "widget": canvas,
                "value_label": value_label,
                "size": size,
                "min": min_val,
                "max": max_val
            }

            def _update_knob(value):
                try:
                    float_value = float(value)
                    self._draw_knob(canvas, size, float_value, min_val, max_val)
                    value_label.config(text=f"{int(float_value)}")
                except (ValueError, TypeError) as e:
                    if app_constants.LOCAL_DEBUG_ENABLE:
                        debug_log(message=f"🔴 ERROR in _update_knob: {e}", file=os.path.basename(__file__), function=current_function_name 

)

            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"✅ SUCCESS! The knob '{label}' has been finely tuned and created!",
                    file=os.path.basename(__file__),
                    version=app_constants.current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}"
                    


                )
            # self.mqtt_callbacks[path] = _update_knob
            return frame
        except Exception as e:
            debug_log(message=f"💥 KABOOM! The knob for '{label}' has stripped its gears! Error: {e}")
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"💥 KABOOM! The knob for '{label}' has stripped its gears! Error: {e}",
                    file=os.path.basename(__file__),
                    version=app_constants.current_version,
                    function=current_function_name
                    


                )
            return None


    def _draw_knob(self, canvas, size, value, min_val, max_val):
        canvas.delete("all")
        # Outer circle
        canvas.create_oval(5, 5, size - 5, size - 5, outline="gray", width=4)
        
        # Indicator
        angle = ((value - min_val) / (max_val - min_val)) * 2 * math.pi - math.pi / 2
        x = size / 2 + (size / 2 - 10) * math.cos(angle)
        y = size / 2 + (size / 2 - 10) * math.sin(angle)
        canvas.create_line(size / 2, size / 2, x, y, width=4, fill="blue")