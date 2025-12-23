## MQTT_TOPIC_FILTER = "OPEN-AIR/configuration/application/filepaths"
# display/tabs/gui_child_1_pusher.py
#
# A GUI frame for displaying and controlling Presets via MQTT using the modular DynamicGuiBuilder.
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
import tkinter as tk
from tkinter import ttk

# --- Module Imports ---
# It's crucial that this path correctly points to the new modular builder
from workers.builder.dynamic_gui_builder import DynamicGuiBuilder
import pathlib

# --- Global Scope Variables ---
current_version = "20251127.000000.1"
current_version_hash = (20251127 * 0 * 1)
current_file = f"{os.path.basename(__file__)}"
current_path = pathlib.Path(__file__).resolve()
JSON_CONFIG_FILE = current_path.with_suffix('.json')




class PresetPusherGui(ttk.Frame):
    """
    A container frame that instantiates the DynamicGuiBuilder for the Presets configuration.
    This replaces the old, monolithic code with a call to the reusable, modular component.
    """
    def __init__(self, parent, config, *args, **kwargs):
        """
        Initializes the Presets frame and the dynamic GUI builder.
        """
        super().__init__(parent, *args, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)

        self.config_data = config # Store the config for later use

        # --- Dynamic GUI Builder ---
        # Create an instance of the new, corrected, and modular builder,
        # passing the specific base topic for this GUI component.
        self.dynamic_gui = DynamicGuiBuilder(
            parent=self,
            json_path=JSON_CONFIG_FILE,
            config=self.config_data
        )