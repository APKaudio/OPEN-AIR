# yak/utils_showtime_trace.py
#
# This utility file centralizes all logic for fetching trace data from the instrument,
# handling trace mode configurations, and updating the corresponding display plots.
# It acts as a high-level API for the UI to trigger trace actions.
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
# Version 20250819.141500.1
# REFACTORED: Moved all trace acquisition and plotting logic from other modules here to centralize control.
# NEW: Implemented a top-level `execute_trace_action` function to orchestrate trace calls based on UI state.

current_version = "20250819.141500.1"
current_version_hash = (20250819 * 141500 * 1)

import os
import inspect
import pandas as pd
import tkinter as tk
from ref.frequency_bands import MHZ_TO_HZ
from display.debug_logic import debug_log
from display.console_logic import console_log

# MODIFIED: Added new YakBeg and YakNab handlers for trace data
from yak.utils_yakbeg_handler import handle_trace_data_beg
from yak.utils_yaknab_handler import handle_all_traces_nab

# MODIFIED: Import display utilities
from display.utils_display_monitor import update_top_plot, update_middle_plot, update_bottom_plot
from display.utils_scan_view import update_single_plot


def _get_current_view_details(controls_frame):
    # [Helper function to determine the current frequency span and title based on UI selection.]
    # This is a copy from utils_showtime_controls.py to keep this file self-contained.
    debug_log(f"Entering _get_current_view_details", file=f"{os.path.basename(__file__)}", version=current_version, function="_get_current_view_details")
    zgd_frame = controls_frame.app_instance.tabs_parent.tab_content_frames['Markers'].showtime_tab.zgd_frame
    
    view_name = "All Markers"
    start_freq_mhz = None
    stop_freq_mhz = None

    try:
        if hasattr(zgd_frame, 'selected_device_info') and zgd_frame.selected_device_info:
            device = zgd_frame.selected_device_info
            center_mhz = device.get('CENTER')
            span_hz = int(float(controls_frame.span_var.get()))
            span_mhz = span_hz / MHZ_TO_HZ
            start_freq_mhz = center_mhz - (span_mhz / 2)
            stop_freq_mhz = center_mhz + (span_mhz / 2)
            view_name = f"Device: {device.get('NAME', 'N/A')}"

        elif zgd_frame.selected_group:
            active_button_key = 'Group'
            devices = zgd_frame.structured_data.get(zgd_frame.selected_zone, {}).get(zgd_frame.selected_group, [])
            freqs = [d.get('CENTER') for d in devices if isinstance(d.get('CENTER'), (int, float))]
            if freqs:
                start_freq_mhz, stop_freq_mhz = min(freqs), max(freqs)
            view_name = f"Group: {zgd_frame.selected_group}"

        elif zgd_frame.selected_zone:
            active_button_key = 'Zone'
            devices = zgd_frame._get_all_devices_in_zone(zgd_frame.structured_data, zgd_frame.selected_zone)
            freqs = [d.get('CENTER') for d in devices if isinstance(d.get('CENTER'), (int, float))]
            if freqs:
                start_freq_mhz, stop_freq_mhz = min(freqs), max(freqs)
            view_name = f"Zone: {zgd_frame.selected_zone}"
        
        else: # All Markers
            devices = zgd_frame._get_all_devices_in_zone(zgd_frame.structured_data, None)
            freqs = [d.get('CENTER') for d in devices if isinstance(d.get('CENTER'), (int, float))]
            if freqs:
                start_freq_mhz, stop_freq_mhz = min(freqs), max(freqs)
            view_name = "All Markers"

        debug_log(f"Current view: {view_name}, Start: {start_freq_mhz} MHz, Stop: {stop_freq_mhz} MHz", file=f"{os.path.basename(__file__)}", version=current_version, function="_get_current_view_details")
        return view_name, start_freq_mhz, stop_freq_mhz

    except Exception as e:
        controls_frame.console_print_func(f"❌ Could not determine current frequency view: {e}", "ERROR")
        return None, None, None


def execute_trace_action(controls_frame):
    # [A new public method to execute the correct trace action based on which button is active.]
    debug_log(f"Entering execute_trace_action. Executing the selected trace handler.", file=f"{os.path.basename(__file__)}", version=current_version, function="execute_trace_action")
    
    # NEW: Check if any button is active. If not, default to 'Get All'
    if not controls_frame.toggle_get_all_traces.get() and not controls_frame.toggle_get_live_trace.get() and not controls_frame.toggle_get_max_traces.get():
        controls_frame.console_print_func("No trace action button is currently active. Defaulting to 'Get All Traces'.")
        controls_frame.toggle_get_all_traces.set(True)
        controls_frame._update_button_styles() # Update the UI to show 'Get All' is active

    if controls_frame.toggle_get_all_traces.get():
        on_get_all_traces_click(controls_frame)
    elif controls_frame.toggle_get_live_trace.get():
        on_get_live_trace_click(controls_frame)
    elif controls_frame.toggle_get_max_traces.get():
        on_get_max_trace_click(controls_frame)
    else:
        controls_frame.console_print_func("No trace action button is currently active.")
        debug_log(f"No trace action button is currently active. Nothing to execute!", file=f"{os.path.basename(__file__)}", version=current_version, function="execute_trace_action")

def on_get_all_traces_click(controls_frame):
    # [Handles 'Get Live, Max and Min' button click.]
    debug_log(f"Entering on_get_all_traces_click", file=f"{os.path.basename(__file__)}", version=current_version, function="on_get_all_traces_click")
    view_name, start_freq_mhz, stop_freq_mhz = _get_current_view_details(controls_frame)
    if not all([view_name, start_freq_mhz, stop_freq_mhz]):
        controls_frame.console_print_func("❌ Cannot get traces, no valid frequency range selected.", "ERROR")
        return
    
    # ADDED DEBUG: Log the parameters before calling the handler
    debug_log(f"Attempting to retrieve all traces. Parameters: Start_MHz={start_freq_mhz}, Stop_MHz={stop_freq_mhz}",
              file=f"{os.path.basename(__file__)}", version=current_version, function="on_get_all_traces_click", special=True)
              
    trace_data_dict = handle_all_traces_nab(controls_frame.app_instance, controls_frame.console_print_func)
    
    # ADDED DEBUG: Log the return value from the handler
    debug_log(f"Returned from handle_all_traces_nab. Result is a {type(trace_data_dict)}. Value: {trace_data_dict}",
              file=f"{os.path.basename(__file__)}", version=current_version, function="on_get_all_traces_click", special=True)

    if trace_data_dict and "TraceData" in trace_data_dict:
        # CORRECTED: Get the monitor tab reference directly from the app instance
        monitor_tab = controls_frame.app_instance.display_parent_tab.bottom_pane.scan_monitor_tab
        if monitor_tab:
            # The NAB handler returns a dict of dataframes, so we pass that directly
            df1 = pd.DataFrame(trace_data_dict["TraceData"]["Trace1"], columns=['Frequency_Hz', 'Power_dBm'])
            update_top_plot(monitor_tab, df1, start_freq_mhz, stop_freq_mhz, f"Live Trace - {view_name}")
            
            df2 = pd.DataFrame(trace_data_dict["TraceData"]["Trace2"], columns=['Frequency_Hz', 'Power_dBm'])
            update_middle_plot(monitor_tab, df2, start_freq_mhz, stop_freq_mhz, f"Max Hold - {view_name}")

            df3 = pd.DataFrame(trace_data_dict["TraceData"]["Trace3"], columns=['Frequency_Hz', 'Power_dBm'])
            update_bottom_plot(monitor_tab, df3, start_freq_mhz, stop_freq_mhz, f"Min Hold - {view_name}")
            controls_frame.console_print_func("✅ Successfully updated monitor with all three traces.", "SUCCESS")
            # ADDED: Switch to the Scan Monitor tab
            controls_frame.app_instance.display_parent_tab.change_display_tab('Monitor')
        else:
            controls_frame.console_print_func("❌ Scan Monitor tab not found.", "ERROR")
    else:
        controls_frame.console_print_func("❌ Failed to retrieve trace data.", "ERROR")
        # ADDED DEBUG: A detailed debug log for the failure
        debug_log(f"Arrr, the plotting operation be capsized! The data from the handler be all wrong! Returned a {type(trace_data_dict)} when a dict was expected. 🏴‍☠️",
                 file=f"{os.path.basename(__file__)}", version=current_version, function="on_get_all_traces_click")

def on_get_live_trace_click(controls_frame):
    # [Handles 'Get Live' button click.]
    debug_log(f"Entering on_get_live_trace_click", file=f"{os.path.basename(__file__)}", version=current_version, function="on_get_live_trace_click")
    view_name, start_freq_mhz, stop_freq_mhz = _get_current_view_details(controls_frame)
    if not all([view_name, start_freq_mhz, stop_freq_mhz]):
        controls_frame.console_print_func("❌ Cannot get trace, no valid frequency range selected.", "ERROR")
        return

    trace_data = handle_trace_data_beg(controls_frame.app_instance, 1, start_freq_mhz, stop_freq_mhz, controls_frame.console_print_func)

    if trace_data:
        # CORRECTED: Get the scan view tab reference directly from the app instance
        scan_view_tab = controls_frame.app_instance.display_parent_tab.bottom_pane.scan_view_tab
        if scan_view_tab:
            # The handler now returns a list of tuples, convert to DataFrame
            df = pd.DataFrame(trace_data, columns=['Frequency_Hz', 'Power_dBm'])
            # MODIFIED: Passed 'yellow' for live trace
            update_single_plot(scan_view_tab, df, start_freq_mhz, stop_freq_mhz, f"Live Trace - {view_name}", line_color='yellow')
            controls_frame.console_print_func("✅ Successfully updated Scan View with live trace.", "SUCCESS")
            # ADDED: Switch to the Scan View tab
            controls_frame.app_instance.display_parent_tab.change_display_tab('View')
        else:
            controls_frame.console_print_func("❌ Scan View tab not found.", "ERROR")
    else:
        controls_frame.console_print_func("❌ Failed to retrieve live trace data.", "ERROR")


def on_get_max_trace_click(controls_frame):
    # [Handles 'Get Max' button click.]
    debug_log(f"Entering on_get_max_trace_click", file=f"{os.path.basename(__file__)}", version=current_version, function="on_get_max_trace_click")
    view_name, start_freq_mhz, stop_freq_mhz = _get_current_view_details(controls_frame)
    if not all([view_name, start_freq_mhz, stop_freq_mhz]):
        controls_frame.console_print_func("❌ Cannot get trace, no valid frequency range selected.", "ERROR")
        return

    trace_data = handle_trace_data_beg(controls_frame.app_instance, 2, start_freq_mhz, stop_freq_mhz, controls_frame.console_print_func)

    if trace_data:
        # CORRECTED: Get the scan view tab reference directly from the app instance
        scan_view_tab = controls_frame.app_instance.display_parent_tab.bottom_pane.scan_view_tab
        if scan_view_tab:
            # The handler now returns a list of tuples, convert to DataFrame
            df = pd.DataFrame(trace_data, columns=['Frequency_Hz', 'Power_dBm'])
            # MODIFIED: Passed 'green' for max hold trace
            update_single_plot(scan_view_tab, df, start_freq_mhz, stop_freq_mhz, f"Max Hold - {view_name}", line_color='green')
            controls_frame.console_print_func("✅ Successfully updated Scan View with max hold trace.", "SUCCESS")
            # ADDED: Switch to the Scan View tab
            controls_frame.app_instance.display_parent_tab.change_display_tab('View')
        else:
            controls_frame.console_print_func("❌ Scan View tab not found.", "ERROR")
    else:
        controls_frame.console_print_func("❌ Failed to retrieve max hold trace data.", "ERROR")
