# workers/builder/dynamic_gui_create_progress_bar.py

import tkinter as tk
from tkinter import ttk
import workers.setup.app_constants as app_constants
from workers.logger.logger import debug_log
import os

class ProgressBarCreatorMixin:
    def _create_progress_bar(self, parent_frame, label, config, path):
        """Creates a progress bar widget."""
        current_function_name = "_create_progress_bar"
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🔬⚡️ Entering '{current_function_name}' to construct a progress indicator for '{label}'.",
                file=os.path.basename(__file__),
                version=app_constants.current_version, # Assuming app_constants is available
                function=f"{self.__class__.__name__}.{current_function_name}"
                


            )

        frame = ttk.Frame(parent_frame)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.LEFT, padx=(0, 10))

        try:
            min_val = config.get("min", 0)
            max_val = config.get("max", 100)
            units = config.get("units", "")
            
            progressbar = ttk.Progressbar(
                frame,
                orient="horizontal",
                length=200,
                mode="determinate",
                maximum=max_val,
                value=config.get("value_default", min_val)
            )
            progressbar.pack(side=tk.LEFT, fill=tk.X, expand=True)

            value_label = ttk.Label(frame, text=f"{progressbar['value']} {units}")
            value_label.pack(side=tk.LEFT, padx=(10, 0))

            self.topic_widgets[path] = {
                "widget": progressbar,
                "value_label": value_label,
                "units": units
            }
            
            def _update_progress(value):
                try:
                    float_value = float(value)
                    progressbar['value'] = float_value
                    value_label['text'] = f"{float_value} {units}"
                except (ValueError, TypeError) as e:
                    if app_constants.LOCAL_DEBUG_ENABLE:
                        debug_log(message=f"🔴 ERROR in _update_progress: {e}", file=os.path.basename(__file__), function=current_function_name 

)

            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"✅ SUCCESS! The progress bar '{label}' has been successfully rendered!",
                    file=os.path.basename(__file__),
                    version=app_constants.current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}"
                    


                )
            # self.mqtt_callbacks[path] = _update_progress
            return frame
        except Exception as e:
            debug_log(message=f"💥 KABOOM! The progress bar '{label}' has failed to materialize! Error: {e}")
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"💥 KABOOM! The progress bar '{label}' has failed to materialize! Error: {e}",
                    file=os.path.basename(__file__),
                    version=app_constants.current_version,
                    function=current_function_name
                    


                )
            return None