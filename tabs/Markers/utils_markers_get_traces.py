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
# Version 20250811.121800.1 (FIXED: The trace update cycle now correctly adheres to a 10-tick loop, calling Max Hold every 5th tick and Min Hold every 10th, if enabled.)

import inspect
import os
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log
from tabs.Instrument.utils_instrument_read_and_write import query_safe
from display.utils_display_monitor import update_top_plot, update_medium_plot, update_bottom_plot


current_version = "20250811.121800.1"
current_version_hash = (20250811 * 121800 * 1)

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

    trace_data_str = query_safe(app_instance.inst, ":TRAC1:DATA?", console_print_func)
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

    trace_data_str = query_safe(app_instance.inst, ":TRAC2:DATA?", console_print_func)
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

    trace_data_str = query_safe(app_instance.inst, ":TRAC3:DATA?", console_print_func)
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
    # Orchestrates the retrieval of trace data from the instrument based on a specific,
    # user-defined update ratio for Live, Max Hold, and Min Hold traces.
    # The ratio is 1 Live update every tick, 1 Max Hold update every 5 ticks,
    # and 1 Min Hold update every 10 ticks. The loop is a 10-tick cycle.
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
    debug_log(f"Getting marker traces with a specific update ratio. The timing must be perfect! ⏱️",
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
    
    # --- Live Trace (Trace 1) ---
    if app_instance.trace_live_var.get():
        plot_title = f"Live: {device_name}" if device_name else "Live Scan"
        trace_1_data = get_trace_1_data(app_instance, console_print_func, start_freq_hz, end_freq_hz)
        publish_top_trace(app_instance, console_print_func, trace_data=trace_1_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=plot_title)
    else:
        plot_title = "Live scan not active"
        publish_top_trace(app_instance, console_print_func, trace_data=[], start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=plot_title)

    # --- Max Hold Trace (Trace 2) ---
    # Update once every 5 live scans, if enabled.
    if app_instance.trace_max_hold_var.get() and _trace_update_cycle_counter % 5 == 0:
        plot_title = f"Max Hold: {device_name}" if device_name else "Max Hold Scan"
        trace_2_data = get_trace_2_data(app_instance, console_print_func, start_freq_hz, end_freq_hz)
        publish_medium_trace(app_instance, console_print_func, trace_data=trace_2_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=plot_title)
    elif not app_instance.trace_max_hold_var.get():
        plot_title = "Max Hold not active"
        publish_medium_trace(app_instance, console_print_func, trace_data=[], start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=plot_title)

    # --- Min Hold Trace (Trace 3) ---
    # Update once every 10 live scans, if enabled.
    if app_instance.trace_min_hold_var.get() and _trace_update_cycle_counter % 10 == 0:
        plot_title = f"Min Hold: {device_name}" if device_name else "Min Hold Scan"
        trace_3_data = get_trace_3_data(app_instance, console_print_func, start_freq_hz, end_freq_hz)
        publish_bottom_trace(app_instance, console_print_func, trace_data=trace_3_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=plot_title)
    elif not app_instance.trace_min_hold_var.get():
        plot_title = "Min Hold not active"
        publish_bottom_trace(app_instance, console_print_func, trace_data=[], start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=plot_title)

    # Increment the counter and reset at 10 to maintain the cycle
    _trace_update_cycle_counter = (_trace_update_cycle_counter + 1) % 10
    
    console_print_func(f"📊 Display range set from {start_freq_hz} Hz to {end_freq_hz} Hz. Live update cycle count: {_trace_update_cycle_counter}.")
