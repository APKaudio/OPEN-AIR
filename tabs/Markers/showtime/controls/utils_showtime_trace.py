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
# Version 20250821.210000.1
# FIXED: Corrected the AttributeErrors by changing the way the `showtime_tab` and `controls_frame` instances are accessed.
# NEW: Added a 'min' option to the `trace_mode_map` for consistency.
# FIXED: Corrected versioning to adhere to project standards.
# NEW: Added debug logging for read data from the NAB handler.

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

# --- Versioning ---
current_version = "20250821.210000.1"
current_version_hash = (20250821 * 210000 * 1)
current_file = file=f"{os.path.basename(__file__)}"

def sync_trace_modes(traces_tab_instance):
    # [Synchronizes the trace mode buttons with the instrument's current state.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function="sync_trace_modes")
    
    showtime_tab = traces_tab_instance.showtime_tab_instance
    app_instance = showtime_tab.app_instance
    console_print_func = showtime_tab.console_print_func

    # Placeholder for getting current trace modes from instrument
    current_modes = ['Live', 'Max Hold', 'Min Hold']
    
    for button_name in traces_tab_instance.shared_state.trace_buttons.keys():
        if button_name in current_modes:
            traces_tab_instance.shared_state.trace_buttons[button_name].config(style='ControlButton.Active.TButton')
        else:
            traces_tab_instance.shared_state.trace_buttons[button_name].config(style='ControlButton.Inactive.TButton')
            
    debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function="sync_trace_modes")

def execute_trace_action(traces_tab_instance, action_type):
    # [Orchestrates the process of fetching and plotting traces based on user action.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function} with action_type: {action_type}", file=f"{os.path.basename(__file__)}", version=current_version, function="execute_trace_action")
    
    # FIXED: Access the parent ShowtimeParentTab instance directly from the child tab
    showtime_tab = traces_tab_instance.showtime_tab_instance

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
    
    # FIXED: Pass the action_type to _get_and_plot_traces
    _get_and_plot_traces(traces_tab_instance, action_type)
    
    debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function="execute_trace_action")

def _get_and_plot_traces(traces_tab_instance, view_name):
    # [Fetches trace data from the instrument and passes it to the plotting utility.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function="_get_and_plot_traces")
    
    # FIXED: Access the parent ShowtimeParentTab instance directly from the child tab
    showtime_tab = traces_tab_instance.showtime_tab_instance
    app_instance = showtime_tab.app_instance
    console_print_func = showtime_tab.console_print_func
    
    # Corrected references to get scan variables from the orchestrator logic
    start_freq_mhz = (app_instance.orchestrator_logic.scan_center_freq_var.get() - app_instance.orchestrator_logic.scan_span_freq_var.get() / 2) / 1000000
    stop_freq_mhz = (app_instance.orchestrator_logic.scan_center_freq_var.get() + app_instance.orchestrator_logic.scan_span_freq_var.get() / 2) / 1000000
    
    try:
        # 📖 Read Data: Fetch the data from the instrument.
        debug_log(message=f"📖 Reading Data: Fetching all traces from the instrument via NAB handler.", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        trace_data = handle_all_traces_nab(app_instance, console_print_func)
        
        # If data is successfully retrieved, pass it to the plotter
        if trace_data:
            plot_all_traces(showtime_tab_instance=showtime_tab, trace_data_dict=trace_data, view_name=view_name, start_freq_mhz=start_freq_mhz, stop_freq_mhz=stop_freq_mhz)
        
    except Exception as e:
        console_print_func(f"❌ Error getting trace data: {e}")
        debug_log(message=f"Shiver me timbers, the trace data be lost at sea! The error be: {e}",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function="execute_trace_action")