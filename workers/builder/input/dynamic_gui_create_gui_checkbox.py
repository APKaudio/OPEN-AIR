# workers/builder/dynamic_gui_create_gui_checkbox.py
#
# This file (dynamic_gui_create_gui_checkbox.py) provides the GuiCheckboxCreatorMixin class for creating checkbox widgets in the GUI.
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251213  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 44 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#


import os
import tkinter as tk
from tkinter import ttk
import inspect
import orjson

# --- Module Imports ---
from workers.logger.logger import  debug_logger
from workers.utils.log_utils import _get_log_args 
from workers.mqtt.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      

# The wrapper functions debug_log and _switch are removed
# as the core debug_log and  now directly handle LOCAL_DEBUG_ENABLE.


# --- Global Scope Variables ---
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2

class GuiCheckboxCreatorMixin:
    """
    A mixin class that provides the functionality for creating a
    checkbox widget.
    """
    def _create_gui_checkbox(self, parent_frame, label, config, path):
        # Creates a checkbox widget.
        current_function_name = inspect.currentframe().f_code.co_name

        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"🔬⚡️ Entering '{current_function_name}' to spawn a checkbox for '{label}'.",
              **_get_log_args()
                


            )
        
        try:
            sub_frame = ttk.Frame(parent_frame)
            # We use a BooleanVar to track the state of the checkbox.
            initial_value = bool(config.get('value', False))
            state_var = tk.BooleanVar(value=initial_value)

            def get_label_text():
                current_state = state_var.get()
                # Use label_active/label_inactive if they exist, otherwise fall back to the main label.
                if current_state:
                    return config.get('label_active', config.get('label', ''))
                else:
                    return config.get('label_inactive', config.get('label', ''))
            
            def update_label():
                # Manually update the checkbox text
                checkbox.config(text=get_label_text())

            def toggle_and_publish():
                # Flips the state and publishes the change via MQTT.
                new_state = state_var.get()
                # Pass raw boolean instead of JSON string
                payload = new_state
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(
                        message=f"GUI ACTION: Publishing state change for '{label}' to path '{path}' with value '{new_state}'.",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}"
                        


                    )
                self._transmit_command(widget_name=path, value=payload)
                # Update the label after the state change
                update_label()

            # Create the checkbox button with an initial label.
            checkbox = ttk.Checkbutton(
                sub_frame,
                text=get_label_text(),
                variable=state_var,
                command=toggle_and_publish
            )
            checkbox.pack(side=tk.LEFT, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
            
            # Store the widget and its state variable for external updates.
            if path and self.state_mirror_engine:
                self.state_mirror_engine.register_widget(path, state_var, self.tab_name)
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(
                        message=f"🔬 Widget '{label}' ({path}) registered with StateMirrorEngine (BooleanVar: {state_var.get()}).",
                        **_get_log_args()
                    )


            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"✅ SUCCESS! The checkbox '{label}' has been successfully instantiated.",
**_get_log_args()
                    


                )
            return sub_frame

        except Exception as e:
            (f"❌ Error in {current_function_name} for '{label}': {e}")
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"💥 KABOOM! The checkbox for '{label}' suffered a quantum entanglement failure! Error: {e}",
**_get_log_args()
                    


                )
            return None