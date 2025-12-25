# display/5_sweeping/2_configuration/gui_configuration.py
#
# A GUI frame that uses the DynamicGuiBuilder to create widgets for frequency settings.
#
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
# Version 20251222.004100.1

import os
import inspect
import tkinter as tk
from tkinter import ttk
import pathlib

# --- Module Imports ---
from workers.builder.dynamic_gui_builder import DynamicGuiBuilder
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
from workers.mqtt.setup.config_reader import Config # Import the Config class
app_constants = Config.get_instance() # Get the singleton instance

# --- Global Scope Variables ---
Current_Date = 20251222
Current_Time = 4100
Current_iteration = 1

current_version = "20251222.004100.1"
current_version_hash = (Current_Date * Current_Time * Current_iteration)
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent.parent.parent # Adjusted to reach root if needed, or use absolute
current_file = os.path.basename(__file__)
current_path = pathlib.Path(__file__).resolve()
JSON_CONFIG_FILE = current_path.with_suffix('.json')

# Define the topic filter for this specific module
#MQTT_TOPIC_FILTER = "OPEN-AIR/configuration/sweeping"

class PresetPusherGui(ttk.Frame):
    """
    A GUI Frame that hosts the DynamicGuiBuilder to generate frequency configuration controls.
    """
    def __init__(self, parent, config, **kwargs):
        """
        Initializes the PresetPusherGui.
        """
        # Initialize the superclass (ttk.Frame) with the remaining kwargs
        super().__init__(parent, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)

        self.config_data = config # Store the config for later use
        
        # --- Dynamic GUI Builder ---
        current_function_name = "__init__"
        
        if app_constants.LOCAL_DEBUG_ENABLE:
             debug_log(
                message=f"🟢️️️🟢 ➡️➡️ {current_function_name} to initialize the PresetPusherGui.",
              **_get_log_args()
                            )

        try:
            # Prepare configuration for the builder
            builder_config = {
                # "base_topic": MQTT_TOPIC_FILTER,
                "log_to_gui_console": None,
                "log_to_gui_treeview": None  # Assuming no treeview for this component
            }
            
            # Merge passed config if it exists
            if self.config_data:
                builder_config.update(self.config_data)

            self.dynamic_gui = DynamicGuiBuilder(
                parent=self,
                json_path=JSON_CONFIG_FILE,
                config=builder_config
            )
            
            
        except Exception as e:
            
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
**_get_log_args()
                    


                )

    def _on_tab_selected(self, *args, **kwargs):
        """
        Called by the grand orchestrator (Application) when this tab is brought to focus.
        Using *args to swallow any positional events or data passed by the orchestrator.
        """
        current_function_name = "_on_tab_selected"
        
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🖥️🔵 Tab '{self.__class__.__name__}' activated! Stand back, I'm checking the data flow!",**_get_log_args() )
        
        # Add logic here if specific refresh actions are needed on tab focus
        pass