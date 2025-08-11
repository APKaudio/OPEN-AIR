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
# Version 20250810.220500.56 (FIXED: The publish_traces function now correctly uses the app_instance.scan_monitor_tab attribute, which is now properly exposed by the main app instance.)

import inspect
import os
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log
from tabs.Instrument.utils_instrument_read_and_write import query_safe
from display.utils_display_monitor import update_top_plot, update_medium_plot, update_bottom_plot


current_version = "20250810.220500.56"
current_version_hash = 20250810 * 220500 * 56


def _process_trace_data(trace_data_str, start_freq_hz, end_freq_hz):
    # Function Description:
    # Processes a raw trace data string from the instrument into a list of
    # (frequency, amplitude) tuples.
    #
    # Inputs to this function:
    #   trace_data_str (str): The raw comma-separated string of amplitude data.
    #   start_freq_hz (float): The starting frequency for the scan.
    #   end_freq_hz (float): The ending frequency for the scan.
    #
    # Outputs of this function:
    #   list: A list of tuples, where each tuple is (frequency_mhz, amplitude_dbm).
    #         Returns None if processing fails.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Processing raw trace data into frequency/amplitude pairs. This is a crucial step.",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)
              
    try:
        amplitudes_dbm = [float(val) for val in trace_data_str.split(',') if val.strip()]
        num_points = len(amplitudes_dbm)
        if num_points == 0:
            console_log("⚠️ Warning: No data points in the trace. Useless!")
            return None
        
        # Calculate the frequency points using numpy linspace
        frequencies_hz = np.linspace(start_freq_hz, end_freq_hz, num_points)
        
        # FIXED: Explicitly cast the numpy float to a standard Python float to remove the np.float64 prefix from debug logs
        frequencies_mhz_rounded = [float(round(f / 1000000, 3)) for f in frequencies_hz]
        amplitudes_dbm_rounded = [round(a, 3) for a in amplitudes_dbm]
        
        # Combine the frequencies and rounded amplitudes into a list of tuples
        processed_data = list(zip(frequencies_mhz_rounded, amplitudes_dbm_rounded))
        
        # NEW: Log the processed data for debugging
        debug_log(f"Successfully processed trace data. First 5 points: {processed_data[:5]}...",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
        return processed_data
    except ValueError as e:
        console_log(f"❌ Error parsing trace data: {e}. The data from the instrument is useless!")
        debug_log(f"ValueError: {e}. Failed to parse data string: {trace_data_str[:50]}...",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function, special=True)
        return None

def get_trace_1_data(app_instance, console_print_func, start_freq_hz, end_freq_hz):
    # Function Description:
    # Queries the instrument for Trace 1 data, processes it, and returns the result.
    #
    # Inputs to this function:
    #   app_instance (object): A reference to the main application instance.
    #   console_print_func (function): A function for printing to the console.
    #   start_freq_hz (float): The start frequency for the x-axis.
    #   end_freq_hz (float): The end frequency for the x-axis.
    #
    # Outputs of this function:
    #   list: A list of tuples, where each tuple is (frequency_mhz, amplitude_dbm).
    #         Returns None if processing fails.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to get Trace 1 data.",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)
              
    if not app_instance.inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot get Trace 1 data.")
        return None

    trace_data_str = query_safe(app_instance.inst, ":TRAC1:DATA?", app_instance, console_print_func)
    if trace_data_str:
        processed_data = _process_trace_data(trace_data_str, start_freq_hz, end_freq_hz)
        if processed_data:
            console_print_func(f"✅ Successfully retrieved Trace 1 data.")
            return processed_data
    
    console_print_func("❌ Failed to get Trace 1 data from instrument.")
    return None


def get_trace_2_data(app_instance, console_print_func, start_freq_hz, end_freq_hz):
    # Function Description:
    # Queries the instrument for Trace 2 data, processes it, and returns the result.
    #
    # Inputs to this function:
    #   app_instance (object): A reference to the main application instance.
    #   console_print_func (function): A function for printing to the console.
    #   start_freq_hz (float): The start frequency for the x-axis.
    #   end_freq_hz (float): The end frequency for the x-axis.
    #
    # Outputs of this function:
    #   list: A list of tuples, where each tuple is (frequency_mhz, amplitude_dbm).
    #         Returns None if processing fails.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to get Trace 2 data.",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)
    
    if not app_instance.inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot get Trace 2 data.")
        return None
        
    trace_data_str = query_safe(app_instance.inst, ":TRAC2:DATA?", app_instance, console_print_func)
    if trace_data_str:
        processed_data = _process_trace_data(trace_data_str, start_freq_hz, end_freq_hz)
        if processed_data:
            console_print_func(f"✅ Successfully retrieved Trace 2 data.")
            return processed_data
    
    console_print_func("❌ Failed to get Trace 2 data from instrument.")
    return None


def get_trace_3_data(app_instance, console_print_func, start_freq_hz, end_freq_hz):
    # Function Description:
    # Queries the instrument for Trace 3 data, processes it, and returns the result.
    #
    # Inputs to this function:
    #   app_instance (object): A reference to the main application instance.
    #   console_print_func (function): A function for printing to the console.
    #   start_freq_hz (float): The start frequency for the x-axis.
    #   end_freq_hz (float): The end frequency for the x-axis.
    #
    # Outputs of this function:
    #   list: A list of tuples, where each tuple is (frequency_mhz, amplitude_dbm).
    #         Returns None if processing fails.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to get Trace 3 data.",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)

    if not app_instance.inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot get Trace 3 data.")
        return None

    trace_data_str = query_safe(app_instance.inst, ":TRAC3:DATA?", app_instance, console_print_func)
    if trace_data_str:
        processed_data = _process_trace_data(trace_data_str, start_freq_hz, end_freq_hz)
        if processed_data:
            console_print_func(f"✅ Successfully retrieved Trace 3 data.")
            return processed_data
    
    console_print_func("❌ Failed to get Trace 3 data from instrument.")
    return None


def publish_traces(app_instance, console_print_func, trace_1_data=None, trace_2_data=None, trace_3_data=None, start_freq_mhz=0, end_freq_mhz=0, plot_titles=[]):
    # Function Description:
    # Publishes the processed trace data to the display monitor plots.
    # This function acts as the single point of contact with the display module.
    #
    # Inputs to this function:
    #   app_instance (object): A reference to the main application instance.
    #   console_print_func (function): A function for printing to the console.
    #   trace_1_data (list): A list of (frequency, amplitude) tuples for the top plot.
    #   trace_2_data (list): A list of (frequency, amplitude) tuples for the medium plot.
    #   trace_3_data (list): A list of (frequency, amplitude) tuples for the bottom plot.
    #   start_freq_mhz (float): The start frequency of the plot in MHz.
    #   end_freq_mhz (float): The end frequency of the plot in MHz.
    #   plot_titles (list): A list of titles for the three plots.
    #
    # Outputs of this function:
    #   None. Triggers updates to the GUI plots.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Publishing processed trace data to the display plots. The audience is waiting! 🎭",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)

    # Get the instance of the ScanMonitorTab from the app_instance
    scan_monitor_tab_instance = app_instance.scan_monitor_tab
    if not scan_monitor_tab_instance:
        console_print_func("❌ The Scan Monitor tab instance could not be found. Display updates aborted.")
        debug_log(f"The Scan Monitor tab instance is a big fat ZERO. Aborting.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        return
        
    if trace_1_data:
        update_top_plot(scan_monitor_tab_instance=scan_monitor_tab_instance, data=trace_1_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=plot_titles[0])
        console_print_func(f"✅ Successfully updated top plot with Trace 1 data.")
    
    if trace_2_data:
        update_medium_plot(scan_monitor_tab_instance=scan_monitor_tab_instance, data=trace_2_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=plot_titles[1])
        console_print_func(f"✅ Successfully updated medium plot with Trace 2 data.")

    if trace_3_data:
        update_bottom_plot(scan_monitor_tab_instance=scan_monitor_tab_instance, data=trace_3_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=plot_titles[2])
        console_print_func(f"✅ Successfully updated bottom plot with Trace 3 data.")


def get_marker_traces(app_instance, console_print_func):
    # Function Description:
    # Orchestrates the retrieval of trace data from the instrument. It first queries
    # for the current center frequency and span to define the plot's frequency range,
    # then calls functions to get data for all three traces and publishes them.
    #
    # Inputs to this function:
    #   app_instance (object): A reference to the main application instance.
    #   console_print_func (function): A function for printing to the console.
    #
    # Outputs of this function:
    #   None. Calls other functions to update the display monitors.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Getting marker traces from the instrument. It's go time!",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)

    if not app_instance.inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot get marker traces.")
        debug_log(f"Instrument is not connected. Aborting trace retrieval.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        return
    
    try:
        center_freq_str = query_safe(app_instance.inst, ":SENSe:FREQuency:CENTer?", app_instance, console_print_func)
        span_str = query_safe(app_instance.inst, ":SENSe:FREQuency:SPAN?", app_instance, console_print_func)
        
        if not center_freq_str or not span_str:
            console_print_func("❌ Failed to query center frequency or span from instrument.")
            debug_log(f"Failed to get center frequency or span. Aborting.",
                      file=f"{os.path.basename(__file__)} - {current_version}",
                      version=current_version,
                      function=current_function)
            return

        center_freq_hz = float(center_freq_str)
        span_hz = float(span_str)

        start_freq_hz = center_freq_hz - (span_hz / 2)
        end_freq_hz = center_freq_hz + (span_hz / 2)
        
        # NEW: Define plot titles here
        plot_titles = ["Trace 1 (Live)", "Trace 2 (Max Hold)", "Trace 3 (Min Hold)"]

        console_print_func(f"✅ Queried instrument. Center Freq: {center_freq_hz} Hz, Span: {span_hz} Hz.")
        console_print_func(f"📊 Display range set from {start_freq_hz} Hz to {end_freq_hz} Hz.")

        # Get data from each trace
        trace_1_data = get_trace_1_data(app_instance, console_print_func, start_freq_hz, end_freq_hz)
        trace_2_data = get_trace_2_data(app_instance, console_print_func, start_freq_hz, end_freq_hz)
        trace_3_data = get_trace_3_data(app_instance, console_print_func, start_freq_hz, end_freq_hz)

        # Convert frequency range to MHz for plotting
        start_freq_mhz = start_freq_hz / 1000000
        end_freq_mhz = end_freq_hz / 1000000

        # Publish the traces to the display module
        publish_traces(app_instance=app_instance, console_print_func=console_print_func, trace_1_data=trace_1_data, trace_2_data=trace_2_data, trace_3_data=trace_3_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_titles=plot_titles)


    except Exception as e:
        console_print_func(f"❌ An error occurred while getting marker traces: {e}")
        debug_log(f"An unexpected error occurred: {e}",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
