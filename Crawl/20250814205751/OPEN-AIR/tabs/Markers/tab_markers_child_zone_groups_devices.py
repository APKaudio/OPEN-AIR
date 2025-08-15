# FolderName/tab_markers_child_zone_groups_devices.py
#
# This file defines the ZoneGroupsDevicesFrame, which now dynamically loads
# and displays data from the MARKERS.CSV file.
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
# Version 20250814.180000.7

current_version = "20250814.180000.7"
current_version_hash = (20250814 * 180000 * 7)

import tkinter as tk
from tkinter import ttk
from functools import partial
import os
import inspect
import pandas as pd

# Import the new utility functions
from .utils_markers_files_zone_groups_devices import load_and_structure_markers_data, create_progress_bar
from .utils_markers_zone_group_devices_actions import _start_orchestrated_scan_loop, _stop_scan_loops, focus_device
from display.debug_logic import debug_log
from display.console_logic import console_log

class ZoneGroupsDevicesFrame(ttk.Frame):
    def __init__(self, parent, app_instance, showtime_tab_instance):
        # Initializes the frame and loads the initial data.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        super().__init__(parent, style='TFrame')
        self.app_instance = app_instance
        self.showtime_tab_instance = showtime_tab_instance # Store reference to parent ShowtimeTab
        self.grid(row=0, column=0, sticky="nsew")

        self.structured_data = None
        self.selected_zone = None
        self.selected_group = None
        self.active_zone_button = None
        self.active_group_button = None
        self.active_device_button = None
        self.device_buttons = {} # Store device button widgets

        self._create_layout()
        self.load_and_display_data()
        
        # TODO: Implement a file watcher for MARKERS.CSV to call self.load_and_display_data on change.
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def _create_layout(self):
        # Creates the static layout frames for zones, groups, and devices.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.zones_frame = ttk.LabelFrame(self, text="Zones", style='TLabelframe')
        self.zones_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        self.groups_frame = ttk.LabelFrame(self, text="Groups", style='TLabelframe')
        self.groups_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        self._create_device_frame(self)
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def _create_device_frame(self, parent):
        # Creates the scrollable area for device buttons.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        devices_outer_frame = ttk.LabelFrame(parent, text="Devices", style='TLabelframe')
        devices_outer_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        devices_outer_frame.grid_rowconfigure(0, weight=1)
        devices_outer_frame.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(devices_outer_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(devices_outer_frame, orient="vertical", command=canvas.yview)
        self.devices_scrollable_frame = ttk.Frame(canvas, style='Dark.TFrame')

        self.devices_scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.devices_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)


    def load_and_display_data(self):
        # Fetches data using the utility and triggers the UI build.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        
        self.structured_data = load_and_structure_markers_data()
        self._make_zone_buttons()
        self._make_group_buttons()
        self._make_device_buttons()
        
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)


    def _make_zone_buttons(self):
        # Clears and rebuilds the zone buttons based on the loaded data.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        for widget in self.zones_frame.winfo_children():
            widget.destroy()
        
        if self.structured_data is None or not self.structured_data:
            console_log(f"❌ Marker CSV not found or is empty. Cannot load zones.", "ERROR")
            debug_log("Marker CSV not found or is empty. Cannot load zones. Fucking useless!", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
            ttk.Label(self.zones_frame, text="Could not load MARKERS.CSV").pack(padx=5, pady=5)
            return

        max_columns = 6
        for i, zone_name in enumerate(self.structured_data.keys()):
            row = i // max_columns
            col = i % max_columns
            btn = ttk.Button(self.zones_frame, text=zone_name, style='ControlButton.Inactive.TButton',
                             command=partial(self.on_zone_selected, zone_name))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            self.zones_frame.columnconfigure(col, weight=1)
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)


    def _make_group_buttons(self):
        # Clears and rebuilds group buttons for the currently selected zone.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        for widget in self.groups_frame.winfo_children():
            widget.destroy()
            
        self.groups_frame.grid_remove()  # Hide the frame by default
        
        if not self.selected_zone or not self.structured_data:
            debug_log("No zone selected or no structured data. Exiting _make_group_buttons.", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
            return

        groups = self.structured_data.get(self.selected_zone, {})
        
        # Only show groups if there is more than one group or the single group is NOT 'Ungrouped'
        if len(groups) > 1:
             self.groups_frame.grid()  # Show the frame again if conditions are met
             self.selected_group = next(iter(groups))
        elif len(groups) == 1 and ('Ungrouped' not in groups and 'No Group' not in groups):
             self.groups_frame.grid()
        else:
             self._make_device_buttons() # Call _make_device_buttons directly to show all devices
             return
            
        max_columns = 6
        for i, group_name in enumerate(groups.keys()):
            row = i // max_columns
            col = i % max_columns
            btn = ttk.Button(self.groups_frame, text=group_name, style='ControlButton.Inactive.TButton',
                             command=partial(self.on_group_selected, group_name))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            self.groups_frame.columnconfigure(col, weight=1)
        
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)


    def _make_device_buttons(self):
        # Clears and rebuilds device buttons for the selected zone/group.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        
        for widget in self.devices_scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.selected_zone or self.structured_data is None:
            debug_log("No zone selected or no structured data. Exiting _make_device_buttons.", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
            return
            
        devices = []
        if self.selected_group:
            devices = self.structured_data.get(self.selected_zone, {}).get(self.selected_group, [])
        else: # Display all devices in the zone if no group is selected
            for group_name in self.structured_data.get(self.selected_zone, {}).keys():
                devices.extend(self.structured_data.get(self.selected_zone, {}).get(group_name, []))

        max_cols = 4
        for i, device in enumerate(devices):
            name = device.get('NAME', 'N/A')
            device_type = device.get('DEVICE', 'N/A')
            center = device.get('CENTER', 'N/A')
            peak = device.get('PEAK', -120.0)
            
            progress_bar = create_progress_bar(peak)
            
            btn_text = f"{name}\n{device_type}\n{center} MHz\n{peak} dBm\n{progress_bar}"
            
            btn = ttk.Button(self.devices_scrollable_frame, text=btn_text, style='DeviceButton.Inactive.TButton',
                             command=partial(self.on_device_selected, name))
            
            row = i // max_cols
            col = i % max_cols
            
            btn.grid(row=row, column=col, padx=5, pady=2, sticky="ew", ipadx=10, ipady=5)
            self.devices_scrollable_frame.grid_columnconfigure(col, weight=1)
        
        debug_log(f"Exiting {current_function}. Rebuilt {len(devices)} device buttons.", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)


    # --- Event Handlers ---
    def on_zone_selected(self, zone_name, event=None):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function} for zone: {zone_name}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        
        if self.active_zone_button:
            self.active_zone_button.config(style='ControlButton.Inactive.TButton')
            
        if self.active_group_button:
            self.active_group_button.config(style='ControlButton.Inactive.TButton')
            self.active_group_button = None

        self.selected_zone = zone_name
        self.selected_group = None
        console_log(f"EVENT: Zone '{zone_name}' selected. Loading groups and devices...", "INFO")
        
        if event and event.widget:
            event.widget.config(style='ControlButton.Active.TButton')
            self.active_zone_button = event.widget
        
        _stop_scan_loops()
        _start_orchestrated_scan_loop(self.app_instance, self.showtime_tab_instance)

        self._make_group_buttons()
        self._make_device_buttons()
        
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        
    def on_group_selected(self, group_name, event=None):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function} for group: {group_name}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        if self.active_group_button:
            self.active_group_button.config(style='ControlButton.Inactive.TButton')

        self.selected_group = group_name
        console_log(f"EVENT: Group '{group_name}' selected in Zone '{self.selected_zone}'. Loading devices...", "INFO")
        
        if event and event.widget:
            event.widget.config(style='ControlButton.Active.TButton')
            self.active_group_button = event.widget
        
        _stop_scan_loops()
        _start_orchestrated_scan_loop(self.app_instance, self.showtime_tab_instance)
            
        self._make_device_buttons()

        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def on_device_selected(self, device_name, event=None):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function} for device: {device_name}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        console_log(f"EVENT: Device '{device_name}' selected.", "INFO")
        
        _stop_scan_loops()
        focus_device(self.app_instance, self.showtime_tab_instance, device_name)

        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)