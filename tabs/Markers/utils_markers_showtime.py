# tabs/Markers/utils_markers_showtime.py
#
# This file provides utility functions for the ShowtimeTab.
# All complex logic related to button actions, data processing, and instrument
# control has been moved here to keep the main GUI class clean and focused
# on visual layout. This refactoring improves modularity and testability.
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
# Version 20250813.094700.1 (REFACTORED: All operational logic moved from ShowtimeTab to this utility file.)

current_version = "20250813.094700.1"
current_version_hash = (20250813 * 94700 * 1)

import tkinter as tk
from tkinter import ttk
import os
import csv
import inspect
import pandas as pd
import threading
import time
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log
from display.utils_display_monitor import update_top_plot, update_medium_plot, update_bottom_plot

# Import the utility functions for markers
from tabs.Markers.utils_marker_peaks import get_peak_values_and_update_csv
from tabs.Markers.utils_markers_get_traces import get_marker_traces
from tabs.Markers.utils_markers import (
    SPAN_OPTIONS,
    RBW_OPTIONS,
    set_span_logic,
    set_frequency_logic,
    set_trace_modes_logic,
    set_marker_logic,
    set_rbw_logic
)
from src.program_style import COLOR_PALETTE
from src.settings_and_config.config_manager import save_config
from ref.frequency_bands import MHZ_TO_HZ

# NEW: Options for the Loop tab's delay setting
LOOP_DELAY_OPTIONS = [500, 1000, 1500, 2000]

def format_hz(hz_val):
    # Function Description:
    # Formats a frequency in Hz to a human-readable string in MHz or kHz.
    debug_log(message=f"Formatting frequency: {hz_val} Hz.",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)
    try:
        hz = float(hz_val)
        if hz == 100 * MHZ_TO_HZ: return "100 MHz"
        if hz >= MHZ_TO_HZ:
            return f"{hz / MHZ_TO_HZ:.1f}".replace('.0', '') + " MHz"
        elif hz >= 1000:
            return f"{hz / 1000:.1f}".replace('.0', '') + " kHz"
        else:
            return f"{hz} Hz"
    except (ValueError, TypeError):
        return "N/A"

def load_markers_data(showtime_tab_instance):
    # Function Description:
    # Loads marker data from the internal MARKERS.CSV file.
    debug_log(message=f"Loading markers from the CSV file. �",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)
    
    showtime_tab_instance.markers_data = pd.DataFrame()
    showtime_tab_instance.zones = {}
    
    if showtime_tab_instance.app_instance and hasattr(showtime_tab_instance.app_instance, 'MARKERS_FILE_PATH'):
        path = showtime_tab_instance.app_instance.MARKERS_FILE_PATH
        if os.path.exists(path):
            try:
                showtime_tab_instance.markers_data = pd.read_csv(path)
                debug_log(f"Successfully read MARKERS.CSV. Shape: {showtime_tab_instance.markers_data.shape}. Columns: {showtime_tab_instance.markers_data.columns.tolist()}",
                          file=f"{os.path.basename(__file__)}",
                          version=current_version,
                          function=inspect.currentframe().f_code.co_name, special=True)
                showtime_tab_instance.zones = _group_by_zone_and_group(showtime_tab_instance.markers_data)
                showtime_tab_instance.console_print_func(f"✅ Loaded {len(showtime_tab_instance.markers_data)} markers from MARKERS.CSV.")
            except Exception as e:
                showtime_tab_instance.console_print_func(f"❌ Error loading MARKERS.CSV: {e}")
                debug_log(f"A file loading calamity! The MARKERS.CSV file couldn't be loaded. Error: {e}",
                          file=f"{os.path.basename(__file__)}",
                          version=current_version,
                          function=inspect.currentframe().f_code.co_name, special=True)
        else:
            showtime_tab_instance.console_print_func("ℹ️ MARKERS.CSV not found. Please create one.")
            debug_log(f"MARKERS.CSV file not found at path: {path}",
                      file=f"{os.path.basename(__file__)}",
                      version=current_version,
                      function=inspect.currentframe().f_code.co_name)

def _group_by_zone_and_group(data):
    # Function Description:
    # Groups marker data by zone and then by group.
    debug_log(message=f"Grouping data by ZONE and GROUP. Data shape: {data.shape}",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)

    if data.empty:
        return {}
    
    data['GROUP'] = data['GROUP'].fillna('No Group')
    
    zones = {}
    for zone, zone_data in data.groupby('ZONE'):
        groups = {group: group_data.to_dict('records') for group, group_data in zone_data.groupby('GROUP')}
        zones[zone] = groups
    
    debug_log(f"Grouping complete. Found {len(zones)} zones.",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)
    return zones

def populate_zone_buttons(showtime_tab_instance):
    # Function Description:
    # Creates buttons for each zone, arranged in a grid with a maximum of 8 columns.
    for widget in showtime_tab_instance.zone_button_subframe.winfo_children():
        widget.destroy()

    showtime_tab_instance.zone_buttons = {} # Clear the dictionary
    
    if not isinstance(showtime_tab_instance.zones, dict) or not showtime_tab_instance.zones:
        ttk.Label(showtime_tab_instance.zone_button_subframe, text="No zones found in MARKERS.CSV.").grid(row=0, column=0, columnspan=8)
        return
        
    max_cols = 8 # Changed max columns to 8 from 10
    for i, zone_name in enumerate(sorted(showtime_tab_instance.zones.keys())):
        row = i // max_cols
        col = i % max_cols
        
        # Count the total number of devices in the zone
        device_count = sum(len(group) for group in showtime_tab_instance.zones[zone_name].values())
        
        btn = ttk.Button(showtime_tab_instance.zone_button_subframe, 
                         text=f"{zone_name} ({device_count})",
                         command=lambda z=zone_name: on_zone_button_click(showtime_tab_instance, z))
        btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
        showtime_tab_instance.zone_buttons[zone_name] = btn
    
    _update_zone_button_styles(showtime_tab_instance)

def populate_group_buttons(showtime_tab_instance):
    # Function Description:
    # Creates buttons for each group in the selected zone.
    for widget in showtime_tab_instance.group_button_subframe.winfo_children():
        widget.destroy()
    
    showtime_tab_instance.group_buttons = {} # Clear the dictionary
    
    if not showtime_tab_instance.selected_zone or showtime_tab_instance.selected_zone not in showtime_tab_instance.zones:
        showtime_tab_instance.group_buttons_frame.grid_remove() # Hide the frame if no zone selected
        return
    
    groups = showtime_tab_instance.zones[showtime_tab_instance.selected_zone]
    
    if not groups:
        showtime_tab_instance.group_buttons_frame.grid_remove() # Hide the frame if no groups
        return
    
    # If there are groups, make sure the frame is visible
    showtime_tab_instance.group_buttons_frame.grid()
    
    max_cols = 8 # Changed max columns to 8 from 10
    for i, group_name in enumerate(sorted(groups.keys())):
        row = i // max_cols
        col = i % max_cols
        
        device_count = len(groups[group_name])
        btn = ttk.Button(showtime_tab_instance.group_button_subframe, 
                         text=f"{group_name} ({device_count})",
                         command=lambda g=group_name: on_group_button_click(showtime_tab_instance, g))
        btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
        showtime_tab_instance.group_buttons[group_name] = btn
        
    _update_group_button_styles(showtime_tab_instance)


def on_zone_button_click(showtime_tab_instance, zone_name):
    # Function Description:
    # Handles a click on a zone button.
    debug_log(message=f"Zone button '{zone_name}' clicked. Initiating peak search for the entire zone.",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)
    
    stop_loop_action(showtime_tab_instance)
    showtime_tab_instance.selected_zone = zone_name
    showtime_tab_instance.selected_group = None
    _update_zone_button_styles(showtime_tab_instance)
    
    # Filter the devices to be processed by the utility function
    devices_in_zone_df = showtime_tab_instance.markers_data[showtime_tab_instance.markers_data['ZONE'] == zone_name]

    if not devices_in_zone_df.empty:
        showtime_tab_instance.console_print_func(f"🔎 Starting batch peak search for all devices in zone '{zone_name}'...")
        _peak_search_and_get_trace(showtime_tab_instance, devices=devices_in_zone_df, name=f"Zone: {zone_name}")
        populate_group_buttons(showtime_tab_instance)
        populate_device_buttons(showtime_tab_instance)
    else:
        showtime_tab_instance.console_print_func(f"ℹ️ No devices found in zone '{zone_name}'.")
        populate_group_buttons(showtime_tab_instance)
        populate_device_buttons(showtime_tab_instance)
        
    _update_group_button_styles(showtime_tab_instance)

def on_group_button_click(showtime_tab_instance, group_name):
    # Function Description:
    # Handles a click on a group button.
    debug_log(message=f"Group button '{group_name}' clicked. Initiating peak search for the group.",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)

    stop_loop_action(showtime_tab_instance)
    showtime_tab_instance.selected_group = group_name
    _update_group_button_styles(showtime_tab_instance)

    devices_in_group_df = showtime_tab_instance.markers_data[(showtime_tab_instance.markers_data['ZONE'] == showtime_tab_instance.selected_zone) & (showtime_tab_instance.markers_data['GROUP'] == showtime_tab_instance.selected_group)]

    if not devices_in_group_df.empty:
        showtime_tab_instance.console_print_func(f"🔎 Starting batch peak search for all devices in group '{group_name}'...")
        _peak_search_and_get_trace(showtime_tab_instance, devices=devices_in_group_df, name=f"Group: {group_name}")
        populate_device_buttons(showtime_tab_instance)
    else:
        showtime_tab_instance.console_print_func(f"ℹ️ No devices found in group '{group_name}'.")
        populate_device_buttons(showtime_tab_instance)

def _peak_search_and_get_trace(showtime_tab_instance, devices, name):
    # Function Description:
    # Performs a batch peak search and then gets the trace for the full span of the devices.
    debug_log(message=f"Entering _peak_search_and_get_trace for {name}. Processing {len(devices)} devices.",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)
    
    if not showtime_tab_instance.app_instance.inst or devices.empty:
        showtime_tab_instance.console_print_func("❌ Cannot perform peak search: no instrument connected or no devices selected.")
        return

    # Perform peak search and update CSV in a separate thread to not block the UI
    threading.Thread(target=_perform_peak_search_task, args=(showtime_tab_instance, devices, name), daemon=True).start()

def _perform_peak_search_task(showtime_tab_instance, devices, name):
    """Worker function for the peak search task."""
    debug_log(message=f"Starting background task for peak search on {name}.",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)
    
    with showtime_tab_instance.instrument_lock:
        updated_markers_df = get_peak_values_and_update_csv(app_instance=showtime_tab_instance.app_instance, devices_to_process=devices, console_print_func=showtime_tab_instance.console_print_func)
    
    if updated_markers_df is None:
        showtime_tab_instance.app_instance.after(0, lambda: showtime_tab_instance.console_print_func("❌ Peak search failed. See console for details."))
        return
        
    showtime_tab_instance.app_instance.after(0, lambda: load_markers_data(showtime_tab_instance)) # Reload data to get fresh peak values
    
    all_freqs_mhz = devices['FREQ'].dropna().tolist()
    if not all_freqs_mhz:
        showtime_tab_instance.app_instance.after(0, lambda: showtime_tab_instance.console_print_func(f"⚠️ No valid frequencies found in {name}. Cannot get a trace."))
        return
        
    min_freq_mhz = min(all_freqs_mhz)
    max_freq_mhz = max(all_freqs_mhz)
    
    span_mhz = max_freq_mhz - min_freq_mhz
    
    MIN_SPAN_KHZ = 100
    
    if span_mhz == 0:
        trace_center_freq_mhz = min_freq_mhz
        trace_span_mhz = MIN_SPAN_KHZ / 1e3
    else:
        buffer_mhz = span_mhz * 0.1
        trace_start_freq_mhz = max(0, min_freq_mhz - buffer_mhz)
        trace_end_freq_mhz = max_freq_mhz + buffer_mhz
        trace_center_freq_mhz = (trace_start_freq_mhz + trace_end_freq_mhz) / 2
        trace_span_mhz = trace_end_freq_mhz - trace_start_freq_mhz
        
    trace_center_freq_hz = int(trace_center_freq_mhz * MHZ_TO_HZ)
    trace_span_hz = int(trace_span_mhz * MHZ_TO_HZ)
    
    showtime_tab_instance.app_instance.after(0, lambda: showtime_tab_instance.console_print_func(f"📊 Displaying trace for {name} over a buffered span of {trace_span_mhz:.3f} MHz."))
    
    with showtime_tab_instance.instrument_lock:
        showtime_tab_instance.app_instance.after(0, lambda: get_marker_traces(app_instance=showtime_tab_instance.app_instance, showtime_tab_instance=showtime_tab_instance, console_print_func=showtime_tab_instance.console_print_func, center_freq_hz=trace_center_freq_hz, span_hz=trace_span_hz, device_name=name))
    
    showtime_tab_instance.app_instance.after(0, lambda: populate_device_buttons(showtime_tab_instance))

def _update_zone_button_styles(showtime_tab_instance):
    # Function Description:
    # Updates the styles of the zone buttons to show which is active.
    debug_log(message=f"Entering _update_zone_button_styles. Updating zone button styles.",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)
    for zone_name, btn in showtime_tab_instance.zone_buttons.items():
        if btn.winfo_exists():
            if zone_name == showtime_tab_instance.selected_zone:
                btn.config(style='SelectedPreset.Orange.TButton')
            else:
                btn.config(style='LocalPreset.TButton')

def _update_group_button_styles(showtime_tab_instance):
    # Function Description:
    # Updates the styles of the group buttons to show which is active.
    debug_log(message=f"Entering _update_group_button_styles. Updating group button styles.",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)
    for group_name, btn in showtime_tab_instance.group_buttons.items():
        if btn.winfo_exists():
            if group_name == showtime_tab_instance.selected_group:
                btn.config(style='SelectedPreset.Orange.TButton')
            else:
                btn.config(style='LocalPreset.TButton')

def populate_device_buttons(showtime_tab_instance):
    # Function Description:
    # Creates buttons for each device in the selected zone or group.
    debug_log(message=f"Entering populate_device_buttons. Populating device buttons.",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)
    
    for widget in showtime_tab_instance.device_buttons_frame.winfo_children():
        widget.destroy()

    showtime_tab_instance.device_buttons = {}

    if not showtime_tab_instance.selected_zone:
        ttk.Label(showtime_tab_instance.device_buttons_frame, text="Select a zone and a group to view devices.").grid(row=0, column=0, columnspan=4, padx=10, pady=10)
        return

    devices = []
    if showtime_tab_instance.selected_group:
        devices = showtime_tab_instance.zones[showtime_tab_instance.selected_zone][showtime_tab_instance.selected_group]
    else:
        for group in showtime_tab_instance.zones[showtime_tab_instance.selected_zone].values():
            devices.extend(group)

    if not devices:
        ttk.Label(showtime_tab_instance.device_buttons_frame, text="No devices found in this selection.").grid(row=0, column=0, columnspan=4, padx=10, pady=10)
        return

    row_idx = 0
    col_idx = 0
    for device in devices:
        device_name = device.get('NAME', 'N/A')
        peak_value = device.get('Peak', None)
        
        if pd.notna(peak_value):
            peak_value = float(peak_value)
            if -130 <= peak_value < -80:
                style = 'Red.TButton'
            elif -80 <= peak_value < -50:
                style = 'Orange.TButton'
            elif peak_value >= -50:
                style = 'Green.TButton'
            else:
                style = 'LocalPreset.TButton'
        else:
            style = 'LocalPreset.TButton'

        progress_bar = _create_progress_bar_text(peak_value)
        text = f"{device_name}\n{device.get('FREQ', 'N/A')} MHz\nPeak: {peak_value:.2f} dBm\n{progress_bar}" if pd.notna(peak_value) else f"{device_name}\n{device.get('FREQ', 'N/A')} MHz\nPeak: N/A"
        
        btn = ttk.Button(showtime_tab_instance.device_buttons_frame, text=text, style=style,
                         command=lambda d=device: on_device_button_click(showtime_tab_instance, d))
        btn.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="nsew")
        showtime_tab_instance.device_buttons[device_name] = btn

        col_idx += 1
        if col_idx > 3:
            col_idx = 0
            row_idx += 1

def _create_progress_bar_text(peak_value):
    # Function Description:
    # Creates a text-based progress bar for display on a button.
    debug_log(message=f"Creating progress bar text for peak value: {peak_value}.",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)
              
    if pd.isna(peak_value):
        return "[                        ]"
    
    min_dbm = -120.0
    max_dbm = 0.0
    
    clamped_value = max(min_dbm, min(max_dbm, peak_value))
    
    num_filled_chars = int((clamped_value - min_dbm) / (max_dbm - min_dbm) * 24)
    num_empty_chars = 24 - num_filled_chars
    
    spaces_part = "█" * num_filled_chars
    blocks_part = " " * num_empty_chars
    
    return f"[{spaces_part}{blocks_part}]"


def on_device_button_click(showtime_tab_instance, device_data):
    # Function Description:
    # Handles a click on a device button.
    debug_log(message=f"Device button clicked: {device_data.get('NAME', 'N/A')}",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)
    
    if showtime_tab_instance.is_loop_running:
        stop_loop_action(showtime_tab_instance)

    try:
        freq_mhz = device_data.get('FREQ', 'N/A')
        zone_name = device_data.get('ZONE', 'N/A')
        group_name = device_data.get('GROUP', 'N/A')
        device_name = device_data.get('NAME', 'N/A')
        
        if group_name and group_name != 'N/A' and group_name.strip():
            showtime_tab_instance.selected_device_name = f"{zone_name} / {group_name} / {device_name}"
        else:
            showtime_tab_instance.selected_device_name = f"{zone_name} / {device_name}"
        
        showtime_tab_instance.selected_device_freq = float(freq_mhz) * MHZ_TO_HZ
        
        if showtime_tab_instance.app_instance.inst:
            freq_hz = showtime_tab_instance.selected_device_freq
            span_hz = float(showtime_tab_instance.span_var.get())
            
            with showtime_tab_instance.instrument_lock:
                set_span_logic(app_instance=showtime_tab_instance.app_instance, span_hz=span_hz, console_print_func=showtime_tab_instance.console_print_func)
                set_trace_modes_logic(app_instance=showtime_tab_instance.app_instance, live_mode=showtime_tab_instance.trace_live_mode.get(), max_hold_mode=showtime_tab_instance.trace_max_hold_mode.get(), min_hold_mode=showtime_tab_instance.trace_min_hold_mode.get(), console_print_func=showtime_tab_instance.console_print_func)
                set_frequency_logic(app_instance=showtime_tab_instance.app_instance, frequency_hz=freq_hz, console_print_func=showtime_tab_instance.console_print_func)
                set_marker_logic(app_instance=showtime_tab_instance.app_instance, frequency_hz=freq_hz, marker_name=showtime_tab_instance.selected_device_name, console_print_func=showtime_tab_instance.console_print_func)
            
            showtime_tab_instance.loop_counter_var.set(0)
            showtime_tab_instance.loop_run_count = 0
            if device_name in showtime_tab_instance.device_buttons:
                clicked_button = showtime_tab_instance.device_buttons[device_name]
                start_device_trace_loop(showtime_tab_instance, center_freq_hz=freq_hz, span_hz=span_hz, button_to_blink=clicked_button)
            else:
                showtime_tab_instance.console_print_func(f"❌ Cannot find button for device '{device_name}'.")

    except (ValueError, TypeError) as e:
        showtime_tab_instance.console_print_func(f"❌ Error setting frequency and starting trace loop: {e}")
        debug_log(f"Dastardly bug! A TypeError or ValueError has struck our brave loop! Error: {e}",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=inspect.currentframe().f_code.co_name, special=True)

def stop_loop_action(showtime_tab_instance):
    # Function Description:
    # Handles the "Stop Loop" button action.
    debug_log(message=f"Stopping the loop! All systems, cease and desist!",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)

    if showtime_tab_instance.is_loop_running:
        showtime_tab_instance.is_loop_running = False
        if showtime_tab_instance.marker_trace_loop_job:
            showtime_tab_instance.after_cancel(showtime_tab_instance.marker_trace_loop_job)
            showtime_tab_instance.marker_trace_loop_job = None
        if showtime_tab_instance.blinking_button_job:
            showtime_tab_instance.after_cancel(showtime_tab_instance.blinking_button_job)
            showtime_tab_instance.blinking_button_job = None
        if showtime_tab_instance.currently_blinking_button:
            showtime_tab_instance.currently_blinking_button.config(style='LocalPreset.TButton')
            showtime_tab_instance.currently_blinking_button = None
        showtime_tab_instance.loop_counter_var.set(0)
        showtime_tab_instance.loop_run_count = 0
        showtime_tab_instance.console_print_func("✅ Marker trace loop stopped.")
        _update_control_styles(showtime_tab_instance)
    else:
        showtime_tab_instance.console_print_func("❌ No active loop to stop.")

def start_device_trace_loop(showtime_tab_instance, center_freq_hz=None, span_hz=None, button_to_blink=None):
    # Function Description:
    # Starts a recurring loop to fetch marker traces for a specific device, limited to 10 cycles.
    debug_log(message=f"Starting the device trace loop. Get ready for some data! 📈",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)
    
    if showtime_tab_instance.app_instance and showtime_tab_instance.app_instance.inst and center_freq_hz is not None and span_hz is not None:
        showtime_tab_instance.is_loop_running = True
        showtime_tab_instance.currently_blinking_button = button_to_blink
        _blink_device_button(showtime_tab_instance)
        
        def loop_func():
            if not showtime_tab_instance.winfo_ismapped() or showtime_tab_instance.loop_run_count >= showtime_tab_instance.loop_limit or not showtime_tab_instance.is_loop_running:
                stop_loop_action(showtime_tab_instance)
                return
                
            with showtime_tab_instance.instrument_lock:
                get_marker_traces(app_instance=showtime_tab_instance.app_instance, showtime_tab_instance=showtime_tab_instance, console_print_func=showtime_tab_instance.console_print_func, center_freq_hz=center_freq_hz, span_hz=span_hz, device_name=showtime_tab_instance.selected_device_name)
            
            showtime_tab_instance.loop_counter_var.set(showtime_tab_instance.loop_counter_var.get() + 1)
            showtime_tab_instance.loop_run_count += 1
            
            try:
                delay = int(showtime_tab_instance.loop_delay_var.get())
                showtime_tab_instance.marker_trace_loop_job = showtime_tab_instance.after(delay, loop_func)
            except ValueError:
                showtime_tab_instance.console_print_func("❌ Invalid loop delay. Please enter a valid number (e.g., 500, 1000). Stopping loop.")
                showtime_tab_instance.is_loop_running = False
                showtime_tab_instance.loop_stop_button.config(state=tk.DISABLED)
                return
        
        showtime_tab_instance.loop_stop_button.config(state=tk.NORMAL)
        showtime_tab_instance.marker_trace_loop_job = showtime_tab_instance.after(0, loop_func)
        
    else:
        showtime_tab_instance.console_print_func("❌ Invalid parameters for marker trace loop. Cannot start.")
        debug_log(f"Invalid parameters! We need a center frequency and a span to begin our voyage! Parameters were: center_freq_hz={center_freq_hz}, span_hz={span_hz}",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=inspect.currentframe().f_code.co_name, special=True)
                  
def _blink_device_button(showtime_tab_instance):
    # Function Description:
    # Toggles the style of the selected device button to create a blinking effect.
    if not showtime_tab_instance.is_loop_running or not showtime_tab_instance.currently_blinking_button or not showtime_tab_instance.currently_blinking_button.winfo_exists():
        return
        
    current_style = showtime_tab_instance.currently_blinking_button.cget('style')
    
    if current_style == 'DeviceButton.Blinking.TButton':
        device_name = showtime_tab_instance.currently_blinking_button.cget('text').split('\n')[0]
        device_data = showtime_tab_instance.markers_data[showtime_tab_instance.markers_data['NAME'] == device_name].iloc[0]
        peak_value = device_data.get('Peak')
        
        if pd.notna(peak_value):
            peak_value = float(peak_value)
            if -130 <= peak_value < -80:
                new_style = 'Red.TButton'
            elif -80 <= peak_value < -50:
                new_style = 'Orange.TButton'
            elif peak_value >= -50:
                new_style = 'Green.TButton'
            else:
                new_style = 'LocalPreset.TButton'
        else:
            new_style = 'LocalPreset.TButton'
    else:
        new_style = 'DeviceButton.Blinking.TButton'
    
    showtime_tab_instance.currently_blinking_button.config(style=new_style)
    showtime_tab_instance.blinking_button_job = showtime_tab_instance.after(200, lambda: _blink_device_button(showtime_tab_instance))

def _update_control_styles(showtime_tab_instance):
    # Function Description:
    # Updates the style of control buttons to reflect the current state.
    debug_log(message=f"Updating control button styles.",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)
    current_span_str = showtime_tab_instance.span_var.get()
    for span_val, button in showtime_tab_instance.span_buttons.items():
        if button.winfo_exists():
            style = 'ControlButton.Active.TButton' if float(span_val) == float(current_span_str) else 'ControlButton.Inactive.TButton'
            button.configure(style=style)

    current_rbw_str = showtime_tab_instance.rbw_var.get()
    for rbw_val, button in showtime_tab_instance.rbw_buttons.items():
        if button.winfo_exists():
            style = 'ControlButton.Active.TButton' if float(rbw_val) == float(current_rbw_str) else 'ControlButton.Inactive.TButton'
            button.configure(style=style)
    
    if showtime_tab_instance.trace_buttons['Live'].winfo_exists():
        showtime_tab_instance.trace_buttons['Live'].configure(style='ControlButton.Active.TButton' if showtime_tab_instance.trace_live_mode.get() else 'ControlButton.Inactive.TButton')
    if showtime_tab_instance.trace_buttons['Max Hold'].winfo_exists():
        showtime_tab_instance.trace_buttons['Max Hold'].configure(style='ControlButton.Active.TButton' if showtime_tab_instance.trace_max_hold_mode.get() else 'ControlButton.Inactive.TButton')
    if showtime_tab_instance.trace_buttons['Min Hold'].winfo_exists():
        showtime_tab_instance.trace_buttons['Min Hold'].configure(style='ControlButton.Active.TButton' if showtime_tab_instance.trace_min_hold_mode.get() else 'ControlButton.Inactive.TButton')
    
    if showtime_tab_instance.loop_stop_button.winfo_exists():
        if showtime_tab_instance.is_loop_running:
            showtime_tab_instance.loop_stop_button.config(state=tk.NORMAL)
        else:
            showtime_tab_instance.loop_stop_button.config(state=tk.DISABLED)

def on_span_button_click(showtime_tab_instance, span_hz):
    # Function Description:
    # Handles a span button click.
    debug_log(message=f"A span button has been clicked. Updating the instrument's span to {span_hz} Hz!",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)
    showtime_tab_instance.span_var.set(str(span_hz))
    _update_control_styles(showtime_tab_instance)
    if showtime_tab_instance.app_instance and showtime_tab_instance.app_instance.inst:
        try:
            with showtime_tab_instance.instrument_lock:
                set_span_logic(app_instance=showtime_tab_instance.app_instance, span_hz=float(span_hz), console_print_func=showtime_tab_instance.console_print_func)
            if showtime_tab_instance.selected_device_freq is not None and showtime_tab_instance.is_loop_running:
                showtime_tab_instance.after_cancel(showtime_tab_instance.marker_trace_loop_job)
                start_device_trace_loop(showtime_tab_instance, center_freq_hz=showtime_tab_instance.selected_device_freq, span_hz=float(span_hz), button_to_blink=showtime_tab_instance.currently_blinking_button)
        except (ValueError, TypeError) as e:
            debug_log(f"A ValueError or TypeError has corrupted our span logic! Error: {e}",
                      file=f"{os.path.basename(__file__)}",
                      version=current_version,
                      function=inspect.currentframe().f_code.co_name, special=True)
            pass
    save_config(config=showtime_tab_instance.app_instance.config, file_path=showtime_tab_instance.app_instance.CONFIG_FILE_PATH, console_print_func=showtime_tab_instance.console_print_func, app_instance=showtime_tab_instance.app_instance)

def on_rbw_button_click(showtime_tab_instance, rbw_hz):
    # Function Description:
    # Handles an RBW button click.
    debug_log(message=f"An RBW button has been clicked. Setting the RBW to {rbw_hz} Hz!",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)
    showtime_tab_instance.rbw_var.set(str(rbw_hz))
    _update_control_styles(showtime_tab_instance)
    if showtime_tab_instance.app_instance and showtime_tab_instance.app_instance.inst:
        try:
            with showtime_tab_instance.instrument_lock:
                set_rbw_logic(app_instance=showtime_tab_instance.app_instance, rbw_hz=float(rbw_hz), console_print_func=showtime_tab_instance.console_print_func)
        except (ValueError, TypeError) as e:
            debug_log(f"An RBW ValueError or TypeError! It's a disaster! Error: {e}",
                      file=f"{os.path.basename(__file__)}",
                      version=current_version,
                      function=inspect.currentframe().f_code.co_name, special=True)
            pass
    save_config(config=showtime_tab_instance.app_instance.config, file_path=showtime_tab_instance.app_instance.CONFIG_FILE_PATH, console_print_func=showtime_tab_instance.console_print_func, app_instance=showtime_tab_instance.app_instance)

def on_trace_button_click(showtime_tab_instance, trace_var):
    # Function Description:
    # Handles a trace button click.
    debug_log(message=f"A trace mode button has been toggled.",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)
    trace_var.set(not trace_var.get())
    _update_control_styles(showtime_tab_instance)
    if showtime_tab_instance.app_instance and showtime_tab_instance.app_instance.inst:
        with showtime_tab_instance.instrument_lock:
            set_trace_modes_logic(app_instance=showtime_tab_instance.app_instance, live_mode=showtime_tab_instance.trace_live_mode.get(), max_hold_mode=showtime_tab_instance.trace_max_hold_mode.get(), min_hold_mode=showtime_tab_instance.trace_min_hold_mode.get(), console_print_func=showtime_tab_instance.console_print_func)
    save_config(config=showtime_tab_instance.app_instance.config, file_path=showtime_tab_instance.app_instance.CONFIG_FILE_PATH, console_print_func=showtime_tab_instance.console_print_func, app_instance=showtime_tab_instance.app_instance)

def on_poke_action(showtime_tab_instance):
    # Function Description:
    # Handles the Poke button action.
    debug_log(message=f"The 'Poke' button has been pressed! Prepare for a new frequency point! 🎯",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=inspect.currentframe().f_code.co_name)
    if showtime_tab_instance.app_instance and showtime_tab_instance.app_instance.inst:
        try:
            freq_mhz = showtime_tab_instance.poke_freq_var.get()
            freq_hz = float(freq_mhz) * MHZ_TO_HZ
            
            poke_marker_name = f"POKE: {freq_mhz} MHz"
            
            span_hz = float(showtime_tab_instance.span_var.get())
            with showtime_tab_instance.instrument_lock:
                set_span_logic(showtime_tab_instance.app_instance, span_hz, console_log)
                set_trace_modes_logic(showtime_tab_instance.app_instance, showtime_tab_instance.trace_live_mode.get(), showtime_tab_instance.trace_max_hold_mode.get(), showtime_tab_instance.trace_min_hold_mode.get(), console_log)
                set_frequency_logic(showtime_tab_instance.app_instance, freq_hz, console_log)
                set_marker_logic(showtime_tab_instance.app_instance, freq_hz, poke_marker_name, console_log)
            
            showtime_tab_instance.selected_device_unique_id = None
            showtime_tab_instance.selected_device_name = poke_marker_name
            showtime_tab_instance.selected_device_freq = freq_hz
            
            _update_device_button_styles(showtime_tab_instance)
            
            if showtime_tab_instance.is_loop_running:
                stop_loop_action(showtime_tab_instance)
                
            try:
                delay = int(showtime_tab_instance.loop_delay_var.get())
                showtime_tab_instance.loop_counter_var.set(0)
                start_device_trace_loop(showtime_tab_instance, center_freq_hz=freq_hz, span_hz=span_hz)
            except (ValueError, TypeError) as e:
                showtime_tab_instance.console_print_func(f"❌ Error starting marker trace loop after poke: {e}")
                debug_log(f"Dastardly bug! A TypeError or ValueError has struck our brave poke loop! Error: {e}",
                          file=f"{os.path.basename(__file__)}",
                          version=current_version,
                          function=inspect.currentframe().f_code.co_name)
        except (ValueError, TypeError) as e:
            showtime_tab_instance.console_print_func(f"Invalid POKE frequency: {e}")
            debug_log(f"Captain, the frequency given is gibberish! Error: {e}",
                      file=f"{os.path.basename(__file__)}",
                      version=current_version,
                      function=inspect.currentframe().f_code.co_name, special=True)
