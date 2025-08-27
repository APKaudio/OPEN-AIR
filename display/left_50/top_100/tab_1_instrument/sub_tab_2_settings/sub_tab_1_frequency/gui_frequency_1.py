MQTT_TOPIC_FILTER = "OPEN-AIR/configuration/instrument/Instrument_Settings"
# display/tabs/gui_child_2_settings.py
#
# A GUI frame for displaying and controlling Marker Settings via MQTT.
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
# Version 20250827.140519.3

import os
import tkinter as tk
from tkinter import ttk

# --- Module Imports ---
from display.builder.dynamic_gui_builder import DynamicGuiBuilder

# --- Global Scope Variables ---
current_version = "20250827.140519.3"
current_version_hash = (20250827 * 140519 * 3)
current_file = f"{os.path.basename(__file__)}"


class DynamicGui(ttk.Frame):
    """
    A container frame that instantiates the DynamicGuiBuilder for Marker Settings.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        """
        Initializes the Marker Settings frame and the dynamic GUI builder.
        """
        super().__init__(parent, *args, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)

        # --- Dynamic GUI Builder ---
        # Create an instance of the dynamic builder, passing the specific
        # base topic for this GUI component.
        self.dynamic_gui = DynamicGuiBuilder(
            parent=self,
            mqtt_util=mqtt_util,
            base_topic=MQTT_TOPIC_FILTER
        )