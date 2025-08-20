# tabs/Markers/showtime/tab_markers_parent_showtime.py
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
# Version 20250818.145245.1

current_version = "20250818.145245.1"
current_version_hash = (20250818 * 145245 * 1)

import tkinter as tk
from tkinter import ttk
import os
import inspect

# Import the custom frame components
from tabs.Markers.showtime.zones_groups_devices.tab_markers_child_zone_groups_devices import ZoneGroupsDevicesFrame
# The import for ControlsFrame is now moved inside _create_widgets to prevent circular dependency

# Import the sync_trace_modes function
from tabs.Markers.showtime.controls.tab_markers_parent_bottom_controls import ControlsFrame


from display.debug_logic import debug_log
from display.console_logic import console_log

class ShowtimeTab(ttk.Frame):
    def __init__(self, parent, app_instance):
        # Initializes the ShowtimeTab, creating and arranging its main UI components.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        
        super().__init__(parent)
        self.app_instance = app_instance
        self.console_print_func = console_log

        self._create_widgets()
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def _create_widgets(self):
        # --- MOVED IMPORT HERE TO FIX CIRCULAR DEPENDENCY ---
        

        # Creates and places the primary UI frames for this tab.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        
        try:
            self.rowconfigure(0, weight=1)
            self.columnconfigure(0, weight=1)

            self.zgd_frame = ZoneGroupsDevicesFrame(self, self.app_instance, self)
            self.zgd_frame.grid(row=0, column=0, sticky="nsew")

            self.controls_frame = ControlsFrame(self, self.app_instance)
            self.controls_frame.grid(row=1, column=0, sticky="ew")
            
            debug_log("ShowtimeTab widgets created successfully. ✅", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        except Exception as e:
            console_log(f"❌ Error in _create_widgets for ShowtimeTab: {e}", "ERROR")
            debug_log(f"Arrr, the code be capsized in creating widgets! The error be: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def _on_tab_selected(self, event):
        # Handles the event when this tab is selected.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        try:
            self.zgd_frame.load_and_display_data()
            ControlsFrame(self.controls_frame)
            console_log("✅ Showtime tab refreshed.", "INFO")
            debug_log("Showtime tab refreshed successfully. 👍", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        except Exception as e:
            console_log(f"❌ Error during Showtime tab selection: {e}", "ERROR")
            debug_log(f"Error during Showtime tab selection: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
            
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)