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
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250821.161000.1
# NEW: Added `on_group_deselected` and `on_device_deselected` functions for clean state management.
# NEW: Added `get_current_view_details` function to return frequency information of the current selection.
# FIXED: The `on_group_selected` and `on_device_selected` functions now call the new deselection utilities.
# REFACTORED: All functions now access and modify state directly on the `showtime_tab_instance` object.
# NEW: Implemented a new _update_zone_zoom_tab function to keep the Zone Zoom tab in sync.

current_version = "20250821.161000.1"
current_version_hash = (20250821 * 161000 * 1)

import os
import inspect
import math
from tkinter import ttk

from display.debug_logic import debug_log
from display.console_logic import console_log

def _update_zone_zoom_tab(zgd_frame_instance):
    # [A helper function to update the ZoneZoomTab with the current selection details.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
    
    showtime_tab = zgd_frame_instance.showtime_tab_instance
    try:
        details = get_current_view_details(zgd_frame_instance)
        if details:
            start_freq = details['start']
            stop_freq = details['stop']
            count = len(zgd_frame_instance._get_devices_to_display())
            
            if showtime_tab.shared_state.last_selected_type == 'zone':
                showtime_tab.shared_state.zone_zoom_label_left_var.set(f"Zone: {showtime_tab.shared_state.selected_zone}")
                showtime_tab.shared_state.zone_zoom_label_center_var.set(f"Start: {start_freq:.3f} MHz")
                showtime_tab.shared_state.zone_zoom_label_right_var.set(f"Stop: {stop_freq:.3f} MHz ({count} Devices)")
            elif showtime_tab.shared_state.last_selected_type == 'group':
                showtime_tab.shared_state.zone_zoom_label_left_var.set(f"Group: {showtime_tab.shared_state.selected_group}")
                showtime_tab.shared_state.zone_zoom_label_center_var.set(f"Start: {start_freq:.3f} MHz")
                showtime_tab.shared_state.zone_zoom_label_right_var.set(f"Stop: {stop_freq:.3f} MHz ({count} Devices)")
            elif showtime_tab.shared_state.last_selected_type == 'device':
                showtime_tab.shared_state.zone_zoom_label_left_var.set(f"Device: {showtime_tab.shared_state.selected_device_info.get('NAME')}")
                showtime_tab.shared_state.zone_zoom_label_center_var.set(f"Center: {start_freq:.3f} MHz")
                showtime_tab.shared_state.zone_zoom_label_right_var.set(f"Span: {stop_freq:.3f} MHz")
            else: # All markers
                showtime_tab.shared_state.zone_zoom_label_left_var.set("All Markers")
                showtime_tab.shared_state.zone_zoom_label_center_var.set(f"Start: {start_freq:.3f} MHz")
                showtime_tab.shared_state.zone_zoom_label_right_var.set(f"Stop: {stop_freq:.3f} MHz ({count} Devices)")

        else:
            showtime_tab.shared_state.zone_zoom_label_left_var.set("Select Zone/Group/Device")
            showtime_tab.shared_state.zone_zoom_label_center_var.set("N/A")
            showtime_tab.shared_state.zone_zoom_label_right_var.set("N/A")
            
        showtime_tab.controls_frame.zone_zoom_tab._sync_ui_from_state()

    except Exception as e:
        debug_log(f"Error in _update_zone_zoom_tab: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
    
    debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

def get_current_view_details(zgd_frame_instance):
    # [Returns a dictionary with the start, stop, center, and span frequencies for the current view.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

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
        freqs = [float(d.get('CENTER')) for d in all_devices if d.get('CENTER') and isinstance(d.get('CENTER'), (int, float))]
        if freqs:
            start_freq = min(freqs)
            stop_freq = max(freqs)
            
    if start_freq is not None and stop_freq is not None:
        center = (start_freq + stop_freq) / 2
        span = stop_freq - start_freq
        return {"start": start_freq, "stop": stop_freq, "center": center, "span": span}
    
    debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
    return None

def no_zone_grou_device_selected(zgd_frame_instance):
    # [Handles the logic for when no zone, group, or device is selected.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
    
    console_log(f"EVENT: No zone, group, or device selected. Displaying all devices. 🔍")
    
    # Access and update parent's state variables directly
    showtime_tab = zgd_frame_instance.showtime_tab_instance
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
    
    debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

def on_zone_selected(zgd_frame_instance, zone_name):
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function} for zone: {zone_name}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

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
        
        showtime_tab.shared_state.active_device_button = None
        showtime_tab.shared_state.selected_device_info = None
        showtime_tab.shared_state.selected_zone = zone_name
        showtime_tab.shared_state.selected_group = None
        showtime_tab.shared_state.last_selected_type = 'zone'
        
        if selected_button:
            selected_button.config(style='ControlButton.Active.TButton')
            zgd_frame_instance.active_zone_button = selected_button
        
        all_devices_in_zone = zgd_frame_instance._get_all_devices_in_zone(zgd_frame_instance.structured_data, showtime_tab.shared_state.selected_zone)
        zgd_frame_instance._get_min_max_freq_and_update_title(frame_widget=zgd_frame_instance.zones_frame, devices=all_devices_in_zone, title_prefix=f"Zone '{zone_name}'")

        zgd_frame_instance._get_min_max_freq_and_update_title(frame_widget=zgd_frame_instance.groups_frame, devices=[], title_prefix=f"Groups in Zone '{showtime_tab.shared_state.selected_zone}'" if showtime_tab.shared_state.selected_zone else "Groups")

        zgd_frame_instance._make_group_buttons()
        zgd_frame_instance._make_device_buttons()
        zgd_frame_instance.canvas.yview_moveto(0)
        
        _update_zone_zoom_tab(zgd_frame_instance)

    debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
    
def on_group_deselected(zgd_frame_instance):
    # [Handles the logic for when a group is deselected.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
    
    showtime_tab = zgd_frame_instance.showtime_tab_instance

    if zgd_frame_instance.active_group_button and zgd_frame_instance.active_group_button.winfo_exists():
        zgd_frame_instance.active_group_button.config(style='ControlButton.Inactive.TButton')
        zgd_frame_instance.active_group_button = None
        
    showtime_tab.shared_state.selected_group = None
    showtime_tab.shared_state.last_selected_type = 'zone'
    zgd_frame_instance._make_device_buttons()
    
    _update_zone_zoom_tab(zgd_frame_instance)
    
    debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

def on_group_selected(zgd_frame_instance, group_name):
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function} for group: {group_name}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    showtime_tab = zgd_frame_instance.showtime_tab_instance
    devices_in_group = zgd_frame_instance.structured_data.get(showtime_tab.shared_state.selected_zone, {}).get(group_name, [])

    if len(devices_in_group) == 1:
        console_log(f"EVENT: Group '{group_name}' contains one device. Auto-selecting device...", "INFO")
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

    showtime_tab.shared_state.active_device_button = None
    showtime_tab.shared_state.selected_device_info = None
    showtime_tab.shared_state.selected_group = group_name
    showtime_tab.shared_state.last_selected_type = 'group'

    if selected_button:
        selected_button.config(style='ControlButton.Active.TButton')
        zgd_frame_instance.active_group_button = selected_button
    
    zgd_frame_instance._get_min_max_freq_and_update_title(frame_widget=zgd_frame_instance.groups_frame, devices=devices_in_group, title_prefix=f"Group '{group_name}'")

    zgd_frame_instance._make_device_buttons()
    zgd_frame_instance.canvas.yview_moveto(0)
    
    _update_zone_zoom_tab(zgd_frame_instance)
    
    debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
    
def on_device_deselected(zgd_frame_instance):
    # [Handles the logic for when a device is deselected.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
    
    showtime_tab = zgd_frame_instance.showtime_tab_instance
    showtime_tab.shared_state.selected_device_info = None
    showtime_tab.shared_state.last_selected_type = 'group'

    if showtime_tab.shared_state.active_device_button and showtime_tab.shared_state.active_device_button.winfo_exists():
        showtime_tab.shared_state.active_device_button.config(style='DeviceButton.Inactive.TButton')
    showtime_tab.shared_state.active_device_button = None
    
    _update_zone_zoom_tab(zgd_frame_instance)
    
    if hasattr(showtime_tab.controls_frame, 'switch_to_tab'):
        showtime_tab.controls_frame.switch_to_tab("Zone Zoom")
        
    debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

def on_device_selected(zgd_frame_instance, device_info):
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function} for device object: {device_info}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    showtime_tab = zgd_frame_instance.showtime_tab_instance
    device_name = device_info.get('NAME', 'N/A')

    if isinstance(device_name, float) and math.isnan(device_name):
        device_name = 'nan'
    
    if showtime_tab.shared_state.selected_device_info and id(showtime_tab.shared_state.selected_device_info) == id(device_info):
        console_log(f"EVENT: Device '{device_name}' deselected.")
        on_device_deselected(zgd_frame_instance)
        debug_log(f"Exiting {current_function} after deselecting device.", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        return

    showtime_tab.shared_state.selected_device_info = device_info
    showtime_tab.shared_state.last_selected_type = 'device'

    selected_button = showtime_tab.shared_state.device_buttons.get(id(device_info))
    
    if showtime_tab.shared_state.active_device_button and showtime_tab.shared_state.active_device_button.winfo_exists():
        showtime_tab.shared_state.active_device_button.config(style='DeviceButton.Inactive.TButton')

    if selected_button:
        selected_button.config(style='DeviceButton.Active.TButton')
        showtime_tab.shared_state.active_device_button = selected_button
        console_log(f"EVENT: Device '{device_name}' selected. 🎵")
    
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
    
    debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
