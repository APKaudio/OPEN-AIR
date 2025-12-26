## MQTT_TOPIC_FILTER = "OPEN-AIR/configuration/application/Application_Info"










# display/left_50/top_100/tab_1_instrument/sub_tab_2_settings/sub_tab_1_frequency/gui_frequency_1.py
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
#
# Version 20251127.000000.1

import os
import inspect
import tkinter as tk
from tkinter import ttk

# --- Module Imports ---
from workers.builder.dynamic_gui_builder import DynamicGuiBuilder
from workers.logger.logger import  debug_logger
from workers.utils.log_utils import _get_log_args 
import pathlib

# --- Global Scope Variables ---
current_version = "20251226.000000.1"
current_version_hash = (20251127 * 0 * 1)
current_file = f"{os.path.basename(__file__)}"
current_path = pathlib.Path(__file__).resolve()
JSON_CONFIG_FILE = current_path.with_suffix('.json')


class PresetPusherGui(ttk.Frame):
    """
    A container frame that instantiates the DynamicGuiBuilder for the Frequency configuration.
    """
    def __init__(self, parent, *args, **kwargs):
        """
        Initializes the Frequency frame and the dynamic GUI builder.
        """
        config = kwargs.pop('config', {}) # Pop config dict from kwargs
        self.config_data = config # Store the full config for later use, including MQTT components
        super().__init__(parent, *args, **kwargs)
        
        self.state_mirror_engine = self.config_data.get('state_mirror_engine')
        self.subscriber_router = self.config_data.get('subscriber_router')
        
        # --- Dynamic GUI Builder ---
        current_function_name = "__init__"
        debug_logger(
            message=f"🟢️️️🟢 ➡️➡️ {current_function_name} to initialize the PresetPusherGui.",
**_get_log_args()
        )
        try:
            self.dynamic_gui = DynamicGuiBuilder(
                parent=self,
                json_path=JSON_CONFIG_FILE,
                config=self.config_data # Pass the full config dictionary
            )
            debug_logger(
                message="✅ The PresetPusherGui did initialize its dynamic GUI builder.",
              **_get_log_args()
            )
        except Exception as e:
            debug_logger(
                message=f"❌ Error in {current_function_name}: {e}",
              **_get_log_args()
            )
            debug_logger(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
              **_get_log_args()
            )