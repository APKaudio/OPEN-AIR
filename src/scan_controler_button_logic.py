# src/scan_controler_button_logic.py
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
# Version 20250802.0035.1 (Refactored debug_print to debug_log; updated imports and flair.)

current_version = "20250802.0035.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 35 * 1 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk, filedialog
import threading
import time
import os
from datetime import datetime
import pandas as pd # Keep pandas for DataFrame operations on stitched data
import inspect
import subprocess # For opening folders (kept for now, but likely to be removed if no folder operations remain)
import sys # For platform detection for opening folders (kept for now)

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Import scan utility functions - CORRECTED PATH
from utils.utils_scan_instrument import scan_bands
from process_math.scan_stitch import stitch_and_save_scan_data

class ScanControlTab(ttk.Frame):
    """
    Function Description:
    A Tkinter Frame that provides controls for starting, pausing, and stopping spectrum scans.
    It manages the scan process in a separate thread to keep the GUI responsive.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the ScanControlTab.

        Inputs:
            master (tk.Widget): The parent widget.
            app_instance (App): The main application instance, used for accessing
                                 shared state and methods.
            console_print_func (function, optional): Function to print messages to the GUI console.
                                                     Defaults to console_log if None.
            **kwargs: Arbitrary keyword arguments for Tkinter Frame.

        Process of this function:
            1. Calls the superclass constructor.
            2. Stores app_instance and console_print_func.
            3. Initializes scan state variables (is_scanning, is_paused, stop_event, pause_event).
            4. Creates and places GUI elements:
               - Scan control buttons (Start, Pause/Resume, Stop).
               - A progress bar.
               - A label to display current scan status.
            5. Configures button styles.

        Outputs of this function:
            None. Initializes the scan control tab frame and its components.

        (2025-07-30) Change: Initial implementation of ScanControlTab.
        (2025-07-31) Change: Added progress bar and status label.
        (2025-08-01 5) Change: Renamed buttons to START, PAUSE/RESUME, STOP.
                               Ensured all scan control buttons consistently use 'BigScanButton'
                               styles for larger appearance. Adjusted _toggle_pause_resume
                               to correctly set 'PAUSE' and 'RESUME' text.
        (2025-08-02 0035.1) Change: Refactored debug_print to debug_log; updated imports and flair.
        """
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
        
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing ScanControlTab. Setting up scan controls! Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        self.is_scanning = False
        self.is_paused = False
        self.scan_thread = None
        self.stop_event = threading.Event()
        self.pause_event = threading.Event() # Event to signal pausing

        # Configure grid for this frame
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=0) # Buttons row
        self.grid_rowconfigure(1, weight=1) # Status/Progress row

        # --- Scan Control Buttons ---
        button_frame = ttk.Frame(self)
        button_frame.grid(row=0, column=0, columnspan=3, pady=10)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)

        self.start_button = ttk.Button(button_frame, text="START SCAN", command=self._start_scan, style='BigScanButton')
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.pause_resume_button = ttk.Button(button_frame, text="PAUSE", command=self._toggle_pause_resume, style='BigScanButton', state=tk.DISABLED)
        self.pause_resume_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.stop_button = ttk.Button(button_frame, text="STOP", command=self._stop_scan, style='BigScanButton', state=tk.DISABLED)
        self.stop_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # --- Progress Bar and Status Label ---
        status_frame = ttk.Frame(self)
        status_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        status_frame.grid_rowconfigure(0, weight=1)
        status_frame.grid_rowconfigure(1, weight=1)
        status_frame.grid_columnconfigure(0, weight=1)

        self.progress_label_var = tk.StringVar(value="Ready to scan.")
        self.progress_label = ttk.Label(status_frame, textvariable=self.progress_label_var, font=('Helvetica', 10, 'bold'))
        self.progress_label.grid(row=0, column=0, pady=5, sticky="w")

        self.progress_bar = ttk.Progressbar(status_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=5)

        # Initialize button states based on initial connection status
        self._update_button_states()

        debug_log(f"ScanControlTab initialized. Buttons are ready! Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _update_button_states(self):
        """
        Function Description:
        Updates the state (enabled/disabled) of the scan control buttons
        based on the current scan status and instrument connection.

        Inputs:
        - None.

        Process of this function:
        1. Checks `self.is_scanning` and `self.is_paused`.
        2. Checks if an instrument is connected via `self.app_instance.inst`.
        3. Sets the state of `start_button`, `pause_resume_button`, and `stop_button` accordingly.

        Outputs of this function:
        - None. Modifies Tkinter widget states.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating scan button states. Scanning: {self.is_scanning}, Paused: {self.is_paused}, Connected: {self.app_instance.inst is not None}. Adjusting controls!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        is_connected = self.app_instance.inst is not None

        if self.is_scanning:
            self.start_button.config(state=tk.DISABLED)
            self.pause_resume_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
            if self.is_paused:
                self.pause_resume_button.config(text="RESUME")
                self.progress_label_var.set("Scan paused.")
            else:
                self.pause_resume_button.config(text="PAUSE")
                # Progress label updated by scan_update_progress during active scan
        else:
            self.start_button.config(state=tk.NORMAL if is_connected else tk.DISABLED)
            self.pause_resume_button.config(state=tk.DISABLED, text="PAUSE") # Reset text
            self.stop_button.config(state=tk.DISABLED)
            self.progress_bar['value'] = 0
            if not is_connected:
                self.progress_label_var.set("Instrument not connected. Please connect to start scan.")
            elif not self.is_paused: # Only reset label if not paused and finished
                self.progress_label_var.set("Ready to scan.")

        debug_log("Scan button states updated. Controls are responsive!",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _start_scan(self):
        """
        Function Description:
        Initiates the scan process in a separate thread.

        Inputs:
        - None.

        Process of this function:
        1. Prints a debug message.
        2. Checks if an instrument is connected.
        3. If already scanning, logs a warning and returns.
        4. Resets stop and pause events.
        5. Sets `is_scanning` to True.
        6. Creates and starts a new `threading.Thread` that runs `self._scan_thread_target`.
        7. Updates button states.

        Outputs of this function:
        - None. Starts a new thread for scanning.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Attempting to start scan. Kicking off the process!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if not self.app_instance.inst:
            self.console_print_func("❌ Cannot start scan: No instrument connected. Connect the damn thing first!")
            debug_log("Scan start failed: No instrument connected. Fucking useless!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        if self.is_scanning:
            self.console_print_func("⚠️ Scan already in progress. Please wait or stop the current scan.")
            debug_log("Scan already in progress. Aborting start request.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        # Reset events for a new scan
        self.stop_event.clear()
        self.pause_event.clear()
        self.is_scanning = True
        self.is_paused = False
        self._update_button_states()
        self.progress_label_var.set("Scan started...")
        self.progress_bar['value'] = 0
        self.console_print_func("--- Initiating Spectrum Scan ---")

        # Start the scan in a separate thread to keep GUI responsive
        self.scan_thread = threading.Thread(target=self._scan_thread_target, daemon=True)
        self.scan_thread.start()
        debug_log("Scan thread started. The data acquisition has begun!",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _toggle_pause_resume(self):
        """
        Function Description:
        Toggles the pause/resume state of the scan.

        Inputs:
        - None.

        Process of this function:
        1. Prints a debug message.
        2. Toggles `self.is_paused`.
        3. If resuming, clears the `pause_event`.
        4. If pausing, sets the `pause_event`.
        5. Updates button states and status label.

        Outputs of this function:
        - None. Modifies scan state and GUI.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Toggling pause/resume for scan. Controlling the flow!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if self.is_scanning:
            self.is_paused = not self.is_paused
            if self.is_paused:
                self.pause_event.set() # Signal the scan thread to pause
                self.console_print_func("⏸️ Scan paused.")
                debug_log("Scan paused. Taking a breather!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            else:
                self.pause_event.clear() # Signal the scan thread to resume
                self.console_print_func("▶️ Scan resumed.")
                debug_log("Scan resumed. Back to work!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            self._update_button_states()
        else:
            self.console_print_func("⚠️ No scan in progress to pause/resume. What are you trying to do?!")
            debug_log("No scan in progress to pause/resume. Invalid action.",
                        file=__file__,
                        version=current_version,
                        function=current_function)


    def _stop_scan(self):
        """
        Function Description:
        Stops the ongoing scan process.

        Inputs:
        - None.

        Process of this function:
        1. Prints a debug message.
        2. Sets the `stop_event` to signal the scan thread to terminate.
        3. Clears the `pause_event` to ensure thread can exit pause state.
        4. Joins the scan thread to wait for its completion (with a timeout).
        5. Resets scan state variables.
        6. Updates button states and status label.

        Outputs of this function:
        - None. Terminates the scan thread.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Attempting to stop scan. Bringing it to a halt!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if self.is_scanning:
            self.console_print_func("🛑 Stopping scan. Please wait...")
            self.stop_event.set() # Signal the scan thread to stop
            self.pause_event.clear() # Ensure it's not stuck in pause if stopping from paused state

            if self.scan_thread and self.scan_thread.is_alive():
                # Give the thread a moment to respond to the stop event
                self.scan_thread.join(timeout=5) # Wait for thread to finish, with a timeout
                if self.scan_thread.is_alive():
                    self.console_print_func("❌ Scan thread did not terminate gracefully. Forcing stop. This is problematic!")
                    debug_log("Scan thread did not terminate gracefully. Forcing stop.",
                                file=__file__,
                                version=current_version,
                                function=current_function)
            
            self.is_scanning = False
            self.is_paused = False
            self._update_button_states()
            self.progress_label_var.set("Scan stopped by user.")
            self.console_print_func("--- Scan stopped ---")
            debug_log("Scan stopped by user. Mission aborted!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            self.console_print_func("ℹ️ No scan in progress to stop. Nothing to do here!")
            debug_log("No scan in progress to stop. Invalid action.",
                        file=__file__,
                        version=current_version,
                        function=current_function)


    def scan_update_progress(self, progress_percent):
        """
        Function Description:
        Updates the GUI's progress bar and label with the current scan progress.
        This method is called from the scan thread and uses `app_instance.after`
        to safely update Tkinter widgets from a non-GUI thread.

        Inputs:
        - progress_percent (float): The current scan progress as a percentage (0-100).

        Process of this function:
        1. Uses `app_instance.after` to schedule a function on the main Tkinter thread.
        2. The scheduled function updates the `progress_bar` value and `progress_label_var`.

        Outputs of this function:
        - None. Updates GUI elements.
        """
        current_function = inspect.currentframe().f_code.co_name
        # This function is called frequently, so keep debug_log minimal or conditional
        # debug_log(f"Updating progress to {progress_percent:.2f}%.", file=__file__, function=current_function)
        
        self.app_instance.after(0, lambda: self.progress_bar.config(value=progress_percent))
        self.app_instance.after(0, lambda: self.progress_label_var.set(f"Scanning... {progress_percent:.1f}% complete."))


    def _scan_thread_target(self):
        """
        Function Description:
        The target function for the scan thread. This is where the actual instrument
        scanning logic is executed. It calls `scan_bands` and handles data processing
        and saving after the scan is complete or interrupted.

        Inputs:
        - None.

        Process of this function:
        1. Prints debug messages.
        2. Retrieves selected bands and scan parameters from `app_instance`.
        3. Calls `scan_bands` to perform the instrument sweep, passing `stop_event`
           and `pause_event` for control.
        4. Handles exceptions during the scan.
        5. If the scan completes successfully:
           a. Stitches and saves the collected raw data.
           b. Updates the GUI about completion.
           c. Opens the output folder.
        6. Ensures button states are updated in the `finally` block.

        Outputs of this function:
        - None. Executes scan, processes data, and updates GUI.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Scan thread target initiated. Starting the heavy lifting!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        try:
            selected_bands = [
                band_item for band_item in self.app_instance.band_vars if band_item["var"].get()
            ]
            
            if not selected_bands:
                self.app_instance.after(0, lambda: self.console_print_func("⚠️ No bands selected for scan. Please select at least one band!"))
                debug_log("No bands selected for scan. Aborting thread.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                return

            self.app_instance.after(0, lambda: self.progress_label_var.set("Configuring instrument..."))
            debug_log("Calling scan_bands function...",
                        file=__file__,
                        version=current_version,
                        function=current_function)

            # Pass app_instance.inst directly to scan_bands
            last_successful_band_index, raw_scan_data_for_current_sweep, markers_data = scan_bands(
                self.app_instance, # Pass the full app_instance
                selected_bands,
                self.scan_update_progress,
                self.stop_event,
                self.pause_event, # Pass pause_event
                self.console_print_func
            )
            debug_log("scan_bands function returned.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

            if self.stop_event.is_set():
                self.app_instance.after(0, lambda: self.console_print_func("Scan process stopped by user. Data might be incomplete."))
                debug_log("Scan thread detected stop event. Exiting gracefully.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                return

            if raw_scan_data_for_current_sweep:
                self.app_instance.after(0, lambda: self.progress_label_var.set("Stitching and saving data..."))
                self.app_instance.after(0, lambda: self.console_print_func("--- Stitching and Saving Scan Data ---"))
                debug_log(f"Stitching and saving {len(raw_scan_data_for_current_sweep)} raw scan segments.",
                            file=__file__,
                            version=current_version,
                            function=current_function)

                # Call the new stitch and save function
                stitched_df, output_file_path = stitch_and_save_scan_data(
                    raw_scan_data_for_current_sweep,
                    self.app_instance.output_folder_var.get(),
                    self.app_instance.scan_name_var.get(),
                    self.app_instance.operator_name_var.get(),
                    self.app_instance.venue_name_var.get(),
                    self.app_instance.equipment_used_var.get(),
                    self.app_instance.notes_var.get(),
                    self.app_instance.postal_code_var.get(),
                    self.app_instance.latitude_var.get(),
                    self.app_instance.longitude_var.get(),
                    self.app_instance.antenna_type_var.get(),
                    self.app_instance.antenna_amplifier_var.get(),
                    self.console_print_func
                )

                if stitched_df is not None:
                    self.app_instance.collected_scans_dataframes.append(stitched_df) # Store for plotting
                    self.app_instance.after(0, lambda: self.console_print_func(f"✅ Scan data saved to: {output_file_path}. All done!"))
                    debug_log(f"Stitched and saved scan data to: {output_file_path}.",
                                file=__file__,
                                version=current_version,
                                function=current_function)
                    
                    # Open the output folder
                    if os.path.exists(self.app_instance.output_folder_var.get()):
                        try:
                            if sys.platform == "win32":
                                os.startfile(self.app_instance.output_folder_var.get())
                            elif sys.platform == "darwin":
                                subprocess.Popen(["open", self.app_instance.output_folder_var.get()])
                            else:
                                subprocess.Popen(["xdg-open", self.app_instance.output_folder_var.get()])
                            self.app_instance.after(0, lambda: self.console_print_func(f"📂 Opened output folder: {self.app_instance.output_folder_var.get()}"))
                            debug_log(f"Opened output folder: {self.app_instance.output_folder_var.get()}.",
                                        file=__file__,
                                        version=current_version,
                                        function=current_function)
                        except Exception as e:
                            self.app_instance.after(0, lambda: self.console_print_func(f"❌ Error opening output folder: {e}. You'll have to find it yourself!"))
                            debug_log(f"Error opening output folder: {e}.",
                                        file=__file__,
                                        version=current_version,
                                        function=current_function)
                else:
                    self.app_instance.after(0, lambda: self.console_print_func("❌ Failed to stitch or save scan data. This is a disaster!"))
                    debug_log("Failed to stitch or save scan data.",
                                file=__file__,
                                version=current_version,
                                function=current_function)
            else:
                self.app_instance.after(0, lambda: self.console_print_func("⚠️ No scan data collected. Was the instrument connected and configured?"))
                debug_log("No raw scan data collected. Nothing to stitch.",
                            file=__file__,
                            version=current_version,
                            function=current_function)

            self.app_instance.after(0, lambda: self.progress_label_var.set("Scan complete!"))
            self.app_instance.after(0, lambda: self.console_print_func("--- 🎉 Scan Process Finished! ---"))
            debug_log("Scan process finished successfully.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        except AttributeError as e:
            # Catch specific Tkinter-related errors if a variable isn't found
            self.is_scanning = False
            self.is_paused = False
            self.app_instance.after(0, lambda: self.console_print_func(f"❌ An AttributeError occurred during scan: {e}. This might indicate a missing Tkinter variable or incorrect object reference. This is a **fucking nightmare**!"))
            debug_log(f"AttributeError during scan: {e}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            self.app_instance.after(0, self.app_instance.update_connection_status, self.app_instance.inst is not None)
        except Exception as e:
            self.is_scanning = False
            self.is_paused = False
            self.app_instance.after(0, lambda: self.console_print_func(f"❌ An error occurred during scan: {e}. This is some serious **bullshit**!"))
            debug_log(f"Error during scan: {e}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            self.app_instance.after(0, self.app_instance.update_connection_status, self.app_instance.inst is not None)
        finally:
            self.is_scanning = False
            self.is_paused = False
            self.app_instance.after(0, lambda: self.console_print_func("--- Scan process finished. Thank the lord! ---"))
            debug_log("Scan process finished in finally block. Cleanup complete!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            self.app_instance.after(0, self._update_button_states) # Ensure buttons are reset
            self.app_instance.after(0, self.app_instance.update_connection_status, self.app_instance.inst is not None) # Update main app status
            self.app_instance.after(0, self.app_instance.main_notebook.nametowidget(self.app_instance.main_notebook.select())._on_tab_selected, None) # Refresh current tab
