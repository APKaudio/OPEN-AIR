# tabs/Start_Pause_Stop/scan_control_logic.py
#
# This file contains the core logic for controlling spectrum scans,
# including starting, pausing, stopping, and executing the scan process.
# It abstracts the instrument communication and data processing from the GUI.
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
# Version 20250811.221000.1 (FIXED: Removed the defunct import of 'initialize_instrument_logic' to resolve ModuleNotFoundError and streamline scan initiation.)

current_version = "20250811.221000.1"
current_version_hash = 20250811 * 221000 * 1

import threading
import time
import os
from datetime import datetime
import pandas as pd
import inspect

from display.debug_logic import debug_log
from display.console_logic import console_log
# The main scan_bands function
from tabs.Scanning.utils_scan_instrument import scan_bands
from process_math.scan_stitch import stitch_and_save_scan_data
from src.connection_status_logic import update_connection_status_logic

# REMOVED: Import initialize_instrument_logic here, as it's no longer used.

def start_scan_logic(app_instance, console_print_func, stop_event, pause_event, update_progress_func):
    """Initiates the spectrum scan in a separate thread."""
    if app_instance.scan_thread and app_instance.scan_thread.is_alive():
        console_print_func("⚠️ Scan already in progress.")
        return False

    if not app_instance.is_connected.get():
        console_print_func("❌ Instrument not connected. Cannot start scan.")
        return False

    selected_bands = [band_item["band"] for band_item in app_instance.band_vars if band_item["var"].get()]

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
    return True

def toggle_pause_resume_logic(app_instance, console_print_func, pause_event):
    """Toggles the pause/resume state of the scan."""
    if app_instance.scan_thread and app_instance.scan_thread.is_alive():
        if pause_event.is_set():
            pause_event.clear()
            app_instance.is_paused_by_user = False
            console_print_func("▶️ Scan resumed.")
        else:
            pause_event.set()
            app_instance.is_paused_by_user = True
            console_print_func("⏸️ Scan paused.")

def stop_scan_logic(app_instance, console_print_func, stop_event, pause_event):
    """Stops the currently running scan."""
    if app_instance.scan_thread and app_instance.scan_thread.is_alive():
        stop_event.set()
        pause_event.clear()
        app_instance.is_paused_by_user = False
        console_print_func("⏹️ Stopping scan...")

def _scan_thread_target(app_instance, selected_bands, stop_event, pause_event, console_print_func, update_progress_func):
    """The main function executed in the scanning thread."""
    console_print_func("--- Initiating Spectrum Scan ---")
    try:
        raw_scan_data, markers_data = scan_bands(
            app_instance_ref=app_instance,
            inst=app_instance.inst,
            selected_bands=selected_bands,
            rbw_hz=float(app_instance.scan_rbw_hz_var.get()),
            ref_level_dbm=float(app_instance.reference_level_dbm_var.get()),
            freq_shift_hz=float(app_instance.freq_shift_var.get()),
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
            # Removed the call to initialize_instrument_func
        )

        if not stop_event.is_set():
            console_print_func("\n--- Stitching and saving scan data ---")
            # This is a placeholder for where you would call stitching and saving logic
            # stitch_and_save_scan_data(...)
            console_print_func("--- Scan process finished. ---")
        else:
            console_print_func("--- Scan process stopped by user. ---")

    except Exception as e:
        console_print_func(f"❌ An error occurred during scan: {e}")
        debug_log(f"Error in scan thread target: {e}",
                    file=os.path.basename(__file__), function="_scan_thread_target")
    finally:
        app_instance.after(0, lambda: app_instance.scan_control_tab._update_button_states())
        app_instance.after(0, lambda: update_connection_status_logic(app_instance, app_instance.is_connected.get(), False, console_print_func))