# workers/builder/dynamic_gui_create_vu_meter.py

import tkinter as tk
from tkinter import ttk
import math
from workers.mqtt.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      
from workers.logger.logger import  debug_logger
from workers.utils.log_utils import _get_log_args 
import os

class VUMeterCreatorMixin:
    def _create_vu_meter(self, parent_frame, label, config, path):
        """Creates a VU meter widget."""
        current_function_name = "_create_vu_meter"
        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"🔬⚡️ Entering '{current_function_name}' to calibrate a VU meter for '{label}'.",
**_get_log_args()
                


            )

        frame = ttk.Frame(parent_frame)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.TOP, pady=(0, 5))

        try:
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

            def _update_vu(topic, payload): # Modified signature
                try:
                    data = orjson.loads(payload) # Parse payload
                    float_value = float(data.get("value")) # Extract value
                    
                    if float_value < min_val:
                        float_value = min_val
                    if float_value > max_val:
                        float_value = max_val
                    
                    x_pos = (float_value - min_val) / (max_val - min_val) * width
                    canvas.coords(indicator, x_pos - 2.5, 0, x_pos + 2.5, height)

                except (ValueError, TypeError, orjson.JSONDecodeError) as e: # Added JSONDecodeError
                    if app_constants.global_settings['debug_enabled']:
                        debug_logger(message=f"🔴 ERROR in _update_vu for topic {topic}: {e}", file=os.path.basename(__file__), function=current_function_name)

            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"✅ SUCCESS! The VU meter '{label}' is now registering on the Richter scale!",
                    file=os.path.basename(__file__),
                    version=app_constants.CURRENT_VERSION,
                    function=f"{self.__class__.__name__}.{current_function_name}"
                )
            
            # Subscribe to updates for this VU meter
            if self.subscriber_router:
                self.subscriber_router.subscribe_to_topic(path, _update_vu)
            
            return frame
        except Exception as e:
            debug_logger(message=f"💥 KABOOM! The VU meter for '{label}' has overloaded! Error: {e}")
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"💥 KABOOM! The VU meter for '{label}' has overloaded! Error: {e}",
                    file=os.path.basename(__file__),
                    version=app_constants.CURRENT_VERSION,
                    function=current_function_name
                )
            return None