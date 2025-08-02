# tabs/Start_Pause_Stop/scan_controler_button_logic.py
#
# This file contains the Tkinter Frame for controlling spectrum scans,
# including starting, pausing, and stopping scans.
# It orchestrates the threading for the scan operation to keep the GUI responsive.
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
# Version 20250802.0035.4 (Updated scan_bands() call to match reverted 17-argument signature.)

current_version = "20250802.0035.4" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 35 * 4 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk, filedialog
import threading
import time
import os
from datetime import datetime
import pandas as pd # Keep pandas for DataFrame operations on stitched data
import inspect
import subprocess # For opening folders (kept for now, but likely to be removed if no folder operations remain)
import sys # For platform detection for opening

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Import instrument control functions - CORRECTED PATHS

from tabs.Instrument.instrument_logic import query_current_instrument_settings_logic 

from tabs.Scanning.utils_scan_instrument import scan_bands # Import scan_bands

from process_math.scan_stitch import stitch_and_save_scan_data # Import the stitching logic

from src.settings_and_config.config_manager import save_config # Import save_config

# Import connection status logic
from src.connection_status_logic import update_connection_status_logic


class ScanControlTab(ttk.Frame):
    """
    A Tkinter Frame that provides controls for starting, pausing, and stopping spectrum scans.
    It manages the threading for the scan operation to keep the GUI responsive.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the ScanControlTab.

        Inputs:
            master (tk.Widget): The parent widget.
            app_instance (App): The main application instance, used for accessing
                                 shared state like Tkinter variables and console print function.
            console_print_func (function): Function to print messages to the GUI console.
            **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        """
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log # Use console_log as default

        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing ScanControlTab. Version: {current_version}. Setting up scan controls!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        self.scan_thread = None
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.is_paused_by_user = False # Track if pause was user-initiated

        self._create_widgets()
        self._update_button_states() # Initial state update

        debug_log(f"ScanControlTab initialized. Version: {current_version}. Scan controls ready!",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _create_widgets(self):
        """
        Creates and arranges the buttons for scan control (Start, Pause, Stop).
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating ScanControlTab widgets... Building the scan control buttons! Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1) # Center buttons horizontally

        # Start Scan Button
        self.start_button = ttk.Button(self, text="Start Scan", command=self._start_scan, style='Green.TButton')
        self.start_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Pause/Resume Button
        self.pause_resume_button = ttk.Button(self, text="Pause Scan", command=self._toggle_pause_resume, style='Orange.TButton')
        self.pause_resume_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Stop Scan Button
        self.stop_button = ttk.Button(self, text="Stop Scan", command=self._stop_scan, style='Red.TButton')
        self.stop_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Progress Bar
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Progress Label
        self.progress_label = ttk.Label(self, text="Scan Progress: 0%", style='TLabel')
        self.progress_label.grid(row=4, column=0, padx=10, pady=2, sticky="ew")

        debug_log(f"ScanControlTab widgets created. Buttons are in place! Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _update_button_states(self):
        """
        Updates the state of the scan control buttons based on connection and scan status.
        This function is called by connection_status_logic.py
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating scan button states. Connected: {self.app_instance.inst is not None}, Scanning: {self.scan_thread and self.scan_thread.is_alive()}. Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        is_connected = self.app_instance.inst is not None
        is_scanning = self.scan_thread and self.scan_thread.is_alive()

        # Start button: Enabled if connected and not scanning
        self.start_button.config(state=tk.NORMAL if is_connected and not is_scanning else tk.DISABLED)

        # Pause/Resume button: Enabled if scanning
        self.pause_resume_button.config(state=tk.NORMAL if is_scanning else tk.DISABLED)
        if is_scanning:
            if self.pause_event.is_set(): # If paused
                self.pause_resume_button.config(text="Resume Scan", style='OrangeBlink.TButton')
            else: # If running
                self.pause_resume_button.config(text="Pause Scan", style='Orange.TButton')
        else:
            self.pause_resume_button.config(text="Pause Scan", style='Orange.TButton')


        # Stop button: Enabled if scanning
        self.stop_button.config(state=tk.NORMAL if is_scanning else tk.DISABLED)

        # Progress bar and label visibility
        if is_scanning:
            self.progress_bar.grid()
            self.progress_label.grid()
        else:
            self.progress_bar.grid_remove()
            self.progress_label.grid_remove()
            self.progress_bar["value"] = 0
            self.progress_label.config(text="Scan Progress: 0%")

        debug_log("Scan button states updated. UI responsive!",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _start_scan(self):
        """
        Initiates the spectrum scan in a separate thread to keep the GUI responsive.
        """
        current_function = inspect.currentframe().f_code.co_name
        self.console_print_func("--- Initiating Spectrum Scan ---")
        debug_log(f"Starting scan. Version: {current_version}. Let's get this show on the road!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if self.scan_thread and self.scan_thread.is_alive():
            self.console_print_func("⚠️ Scan already in progress. Please wait or stop the current scan. Patience, you bastard!")
            debug_log("Scan already in progress. Aborting new scan request.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        if not self.app_instance.inst:
            self.console_print_func("❌ Instrument not connected. Cannot start scan. Connect the damn thing first!")
            debug_log("Instrument not connected. Scan aborted.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        # Get selected bands
        selected_bands = [
            band_item for band_item in self.app_instance.band_vars
            if band_item["var"].get()
        ]

        if not selected_bands:
            self.console_print_func("⚠️ No bands selected for scan. Please select at least one band!")
            debug_log("No bands selected. Scan aborted.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            self.console_print_func("--- Scan process finished. Thank the lord! ---") # Indicate scan finished
            return

        # Reset events for a new scan
        self.stop_event.clear()
        self.pause_event.clear()
        self.is_paused_by_user = False

        # Start the scan in a new thread
        self.scan_thread = threading.Thread(
            target=self._scan_thread_target,
            args=(selected_bands,)
        )
        self.scan_thread.daemon = True # Allow the program to exit even if thread is running
        self.scan_thread.start()
        self._update_button_states() # Update UI immediately after starting thread
        update_connection_status_logic(self.app_instance, True, True, self.console_print_func) # Update main app status


    def _toggle_pause_resume(self):
        """
        Toggles the pause/resume state of the scan.
        """
        current_function = inspect.currentframe().f_code.co_name
        if self.scan_thread and self.scan_thread.is_alive():
            if self.pause_event.is_set():
                self.pause_event.clear() # Resume
                self.is_paused_by_user = False
                self.console_print_func("▶️ Scan resumed. Let's get back to it!")
                debug_log("Scan resumed by user.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            else:
                self.pause_event.set() # Pause
                self.is_paused_by_user = True
                self.console_print_func("⏸️ Scan paused. Taking a breather!")
                debug_log("Scan paused by user.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            self._update_button_states() # Update UI immediately


    def _stop_scan(self):
        """
        Stops the currently running scan.
        """
        current_function = inspect.currentframe().f_code.co_name
        if self.scan_thread and self.scan_thread.is_alive():
            self.stop_event.set() # Signal the thread to stop
            self.pause_event.clear() # Clear pause just in case it was paused
            self.is_paused_by_user = False
            self.console_print_func("⏹️ Stopping scan... This might take a moment.")
            debug_log("Stop event set for scan thread.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            # No need to join here, the thread will exit gracefully.
            # The UI will be updated by _scan_thread_target's finally block.
        else:
            self.console_print_func("ℹ️ No active scan to stop. Nothing to do here!")
            debug_log("No active scan to stop.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        self._update_button_states() # Update UI immediately after stopping


    def _scan_thread_target(self, selected_bands):
        """
        The main function executed in the scanning thread.
        Orchestrates the instrument control, data collection, and progress updates.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Scan thread started. Version: {current_version}. Let the data flow!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        
        last_successful_band_index = -1
        raw_scan_data = [] # To accumulate data across all bands and segments
        markers_data = [] # To accumulate marker data

        try:
            # (2025-08-02 12:30) Change: Updated call to scan_bands to match its 17-argument signature.
            last_successful_band_index, raw_scan_data, markers_data = scan_bands(
                app_instance_ref=self.app_instance,
                inst=self.app_instance.inst,
                selected_bands=selected_bands,
                rbw_hz=float(self.app_instance.scan_rbw_hz_var.get()),
                ref_level_dbm=float(self.app_instance.reference_level_dbm_var.get()),
                freq_shift_hz=float(self.app_instance.freq_shift_hz_var.get()),
                maxhold_enabled=bool(self.app_instance.maxhold_time_seconds_var.get()), # Max hold enabled if time > 0
                high_sensitivity=self.app_instance.high_sensitivity_var.get(),
                preamp_on=self.app_instance.preamp_on_var.get(),
                rbw_step_size_hz=float(self.app_instance.rbw_step_size_hz_var.get()), # This is 'Graph Quality'
                max_hold_time_seconds=float(self.app_instance.maxhold_time_seconds_var.get()), # This is 'Dwell / Settle Time'
                scan_name=self.app_instance.scan_name_var.get(),
                output_folder=self.app_instance.output_folder_var.get(),
                stop_event=self.stop_event,
                pause_event=self.pause_event,
                log_visa_commands_enabled=self.app_instance.log_visa_commands_var.get(),
                general_debug_enabled=self.app_instance.general_debug_var.get(),
                app_console_update_func=self.console_print_func
            )

            if not self.stop_event.is_set(): # Only process if not stopped by user
                # Stitch and save data after scan is complete
                self.console_print_func("\n--- Stitching and saving scan data ---")
                debug_log("Stitching and saving scan data. Almost done!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                
                output_folder = self.app_instance.output_folder_var.get()
                scan_name = self.app_instance.scan_name_var.get()
                
                # Retrieve all metadata variables from app_instance
                meta_data = {
                    "Operator Name": self.app_instance.operator_name_var.get(),
                    "Operator Contact": self.app_instance.operator_contact_var.get(),
                    "Venue Name": self.app_instance.venue_name_var.get(),
                    "Venue Postal Code": self.app_instance.venue_postal_code_var.get(),
                    "Address Field": self.app_instance.address_field_var.get(),
                    "City": self.app_instance.city_var.get(),
                    "Province": self.app_instance.province_var.get(),
                    "Scanner Type": self.app_instance.scanner_type_var.get(),
                    "Antenna Type": self.app_instance.selected_antenna_type_var.get(),
                    "Antenna Description": self.app_instance.antenna_description_var.get(),
                    "Antenna Use": self.app_instance.antenna_use_var.get(),
                    "Antenna Mount": self.app_instance.antenna_mount_var.get(),
                    "Antenna Amplifier Type": self.app_instance.selected_amplifier_type_var.get(),
                    "Amplifier Description": self.app_instance.amplifier_description_var.get(),
                    "Amplifier Use": self.app_instance.amplifier_use_var.get(),
                    "Notes": self.app_instance.notes_var.get(),
                    "Scan Cycles": self.app_instance.num_scan_cycles_var.get(),
                    "RBW Step Size (Hz)": self.app_instance.rbw_step_size_hz_var.get(),
                    "Cycle Wait Time (s)": self.app_instance.cycle_wait_time_seconds_var.get(),
                    "Max Hold Time (s)": self.app_instance.maxhold_time_seconds_var.get(),
                    "Scan RBW (Hz)": self.app_instance.scan_rbw_hz_var.get(),
                    "Reference Level (dBm)": self.app_instance.reference_level_dbm_var.get(),
                    "Frequency Shift (Hz)": self.app_instance.freq_shift_hz_var.get(),
                    "High Sensitivity": self.app_instance.high_sensitivity_var.get(),
                    "Preamplifier ON": self.app_instance.preamp_on_var.get(),
                    "Scan RBW Segmentation (Hz)": self.app_instance.scan_rbw_segmentation_var.get(),
                    "Desired Default Focus Width (Hz)": self.app_instance.desired_default_focus_width_var.get(),
                }

                # Pass all relevant flags for marker inclusion
                marker_flags = {
                    "include_gov_markers": self.app_instance.include_gov_markers_var.get(),
                    "include_tv_markers": self.app_instance.include_tv_markers_var.get(),
                    "include_markers": self.app_instance.include_markers_var.get(),
                    "include_scan_intermod_markers": self.app_instance.include_scan_intermod_markers_var.get(),
                    "avg_include_gov_markers": self.app_instance.avg_include_gov_markers_var.get(),
                    "avg_include_tv_markers": self.app_instance.avg_include_tv_markers_var.get(),
                    "avg_include_markers": self.app_instance.avg_include_markers_var.get(),
                    "avg_include_intermod_markers": self.app_instance.avg_include_intermod_markers_var.get(),
                }

                # Pass all relevant math flags
                math_flags = {
                    "math_average": self.app_instance.math_average_var.get(),
                    "math_median": self.app_instance.math_median_var.get(),
                    "math_range": self.app_instance.math_range_var.get(),
                    "math_standard_deviation": self.app_instance.math_standard_deviation_var.get(),
                    "math_variance": self.app_instance.math_variance_var.get(),
                    "math_psd": self.app_instance.math_psd_var.get(),
                }

                stitch_and_save_scan_data(
                    raw_scan_data,
                    markers_data,
                    output_folder,
                    scan_name,
                    meta_data,
                    marker_flags,
                    math_flags,
                    self.console_print_func,
                    self.app_instance.create_html_var.get(), # Pass create_html_var
                    self.app_instance.open_html_after_complete_var.get() # Pass open_html_after_complete_var
                )
                self.console_print_func("--- Scan process finished. Thank the lord! ---")
                debug_log("Scan process finished successfully.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            else:
                self.console_print_func("--- Scan process stopped by user. Thank the lord! ---")
                debug_log("Scan process stopped by user.",
                            file=__file__,
                            version=current_version,
                            function=current_function)

        except Exception as e:
            self.console_print_func(f"❌ An error occurred during scan: {e}. This is some serious **bullshit**!")
            debug_log(f"Error during scan thread: {e}. Fucking hell!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            self.app_instance.after(0, lambda: self.console_print_func("--- Scan process finished. Thank the lord! ---"))
        finally:
            self.app_instance.after(0, self._update_button_states) # Update UI on main thread
            self.app_instance.after(0, lambda: update_connection_status_logic(self.app_instance, self.app_instance.inst is not None, False, self.console_print_func)) # Update main app status


    def _update_progress(self, value):
        """
        Updates the progress bar and label on the GUI.
        This method is called from the scanning thread, so it uses after() to update the GUI.
        """
        # Ensure GUI updates are done on the main thread
        self.app_instance.after(0, lambda: self.progress_bar.config(value=value))
        self.app_instance.after(0, lambda: self.progress_label.config(text=f"Scan Progress: {value:.1f}%"))

    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Ensures button states are refreshed.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Scan Control Tab selected. Refreshing button states! Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        self._update_button_states()
        # Also ensure the main app's connection status logic is run to update other tabs
        is_connected = self.app_instance.inst is not None
        is_scanning = self.scan_thread and self.scan_thread.is_alive()
        update_connection_status_logic(self.app_instance, is_connected, is_scanning, self.console_print_func)
