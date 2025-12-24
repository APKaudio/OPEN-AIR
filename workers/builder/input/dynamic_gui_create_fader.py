# workers/builder/dynamic_gui_create_fader.py

import tkinter as tk
from tkinter import ttk
import workers.setup.app_constants as app_constants
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
import os

class FaderCreatorMixin:
    def _create_fader(self, parent_frame, label, config, path):
        """Creates a fader widget."""
        current_function_name = "_create_fader"
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🔬⚡️ Entering '{current_function_name}' to sculpt a fader for '{label}'.",
**_get_log_args()
                


            )
        
        frame = ttk.Frame(parent_frame)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.TOP, pady=(0, 5))

        try:
            orient = config.get("orientation", "vertical")
            
            scale = ttk.Scale(
                frame,
                from_=config.get("min", 0),
                to=config.get("max", 100),
                orient=orient,
                value=config.get("value_default", 0)
            )
            
            if orient == "vertical":
                scale.pack(side=tk.LEFT, fill=tk.Y, expand=True)
            else:
                scale.pack(side=tk.TOP, fill=tk.X, expand=True)

            value_label = ttk.Label(frame, text=f"{scale.get():.2f}")
            if orient == "vertical":
                value_label.pack(side=tk.BOTTOM, pady=(5,0))
            else:
                value_label.pack(side=tk.RIGHT, padx=(10,0))


            def _on_scale_move(value):
                try:
                    value_label.config(text=f"{float(value):.2f}")
                    # Here you would add logic to publish the value via MQTT
                    # self.mqtt_util.publish(path, value)
                except Exception as e:
                    if app_constants.LOCAL_DEBUG_ENABLE:
                        debug_log(message=f"🔴 ERROR in _on_scale_move: {e}", file=os.path.basename(__file__), function=current_function_name 

)

            scale.config(command=_on_scale_move)

            self.topic_widgets[path] = {
                "widget": scale,
                "value_label": value_label
            }

            def _update_fader(value):
                try:
                    float_value = float(value)
                    scale.set(float_value)
                    value_label.config(text=f"{float_value:.2f}")
                except (ValueError, TypeError) as e:
                    if app_constants.LOCAL_DEBUG_ENABLE:
                        debug_log(message=f"🔴 ERROR in _update_fader: {e}", file=os.path.basename(__file__), function=current_function_name 

)

            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"✅ SUCCESS! The fader '{label}' is now sliding into existence!",
                    file=os.path.basename(__file__),
                    version=app_constants.current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}"
                    


                )
            # self.mqtt_callbacks[path] = _update_fader
            return frame
        except Exception as e:
            debug_log(message=f"💥 KABOOM! The fader for '{label}' has gone off the rails! Error: {e}")
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"💥 KABOOM! The fader for '{label}' has gone off the rails! Error: {e}",
                    file=os.path.basename(__file__),
                    version=app_constants.current_version,
                    function=current_function_name
                    


                )
            return None