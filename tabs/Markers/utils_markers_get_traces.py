# utils/utils_markers_get_traces.py
#
# This file contains the logic for retrieving trace data from a connected instrument
# and displaying it in the scan monitor plots.
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
# Version 20250812.225701.1 (FIXED: Added 'showtime_tab_instance' parameter to correctly access trace mode variables.)

current_version = "20250812.225701.1"
current_version_hash = (20250812 * 225701 * 1)

import inspect
import os
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log
from display.utils_display_monitor import update_top_plot, update_medium_plot, update_bottom_plot
from tabs.Instrument.Yakety_Yak import YakGet 
from ref.frequency_bands import MHZ_TO_HZ, KHZ_TO_HZ

# A global counter to manage the trace update cycle state.
_trace_update_cycle_counter = 0

def get_marker_traces(app_instance, showtime_tab_instance, console_print_func, center_freq_hz, span_hz, device_name=None):
    """
    Function Description:
    Retrieves and displays the live, max hold, and min hold traces from the instrument.
    This function has been refactored to be more robust, checking for valid data and
    handling different trace modes with a simple update cycle counter.

    Inputs:
    - app_instance (object): A reference to the main application instance.
    - showtime_tab_instance (object): A reference to the ShowtimeTab instance to access its state variables.
    - console_print_func (function): A function to print to the GUI console.
    - center_freq_hz (int): The center frequency for the scan in Hz.
    - span_hz (int): The span for the scan in Hz.
    - device_name (str, optional): The name of the device being monitored.
                                     Used for plot titles.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message="Getting marker traces with a specific update ratio. The timing must be perfect! ⏱️",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)

    # Calculate start and end frequencies for the plots
    start_freq_hz = center_freq_hz - (span_hz / 2)
    end_freq_hz = center_freq_hz + (span_hz / 2)
    start_freq_mhz = start_freq_hz / MHZ_TO_HZ
    end_freq_mhz = end_freq_hz / MHZ_TO_HZ

    global _trace_update_cycle_counter
    _trace_update_cycle_counter += 1

    scan_monitor_tab = app_instance.scan_monitor_tab
    if not scan_monitor_tab:
        console_print_func("❌ Error: Scan Monitor tab not found. Cannot update plots.")
        debug_log("CRITICAL ERROR: app_instance.scan_monitor_tab is None. The plots are lost at sea!",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function, special=True)
        return

    # --- Live Trace (Trace 1) ---
    plot_title = f"Live: {device_name}" if device_name else "Live Scan"
    
    # CORRECTED: Access trace mode variables from the showtime_tab_instance
    if showtime_tab_instance.trace_live_mode.get():
        trace_1_data = get_trace_1_data(app_instance=app_instance, console_print_func=console_print_func, start_freq_hz=start_freq_hz, end_freq_hz=end_freq_hz)
        update_top_plot(scan_monitor_tab, data=trace_1_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=plot_title)
    else:
        update_top_plot(scan_monitor_tab, data=None, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title="Live Scan not active")

    # --- Max Hold Trace (Trace 2) ---
    plot_title = f"Max Hold: {device_name}" if device_name else "Max Hold Scan"
    
    # CORRECTED: Access trace mode variables from the showtime_tab_instance
    if showtime_tab_instance.trace_max_hold_mode.get():
        trace_2_data = get_trace_2_data(app_instance=app_instance, console_print_func=console_print_func, start_freq_hz=start_freq_hz, end_freq_hz=end_freq_hz)
        update_medium_plot(scan_monitor_tab, data=trace_2_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=plot_title)
    else:
        update_medium_plot(scan_monitor_tab, data=None, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title="Max Hold not active")

    # --- Min Hold Trace (Trace 3) ---
    plot_title = f"Min Hold: {device_name}" if device_name else "Min Hold Scan"

    # CORRECTED: Access trace mode variables from the showtime_tab_instance
    if showtime_tab_instance.trace_min_hold_mode.get() and _trace_update_cycle_counter % 10 == 0:
        trace_3_data = get_trace_3_data(app_instance=app_instance, console_print_func=console_print_func, start_freq_hz=start_freq_hz, end_freq_hz=end_freq_hz)
        update_bottom_plot(scan_monitor_tab, data=trace_3_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=plot_title)
    elif not showtime_tab_instance.trace_min_hold_mode.get():
        update_bottom_plot(scan_monitor_tab, data=None, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title="Min Hold not active")

def get_trace_1_data(app_instance, console_print_func, start_freq_hz, end_freq_hz):
    """
    Function Description:
    Retrieves Trace 1 (Live) data from the instrument.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message="Attempting to get Trace 1 data.",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)

    raw_data_string = YakGet(app_instance=app_instance, command_type="TRACE/1/DATA", console_print_func=console_print_func)
    
    if raw_data_string is None or raw_data_string == "FAILED":
        console_print_func("❌ Failed to retrieve Trace 1 data from instrument.")
        return None
        
    return _process_trace_data(raw_data_string, start_freq_hz, end_freq_hz, console_print_func)

def get_trace_2_data(app_instance, console_print_func, start_freq_hz, end_freq_hz):
    """
    Function Description:
    Retrieves Trace 2 (Max Hold) data from the instrument.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message="Attempting to get Trace 2 data.",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)
    
    raw_data_string = YakGet(app_instance=app_instance, command_type="TRACE/2/DATA", console_print_func=console_print_func)
    
    if raw_data_string is None or raw_data_string == "FAILED":
        console_print_func("❌ Failed to retrieve Trace 2 data from instrument.")
        return None
    
    return _process_trace_data(raw_data_string, start_freq_hz, end_freq_hz, console_print_func)

def get_trace_3_data(app_instance, console_print_func, start_freq_hz, end_freq_hz):
    """
    Function Description:
    Retrieves Trace 3 (Min Hold) data from the instrument.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message="Attempting to get Trace 3 data.",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)

    raw_data_string = YakGet(app_instance=app_instance, command_type="TRACE/3/DATA", console_print_func=console_print_func)
    
    if raw_data_string is None or raw_data_string == "FAILED":
        console_print_func("❌ Failed to retrieve Trace 3 data from instrument.")
        return None
    
    return _process_trace_data(raw_data_string, start_freq_hz, end_freq_hz, console_print_func)

def _process_trace_data(raw_data_string, start_freq_hz, end_freq_hz, console_print_func):
    """
    Function Description:
    Processes a raw comma-separated string of trace amplitude data into
    a list of (frequency, amplitude) pairs. It gracefully handles parsing errors.
    
    Inputs:
    - raw_data_string (str): A comma-separated string of amplitude values from the instrument.
    - start_freq_hz (int): The starting frequency of the trace in Hz.
    - end_freq_hz (int): The ending frequency of the trace in Hz.
    - console_print_func (function): A function to print to the GUI console.
    
    Returns:
    - list or None: A list of tuples `(frequency_mhz, amplitude_dbm)` or None on failure.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message="Processing raw trace data into frequency/amplitude pairs. This is a crucial step.",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)

    if not raw_data_string or "FAILED" in raw_data_string:
        console_print_func("❌ Received invalid data from the instrument. Cannot process trace.")
        debug_log(f"Received invalid data from the instrument: '{raw_data_string}'. Aborting processing.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function, special=True)
        return None

    try:
        amplitudes_dbm = [float(val) for val in raw_data_string.split(',')]
        
        num_points = len(amplitudes_dbm)
        if num_points <= 1:
            console_print_func("⚠️ Received insufficient data points from the instrument. Cannot create a meaningful trace.")
            debug_log(f"Insufficient data points received ({num_points}). A trace needs more substance!",
                      file=f"{os.path.basename(__file__)} - {current_version}",
                      version=current_version,
                      function=current_function, special=True)
            return None
            
        freq_points = np.linspace(start_freq_hz, end_freq_hz, num_points)
        
        processed_data = list(zip(freq_points / MHZ_TO_HZ, amplitudes_dbm))

        debug_log(f"Successfully processed trace data. First 5 points: {processed_data[:5]}...",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
        return processed_data

    except ValueError as e:
        console_print_func(f"❌ Failed to parse trace data string. Error: {e}")
        debug_log(f"ValueError: could not convert string to float: '{raw_data_string.split(',')}'... Failed to parse data string. Error: {e}",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function, special=True)
        return None
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred while processing trace data: {e}")
        debug_log(f"An unexpected error occurred: {e}",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function, special=True)
        return None
