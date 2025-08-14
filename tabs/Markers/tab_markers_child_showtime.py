# tabs/Markers/tab_markers_child_showtime.py
#
# This file defines the Showtime tab. It assembles the main UI components
# by combining the ZoneGroupsDevicesFrame and the ControlsFrame.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250814.161500.1

current_version = "20250814.161500.1"
current_version_hash = (20250814 * 161500 * 1)

import tkinter as tk
from tkinter import ttk

# Import the custom frame components
from .tab_markers_child_zone_groups_devices import ZoneGroupsDevicesFrame
from .tab_markers_child_controls import ControlsFrame

class ShowtimeTab(ttk.Frame):
    def __init__(self, parent, app_instance):
        # [A brief, one-sentence description of the function's purpose.]
        # Initializes the ShowtimeTab, creating and arranging its main UI components.
        super().__init__(parent)
        self.app_instance = app_instance
        self.grid(row=0, column=0, sticky="nsew")

        self._create_widgets()

    def _create_widgets(self):
        # [A brief, one-sentence description of the function's purpose.]
        # Creates and places the primary UI frames for this tab.
        
        # Configure the grid layout for the ShowtimeTab itself.
        # Row 0 (Zone/Groups/Devices) should expand. Row 1 (Controls) should not.
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Create and place the Zones, Groups, and Devices frame at the top
        self.zgd_frame = ZoneGroupsDevicesFrame(self, self.app_instance)
        self.zgd_frame.grid(row=0, column=0, sticky="nsew")

        # Create and place the Controls frame at the bottom
        self.controls_frame = ControlsFrame(self, self.app_instance)
        self.controls_frame.grid(row=1, column=0, sticky="ew")