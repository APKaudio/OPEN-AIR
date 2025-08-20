# tabs/Markers/showtime/controls/utils_showtime_trace.py
#
# This utility file centralizes all logic for fetching trace data from the instrument,
# handling trace mode configurations, and updating the corresponding display plots.
# It acts as a high-level API for the UI to trigger trace actions.
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
# Version 20250821.011000.1
# REFACTORED: All functions now directly access shared state from the parent
#             `showtime_tab_instance` via the `traces_tab_instance` passed as an argument.

current_version = "20250821.011000.1"
current_version_hash = (20250821 * 11000 * 1)

import os
import inspect
import pandas as pd
import tkinter as tk
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log

from yak.utils_yaknab_handler import handle_all_traces_nab
from yak.utils_yakbeg_handler import handle_trace_modes_beg

from tabs.Markers.showtime.controls.utils_showtime_plot import plot_all_traces
from process_math.math_frequency_translation import MHZ_TO_HZ

def sync_trace_modes(traces_tab_instance):
    # [Synchronizes the trace mode buttons with the instrument's current state.]
    debug_log(f"Entering sync_trace_modes", file=f"{os.path.basename(__file__)}", version=current_version, function="sync_trace_modes")
    
    showtime_tab = traces_tab_instance.controls_frame.showtime_tab_instance
    app_instance = showtime_tab.app_instance
    console_print_func = showtime_tab.console_print_func

    # Placeholder for getting current trace modes from instrument
    current_modes = ['Live', 'Max Hold', 'Min Hold']
    
    for button_name in traces_tab_instance.trace_buttons.keys():
        if button_name in current_modes:
            showtime_tab.trace_buttons[button_name].config(style='ControlButton.Active.TButton')
        else:
            showtime_tab.trace_buttons[button_name].config(style='ControlButton.Inactive.TButton')
            
    debug_log(f"Exiting sync_trace_modes", file=f"{os.path.basename(__file__)}", version=current_version, function="sync_trace_modes")

def execute_trace_action(traces_tab_instance, action_type):
    # [Orchestrates the process of fetching and plotting traces based on user action.]
    debug_log(f"Entering execute_trace_action with action_type: {action_type}", file=f"{os.path.basename(__file__)}", version=current_version, function="execute_trace_action")
    
    showtime_tab = traces_tab_instance.controls_frame.showtime_tab_instance

    # Set the instrument's trace mode based on the button clicked
    trace_mode_map = {
        'all': ['Live', 'Max Hold', 'Min Hold'],
        'live': ['Live'],
        'max': ['Max Hold'],
        'min': ['Min Hold']
    }
    
    selected_modes = trace_mode_map.get(action_type, [])
    
    # Placeholder for calling Yaknab handler to set trace modes on the instrument
    # handle_trace_modes_beg(showtime_tab.app_instance, selected_modes, showtime_tab.console_print_func)
    
    _get_and_plot_traces(traces_tab_instance, action_type)
    
    debug_log(f"Exiting execute_trace_action", file=f"{os.path.basename(__file__)}", version=current_version, function="execute_trace_action")

def _get_and_plot_traces(traces_tab_instance, view_name):
    # [Fetches trace data from the instrument and passes it to the plotting utility.]
    debug_log(f"Entering _get_and_plot_traces", file=f"{os.path.basename(__file__)}", version=current_version, function="_get_and_plot_traces")
    
    showtime_tab = traces_tab_instance.controls_frame.showtime_tab_instance
    app_instance = showtime_tab.app_instance
    console_print_func = showtime_tab.console_print_func
    
    # Corrected references to get scan variables from the orchestrator logic
    start_freq_mhz = (app_instance.scan_center_freq_var.get() - app_instance.scan_span_freq_var.get() / 2) / 1000000
    stop_freq_mhz = (app_instance.scan_center_freq_var.get() + app_instance.scan_span_freq_var.get() / 2) / 1000000
    
    try:
        # Fetch the data from the instrument
        trace_data = handle_all_traces_nab(app_instance, console_print_func)
        
        # If data is successfully retrieved, pass it to the plotter
        if trace_data:
            plot_all_traces(controls_frame=showtime_tab.controls_frame, trace_data_dict=trace_data, view_name=view_name, start_freq_mhz=start_freq_mhz, stop_freq_mhz=stop_freq_mhz)
        
    except Exception as e:
        console_print_func(f"❌ Error getting trace data: {e}")
        debug_log(f"Shiver me timbers, the trace data be lost at sea! The error be: {e}",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function="execute_trace_action")