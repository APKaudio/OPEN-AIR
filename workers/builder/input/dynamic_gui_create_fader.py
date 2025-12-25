# workers/builder/dynamic_gui_create_fader.py

import tkinter as tk
from tkinter import ttk
from workers.mqtt.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      
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
            value_default = float(config.get("value_default", 0)) # Ensure float
            fader_value_var = tk.DoubleVar(value=value_default)

            scale = ttk.Scale(
                frame,
                from_=config.get("min", 0),
                to=config.get("max", 100),
                orient=orient,
                variable=fader_value_var # Bind the StringVar to the scale
            )
            
            if orient == "vertical":
                scale.pack(side=tk.LEFT, fill=tk.Y, expand=True)
            else:
                scale.pack(side=tk.TOP, fill=tk.X, expand=True)

            value_label = ttk.Label(frame, text=f"{fader_value_var.get():.2f}")
            if orient == "vertical":
                value_label.pack(side=tk.BOTTOM, pady=(5,0))
            else:
                value_label.pack(side=tk.RIGHT, padx=(10,0))

            def update_fader_visuals(*args):
                current_fader_val = fader_value_var.get()
                value_label.config(text=f"{current_fader_val:.2f}")
                if app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                        message=f"⚡ fluxing... Fader '{label}' updated visually to {current_fader_val} from MQTT.",
                        **_get_log_args()
                    )
            fader_value_var.trace_add("write", update_fader_visuals)
            
            # Initial update of the label
            update_fader_visuals()

            def _on_scale_change(*args):
                # This is triggered by user interaction AND tk_var.set
                # Only publish if it's a user interaction (not an MQTT sync)
                # The _silent_update flag in StateMirrorEngine handles the suppression
                
                # Publish the value via MQTT
                self._transmit_command(widget_name=path, value=fader_value_var.get())

            scale.config(command=_on_scale_change) # Bind command to the trace

            if path and self.state_mirror_engine:
                # Register the StringVar with the StateMirrorEngine for MQTT updates
                self.state_mirror_engine.register_widget(path, fader_value_var, self.tab_name)
                if app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                        message=f"🔬 Widget '{label}' ({path}) registered with StateMirrorEngine (DoubleVar: {fader_value_var.get()}).",
                        **_get_log_args()
                    )

            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"✅ SUCCESS! The fader '{label}' is now sliding into existence!",
                    **_get_log_args()
                )
            return frame
        except Exception as e:
            debug_log(message=f"💥 KABOOM! The fader for '{label}' has gone off the rails! Error: {e}")
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"💥 KABOOM! The fader for '{label}' has gone off the rails! Error: {e}",
                    file=os.path.basename(__file__),
                    version=app_constants.CURRENT_VERSION,
                    function=current_function_name
                    


                )
            return None