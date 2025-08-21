# tabs/Markers/showtime/zones_groups_devices/utils_display_showtime_zones.py
#
# This module provides the backend logic for handling Zone-level button clicks.
# It manages the selection and deselection of zones, updates the UI to reflect
# the current state, and delegates to shared utility functions for saving
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
# REFACTORED: Extracted zone-specific logic from the main utility file.
# FIXED: The logic for selecting and deselecting a zone is now self-contained.
# UPDATED: Corrected import statements to resolve circular dependencies.
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
from tabs.Markers.showtime.controls.utils_showtime_zone_zoom import set_span_to_zone
from .utils_display_showtime_shared import no_zone_grou_device_selected, _update_zone_zoom_tab, _save_showtime_state_to_config
from .utils_display_showtime_shared import on_group_deselected


# --- Versioning ---
w = 20250824
x_str = '110500'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 6
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"


def on_zone_selected(zgd_frame_instance, zone_name):
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️🟢 Entering {current_function} for zone: {zone_name}", file=current_file, version=current_version, function=current_function)

    showtime_tab = zgd_frame_instance.showtime_tab_instance

    for widget in zgd_frame_instance.zones_frame.winfo_children():
        if widget.cget("text") == zone_name:
            selected_button = widget
            break
    else:
        selected_button = None

    if showtime_tab.selected_zone == zone_name:
        no_zone_grou_device_selected(zgd_frame_instance)
    else:
        console_log(f"EVENT: Zone '{zone_name}' selected. Loading groups and devices... 🚀")
        if zgd_frame_instance.active_zone_button and zgd_frame_instance.active_zone_button.winfo_exists():
            zgd_frame_instance.active_zone_button.config(style='ControlButton.Inactive.TButton')
        if zgd_frame_instance.active_group_button and zgd_frame_instance.active_group_button.winfo_exists():
            zgd_frame_instance.active_group_button.config(style='ControlButton.Inactive.TButton')
            zgd_frame_instance.active_group_button = None
        
        # 📝 Write Data: Update selected state variables.
        debug_log(message=f"🛠️📝 Writing to state: Updating selected zone and resetting group/device.", file=current_file, version=current_version, function=current_function)
        showtime_tab.active_device_button = None
        showtime_tab.selected_device_info = None
        showtime_tab.selected_zone = zone_name
        showtime_tab.selected_group = None
        showtime_tab.last_selected_type = 'zone'

        # NEW: Calculate and store zone information in state
        all_devices_in_zone = zgd_frame_instance._get_all_devices_in_zone(zgd_frame_instance.structured_data, showtime_tab.selected_zone)
        freqs = [float(d['CENTER']) for d in all_devices_in_zone if isinstance(d.get('CENTER'), (int, float))]
        
        # FIXED: Check if freqs is not empty before calling min/max
        if freqs:
            min_freq = min(freqs)
            max_freq = max(freqs)
        else:
            min_freq = 0.0
            max_freq = 0.0

        showtime_tab.selected_zone_info = {
            'min_freq': min_freq,
            'max_freq': max_freq,
            'device_count': len(all_devices_in_zone)
        }
        
        debug_log(message=f"🛠️📦 Stored zone info in state: {showtime_tab.selected_zone_info}", file=current_file, version=current_version, function=current_function)

        if selected_button:
            selected_button.config(style='ControlButton.Active.TButton')
            zgd_frame_instance.active_zone_button = selected_button
        
        zgd_frame_instance._get_min_max_freq_and_update_title(frame_widget=zgd_frame_instance.zones_frame, devices=all_devices_in_zone, title_prefix=f"Zone '{zone_name}'")

        zgd_frame_instance._get_min_max_freq_and_update_title(frame_widget=zgd_frame_instance.groups_frame, devices=[], title_prefix=f"Groups in Zone '{showtime_tab.selected_zone}'" if showtime_tab.selected_zone else "Groups")

        zgd_frame_instance._make_group_buttons()
        zgd_frame_instance.canvas.yview_moveto(0)
        
        # FIXED: Call the set_span_to_zone utility function here to trigger the update
        set_span_to_zone(showtime_tab_instance=showtime_tab, zone_zoom_tab=showtime_tab.controls_frame.zone_zoom_tab)
        _save_showtime_state_to_config(showtime_tab)

    debug_log(message=f"🛠️🟢 Exiting {current_function}", file=current_file, version=current_version, function=current_function)

