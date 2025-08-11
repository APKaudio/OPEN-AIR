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
# Version 20250811.130322.4 (REFACTORED: The trace update loop is now a cycle of 5:1:5:1 for Live, Max Hold, and Min Hold, respectively. The single publish_traces function has been broken into three separate functions for clarity.)

import inspect
import os
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log
from tabs.Instrument.utils_instrument_read_and_write import query_safe
from display.utils_display_monitor import update_top_plot, update_medium_plot, update_bottom_plot


current_version = "20250811.130322.4"
current_version_hash = (20250811 * 130322 * 4)

# A global counter to manage the trace update cycle state.
_trace_update_cycle_counter = 0

def _process_trace_data(trace_data_str, start_freq_hz, end_freq_hz):
    # Function Description:
    # Processes a raw trace data string from the instrument into a list of
    # (frequency, amplitude) tuples.
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

        frequencies_mhz_rounded = [float(round(f / 1000000, 3)) for f in frequencies_hz]
        amplitudes_dbm_rounded = [round(a, 3) for a in amplitudes_dbm]

        # Combine the frequencies and rounded amplitudes into a list of tuples
        processed_data = list(zip(frequencies_mhz_rounded, amplitudes_dbm_rounded))

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


def publish_top_trace(app_instance, console_print_func, trace_data, start_freq_mhz, end_freq_mhz, plot_title):
    # Function Description:
    # Publishes trace data to the top display monitor plot (Live).
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Publishing top trace data. The audience is waiting! 🎭",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)
    scan_monitor_tab_instance = app_instance.scan_monitor_tab
    if not scan_monitor_tab_instance:
        console_print_func("❌ The Scan Monitor tab instance could not be found. Display updates aborted.")
        return
    update_top_plot(scan_monitor_tab_instance=scan_monitor_tab_instance, data=trace_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=plot_title)
    console_print_func(f"✅ Successfully updated top plot with Trace data.")

def publish_medium_trace(app_instance, console_print_func, trace_data, start_freq_mhz, end_freq_mhz, plot_title):
    # Function Description:
    # Publishes trace data to the middle display monitor plot (Max Hold).
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Publishing medium trace data. The audience is waiting! 🎭",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)
    scan_monitor_tab_instance = app_instance.scan_monitor_tab
    if not scan_monitor_tab_instance:
        console_print_func("❌ The Scan Monitor tab instance could not be found. Display updates aborted.")
        return
    update_medium_plot(scan_monitor_tab_instance=scan_monitor_tab_instance, data=trace_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=plot_title)
    console_print_func(f"✅ Successfully updated medium plot with Trace data.")

def publish_bottom_trace(app_instance, console_print_func, trace_data, start_freq_mhz, end_freq_mhz, plot_title):
    # Function Description:
    # Publishes trace data to the bottom display monitor plot (Min Hold).
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Publishing bottom trace data. The audience is waiting! 🎭",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)
    scan_monitor_tab_instance = app_instance.scan_monitor_tab
    if not scan_monitor_tab_instance:
        console_print_func("❌ The Scan Monitor tab instance could not be found. Display updates aborted.")
        return
    update_bottom_plot(scan_monitor_tab_instance=scan_monitor_tab_instance, data=trace_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=plot_title)
    console_print_func(f"✅ Successfully updated bottom plot with Trace data.")


def get_marker_traces(app_instance, console_print_func, center_freq_hz, span_hz, device_name=None):
    # Function Description:
    # Orchestrates the retrieval of trace data from the instrument in a specific cycle.
    # The cycle is 5 updates for the live trace, then 1 for the max hold, then 5 for the live,
    # then 1 for the min hold. This prioritizes fresh live data while still updating the hold traces.
    #
    # Inputs:
    #   app_instance (object): A reference to the main application instance.
    #   console_print_func (function): A function for printing to the console.
    #   center_freq_hz (float): The center frequency of the scan in Hz.
    #   span_hz (float): The span of the scan in Hz.
    #   device_name (str): The name of the selected device to use in the plot titles.
    #
    # Outputs:
    #   None. Calls other functions to update the display monitors.
    global _trace_update_cycle_counter
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Getting marker traces with pre-defined center and span frequencies. This is a much better way to do it! 🚀",
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

    start_freq_hz = center_freq_hz - (span_hz / 2)
    end_freq_hz = center_freq_hz + (span_hz / 2)

    start_freq_mhz = start_freq_hz / 1000000
    end_freq_mhz = end_freq_hz / 1000000

    if device_name:
        plot_title = device_name
    else:
        plot_title = "Live"
        
    debug_log(f"The current cycle counter is: {_trace_update_cycle_counter}. Let's see what happens!",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)

    if _trace_update_cycle_counter < 5:
        # Update Trace 1 five times
        trace_1_data = get_trace_1_data(app_instance, console_print_func, start_freq_hz, end_freq_hz)
        if trace_1_data:
            publish_top_trace(app_instance, console_print_func, trace_data=trace_1_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=f"Live: {plot_title}")
        _trace_update_cycle_counter += 1
    elif _trace_update_cycle_counter == 5:
        # Update Trace 2 once
        trace_2_data = get_trace_2_data(app_instance, console_print_func, start_freq_hz, end_freq_hz)
        if trace_2_data:
            publish_medium_trace(app_instance, console_print_func, trace_data=trace_2_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=f"Max Hold: {plot_title}")
        _trace_update_cycle_counter += 1
    elif _trace_update_cycle_counter < 11:
        # Update Trace 1 five more times
        trace_1_data = get_trace_1_data(app_instance, console_print_func, start_freq_hz, end_freq_hz)
        if trace_1_data:
            publish_top_trace(app_instance, console_print_func, trace_data=trace_1_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=f"Live: {plot_title}")
        _trace_update_cycle_counter += 1
    elif _trace_update_cycle_counter == 11:
        # Update Trace 3 once
        trace_3_data = get_trace_3_data(app_instance, console_print_func, start_freq_hz, end_freq_hz)
        if trace_3_data:
            publish_bottom_trace(app_instance, console_print_func, trace_data=trace_3_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=f"Min Hold: {plot_title}")
        _trace_update_cycle_counter = 0 # Reset the cycle

    console_print_func(f"📊 Display range set from {start_freq_hz} Hz to {end_freq_hz} Hz.")
