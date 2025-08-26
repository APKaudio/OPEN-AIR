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
# Version 20250824.010400.1
# UPDATED: The execute_trace_action function now correctly calls handle_trace_modes_beg to set the new mode on the instrument before fetching data.
# UPDATED: The trace mode mapping now correctly uses the mode strings defined in the new MarkerTab config.
# FIXED: The execute_trace_action function now saves the config after changing trace modes.
# FIXED: Corrected the AttributeErrors in `_get_and_plot_traces` by retrieving
#        frequency and span values from the `app_instance.config` object.

import os
import inspect
import pandas as pd
import tkinter as tk
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log

from yak.utils_yaknab_handler import handle_all_traces_nab
from yak.utils_yakbeg_handler import handle_trace_modes_beg
from settings_and_config.config_manager_save import save_program_config 

from .utils_showtime_plot import plot_all_traces
from process_math.math_frequency_translation import MHZ_TO_HZ

# --- Versioning ---
w = 20250824
x_str = '010400'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"

def sync_trace_modes(traces_tab_instance):
    # [Synchronizes the trace mode buttons with the instrument's current state.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function="sync_trace_modes")
    
    showtime_tab = traces_tab_instance.showtime_tab_instance
    app_instance = showtime_tab.app_instance
    console_print_func = showtime_tab.console_print_func

    # Placeholder for getting current trace modes from instrument
    current_modes = ['Live', 'Max Hold', 'Min Hold']
    
    for button_name in traces_tab_instance.trace_buttons.keys():
        if button_name in current_modes:
            traces_tab_instance.trace_buttons[button_name].config(style='ControlButton.Active.TButton')
        else:
            traces_tab_instance.trace_buttons[button_name].config(style='ControlButton.Inactive.TButton')
            
    debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function="sync_trace_modes")

def execute_trace_action(traces_tab_instance, action_type):
    # [Orchestrates the process of fetching and plotting traces based on user action.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function} with action_type: {action_type}", file=f"{os.path.basename(__file__)}", version=current_version, function="execute_trace_action")
    
    # FIXED: Access the parent ShowtimeParentTab instance directly from the child tab
    showtime_tab = traces_tab_instance.showtime_tab_instance

    # Set the instrument's trace mode based on the button clicked
    trace_mode_map = {
        'all': ['WRITE', 'MAXHold', 'MINHold'],
        'live': ['WRITE', 'BLANK', 'BLANK', 'BLANK'],
        'max': ['BLANK', 'MAXHold', 'BLANK', 'BLANK'],
        'min': ['BLANK', 'BLANK', 'MINHold', 'BLANK']
    }
    
    selected_modes = trace_mode_map.get(action_type, [])
    
    # NEW: Call handle_trace_modes_beg to set the modes on the instrument
    debug_log(f"Calling YakBeg to set trace modes on the instrument. ⚡",
                file=f"{os.path.basename(__file__)}",
                version=current_version,
                function=current_function)
    handle_trace_modes_beg(showtime_tab.app_instance, selected_modes, showtime_tab.console_print_func)
    
    # FIXED: Pass the action_type to _get_and_plot_traces
    _get_and_plot_traces(traces_tab_instance, action_type)
    
    # FIXED: Save config after a successful trace action
    save_program_config (config=showtime_tab.app_instance.config,
                file_path=showtime_tab.app_instance.CONFIG_FILE_PATH,
                console_print_func=showtime_tab.console_print_func,
                app_instance=showtime_tab.app_instance)

    debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function="execute_trace_action")

def _get_and_plot_traces(traces_tab_instance, view_name):
    # [Fetches trace data from the instrument and passes it to the plotting utility.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function="_get_and_plot_traces")
    
    # FIXED: Access the parent ShowtimeParentTab instance directly from the child tab
    showtime_tab = traces_tab_instance.showtime_tab_instance
    app_instance = showtime_tab.app_instance
    console_print_func = showtime_tab.console_print_func
    
    # CORRECTED: Retrieve center and span values from the config file, which is the correct source of truth.
    # The previous code was trying to access attributes on orchestrator_logic that do not exist.
    center_freq_MHz = float(app_instance.config.get('InstrumentSettings', 'center_freq_MHz', fallback='1500'))
    span_freq_MHz = float(app_instance.config.get('InstrumentSettings', 'span_freq_MHz', fallback='3000'))
    
    start_freq_MHz = (center_freq_MHz - span_freq_MHz / 2)
    stop_freq_MHz = (center_freq_MHz + span_freq_MHz / 2)
    
    try:
        # 📖 Read Data: Fetch the data from the instrument.
        debug_log(message=f"📖 Reading Data: Fetching all traces from the instrument via NAB handler.", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        trace_data = handle_all_traces_nab(app_instance, console_print_func)
        
        # If data is successfully retrieved, pass it to the plotter
        if trace_data:
            plot_all_traces(showtime_tab_instance=showtime_tab, trace_data_dict=trace_data, view_name=view_name, start_freq_MHz=start_freq_MHz, stop_freq_MHz=stop_freq_MHz)
        
    except Exception as e:
        console_print_func(f"❌ Error getting trace data: {e}")
        debug_log(message=f"Shiver me timbers, the trace data be lost at sea! The error be: {e}",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function="execute_trace_action")