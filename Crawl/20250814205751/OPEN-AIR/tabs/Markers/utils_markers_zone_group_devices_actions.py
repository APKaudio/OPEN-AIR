# FolderName/utils_markers_zone_group_devices_actions.py
#
# This file centralizes the high-level logic for the Showtime tab, including the
# orchestration of the marker scanning loop and the "focus device" functionality.
# It acts as a bridge between the GUI and the low-level instrument control utilities.
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
# Version 20250814.200000.5

current_version = "20250814.200000.5"
current_version_hash = (20250814 * 200000 * 5)

import os
import inspect
import time
import threading
import pandas as pd
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log
from tabs.Instrument.Yakety_Yak import YakSet, YakDo, YakNab
from tabs.Instrument.utils_yakbeg_handler import handle_marker_place_all_beg, handle_trace_data_beg, handle_freq_center_span_beg
from .utils_markers_files_zone_groups_devices import load_and_structure_markers_data
from .utils_markers_get_traces import get_marker_traces
from ref.frequency_bands import MHZ_TO_HZ, VBW_RBW_RATIO
from src.settings_and_config.config_manager import save_config

# Global state management for the loops
_peak_scan_loop_running = False
_focus_loop_running = False
_active_scan_thread = None
_active_focus_thread = None

def _get_all_devices_in_zone(structured_data, zone_name):
    # Combines all devices from all groups within a given zone.
    devices = []
    if structured_data and zone_name in structured_data:
        for group_name, group_devices in structured_data[zone_name].items():
            devices.extend(group_devices)
    return devices

def _calculate_zone_span(devices):
    # Calculates a suitable span and center frequency for a list of devices.
    if not devices:
        return 0, 0
    
    frequencies = [float(d.get('CENTER', 0)) for d in devices if d.get('CENTER') and d.get('CENTER') != 'N/A']
    if not frequencies:
        return 0, 0
        
    min_freq = min(frequencies)
    max_freq = max(frequencies)
    
    if min_freq == max_freq:
        center = min_freq
        span = 20 * MHZ_TO_HZ  # Default span of 20 MHz if only one device
    else:
        span = (max_freq - min_freq) * MHZ_TO_HZ + 20 * MHZ_TO_HZ # Add a 20 MHz buffer
        center = (min_freq + max_freq) / 2
        
    return int(center), int(span)


def _start_orchestrated_scan_loop(app_instance, showtime_tab_instance):
    # Starts the main orchestrated loop in a new thread.
    global _peak_scan_loop_running, _active_scan_thread
    
    if _peak_scan_loop_running:
        return
        
    _peak_scan_loop_running = True
    _active_scan_thread = threading.Thread(
        target=_orchestrated_scan_loop,
        args=(app_instance, showtime_tab_instance)
    )
    _active_scan_thread.daemon = True
    _active_scan_thread.start()


def _stop_scan_loops():
    # Stops all active scanning and focus loops.
    global _peak_scan_loop_running, _focus_loop_running
    _peak_scan_loop_running = False
    _focus_loop_running = False


def _orchestrated_scan_loop(app_instance, showtime_tab_instance):
    # Main loop for continuous peak scanning and trace updates.
    global _peak_scan_loop_running, _focus_loop_running
    
    source_file = os.path.basename(__file__)
    
    while _peak_scan_loop_running:
        if _focus_loop_running: # Do not run peak scan if focus is active
            time.sleep(1)
            continue
            
        orchestrator_status = app_instance.orchestrator_logic.get_status()
        app_instance.orchestrator_logic.log_check_in(source_file)

        if not orchestrator_status['is_running'] or orchestrator_status['is_paused']:
            time.sleep(1)
            continue
            
        if not showtime_tab_instance.zgd_frame.selected_zone:
            time.sleep(1)
            continue
            
        all_devices = _get_all_devices_in_zone(showtime_tab_instance.zgd_frame.structured_data, showtime_tab_instance.zgd_frame.selected_zone)
        
        if not all_devices:
            time.sleep(1)
            continue
            
        # Get the overall span and center for the zone to use for trace plots
        zone_center, zone_span = _calculate_zone_span(all_devices)
        zone_name = showtime_tab_instance.zgd_frame.selected_zone
        
        # Divide devices into chunks of 6
        chunks = [all_devices[i:i + 6] for i in range(0, len(all_devices), 6)]
        
        for i, chunk in enumerate(chunks):
            if not _peak_scan_loop_running: break
            
            # Extract frequencies from the chunk
            marker_freqs_mhz = [d.get('CENTER', 'N/A') for d in chunk]
            
            # Call YakBeg to get peak values and update markers
            peak_values = _get_peak_values_and_update_csv_logic(app_instance, chunk)
            
            # Update the UI buttons on the main thread
            app_instance.after(0, lambda: showtime_tab_instance.zgd_frame.update_device_buttons_with_peaks(peak_values))

            # Trigger trace updates based on loop count
            if i % 3 == 0:
                # Update Trace 1
                app_instance.after(0, lambda: get_marker_traces(app_instance, showtime_tab_instance.zgd_frame, showtime_tab_instance.console_print_func, center_freq_hz=zone_center, span_hz=zone_span, device_name=zone_name, trace_number=1))
            if i % 5 == 0:
                # Update Trace 2
                app_instance.after(0, lambda: get_marker_traces(app_instance, showtime_tab_instance.zgd_frame, showtime_tab_instance.console_print_func, center_freq_hz=zone_center, span_hz=zone_span, device_name=zone_name, trace_number=2))
            if i % 7 == 0:
                # Update Trace 3
                app_instance.after(0, lambda: get_marker_traces(app_instance, showtime_tab_instance.zgd_frame, showtime_tab_instance.console_print_func, center_freq_hz=zone_center, span_hz=zone_span, device_name=zone_name, trace_number=3))
            
            time.sleep(2) # Wait between chunks
        
    _peak_scan_loop_running = False

def _get_peak_values_and_update_csv_logic(app_instance, devices_to_process):
    # Handles calling YakBeg and parsing the response to update MARKERS.CSV
    pass # This function will contain the logic to call YakBeg and update the CSV


def focus_device(app_instance, showtime_tab_instance, device_name):
    # Initiates a continuous focus loop on a single device.
    global _focus_loop_running, _peak_scan_loop_running, _active_focus_thread
    
    _stop_scan_loops()
    
    _focus_loop_running = True
    
    _active_focus_thread = threading.Thread(
        target=_focus_loop,
        args=(app_instance, showtime_tab_instance, device_name)
    )
    _active_focus_thread.daemon = True
    _active_focus_thread.start()


def _focus_loop(app_instance, showtime_tab_instance, device_name):
    # The dedicated loop for focusing on a single device.
    global _focus_loop_running
    
    while _focus_loop_running:
        # Get the device's frequency
        device_info = next((d for d in _get_all_devices_in_zone(showtime_tab_instance.zgd_frame.structured_data, showtime_tab_instance.zgd_frame.selected_zone) if d['NAME'] == device_name), None)
        if not device_info:
            _focus_loop_running = False
            break
            
        center_freq_mhz = float(device_info.get('CENTER'))
        
        # Get the span from the UI controls, accessed via the ShowtimeTab instance
        span_hz = showtime_tab_instance.controls_frame.span_var.get()
        
        # Call YakBeg to set frequency and get traces
        handle_freq_center_span_beg(app_instance, center_freq_mhz * MHZ_TO_HZ, int(span_hz), showtime_tab_instance.console_print_func)
        
        # Get and plot traces 1, 2, and 3
        get_marker_traces(app_instance, showtime_tab_instance, showtime_tab_instance.console_print_func, center_freq_hz=center_freq_mhz * MHZ_TO_HZ, span_hz=int(span_hz), device_name=device_name, trace_number=1)
        get_marker_traces(app_instance, showtime_tab_instance, showtime_tab_instance.console_print_func, center_freq_hz=center_freq_mhz * MHZ_TO_HZ, span_hz=int(span_hz), device_name=device_name, trace_number=2)
        get_marker_traces(app_instance, showtime_tab_instance, showtime_tab_instance.console_print_func, center_freq_hz=center_freq_mhz * MHZ_TO_HZ, span_hz=int(span_hz), device_name=device_name, trace_number=3)

        time.sleep(1) # Loop every second