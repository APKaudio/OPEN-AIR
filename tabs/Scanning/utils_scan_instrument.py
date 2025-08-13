# tabs/Scanning/utils_scan_instrument.py
#
# Core logic for controlling the spectrum analyzer to perform frequency sweeps.
# Handles instrument communication, trace data acquisition, and saving to CSV.
# This module also contains the logic for initiating and running the scan thread.
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
# Version 20250813.160010.1

import pyvisa
import time
import numpy as np
import re
import datetime
import os
import inspect
import threading
import pandas as pd

from display.debug_logic import debug_log, log_visa_command
from display.console_logic import console_log
from process_math.scan_stitch import stitch_and_save_scan_data
from src.connection_status_logic import update_connection_status_logic

from utils.utils_csv_writer import write_scan_data_to_csv
from ref.frequency_bands import MHZ_TO_HZ, VBW_RBW_RATIO

current_version = "20250813.160010.1"
current_version_hash = (20250813 * 160010 * 1)

def initiate_scan_thread(app_instance, console_print_func, stop_event, pause_event, update_progress_func):
    """
    Function Description:
    Initiates the spectrum scan in a separate thread. This is the main entry point
    called by the Orchestrator GUI to start the scanning process.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
    
    if app_instance.scan_thread and app_instance.scan_thread.is_alive():
        console_print_func("⚠️ Process already running.")
        return False

    if not app_instance.is_connected.get():
        console_print_func("❌ Instrument not connected. Cannot start.")
        return False

    selected_bands = [band_item["band"] for band_item in app_instance.band_vars if band_item["level"] > 0]
    if not selected_bands:
        console_print_func("⚠️ No bands selected for scan.")
        return False

    stop_event.clear()
    pause_event.clear()
    app_instance.is_paused_by_user = False

    app_instance.scan_thread = threading.Thread(
        target=_scan_thread_target,
        args=(app_instance, selected_bands, stop_event, pause_event, console_print_func, update_progress_func)
    )
    app_instance.scan_thread.daemon = True
    app_instance.scan_thread.start()
    debug_log(f"Scan thread started successfully.", file=os.path.basename(__file__), version=current_version, function=current_function)
    return True

def _scan_thread_target(app_instance, selected_bands, stop_event, pause_event, console_print_func, update_progress_func):
    """
    The main function executed in the scanning thread. It orchestrates the scan process.
    """
    current_function = inspect.currentframe().f_code.co_name
    console_print_func("--- Initiating Spectrum Scan ---")
    try:
        from tabs.Instrument.utils_instrument_initialization import initialize_instrument_logic
        
        raw_scan_data, markers_data = scan_bands(
            app_instance_ref=app_instance,
            inst=app_instance.inst,
            selected_bands=selected_bands,
            rbw_hz=float(app_instance.scan_rbw_hz_var.get()),
            ref_level_dbm=float(app_instance.reference_level_dbm_var.get()),
            freq_shift_hz=float(app_instance.freq_shift_hz_var.get()),
            maxhold_enabled=bool(app_instance.maxhold_enabled_var.get()),
            high_sensitivity=app_instance.high_sensitivity_var.get(),
            preamp_on=app_instance.preamp_on_var.get(),
            rbw_step_size_hz=float(app_instance.rbw_step_size_hz_var.get()),
            max_hold_time_seconds=float(app_instance.maxhold_time_seconds_var.get()),
            scan_name=app_instance.scan_name_var.get(),
            output_folder=app_instance.output_folder_var.get(),
            stop_event=stop_event,
            pause_event=pause_event,
            log_visa_commands_enabled=app_instance.log_visa_commands_enabled_var.get(),
            general_debug_enabled=app_instance.general_debug_enabled_var.get(),
            app_console_update_func=console_print_func,
            initialize_instrument_func=initialize_instrument_logic
        )

        if not stop_event.is_set():
            console_print_func("\n--- Stitching and saving scan data ---")
            stitch_and_save_scan_data(
                raw_scan_data_for_current_sweep=raw_scan_data,
                output_folder=app_instance.output_folder_var.get(),
                scan_name=app_instance.scan_name_var.get(),
                operator_name=app_instance.operator_name_var.get(),
                venue_name=app_instance.venue_name_var.get(),
                equipment_used=app_instance.scanner_type_var.get(),
                notes=app_instance.notes_var.get(),
                postal_code=app_instance.venue_postal_code_var.get(),
                latitude="N/A", # Placeholder
                longitude="N/A", # Placeholder
                antenna_type=app_instance.selected_antenna_type_var.get(),
                antenna_amplifier=app_instance.selected_amplifier_type_var.get(),
                console_print_func=console_print_func
            )
            console_print_func("--- Scan process finished. ---")
        else:
            console_print_func("--- Scan process stopped by user. ---")

    except Exception as e:
        console_print_func(f"❌ An error occurred during scan: {e}")
        debug_log(f"Error in scan thread target: {e}",
                    file=os.path.basename(__file__), function="_scan_thread_target")
    finally:
        # Update button states via the orchestrator_gui attribute
        app_instance.orchestrator_gui.is_running = False
        app_instance.orchestrator_gui.is_paused = False
        app_instance.after(0, lambda: app_instance.orchestrator_gui._update_button_states())
        app_instance.after(0, lambda: update_connection_status_logic(app_instance, app_instance.is_connected.get(), False, console_print_func))

def write_safe(inst, command, app_instance_ref, app_console_update_func):
    """Safely writes a SCPI command to the instrument."""
    # ... (function content is unchanged)
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to write command: {command}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    if not inst:
        app_instance_ref.after(0, lambda: app_console_update_func("⚠️ Warning: Instrument not connected. Cannot write command. What the hell?!"))
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
        app_instance_ref.after(0, lambda: app_console_update_func(f"❌ Error writing command '{command}': {e}. This thing is a pain in the ass!"))
        debug_log(f"Error writing command '{command}': {e}. What a mess!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False

def query_safe(inst, command, app_instance_ref, app_console_update_func):
    """Safely queries the instrument and returns the response."""
    # ... (function content is unchanged)
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to query command: {command}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    if not inst:
        app_instance_ref.after(0, lambda: app_console_update_func("⚠️ Warning: Instrument not connected. Cannot query command. What the hell?!"))
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
        app_instance_ref.after(0, lambda: app_console_update_func(f"❌ Error querying command '{command}': {e}. This goddamn thing is broken!"))
        debug_log(f"Error querying command '{command}': {e}. What a pain!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return None


def configure_instrument_for_scan(inst, center_freq_hz, span_hz, rbw_hz, ref_level_dbm,
                                  freq_shift_hz, high_sensitivity_on, preamp_on,
                                  app_instance_ref, app_console_update_func):
    """Configures the spectrum analyzer with specified settings for a scan segment."""
    # ... (function content is unchanged)
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Configuring instrument for scan. Center: {center_freq_hz/MHZ_TO_HZ:.3f} MHz, Span: {span_hz/MHZ_TO_HZ:.3f} MHz, RBW: {rbw_hz} Hz. Let's get this machine ready!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    if not inst:
        app_instance_ref.after(0, lambda: app_console_update_func("⚠️ Warning: Instrument not connected. Cannot configure for scan. Connect the damn thing first!"))
        debug_log("Instrument not connected for configuration. Fucking useless!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False

    success = True
    if not write_safe(inst, "*RST", app_instance_ref, app_console_update_func): success = False
    time.sleep(0.1)
    if not write_safe(inst, ":SENSe:AVERage:COUNt 1", app_instance_ref, app_console_update_func): success = False
    if not write_safe(inst, ":SENSe:SWEep:POINts 1001", app_instance_ref, app_console_update_func): success = False
    if not write_safe(inst, f":SENSe:FREQuency:CENTer {center_freq_hz}", app_instance_ref, app_console_update_func): success = False
    time.sleep(0.05)
    if not write_safe(inst, f":SENSe:FREQuency:SPAN {span_hz}", app_instance_ref, app_console_update_func): success = False
    time.sleep(0.05)
    if not write_safe(inst, f":SENSe:BANDwidth:RESolution {rbw_hz}", app_instance_ref, app_console_update_func): success = False
    time.sleep(0.05)
    if not write_safe(inst, f":DISPlay:WINDow:TRACe:Y:RLEVel {ref_level_dbm}DBM", app_instance_ref, app_console_update_func): success = False
    time.sleep(0.05)
    if not write_safe(inst, f":SENSe:FREQuency:RFShift {freq_shift_hz}", app_instance_ref, app_console_update_func): success = False
    time.sleep(0.05)
    high_sensitivity_cmd = ":SENSe:POWer:RF:HSENs ON" if high_sensitivity_on else ":SENSe:POWer:RF:HSENs OFF"
    if not write_safe(inst, high_sensitivity_cmd, app_instance_ref, app_console_update_func): success = False
    time.sleep(0.05)
    preamp_cmd = ":SENSe:POWer:RF:GAIN ON" if preamp_on else ":SENSe:POWer:RF:GAIN OFF"
    if not write_safe(inst, preamp_cmd, app_instance_ref, app_console_update_func): success = False
    time.sleep(0.05)

    if success:
        app_instance_ref.after(0, lambda: app_console_update_func("✅ Instrument configured successfully for scan. Ready for data!"))
    else:
        app_instance_ref.after(0, lambda: app_console_update_func("❌ Failed to fully configure instrument for scan. This is a disaster!"))
    return success

def perform_single_sweep(inst, app_instance_ref, app_console_update_func):
    """Triggers a single sweep and retrieves trace data."""
    # ... (function content is unchanged)
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Performing single sweep... Getting that juicy data!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    if not inst:
        app_instance_ref.after(0, lambda: app_console_update_func("⚠️ Warning: Instrument not connected. Cannot perform sweep. Connect the damn thing first!"))
        return None, None

    try:
        if not write_safe(inst, ":INITiate:CONTinuous OFF", app_instance_ref, app_console_update_func): return None, None
        time.sleep(0.1)
        if not write_safe(inst, ":INITiate:IMMediate; *WAI", app_instance_ref, app_console_update_func): return None, None
        time.sleep(0.5)

        freq_response = query_safe(inst, ":TRACe:X:VALues?", app_instance_ref, app_console_update_func)
        if freq_response is None:
            app_instance_ref.after(0, lambda: app_console_update_func("❌ Failed to query frequency data. This is a disaster!"))
            return None, None
        frequencies_hz = [float(f) for f in freq_response.split(',')]

        trace_response = query_safe(inst, ":TRACe:DATA? TRACE1", app_instance_ref, app_console_update_func)
        if trace_response is None:
            app_instance_ref.after(0, lambda: app_console_update_func("❌ Failed to query trace data. This is frustrating!"))
            return None, None
        power_dbm = [float(p) for p in trace_response.split(',')]

        if len(frequencies_hz) != len(power_dbm):
            app_instance_ref.after(0, lambda: app_console_update_func("❌ Mismatch between frequency and power data points. Data corrupted!"))
            return None, None

        app_instance_ref.after(0, lambda: app_console_update_func(f"✅ Single sweep complete. Collected {len(frequencies_hz)} data points. Success!"))
        return frequencies_hz, power_dbm

    except Exception as e:
        app_instance_ref.after(0, lambda: app_console_update_func(f"❌ Error during single sweep: {e}. This is a disaster!"))
        return None, None

def perform_segment_sweep(inst, segment_start_freq_hz, segment_stop_freq_hz, maxhold_enabled, max_hold_time, app_instance_ref, pause_event, stop_event, segment_counter, total_segments_in_band, band_name, app_console_update_func, current_segment_start_freq_hz):
    """Performs a single frequency sweep segment on the instrument and retrieves data."""
    # ... (function content is unchanged, but I must add the missing `current_segment_start_freq_hz` to the signature)
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function} function. Segment {segment_counter}/{total_segments_in_band}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    while pause_event.is_set():
        app_instance_ref.after(0, lambda: app_console_update_func("Scan Paused. Click Resume to continue."))
        time.sleep(0.1)
        if stop_event.is_set():
            app_instance_ref.after(0, lambda: app_console_update_func(f"Scan for {band_name} interrupted during pause in max hold for segment {segment_counter}."))
            return []
    if stop_event.is_set():
        app_instance_ref.after(0, lambda: app_console_update_func(f"Scan for {band_name} interrupted during segment {segment_counter}."))
        return []

    if not write_safe(inst, f":SENS:FREQ:STAR {segment_start_freq_hz};:SENS:FREQ:STOP {segment_stop_freq_hz}", app_instance_ref, app_console_update_func):
        app_instance_ref.after(0, lambda: app_console_update_func(f"❌ Error: Failed to set frequency range for segment {segment_counter}."))
        return []

    if not write_safe(inst, ":TRAC1:MODE BLANk;:TRAC2:MODE BLANk;:TRAC3:MODE BLANk", app_instance_ref, app_console_update_func):
        app_instance_ref.after(0, lambda: app_console_update_func(f"❌ Error: Failed to blank traces for segment {segment_counter}."))
    if maxhold_enabled:
        if not write_safe(inst, ":TRAC2:MODE MAXHold;", app_instance_ref, app_console_update_func):
            app_instance_ref.after(0, lambda: app_console_update_func(f"❌ Error: Failed to set Max Hold mode for segment {segment_counter}."))

    app_instance_ref.after(0, lambda: app_console_update_func("💬 Initiating single sweep for segment..."))
    if not write_safe(inst, ":INITiate:CONTinuous OFF", app_instance_ref, app_console_update_func): return []
    if not write_safe(inst, ":INITiate:IMMediate; *WAI", app_instance_ref, app_console_update_func): return []
    
    if maxhold_enabled and max_hold_time > 0:
        for _ in range(int(max_hold_time * 10)):
            while pause_event.is_set():
                app_instance_ref.after(0, lambda: app_console_update_func("Scan Paused. Click Resume to continue."))
                time.sleep(0.1)
            if stop_event.is_set():
                app_instance_ref.after(0, lambda: app_console_update_func(f"Scan for {band_name} interrupted during pause in max hold for segment {segment_counter}."))
                return []
            if stop_event.is_set():
                app_instance_ref.after(0, lambda: app_console_update_func(f"Scan for {band_name} interrupted during max hold for segment {segment_counter}."))
                return []
            if _ % 10 == 0:
                sec_remaining = int(max_hold_time - (_ / 10))
            time.sleep(0.1)

    if stop_event.is_set():
        app_instance_ref.after(0, lambda: app_console_update_func(f"Scan for {band_name} interrupted after max hold for segment {segment_counter}."))
        return []

    progress_percentage = (segment_counter / total_segments_in_band)
    bar_length = 20
    filled_length = int(round(bar_length * progress_percentage))
    progressbar = '█' * filled_length + '-' * (bar_length - filled_length)
    progress_message = f"{progressbar}🔍 Span:📊{(segment_stop_freq_hz - segment_start_freq_hz)/MHZ_TO_HZ:.3f} MHz--📈{current_segment_start_freq_hz/MHZ_TO_HZ:.3f} MHz to 📉{segment_stop_freq_hz/MHZ_TO_HZ:.3f} MHz   ✅{segment_counter} of {total_segments_in_band} "
    app_instance_ref.after(0, lambda msg=progress_message: app_console_update_func(msg))
    
    segment_raw_data = []
    # (rest of the logic from original file...)
    try:
        instrument_model = app_instance_ref.connected_instrument_model.get()
        if instrument_model == "N9340B":
            trace_data_str = query_safe(inst, ":TRAC2:DATA?", app_instance_ref, app_console_update_func)
        else: # Default/N9342CN
            trace_data_str = query_safe(inst, ":TRACe:DATA? TRACe2", app_instance_ref, app_console_update_func)

        if trace_data_str is None or not trace_data_str.strip():
            app_instance_ref.after(0, lambda: app_console_update_func("🚫 No valid trace data string received for this segment."))
            return []

        match = re.match(r'#\d+\d+(.*)', trace_data_str)
        data_part = match.group(1) if match else trace_data_str

        if data_part:
            amplitudes_dbm = [float(val) for val in data_part.split(',') if val.strip()]
            num_points = len(amplitudes_dbm)
            if num_points > 1:
                frequencies_hz = np.linspace(segment_start_freq_hz, segment_stop_freq_hz, num_points)
                if len(amplitudes_dbm) == len(frequencies_hz):
                    segment_raw_data.extend(zip(frequencies_hz, amplitudes_dbm))
    except Exception as e:
        app_instance_ref.after(0, lambda: app_console_update_func(f"🚨 Error in segment sweep: {e}"))
        return []
    
    return segment_raw_data


def scan_bands(app_instance_ref, inst, selected_bands, rbw_hz, ref_level_dbm, freq_shift_hz, maxhold_enabled, high_sensitivity, preamp_on, rbw_step_size_hz, max_hold_time_seconds, scan_name, output_folder, stop_event, pause_event, log_visa_commands_enabled, general_debug_enabled, app_console_update_func, initialize_instrument_func):
    """Orchestrates a full frequency scan across multiple specified bands."""
    # ... (function content is unchanged)
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function} function. Starting scan_bands.",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    overall_start_freq_hz = min(band["Start MHz"] for band in selected_bands) * MHZ_TO_HZ
    overall_stop_freq_hz = max(band["Stop MHz"] for band in selected_bands) * MHZ_TO_HZ
    
    app_instance_ref.after(0, lambda: app_console_update_func(f"Scanning from {overall_start_freq_hz / MHZ_TO_HZ:.3f} MHz to {overall_stop_freq_hz / MHZ_TO_HZ:.3f} MHz..."))

    if not initialize_instrument_logic(
        inst,
        model_match=app_instance_ref.connected_instrument_model.get(),
        ref_level_dbm=ref_level_dbm,
        high_sensitivity_on=high_sensitivity,
        preamp_on=preamp_on,
        rbw_config_val=rbw_hz,
        vbw_config_val=rbw_hz * VBW_RBW_RATIO,
        app_instance_ref=app_instance_ref,
        console_print_func=app_console_update_func
    ):
        app_instance_ref.after(0, lambda: app_console_update_func("❌ Error: Failed to initialize instrument for scan. Aborting."))
        return -1, None, None

    # (rest of setup commands...)

    timestamp_hm = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename_current_cycle = os.path.join(output_folder, f"{scan_name}_RBW{int(rbw_hz/1000)}K_HOLD{int(max_hold_time_seconds)}_Offset{int(freq_shift_hz)}_{timestamp_hm}.csv")

    raw_scan_data_for_current_sweep = []
    last_successful_band_index = -1
    markers_data_from_scan = []

    app_instance_ref.after(0, lambda: app_console_update_func("\n--- 📡 Starting Band Scan ---"))

    for i, band in enumerate(selected_bands):
        if stop_event.is_set():
            break

        band_name = band["Band Name"]
        band_start_freq_hz = (band["Start MHz"] * MHZ_TO_HZ) + freq_shift_hz
        band_stop_freq_hz = (band["Stop MHz"] * MHZ_TO_HZ) + freq_shift_hz

        app_instance_ref.after(0, lambda: app_console_update_func(f"\n📈 Processing Band: {band_name}"))

        # (segment calculation logic...)
        full_band_span_hz = band_stop_freq_hz - band_start_freq_hz
        total_segments_in_band = 1
        if full_band_span_hz > 0:
            expected_sweep_points = 461 if "N9340B" in app_instance_ref.connected_instrument_model.get() else 501
            total_segments_in_band = int(np.ceil(full_band_span_hz / (rbw_step_size_hz * (expected_sweep_points - 1))))
        
        if total_segments_in_band <= 0: total_segments_in_band = 1
        optimal_segment_span_hz = full_band_span_hz / total_segments_in_band

        current_segment_start_freq_hz = band_start_freq_hz
        segment_counter = 0

        while current_segment_start_freq_hz < band_stop_freq_hz:
            segment_counter += 1
            segment_stop_freq_hz_current = current_segment_start_freq_hz + optimal_segment_span_hz
            if segment_stop_freq_hz_current > band_stop_freq_hz:
                segment_stop_freq_hz_current = band_stop_freq_hz
            
            segment_raw_data = perform_segment_sweep(
                inst,
                current_segment_start_freq_hz,
                segment_stop_freq_hz_current,
                maxhold_enabled,
                max_hold_time_seconds,
                app_instance_ref,
                pause_event,
                stop_event,
                segment_counter,
                total_segments_in_band,
                band_name,
                app_console_update_func,
                current_segment_start_freq_hz
            )

            if stop_event.is_set():
                break

            if segment_raw_data:
                raw_scan_data_for_current_sweep.extend(segment_raw_data)
                
                # Write to CSV
                csv_data_to_write = [(f / MHZ_TO_HZ, amp) for f, amp in segment_raw_data]
                write_scan_data_to_csv(
                    csv_filename_current_cycle,
                    header=None,
                    data=csv_data_to_write,
                    app_instance_ref=app_instance_ref,
                    append_mode=True,
                    console_print_func=app_console_update_func
                )
            
            current_segment_start_freq_hz = segment_stop_freq_hz_current
            last_successful_band_index = i

        if stop_event.is_set():
            break

    app_instance_ref.after(0, lambda: app_console_update_func("\n--- 🎉 Band Scan Data Collection Complete! ---"))
    return last_successful_band_index, raw_scan_data_for_current_sweep, markers_data_from_scan