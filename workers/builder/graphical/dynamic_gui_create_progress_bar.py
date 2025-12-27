# workers/builder/dynamic_gui_create_progress_bar.py

import tkinter as tk
from tkinter import ttk
from workers.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      
from workers.logger.logger import  debug_logger
from workers.utils.log_utils import _get_log_args
from workers.utils.topic_utils import get_topic
import os
class ProgressBarCreatorMixin:
    def _create_progress_bar(self, parent_frame, label, config, path, state_mirror_engine, subscriber_router):
        """Creates a progress bar widget."""
        current_function_name = "_create_progress_bar"
        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"🔬⚡️ Entering '{current_function_name}' to construct a progress indicator for '{label}'.",
                file=os.path.basename(__file__),
                version=app_constants.CURRENT_VERSION, # Assuming app_constants is available
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

            def _update_progress(value):
                try:
                    float_value = float(value)
                    progressbar['value'] = float_value
                    value_label['text'] = f"{float_value} {units}"
                except (ValueError, TypeError) as e:
                    if app_constants.global_settings['debug_enabled']:
                        debug_logger(message=f"❌ ERROR in _update_progress: {e}", file=os.path.basename(__file__), function=current_function_name)

            if path:
                self.topic_widgets[path] = _update_progress # Store the update callable

                # --- MQTT Subscription for incoming updates ---
                topic = get_topic("OPEN-AIR", self.tab_name, path) # Use self.tab_name from DynamicGuiBuilder
                subscriber_router.subscribe_to_topic(topic, self._on_progress_update_mqtt)

            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"✅ SUCCESS! The progress bar '{label}' has been successfully rendered!",
                    file=os.path.basename(__file__),
                    version=app_constants.CURRENT_VERSION,
                    function=f"{self.__class__.__name__}.{current_function_name}"
                )
            return frame
        except Exception as e:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"❌ The progress bar '{label}' has failed to materialize! Error: {e}",
                    file=os.path.basename(__file__),
                    version=app_constants.CURRENT_VERSION,
                    function=current_function_name
                )
            return None

    def _on_progress_update_mqtt(self, topic, payload):
        import orjson # Imported here to avoid circular dependency or top-level import issues
        try:
            payload_data = orjson.loads(payload)
            value = payload_data.get('val')
            
            # Extract widget path from topic
            # topic is "OPEN-AIR/<tab_name>/<path>"
            expected_prefix = f"OPEN-AIR/{self.tab_name}/" # Assuming self.tab_name is available from DynamicGuiBuilder
            if topic.startswith(expected_prefix):
                widget_path = topic[len(expected_prefix):]
            else:
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(message=f"⚠️ Unexpected topic format for progress bar update: {topic}", **_get_log_args())
                return
            
            update_func = self.topic_widgets.get(widget_path)
            if update_func:
                update_func(value)
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(message=f"📊 Progress bar '{widget_path}' updated to {value}", **_get_log_args())
            else:
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(message=f"⚠️ Progress bar update function not found for path: {widget_path}", **_get_log_args())

        except (orjson.JSONDecodeError, AttributeError) as e:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(message=f"❌ Error processing progress bar MQTT update for {topic}: {e}. Payload: {payload}", **_get_log_args())