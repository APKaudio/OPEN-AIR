# tabs/Markers/showtime/tab_markers_child_zone_groups_devices.py
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
# Version 20250819.213800.5
# REFACTORED: The logic for handling pandas operations was updated to prevent FutureWarning messages.
# MODIFIED: The function `on_zone_selected` was updated to reset group and device selections when a zone is deselected.
# MODIFIED: Added logic to switch tabs in the ControlsFrame to ensure the correct controls are visible.
# FIXED: Resolved circular import by removing reference to utils_showtime_controls.py and calling the method on the controls_frame instance.

current_version = "20250819.213800.5"
current_version_hash = (20250819 * 213800 * 5)

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

        self.structured_data = None
        self.selected_zone = None
        self.selected_group = None
        self.selected_device_info = None
        self.active_zone_button = None
        self.active_group_button = None
        self.active_device_button = None
        self.device_buttons = {}

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
        self.active_zone_button = None
        self.active_group_button = None
        self.active_device_button = None
        self.selected_device_info = None
        self.structured_data = load_and_structure_markers_data()
        self._make_zone_buttons()
        self._make_group_buttons()
        self._make_device_buttons()
        all_devices = self._get_all_devices_in_zone(self.structured_data, None)
        self._get_min_max_freq_and_update_title(frame_widget=self.zones_frame, devices=all_devices, title_prefix="ALL DEVICES")
        self.groups_frame.config(text="Groups")
        self.devices_outer_frame.config(text="Devices")
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def _make_zone_buttons(self):
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
            btn = ttk.Button(self.zones_frame, text=zone_name, style='ControlButton.Inactive.TButton', command=partial(self.on_zone_selected, zone_name))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            self.zones_frame.columnconfigure(col, weight=1)
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def _make_group_buttons(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        for widget in self.groups_frame.winfo_children():
            widget.destroy()
        self.groups_frame.grid_remove()
        if not self.selected_zone or not self.structured_data:
            debug_log("No zone selected or no structured data. Exiting _make_group_buttons.", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
            return
        groups = self.structured_data.get(self.selected_zone, {})
        if len(groups) > 1 or (len(groups) == 1 and next(iter(groups)) not in ['Ungrouped', 'No Group']):
            self.groups_frame.grid()
        else:
            debug_log("Only one group or no groups, keeping the groups frame hidden. We don't need no stinkin' groups!", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
            return
        max_columns = 6
        for i, group_name in enumerate(groups.keys()):
            row = i // max_columns
            col = i % max_columns
            btn = ttk.Button(self.groups_frame, text=group_name, style='ControlButton.Inactive.TButton', command=partial(self.on_group_selected, group_name))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            self.groups_frame.columnconfigure(col, weight=1)
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def _make_device_buttons(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        for widget in self.devices_scrollable_frame.winfo_children():
            widget.destroy()
        self.device_buttons.clear()
        devices_to_display = []
        if self.selected_zone:
            if self.selected_group:
                devices_to_display = self.structured_data.get(self.selected_zone, {}).get(self.selected_group, [])
            else:
                for group_name in self.structured_data.get(self.selected_zone, {}).keys():
                    devices_to_display.extend(self.structured_data.get(self.selected_zone, {}).get(group_name, []))
        else:
            for zone_name in self.structured_data.keys():
                for group_name in self.structured_data.get(zone_name, {}).keys():
                    devices_to_display.extend(self.structured_data.get(zone_name, {}).get(group_name, []))
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
            btn = ttk.Button(self.devices_scrollable_frame, text=btn_text, style='DeviceButton.Inactive.TButton', command=partial(self.on_device_selected, device))
            self.device_buttons[id(device)] = btn
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

    def on_zone_selected(self, zone_name):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function} for zone: {zone_name}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        for widget in self.zones_frame.winfo_children():
            if widget.cget("text") == zone_name:
                selected_button = widget
                break
        else:
            selected_button = None

        if self.selected_zone == zone_name:
            console_log(f"EVENT: Zone '{zone_name}' deselected. Unfiltering to show all devices. 🔍", "INFO")
            self.selected_zone = None
            self.selected_group = None
            self.selected_device_info = None
            if self.active_zone_button and self.active_zone_button.winfo_exists():
                self.active_zone_button.config(style='ControlButton.Inactive.TButton')
                self.active_zone_button = None
            if self.active_group_button and self.active_group_button.winfo_exists():
                self.active_group_button.config(style='ControlButton.Inactive.TButton')
                self.active_group_button = None
            self.groups_frame.grid_remove()
            all_devices = self._get_all_devices_in_zone(self.structured_data, None)
            self._get_min_max_freq_and_update_title(frame_widget=self.zones_frame, devices=all_devices, title_prefix="ALL DEVICES")
        else:
            console_log(f"EVENT: Zone '{zone_name}' selected. Loading groups and devices... 🚀", "INFO")
            if self.active_zone_button and self.active_zone_button.winfo_exists():
                self.active_zone_button.config(style='ControlButton.Inactive.TButton')
            if self.active_group_button and self.active_group_button.winfo_exists():
                self.active_group_button.config(style='ControlButton.Inactive.TButton')
                self.active_group_button = None
            
            self.active_device_button = None
            self.selected_device_info = None

            self.selected_zone = zone_name
            self.selected_group = None
            
            if selected_button:
                selected_button.config(style='ControlButton.Active.TButton')
                self.active_zone_button = selected_button
            
            all_devices_in_zone = self._get_all_devices_in_zone(self.structured_data, self.selected_zone)
            self._get_min_max_freq_and_update_title(frame_widget=self.zones_frame, devices=all_devices_in_zone, title_prefix=f"Zone '{zone_name}'")

        self._get_min_max_freq_and_update_title(frame_widget=self.groups_frame, devices=[], title_prefix=f"Groups in Zone '{self.selected_zone}'" if self.selected_zone else "Groups")

        self._make_group_buttons()
        self._make_device_buttons()
        self.canvas.yview_moveto(0)
        
        self.showtime_tab_instance.controls_frame._update_control_styles()
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        
    def on_group_selected(self, group_name):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function} for group: {group_name}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        devices_in_group = self.structured_data.get(self.selected_zone, {}).get(group_name, [])

        if len(devices_in_group) == 1:
            console_log(f"EVENT: Group '{group_name}' contains one device. Auto-selecting device...", "INFO")
            self.selected_group = group_name 
            self._make_device_buttons() 
            self.on_device_selected(devices_in_group[0]) 
            
            for widget in self.groups_frame.winfo_children():
                if widget.cget("text") == group_name:
                    if self.active_group_button and self.active_group_button.winfo_exists():
                        self.active_group_button.config(style='ControlButton.Inactive.TButton')
                    widget.config(style='ControlButton.Active.TButton')
                    self.active_group_button = widget
                    break
            return

        # --- MODIFIED: Corrected logic for group deselection ---
        if self.selected_group == group_name:
            console_log(f"EVENT: Group '{group_name}' deselected. Reverting to show all devices in Zone '{self.selected_zone}'.", "INFO")
            if self.active_group_button and self.active_group_button.winfo_exists():
                self.active_group_button.config(style='ControlButton.Inactive.TButton')
                self.active_group_button = None
            self.selected_group = None
            self._make_device_buttons()
            self.showtime_tab_instance.controls_frame._update_control_styles()
            return

        # --- Existing group selection logic ---
        for widget in self.groups_frame.winfo_children():
            if widget.cget("text") == group_name:
                selected_button = widget
                break
        else:
            selected_button = None

        console_log(f"EVENT: Group '{group_name}' selected in Zone '{self.selected_zone}'. Loading devices... ⚙️", "INFO")
        if self.active_group_button and self.active_group_button.winfo_exists():
            self.active_group_button.config(style='ControlButton.Inactive.TButton')

        self.active_device_button = None
        self.selected_device_info = None
        self.selected_group = group_name

        if selected_button:
            selected_button.config(style='ControlButton.Active.TButton')
            self.active_group_button = selected_button
        
        self._get_min_max_freq_and_update_title(frame_widget=self.groups_frame, devices=devices_in_group, title_prefix=f"Group '{group_name}'")

        self._make_device_buttons()
        self.canvas.yview_moveto(0)
        self.showtime_tab_instance.controls_frame._update_control_styles()
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def on_device_selected(self, device_info):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function} for device object: {device_info}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        device_name = device_info.get('NAME', 'N/A')
        if isinstance(device_name, float) and math.isnan(device_name):
            device_name = 'nan'

        if self.selected_device_info and id(self.selected_device_info) == id(device_info):
            console_log(f"EVENT: Device '{device_name}' deselected.", "INFO")
            self.selected_device_info = None
            if self.active_device_button and self.active_device_button.winfo_exists():
                self.active_device_button.config(style='DeviceButton.Inactive.TButton')
            self.active_device_button = None
            self.showtime_tab_instance.controls_frame._update_control_styles()
            # FIXED: Add tab switch logic for deselection
            if hasattr(self.showtime_tab_instance.controls_frame, 'switch_to_tab'):
                self.showtime_tab_instance.controls_frame.switch_to_tab("Zone Zoom")
            debug_log(f"Exiting {current_function} after deselecting device.", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
            return

        self.selected_device_info = device_info
        selected_button = self.device_buttons.get(id(device_info))
        
        if self.active_device_button and self.active_device_button.winfo_exists():
            self.active_device_button.config(style='DeviceButton.Inactive.TButton')

        if selected_button:
            selected_button.config(style='DeviceButton.Active.TButton')
            self.active_device_button = selected_button
            console_log(f"EVENT: Device '{device_name}' selected. 🎵", "INFO")
        
        if device_info:
            freq = device_info.get('CENTER', 'N/A')
            if freq != 'N/A':
                self.devices_outer_frame.config(text=f"Devices - {device_name} - {freq:.3f} MHz")
                console_log(f"✅ Displaying device '{device_name}' at frequency {freq:.3f} MHz.", "SUCCESS")
                # FIXED: Add tab switch logic for selection
                if hasattr(self.showtime_tab_instance.controls_frame, 'switch_to_tab'):
                    self.showtime_tab_instance.controls_frame.switch_to_tab("Span")
            else:
                self.devices_outer_frame.config(text=f"Devices - {device_name} - N/A")
                console_log(f"⚠️ Device '{device_name}' has no valid frequency.", "WARNING")
        else:
            self.devices_outer_frame.config(text="Devices")
            console_log(f"❌ Device info not found. The device has vanished into thin air!", "ERROR")

        self.showtime_tab_instance.controls_frame._update_control_styles()
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