# utils/utils_scan_instrument.py
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
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250801.2340.1 (Refactored debug_print to use debug_log and console_log.)

current_version = "20250801.2340.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250801 * 2340 * 1 # Example hash, adjust as needed

import pyvisa
import time
import numpy as np
import re
import tkinter as tk # Keeping tk for potential future GUI interactions, though messagebox is removed
import datetime
import os
# import pandas as pd # Removed: Data processing moved to scan_stitch.py
import inspect

# Updated imports for new logging functions
from src.debug_logic import debug_log, log_visa_command
from src.console_logic import console_log

# Import instrument control functions - CORRECTED PATHS
# Note: These are now the *only* imports from utils_instrument_control
from utils.utils_instrument_control import initialize_instrument # Only initialize_instrument is kept
from src.config_manager import save_config # For saving scan progress

# Import constants from frequency_bands.py - CORRECTED PATH
from ref.frequency_bands import MHZ_TO_HZ, GHZ_TO_HZ

# Import the new scan stitching logic
from process_math.scan_stitch import stitch_and_save_scan_data

# Helper functions for instrument communication, now using the new logging
def write_safe(inst, command, console_print_func):
    """
    Function Description:
    Safely writes a SCPI command to the instrument.
    Logs the command and handles potential errors.

    Inputs to this function:
    - inst (pyvisa.resources.Resource): The PyVISA instrument object.
    - command (str): The SCPI command string to write.
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Checks if the instrument is connected.
    2. Attempts to write the command.
    3. Logs success or failure to the console and debug log.

    Outputs of this function:
    - bool: True if the command was written successfully, False otherwise.

    (2025-08-01) Change: Refactored to use new logging.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to write command: {command}",
                file=__file__,
                version=current_version,
                function=current_function)
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot write command. What the hell?!")
        debug_log("Instrument not connected. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False
    try:
        inst.write(command)
        log_visa_command(command, "SENT") # Log the VISA command
        return True
    except Exception as e:
        console_print_func(f"❌ Error writing command '{command}': {e}. This thing is a pain in the ass!")
        debug_log(f"Error writing command '{command}': {e}. What a mess!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False

def query_safe(inst, command, console_print_func):
    """
    Function Description:
    Safely queries the instrument with a SCPI command and returns the response.
    Logs the command and response, and handles potential errors.

    Inputs to this function:
    - inst (pyvisa.resources.Resource): The PyVISA instrument object.
    - command (str): The SCPI query command string.
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Checks if the instrument is connected.
    2. Attempts to query the instrument.
    3. Logs the command, response, and handles errors.

    Outputs of this function:
    - str or None: The instrument's response if successful, None otherwise.

    (2025-08-01) Change: Refactored to use new logging.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to query command: {command}",
                file=__file__,
                version=current_version,
                function=current_function)
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot query command. What the hell?!")
        debug_log("Instrument not connected. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return None
    try:
        response = inst.query(command).strip()
        log_visa_command(command, "SENT") # Log the VISA command
        log_visa_command(response, "RECEIVED") # Log the VISA response
        return response
    except Exception as e:
        console_print_func(f"❌ Error querying command '{command}': {e}. This goddamn thing is broken!")
        debug_log(f"Error querying command '{command}': {e}. What a pain!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return None


def configure_instrument_for_scan(inst, center_freq_hz, span_hz, rbw_hz, ref_level_dbm,
                                  freq_shift_hz, high_sensitivity_on, preamp_on,
                                  app_console_update_func):
    # This function description tells me what this function does
    # Configures the spectrum analyzer with the specified settings before a scan.
    # It sends SCPI commands for center frequency, span, RBW, reference level,
    # frequency shift, high sensitivity mode, and preamplifier state.
    #
    # Inputs to this function:
    #   inst (pyvisa.resources.Resource): The PyVISA instrument object.
    #   center_freq_hz (float): Center frequency for the scan segment in Hz.
    #   span_hz (float): Span for the scan segment in Hz.
    #   rbw_hz (float): Resolution Bandwidth in Hz.
    #   ref_level_dbm (float): Reference level in dBm.
    #   freq_shift_hz (float): Frequency shift in Hz.
    #   high_sensitivity_on (bool): True to enable high sensitivity mode, False otherwise.
    #   preamp_on (bool): True to enable preamplifier, False otherwise.
    #   app_console_update_func (function): Function to print messages to the GUI console.
    #
    # Process of this function:
    #   1. Prints debug messages.
    #   2. Checks if the instrument is connected.
    #   3. Sends a series of SCPI commands using `write_safe` to configure the instrument:
    #      - Reset (RST)
    #      - Set average count to 1 (no averaging during raw scan)
    #      - Set sweep points to 1001 (fixed for consistency)
    #      - Set center frequency
    #      - Set span
    #      - Set RBW
    #      - Set reference level
    #      - Set frequency shift
    #      - Set high sensitivity (if applicable)
    #      - Set preamplifier (if applicable)
    #   4. Introduces small delays after critical commands.
    #   5. Logs success or failure for each command.
    #   6. Returns True if all configurations were successfully sent, False otherwise.
    #
    # Outputs of this function:
    #   bool: True if configuration was successful, False otherwise.
    #
    # (2025-07-30) Change: Added high_sensitivity_on and preamp_on parameters and commands.
    # (2025-08-01 1106.1) Change: No functional changes.
    # (2025-08-01 2340.1) Change: Refactored debug_print to use debug_log and console_log.
    """
    Configures the spectrum analyzer with the specified settings before a scan.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Configuring instrument for scan. Center: {center_freq_hz/MHZ_TO_HZ:.3f} MHz, Span: {span_hz/MHZ_TO_HZ:.3f} MHz, RBW: {rbw_hz} Hz. Let's get this machine ready!",
                file=__file__,
                version=current_version,
                function=current_function)

    if not inst:
        app_console_update_func("⚠️ Warning: Instrument not connected. Cannot configure for scan. Connect the damn thing first!")
        debug_log("Instrument not connected for configuration. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False

    success = True
    # Reset the instrument to a known state
    if not write_safe(inst, "*RST", app_console_update_func): success = False
    time.sleep(0.1) # Give instrument time to reset

    # Set average count to 1 (no averaging during raw scan)
    if not write_safe(inst, ":SENSe:AVERage:COUNt 1", app_console_update_func): success = False
    # Set sweep points (fixed for consistency)
    if not write_safe(inst, ":SENSe:SWEep:POINts 1001", app_console_update_func): success = False

    # Set center frequency
    if not write_safe(inst, f":SENSe:FREQuency:CENTer {center_freq_hz}", app_console_update_func): success = False
    time.sleep(0.05) # Small delay

    # Set span
    if not write_safe(inst, f":SENSe:FREQuency:SPAN {span_hz}", app_console_update_func): success = False
    time.sleep(0.05) # Small delay

    # Set RBW
    if not write_safe(inst, f":SENSe:BANDwidth:RESolution {rbw_hz}", app_console_update_func): success = False
    time.sleep(0.05) # Small delay

    # Set Reference Level
    if not write_safe(inst, f":DISPlay:WINDow:TRACe:Y:RLEVel {ref_level_dbm}DBM", app_console_update_func): success = False
    time.sleep(0.05)

    # Set Frequency Shift
    if not write_safe(inst, f":SENSe:FREQuency:RFShift {freq_shift_hz}", app_console_update_func): success = False
    time.sleep(0.05)

    # Set High Sensitivity
    high_sensitivity_cmd = ":SENSe:POWer:RF:HSENs ON" if high_sensitivity_on else ":SENSe:POWer:RF:HSENs OFF"
    if not write_safe(inst, high_sensitivity_cmd, app_console_update_func): success = False
    time.sleep(0.05)

    # Set Preamplifier
    preamp_cmd = ":SENSe:POWer:RF:GAIN ON" if preamp_on else ":SENSe:POWer:RF:GAIN OFF"
    if not write_safe(inst, preamp_cmd, app_console_update_func): success = False
    time.sleep(0.05)

    if success:
        app_console_update_func("✅ Instrument configured successfully for scan. Ready for data!")
        debug_log("Instrument configured successfully.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    else:
        app_console_update_func("❌ Failed to fully configure instrument for scan. This is a disaster!")
        debug_log("Failed to fully configure instrument for scan. What a mess!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    return success

def perform_single_sweep(inst, app_console_update_func):
    # This function description tells me what this function does
    # Triggers a single sweep on the instrument and retrieves the trace data.
    # It sets the sweep mode to single, waits for completion, and then queries
    # the trace data (frequencies and power levels).
    #
    # Inputs to this function:
    #   inst (pyvisa.resources.Resource): The PyVISA instrument object.
    #   app_console_update_func (function): Function to print messages to the GUI console.
    #
    # Process of this function:
    #   1. Prints debug messages.
    #   2. Checks if the instrument is connected.
    #   3. Sets the sweep mode to single using `:INITiate:CONTinuous OFF`.
    #   4. Triggers a single sweep using `:INITiate:IMMediate; *WAI`.
    #   5. Queries the frequency axis data using `:TRACe:X:VALues?`.
    #   6. Queries the trace data (power levels) using `:TRACe:DATA? TRACE1`.
    #   7. Parses the responses into lists of floats.
    #   8. Logs success or failure.
    #   9. Returns the frequency and power data, or (None, None) on error.
    #
    # Outputs of this function:
    #   tuple: (list of float, list of float) or (None, None)
    #          - Frequencies in Hz.
    #          - Power levels in dBm.
    #
    # (2025-07-30) Change: No functional changes.
    # (2025-08-01 1106.1) Change: No functional changes.
    # (2025-08-01 2340.1) Change: Refactored debug_print to use debug_log and console_log.
    """
    Triggers a single sweep on the instrument and retrieves the trace data.
    Returns (frequencies_hz, power_dbm) or (None, None) on error.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Performing single sweep... Getting that juicy data!",
                file=__file__,
                version=current_version,
                function=current_function)

    if not inst:
        app_console_update_func("⚠️ Warning: Instrument not connected. Cannot perform sweep. Connect the damn thing first!")
        debug_log("Instrument not connected for sweep. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return None, None

    try:
        # Stop continuous sweep and initiate single sweep
        if not write_safe(inst, ":INITiate:CONTinuous OFF", app_console_update_func): return None, None
        time.sleep(0.1) # Small delay
        if not write_safe(inst, ":INITiate:IMMediate; *WAI", app_console_update_func): return None, None
        time.sleep(0.5) # Wait for sweep to complete (adjust as needed)

        # Query frequency axis data
        freq_response = query_safe(inst, ":TRACe:X:VALues?", app_console_update_func)
        if freq_response is None:
            app_console_update_func("❌ Failed to query frequency data. This is a disaster!")
            debug_log("Failed to query frequency data. What a mess!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return None, None
        frequencies_hz = [float(f) for f in freq_response.split(',')]

        # Query trace data (power levels)
        trace_response = query_safe(inst, ":TRACe:DATA? TRACE1", app_console_update_func)
        if trace_response is None:
            app_console_update_func("❌ Failed to query trace data. This is frustrating!")
            debug_log("Failed to query trace data. What a pain!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return None, None
        power_dbm = [float(p) for p in trace_response.split(',')]

        if len(frequencies_hz) != len(power_dbm):
            app_console_update_func("❌ Mismatch between frequency and power data points. Data corrupted!")
            debug_log(f"Mismatch: Freq points {len(frequencies_hz)}, Power points {len(power_dbm)}. This is a nightmare!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return None, None

        app_console_update_func(f"✅ Single sweep complete. Collected {len(frequencies_hz)} data points. Success!")
        debug_log(f"Single sweep complete. Collected {len(frequencies_hz)} data points. Data acquired!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return frequencies_hz, power_dbm

    except Exception as e:
        app_console_update_func(f"❌ Error during single sweep: {e}. This is a disaster!")
        debug_log(f"Error during single sweep: {e}. Fucking hell!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return None, None


def scan_bands(app_instance, selected_bands, progress_callback, stop_event, app_console_update_func):
    # This function description tells me what this function does
    # Orchestrates the scanning of selected frequency bands.
    # It iterates through each selected band, divides it into segments if necessary,
    # configures the instrument for each segment, performs sweeps, and collects data.
    # It also handles saving intermediate scan data and updating scan progress.
    #
    # Inputs to this function:
    #   app_instance (object): Reference to the main application instance
    #                          to access instrument (`app_instance.inst`),
    #                          configuration variables, and other shared states.
    #   selected_bands (list): A list of dictionaries, each representing a selected
    #                          frequency band with "Band Name", "Start MHz", "Stop MHz".
    #   progress_callback (function): A function to update the GUI with scan progress.
    #   stop_event (threading.Event): An event object to signal scan termination.
    #   app_console_update_func (function): Function to print messages to the GUI console.
    #
    # Process of this function:
    #   1. Prints debug messages.
    #   2. Checks if an instrument is connected.
    #   3. Initializes data structures for raw scan data and markers.
    #   4. Iterates through each `selected_band`:
    #      a. Calculates segment parameters based on `scan_rbw_segmentation_var`.
    #      b. Iterates through each segment within the band:
    #         i. Checks `stop_event` for termination signal.
    #         ii. Configures the instrument for the current segment using `configure_instrument_for_scan`.
    #         iii. Performs a single sweep using `perform_single_sweep`.
    #         iv. Collects frequency and power data.
    #         v. Appends data to `raw_scan_data_for_current_sweep`.
    #         vi. Updates progress via `progress_callback`.
    #         vii. Saves intermediate scan data to a temporary CSV file.
    #   5. Logs completion or interruption.
    #   6. Returns `last_successful_band_index`, `raw_scan_data_for_current_sweep`, and `markers_data`.
    #
    # Outputs of this function:
    #   tuple: (last_successful_band_index, raw_scan_data_for_current_sweep, markers_data)
    #          - last_successful_band_index (int): Index of the last successfully scanned band.
    #          - raw_scan_data_for_current_sweep (list of dict): Raw frequency and power data.
    #          - markers_data (list): Placeholder for marker data (not fully implemented here).
    #
    # (2025-07-30) Change: Added logic for scan segmentation.
    # (2025-07-30) Change: Added saving of intermediate scan data.
    # (2025-08-01 1106.1) Change: No functional changes.
    # (2025-08-01 2340.1) Change: Refactored debug_print to use debug_log and console_log.
    """
    Performs a scan across the specified frequency bands, segmenting if necessary.
    Collects raw trace data and returns it.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Starting band scan for {len(selected_bands)} bands. Let's get some data!",
                file=__file__,
                version=current_version,
                function=current_function)

    inst = app_instance.inst
    if not inst:
        app_console_update_func("⚠️ Warning: Instrument not connected. Cannot start scan. Connect the damn thing first!")
        debug_log("Instrument not connected for scan. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return -1, [], []

    raw_scan_data_for_current_sweep = [] # List of dictionaries: [{'Frequency (Hz)': [...], 'Power (dBm)': [...]}, ...]
    markers_data = [] # Placeholder for marker data if collected during scan
    last_successful_band_index = -1 # To track progress if interrupted

    total_bands = len(selected_bands)
    app_console_update_func(f"--- Starting Scan across {total_bands} selected bands ---")

    for i, band_item in enumerate(selected_bands):
        if stop_event.is_set():
            app_console_update_func("Scan interrupted by user. Aborting!")
            debug_log("Scan interrupted by user. Quitting this madness!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            break

        band = band_item["band"]
        band_name = band["Band Name"]
        start_freq_mhz = band["Start MHz"]
        stop_freq_mhz = band["Stop MHz"]

        start_freq_hz = start_freq_mhz * MHZ_TO_HZ
        stop_freq_hz = stop_freq_mhz * MHZ_TO_HZ

        app_console_update_func(f"\n--- Scanning Band: {band_name} ({start_freq_mhz:.3f} - {stop_freq_mhz:.3f} MHz) ---")
        debug_log(f"Scanning Band: {band_name} ({start_freq_hz} - {stop_freq_hz} Hz). Getting ready!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Determine segmentation
        segment_rbw_hz = float(app_instance.scan_rbw_segmentation_var.get())
        if segment_rbw_hz <= 0:
            app_console_update_func("❌ Scan RBW Segmentation must be greater than 0. Using full band scan. You broke it!")
            debug_log("Scan RBW Segmentation is <= 0. Using full band scan. What a mess!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            segment_rbw_hz = stop_freq_hz - start_freq_hz # Effectively no segmentation

        # Calculate number of segments and segment span
        # Ensure segment_rbw_hz is not zero to prevent division by zero
        if segment_rbw_hz == 0:
            segment_rbw_hz = 1 # Fallback to 1 Hz to avoid division by zero, though this should be caught earlier
            debug_log("segment_rbw_hz was 0, set to 1 to prevent division by zero. This shouldn't happen!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        num_segments = int(np.ceil((stop_freq_hz - start_freq_hz) / segment_rbw_hz))
        if num_segments == 0: # Handle case where band is smaller than segment_rbw_hz
            num_segments = 1
        segment_span_hz = (stop_freq_hz - start_freq_hz) / num_segments

        app_console_update_func(f"Band will be scanned in {num_segments} segments with span {segment_span_hz / MHZ_TO_HZ:.3f} MHz each.")
        debug_log(f"Band {band_name} will be scanned in {num_segments} segments, each with span {segment_span_hz} Hz. Let's do this!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        current_segment_start_freq_hz = start_freq_hz
        for segment_counter in range(num_segments):
            if stop_event.is_set():
                app_console_update_func("Scan interrupted during segment processing. Aborting!")
                debug_log("Scan interrupted during segment processing. Quitting this madness!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                break

            segment_center_freq_hz = current_segment_start_freq_hz + (segment_span_hz / 2)
            segment_stop_freq_hz = current_segment_start_freq_hz + segment_span_hz

            # Ensure segment_stop_freq_hz does not exceed band_stop_freq_hz due to float precision
            if segment_stop_freq_hz > stop_freq_hz + 1: # Add a small tolerance
                 segment_stop_freq_hz = stop_freq_hz
                 segment_span_hz = stop_freq_hz - current_segment_start_freq_hz # Adjust span for last segment
                 segment_center_freq_hz = current_segment_start_freq_hz + (segment_span_hz / 2)

            app_console_update_func(f"  Scanning Segment {segment_counter + 1}/{num_segments}: Center {segment_center_freq_hz / MHZ_TO_HZ:.3f} MHz, Span {segment_span_hz / MHZ_TO_HZ:.3f} MHz")
            debug_log(f"Scanning Segment {segment_counter + 1}/{num_segments}: Center {segment_center_freq_hz} Hz, Span {segment_span_hz} Hz. Getting ready for sweep!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

            # Configure instrument for this segment
            config_success = configure_instrument_for_scan(
                inst,
                segment_center_freq_hz,
                segment_span_hz,
                float(app_instance.scan_rbw_hz_var.get()), # Use scanner RBW from config
                float(app_instance.reference_level_dbm_var.get()),
                float(app_instance.freq_shift_hz_var.get()),
                app_instance.high_sensitivity_var.get(),
                app_instance.preamp_on_var.get(),
                app_console_update_func
            )

            if not config_success:
                app_console_update_func(f"❌ Failed to configure instrument for segment {segment_counter + 1}. Skipping segment. This is a disaster!")
                debug_log(f"Failed to configure instrument for segment {segment_counter + 1}. What a mess!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                current_segment_start_freq_hz = segment_stop_freq_hz # Still advance to next segment
                continue

            # Perform sweep and get data
            frequencies, powers = perform_single_sweep(inst, app_console_update_func)

            if frequencies and powers:
                # Store raw data for later stitching
                raw_scan_data_for_current_sweep.append({
                    'Frequency (Hz)': frequencies,
                    'Power (dBm)': powers,
                    'Band Name': band_name,
                    'Segment Center (Hz)': segment_center_freq_hz,
                    'Segment Span (Hz)': segment_span_hz,
                    'Timestamp': datetime.datetime.now().isoformat()
                })
                app_console_update_func(f"  Collected {len(frequencies)} points for segment {segment_counter + 1}. Nice!")
                debug_log(f"Collected {len(frequencies)} points for segment {segment_counter + 1}. Data in hand!",
                            file=__file__,
                            version=current_version,
                            function=current_function)

                # Update progress
                progress_percent = ((i * num_segments + (segment_counter + 1)) / (total_bands * num_segments)) * 100
                progress_callback(progress_percent)
                debug_log(f"Progress: {progress_percent:.2f}%. Keeping track!",
                            file=__file__,
                            version=current_version,
                            function=current_function)

                # Save intermediate data to a temporary file
                # This ensures data is not lost if the application crashes mid-scan
                temp_output_dir = os.path.join(app_instance.output_folder_var.get(), "temp_scans")
                os.makedirs(temp_output_dir, exist_ok=True)
                temp_filename = os.path.join(temp_output_dir, f"temp_scan_{band_name}_segment_{segment_counter + 1}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
                
                try:
                    with open(temp_filename, 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(['Frequency (Hz)', 'Power (dBm)'])
                        for freq, power in zip(frequencies, powers):
                            writer.writerow([freq, power])
                    app_console_update_func(f"  Saved intermediate data to: {os.path.basename(temp_filename)}. Safety first!")
                    debug_log(f"Saved intermediate data to: {temp_filename}. Data secured!",
                                file=__file__,
                                version=current_version,
                                function=current_function)
                except Exception as e:
                    app_console_update_func(f"❌ Error saving intermediate scan data to CSV: {e}. This is a disaster!")
                    debug_log(f"Error saving intermediate scan data to CSV: {e}. Fucking hell!",
                                file=__file__,
                                version=current_version,
                                function=current_function)
            else:
                app_console_update_func(f"🚫 No data collected for segment {segment_counter} of band {band_name}. What a waste!")
                debug_log(f"No data collected for segment {segment_counter}. Fucking useless!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            
            # Update last_successful_band_index after successfully processing a band
            last_successful_band_index = i

            # Move to the start of the next segment
            current_segment_start_freq_hz = segment_stop_freq_hz

        if stop_event.is_set():
            break # Exit band loop if stop was requested during segment processing

    app_console_update_func("\n--- 🎉 Band Scan Data Collection Complete! ---")
    debug_log(f"Exiting {current_function} function. Result: {last_successful_band_index}, raw_data, Markers Data. Done!",
                file=__file__,
                version=current_version,
                function=current_function)
    # Return raw_scan_data_for_current_sweep for further processing in scan_controler_button_logic
    return last_successful_band_index, raw_scan_data_for_current_sweep, markers_data
