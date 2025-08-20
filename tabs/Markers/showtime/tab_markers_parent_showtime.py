# tabs/Markers/showtime/tab_markers_parent_showtime.py
#
# This file defines the Showtime tab. It assembles the main UI components
# by combining the ZoneGroupsDevicesFrame and the ControlsFrame.
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
# Version 20250821.140800.1
# FIXED: The grid layout was corrected to ensure the controls_frame is
#        properly anchored to the bottom of the window.
# FIXED: Updated versioning to adhere to project standards.

import tkinter as tk
from tkinter import ttk
import os
import inspect
from datetime import datetime

from display.debug_logic import debug_log
from display.console_logic import console_log

from .storage_showtime_shared import ShowtimeSharedState
from tabs.Markers.showtime.zones_groups_devices.tab_markers_child_zone_groups_devices import ZoneGroupsDevicesFrame
from tabs.Markers.showtime.controls.tab_markers_parent_bottom_controls import ControlsFrame

# --- Versioning ---
w = 20250821
x_str = '140800'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"

class ShowtimeParentTab(ttk.Frame):
    def __init__(self, parent_notebook, app_instance, console_print_func):
        # [Initializes the Showtime tab, setting up the main frames and shared state.]
        super().__init__(parent_notebook)
        self.app_instance = app_instance
        self.console_print_func = console_print_func
        self.shared_state = ShowtimeSharedState()

        self._create_widgets()
        self.bind("<<NotebookTabChanged>>", self._on_tab_selected)

    def _create_widgets(self):
        # [Creates and packs the main UI components for the Showtime tab.]
        content_frame = ttk.Frame(self, style='Main.TFrame')
        content_frame.pack(expand=True, fill='both')

        # NEW: Configure the content_frame's grid to allow the top row to expand
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        self.zgd_frame = ZoneGroupsDevicesFrame(
            parent_frame=content_frame,
            showtime_tab_instance=self,
            shared_state=self.shared_state
        )
        self.zgd_frame.grid(row=0, column=0, sticky="nsew")

        self.controls_frame = ControlsFrame(
            parent_frame=content_frame,
            showtime_tab_instance=self,
            shared_state=self.shared_state
        )
        self.controls_frame.grid(row=1, column=0, sticky="ew")

        # The parent grid configuration is no longer needed here as content_frame handles its own layout
        # self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=1)

    def _on_tab_selected(self, event):
        # [Handles the event when this tab is selected.]
        try:
            self.zgd_frame.load_and_display_data()
            console_log("✅ Showtime tab refreshed.")
        except Exception as e:
            console_log(f"❌ Error during Showtime tab selection: {e}")
            raise
