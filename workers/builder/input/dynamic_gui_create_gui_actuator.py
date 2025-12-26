# workers/builder/dynamic_gui_create_gui_actuator.py
#
# This file (dynamic_gui_create_gui_actuator.py) provides the GuiActuatorCreatorMixin class for creating simple actuator buttons in the GUI.
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
from workers.mqtt.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      
from workers.utils.topic_utils import get_topic
# --- Constants ---
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2
TOPIC_DELIMITER = "/"


class GuiActuatorCreatorMixin:
    """
    A mixin class that provides the functionality for creating a simple
    actuator button widget that triggers an action.
    """
    def _create_gui_actuator(self, parent_frame, label, config, path, state_mirror_engine, subscriber_router):
        # Creates a button that acts as a simple actuator.
        current_function_name = inspect.currentframe().f_code.co_name
        
        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"🔬⚡️ Entering '{current_function_name}' to construct an actuator for '{label}'.",
              **_get_log_args()
            )

        try:
            # Create a frame to hold the label and button
            sub_frame = ttk.Frame(parent_frame)

            button_text = config.get('label', config.get('label_active', config.get('label_inactive', label)))

            button = ttk.Button(
                sub_frame,
                text=button_text,
                style='Custom.TButton' 
            )
            button.pack(side=tk.LEFT, padx=DEFAULT_PAD_X)

            def on_press(event):
                action_path = f"{path}/trigger"
                
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(
                        message=f"GUI ACTION: Activating actuator '{label}' to path '{action_path}'",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}"
                    )
                self._transmit_command(widget_name=action_path, value=True)

            def on_release(event):
                action_path = f"{path}/trigger"

                if app_constants.global_settings['debug_enabled']:
                    debug_logger(
                        message=f"GUI ACTION: Deactivating actuator '{label}' to path '{action_path}'",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}"
                    )
                self._transmit_command(widget_name=action_path, value=False)

            button.bind("<ButtonPress-1>", on_press)
            button.bind("<ButtonRelease-1>", on_release)

            if path:
                self.topic_widgets[path] = button
                
                # --- New MQTT Wiring ---
                widget_id = path
                
                # 1. This widget is stateless and directly transmits commands,
                #    so no StringVar to register.

                # 2. No variable trace for outgoing messages, as it's a direct command.

                # 3. Subscribe to topic for incoming messages (to activate/deactivate button)
                #    The topic for status is usually 'path/active' or 'path/label_active'
                status_topic = f"{get_topic('OPEN-AIR', self.tab_name, widget_id)}/active"
                subscriber_router.subscribe_to_topic(status_topic, self._on_actuator_state_update)

            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"✅ SUCCESS! The actuator '{label}' is ready for action!",
                    **_get_log_args()
                )
            return sub_frame

        except Exception as e:
            
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"💥 KABOOM! The actuator '{label}' has short-circuited! Error: {e}",
                    file=current_file,
                    version=current_version,
                    function=current_function_name
                )
            return None

    def _on_actuator_state_update(self, topic, payload):
        import orjson
        try:
            payload_data = orjson.loads(payload)
            is_active = payload_data.get('val')
            
            # Derive widget_id from topic
            # Example topic: "OPEN-AIR/TAB_NAME/WIDGET_ID/active"
            # We need "TAB_NAME/WIDGET_ID"
            parts = topic.split(TOPIC_DELIMITER)
            # Assuming 'OPEN-AIR' is parts[0] and 'active' is parts[-1]
            # The actual widget_id path starts after 'OPEN-AIR' and ends before '/active'
            widget_path_parts = parts[1:-1] # Exclude 'OPEN-AIR' and 'active'
            widget_id_from_topic = TOPIC_DELIMITER.join(widget_path_parts)
            
            # The path stored in self.topic_widgets is typically relative to the base,
            # so it usually doesn't include "OPEN-AIR/TAB_NAME".
            # We need to match the key used when setting self.topic_widgets[path] = button.
            # If path was "tab_name/widget_id", then we need "tab_name/widget_id".
            # If path was just "widget_id" (meaning tab_name was empty or not included in path_prefix),
            # then we need to extract only the widget_id part.
            
            # Let's assume path is "tab_name/widget_id" or "widget_id"
            # The `widget_id` passed to register_widget was `path`
            # and `status_topic` was derived from `get_topic('OPEN-AIR', self.tab_name, widget_id)` + "/active"
            # so the topic would be OPEN-AIR/<self.tab_name>/<path>/active
            # we need <path>
            
            # Simplified extraction for the path used as key in self.topic_widgets
            # This relies on the fact that `get_topic` uses self.tab_name and widget_id (which is `path`)
            # so `topic` is essentially `OPEN-AIR/{self.tab_name}/{path}/active`
            expected_prefix = f"OPEN-AIR{TOPIC_DELIMITER}{self.tab_name}{TOPIC_DELIMITER}"
            if topic.startswith(expected_prefix):
                key_in_topic_widgets = topic[len(expected_prefix):].replace(f"{TOPIC_DELIMITER}active", "")
            else:
                # Fallback if topic structure is different or tab_name is empty
                # This needs to be robust. The `widget_id` argument to `get_topic` was `path`.
                # So we need to reverse get_topic effectively.
                # get_topic("OPEN-AIR", self.tab_name, widget_id) -> "OPEN-AIR/TAB/WIDGET"
                # so the incoming topic is "OPEN-AIR/TAB/WIDGET/active"
                # We need to find "WIDGET"
                
                # Try to find the original path (widget_id) from the topic
                # Assuming `path` is what we need to match in `self.topic_widgets`
                # A better way might be to store the button object by full topic.
                # For now, let's try to reconstruct the key.
                
                # This assumes 'active' is always at the end.
                topic_without_active = topic.rsplit(TOPIC_DELIMITER, 1)[0]
                
                # And remove the 'OPEN-AIR/TAB_NAME/' prefix if it exists, otherwise just use the rest
                if topic_without_active.startswith(f"OPEN-AIR{TOPIC_DELIMITER}"):
                    key_in_topic_widgets = topic_without_active.replace(f"OPEN-AIR{TOPIC_DELIMITER}", "", 1)
                else:
                    key_in_topic_widgets = topic_without_active # As a last resort

            button = self.topic_widgets.get(key_in_topic_widgets)
            if button:
                if is_active:
                    button.config(style='Custom.Selected.TButton')
                else:
                    button.config(style='Custom.TButton')
                
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(message=f"GUI ACTUATOR: Actuator '{key_in_topic_widgets}' state updated to {is_active}", **_get_log_args())
            else:
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(message=f"GUI ACTUATOR: Button widget not found in topic_widgets for key: {key_in_topic_widgets} (from topic: {topic})", **_get_log_args())

        except (orjson.JSONDecodeError, AttributeError) as e:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(message=f"❌ Error processing actuator MQTT update for {topic}: {e}. Payload: {payload}", **_get_log_args())