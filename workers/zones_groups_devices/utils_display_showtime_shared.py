# tabs/Markers/showtime/zones_groups_devices/utils_display_showtime_shared.py
#
# This file provides shared utility functions for the Showtime tab's UI and state management.
# It contains logic that is common to handling selections at the zone, group, and device level,
# including saving the entire Showtime state to the config file and updating the zone-zoom display.
# By centralizing this code, it prevents duplication and ensures consistent behavior across
# all selection handlers.
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
# REFACTORED: Consolidated all truly shared functions into this single file.
# FIXED: The save function has been made more robust with checks for None values.
# FIXED: All references to shared state variables are now robustly handled.
# FIXED: Moved `on_group_deselected` to this file to break a circular import.

import os
import inspect
import math
from tkinter import ttk
import pandas as pd
import numpy as np
import threading

from display.debug_logic import debug_log
from display.console_logic import console_log
from settings_and_config.config_manager_save import save_program_config

# Import shared utility functions
from Markers.showtime.controls.utils_showtime_zone_zoom import _buffer_start_stop_frequencies, set_span_to_group


# --- Versioning ---
w = 20250824
x_str = '110500'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 6
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"


def _save_showtime_state_to_config(showtime_tab):
    # [Internal function to save all Showtime state variables to the config.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️📝 Writing Showtime state to configuration.", file=current_file, version=current_version, function=current_function)
    
    # Check if the parent tab exists before trying to save its state
    if not hasattr(showtime_tab, 'app_instance'):
        debug_log("❌ Cannot save config. ShowtimeParentTab instance does not have 'app_instance' attribute.", file=current_file, version=current_version, function=current_function)
        return
        
    try:
        config = showtime_tab.app_instance.config
        
        if not config.has_section('MarkerTab'):
            config.add_section('MarkerTab')
            
        # Save all the state variables to the config file
        config.set('MarkerTab', 'span_hz', str(showtime_tab.span_var.get()))
        config.set('MarkerTab', 'rbw_hz', str(showtime_tab.rbw_var.get()))
        config.set('MarkerTab', 'trace_live', str(showtime_tab.trace_modes['live'].get()))
        config.set('MarkerTab', 'trace_max_hold', str(showtime_tab.trace_modes['max'].get()))
        config.set('MarkerTab', 'trace_min_hold', str(showtime_tab.trace_modes['min'].get()))
        config.set('MarkerTab', 'buffer_MHz', str(showtime_tab.buffer_var.get()))
        config.set('MarkerTab', 'poke_MHz', str(showtime_tab.poke_freq_var.get()))
        
        config.set('MarkerTab', 'buffered_start_var', str(showtime_tab.buffered_start_var.get()))
        config.set('MarkerTab', 'buffered_stop_var', str(showtime_tab.buffered_stop_var.get()))
        
        # Save selection state with robust checks
        config.set('MarkerTab', 'zone_selected', 'true' if showtime_tab.selected_zone else 'false')
        config.set('MarkerTab', 'zone_zoom_button_selected_name', showtime_tab.selected_zone if showtime_tab.selected_zone else '')
        
        config.set('MarkerTab', 'group_selected', 'true' if showtime_tab.selected_group else 'false')
        config.set('MarkerTab', 'group_zoom_button_selected', 'true' if showtime_tab.selected_group else 'false')

        # We need to save device info as a string or a set of strings, not a dictionary directly
        if showtime_tab.selected_device_info:
            config.set('MarkerTab', 'device_selected_name', str(showtime_tab.selected_device_info.get('NAME', '')))
            config.set('MarkerTab', 'device_selected_device_type', str(showtime_tab.selected_device_info.get('DEVICE', '')))
            config.set('MarkerTab', 'device_selected_center', str(showtime_tab.selected_device_info.get('CENTER', '')))
        else:
            config.set('MarkerTab', 'device_selected_name', '')
            config.set('MarkerTab', 'device_selected_device_type', '')
            config.set('MarkerTab', 'device_selected_center', '')
            
        # The info dictionaries need to be saved as strings.
        config.set('MarkerTab', 'zone_zoom_label_left_var', showtime_tab.zone_zoom_label_left_var.get())
        config.set('MarkerTab', 'zone_zoom_label_center_var', showtime_tab.zone_zoom_label_center_var.get())
        config.set('MarkerTab', 'zone_zoom_label_right_var', showtime_tab.zone_zoom_label_right_var.get())

        config.set('MarkerTab', 'zone_zoom_start', str(showtime_tab.buffered_start_var.get()))
        config.set('MarkerTab', 'zone_zoom_stop', str(showtime_tab.buffered_stop_var.get()))
        config.set('MarkerTab', 'group_zoom_start', str(showtime_tab.buffered_start_var.get()))
        config.set('MarkerTab', 'group_zoom_stop', str(showtime_tab.buffered_stop_var.get()))
        
        # FIXED: Corrected the way device counts are retrieved with safe defaults, preventing crashes if state is None
        zone_info = showtime_tab.selected_zone_info if hasattr(showtime_tab, 'selected_zone_info') and showtime_tab.selected_zone_info else {}
        group_info = showtime_tab.selected_group_info if hasattr(showtime_tab, 'selected_group_info') and showtime_tab.selected_group_info else {}
        
        config.set('MarkerTab', 'zone_device_count', str(zone_info.get('device_count', 0)))
        
        # FIXED: The previous line was incorrect, trying to get `keys()` from a potentially empty dict
        zone_groups = showtime_tab.structured_data.get(showtime_tab.selected_zone, {}) if showtime_tab.structured_data and showtime_tab.selected_zone else {}
        config.set('MarkerTab', 'zone_group_count', str(len(zone_groups.keys()) if showtime_tab.selected_zone else 0))

        config.set('MarkerTab', 'group_device_count', str(group_info.get('device_count', 0)))
        
        
        save_program_config(config=config,
                    file_path=showtime_tab.app_instance.CONFIG_FILE_PATH,
                    console_print_func=showtime_tab.console_print_func,
                    app_instance=showtime_tab.app_instance)
        
        debug_log(message=f"🛠️ ✅ Showtime state successfully written to config.", file=current_file, version=current_version, function=current_function)

    except Exception as e:
        console_log(f"❌ Error saving Showtime state to config: {e}. Fucking useless!", "ERROR")
        debug_log(message=f"🛠️❌ Failed to save Showtime state. Error: {e}", file=current_file, version=current_version, function=current_function)


def _update_zone_zoom_tab(zgd_frame_instance):
    # [A helper function to update the ZoneZoomTab with the current selection details.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
    
    showtime_tab = zgd_frame_instance.showtime_tab_instance
    try:
        # --- NEW LOGIC: Calculate buffered frequencies based on current selection state ---
        current_type = showtime_tab.last_selected_type
        buffer_MHz = float(showtime_tab.buffer_var.get())
        
        start_freq_MHz = 0.0
        stop_freq_MHz = 0.0
        
        if current_type == 'zone':
            zone_info = showtime_tab.selected_zone_info
            start_freq_MHz = zone_info.get('min_freq', 0.0)
            stop_freq_MHz = zone_info.get('max_freq', 0.0)
        elif current_type == 'group':
            group_info = showtime_tab.selected_group_info
            start_freq_MHz = group_info.get('min_freq', 0.0)
            stop_freq_MHz = group_info.get('max_freq', 0.0)
        elif current_type == 'device':
            device_info = showtime_tab.selected_device_info
            if device_info:
                center_freq = device_info.get('CENTER', 0.0)
                span_str = showtime_tab.span_var.get()
                if 'M' in span_str:
                    span_MHz = float(span_str.replace('M', ''))
                else:
                    span_MHz = float(span_str)
                # FIXED: Calculate start/stop correctly for a device without buffer
                start_freq_MHz = center_freq - (span_MHz / 2)
                stop_freq_MHz = center_freq + (span_MHz / 2)
        else: # All markers
            all_devices = zgd_frame_instance._get_all_devices_in_zone(zgd_frame_instance.structured_data, None)
            freqs = [float(d['CENTER']) for d in all_devices if isinstance(d.get('CENTER'), (int, float))]
            if freqs:
                start_freq_MHz = min(freqs)
                stop_freq_MHz = max(freqs)

        # Calculate and write buffered frequencies to state. This fixes the main bug.
        buffered_start_freq_MHz, buffered_stop_freq_MHz = _buffer_start_stop_frequencies(start_freq_MHz, stop_freq_MHz, buffer_MHz)
        debug_log(message=f"🛠️📝 Writing state: buffered_start_var = {buffered_start_freq_MHz}, buffered_stop_var = {buffered_stop_freq_MHz}", file=current_file, version=current_version, function=current_function)
        showtime_tab.buffered_start_var.set(buffered_start_freq_MHz)
        showtime_tab.buffered_stop_var.set(buffered_stop_freq_MHz)

        # --- Update Labels based on the correct values from state ---
        buffered_start_freq = showtime_tab.buffered_start_var.get()
        buffered_stop_freq = showtime_tab.buffered_stop_var.get()

        if current_type == 'zone':
            zone_info = showtime_tab.selected_zone_info
            count = zone_info.get('device_count', 0)
            
            debug_log(message=f"🛠️📝 Writing to state: Updating zone_zoom labels.", file=current_file, version=current_version, function=current_function)
            showtime_tab.zone_zoom_label_left_var.set(f"Zone ({count} Devices)")
            showtime_tab.zone_zoom_label_center_var.set(f"Name: {showtime_tab.selected_zone}")
            showtime_tab.zone_zoom_label_right_var.set(f"Start: {buffered_start_freq:.3f} MHz\nStop: {buffered_stop_freq:.3f} MHz")
        elif current_type == 'group':
            group_info = showtime_tab.selected_group_info
            count = group_info.get('device_count', 0)
            
            debug_log(message=f"🛠️📝 Writing to state: Updating zone_zoom labels.", file=current_file, version=current_version, function=current_function)
            showtime_tab.zone_zoom_label_left_var.set(f"Group ({count} Devices)")
            showtime_tab.zone_zoom_label_center_var.set(f"Name: {showtime_tab.selected_group}")
            showtime_tab.zone_zoom_label_right_var.set(f"Start: {buffered_start_freq:.3f} MHz\nStop: {buffered_stop_freq:.3f} MHz")
        elif current_type == 'device':
            device_info = showtime_tab.selected_device_info
            if device_info:
                debug_log(message=f"🛠️📝 Writing to state: Updating zone_zoom labels.", file=current_file, version=current_version, function=current_function)
                showtime_tab.zone_zoom_label_left_var.set(f"Device: {device_info.get('NAME')}")
                showtime_tab.zone_zoom_label_center_var.set(f"Name: {device_info.get('NAME')}")
                showtime_tab.zone_zoom_label_right_var.set(f"Center: {device_info.get('CENTER'):.3f} MHz\nStart: {buffered_start_freq:.3f} MHz\nStop: {buffered_stop_freq:.3f} MHz")
            else:
                debug_log(message=f"🛠️📝 Writing to state: No device info available, clearing labels.", file=current_file, version=current_version, function=current_function)
                showtime_tab.zone_zoom_label_left_var.set("No Device Selected")
                showtime_tab.zone_zoom_label_center_var.set("N/A")
                showtime_tab.zone_zoom_label_right_var.set("N/A")
        else: # All markers
            all_devices = zgd_frame_instance._get_all_devices_in_zone(zgd_frame_instance.structured_data, None)
            count = len(all_devices) if all_devices else 0
            
            debug_log(message=f"🛠️📝 Writing to state: Updating zone_zoom labels.", file=current_file, version=current_version, function=current_function)
            showtime_tab.zone_zoom_label_left_var.set("All Markers")
            showtime_tab.zone_zoom_label_center_var.set(f"({count} Devices)")
            showtime_tab.zone_zoom_label_right_var.set(f"Start: {buffered_start_freq:.3f} MHz\nStop: {buffered_stop_freq:.3f} MHz")

        showtime_tab.controls_frame.zone_zoom_tab._sync_ui_from_state()
        
        _save_showtime_state_to_config(showtime_tab)

    except Exception as e:
        debug_log(message=f"🛠️❌ Error in _update_zone_zoom_tab: {e}", file=current_file, version=current_version, function=current_function)
    
    debug_log(message=f"🛠️🟢 Exiting {current_function}", file=current_file, version=current_version, function=current_function)

def get_current_view_details(zgd_frame_instance):
    # [Returns a dictionary with the start, stop, center, and span frequencies for the current view.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)

    start_freq = None
    stop_freq = None
    
    # Access state from the parent ShowtimeTab instance
    showtime_tab = zgd_frame_instance.showtime_tab_instance

    if showtime_tab.selected_device_info:
        center_freq = showtime_tab.selected_device_info.get('CENTER')
        if center_freq:
            # Check for 'M' in span_var and convert appropriately
            span_str = showtime_tab.span_var.get()
            if 'M' in span_str:
                span = float(span_str.replace('M', ''))
            else:
                span = float(span_str)
            start_freq = center_freq - (span / 2)
            stop_freq = center_freq + (span / 2)
    
    elif showtime_tab.selected_zone or showtime_tab.selected_group:
        devices = []
        if showtime_tab.selected_group:
            devices = zgd_frame_instance.structured_data.get(showtime_tab.selected_zone, {}).get(showtime_tab.selected_group, [])
        elif showtime_tab.selected_zone:
            for group_name in showtime_tab.structured_data.get(showtime_tab.selected_zone, {}).keys():
                devices.extend(showtime_tab.structured_data.get(showtime_tab.selected_zone, {}).get(group_name, []))
        
        freqs = [float(d.get('CENTER')) for d in devices if d.get('CENTER') and isinstance(d.get('CENTER'), (int, float))]
        if freqs:
            start_freq = min(freqs)
            stop_freq = max(freqs)
    
    else:
        all_devices = zgd_frame_instance._get_all_devices_in_zone(zgd_frame_instance.structured_data, None)
        freqs = [float(d.get('CENTER')) for d in all_devices if isinstance(d.get('CENTER'), (int, float))]
        if freqs:
            start_freq = min(freqs)
            stop_freq = max(freqs)
            
    if start_freq is not None and stop_freq is not None:
        center = (start_freq + stop_freq) / 2
        span = stop_freq - start_freq
        return {"start": start_freq, "stop": stop_freq, "center": center, "span": span}
    
    debug_log(message=f"🛠️🟢 Exiting {current_function}", file=current_file, version=current_version, function=current_function)
    return None