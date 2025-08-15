# FolderName/utils_markers_get_traces.py
#
# This file provides utility functions for retrieving trace data from a spectrum analyzer
# and processing it into a format suitable for plotting. It also handles retrieving
# traces for active markers.
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
# Version 20250814.000100.3

current_version = "20250814.000100.3"
current_version_hash = (20250814 * 100 * 3)

import os
import inspect
import pandas as pd
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log
from display.utils_display_monitor import update_bottom_plot, update_middle_plot, update_top_plot
from ref.frequency_bands import MHZ_TO_HZ

# NEW: Import the centralized YakGet command from the instrument utility
from yak.Yakety_Yak import YakGet

def _process_trace_data(raw_data_string, start_freq_hz, end_freq_hz, console_print_func):
    # Function Description:
    # Processes raw trace data string from the instrument into a pandas DataFrame.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Processing raw trace data string into a DataFrame. Let's make some sense of this glorious data!",
              file=f"{os.path.basename(__file__)} & {current_version}",
              version=current_version,
              function=current_function)

    try:
        if not raw_data_string:
            console_print_func("❌ No data received from the instrument to process.")
            return None

        # The data from the analyzer is a string of comma-separated floats
        power_levels_dbm = np.array([float(x) for x in raw_data_string.split(',')])

        # Get the number of data points
        num_points = len(power_levels_dbm)
        if num_points == 0:
            console_print_func("❌ Received an empty data set from the instrument.")
            return None

        # Create a frequency array based on the start, end, and number of points
        freqs_hz = np.linspace(start_freq_hz, end_freq_hz, num_points)

        # Create a DataFrame
        data_df = pd.DataFrame({
            'Frequency_Hz': freqs_hz,
            'Power_dBm': power_levels_dbm
        })

        console_print_func("✅ Successfully processed trace data into a DataFrame.")
        debug_log(f"Successfully processed trace data into a DataFrame with {num_points} points.",
                  file=f"{os.path.basename(__file__)} & {current_version}",
                  version=current_version,
                  function=current_function)
        return data_df

    except (ValueError, IndexError, TypeError) as e:
        console_print_func(f"❌ Failed to process trace data string. Error: {e}")
        debug_log(f"ValueError: could not convert string to float. Failed to parse data string. Error: {e}",
                  file=f"{os.path.basename(__file__)} & {current_version}",
                  version=current_version,
                  function=current_function, special=True)
        return None
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred while processing trace data: {e}")
        debug_log(f"An unexpected error occurred: {e}",
                  file=f"{os.path.basename(__file__)} & {current_version}",
                  version=current_version,
                  function=current_function, special=True)
        return None
    

def get_trace_data_by_number(app_instance, console_print_func, trace_number, start_freq_hz, end_freq_hz):
    # Function Description:
    # Retrieves trace data for a specific trace number using a single YakGet command.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Getting data for Trace {trace_number} from the instrument. A fantastic new approach!",
              file=f"{os.path.basename(__file__)} & {current_version}",
              version=current_version,
              function=current_function)
              
    trace_data_string = YakGet(app_instance=app_instance, command_type=f"TRACE/{trace_number}/DATA", console_print_func=console_print_func)
    
    if trace_data_string == "FAILED":
        return None
    
    return _process_trace_data(raw_data_string=trace_data_string, start_freq_hz=start_freq_hz, end_freq_hz=end_freq_hz, console_print_func=console_print_func)
    

def get_marker_traces(app_instance, showtime_tab_instance, console_print_func, center_freq_hz, span_hz, device_name, trace_number):
    # Function Description:
    # Gets a specific trace and updates the corresponding plot on the scan monitor tab.
    # FIXED: Function signature now correctly accepts all required parameters.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function} for trace {trace_number}. Retrieving traces for marker display. Oh, this is going to be good!",
              file=f"{os.path.basename(__file__)} & {current_version}",
              version=current_version,
              function=current_function)

    if not app_instance.inst:
        console_print_func("❌ No instrument connected. Cannot get traces.")
        debug_log(f"Error: No instrument connected. Trace retrieval failed.",
                  file=f"{os.path.basename(__file__)} & {current_version}",
                  version=current_version,
                  function=current_function)
        return

    # Calculate start and end frequencies from center and span
    start_freq_hz = center_freq_hz - (span_hz / 2)
    end_freq_hz = center_freq_hz + (span_hz / 2)
    
    start_freq_mhz = start_freq_hz / MHZ_TO_HZ
    end_freq_mhz = end_freq_hz / MHZ_TO_HZ
    
    plot_title = f"{device_name} - Traces ({start_freq_mhz:.3f} MHz to {end_freq_mhz:.3f} MHz)"
    
    # Get trace data using the new consolidated function
    # The function now handles a single trace at a time
    trace_df = get_trace_data_by_number(app_instance, console_print_func, trace_number, start_freq_hz, end_freq_hz)

    # Now, update the correct monitor plot based on trace_number
    if trace_df is not None:
        if trace_number == 1:
            update_top_plot(showtime_tab_instance.app_instance.scan_monitor_tab, trace_df, start_freq_mhz, end_freq_mhz, f"{plot_title} - Trace 1")
        elif trace_number == 2:
            update_middle_plot(showtime_tab_instance.app_instance.scan_monitor_tab, trace_df, start_freq_mhz, end_freq_mhz, f"{plot_title} - Trace 2")
        elif trace_number == 3:
            update_bottom_plot(showtime_tab_instance.app_instance.scan_monitor_tab, trace_df, start_freq_mhz, end_freq_mhz, f"{plot_title} - Trace 3")
        
        console_print_func(f"✅ Trace {trace_number} retrieved and plot updated for '{device_name}'.")