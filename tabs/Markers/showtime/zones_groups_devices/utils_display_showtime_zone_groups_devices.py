# tabs/Markers/showtime/zones_groups_devices/utils_display_showtime_zone_groups_devices.py
#
# This module provides the backend logic for the ZoneGroupsDevicesFrame.
# It contains the functions that handle user interactions (button clicks)
# and manage the state of the UI based on those selections.
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
# Version 20250822.103500.5
# FIXED: on_device_deselected now correctly reverts the view to the parent group.
# FIXED: The _update_zone_zoom_tab function now correctly calculates the buffered
#        start and stop frequencies for a device selection, resolving a critical bug
#        that caused negative frequencies to be displayed.
# UPDATED: All debug logs now include the correct emoji prefixes.
# UPDATED: Versioning and file header adhere to new standards.

import os
import inspect
import math
from tkinter import ttk
import pandas as pd
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log

# NEW: Import the required setting handler functions
from yak.utils_yak_setting_handler import set_center_frequency
from yak.utils_yakbeg_handler import handle_freq_start_stop_beg, handle_freq_center_span_beg
from tabs.Markers.showtime.controls.utils_showtime_zone_zoom import _buffer_start_stop_frequencies, set_span_to_group


# --- Versioning ---
w = 20250822
x_str = '103500'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 5
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"


def _update_zone_zoom_tab(zgd_frame_instance):
    # [A helper function to update the ZoneZoomTab with the current selection details.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
    
    showtime_tab = zgd_frame_instance.showtime_tab_instance
    try:
        # --- NEW LOGIC: Calculate buffered frequencies based on current selection state ---
        current_type = showtime_tab.shared_state.last_selected_type
        buffer_mhz = float(showtime_tab.shared_state.buffer_var.get())
        
        start_freq_mhz = 0.0
        stop_freq_mhz = 0.0
        
        if current_type == 'zone':
            zone_info = showtime_tab.shared_state.selected_zone_info
            start_freq_mhz = zone_info.get('min_freq', 0.0)
            stop_freq_mhz = zone_info.get('max_freq', 0.0)
        elif current_type == 'group':
            group_info = showtime_tab.shared_state.selected_group_info
            start_freq_mhz = group_info.get('min_freq', 0.0)
            stop_freq_mhz = group_info.get('max_freq', 0.0)
        elif current_type == 'device':
            device_info = showtime_tab.shared_state.selected_device_info
            if device_info:
                center_freq = device_info.get('CENTER', 0.0)
                span_str = showtime_tab.shared_state.span_var.get()
                if 'M' in span_str:
                    span_mhz = float(span_str.replace('M', ''))
                else:
                    span_mhz = float(span_str)
                # FIXED: Calculate start/stop correctly for a device without buffer
                start_freq_mhz = center_freq - (span_mhz / 2)
                stop_freq_mhz = center_freq + (span_mhz / 2)
        else: # All markers
            all_devices = zgd_frame_instance._get_all_devices_in_zone(zgd_frame_instance.structured_data, None)
            freqs = [float(d['CENTER']) for d in all_devices if isinstance(d.get('CENTER'), (int, float))]
            if freqs:
                start_freq_mhz = min(freqs)
                stop_freq_mhz = max(freqs)

        # Calculate and write buffered frequencies to shared state. This fixes the main bug.
        buffered_start_freq_mhz, buffered_stop_freq_mhz = _buffer_start_stop_frequencies(start_freq_mhz, stop_freq_mhz, buffer_mhz)
        debug_log(message=f"🛠️📝 Writing shared state: buffered_start_var = {buffered_start_freq_mhz}, buffered_stop_var = {buffered_stop_freq_mhz}", file=current_file, version=current_version, function=current_function)
        showtime_tab.shared_state.buffered_start_var.set(buffered_start_freq_mhz)
        showtime_tab.shared_state.buffered_stop_var.set(buffered_stop_freq_mhz)

        # --- Update Labels based on the correct values from shared state ---
        buffered_start_freq = showtime_tab.shared_state.buffered_start_var.get()
        buffered_stop_freq = showtime_tab.shared_state.buffered_stop_var.get()

        if current_type == 'zone':
            zone_info = showtime_tab.shared_state.selected_zone_info
            count = zone_info.get('device_count', 0)
            
            debug_log(message=f"🛠️📝 Writing to shared state: Updating zone_zoom labels.", file=current_file, version=current_version, function=current_function)
            showtime_tab.shared_state.zone_zoom_label_left_var.set(f"Zone ({count} Devices)")
            showtime_tab.shared_state.zone_zoom_label_center_var.set(f"Name: {showtime_tab.shared_state.selected_zone}")
            showtime_tab.shared_state.zone_zoom_label_right_var.set(f"Start: {buffered_start_freq:.3f} MHz\nStop: {buffered_stop_freq:.3f} MHz")
        elif current_type == 'group':
            group_info = showtime_tab.shared_state.selected_group_info
            count = group_info.get('device_count', 0)
            
            debug_log(message=f"🛠️📝 Writing to shared state: Updating zone_zoom labels.", file=current_file, version=current_version, function=current_function)
            showtime_tab.shared_state.zone_zoom_label_left_var.set(f"Group ({count} Devices)")
            showtime_tab.shared_state.zone_zoom_label_center_var.set(f"Name: {showtime_tab.shared_state.selected_group}")
            showtime_tab.shared_state.zone_zoom_label_right_var.set(f"Start: {buffered_start_freq:.3f} MHz\nStop: {buffered_stop_freq:.3f} MHz")
        elif current_type == 'device':
            device_info = showtime_tab.shared_state.selected_device_info
            if device_info:
                debug_log(message=f"🛠️📝 Writing to shared state: Updating zone_zoom labels.", file=current_file, version=current_version, function=current_function)
                showtime_tab.shared_state.zone_zoom_label_left_var.set(f"Device: {device_info.get('NAME')}")
                showtime_tab.shared_state.zone_zoom_label_center_var.set(f"Name: {device_info.get('NAME')}")
                showtime_tab.shared_state.zone_zoom_label_right_var.set(f"Center: {device_info.get('CENTER'):.3f} MHz\nStart: {buffered_start_freq:.3f} MHz\nStop: {buffered_stop_freq:.3f} MHz")
            else:
                debug_log(message=f"🛠️📝 Writing to shared state: No device info available, clearing labels.", file=current_file, version=current_version, function=current_function)
                showtime_tab.shared_state.zone_zoom_label_left_var.set("No Device Selected")
                showtime_tab.shared_state.zone_zoom_label_center_var.set("N/A")
                showtime_tab.shared_state.zone_zoom_label_right_var.set("N/A")
        else: # All markers
            all_devices = zgd_frame_instance._get_all_devices_in_zone(zgd_frame_instance.structured_data, None)
            count = len(all_devices) if all_devices else 0
            
            debug_log(message=f"🛠️📝 Writing to shared state: Updating zone_zoom labels.", file=current_file, version=current_version, function=current_function)
            showtime_tab.shared_state.zone_zoom_label_left_var.set("All Markers")
            showtime_tab.shared_state.zone_zoom_label_center_var.set(f"({count} Devices)")
            showtime_tab.shared_state.zone_zoom_label_right_var.set(f"Start: {buffered_start_freq:.3f} MHz\nStop: {buffered_stop_freq:.3f} MHz")

        showtime_tab.controls_frame.zone_zoom_tab._sync_ui_from_state()

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

    if showtime_tab.shared_state.selected_device_info:
        center_freq = showtime_tab.shared_state.selected_device_info.get('CENTER')
        if center_freq:
            # Check for 'M' in span_var and convert appropriately
            span_str = showtime_tab.shared_state.span_var.get()
            if 'M' in span_str:
                span = float(span_str.replace('M', ''))
            else:
                span = float(span_str)
            start_freq = center_freq - (span / 2)
            stop_freq = center_freq + (span / 2)
    
    elif showtime_tab.shared_state.selected_zone or showtime_tab.shared_state.selected_group:
        devices = []
        if showtime_tab.shared_state.selected_group:
            devices = zgd_frame_instance.structured_data.get(showtime_tab.shared_state.selected_zone, {}).get(showtime_tab.shared_state.selected_group, [])
        elif showtime_tab.shared_state.selected_zone:
            for group_name in zgd_frame_instance.structured_data.get(showtime_tab.shared_state.selected_zone, {}).keys():
                devices.extend(zgd_frame_instance.structured_data.get(showtime_tab.shared_state.selected_zone, {}).get(group_name, []))
        
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

def no_zone_grou_device_selected(zgd_frame_instance):
    # [Handles the logic for when no zone, group, or device is selected.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
    
    console_log(f"EVENT: No zone, group, or device selected. Displaying all devices. 🔍")
    
    # Access and update parent's state variables directly
    showtime_tab = zgd_frame_instance.showtime_tab_instance
    # 📝 Write Data: Reset selected state variables.
    debug_log(message=f"🛠️📝 Writing to shared state: Resetting selected state variables.", file=current_file, version=current_version, function=current_function)
    showtime_tab.shared_state.selected_zone = None
    showtime_tab.shared_state.selected_group = None
    showtime_tab.shared_state.selected_device_info = None
    showtime_tab.shared_state.last_selected_type = None

    if zgd_frame_instance.active_zone_button and zgd_frame_instance.active_zone_button.winfo_exists():
        zgd_frame_instance.active_zone_button.config(style='ControlButton.Inactive.TButton')
        zgd_frame_instance.active_zone_button = None
        
    if zgd_frame_instance.active_group_button and zgd_frame_instance.active_group_button.winfo_exists():
        zgd_frame_instance.active_group_button.config(style='ControlButton.Inactive.TButton')
        zgd_frame_instance.active_group_button = None
        
    if showtime_tab.shared_state.active_device_button and showtime_tab.shared_state.active_device_button.winfo_exists():
        showtime_tab.shared_state.active_device_button.config(style='DeviceButton.Inactive.TButton')
        showtime_tab.shared_state.active_device_button = None
        
    zgd_frame_instance.groups_frame.grid_remove()
    
    all_devices = zgd_frame_instance._get_all_devices_in_zone(zgd_frame_instance.structured_data, None)
    zgd_frame_instance._get_min_max_freq_and_update_title(frame_widget=zgd_frame_instance.zones_frame, devices=all_devices, title_prefix="ALL DEVICES")
    
    zgd_frame_instance.groups_frame.config(text="Groups")
    zgd_frame_instance.devices_outer_frame.config(text=f"Devices ({len(all_devices)})")
    
    zgd_frame_instance._make_group_buttons()
    zgd_frame_instance._make_device_buttons()
    zgd_frame_instance.canvas.yview_moveto(0)
    
    _update_zone_zoom_tab(zgd_frame_instance)
    
    debug_log(message=f"🛠️🟢 Exiting {current_function}", file=current_file, version=current_version, function=current_function)

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

    if showtime_tab.shared_state.selected_zone == zone_name:
        no_zone_grou_device_selected(zgd_frame_instance)
    else:
        console_log(f"EVENT: Zone '{zone_name}' selected. Loading groups and devices... 🚀")
        if zgd_frame_instance.active_zone_button and zgd_frame_instance.active_zone_button.winfo_exists():
            zgd_frame_instance.active_zone_button.config(style='ControlButton.Inactive.TButton')
        if zgd_frame_instance.active_group_button and zgd_frame_instance.active_group_button.winfo_exists():
            zgd_frame_instance.active_group_button.config(style='ControlButton.Inactive.TButton')
            zgd_frame_instance.active_group_button = None
        
        # 📝 Write Data: Update selected state variables.
        debug_log(message=f"🛠️📝 Writing to shared state: Updating selected zone and resetting group/device.", file=current_file, version=current_version, function=current_function)
        showtime_tab.shared_state.active_device_button = None
        showtime_tab.shared_state.selected_device_info = None
        showtime_tab.shared_state.selected_zone = zone_name
        showtime_tab.shared_state.selected_group = None
        showtime_tab.shared_state.last_selected_type = 'zone'

        # NEW: Calculate and store zone information in shared_state
        all_devices_in_zone = zgd_frame_instance._get_all_devices_in_zone(zgd_frame_instance.structured_data, showtime_tab.shared_state.selected_zone)
        freqs = [float(d['CENTER']) for d in all_devices_in_zone if isinstance(d.get('CENTER'), (int, float))]

        showtime_tab.shared_state.selected_zone_info = {
            'min_freq': min(freqs) if freqs else 0.0,
            'max_freq': max(freqs) if freqs else 0.0,
            'device_count': len(all_devices_in_zone)
        }
        
        debug_log(message=f"🛠️📦 Stored zone info in shared state: {showtime_tab.shared_state.selected_zone_info}", file=current_file, version=current_version, function=current_function)

        if selected_button:
            selected_button.config(style='ControlButton.Active.TButton')
            zgd_frame_instance.active_zone_button = selected_button
        
        zgd_frame_instance._get_min_max_freq_and_update_title(frame_widget=zgd_frame_instance.zones_frame, devices=all_devices_in_zone, title_prefix=f"Zone '{zone_name}'")

        zgd_frame_instance._get_min_max_freq_and_update_title(frame_widget=zgd_frame_instance.groups_frame, devices=[], title_prefix=f"Groups in Zone '{showtime_tab.shared_state.selected_zone}'" if showtime_tab.shared_state.selected_zone else "Groups")

        zgd_frame_instance._make_group_buttons()
        zgd_frame_instance._make_device_buttons()
        zgd_frame_instance.canvas.yview_moveto(0)
        
        # FIXED: Call the set_span_to_zone utility function here to trigger the update
        from tabs.Markers.showtime.controls.utils_showtime_zone_zoom import set_span_to_zone
        set_span_to_zone(showtime_tab_instance=showtime_tab, zone_zoom_tab=showtime_tab.controls_frame.zone_zoom_tab)

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
    debug_log(message=f"🛠️📝 Writing to shared state: Resetting selected group and related info.", file=current_file, version=current_version, function=current_function)
    showtime_tab.shared_state.selected_group = None
    showtime_tab.shared_state.last_selected_type = 'zone'
    showtime_tab.shared_state.selected_group_info = {
        'min_freq': 0.0,
        'max_freq': 0.0,
        'device_count': 0
    }
    zgd_frame_instance._make_device_buttons()
    
    _update_zone_zoom_tab(zgd_frame_instance)
    
    debug_log(message=f"🛠️🟢 Exiting {current_function}", file=current_file, version=current_version, function=current_function)

def on_group_selected(zgd_frame_instance, group_name):
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️🟢 Entering {current_function} for group: {group_name}", file=current_file, version=current_version, function=current_function)

    showtime_tab = zgd_frame_instance.showtime_tab_instance
    devices_in_group = zgd_frame_instance.structured_data.get(showtime_tab.shared_state.selected_zone, {}).get(group_name, [])

    if len(devices_in_group) == 1:
        console_log(f"EVENT: Group '{group_name}' contains one device. Auto-selecting device...", "INFO")
        # 📝 Write Data: Update selected state variables.
        debug_log(message=f"🛠️📝 Writing to shared state: Updating selected group and resetting device.", file=current_file, version=current_version, function=current_function)
        showtime_tab.shared_state.selected_group = group_name
        zgd_frame_instance._make_device_buttons()
        on_device_selected(zgd_frame_instance, devices_in_group[0])
        
        for widget in zgd_frame_instance.groups_frame.winfo_children():
            if widget.cget("text") == group_name:
                if zgd_frame_instance.active_group_button and zgd_frame_instance.active_group_button.winfo_exists():
                    zgd_frame_instance.active_group_button.config(style='ControlButton.Inactive.TButton')
                widget.config(style='ControlButton.Active.TButton')
                zgd_frame_instance.active_group_button = widget
                break
        return

    if showtime_tab.shared_state.selected_group == group_name:
        console_log(f"EVENT: Group '{group_name}' deselected. Reverting to show all devices in Zone '{showtime_tab.shared_state.selected_zone}'.", "INFO")
        on_group_deselected(zgd_frame_instance)
        return

    for widget in zgd_frame_instance.groups_frame.winfo_children():
        if widget.cget("text") == group_name:
            selected_button = widget
            break
    else:
        selected_button = None

    console_log(f"EVENT: Group '{group_name}' selected in Zone '{showtime_tab.shared_state.selected_zone}'. Loading devices... ⚙️")
    if zgd_frame_instance.active_group_button and zgd_frame_instance.active_group_button.winfo_exists():
        zgd_frame_instance.active_group_button.config(style='ControlButton.Inactive.TButton')

    # 📝 Write Data: Update selected state variables.
    debug_log(message=f"🛠️📝 Writing to shared state: Updating selected group and resetting device.", file=current_file, version=current_version, function=current_function)
    showtime_tab.shared_state.active_device_button = None
    showtime_tab.shared_state.selected_device_info = None
    showtime_tab.shared_state.selected_group = group_name
    showtime_tab.shared_state.last_selected_type = 'group'

    # NEW: Calculate and store group information in shared_state
    freqs = [float(d['CENTER']) for d in devices_in_group if isinstance(d.get('CENTER'), (int, float))]
    
    showtime_tab.shared_state.selected_group_info = {
        'min_freq': min(freqs) if freqs else 0.0,
        'max_freq': max(freqs) if freqs else 0.0,
        'device_count': len(devices_in_group)
    }
    
    debug_log(message=f"🛠️📦 Stored group info in shared state: {showtime_tab.shared_state.selected_group_info}", file=current_file, version=current_version, function=current_function)

    if selected_button:
        selected_button.config(style='ControlButton.Active.TButton')
        zgd_frame_instance.active_group_button = selected_button
    
    devices_in_group_list = zgd_frame_instance.structured_data.get(showtime_tab.shared_state.selected_zone, {}).get(group_name, [])
    zgd_frame_instance._get_min_max_freq_and_update_title(frame_widget=zgd_frame_instance.groups_frame, devices=devices_in_group_list, title_prefix=f"Group '{group_name}'")

    zgd_frame_instance._make_device_buttons()
    zgd_frame_instance.canvas.yview_moveto(0)
    
    # FIXED: Call the set_span_to_group utility function here to trigger the update
    from tabs.Markers.showtime.controls.utils_showtime_zone_zoom import set_span_to_group
    set_span_to_group(showtime_tab_instance=showtime_tab, zone_zoom_tab=showtime_tab.controls_frame.zone_zoom_tab)

    debug_log(message=f"🛠️🟢 Exiting {current_function}", file=current_file, version=current_version, function=current_function)
    
def on_device_deselected(zgd_frame_instance):
    # [Handles the logic for when a device is deselected.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
    
    showtime_tab = zgd_frame_instance.showtime_tab_instance
    # 📝 Write Data: Reset selected state variables.
    debug_log(message=f"🛠️📝 Writing to shared state: Resetting selected device.", file=current_file, version=current_version, function=current_function)
    showtime_tab.shared_state.selected_device_info = None
    showtime_tab.shared_state.last_selected_type = 'group'

    if showtime_tab.shared_state.active_device_button and showtime_tab.shared_state.active_device_button.winfo_exists():
        showtime_tab.shared_state.active_device_button.config(style='DeviceButton.Inactive.TButton')
    showtime_tab.shared_state.active_device_button = None
    
    # FIXED: Revert the view to the parent group when a device is deselected.
    set_span_to_group(showtime_tab_instance=showtime_tab, zone_zoom_tab=showtime_tab.controls_frame.zone_zoom_tab)
    _update_zone_zoom_tab(zgd_frame_instance)
    
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
    
    if showtime_tab.shared_state.selected_device_info and id(showtime_tab.shared_state.selected_device_info) == id(device_info):
        console_log(f"EVENT: Device '{device_name}' deselected.")
        on_device_deselected(zgd_frame_instance)
        debug_log(message=f"🛠️🟢 Exiting {current_function} after deselecting device.", file=current_file, version=current_version, function=current_function)
        return

    # 📝 Write Data: Update selected state variables.
    debug_log(message=f"🛠️📝 Writing to shared state: Storing selected device info.", file=current_file, version=current_version, function=current_function)
    showtime_tab.shared_state.selected_device_info = device_info
    showtime_tab.shared_state.last_selected_type = 'device'

    selected_button = showtime_tab.shared_state.device_buttons.get(id(device_info))
    
    if showtime_tab.shared_state.active_device_button and showtime_tab.shared_state.active_device_button.winfo_exists():
        showtime_tab.shared_state.active_device_button.config(style='DeviceButton.Inactive.TButton')

    if selected_button:
        selected_button.config(style='DeviceButton.Active.TButton')
        showtime_tab.shared_state.active_device_button = selected_button
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
    
    # NEW: Set the instrument's center frequency and span based on the shared state.
    center_freq_mhz = device_info.get('CENTER')
    # 📖 Read Data: Get the current span from the shared state.
    span_str = showtime_tab.shared_state.span_var.get()
    if 'M' in span_str:
        span_mhz = float(span_str.replace('M', ''))
    else:
        span_mhz = float(span_str)

    if center_freq_mhz is not None and isinstance(center_freq_mhz, (float, int)):
        debug_log(message=f"🛠️📤 Outbound: Setting instrument center frequency to {center_freq_mhz} MHz and span to {span_mhz} MHz.", file=current_file, version=current_version, function=current_function)
        
        # Convert to Hz for the handler function
        center_freq_hz = int(center_freq_mhz * 1_000_000)
        span_hz = int(span_mhz * 1_000_000)
        
        handle_freq_center_span_beg(app_instance=showtime_tab.app_instance, 
                             center_freq=center_freq_hz, 
                             span_freq=span_hz,
                             console_print_func=showtime_tab.console_print_func)
    else:
        console_log("❌ Cannot set instrument center frequency. Invalid device center frequency.")
        debug_log(message=f"🛠️❌ Invalid center frequency for device: {center_freq_mhz}. Cannot set instrument.", 
                  file=current_file, 
                  version=current_version, 
                  function=current_function)

    debug_log(message=f"🛠️🟢 Exiting {current_function}", file=current_file, version=current_version, function=current_function)
