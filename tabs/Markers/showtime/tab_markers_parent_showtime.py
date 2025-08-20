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
# Version 20250821.020000.1
# REFACTORED: The ShowtimeTab now acts as a central state manager, housing all shared
#             Tkinter variables and attributes for its child components.
# FIXED: Removed the redundant call to `controls_frame._update_control_styles()` from
#        the `_on_tab_selected` method to prevent a race condition and `AttributeError`.
# FIXED: Corrected the typo for `toggle_get_max_traces` to resolve `AttributeError`.

current_version = "20250821.020000.1"
current_version_hash = (20250821 * 20000 * 1)

import tkinter as tk
from tkinter import ttk
import os
import inspect

from tabs.Markers.showtime.controls.tab_markers_parent_bottom_controls import ControlsFrame
from tabs.Markers.showtime.zones_groups_devices.tab_markers_child_zone_groups_devices import ZoneGroupsDevicesFrame
from display.debug_logic import debug_log
from display.console_logic import console_log


class ShowtimeTab(ttk.Frame):
    def __init__(self, parent, app_instance):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        super().__init__(parent)
        self.app_instance = app_instance
        self.console_print_func = console_log
        self.grid(row=0, column=0, sticky="nsew")

        # --- Shared State Variables for ControlsFrame and ZoneGroupsDevicesFrame ---
        # These variables are accessed and modified by the child frames.
        
        # UI State
        self.active_zone_button = None
        self.active_group_button = None
        self.active_device_button = None
        self.last_selected_type = None

        # Zone/Group/Device Data
        self.structured_data = None
        self.selected_zone = None
        self.selected_group = None
        self.selected_device_info = None
        self.device_buttons = {}

        # Frequency Controls
        self.span_var = tk.StringVar(value="1000000") # Span in Hz
        self.rbw_var = tk.StringVar(value="100000") # RBW in Hz
        self.poke_freq_var = tk.StringVar()
        self.buffer_var = tk.StringVar(value="1") # Buffer for zone/group/all markers zoom in MHz
        self.follow_zone_span_var = tk.BooleanVar(value=True) # If true, span is determined by zone/group/all markers

        # Zoom Labels
        self.zone_zoom_label_left_var = tk.StringVar(value="All Markers")
        self.zone_zoom_label_center_var = tk.StringVar(value="Start: N/A")
        self.zone_zoom_label_right_var = tk.StringVar(value="Stop: N/A (0 Markers)")

        # Trace Controls
        self.toggle_get_all_traces = tk.BooleanVar(value=False)
        self.toggle_get_live_trace = tk.BooleanVar(value=False)
        self.toggle_get_max_traces = tk.BooleanVar(value=False) # Corrected typo here
        self.trace_buttons = {} # Stores references to trace control buttons
        self.span_buttons = {}
        self.rbw_buttons = {}
        self.zone_zoom_buttons = {}
        
        self._create_widgets()
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)


    def _create_widgets(self):
        # Creates and places the primary UI frames for this tab.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        
        try:
            self.rowconfigure(0, weight=1)
            self.columnconfigure(0, weight=1)

            # Pass a reference to THIS parent class to the child classes
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
            console_log("✅ Showtime tab refreshed.", "INFO")
            debug_log("Showtime tab refreshed successfully. 👍", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        except Exception as e:
            console_log(f"❌ Error during Showtime tab selection: {e}", "ERROR")
            debug_log(f"Error during Showtime tab selection: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
            
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)