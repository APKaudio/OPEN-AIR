# tabs/Markers/showtime/zones_groups_devices/utils_display_showtime_all.py
#
# This module provides the backend logic for handling the "All Markers" view.
# It manages the selection of all markers and delegates to shared utility
# functions for updating the display and instrument's span.
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
# REFACTORED: Created a new file for the "All Markers" view to improve modularity.
# UPDATED: Imports now point to the new shared utility file.
# FIXED: The function now correctly gets all devices and calls the appropriate
#        span utility function.

import os
import inspect
from tkinter import ttk
import pandas as pd
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log

# Import shared utility functions
from Markers.showtime.controls.utils_showtime_zone_zoom import set_span_to_all_markers, set_span_to_group

from .utils_display_showtime_shared import _update_zone_zoom_tab, _save_showtime_state_to_config


# --- Versioning ---
w = 20250824
x_str = '110500'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 6
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"


def on_all_markers_selected(zgd_frame_instance):
    # [Handles the logic for selecting and viewing all markers.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)

    showtime_tab = zgd_frame_instance.showtime_tab_instance
    
    console_log(f"EVENT: All markers selected. Displaying all devices...", "INFO")
    
    # Reset all active selections
    if zgd_frame_instance.active_zone_button and zgd_frame_instance.active_zone_button.winfo_exists():
        zgd_frame_instance.active_zone_button.config(style='ControlButton.Inactive.TButton')
        zgd_frame_instance.active_zone_button = None
    if zgd_frame_instance.active_group_button and zgd_frame_instance.active_group_button.winfo_exists():
        zgd_frame_instance.active_group_button.config(style='ControlButton.Inactive.TButton')
        zgd_frame_instance.active_group_button = None
    if showtime_tab.active_device_button and showtime_tab.active_device_button.winfo_exists():
        showtime_tab.active_device_button.config(style='DeviceButton.Inactive.TButton')
    showtime_tab.active_device_button = None
    
    # 📝 Write Data: Update selected state variables.
    debug_log(message=f"🛠️📝 Writing to state: Setting selection to all markers.", file=current_file, version=current_version, function=current_function)
    showtime_tab.selected_zone = None
    showtime_tab.selected_group = None
    showtime_tab.selected_device_info = None
    showtime_tab.last_selected_type = 'all markers'
    
    all_devices = zgd_frame_instance._get_all_devices_in_zone(zgd_frame_instance.structured_data, None)
    
    if all_devices:
        freqs = [float(d['CENTER']) for d in all_devices if isinstance(d.get('CENTER'), (int, float))]
        min_freq = min(freqs) if freqs else 0.0
        max_freq = max(freqs) if freqs else 0.0
        device_count = len(all_devices)

        showtime_tab.selected_zone_info = {
            'min_freq': min_freq,
            'max_freq': max_freq,
            'device_count': device_count
        }
        showtime_tab.selected_group_info = {}
        
        zgd_frame_instance._get_min_max_freq_and_update_title(frame_widget=zgd_frame_instance.zones_frame, devices=all_devices, title_prefix="All Devices")
        zgd_frame_instance._make_group_buttons()
        zgd_frame_instance._make_device_buttons()
        
    # Call the set_span_to_all_markers utility function to trigger the update
    from Markers.showtime.controls.utils_showtime_zone_zoom import set_span_to_all_markers
    set_span_to_all_markers(showtime_tab_instance=showtime_tab, zone_zoom_tab=showtime_tab.controls_frame.zone_zoom_tab)

    _save_showtime_state_to_config(showtime_tab)

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
  