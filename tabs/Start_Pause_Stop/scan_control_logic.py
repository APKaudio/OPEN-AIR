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
# Version 20250802.1701.16 (Initial creation of scan control logic module.)

current_version = "20250802.1701.16" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 1701 * 16 # Example hash, adjust as needed

import threading
import time
import os
from datetime import datetime
import pandas as pd
import inspect

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Import instrument control functions
from tabs.Instrument.instrument_logic import query_current_settings_logic # Corrected import name

from tabs.Scanning.utils_scan_instrument import scan_bands # Import scan_bands

from process_math.scan_stitch import stitch_and_save_scan_data # Import the stitching logic

from src.settings_and_config.config_manager import save_config # Import save_config

# Import connection status logic
from src.connection_status_logic import update_connection_status_logic


def start_scan_logic(app_instance, console_print_func, stop_event, pause_event, update_progress_func):
    """
    Initiates the spectrum scan in a separate thread. This is the logic entry point.

    Inputs:
        app_instance (App): The main application instance.
        console_print_func (function): Function to print messages to the GUI console.
        stop_event (threading.Event): Event to signal scan stop.
        pause_event (threading.Event): Event to signal scan pause/resume.
        update_progress_func (function): Callback function to update the GUI progress bar.
    """
    current_function = inspect.currentframe().f_code.co_name
    console_print_func("--- Initiating Spectrum Scan ---")
    debug_log(f"Starting scan logic. Version: {current_version}. Let's get this show on the road!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    if app_instance.scan_thread and app_instance.scan_thread.is_alive():
        console_print_func("⚠️ Scan already in progress. Please wait or stop the current scan. Patience, you bastard!")
        debug_log("Scan already in progress. Aborting new scan request.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False

    if not app_instance.inst:
        console_print_func("❌ Instrument not connected. Cannot start scan. Connect the damn thing first!")
        debug_log("Instrument not connected. Scan aborted.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False

    # Get selected bands
    selected_bands = [
        band_item for band_item in app_instance.band_vars
        if band_item["var"].get()
    ]

    if not selected_bands:
        console_print_func("⚠️ No bands selected for scan. Please select at least one band!")
        debug_log("No bands selected. Scan aborted.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        console_print_func("--- Scan process finished. Thank the lord! ---") # Indicate scan finished
        return False

    # Reset events for a new scan
    stop_event.clear()
    pause_event.clear()
    app_instance.is_paused_by_user = False # Reset pause state

    # Start the scan in a new thread
    app_instance.scan_thread = threading.Thread(
        target=_scan_thread_target,
        args=(app_instance, selected_bands, stop_event, pause_event, console_print_func, update_progress_func)
    )
    app_instance.scan_thread.daemon = True # Allow the program to exit even if thread is running
    app_instance.scan_thread.start()
    return True


def toggle_pause_resume_logic(app_instance, console_print_func, pause_event):
    """
    Toggles the pause/resume state of the scan.

    Inputs:
        app_instance (App): The main application instance.
        console_print_func (function): Function to print messages to the GUI console.
        pause_event (threading.Event): Event to signal scan pause/resume.
    """
    current_function = inspect.currentframe().f_code.co_name
    if app_instance.scan_thread and app_instance.scan_thread.is_alive():
        if pause_event.is_set():
            pause_event.clear() # Resume
            app_instance.is_paused_by_user = False
            console_print_func("▶️ Scan resumed. Let's get back to it!")
            debug_log("Scan resumed by user.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        else:
            pause_event.set() # Pause
            app_instance.is_paused_by_user = True
            console_print_func("⏸️ Scan paused. Taking a breather!")
            debug_log("Scan paused by user.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
    else:
        console_print_func("ℹ️ No active scan to pause/resume. Nothing to do here!")
        debug_log("No active scan to pause/resume.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


def stop_scan_logic(app_instance, console_print_func, stop_event, pause_event):
    """
    Stops the currently running scan.

    Inputs:
        app_instance (App): The main application instance.
        console_print_func (function): Function to print messages to the GUI console.
        stop_event (threading.Event): Event to signal scan stop.
        pause_event (threading.Event): Event to signal scan pause.
    """
    current_function = inspect.currentframe().f_code.co_name
    if app_instance.scan_thread and app_instance.scan_thread.is_alive():
        stop_event.set() # Signal the thread to stop
        pause_event.clear() # Clear pause just in case it was paused
        app_instance.is_paused_by_user = False
        console_print_func("⏹️ Stopping scan... This might take a moment.")
        debug_log("Stop event set for scan thread.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        console_print_func("ℹ️ No active scan to stop. Nothing to do here!")
        debug_log("No active scan to stop.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


def _scan_thread_target(app_instance, selected_bands, stop_event, pause_event, console_print_func, update_progress_func):
    """
    The main function executed in the scanning thread.
    Orchestrates the instrument control, data collection, and progress updates.

    Inputs:
        app_instance (App): The main application instance.
        selected_bands (list): List of dictionaries, each containing band details and its Tkinter BooleanVar.
        stop_event (threading.Event): Event to signal scan stop.
        pause_event (threading.Event): Event to signal scan pause.
        console_print_func (function): Function to print messages to the GUI console.
        update_progress_func (function): Callback function to update the GUI progress bar.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Scan thread started. Version: {current_version}. Let the data flow!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    last_successful_band_index = -1
    raw_scan_data = [] # To accumulate data across all bands and segments
    markers_data = [] # To accumulate marker data

    try:
        # (2025-08-02 12:30) Change: Updated call to scan_bands to match its 17-argument signature.
        last_successful_band_index, raw_scan_data, markers_data = scan_bands(
            app_instance_ref=app_instance,
            inst=app_instance.inst,
            selected_bands=selected_bands,
            rbw_hz=float(app_instance.scan_rbw_hz_var.get()),
            ref_level_dbm=float(app_instance.reference_level_dbm_var.get()),
            freq_shift_hz=float(app_instance.freq_shift_var.get()), # Corrected to freq_shift_var
            maxhold_enabled=bool(app_instance.maxhold_enabled_var.get()), # Corrected to maxhold_enabled_var
            high_sensitivity=app_instance.high_sensitivity_var.get(),
            preamp_on=app_instance.preamp_on_var.get(),
            rbw_step_size_hz=float(app_instance.rbw_step_size_hz_var.get()),
            max_hold_time_seconds=float(app_instance.maxhold_time_seconds_var.get()),
            scan_name=app_instance.scan_name_var.get(),
            output_folder=app_instance.output_folder_var.get(),
            stop_event=stop_event,
            pause_event=pause_event,
            log_visa_commands_enabled=app_instance.log_visa_commands_enabled_var.get(), # Corrected to log_visa_commands_enabled_var
            general_debug_enabled=app_instance.general_debug_enabled_var.get(), # Corrected to general_debug_enabled_var
            app_console_update_func=console_print_func,
            update_progress_func=update_progress_func # Pass the progress update callback
        )

        if not stop_event.is_set(): # Only process if not stopped by user
            # Stitch and save data after scan is complete
            console_print_func("\n--- Stitching and saving scan data ---")
            debug_log("Stitching and saving scan data. Almost done!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

            output_folder = app_instance.output_folder_var.get()
            scan_name = app_instance.scan_name_var.get()

            # Retrieve all metadata variables from app_instance
            meta_data = {
                "Operator Name": app_instance.operator_name_var.get(),
                "Operator Contact": app_instance.operator_contact_var.get(),
                "Venue Name": app_instance.venue_name_var.get(),
                "Venue Postal Code": app_instance.venue_postal_code_var.get(),
                "Address Field": app_instance.address_field_var.get(),
                "City": app_instance.city_var.get(),
                "Province": app_instance.province_var.get(),
                "Scanner Type": app_instance.scanner_type_var.get(),
                "Antenna Type": app_instance.selected_antenna_type_var.get(),
                "Antenna Description": app_instance.antenna_description_var.get(),
                "Antenna Use": app_instance.antenna_use_var.get(),
                "Antenna Mount": app_instance.antenna_mount_var.get(),
                "Antenna Amplifier Type": app_instance.selected_amplifier_type_var.get(),
                "Amplifier Description": app_instance.amplifier_description_var.get(),
                "Amplifier Use": app_instance.amplifier_use_var.get(),
                "Notes": app_instance.notes_var.get(),
                "Scan Cycles": app_instance.num_scan_cycles_var.get(),
                "RBW Step Size (Hz)": app_instance.rbw_step_size_hz_var.get(),
                "Cycle Wait Time (s)": app_instance.cycle_wait_time_seconds_var.get(),
                "Max Hold Time (s)": app_instance.maxhold_time_seconds_var.get(),
                "Scan RBW (Hz)": app_instance.scan_rbw_hz_var.get(),
                "Reference Level (dBm)": app_instance.reference_level_dbm_var.get(),
                "Frequency Shift (Hz)": app_instance.freq_shift_var.get(),
                "High Sensitivity": app_instance.high_sensitivity_var.get(),
                "Preamplifier ON": app_instance.preamp_on_var.get(),
                "Scan RBW Segmentation (Hz)": app_instance.scan_rbw_segmentation_var.get(),
                "Desired Default Focus Width (Hz)": app_instance.desired_default_focus_width_var.get(),
            }

            # Pass all relevant flags for marker inclusion
            marker_flags = {
                "include_gov_markers": app_instance.include_gov_markers_var.get(),
                "include_tv_markers": app_instance.include_tv_markers_var.get(),
                "include_markers": app_instance.include_markers_var.get(),
                "include_scan_intermod_markers": app_instance.include_scan_intermod_markers_var.get(),
                "avg_include_gov_markers": app_instance.avg_include_gov_markers_var.get(),
                "avg_include_tv_markers": app_instance.avg_include_tv_markers_var.get(),
                "avg_include_markers": app_instance.avg_include_markers_var.get(),
                "avg_include_intermod_markers": app_instance.avg_include_intermod_markers_var.get(),
            }

            # Pass all relevant math flags
            math_flags = {
                "math_average": app_instance.math_average_var.get(),
                "math_median": app_instance.math_median_var.get(),
                "math_range": app_instance.math_range_var.get(),
                "math_standard_deviation": app_instance.math_standard_deviation_var.get(),
                "math_variance": app_instance.math_variance_var.get(),
                "math_psd": app_instance.math_psd_var.get(),
            }

            stitch_and_save_scan_data(
                raw_scan_data,
                markers_data,
                output_folder,
                scan_name,
                meta_data,
                marker_flags,
                math_flags,
                console_print_func,
                app_instance.create_html_var.get(),
                app_instance.open_html_after_complete_var.get()
            )
            console_print_func("--- Scan process finished. Thank the lord! ---")
            debug_log("Scan process finished successfully.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        else:
            console_print_func("--- Scan process stopped by user. Thank the lord! ---")
            debug_log("Scan process stopped by user.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

    except Exception as e:
        console_print_func(f"❌ An error occurred during scan: {e}. This is some serious **bullshit**!")
        debug_log(f"Error during scan thread: {e}. Fucking hell!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        app_instance.after(0, lambda: console_print_func("--- Scan process finished. Thank the lord! ---"))
    finally:
        # These updates must be scheduled on the main Tkinter thread
        app_instance.after(0, lambda: app_instance.scan_control_tab._update_button_states()) # Call the display's update method
        app_instance.after(0, lambda: update_connection_status_logic(app_instance, app_instance.inst is not None, False, console_print_func))

