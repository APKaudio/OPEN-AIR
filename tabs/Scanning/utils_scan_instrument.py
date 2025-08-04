# tabs/Scanning/utils_scan_instrument.py
#
# Core logic for controlling the spectrum analyzer to perform frequency sweeps.
# Handles instrument communication, trace data acquisition, and saving to CSV.
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
# Version 20250804.030500.0 (FIXED: Added sweep initiation and wait in perform_segment_sweep to prevent VISA timeout.)
# Version 20250804.030800.0 (REFACTORED: Drastically reduced comment verbosity as per user request. FUCK!)
# Version 20250804.030900.0 (FIXED: Corrected app_instance_ref.instrument_model access and debug_print calls.)
# Version 20250804.031200.0 (FIXED: Removed accidental 'cite' placeholder from code.)
# Version 20250804.031500.0 (FIXED: Changed import path for initialize_instrument_logic to break circular dependency.)
# Version 20250804.031800.0 (FIXED: Removed top-level import of initialize_instrument_logic to break circularity. Now passed as argument.)

current_version = "20250804.031800.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250804 * 3180 * 0 # Example hash, adjust as needed

import pyvisa
import time
import numpy as np
import re
import datetime
import os
import inspect

from src.debug_logic import debug_log, log_visa_command
from src.console_logic import console_log

# REMOVED: Top-level import of initialize_instrument_logic to break circular dependency.
# from tabs.Instrument.utils_instrument_initialization import initialize_instrument_logic

from utils.utils_csv_writer import write_scan_data_to_csv
from ref.frequency_bands import MHZ_TO_HZ, VBW_RBW_RATIO


def write_safe(inst, command, console_print_func):
    """Safely writes a SCPI command to the instrument."""
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to write command: {command}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot write command. What the hell?!")
        debug_log("Instrument not connected. Fucking useless!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False
    try:
        inst.write(command)
        log_visa_command(command, "SENT")
        return True
    except Exception as e:
        console_print_func(f"❌ Error writing command '{command}': {e}. This thing is a pain in the ass!")
        debug_log(f"Error writing command '{command}': {e}. What a mess!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False

def query_safe(inst, command, console_print_func):
    """Safely queries the instrument and returns the response."""
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to query command: {command}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot query command. What the hell?!")
        debug_log("Instrument not connected. Fucking useless!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return None
    try:
        response = inst.query(command).strip()
        log_visa_command(command, "SENT")
        log_visa_command(response, "RECEIVED")
        return response
    except Exception as e:
        console_print_func(f"❌ Error querying command '{command}': {e}. This goddamn thing is broken!")
        debug_log(f"Error querying command '{command}': {e}. What a pain!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return None


def configure_instrument_for_scan(inst, center_freq_hz, span_hz, rbw_hz, ref_level_dbm,
                                  freq_shift_hz, high_sensitivity_on, preamp_on,
                                  app_console_update_func):
    """Configures the spectrum analyzer with specified settings for a scan segment."""
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Configuring instrument for scan. Center: {center_freq_hz/MHZ_TO_HZ:.3f} MHz, Span: {span_hz/MHZ_TO_HZ:.3f} MHz, RBW: {rbw_hz} Hz. Let's get this machine ready!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    if not inst:
        app_console_update_func("⚠️ Warning: Instrument not connected. Cannot configure for scan. Connect the damn thing first!")
        debug_log("Instrument not connected for configuration. Fucking useless!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False

    success = True
    # Reset and configure basic sweep parameters
    if not write_safe(inst, "*RST", app_console_update_func): success = False
    time.sleep(0.1)
    if not write_safe(inst, ":SENSe:AVERage:COUNt 1", app_console_update_func): success = False
    if not write_safe(inst, ":SENSe:SWEep:POINts 1001", app_console_update_func): success = False

    # Set scan specific parameters
    if not write_safe(inst, f":SENSe:FREQuency:CENTer {center_freq_hz}", app_console_update_func): success = False
    time.sleep(0.05)
    if not write_safe(inst, f":SENSe:FREQuency:SPAN {span_hz}", app_console_update_func): success = False
    time.sleep(0.05)
    if not write_safe(inst, f":SENSe:BANDwidth:RESolution {rbw_hz}", app_console_update_func): success = False
    time.sleep(0.05)
    if not write_safe(inst, f":DISPlay:WINDow:TRACe:Y:RLEVel {ref_level_dbm}DBM", app_console_update_func): success = False
    time.sleep(0.05)
    if not write_safe(inst, f":SENSe:FREQuency:RFShift {freq_shift_hz}", app_console_update_func): success = False
    time.sleep(0.05)

    # Set High Sensitivity and Preamplifier
    high_sensitivity_cmd = ":SENSe:POWer:RF:HSENs ON" if high_sensitivity_on else ":SENSe:POWer:RF:HSENs OFF"
    if not write_safe(inst, high_sensitivity_cmd, app_console_update_func): success = False
    time.sleep(0.05)
    preamp_cmd = ":SENSe:POWer:RF:GAIN ON" if preamp_on else ":SENSe:POWer:RF:GAIN OFF"
    if not write_safe(inst, preamp_cmd, app_console_update_func): success = False
    time.sleep(0.05)

    if success:
        app_console_update_func("✅ Instrument configured successfully for scan. Ready for data!")
        debug_log("Instrument configured successfully.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        app_console_update_func("❌ Failed to fully configure instrument for scan. This is a disaster!")
        debug_log("Failed to fully configure instrument for scan. What a mess!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    return success

def perform_single_sweep(inst, app_console_update_func):
    """Triggers a single sweep and retrieves trace data."""
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Performing single sweep... Getting that juicy data!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    if not inst:
        app_console_update_func("⚠️ Warning: Instrument not connected. Cannot perform sweep. Connect the damn thing first!")
        debug_log("Instrument not connected for sweep. Fucking useless!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return None, None

    try:
        # Stop continuous sweep, initiate single sweep, and wait
        if not write_safe(inst, ":INITiate:CONTinuous OFF", app_console_update_func): return None, None
        time.sleep(0.1)
        if not write_safe(inst, ":INITiate:IMMediate; *WAI", app_console_update_func): return None, None
        time.sleep(0.5)

        # Query frequency axis data
        freq_response = query_safe(inst, ":TRACe:X:VALues?", app_console_update_func)
        if freq_response is None:
            app_console_update_func("❌ Failed to query frequency data. This is a disaster!")
            debug_log("Failed to query frequency data. What a mess!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return None, None
        frequencies_hz = [float(f) for f in freq_response.split(',')]

        # Query trace data (power levels)
        trace_response = query_safe(inst, ":TRACe:DATA? TRACE1", app_console_update_func)
        if trace_response is None:
            app_console_update_func("❌ Failed to query trace data. This is frustrating!")
            debug_log("Failed to query trace data. What a pain!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return None, None
        power_dbm = [float(p) for p in trace_response.split(',')]

        if len(frequencies_hz) != len(power_dbm):
            app_console_update_func("❌ Mismatch between frequency and power data points. Data corrupted!")
            debug_log(f"Mismatch: Freq points {len(frequencies_hz)}, Power points {len(power_dbm)}. This is a nightmare!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return None, None

        app_console_update_func(f"✅ Single sweep complete. Collected {len(frequencies_hz)} data points. Success!")
        debug_log(f"Single sweep complete. Collected {len(frequencies_hz)} data points. Data acquired!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return frequencies_hz, power_dbm

    except Exception as e:
        app_console_update_func(f"❌ Error during single sweep: {e}. This is a disaster!")
        debug_log(f"Error during single sweep: {e}. Fucking hell!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return None, None


def perform_segment_sweep(inst, segment_start_freq_hz, segment_stop_freq_hz, maxhold_enabled, max_hold_time, app_instance_ref, pause_event, stop_event, segment_counter, total_segments_in_band, band_name, app_console_update_func):
    """Performs a single frequency sweep segment on the instrument and retrieves data."""
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function} function. Segment {segment_counter}/{total_segments_in_band}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    # Handle pause/stop events
    while pause_event.is_set():
        app_console_update_func("Scan Paused. Click Resume to continue.")
        time.sleep(0.1)
        if stop_event.is_set():
            app_console_update_func(f"Scan for {band_name} interrupted during pause in max hold for segment {segment_counter}.")
            debug_log("Stop event set during pause.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return []
    if stop_event.is_set():
        app_console_update_func(f"Scan for {band_name} interrupted during segment {segment_counter}.")
        debug_log("Stop event set before segment scan.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return []

    # Set frequency range for the current segment
    if not write_safe(inst, f":SENS:FREQ:STAR {segment_start_freq_hz};:SENS:FREQ:STOP {segment_stop_freq_hz}", app_console_update_func):
        app_console_update_func(f"❌ Error: Failed to set frequency range for segment {segment_counter}.")
        debug_log(f"Failed to set frequency range: {segment_start_freq_hz}-{segment_stop_freq_hz}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return []

    # Set trace modes
    if not write_safe(inst, ":TRAC1:MODE BLANk;:TRAC2:MODE BLANk;:TRAC3:MODE BLANk", app_console_update_func):
        app_console_update_func(f"❌ Error: Failed to blank traces for segment {segment_counter}.")
    if maxhold_enabled:
        if not write_safe(inst, ":TRAC2:MODE MAXHold;", app_console_update_func):
            app_console_update_func(f"❌ Error: Failed to set Max Hold mode for segment {segment_counter}.")

    # Initiate single sweep and wait for completion
    app_console_update_func("💬 Initiating single sweep for segment...")
    if not write_safe(inst, ":INITiate:CONTinuous OFF", app_console_update_func): return []
    if not write_safe(inst, ":INITiate:IMMediate; *WAI", app_console_update_func): return []
    debug_log("Single sweep initiated and waited for completion.",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function, special=True)

    # Wait for Max Hold values to stabilize if enabled
    if maxhold_enabled and max_hold_time > 0:
        for _ in range(int(max_hold_time * 10)):
            while pause_event.is_set():
                app_console_update_func("Scan Paused. Click Resume to continue.")
                time.sleep(0.1)
                if stop_event.is_set():
                    app_console_update_func(f"Scan for {band_name} interrupted during pause in max hold for segment {segment_counter}.")
                    return []
            if stop_event.is_set():
                app_console_update_func(f"Scan for {band_name} interrupted during max hold for segment {segment_counter}.")
                return []
            if _ % 10 == 0:
                sec_remaining = int(max_hold_time - (_ / 10))
            time.sleep(0.1)

    if stop_event.is_set():
        app_console_update_func(f"Scan for {band_name} interrupted after max hold for segment {segment_counter}.")
        debug_log("Stop event set after max hold.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return []

    # Display progress
    progress_percentage = (segment_counter / total_segments_in_band)
    bar_length = 20
    filled_length = int(round(bar_length * progress_percentage))
    progressbar = '█' * filled_length + '-' * (bar_length - filled_length)
    progress_message = f"{progressbar}🔍 Span:📊{(segment_stop_freq_hz - segment_start_freq_hz)/MHZ_TO_HZ:.3f} MHz--📈{segment_start_freq_hz/MHZ_TO_HZ:.3f} MHz to 📉{segment_stop_freq_hz/MHZ_TO_HZ:.3f} MHz   ✅{segment_counter} of {total_segments_in_band} "
    app_console_update_func(progress_message)

    segment_raw_data = []
    try:
        # Query trace data
        instrument_model = app_instance_ref.connected_instrument_model.get()
        if instrument_model == "N9340B":
            trace_data_str = query_safe(inst, ":TRAC2:DATA?", app_console_update_func)
        elif instrument_model == "N9342CN":
            trace_data_str = query_safe(inst, ":TRACe:DATA? TRACe2", app_console_update_func)
        else:
            trace_data_str = query_safe(inst, ":TRACe:DATA? TRACe2", app_console_update_func)

        if trace_data_str is None or "[Not Supported or Timeout]" in trace_data_str or not trace_data_str.strip():
            app_console_update_func("🚫 No valid trace data string received for this segment.")
            debug_log("No valid trace data string.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return []

        # Parse trace data
        data_part = None
        match = re.match(r'#\d+\d+(.*)', trace_data_str)
        if match:
            data_part = match.group(1)
        else:
            data_part = trace_data_str
            debug_log("Trace data header not found. Attempting to parse raw string directly.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

        if data_part:
            try:
                amplitudes_dbm = [float(val) for val in data_part.split(',') if val.strip()]
                debug_log(f"Parsed {len(amplitudes_dbm)} amplitude points.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)

                # Query actual start/stop frequencies from instrument
                actual_center_freq_hz = float(query_safe(inst, ":SENSe:FREQuency:CENTer?", app_console_update_func))
                actual_span_hz = float(query_safe(inst, ":SENSe:FREQuency:SPAN?", app_console_update_func))
                
                num_points = len(amplitudes_dbm)
                if num_points == 0:
                    app_console_update_func(f"⚠️ Warning: No amplitude data received for segment {segment_counter}. Skipping data processing.")
                    debug_log("No amplitude data received.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                    return []
                if num_points > 1:
                    segment_trace_start_freq = actual_center_freq_hz - (actual_span_hz / 2)
                    segment_trace_stop_freq = actual_center_freq_hz + (actual_span_hz / 2)
                    frequencies_hz = np.linspace(segment_trace_start_freq, segment_trace_stop_freq, num_points)
                else:
                    frequencies_hz = np.array([actual_center_freq_hz])

                # Ensure lengths match and append
                if len(amplitudes_dbm) == len(frequencies_hz):
                    for freq, amp in zip(frequencies_hz, amplitudes_dbm):
                        segment_raw_data.append((freq, amp))
                    debug_log(f"Collected {len(amplitudes_dbm)} data points.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                else:
                    app_console_update_func(f"❌ Error: Mismatch in data points and frequencies for segment {segment_counter}. Expected {len(frequencies_hz)}, got {len(amplitudes_dbm)} amplitudes. Raw data: {data_part[:100]}...")
                    debug_log(f"Data length mismatch. Expected {len(frequencies_hz)}, got {len(amplitudes_dbm)}.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                    return []
            except ValueError as ve:
                app_console_update_func(f"❌ Data Parsing Error in segment {segment_counter}: {ve}. Could not convert data to float. Raw data: {data_part[:100]}...")
                debug_log(f"ValueError parsing trace data: {ve}",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                return []
        else:
            app_console_update_func(f"❌ Error: No parsable data part found in trace data for segment {segment_counter}. Raw data: {trace_data_str[:100]}...")
            debug_log(f"No parsable data part found: {trace_data_str[:50]}...",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return []

    except pyvisa.errors.VisaIOError as e:
        app_console_update_func(f"❌ VISA Error during segment {segment_counter} sweep: {e}")
        debug_log(f"VISA Error in perform_segment_sweep: {e}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return []
    except Exception as e:
        app_console_update_func(f"🚨 An unexpected error occurred during segment {segment_counter} sweep: {e}\n")
        debug_log(f"Unexpected error during segment sweep: {e}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return []

    debug_log(f"Exiting {current_function} function. Collected {len(segment_raw_data)} points.",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    return segment_raw_data


def scan_bands(app_instance_ref, inst, selected_bands, rbw_hz, ref_level_dbm, freq_shift_hz, maxhold_enabled, high_sensitivity, preamp_on, rbw_step_size_hz, max_hold_time_seconds, scan_name, output_folder, stop_event, pause_event, log_visa_commands_enabled, general_debug_enabled, app_console_update_func, initialize_instrument_func): # ADDED initialize_instrument_func
    """Orchestrates a full frequency scan across multiple specified bands."""
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function} function. Starting scan_bands.",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    overall_start_freq_hz = min(band["Start MHz"] for band in selected_bands) * MHZ_TO_HZ
    overall_stop_freq_hz = max(band["Stop MHz"] for band in selected_bands) * MHZ_TO_HZ
    
    app_console_update_func(f"Scanning from {overall_start_freq_hz / MHZ_TO_HZ:.3f} MHz to {overall_stop_freq_hz / MHZ_TO_HZ:.3f} MHz...")
    debug_log(f"Overall scan range: {overall_start_freq_hz} Hz to {overall_stop_freq_hz} Hz",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    # Initialize instrument for scan
    app_console_update_func("Initializing instrument for scan settings...")
    # MODIFIED: Use the passed initialize_instrument_func
    if not initialize_instrument_func(
        inst,
        model_match=app_instance_ref.connected_instrument_model.get(),
        ref_level_dbm=ref_level_dbm,
        high_sensitivity_on=high_sensitivity,
        preamp_on=preamp_on,
        rbw_config_val=rbw_hz,
        vbw_config_val=rbw_hz * VBW_RBW_RATIO,
        console_print_func=app_console_update_func
    ):
        app_console_update_func("❌ Error: Failed to initialize instrument for scan. Aborting.")
        debug_log("Instrument initialization failed in scan_bands.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return -1, None, None

    # Apply specific scan settings
    app_console_update_func("Applying scan parameters to instrument...")
    if not write_safe(inst, f":SENSe:BANDwidth:RESolution {rbw_hz}HZ", app_console_update_func):
        app_console_update_func(f"❌ Error: Failed to set RBW to {rbw_hz}Hz.")
        debug_log(f"Failed to set RBW: {rbw_hz}Hz",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return -1, None, None
    
    vbw_percent = int(VBW_RBW_RATIO * 100)
    if not write_safe(inst, f":SENSe:BANDwidth:VIDeo:RATio {vbw_percent}PCT", app_console_update_func):
        app_console_update_func(f"❌ Error: Failed to set VBW ratio to {vbw_percent}PCT.")
        debug_log(f"Failed to set VBW ratio: {vbw_percent}PCT",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    if not write_safe(inst, f":DISPlay:WINDow:TRACe:Y:RLEVel {ref_level_dbm}DBM", app_console_update_func):
        app_console_update_func(f"❌ Error: Failed to set reference level to {ref_level_dbm}dBm.")
        debug_log(f"Failed to set reference level: {ref_level_dbm}dBm",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return -1, None, None

    if not write_safe(inst, f":SENSe:FREQuency:RFShift {freq_shift_hz}HZ", app_console_update_func):
        app_console_update_func(f"❌ Error: Failed to set frequency shift to {freq_shift_hz}Hz.")
        debug_log(f"Failed to set frequency shift: {freq_shift_hz}Hz",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    if high_sensitivity:
        if not write_safe(inst, ":SENSe:POWer:RF:HSENs ON", app_console_update_func):
            app_console_update_func("❌ Error: Failed to set High Sensitivity ON.")
            debug_log("Failed to set High Sensitivity ON.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
    else:
        if not write_safe(inst, ":SENSe:POWer:RF:HSENs OFF", app_console_update_func):
            app_console_update_func("❌ Error: Failed to set High Sensitivity OFF.")
            debug_log("Failed to set High Sensitivity OFF.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
    
    if preamp_on:
        if not write_safe(inst, ":SENSe:POWer:RF:GAIN ON", app_console_update_func):
            app_console_update_func("❌ Error: Failed to turn ON preamp.")
            debug_log("Failed to turn ON preamp.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
    else:
        if not write_safe(inst, ":SENSe:POWer:RF:GAIN OFF", app_console_update_func):
            app_console_update_func("❌ Error: Failed to turn OFF preamp.")
            debug_log("Failed to turn OFF preamp.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)


    timestamp_hm = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename_current_cycle = os.path.join(output_folder, f"{scan_name}_RBW{int(rbw_hz/1000)}K_HOLD{int(max_hold_time_seconds)}_Offset{int(freq_shift_hz)}_{timestamp_hm}.csv")

    raw_scan_data_for_current_sweep = []
    last_successful_band_index = -1
    markers_data_from_scan = []

    app_console_update_func("\n--- 📡 Starting Band Scan ---")
    app_console_update_func("💾 Assuming ASCII data format for trace data.")

    for i, band in enumerate(selected_bands):
        if stop_event.is_set():
            app_console_update_func(f"Scan stopped by user during band iteration.")
            debug_log("Scan stop event set during band iteration.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            break

        band_name = band["Band Name"]
        band_start_freq_hz = (band["Start MHz"] * MHZ_TO_HZ) + freq_shift_hz
        band_stop_freq_hz = (band["Stop MHz"] * MHZ_TO_HZ) + freq_shift_hz

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        app_console_update_func(f"\n📈 [{current_time}] Processing Band: {band_name} (Shifted Range: {band_start_freq_hz/MHZ_TO_HZ:.3f} MHz to {band_stop_freq_hz/MHZ_TO_HZ:.3f} MHz)")
        debug_log(f"Processing band: {band_name} ({band_start_freq_hz}-{band_stop_freq_hz} Hz)",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        expected_sweep_points = 500
        instrument_model = app_instance_ref.connected_instrument_model.get()
        if instrument_model == "N9340B":
            expected_sweep_points = 461
        elif instrument_model == "N9342CN":
            expected_sweep_points = 500
        app_console_update_func(f"📊 Using {expected_sweep_points} sweep points per trace for {band_name} ({instrument_model if instrument_model else 'Unknown'} detected).")


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

            if stop_event.is_set():
                app_console_update_func(f"Scan for {band_name} interrupted after segment {segment_counter}.")
                break

            if segment_raw_data:
                raw_scan_data_for_current_sweep.extend(segment_raw_data)
                
                filtered_segment_data_for_csv = []
                for freq_hz, amp_value in segment_raw_data:
                    if freq_hz >= band_start_freq_hz and freq_hz <= band_stop_freq_hz + 1e-9:
                        filtered_segment_data_for_csv.append((freq_hz, amp_value))

                if filtered_segment_data_for_csv:
                    csv_data_to_write = [(f / MHZ_TO_HZ, amp) for f, amp in filtered_segment_data_for_csv]
                    write_scan_data_to_csv(csv_filename_current_cycle, header=None, data=csv_data_to_write, append_mode=True, console_print_func=app_console_update_func)
                    debug_log(f"Appended {len(filtered_segment_data_for_csv)} points to {csv_filename_current_cycle}",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                else:
                    debug_log("No data to append to CSV after filtering for this segment.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
            else:
                app_console_update_func(f"🚫 No data collected for segment {segment_counter} of band {band_name}. What a waste!")
                debug_log(f"No data collected for segment {segment_counter}. Fucking useless!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            
            last_successful_band_index = i

            current_segment_start_freq_hz = segment_stop_freq_hz

        if stop_event.is_set():
            break

    app_console_update_func("\n--- 🎉 Band Scan Data Collection Complete! ---")
    debug_log(f"Exiting {current_function} function. Result: {last_successful_band_index}, raw_data, Markers Data. Done!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    return last_successful_band_index, raw_scan_data_for_current_sweep, markers_data_from_scan