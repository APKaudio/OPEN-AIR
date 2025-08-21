# tabs/Markers/showtime/controls/tab_markers_child_control_zone_zoom.py
#
# This file defines the Zone Zoom tab for the ControlsFrame.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: [https://like.audio/category/software/spectrum-scanner/](https://like.audio/category/software/spectrum-scanner/)
# Source Code: [https://github.com/APKaudio/](https://github.com/APKaudio/)
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250824.001000.1
# REFACTORED: Removed dependency on `shared_state` object. State is now accessed from the `showtime_tab_instance`.

import os
import inspect
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from display.debug_logic import debug_log

# --- Versioning ---
w = 20250824
x_str = '001000'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"

class ZoneZoomTab(ttk.Frame):
    def __init__(self, parent_notebook, showtime_tab_instance):
        # [Initializes the Zone Zoom control tab.]
        debug_log(f"🖥️ 🟢 Entering __init__",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        
        super().__init__(parent_notebook)
        self.showtime_tab_instance = showtime_tab_instance
        self._create_widgets()
        
        debug_log(f"🖥️ 🟢 Exiting __init__",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        
    def _create_widgets(self):
        # FIXED: Moved imports inside this method to resolve the ImportError.
        from .utils_showtime_zone_zoom import set_span_to_all_markers, set_span_to_device, set_span_to_group, set_span_to_zone
        
        # [Creates the UI elements for the Zone Zoom tab.]
        debug_log(f"🖥️ 🟢 Creating widgets for the Zone Zoom tab.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        
        # Main container uses a two-column grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Left side frame for buttons and buffer dropdown
        left_frame = ttk.Frame(self, style='TFrame')
        left_frame.grid(row=0, column=0, sticky="nsew")
        left_frame.grid_columnconfigure(0, weight=1)

        # Button Frame for Zone/Group/Device/All Markers buttons
        button_frame = ttk.Frame(left_frame, style='TFrame')
        button_frame.grid(row=0, column=0, sticky="ew")

        buttons_config = [
            ("Zone", lambda: set_span_to_zone(self.showtime_tab_instance, self)),
            ("Group", lambda: set_span_to_group(self.showtime_tab_instance, self)),
            ("Device", lambda: set_span_to_device(self.showtime_tab_instance, self)),
            ("All Markers", lambda: set_span_to_all_markers(self.showtime_tab_instance, self))
        ]

        self.showtime_tab_instance.zone_zoom_buttons.clear()
        for i, (text, command) in enumerate(buttons_config):
            btn = ttk.Button(button_frame, text=text, style='ControlButton.TButton', command=command, width=12)
            btn.grid(row=0, column=i, sticky='ew', padx=2, pady=2)
            self.showtime_tab_instance.zone_zoom_buttons[text.lower()] = btn
        button_frame.grid_columnconfigure(list(range(len(buttons_config))), weight=1)

        # Frame for the new "Window Buffer" dropdown
        buffer_frame = ttk.Frame(left_frame, style='TFrame')
        buffer_frame.grid(row=1, column=0, sticky="ew")
        buffer_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(buffer_frame, text="Window Buffer (MHz):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        buffer_options = ["1", "3", "10", "30"]
        self.buffer_dropdown = ttk.Combobox(buffer_frame, textvariable=self.showtime_tab_instance.buffer_var, values=buffer_options, state="readonly")
        self.buffer_dropdown.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.buffer_dropdown.set(self.showtime_tab_instance.buffer_var.get())

        # Right side frame for labels, allowing it to expand
        right_frame = ttk.Frame(self, style='TFrame')
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1) # The row for labels should expand
        right_frame.grid_columnconfigure(0, weight=1)

        label_frame = ttk.Frame(right_frame, style='TFrame')
        label_frame.grid(row=0, column=0, sticky="nsew")

        # The labels now have a vertical layout
        self.label_left = ttk.Label(label_frame, textvariable=self.showtime_tab_instance.zone_zoom_label_left_var, style='TLabel')
        self.label_center = ttk.Label(label_frame, textvariable=self.showtime_tab_instance.zone_zoom_label_center_var, style='TLabel')
        self.label_right = ttk.Label(label_frame, textvariable=self.showtime_tab_instance.zone_zoom_label_right_var, style='TLabel')

        self.label_left.pack(anchor="w", padx=5)
        self.label_center.pack(anchor="w", padx=5)
        self.label_right.pack(anchor="w", padx=5)
        
        debug_log(f"🖥️ ✅ Widgets created successfully.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        
    def _sync_ui_from_state(self):
        # [Updates button styles and labels based on the current selection in shared state.]
        debug_log(f"🖥️ 🔄 Syncing UI from shared state.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        
        # Reset all buttons to inactive first
        for btn in self.showtime_tab_instance.zone_zoom_buttons.values():
            btn.config(style='ControlButton.Inactive.TButton')
            
        # Set the active button based on the last selected type
        if self.showtime_tab_instance.last_selected_type:
            active_btn = self.showtime_tab_instance.zone_zoom_buttons.get(self.showtime_tab_instance.last_selected_type.lower())
            if active_btn:
                active_btn.config(style='ControlButton.Active.TButton')
        else: # Default to "All Markers" if nothing is selected
            all_markers_btn = self.showtime_tab_instance.zone_zoom_buttons.get('all markers')
            if all_markers_btn:
                all_markers_btn.config(style='ControlButton.Active.TButton')

        # Update the labels from the values stored in the shared state
        buffered_start = self.showtime_tab_instance.buffered_start_var.get()
        buffered_stop = self.showtime_tab_instance.buffered_stop_var.get()

        if self.showtime_tab_instance.last_selected_type == 'zone':
            zone_info = self.showtime_tab_instance.selected_zone_info
            count = zone_info.get('device_count', 0)
            self.showtime_tab_instance.zone_zoom_label_left_var.set(f"Zone ({count} Devices)")
            self.showtime_tab_instance.zone_zoom_label_center_var.set(f"Name: {self.showtime_tab_instance.selected_zone}")
            self.showtime_tab_instance.zone_zoom_label_right_var.set(f"Start: {buffered_start:.3f} MHz\nStop: {buffered_stop:.3f} MHz")
        elif self.showtime_tab_instance.last_selected_type == 'group':
            group_info = self.showtime_tab_instance.selected_group_info
            count = group_info.get('device_count', 0)
            self.showtime_tab_instance.zone_zoom_label_left_var.set(f"Group ({count} Devices)")
            self.showtime_tab_instance.zone_zoom_label_center_var.set(f"Name: {self.showtime_tab_instance.selected_group}")
            self.showtime_tab_instance.zone_zoom_label_right_var.set(f"Start: {buffered_start:.3f} MHz\nStop: {buffered_stop:.3f} MHz")
        elif self.showtime_tab_instance.last_selected_type == 'device':
            device_info = self.showtime_tab_instance.selected_device_info
            self.showtime_tab_instance.zone_zoom_label_left_var.set(f"Device: {device_info.get('NAME')}")
            self.showtime_tab_instance.zone_zoom_label_center_var.set(f"Name: {device_info.get('NAME')}")
            self.showtime_tab_instance.zone_zoom_label_right_var.set(f"Center: {device_info.get('CENTER'):.3f} MHz\nStart: {buffered_start:.3f} MHz\nStop: {buffered_stop:.3f} MHz")
        else: # All markers
            all_devices = self.showtime_tab_instance.zgd_frame._get_all_devices_in_zone(self.showtime_tab_instance.zgd_frame.structured_data, None)
            count = len(all_devices) if all_devices else 0
            self.showtime_tab_instance.zone_zoom_label_left_var.set("All Markers")
            self.showtime_tab_instance.zone_zoom_label_center_var.set(f"({count} Devices)")
            self.showtime_tab_instance.zone_zoom_label_right_var.set(f"Start: {buffered_start:.3f} MHz\nStop: {buffered_stop:.3f} MHz")

        debug_log(f"🖥️ ✅ UI synced successfully.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

    def _on_tab_selected(self, event):
        # [Handles the event when this tab is selected.]
        debug_log(f"🖥️ 🟢 Entering _on_tab_selected",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        self._sync_ui_from_state()
        debug_log(f"🖥️ 🟢 Exiting _on_tab_selected",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
