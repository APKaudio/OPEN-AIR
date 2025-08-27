MQTT_TOPIC_FILTER = "OPEN-AIR/configuration/instrument/active/Instrument"
# display/left_50/top_100/tab_3_presets/sub_tab_1_pusher/gui_child_1_pusher.py
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
# Version 20250827.173001.1

import os
import tkinter as tk
from tkinter import ttk

# --- Module Imports ---
from display.builder.dynamic_gui_builder import DynamicGuiBuilder

# --- Global Scope Variables ---
current_version = "20250827.173001.1"
current_version_hash = (20250827 * 173001 * 1)
current_file = f"{os.path.basename(__file__)}"



class PresetPusherGui(ttk.Frame):
    """
    A container frame that instantiates the DynamicGuiBuilder for the Presets configuration.
    This replaces the old, monolithic code with a call to the reusable, modular component.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        """
        Initializes the Presets frame and the dynamic GUI builder.
        """
        super().__init__(parent, *args, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)

        # --- Dynamic GUI Builder ---
        # The DynamicGuiBuilder is instantiated with the correct and specific MQTT topic
        # filter for this GUI component.
        self.dynamic_gui = DynamicGuiBuilder(
            parent=self,
            mqtt_util=mqtt_util,
            base_topic=MQTT_TOPIC_FILTER
        )