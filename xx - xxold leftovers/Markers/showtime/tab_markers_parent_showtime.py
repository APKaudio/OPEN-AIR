# Markers/showtime/tab_markers_parent_showtime.py
#
# Version 20250821.222500.1 (Refactored for print statements)

import tkinter as tk
from tkinter import ttk
import os
import inspect
from datetime import datetime

from ..showtime.zones_groups_devices.tab_markers_child_zone_groups_devices import ZoneGroupsDevicesFrame
from ..showtime.controls.tab_markers_parent_bottom_controls import ControlsFrame

current_version = "20250821.222500.1"

class ShowtimeTab(ttk.Frame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app_instance = app_instance
        self.parent = parent
        self._create_widgets()
        self.bind("<<NotebookTabChanged>>", self._on_tab_selected)

    def _create_widgets(self):
        content_frame = ttk.Frame(self, style='Main.TFrame')
        content_frame.pack(expand=True, fill='both')
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        self.zgd_frame = ZoneGroupsDevicesFrame(parent_frame=content_frame, showtime_tab_instance=self)
        self.zgd_frame.grid(row=0, column=0, sticky="nsew")
        self.controls_frame = ControlsFrame(parent_frame=content_frame, showtime_tab_instance=self)
        self.controls_frame.grid(row=1, column=0, sticky="ew")

    def _on_tab_selected(self, event):
        pass