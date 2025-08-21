# tabs/Markers/showtime/zones_groups_devices/utils_display_showtime_groups.py
#
# This module provides the backend logic for handling Group-level button clicks.
# It manages the selection and deselection of groups, handles single-device
# auto-selection, and delegates to shared utility functions for saving
# the state and updating the instrument's view.
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
# Version 20250824.110500.6
# REFACTORED: Extracted group-specific logic from the main utility file.
# UPDATED: Corrected imports to resolve circular dependencies.
# FIXED: The logic for selecting a group now correctly checks for single devices and auto-selects them.
# FIXED: Moved `on_group_deselected` to the shared utility file to break a circular import.

import os
import inspect
import math
from tkinter import ttk
import pandas as pd
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log

# Import shared utility functions
from tabs.Markers.showtime.controls.utils_showtime_zone_zoom import set_span_to_group
from .utils_display_showtime_shared import _update_zone_zoom_tab, _save_showtime_state_to_config


# --- Versioning ---
w = 20250824
x_str = '110500'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 6
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"


def on_group_selected(zgd_frame_instance, group_name):
    
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️🟢 Entering {current_function} for group: {group_name}", file=current_file, version=current_version, function=current_function)

    showtime_tab = zgd_frame_instance.showtime_tab_instance
    devices_in_group = zgd_frame_instance.structured_data.get(showtime_tab.selected_zone, {}).get(group_name, [])

    if len(devices_in_group) == 1:
        console_log(f"EVENT: Group '{group_name}' contains one device. Auto-selecting device...", "INFO")
        # 📝 Write Data: Update selected state variables.
        debug_log(message=f"🛠️📝 Writing to state: Updating selected group and resetting device.", file=current_file, version=current_version, function=current_function)
        showtime_tab.selected_group = group_name
        zgd_frame_instance._make_device_buttons()
        # Lazily import on_device_selected to break circular import
        from .utils_display_showtime_devices import on_device_selected 
        on_device_selected(zgd_frame_instance, devices_in_group[0])
        
        for widget in zgd_frame_instance.groups_frame.winfo_children():
            if widget.cget("text") == group_name:
                if zgd_frame_instance.active_group_button and zgd_frame_instance.active_group_button.winfo_exists():
                    zgd_frame_instance.active_group_button.config(style='ControlButton.Inactive.TButton')
                widget.config(style='ControlButton.Active.TButton')
                zgd_frame_instance.active_group_button = widget
                break
        return

    if showtime_tab.selected_group == group_name:
        console_log(f"EVENT: Group '{group_name}' deselected. Reverting to show all devices in Zone '{showtime_tab.selected_zone}'.", "INFO")
        on_group_deselected(zgd_frame_instance)
        return

    for widget in zgd_frame_instance.groups_frame.winfo_children():
        if widget.cget("text") == group_name:
            selected_button = widget
            break
    else:
        selected_button = None

    console_log(f"EVENT: Group '{group_name}' selected in Zone '{showtime_tab.selected_zone}'. Loading devices... ⚙️")
    if zgd_frame_instance.active_group_button and zgd_frame_instance.active_group_button.winfo_exists():
        zgd_frame_instance.active_group_button.config(style='ControlButton.Inactive.TButton')

    # 📝 Write Data: Update selected state variables.
    debug_log(message=f"🛠️📝 Writing to state: Updating selected group and resetting device.", file=current_file, version=current_version, function=current_function)
    showtime_tab.active_device_button = None
    showtime_tab.selected_device_info = None
    showtime_tab.selected_group = group_name
    showtime_tab.last_selected_type = 'group'

    # NEW: Calculate and store group information in state
    freqs = [float(d['CENTER']) for d in devices_in_group if isinstance(d.get('CENTER'), (int, float))]
    
    # FIXED: Check if freqs is not empty before calling min/max
    if freqs:
        min_freq = min(freqs)
        max_freq = max(freqs)
    else:
        min_freq = 0.0
        max_freq = 0.0
        
    showtime_tab.selected_group_info = {
        'min_freq': min_freq,
        'max_freq': max_freq,
        'device_count': len(devices_in_group)
    }
    
    debug_log(message=f"🛠️📦 Stored group info in state: {showtime_tab.selected_group_info}", file=current_file, version=current_version, function=current_function)

    if selected_button:
        selected_button.config(style='ControlButton.Active.TButton')
        zgd_frame_instance.active_group_button = selected_button
    
    devices_in_group_list = zgd_frame_instance.structured_data.get(showtime_tab.selected_zone, {}).get(group_name, [])
    zgd_frame_instance._get_min_max_freq_and_update_title(frame_widget=zgd_frame_instance.groups_frame, devices=devices_in_group_list, title_prefix=f"Group '{group_name}'")

    zgd_frame_instance._make_device_buttons()
    zgd_frame_instance.canvas.yview_moveto(0)
    
    # FIXED: Call the set_span_to_group utility function here to trigger the update
    from tabs.Markers.showtime.controls.utils_showtime_zone_zoom import set_span_to_group
    set_span_to_group(showtime_tab_instance=showtime_tab, zone_zoom_tab=showtime_tab.controls_frame.zone_zoom_tab)
    _save_showtime_state_to_config(showtime_tab)

    debug_log(message=f"🛠️🟢 Exiting {current_function}", file=current_file, version=current_version, function=current_function)

def on_group_deselected(zgd_frame_instance):
    # [Handles the logic for when a group is deselected.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
    
    showtime_tab = zgd_frame_instance.showtime_tab_instance

    if zgd_frame_instance.active_group_button and zgd_frame_instance.active_group_button.winfo_exists():
        zgd_frame_instance.active_group_button.config(style='ControlButton.Inactive.TButton')
        zgd_frame_instance.active_group_button = None
        
    # 📝 Write Data: Reset selected state variables.
    debug_log(message=f"🛠️📝 Writing to state: Resetting selected group and related info.", file=current_file, version=current_version, function=current_function)
    showtime_tab.selected_group = None
    showtime_tab.last_selected_type = 'zone'
    showtime_tab.selected_group_info = {
        'min_freq': 0.0,
        'max_freq': 0.0,
        'device_count': 0
    }
    zgd_frame_instance._make_device_buttons()
    
    _update_zone_zoom_tab(zgd_frame_instance)
    _save_showtime_state_to_config(showtime_tab)
    
    if hasattr(showtime_tab.controls_frame, 'switch_to_tab'):
        showtime_tab.controls_frame.switch_to_tab("Zone Zoom")
        
    debug_log(message=f"🛠️🟢 Exiting {current_function}", file=current_file, version=current_version, function=current_function)

def no_zone_grou_device_selected(zgd_frame_instance):
    # [Handles the logic for when no zone, group, or device is selected.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
    
    console_log(f"EVENT: No zone, group, or device selected. Displaying all devices. ")
    
    # Access and update parent's state variables directly
    showtime_tab = zgd_frame_instance.showtime_tab_instance
    # 📝 Write Data: Reset selected state variables.
    debug_log(message=f"🛠️📝 Writing to state: Resetting selected state variables.", file=current_file, version=current_version, function=current_function)
    showtime_tab.selected_zone = None
    showtime_tab.selected_group = None
    showtime_tab.selected_device_info = None
    showtime_tab.last_selected_type = None

    if zgd_frame_instance.active_zone_button and zgd_frame_instance.active_zone_button.winfo_exists():
        zgd_frame_instance.active_zone_button.config(style='ControlButton.Inactive.TButton')
        zgd_frame_instance.active_zone_button = None
        
    if zgd_frame_instance.active_group_button and zgd_frame_instance.active_group_button.winfo_exists():
        zgd_frame_instance.active_group_button.config(style='ControlButton.Inactive.TButton')
        zgd_frame_instance.active_group_button = None
        
    if showtime_tab.active_device_button and showtime_tab.active_device_button.winfo_exists():
        showtime_tab.active_device_button.config(style='DeviceButton.Inactive.TButton')
    showtime_tab.active_device_button = None
    
    # FIXED: Revert the view to the parent group when a device is deselected.
    set_span_to_group(showtime_tab_instance=showtime_tab, zone_zoom_tab=showtime_tab.controls_frame.zone_zoom_tab)
    _update_zone_zoom_tab(zgd_frame_instance)
    _save_showtime_state_to_config(showtime_tab)
    
    if hasattr(showtime_tab.controls_frame, 'switch_to_tab'):
        showtime_tab.controls_frame.switch_to_tab("Zone Zoom")
        
    debug_log(message=f"🛠️🟢 Exiting {current_function}", file=current_file, version=current_version, function=current_function)