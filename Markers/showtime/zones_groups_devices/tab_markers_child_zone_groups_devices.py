# tabs/Markers/showtime/zones_groups_devices/tab_markers_child_zone_groups_devices.py
#
# [This file defines the ZoneGroupsDevicesFrame, which dynamically loads
# and displays data from the MARKERS.CSV file.]
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
# Version 20250824.110500.1
# REFACTORED: This file has been refactored to serve exclusively as a UI component.
#             The event handler functions have been moved to their own dedicated
#             utility files, thereby eliminating circular dependencies.
# UPDATED: The class now correctly uses `partial` to call the external handler functions.

import tkinter as tk
from tkinter import ttk
from functools import partial
import os
import inspect
from datetime import datetime

# Import utility functions from their dedicated files
from .utils_files_markers_zone_groups_devices import load_and_structure_markers_data
from .utils_button_volume_level import create_signal_level_indicator

# Import the specific selection handlers for each button type
from .utils_display_showtime_zones import on_zone_selected
from .utils_display_showtime_groups import on_group_selected
from .utils_display_showtime_devices import on_device_selected
from .utils_display_showtime_all import on_all_markers_selected

from display.debug_logic import debug_log
from display.console_logic import console_log
from src.program_style import COLOR_PALETTE


# --- Versioning ---
w = 20250824
x_str = '110500'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"


class ZoneGroupsDevicesFrame(ttk.Frame):
    def __init__(self, parent_frame, showtime_tab_instance):
        # [Initializes the frame, restoring the original grid layout and scrollable device list.]
        super().__init__(parent_frame, style='TFrame')
        self.showtime_tab_instance = showtime_tab_instance
        self.structured_data = None
        self.grid(row=0, column=0, sticky="nsew")

        # Widget references for active selections, now correctly on the Frame instance
        self.active_zone_button = None
        self.active_group_button = None

        self._create_layout()

    def _create_layout(self):
        # [Creates the main layout with zones, groups, and the scrollable device frame.]
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1) # Allow device frame to expand
        
        self.zones_frame = ttk.LabelFrame(self, text="Zones", style='TLabelframe')
        self.zones_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        self.groups_frame = ttk.LabelFrame(self, text="Groups", style='TLabelframe')
        self.groups_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        self._create_device_frame(self)

    def _create_device_frame(self, parent):
        # [Creates the scrollable canvas for the device buttons.]
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

    def load_and_display_data(self):
        # [Main entry point to load data and fully rebuild the UI.]
        self.structured_data = load_and_structure_markers_data()
        self._make_zone_buttons()
        self._make_group_buttons()
        self._make_device_buttons()
        
        all_devices = self._get_all_devices_in_zone(self.structured_data, None)
        self._get_min_max_freq_and_update_title(frame_widget=self.zones_frame, devices=all_devices, title_prefix="ALL DEVICES")
        self.groups_frame.config(text="Groups")
        self.devices_outer_frame.config(text="Devices")

    def _make_zone_buttons(self):
        # [Creates the zone selection buttons in a grid.]
        for widget in self.zones_frame.winfo_children():
            widget.destroy()
        if not self.structured_data:
            ttk.Label(self.zones_frame, text="Could not load MARKERS.CSV").pack(padx=5, pady=5)
            return

        max_columns = 6
        for i, zone_name in enumerate(self.structured_data.keys()):
            row, col = divmod(i, max_columns)
            # Calls the external function from utils_display_showtime_zones.py
            btn = ttk.Button(self.zones_frame, text=zone_name, style='ControlButton.Inactive.TButton', command=partial(on_zone_selected, self, zone_name))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            self.zones_frame.columnconfigure(col, weight=1)

    def _make_group_buttons(self):
        # [Creates group buttons, dynamically showing/hiding the frame.]
        for widget in self.groups_frame.winfo_children():
            widget.destroy()
        self.groups_frame.grid_remove() # Hide by default

        if not self.showtime_tab_instance.selected_zone or not self.structured_data:
            return

        groups = self.structured_data.get(self.showtime_tab_instance.selected_zone, {})
        # Show frame only if there are meaningful groups to select
        if len(groups) > 1 or (len(groups) == 1 and next(iter(groups)) not in ['Ungrouped', 'No Group']):
            self.groups_frame.grid()
        else:
            return

        max_columns = 6
        for i, group_name in enumerate(groups.keys()):
            row, col = divmod(i, max_columns)
            # Calls the external function from utils_display_showtime_groups.py
            btn = ttk.Button(self.groups_frame, text=group_name, style='ControlButton.Inactive.TButton', command=partial(on_group_selected, self, group_name))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            self.groups_frame.columnconfigure(col, weight=1)

    def _make_device_buttons(self):
        # [Creates the detailed, multi-line device buttons in the scrollable frame.]
        for widget in self.devices_scrollable_frame.winfo_children():
            widget.destroy()
        self.showtime_tab_instance.device_buttons.clear()

        devices_to_display = self._get_devices_to_display()
        self.devices_outer_frame.config(text=f"Devices ({len(devices_to_display)})")

        max_cols = 4
        for col in range(max_cols):
            self.devices_scrollable_frame.grid_columnconfigure(col, weight=1)
            
        for i, device in enumerate(devices_to_display):
            name = device.get('NAME', 'N/A')
            device_type = device.get('DEVICE', 'N/A')
            center = device.get('CENTER', 'N/A')
            peak = device.get('PEAK', -120.0)
            
            progress_bar = create_signal_level_indicator(peak)
            btn_text = f"{name}\n{device_type}\n{center} MHz\n{peak} dBm\n{progress_bar}"
            
            # Calls the external function from utils_display_showtime_devices.py
            btn = ttk.Button(self.devices_scrollable_frame, text=btn_text, style='DeviceButton.Inactive.TButton', command=partial(on_device_selected, self, device))
            self.showtime_tab_instance.device_buttons[id(device)] = btn
            
            row, col = divmod(i, max_cols)
            btn.grid(row=row, column=col, padx=5, pady=2, sticky="ew")

    def _get_devices_to_display(self):
        # [Helper to determine which list of devices to show based on selection.]
        if self.showtime_tab_instance.selected_zone:
            zone_data = self.structured_data.get(self.showtime_tab_instance.selected_zone, {})
            if self.showtime_tab_instance.selected_group:
                return zone_data.get(self.showtime_tab_instance.selected_group, [])
            else:
                return self._get_all_devices_in_zone(self.structured_data, self.showtime_tab_instance.selected_zone)
        return self._get_all_devices_in_zone(self.structured_data, None)

    def _get_min_max_freq_and_update_title(self, frame_widget, devices, title_prefix):
        # [Calculates min/max frequency and updates a frame's title.]
        freqs = [float(d['CENTER']) for d in devices if isinstance(d.get('CENTER'), (int, float))]
        if freqs:
            min_freq, max_freq = min(freqs), max(freqs)
            new_title = f"{title_prefix} ({len(devices)}) - MIN: {min_freq:.3f} MHz - MAX: {max_freq:.3f} MHz"
        else:
            new_title = f"{title_prefix} ({len(devices)})"
        frame_widget.config(text=new_title)
        
    def _get_all_devices_in_zone(self, structured_data, zone_name):
        # [Helper to flatten all devices from all groups within a zone, or all zones.]
        devices = []
        if structured_data and zone_name: # A specific zone
            for group_devices in structured_data.get(zone_name, {}).values():
                devices.extend(group_devices)
        elif structured_data: # All zones
            for zone in structured_data.values():
                for group_devices in zone.values():
                    devices.extend(group_devices)
        return devices