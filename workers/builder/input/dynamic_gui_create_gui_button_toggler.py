# workers/builder/dynamic_gui_create_gui_button_toggler.py
#
# This file (dynamic_gui_create_gui_button_toggler.py) provides the GuiButtonTogglerCreatorMixin class for creating groups of radio-style buttons in the GUI.
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

# --- Module Imports ---
from workers.logger.logger import  debug_logger
from workers.utils.log_utils import _get_log_args 
from workers.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      
from workers.handlers.widget_event_binder import bind_variable_trace
from workers.utils.topic_utils import get_topic

# --- Global Scope Variables ---
current_file = f"{os.path.basename(__file__)}"
# --- Constants ---
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2

class GuiButtonTogglerCreatorMixin:
    """
    A mixin class that provides the functionality for creating a
    group of buttons that behave like radio buttons.
    """
    def _create_gui_button_toggler(self, parent_frame, label, config, path, base_mqtt_topic_from_path, state_mirror_engine, subscriber_router):
        # Creates a set of custom buttons that behave like radio buttons ("bucket of buttons").
        current_function_name = inspect.currentframe().f_code.co_name

        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"🔬⚡️ Entering '{current_function_name}' to assemble a bucket of buttons for '{label}'.",
              **_get_log_args()
            )

        try:
            group_frame = ttk.Frame(parent_frame)

            label_widget = ttk.Label(group_frame, text=label)
            label_widget.pack(anchor='w', padx=DEFAULT_PAD_X, pady=2)

            button_container = ttk.Frame(group_frame)
            button_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

            options_data = config.get('options', {})
            # Ensure options_data is a dictionary
            if isinstance(options_data, list):
                debug_logger(message=f"⚠️ WARNING: 'options' for '{label}' in config is a list, expected a dictionary. Falling back to empty dict.", **_get_log_args())
                options_data = {} # Fallback to empty dict to prevent crash
            
            buttons = {}

            selected_key = next((key for key, opt in options_data.items() if str(opt.get('selected', 'no')).lower() in ['yes', 'true']), None)
            selected_var = tk.StringVar(value=selected_key)

            def update_button_styles(*args):
                current_selection = selected_var.get()
                for key, button_widget in buttons.items():
                    option_data = options_data.get(key, {})
                    
                    # Determine the text and style for the button based on its state
                    if key == current_selection:
                        # Correct logic: The selected button uses the 'Selected' style.
                        button_text = option_data.get('label_active', option_data.get('label', ''))
                        button_widget.config(style='Custom.Selected.TButton')
                    else:
                        # All other buttons use the default 'TButton' style.
                        button_text = option_data.get('label_inactive', option_data.get('label', ''))
                        button_widget.config(style='Custom.TogglerUnselected.TButton')

                    # Add value and units on separate lines if they exist
                    value = option_data.get('value')
                    units = option_data.get('units')
                    if value is not None:
                        button_text += f"\n{value}"
                    if units is not None:
                        button_text += f"\n{units}"
                    
                    button_widget.config(text=button_text)

            def create_command(key):
                def command():
                    selected_var.set(key)
                return command

            max_cols = 5
            row_num = 0
            col_num = 0

            for option_key, option_data in options_data.items():
                button = ttk.Button(
                    button_container,
                    command=create_command(option_key)
                )
                button.grid(row=row_num, column=col_num, padx=2, pady=2, sticky="ew")
                button_container.grid_columnconfigure(col_num, weight=1)
                buttons[option_key] = button

                col_num += 1
                if col_num >= max_cols:
                    col_num = 0
                    row_num += 1

            update_button_styles()

            if path:
                self.topic_widgets[path] = (selected_var, update_button_styles)
                
                # --- New MQTT Wiring ---
                widget_id = path
                
                # 1. Register widget
                state_mirror_engine.register_widget(widget_id, selected_var, base_mqtt_topic_from_path, config)

                # 2. Bind variable trace for outgoing messages
                callback = lambda: state_mirror_engine.broadcast_gui_change_to_mqtt(widget_id)
                bind_variable_trace(selected_var, callback)

                # 3. Also trace changes to update the button state
                selected_var.trace_add("write", update_button_styles)

                # 4. Subscribe to topic for incoming messages
                topic = get_topic("OPEN-AIR", base_mqtt_topic_from_path, widget_id)
                subscriber_router.subscribe_to_topic(topic, state_mirror_engine.sync_incoming_mqtt_to_gui)

                # 5. Broadcast initial state
                state_mirror_engine.broadcast_gui_change_to_mqtt(widget_id)


            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"✅ SUCCESS! The button toggler '{label}' is fully operational!",
                    **_get_log_args()
                )
            return group_frame

        except Exception as e:
            debug_logger(message=f"❌ Error in {current_function_name} for '{label}': {e}")
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"💥 KABOOM! The button toggler '{label}' has suffered a catastrophic failure! Error: {e}",
                    **_get_log_args()
                )
            return None
