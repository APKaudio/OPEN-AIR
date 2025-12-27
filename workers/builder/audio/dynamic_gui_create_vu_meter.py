# workers/builder/dynamic_gui_create_vu_meter.py

import tkinter as tk
from tkinter import ttk
import math
from workers.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      
from workers.logger.logger import  debug_logger
from workers.utils.log_utils import _get_log_args 
import os
from workers.utils.topic_utils import get_topic

class VUMeterCreatorMixin:
    def _create_vu_meter(self, parent_frame, label, config, path, state_mirror_engine, subscriber_router):
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
            
            if path:
                self.topic_widgets[path] = {
                    "canvas": canvas,
                    "indicator": indicator,
                    "min": min_val,
                    "max": max_val,
                    "width": width
                }

                # Subscribe to updates for this VU meter
                topic = get_topic("OPEN-AIR", self.tab_name, path) # Use self.tab_name from DynamicGuiBuilder
                subscriber_router.subscribe_to_topic(topic, self._on_vu_update_mqtt)

            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"✅ SUCCESS! The VU meter '{label}' is now registering on the Richter scale!",
                    file=os.path.basename(__file__),
                    version=app_constants.CURRENT_VERSION,
                    function=f"{self.__class__.__name__}.{current_function_name}"
                )
            
            return frame
        except Exception as e:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"❌ The VU meter for '{label}' has overloaded! Error: {e}",
                    file=os.path.basename(__file__),
                    version=app_constants.CURRENT_VERSION,
                    function=current_function_name
                )
            return None
    
    def _on_vu_update_mqtt(self, topic, payload):
        import orjson
        try:
            payload_data = orjson.loads(payload) # Parse payload
            float_value = float(payload_data.get("val", 0.0)) # Extract 'val' from payload
            
            # Extract widget path from topic
            expected_prefix = f"OPEN-AIR/{self.tab_name}/" # Assuming self.tab_name is available from DynamicGuiBuilder
            if topic.startswith(expected_prefix):
                widget_path = topic[len(expected_prefix):]
            else:
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(message=f"⚠️ Unexpected topic format for VU meter update: {topic}", **_get_log_args())
                return

            widget_info = self.topic_widgets.get(widget_path)
            if widget_info:
                canvas = widget_info["canvas"]
                indicator = widget_info["indicator"]
                min_val = widget_info["min"]
                max_val = widget_info["max"]
                width = widget_info["width"]

                if float_value < min_val:
                    float_value = min_val
                if float_value > max_val:
                    float_value = max_val
                
                x_pos = (float_value - min_val) / (max_val - min_val) * width
                canvas.coords(indicator, x_pos - 2.5, 0, x_pos + 2.5, canvas.winfo_height()) # Use actual canvas height

                if app_constants.global_settings['debug_enabled']:
                    debug_logger(message=f"🎶 VU meter '{widget_path}' updated to {float_value}", **_get_log_args())
            else:
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(message=f"⚠️ VU meter widget not found for path: {widget_path}", **_get_log_args())

        except (ValueError, TypeError, orjson.JSONDecodeError) as e:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(message=f"🔴 ERROR in _on_vu_update_mqtt for topic {topic}: {e}. Payload: {payload}", **_get_log_args())