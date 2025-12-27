# workers/builder/dynamic_gui_create_text_input.py

import tkinter as tk
from tkinter import ttk
from workers.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      
from workers.logger.logger import  debug_logger
from workers.utils.log_utils import _get_log_args 
import os

class TextInputCreatorMixin:
    def _create_text_input(self, parent_frame, label, config, path, state_mirror_engine, subscriber_router):
        """Creates a text input widget."""
        current_function_name = "_create_text_input"
        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"🔬⚡️ Entering '{current_function_name}' to forge a text input field for '{label}'.",
**_get_log_args()
                


            )

        frame = ttk.Frame(parent_frame)

        if label:
            ttk.Label(frame, text=label).pack(side=tk.LEFT, padx=(0, 10))

        try:
            text_var = tk.StringVar()
            text_var.set(config.get("value_default", ""))
            
            entry = ttk.Entry(
                frame,
                textvariable=text_var
            )
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

            def _on_text_change(*args):
                try:
                    if app_constants.global_settings['debug_enabled']:
                        debug_logger(message=f"Text changed for {label}: {text_var.get()}", file=os.path.basename(__file__), function="_on_text_change")
                    state_mirror_engine.broadcast_gui_change_to_mqtt(path)
                except Exception as e:
                    if app_constants.global_settings['debug_enabled']:
                        debug_logger(message=f"🔴 ERROR in _on_text_change: {e}", file=os.path.basename(__file__), function="_on_text_change")

            text_var.trace_add("write", _on_text_change) # Use trace_add for consistency

            if path:
                state_mirror_engine.register_widget(path, text_var, self.tab_name)
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(
                        message=f"🔬 Widget '{label}' ({path}) registered with StateMirrorEngine (StringVar: {text_var.get()}).",
                        **_get_log_args()
                    )
                # Broadcast initial state
                state_mirror_engine.broadcast_gui_change_to_mqtt(path)
            
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"✅ SUCCESS! The text input '{label}' has been successfully forged!",
                    file=os.path.basename(__file__),
                    version=app_constants.CURRENT_VERSION,
                    function=f"{self.__class__.__name__}.{current_function_name}"
                    


                )
            return frame
        except Exception as e:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"❌ The text input '{label}' has disintegrated! Error: {e}",
                    file=os.path.basename(__file__),
                    version=app_constants.CURRENT_VERSION,
                    function=current_function_name
                )
            return None