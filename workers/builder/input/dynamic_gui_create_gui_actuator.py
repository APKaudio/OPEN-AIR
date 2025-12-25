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
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
from workers.mqtt.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      
from workers.utils.topic_utils import get_topic

LOCAL_DEBUG_ENABLE = False

# --- Global Scope Variables ---
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2
TOPIC_DELIMITER = "/"


class GuiActuatorCreatorMixin:
    """
    A mixin class that provides the functionality for creating a simple
    actuator button widget that triggers an action.
    """
    def _create_gui_actuator(self, parent_frame, label, config, path):
        # Creates a button that acts as a simple actuator.
        current_function_name = inspect.currentframe().f_code.co_name
        
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
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
                # FIXED: The actuator now correctly publishes to the "actions" topic.
                action_path = path.replace("repository", "actions") + "/trigger"

                if app_constants.LOCAL_DEBUG_ENABLE: 
                    debug_log(
                        message=f"GUI ACTION: Activating actuator '{label}' to path '{action_path}'",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}"
                    )
                self._transmit_command(widget_name=action_path, value=True)

            def on_release(event):
                # FIXED: The actuator now correctly publishes to the "actions" topic.
                action_path = path.replace("repository", "actions") + "/trigger"

                if app_constants.LOCAL_DEBUG_ENABLE: 
                    debug_log(
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

            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"✅ SUCCESS! The actuator '{label}' is ready for action!",
                    **_get_log_args()
                )
            return sub_frame

        except Exception as e:
            
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"💥 KABOOM! The actuator '{label}' has short-circuited! Error: {e}",
                    file=current_file,
                    version=current_version,
                    function=current_function_name
                )
            return None