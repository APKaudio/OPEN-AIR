# tabs/Markers/showtime/zones_groups_devices/utils_display_showtime_devices.py
#
# This module provides the backend logic for handling Device-level button clicks.
# It manages the selection and deselection of devices, updates the UI to reflect
# the current state, and communicates directly with the instrument to set the
# center frequency and span. It delegates to shared utility functions for saving
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
# REFACTORED: Extracted device-specific logic from the main utility file.
# UPDATED: Corrected imports to resolve circular dependencies.
# FIXED: The logic for selecting a device now correctly sets the instrument's
#        center frequency and span based on the device's frequency.

import os
import inspect
import pandas as pd
import numpy as np
import math

from display.debug_logic import debug_log
from display.console_logic import console_log

# Import shared utility functions
from Markers.showtime.controls.utils_showtime_zone_zoom import set_span_to_group
from .utils_display_showtime_shared import _update_zone_zoom_tab, _save_showtime_state_to_config
from yak.utils_yakbeg_handler import handle_freq_center_span_beg


# --- Versioning ---
w = 20250824
x_str = '110500'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 6
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"


def on_device_deselected(zgd_frame_instance):
    # [Handles the logic for when a device is deselected.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
    
    showtime_tab = zgd_frame_instance.showtime_tab_instance
    # 📝 Write Data: Reset selected state variables.
    debug_log(message=f"🛠️📝 Writing to state: Resetting selected device.", file=current_file, version=current_version, function=current_function)
    showtime_tab.selected_device_info = None
    showtime_tab.last_selected_type = 'group'

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


def on_device_selected(zgd_frame_instance, device_info):
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️🟢 Entering {current_function} for device object: {device_info}", file=current_file, version=current_version, function=current_function)

    showtime_tab = zgd_frame_instance.showtime_tab_instance
    device_name = device_info.get('NAME', 'N/A')

    if isinstance(device_name, float) and np.isnan(device_name):
        device_name = 'nan'
    
    if showtime_tab.selected_device_info and id(showtime_tab.selected_device_info) == id(device_info):
        console_log(f"EVENT: Device '{device_name}' deselected.")
        from .utils_display_showtime_groups import on_group_deselected # Correctly moved here
        on_device_deselected(zgd_frame_instance)
        debug_log(message=f"🛠️🟢 Exiting {current_function} after deselecting device.", file=current_file, version=current_version, function=current_function)
        return

    # 📝 Write Data: Update selected state variables.
    debug_log(message=f"🛠️📝 Writing to state: Storing selected device info.", file=current_file, version=current_version, function=current_function)
    showtime_tab.selected_device_info = device_info
    showtime_tab.last_selected_type = 'device'

    selected_button = showtime_tab.device_buttons.get(id(device_info))
    
    if showtime_tab.active_device_button and showtime_tab.active_device_button.winfo_exists():
        showtime_tab.active_device_button.config(style='DeviceButton.Inactive.TButton')

    if selected_button:
        selected_button.config(style='DeviceButton.Active.TButton')
        showtime_tab.active_device_button = selected_button
        console_log(f"✅ EVENT: Device '{device_name}' selected. 🎵")
    
    if device_info:
        freq = device_info.get('CENTER', 'N/A')
        if freq != 'N/A':
            zgd_frame_instance.devices_outer_frame.config(text=f"Devices - {device_name} - {freq:.3f} MHz")
            console_log(f"✅ Displaying device '{device_name}' at frequency {freq:.3f} MHz.")
            if hasattr(showtime_tab.controls_frame, 'switch_to_tab'):
                showtime_tab.controls_frame.switch_to_tab("Span")
        else:
            zgd_frame_instance.devices_outer_frame.config(text=f"Devices - {device_name} - N/A")
            console_log(f"⚠️ Device '{device_name}' has no valid frequency.")
    else:
        zgd_frame_instance.devices_outer_frame.config(text="Devices")
        console_log(f"❌ Device info not found. The device has vanished into thin air!")

    _update_zone_zoom_tab(zgd_frame_instance)
    
    # NEW: Set the instrument's center frequency and span based on the state.
    center_freq_MHz = device_info.get('CENTER')
    # 📖 Read Data: Get the current span from the state.
    span_str = showtime_tab.span_var.get()
    if 'M' in span_str:
        span_MHz = float(span_str.replace('M', ''))
    else:
        span_MHz = float(span_str)

    if center_freq_MHz is not None and isinstance(center_freq_MHz, (float, int)):
        debug_log(message=f"🛠️📤 Outbound: Setting instrument center frequency to {center_freq_MHz} MHz and span to {span_MHz} MHz.", file=current_file, version=current_version, function=current_function)
        
        # Convert to Hz for the handler function
        center_freq_hz = int(center_freq_MHz * 1_000_000)
        span_hz = int(span_MHz * 1_000_000)
        
        handle_freq_center_span_beg(app_instance=showtime_tab.app_instance, 
                                 center_freq=center_freq_hz, 
                                 span_freq=span_hz,
                                 console_print_func=showtime_tab.console_print_func)
    else:
        console_log("❌ Cannot set instrument center frequency. Invalid device center frequency.")
        debug_log(message=f"🛠️❌ Invalid center frequency for device: {center_freq_MHz}. Cannot set instrument.", 
                  file=current_file, 
                  version=current_version, 
                  function=current_function)

    _save_showtime_state_to_config(showtime_tab)

    debug_log(message=f"🛠️🟢 Exiting {current_function}", file=current_file, version=current_version, function=current_function)