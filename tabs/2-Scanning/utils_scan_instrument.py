# utils/scan_instrument.py
#
# This module contains the core logic for controlling the spectrum analyzer
# to perform frequency sweeps across specified bands. It handles the low-level
# communication with the instrument via PyVISA, processes raw trace data,
# and saves it to CSV files. This is a critical component for data acquisition.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
#
#
# Version 1.4 (Removed 'end' keyword argument from app_console_update_func calls)

import pyvisa
import time
import numpy as np
import re
import tkinter as tk # Keeping tk for potential future GUI interactions, though messagebox is removed
import datetime
import os
# import pandas as pd # Removed: Data processing moved to scan_stitch.py
import inspect

# Import instrument control functions
from utils.utils_instrument_control import query_safe, write_safe, debug_print, initialize_instrument
from utils.utils_instrument_control import set_debug_mode, set_log_visa_commands_mode
# Import CSV utility (still used for incremental saving of raw data)
from utils.utils_csv_writer import write_scan_data_to_csv

# Import frequency band definitions
from ref.frequency_bands import MHZ_TO_HZ, VBW_RBW_RATIO # SCAN_BAND_RANGES is not directly used here anymore


def perform_segment_sweep(inst, segment_start_freq_hz, segment_stop_freq_hz, maxhold_enabled, max_hold_time, app_instance_ref, pause_event, stop_event, segment_counter, total_segments_in_band, band_name, app_console_update_func):
    # This function description tells me what this function does
    # Performs a single frequency sweep segment on the spectrum analyzer instrument.
    # It configures the instrument's frequency range, trace modes (including Max Hold),
    # queries the trace data, and parses it into frequency-amplitude pairs.
    # It also handles pause and stop events, and provides real-time progress updates to the console.
    # This version assumes the instrument is in a continuous sweep mode and data can be
    # queried immediately after setting the frequency range.
    #
    # Inputs to this function
    #   inst (pyvisa.resources.Resource): The PyVISA instrument resource object, representing the connected spectrum analyzer.
    #   segment_start_freq_hz (float): The starting frequency for this specific sweep segment, in Hertz.
    #   segment_stop_freq_hz (float): The stopping frequency for this specific sweep segment, in Hertz.
    #   maxhold_enabled (bool): A boolean flag indicating whether Max Hold mode should be enabled for this sweep.
    #   max_hold_time (float): The duration in seconds to wait for the Max Hold trace to stabilize.
    #   app_instance_ref (object): A reference to the main application instance, used to access shared attributes like `instrument_model`.
    #   pause_event (threading.Event): A threading event object used to signal and manage pausing of the scan.
    #   stop_event (threading.Event): A threading event object used to signal and manage stopping of the scan.
    #   segment_counter (int): The current segment number within the band, used for display and debugging.
    #   total_segments_in_band (int): The total number of segments planned for the current frequency band, used for progress display.
    #   band_name (str): The name of the current frequency band being scanned, used for console messages.
    #   app_console_update_func (function): A callback function used to print messages to the application's GUI console.
    #
    # Process of this function
    #   1. Logs entry into the function with debug information.
    #   2. Enters a loop to check for `pause_event` and `stop_event` before and during the sweep,
    #      pausing execution or returning an empty list if a stop is requested.
    #   3. Sends SCPI commands to the instrument to set the frequency start and stop for the segment.
    #      Returns an empty list if this command fails.
    #   4. Sends SCPI commands to blank all traces, then sets Trace 2 to Max Hold mode if `maxhold_enabled` is True.
    #   5. If Max Hold is enabled and `max_hold_time` is greater than 0, enters a loop to wait for the
    #      specified duration, providing a countdown to the console. It continuously checks for pause/stop events.
    #   6. Calculates and displays a progress bar for the current segment to the console.
    #   7. Queries the instrument for trace data, using different SCPI commands based on `app_instance_ref.instrument_model`.
    #   8. Checks if the received `trace_data_str` is valid (not None, not a timeout message, not empty).
    #       If invalid, prints an error and returns an empty list.
    #   9. Parses the `trace_data_str` to extract the numerical amplitude values. It handles cases where
    #       the data might or might not have a SCPI header.
    #   10. Queries the instrument for the actual center frequency and span to accurately calculate
    #       the frequency points corresponding to the collected amplitude data.
    #   11. Creates a list of (frequency_hz, amplitude_dbm) tuples.
    #   12. Prints a message indicating the number of data points collected.
    #   13. Includes `try-except` blocks to catch `pyvisa.errors.VisaIOError` for instrument communication issues
    #       and general `Exception` for other unexpected errors, logging them and returning an empty list.
    #   14. Logs exit from the function with debug information.
    #
    # Outputs of this function
    #   list: A list of `(frequency_hz, amplitude_dbm)` tuples representing the collected trace data for the segment.
    #         Returns an empty list `[]` if any error occurs, the scan is stopped, or no valid data is collected.
    #
    # Date / time of changes made to this file: 2025-07-30 18:15:00
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering {current_function} function. Segment {segment_counter}/{total_segments_in_band}", file=current_file, function=current_function, console_print_func=app_console_update_func)

    # Check for pause/stop before starting segment
    while pause_event.is_set():
        app_console_update_func("Scan Paused. Click Resume to continue.")
        time.sleep(0.1)
        if stop_event.is_set():
            app_console_update_func(f"Scan for {band_name} interrupted during pause in segment {segment_counter}.")
            debug_print("Stop event set during pause.", file=current_file, function=current_function, console_print_func=app_console_update_func)
            return []
    if stop_event.is_set():
        app_console_update_func(f"Scan for {band_name} interrupted during segment {segment_counter}.")
        debug_print("Stop event set before segment scan.", file=current_file, function=current_function, console_print_func=app_console_update_func)
        return []

    # Set instrument frequency range for the current segment
    if not write_safe(inst, f":SENS:FREQ:STAR {segment_start_freq_hz};:SENS:FREQ:STOP {segment_stop_freq_hz}"):
        app_console_update_func(f"❌ Error: Failed to set frequency range for segment {segment_counter}.")
        debug_print(f"Failed to set frequency range: {segment_start_freq_hz}-{segment_stop_freq_hz}", file=current_file, function=current_function, console_print_func=app_console_update_func)
        return []

    # Set trace modes
    if not write_safe(inst, ":TRAC1:MODE BLANk;:TRAC2:MODE BLANk;:TRAC3:MODE BLANk"):
        app_console_update_func(f"❌ Error: Failed to blank traces for segment {segment_counter}.")
        debug_print("Failed to blank traces.", file=current_file, function=current_function, console_print_func=app_console_update_func)
        # Continue, as this might not be critical

    if maxhold_enabled:
        if not write_safe(inst, ":TRAC2:MODE MAXHold;"):
            app_console_update_func(f"❌ Error: Failed to set Max Hold mode for segment {segment_counter}.")
            debug_print("Failed to set Max Hold mode.", file=current_file, function=current_function, console_print_func=app_console_update_func)
            # Continue, as this might not be critical

    # Add settling time for max hold values to show up, if max hold is enabled and time > 0
    if maxhold_enabled and max_hold_time > 0:
        for _ in range(int(max_hold_time * 10)): # Check every 0.1 seconds
            while pause_event.is_set():
                app_console_update_func("Scan Paused. Click Resume to continue.")
                time.sleep(0.1)
                if stop_event.is_set():
                    app_console_update_func(f"Scan for {band_name} interrupted during pause in max hold for segment {segment_counter}.")
                    debug_print("Stop event set during max hold pause.", file=current_file, function=current_function, console_print_func=app_console_update_func)
                    return []
            if stop_event.is_set():
                app_console_update_func(f"Scan for {band_name} interrupted during max hold for segment {segment_counter}.")
                debug_print("Stop event set during max hold.", file=current_file, function=current_function, console_print_func=app_console_update_func)
                return []

            if _ % 10 == 0: # Every 10 iterations (1 second)
                sec_remaining = int(max_hold_time - (_ / 10))
                # Removed 'end='\r''
               # app_console_update_func(f"⏳ {sec_remaining}")
            time.sleep(0.1)
        # Removed 'end='\r'' and the empty string print
      #  app_console_update_func("✅ Max Hold Settled.")

    if stop_event.is_set():
        app_console_update_func(f"Scan for {band_name} interrupted after max hold for segment {segment_counter}.")
        debug_print("Stop event set after max hold.", file=current_file, function=current_function, console_print_func=app_console_update_func)
        return []

    # Calculate progress for the emoji bar
    progress_percentage = (segment_counter / total_segments_in_band)
    bar_length = 20
    filled_length = int(round(bar_length * progress_percentage))
    progressbar = '█' * filled_length + '-' * (bar_length - filled_length)

    # Removed 'end='\r''
    progress_message = f"{progressbar}🔍 Span:📊{(segment_stop_freq_hz - segment_start_freq_hz)/MHZ_TO_HZ:.3f} MHz--📈{segment_start_freq_hz/MHZ_TO_HZ:.3f} MHz to 📉{segment_stop_freq_hz/MHZ_TO_HZ:.3f} MHz   ✅{segment_counter} of {total_segments_in_band} "
    app_console_update_func(progress_message)

    segment_raw_data = []
    try:
        # Conditional trace data query based on instrument model
        # Assuming app_instance_ref has instrument_model attribute
        if app_instance_ref.instrument_model == "N9340B":
            trace_data_str = query_safe(inst, ":TRAC2:DATA?")
        elif app_instance_ref.instrument_model == "N9342CN":
            trace_data_str = query_safe(inst, ":TRACe:DATA? TRACe2")
        else: # Fallback for unknown models
            trace_data_str = query_safe(inst, ":TRACe:DATA? TRACe2")

        if trace_data_str is None or "[Not Supported or Timeout]" in trace_data_str or not trace_data_str.strip():
            app_console_update_func("🚫 No valid trace data string received for this segment.")
            debug_print("No valid trace data string.", file=current_file, function=current_function, console_print_func=app_console_update_func)
            return []

        data_part = None
        match = re.match(r'#\d+\d+(.*)', trace_data_str)
        if match:
            data_part = match.group(1)
        else:
            data_part = trace_data_str
            debug_print("Trace data header not found. Attempting to parse raw string directly.", file=current_file, function=current_function, console_print_func=app_console_update_func)

        if data_part:
            try:
                amplitudes_dbm = [float(val) for val in data_part.split(',') if val.strip()]
                debug_print(f"Parsed {len(amplitudes_dbm)} amplitude points.", file=current_file, function=current_function, console_print_func=app_console_update_func)

                # Query actual start/stop frequencies from instrument
                actual_center_freq_hz = float(query_safe(inst, ":SENSe:FREQuency:CENTer?"))
                actual_span_hz = float(query_safe(inst, ":SENSe:FREQuency:SPAN?"))
                
                # Derive num_points from the length of the amplitudes_dbm list
                num_points = len(amplitudes_dbm)

                if num_points == 0:
                    app_console_update_func(f"⚠️ Warning: No amplitude data received for segment {segment_counter}. Skipping data processing.")
                    debug_print("No amplitude data received.", file=current_file, function=current_function, console_print_func=app_console_update_func)
                    return []

                if num_points > 1:
                    segment_trace_start_freq = actual_center_freq_hz - (actual_span_hz / 2)
                    segment_trace_stop_freq = actual_center_freq_hz + (actual_span_hz / 2)
                    frequencies_hz = np.linspace(segment_trace_start_freq, segment_trace_stop_freq, num_points)
                else: # Handle case with a single point
                    frequencies_hz = np.array([actual_center_freq_hz])

                # Ensure amplitudes and frequencies match in length
                if len(amplitudes_dbm) == len(frequencies_hz):
                    for freq, amp in zip(frequencies_hz, amplitudes_dbm):
                        segment_raw_data.append((freq, amp))
                    # Print the "Collected" message. It will appear on the same line as the progress bar
                    # because the progress bar ended with '\r'. We then add a newline to move to the next line.
                 #   app_console_update_func(f"  Collected {len(amplitudes_dbm)} data points for segment {segment_counter}.")
                    debug_print(f"Collected {len(amplitudes_dbm)} data points.", file=current_file, function=current_function, console_print_func=app_console_update_func)
                else:
                    app_console_update_func(f"❌ Error: Mismatch in data points and frequencies for segment {segment_counter}. Expected {len(frequencies_hz)}, got {len(amplitudes_dbm)} amplitudes. Raw data: {data_part[:100]}...")
                    debug_print(f"Data length mismatch. Expected {len(frequencies_hz)}, got {len(amplitudes_dbm)}.", file=current_file, function=current_function, console_print_func=app_console_update_func)
                    return [] # Return empty if data integrity is compromised
            except ValueError as ve:
                app_console_update_func(f"❌ Data Parsing Error in segment {segment_counter}: {ve}. Could not convert data to float. Raw data: {data_part[:100]}...")
                debug_print(f"ValueError parsing trace data: {ve}", file=current_file, function=current_function, console_print_func=app_console_update_func)
                return []
        else:
            app_console_update_func(f"❌ Error: No parsable data part found in trace data for segment {segment_counter}. Raw data: {trace_data_str[:100]}...")
            debug_print(f"No parsable data part found: {trace_data_str[:50]}...", file=current_file, function=current_function, console_print_func=app_console_update_func)
            return []

    except pyvisa.errors.VisaIOError as e:
        app_console_update_func(f"❌ VISA Error during segment {segment_counter} sweep: {e}")
        debug_print(f"VISA Error in perform_segment_sweep: {e}", file=current_file, function=current_function, console_print_func=app_console_update_func)
        return []
    except Exception as e:
        app_console_update_func(f"🚨 An unexpected error occurred during segment {segment_counter} sweep: {e}\n")
        debug_print(f"Unexpected error during segment sweep: {e}", file=current_file, function=current_function, console_print_func=app_console_update_func)
        return []

    debug_print(f"Exiting {current_function} function. Collected {len(segment_raw_data)} points.", file=current_file, function=current_function, console_print_func=app_console_update_func)
    return segment_raw_data


def scan_bands(app_instance_ref, inst, selected_bands, rbw_hz, ref_level_dbm, freq_shift_hz, maxhold_enabled, high_sensitivity, preamp_on, rbw_step_size_hz, max_hold_time_seconds, scan_name, output_folder, stop_event, pause_event, log_visa_commands_enabled, general_debug_enabled, app_console_update_func):
    # This function description tells me what this function does
    # Orchestrates a full frequency scan across multiple specified bands.
    # It initializes the instrument with global scan settings (RBW, Ref Level, etc.),
    # then iterates through each selected band, dividing it into segments if necessary.
    # For each segment, it calls `perform_segment_sweep` to acquire data.
    # It manages stop/pause events and accumulates all raw scan data.
    #
    # Inputs to this function
    #   app_instance_ref (object): Reference to the main application instance, providing access to instrument model and other shared data.
    #   inst (pyvisa.resources.Resource): The PyVISA instrument resource object.
    #   selected_bands (list): A list of dictionaries, where each dictionary defines a frequency band with "Band Name", "Start MHz", and "Stop MHz".
    #   rbw_hz (float): The Resolution Bandwidth in Hertz, to be set on the instrument.
    #   ref_level_dbm (float): The Reference Level in dBm, to be set on the instrument.
    #   freq_shift_hz (float): A frequency offset in Hertz to be applied to all scan ranges.
    #   maxhold_enabled (bool): Flag to enable/disable Max Hold mode during sweeps.
    #   high_sensitivity (bool): Flag to enable/disable high sensitivity mode (e.g., attenuation off, preamp on).
    #   preamp_on (bool): Flag to explicitly turn the preamplifier on/off.
    #   rbw_step_size_hz (float): The step size for RBW, used in calculating segment spans.
    #   max_hold_time_seconds (float): The duration for Max Hold settling time.
    #   scan_name (str): The base name for output files generated during this scan session.
    #   output_folder (str): The directory path where scan data CSVs will be saved.
    #   stop_event (threading.Event): A threading event to signal an immediate stop of the scan.
    #   pause_event (threading.Event): A threading event to signal pausing and resuming of the scan.
    #   log_visa_commands_enabled (bool): Flag to enable verbose logging of VISA commands.
    #   general_debug_enabled (bool): Flag to enable general debug messages.
    #   app_console_update_func (function): A callback function to print messages to the GUI console.
    #
    # Process of this function
    #   1. Logs entry into the function and configures debug modes for underlying instrument control.
    #   2. Calculates the overall start and stop frequencies for the entire scan across all selected bands.
    #   3. Initializes the instrument with global settings (RBW, VBW, Reference Level, Preamp, High Sensitivity).
    #      Returns immediately if instrument initialization fails.
    #   4. Determines a unique CSV filename for the current scan cycle based on scan parameters and timestamp.
    #   5. Initializes `raw_scan_data_for_current_sweep` and `markers_data_from_scan` lists.
    #   6. Iterates through each `band` in `selected_bands`:
    #      a. Checks for a `stop_event` signal to break out of the band loop.
    #      b. Calculates the shifted start and stop frequencies for the current band.
    #      c. Determines the `expected_sweep_points` based on the `instrument_model`.
    #      d. Calculates the optimal segment span and total segments needed to cover the band,
    #         ensuring efficient sweeping based on sweep points and RBW step size.
    #      e. Enters a `while` loop to iterate through each segment within the current band:
    #         i. Calls `perform_segment_sweep` to acquire data for the current segment.
    #         ii. Checks for a `stop_event` after the segment sweep.
    #         iii. If `segment_raw_data` is collected, it extends `raw_scan_data_for_current_sweep`.
    #         iv. Filters the collected segment data to ensure it falls within the original band's range.
    #         v. Appends the filtered segment data to the CSV file (without header for appending).
    #         vi. Updates `last_successful_band_index`.
    #         vii. Moves to the start of the next segment.
    #   7. If a `stop_event` is set during segment processing, breaks out of the band loop.
    #   8. Prints a "Band Scan Data Collection Complete" message.
    #   9. Logs exit from the function.
    #
    # Outputs of this function
    #   tuple: `(last_successful_band_index, raw_scan_data_for_current_sweep, markers_data_from_scan)`
    #          - `last_successful_band_index` (int): The index of the last band successfully processed.
    #          - `raw_scan_data_for_current_sweep` (list): A list of `(frequency_hz, amplitude_dbm)` tuples
    #            containing all collected data points for the entire scan sweep.
    #          - `markers_data_from_scan` (list): Currently an empty list, serving as a placeholder for
    #            future marker extraction functionality.
    #          Returns `(-1, None, None)` if instrument initialization fails.
    #
    # Date / time of changes made to this file: 2025-07-30 18:15:00
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering {current_function} function. Starting scan_bands.", file=current_file, function=current_function, console_print_func=app_console_update_func)

    # Configure debug mode for underlying instrument control functions
    set_debug_mode(general_debug_enabled)
    set_log_visa_commands_mode(log_visa_commands_enabled)

    overall_start_freq_hz = min(band["Start MHz"] for band in selected_bands) * MHZ_TO_HZ
    overall_stop_freq_hz = max(band["Stop MHz"] for band in selected_bands) * MHZ_TO_HZ
    
    app_console_update_func(f"Scanning from {overall_start_freq_hz / MHZ_TO_HZ:.3f} MHz to {overall_stop_freq_hz / MHZ_TO_HZ:.3f} MHz...")
    debug_print(f"Overall scan range: {overall_start_freq_hz} Hz to {overall_stop_freq_hz} Hz", file=current_file, function=current_function, console_print_func=app_console_update_func)

    # Initialize instrument for scan (basic setup, no specific scan parameters here)
    app_console_update_func("Initializing instrument for scan settings...")
    if not initialize_instrument(
        inst,
        model_match=app_instance_ref.instrument_model,
        ref_level_dbm=ref_level_dbm,
        high_sensitivity_on=high_sensitivity,
        preamp_on=preamp_on,
        rbw_config_val=rbw_hz,
        vbw_config_val=rbw_hz * VBW_RBW_RATIO
    ):
        app_console_update_func("❌ Error: Failed to initialize instrument for scan. Aborting.")
        debug_print("Instrument initialization failed in scan_bands.", file=current_file, function=current_function, console_print_func=app_console_update_func)
        return -1, None, None

    # Apply specific scan settings after basic initialization
    app_console_update_func("Applying scan parameters to instrument...")
    if not write_safe(inst, f":SENSe:BANDwidth:RESolution {rbw_hz}HZ"):
        app_console_update_func(f"❌ Error: Failed to set RBW to {rbw_hz}Hz.")
        debug_print(f"Failed to set RBW: {rbw_hz}Hz", file=current_file, function=current_function, console_print_func=app_console_update_func)
        return -1, None, None
    
    vbw_percent = int(VBW_RBW_RATIO * 100)
    if not write_safe(inst, f":SENSe:BANDwidth:VIDeo:RATio {vbw_percent}PCT"):
        app_console_update_func(f"❌ Error: Failed to set VBW ratio to {vbw_percent}PCT.")
        debug_print(f"Failed to set VBW ratio: {vbw_percent}PCT", file=current_file, function=current_function, console_print_func=app_console_update_func)

    if not write_safe(inst, f":DISPlay:WINDow:TRACe:Y:RLEVel {ref_level_dbm}DBM"):
        app_console_update_func(f"❌ Error: Failed to set reference level to {ref_level_dbm}dBm.")
        debug_print(f"Failed to set reference level: {ref_level_dbm}dBm", file=current_file, function=current_function, console_print_func=app_console_update_func)
        return -1, None, None

    if not write_safe(inst, f":INPut:RFSense:FREQuency:SHIFt {freq_shift_hz}HZ"):
        app_console_update_func(f"❌ Error: Failed to set frequency shift to {freq_shift_hz}Hz.")
        debug_print(f"Failed to set frequency shift: {freq_shift_hz}Hz", file=current_file, function=current_function, console_print_func=app_console_update_func)

    if high_sensitivity:
        if not write_safe(inst, ":INPut:ATTenuation:AUTO OFF"):
            app_console_update_func("❌ Error: Failed to set attenuation auto OFF for high sensitivity.")
            debug_print("Failed to set attenuation auto OFF.", file=current_file, function=current_function, console_print_func=app_console_update_func)
        if not write_safe(inst, ":INPut:GAIN:STATe ON"):
            app_console_update_func("❌ Error: Failed to turn ON preamp for high sensitivity.")
            debug_print("Failed to turn ON preamp.", file=current_file, function=current_function, console_print_func=app_console_update_func)
    else:
        if not write_safe(inst, ":INPut:ATTenuation:AUTO ON"):
            app_console_update_func("❌ Error: Failed to set attenuation auto ON for normal sensitivity.")
            debug_print("Failed to set attenuation auto ON.", file=current_file, function=current_function, console_print_func=app_console_update_func)
        if not write_safe(inst, ":INPut:GAIN:STATe OFF"):
            app_console_update_func("❌ Error: Failed to turn OFF preamp for normal sensitivity.")
            debug_print("Failed to turn OFF preamp.", file=current_file, function=current_function, console_print_func=app_console_update_func)

    if preamp_on:
        if not write_safe(inst, ":INPut:GAIN:STATe ON"):
            app_console_update_func("❌ Error: Failed to turn ON preamp.")
            debug_print("Failed to turn ON preamp.", file=current_file, function=current_function, console_print_func=app_console_update_func)
    else:
        if not write_safe(inst, ":INPut:GAIN:STATe OFF"):
            app_console_update_func("❌ Error: Failed to turn OFF preamp.")
            debug_print("Failed to turn OFF preamp.", file=current_file, function=current_function, console_print_func=app_console_update_func)

    # Determine the CSV filename for this scan session (continuous raw data)
    timestamp_hm = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename_current_cycle = os.path.join(output_folder, f"{scan_name}_RBW{int(rbw_hz/1000)}K_HOLD{int(max_hold_time_seconds)}_Offset{int(freq_shift_hz)}_{timestamp_hm}.csv")

    raw_scan_data_for_current_sweep = [] # List to collect (freq, amplitude) tuples for the entire sweep
    last_successful_band_index = -1
    markers_data_from_scan = [] # To collect markers if extracted during the scan (placeholder)

    app_console_update_func("\n--- 📡 Starting Band Scan ---")
    app_console_update_func("💾 Assuming ASCII data format for trace data.")

    for i, band in enumerate(selected_bands):
        if stop_event.is_set():
            app_console_update_func("Scan stopped by user during band iteration.")
            debug_print("Scan stop event set during band iteration.", file=current_file, function=current_function, console_print_func=app_console_update_func)
            break

        band_name = band["Band Name"]
        band_start_freq_hz = (band["Start MHz"] * MHZ_TO_HZ) + freq_shift_hz
        band_stop_freq_hz = (band["Stop MHz"] * MHZ_TO_HZ) + freq_shift_hz

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        app_console_update_func(f"\n📈 [{current_time}] Processing Band: {band_name} (Shifted Range: {band_start_freq_hz/MHZ_TO_HZ:.3f} MHz to {band_stop_freq_hz/MHZ_TO_HZ:.3f} MHz)")
        debug_print(f"Processing band: {band_name} ({band_start_freq_hz}-{band_stop_freq_hz} Hz)", file=current_file, function=current_function, console_print_func=app_console_update_func)

        # Determine expected_sweep_points based on instrument model
        expected_sweep_points = 500 # Default
        if app_instance_ref.instrument_model == "N9340B":
            expected_sweep_points = 461
        elif app_instance_ref.instrument_model == "N9342CN":
            expected_sweep_points = 500
        app_console_update_func(f"📊 Using {expected_sweep_points} sweep points per trace for {band_name} ({app_instance_ref.instrument_model if app_instance_ref.instrument_model else 'Unknown'} detected).")


        full_band_span_hz = band_stop_freq_hz - band_start_freq_hz
        if full_band_span_hz <= 0:
            total_segments_in_band = 1
            optimal_segment_span_hz = full_band_span_hz
        else:
            total_segments_in_band = int(np.ceil(full_band_span_hz / (rbw_step_size_hz * (expected_sweep_points - 1))))
            if total_segments_in_band == 0:
                total_segments_in_band = 1
            optimal_segment_span_hz = full_band_span_hz / total_segments_in_band
            if expected_sweep_points > 1 and optimal_segment_span_hz < (rbw_step_size_hz * (expected_sweep_points - 1)):
                optimal_segment_span_hz = rbw_step_size_hz * (expected_sweep_points - 1)

        effective_scan_stop_freq_hz = band_start_freq_hz + (total_segments_in_band * optimal_segment_span_hz)
        app_console_update_func(f"🎯 Optimal segment span for {band_name}: {optimal_segment_span_hz / MHZ_TO_HZ:.3f} MHz.")
        app_console_update_func(f"📏 Effective scanned range for equal segments: {band_start_freq_hz/MHZ_TO_HZ:.3f} MHz to {effective_scan_stop_freq_hz/MHZ_TO_HZ:.3f} MHz.")

        current_segment_start_freq_hz = band_start_freq_hz
        segment_counter = 0

        while current_segment_start_freq_hz < effective_scan_stop_freq_hz:
            segment_counter += 1
            segment_stop_freq_hz = current_segment_start_freq_hz + optimal_segment_span_hz

            segment_raw_data = perform_segment_sweep(
                inst,
                current_segment_start_freq_hz,
                segment_stop_freq_hz,
                maxhold_enabled,
                max_hold_time_seconds,
                app_instance_ref,
                pause_event,
                stop_event,
                segment_counter,
                total_segments_in_band,
                band_name,
                app_console_update_func
            )

            if stop_event.is_set(): # Check stop event after segment sweep
                app_console_update_func(f"Scan for {band_name} interrupted after segment {segment_counter}.")
                break # Exit segment loop

            if segment_raw_data: # This check is fine as segment_raw_data is a list
                raw_scan_data_for_current_sweep.extend(segment_raw_data)
                
                # --- Write filtered segment data to CSV immediately after processing ---
                filtered_segment_data_for_csv = []
                for freq_hz, amp_value in segment_raw_data:
                    # Filter based on the original band's start and stop frequencies
                    if freq_hz >= band_start_freq_hz and freq_hz <= band_stop_freq_hz + 1e-9: # Add epsilon for float comparison
                        filtered_segment_data_for_csv.append((freq_hz, amp_value))

                if filtered_segment_data_for_csv:
                    # Removed the header from the CSV write call as requested.
                    # The write_scan_data_to_csv function will now be called with header=None.
                    csv_data_to_write = [(f / MHZ_TO_HZ, amp) for f, amp in filtered_segment_data_for_csv]
                    write_scan_data_to_csv(csv_filename_current_cycle, header=None, data=csv_data_to_write, append_mode=True, console_print_func=app_console_update_func)
                    debug_print(f"Appended {len(filtered_segment_data_for_csv)} points to {csv_filename_current_cycle}", file=current_file, function=current_function, console_print_func=app_console_update_func)
                else:
                    debug_print("No data to append to CSV after filtering for this segment.", file=current_file, function=current_function, console_print_func=app_console_update_func)
            else:
                app_console_update_func(f"🚫 No data collected for segment {segment_counter} of band {band_name}.")
                debug_print(f"No data collected for segment {segment_counter}.", file=current_file, function=current_function, console_print_func=app_console_update_func)
            
            # Update last_successful_band_index after successfully processing a band
            last_successful_band_index = i

            # Move to the start of the next segment
            current_segment_start_freq_hz = segment_stop_freq_hz

        if stop_event.is_set():
            break # Exit band loop if stop was requested during segment processing

    app_console_update_func("\n--- 🎉 Band Scan Data Collection Complete! ---")
    debug_print(f"Exiting {current_function} function. Result: {last_successful_band_index}, raw_data, Markers Data", file=current_file, function=current_function, console_print_func=app_console_update_func)
    # Return raw_scan_data_for_current_sweep for further processing in scan_controler_button_logic
    return last_successful_band_index, raw_scan_data_for_current_sweep, markers_data_from_scan # markers_data_from_scan is still a placeholder
