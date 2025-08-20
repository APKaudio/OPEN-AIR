# tabs/Markers/showtime/tab_markers_child_zone_groups_devices.py
#
# This file defines the ZoneGroupsDevicesFrame, which now dynamically loads
# and displays data from the MARKERS.CSV file.
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
# Version 20250821.010500.1
# REFACTORED: The event-handling methods `on_zone_selected`, `on_group_selected`, and
#             `on_device_selected` were moved to a new utility file to improve modularity.
# REFACTORED: Now uses shared state variables from the parent `ShowtimeTab` instance.
#
# FIXED: The `ImportError` was fixed by correcting the import statements and ensuring
#        the correct utility functions are called.

current_version = "20250821.010500.1"
current_version_hash = (20250821 * 10500 * 1)

import tkinter as tk
from tkinter import ttk
from functools import partial
import os
import inspect
import pandas as pd
import math

# Import utility functions
from tabs.Markers.showtime.zones_groups_devices.utils_files_markers_zone_groups_devices import load_and_structure_markers_data
from tabs.Markers.showtime.zones_groups_devices.utils_button_volume_level import create_signal_level_indicator
from tabs.Markers.showtime.zones_groups_devices.utils_display_showtime_zone_groups_devices import on_zone_selected, on_group_selected, on_device_selected
from display.debug_logic import debug_log
from display.console_logic import console_log
from src.program_style import COLOR_PALETTE

class ZoneGroupsDevicesFrame(ttk.Frame):
    def __init__(self, parent, app_instance, showtime_tab_instance):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        super().__init__(parent, style='TFrame')
        self.app_instance = app_instance
        self.showtime_tab_instance = showtime_tab_instance
        self.grid(row=0, column=0, sticky="nsew")

        # The state is now managed in the parent `showtime_tab_instance`
        # self.structured_data = None
        # self.selected_zone = None
        # self.selected_group = None
        # self.selected_device_info = None
        # self.active_zone_button = None
        # self.active_group_button = None
        # self.active_device_button = None
        # self.device_buttons = {}
        # self.last_selected_type = None

        self._create_layout()
        self.load_and_display_data()
        
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def _create_layout(self):
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
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        self.devices_outer_frame = ttk.LabelFrame(parent, text="Devices", style='TLabelframe')
        self.devices_outer_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.devices_outer_frame.grid_rowconfigure(0, weight=1)
        self.devices_outer_frame.grid_columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(self.devices_outer_frame, borderwidth=0, highlightthickness=0, bg=COLOR_PALETTE['background'])
        scrollbar = ttk.Scrollbar(self.devices_outer_frame, orient="vertical", command=self.canvas.yview)
        self.devices_scrollable_frame = ttk.Frame(self.canvas, style='Dark.TFrame')
        self.devices_scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.devices_scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def load_and_display_data(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        # Update the parent's state variables directly
        self.showtime_tab_instance.active_zone_button = None
        self.showtime_tab_instance.active_group_button = None
        self.showtime_tab_instance.active_device_button = None
        self.showtime_tab_instance.selected_device_info = None
        
        self.showtime_tab_instance.structured_data = load_and_structure_markers_data()
        self._make_zone_buttons()
        self._make_group_buttons()
        self._make_device_buttons()
        
        all_devices = self._get_all_devices_in_zone(self.showtime_tab_instance.structured_data, None)
        self._get_min_max_freq_and_update_title(frame_widget=self.zones_frame, devices=all_devices, title_prefix="ALL DEVICES")
        self.groups_frame.config(text="Groups")
        self.devices_outer_frame.config(text="Devices")

        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def _make_zone_buttons(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        for widget in self.zones_frame.winfo_children():
            widget.destroy()
            
        if self.showtime_tab_instance.structured_data is None or not self.showtime_tab_instance.structured_data:
            console_log(f"❌ Marker CSV not found or is empty. Cannot load zones.", "ERROR")
            debug_log("Marker CSV not found or is empty. Cannot load zones. Fucking useless!", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
            ttk.Label(self.zones_frame, text="Could not load MARKERS.CSV").pack(padx=5, pady=5)
            return
            
        max_columns = 6
        for i, zone_name in enumerate(self.showtime_tab_instance.structured_data.keys()):
            row = i // max_columns
            col = i % max_columns
            btn = ttk.Button(self.zones_frame, text=zone_name, style='ControlButton.Inactive.TButton', command=partial(on_zone_selected, self, zone_name))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            self.zones_frame.columnconfigure(col, weight=1)
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def _make_group_buttons(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        for widget in self.groups_frame.winfo_children():
            widget.destroy()
        self.groups_frame.grid_remove()
        
        # Access selected_zone from the parent instance
        if not self.showtime_tab_instance.selected_zone or not self.showtime_tab_instance.structured_data:
            debug_log("No zone selected or no structured data. Exiting _make_group_buttons.", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
            return
            
        # Access structured_data from the parent instance
        groups = self.showtime_tab_instance.structured_data.get(self.showtime_tab_instance.selected_zone, {})
        
        if len(groups) > 1 or (len(groups) == 1 and next(iter(groups)) not in ['Ungrouped', 'No Group']):
            self.groups_frame.grid()
        else:
            debug_log("Only one group or no groups, keeping the groups frame hidden. We don't need no stinkin' groups!", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
            return
            
        max_columns = 6
        for i, group_name in enumerate(groups.keys()):
            row = i // max_columns
            col = i % max_columns
            btn = ttk.Button(self.groups_frame, text=group_name, style='ControlButton.Inactive.TButton', command=partial(on_group_selected, self, group_name))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            self.groups_frame.columnconfigure(col, weight=1)
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def _make_device_buttons(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        for widget in self.devices_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Access device_buttons dict from parent
        self.showtime_tab_instance.device_buttons.clear()
        
        devices_to_display = []
        # Access state from parent
        if self.showtime_tab_instance.selected_zone:
            if self.showtime_tab_instance.selected_group:
                devices_to_display = self.showtime_tab_instance.structured_data.get(self.showtime_tab_instance.selected_zone, {}).get(self.showtime_tab_instance.selected_group, [])
            else:
                for group_name in self.showtime_tab_instance.structured_data.get(self.showtime_tab_instance.selected_zone, {}).keys():
                    devices_to_display.extend(self.showtime_tab_instance.structured_data.get(self.showtime_tab_instance.selected_zone, {}).get(group_name, []))
        else:
            for zone_name in self.showtime_tab_instance.structured_data.keys():
                for group_name in self.showtime_tab_instance.structured_data.get(zone_name, {}).keys():
                    devices_to_display.extend(self.showtime_tab_instance.structured_data.get(zone_name, {}).get(group_name, []))
                    
        self.devices_outer_frame.config(text=f"Devices ({len(devices_to_display)})")
        max_cols = 4
        for col in range(max_cols):
            self.devices_scrollable_frame.grid_columnconfigure(col, weight=1)
            
        for i, device in enumerate(devices_to_display):
            name = device.get('NAME', 'N/A')
            device_type = device.get('DEVICE', 'N/A')
            center = device.get('CENTER', 'N/A')
            peak = device.get('PEAK', -120.0)
            if len(device_type) > 10:
                split_point = device_type.find(' ', 10)
                if split_point != -1:
                    device_type_formatted = device_type[:split_point] + "\n" + device_type[split_point+1:]
                else:
                    device_type_formatted = device_type[:10] + "\n" + device_type[10:]
            else:
                device_type_formatted = device_type
            progress_bar = create_signal_level_indicator(peak)
            btn_text = f"{name}\n{device_type_formatted}\n{center} MHz\n{peak} dBm\n{progress_bar}"
            btn = ttk.Button(self.devices_scrollable_frame, text=btn_text, style='DeviceButton.Inactive.TButton', command=partial(on_device_selected, self, device))
            
            # Store button reference in parent's dictionary
            self.showtime_tab_instance.device_buttons[id(device)] = btn
            
            row = i // max_cols
            col = i % max_cols
            btn.grid(row=row, column=col, padx=5, pady=2, sticky="ew", ipadx=10, ipady=5)
            
        debug_log(f"Exiting {current_function}. Rebuilt {len(devices_to_display)} device buttons. 🤖", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def _get_min_max_freq_and_update_title(self, frame_widget, devices, title_prefix):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function} to update title for '{title_prefix}'.", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        freqs = [float(d.get('CENTER')) for d in devices if d.get('CENTER') and isinstance(d.get('CENTER'), (int, float))]
        if freqs:
            min_freq = min(freqs)
            max_freq = max(freqs)
            new_title = f"{title_prefix} ({len(devices)}) - MIN: {min_freq:.3f} MHz - MAX: {max_freq:.3f} MHz"
            frame_widget.config(text=new_title)
            debug_log(f"Updated title to '{new_title}'.", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        else:
            new_title = f"{title_prefix} ({len(devices)})" if len(devices) > 0 else title_prefix
            frame_widget.config(text=new_title)
            debug_log(f"No frequencies found, title remains '{new_title}'.", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        
    def _get_all_devices_in_zone(self, structured_data, zone_name):
        # Helper function to flatten all devices from all groups within a zone.
        devices = []
        if structured_data and zone_name in structured_data:
            for group_name, group_devices in structured_data[zone_name].items():
                devices.extend(group_devices)
        elif not zone_name and structured_data:
            for zone in structured_data.values():
                for group_name in zone.keys():
                    devices.extend(zone.get(group_name, []))
        return devices