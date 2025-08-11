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
# Version 20250811.130322.2 (FIXED: The get_marker_traces function now accepts center and span frequencies directly, eliminating redundant queries to the instrument. This simplifies the function and improves efficiency.)

import inspect
import os
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log
from tabs.Instrument.utils_instrument_read_and_write import query_safe
from display.utils_display_monitor import update_top_plot, update_medium_plot, update_bottom_plot


current_version = "20250811.130322.2"
current_version_hash = 20250811 * 130322 * 2


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


def publish_traces(app_instance, console_print_func, trace_1_data=None, trace_2_data=None, trace_3_data=None, start_freq_mhz=0, end_freq_mhz=0, plot_titles=[]):
    # Function Description:
    # Publishes the processed trace data to the display monitor plots.
    # This function acts as the single point of contact with the display module.
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

    # Use the provided plot titles, or default to a descriptive title
    title_1 = plot_titles[0] if len(plot_titles) > 0 else "Live"
    title_2 = plot_titles[1] if len(plot_titles) > 1 else "Max Hold"
    title_3 = plot_titles[2] if len(plot_titles) > 2 else "Min Hold"

    if trace_1_data:
        update_top_plot(scan_monitor_tab_instance=scan_monitor_tab_instance, data=trace_1_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=title_1)
        console_print_func(f"✅ Successfully updated top plot with Trace 1 data.")

    if trace_2_data:
        update_medium_plot(scan_monitor_tab_instance=scan_monitor_tab_instance, data=trace_2_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=title_2)
        console_print_func(f"✅ Successfully updated medium plot with Trace 2 data.")

    if trace_3_data:
        update_bottom_plot(scan_monitor_tab_instance=scan_monitor_tab_instance, data=trace_3_data, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz, plot_title=title_3)
        console_print_func(f"✅ Successfully updated bottom plot with Trace 3 data.")


def get_marker_traces(app_instance, console_print_func, center_freq_hz, span_hz, device_name=None):
    # Function Description:
    # Orchestrates the retrieval of trace data from the instrument. This function
    # now accepts the center frequency and span directly, removing the need to
    # query the instrument for these values. It then gets data for all three
    # traces and publishes them to the display monitor.
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
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Getting marker traces with pre-defined center and span frequencies. This is a much better way to do it! 🚀",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)

    # Let the calling function handle the instrument connection check. This function will proceed
    # with the assumption that a valid instrument instance is present.
    if not app_instance.inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot get marker traces.")
        debug_log(f"Instrument is not connected. Aborting trace retrieval.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        return

    # A wild scientist appears! He says: "By golly! We've been given the sacred numbers!
    # No need to ask the machine itself for its secrets. We can use these values directly to calculate
    # the start and end frequencies. It's a much more elegant solution, don't you think?"

    start_freq_hz = center_freq_hz - (span_hz / 2)
    end_freq_hz = center_freq_hz + (span_hz / 2)

    # Define plot titles here based on the device_name
    if device_name:
        plot_titles = [f"Live: {device_name}", f"Max Hold: {device_name}", f"Min Hold: {device_name}"]
    else:
        plot_titles = ["Live", "Max Hold", "Min Hold"]


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

