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
#
#
# Version 20250801.5 (Renamed buttons to START, PAUSE/RESUME, STOP.
#                     Ensured all scan control buttons consistently use 'BigScanButton'
#                     styles for larger appearance. Adjusted _toggle_pause_resume
#                     to correctly set 'PAUSE' and 'RESUME' text.)

current_version = "20250801.5" # this variable should always be defined below the header to make the debuggin better

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

# Import scan-related logic
from tabs.Scanning.utils_scan_instrument import scan_bands # Simplified scan_bands
from process_math.scan_stitch import process_and_stitch_scan_data # New import for data stitching
from ref.frequency_bands import MHZ_TO_HZ
from utils.utils_instrument_control import debug_print


# Import plotly express for colors in multi-trace plots (kept for now, might go)
import plotly.express as px


class ScanControlTab(ttk.Frame):
    """
    A Tkinter Frame that provides controls for starting, pausing, and stopping spectrum scans.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        # This function descriotion tells me what this function does
        # Initializes the ScanControlTab, setting up the UI frame,
        # linking to the main application instance, and preparing
        # threading events for scan control.
        #
        # Inputs to this function
        #   master (tk.Widget): The parent widget, typically a ttk.Notebook.
        #   app_instance (object): Reference to the main application instance
        #                          to access shared variables and methods.
        #   console_print_func (function): A function to print messages to the
        #                                  application's console output.
        #   **kwargs: Arbitrary keyword arguments passed to the ttk.Frame constructor.
        #
        # Process of this function
        #   1. Calls the superclass constructor (ttk.Frame).
        #   2. Stores references to app_instance and console_print_func.
        #   3. Initializes internal state variables for scan control (is_scanning, is_paused).
        #   4. Creates threading.Event objects (stop_scan_event, pause_scan_event)
        #      for inter-thread communication.
        #   5. Calls _create_widgets to build the UI.
        #
        # Outputs of this function
        #   None. Initializes the Tkinter frame and its internal state.
        #
        # Date / time of changes made to this file: 2025-07-30 18:00:00
        # (2025-08-01) Change: Added current_version to debug_print calls.
        # (2025-08-01) Change: Updated to use 'BigScanButton.TButton' style.
        # (2025-08-01) Change: Updated version to 20250801.5.
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else print

        self.scan_thread = None
        self.is_scanning = False
        self.is_paused = False # New state for pausing
        self.flash_id = None # To store the after ID for flashing, allows cancellation

        # Initialize threading.Event objects for controlling scan flow
        self.stop_scan_event = threading.Event()
        self.pause_scan_event = threading.Event()

        self._create_widgets()


    def _create_widgets(self):
        # This function descriotion tells me what this function does
        # Creates and arranges all the Tkinter widgets that make up the Scan Control tab's GUI.
        # This includes buttons for starting, pausing, and stopping scans.
        #
        # Inputs to this function
        #   None (operates on self).
        #
        # Process of this function
        #   1. Prints a debug message indicating widget creation has started.
        #   2. Creates a LabelFrame for "Scan Control" buttons (Start, Pause, Stop).
        #   3. Creates and grids each button within the scan_buttons_frame,
        #      assigning appropriate commands and initial states.
        #   4. Prints a debug message indicating widget creation is complete.
        #
        # Outputs of this function
        #   None. Modifies the Tkinter frame by adding widgets.
        #
        # Date / time of changes made to this file: 2025-07-30 18:00:00
        # (2025-08-01) Change: Removed 'Skip Group' button.
        # (2025-08-01) Change: Combined Pause and Resume into a single button (`pause_resume_button`).
        # (2025-08-01) Change: Adjusted column configuration for the new button layout.
        # (2025-08-01) Change: Set font size for all buttons to 40pt.
        # (2025-08-01) Change: Updated build version in debug_print calls.
        # (2025-08-01) Change: Updated Start, Pause/Resume, Stop buttons to use 'BigScanButton.TButton' style.
        #                     Removed redundant local ttk.Style configurations.
        # (2025-08-01) Change: Applied specific color styles (Green, Orange, Red) to BigScanButtons.
        # (2025-08-01) Change: Renamed button texts to START, PAUSE, STOP.
        # (2025-08-01) Change: Updated version to 20250801.5.
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/scan_controler_button_logic.py - {current_version}"
        debug_print("Creating Scan Control widgets...", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Frame for scan control buttons
        scan_buttons_frame = ttk.LabelFrame(self, text="Scan Control", style='Dark.TLabelframe')
        scan_buttons_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        # Configure columns for 33% width for three buttons per row (Start, Pause/Resume, Stop)
        scan_buttons_frame.columnconfigure(0, weight=1) # Column for Start
        scan_buttons_frame.columnconfigure(1, weight=1) # Column for Pause/Resume
        scan_buttons_frame.columnconfigure(2, weight=1) # Column for Stop

        # Start Scan Button - Using the new 'BigScanButton.Green.TButton' style
        self.start_button = ttk.Button(scan_buttons_frame, text="START", command=self._start_scan_thread, style='BigScanButton.Green.TButton')
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Pause/Resume Scan Button (combined) - Using the new 'BigScanButton.Orange.TButton' style
        self.pause_resume_button = ttk.Button(scan_buttons_frame, text="PAUSE", command=self._toggle_pause_resume, style='BigScanButton.Orange.TButton', state=tk.DISABLED)
        self.pause_resume_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Stop Scan Button - Using the new 'BigScanButton.Red.TButton' style
        self.stop_button = ttk.Button(scan_buttons_frame, text="STOP", command=self._stop_scan, style='BigScanButton.Red.TButton', state=tk.DISABLED)
        self.stop_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        debug_print("Scan Control widgets created.", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def _start_scan_thread(self):
        # This function descriotion tells me what this function does
        # Initiates the spectrum scan process by creating and starting a new
        # daemon thread to run the _run_scan method. This ensures the GUI
        # remains responsive during the scan.
        #
        # Inputs to this function
        #   None (operates on self).
        #
        # Process of this function
        #   1. Checks if a scan is not already in progress.
        #   2. Clears any existing stop or pause signals to prepare for a new scan.
        #   3. Sets internal flags (is_scanning, is_paused) to reflect the new state.
        #   4. Stops any active flashing animation on the pause/resume button.
        #   5. Updates the GUI's connection status via the main app instance.
        #   6. Creates a new threading.Thread object targeting the _run_scan method.
        #   7. Sets the thread as a daemon thread so it exits with the main application.
        #   8. Starts the newly created thread.
        #   9. Prints messages to the console and debug log.
        #   10. If a scan is already running, it prints an informational message.
        #
        # Outputs of this function
        #   None. Starts a background thread and updates GUI/internal state.
        #
        # Date / time of changes made to this file: 2025-07-30 18:00:00
        # (2025-08-01) Change: Added current_version to debug_print calls.
        # (2025-08-01) Change: Ensures flashing is stopped when starting a new scan.
        # (2025-08-01) Change: Reset pause_resume_button style to 'Orange.TButton' (which is now based on BigScanButton).
        # (2025-08-01) Change: Reset pause_resume_button style to 'BigScanButton.Orange.TButton'.
        # (2025-08-01) Change: Updated version to 20250801.5.
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/scan_controler_button_logic.py - {current_version}"
        debug_print(f"Attempting to start scan thread. Current is_scanning: {self.is_scanning}, is_paused: {self.is_paused}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        if not self.is_scanning:
            # Clear any previous stop/pause signals
            self.stop_scan_event.clear()
            self.pause_scan_event.clear()
            debug_print("Stop/Pause events cleared.", file=current_file, function=current_function, console_print_func=self.console_print_func)

            self.is_scanning = True
            self.is_paused = False # Ensure not paused when starting
            debug_print("is_scanning set to True, is_paused set to False.", file=current_file, function=current_function, console_print_func=self.console_print_func)

            # Stop any flashing when a new scan starts
            self._stop_flashing()
            # Reset button appearance using the appropriate BigScanButton style
            self.pause_resume_button.config(text="PAUSE", style='BigScanButton.Orange.TButton') # Revert to default BigScanButton style

            # Update GUI elements via app_instance's wrapper
            self.app_instance.update_connection_status(self.app_instance.inst is not None)
            debug_print("GUI connection status updated.", file=current_file, function=current_function, console_print_func=self.console_print_func)

            self.scan_thread = threading.Thread(target=self._run_scan, daemon=True)
            self.scan_thread.start()
            self.console_print_func("✅ Scan initiated. Check console for updates.")
            debug_print("Scan thread object created and started.", file=current_file, function=current_function, console_print_func=self.console_print_func)
        else:
            self.console_print_func("ℹ️ Scan is already running. This is annoying, you can't start two scans at once!")
            debug_print("Scan already running, ignoring start request.", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def _toggle_pause_resume(self):
        # This function descriotion tells me what this function does
        # Toggles the pause/resume state of the active scan.
        # It changes the button text, style, and starts/stops flashing.
        #
        # Inputs to this function
        #   None (operates on self).
        #
        # Process of this function
        #   1. Checks if a scan is currently running.
        #   2. If scanning and not paused:
        #      a. Sets the pause event for the background thread.
        #      b. Sets `is_paused` to True.
        #      c. Changes button text to "RESUME".
        #      d. Starts flashing the button.
        #      e. Prints a console message.
        #   3. If scanning and paused:
        #      a. Clears the pause event for the background thread.
        #      b. Sets `is_paused` to False.
        #      c. Changes button text back to "PAUSE".
        #      d. Stops flashing the button.
        #      e. Prints a console message.
        #   4. Updates the GUI's connection status.
        #   5. If no scan is active, prints an informational message.
        #
        # Outputs of this function
        #   None. Modifies internal state and GUI elements related to scan pausing/resuming.
        #
        # Date / time of changes made to this file: 2025-08-01
        # (2025-08-01) Change: Combined _pause_scan and _resume_scan logic into a single toggle function.
        # (2025-08-01) Change: Implemented button text and style changes based on pause/resume state.
        # (2025-08-01) Change: Added flashing mechanism for the button when paused.
        # (2025-08-01) Change: Ensured console message is printed only once per state change.
        # (2025-08-01) Change: Updated button styles to use 'BigScanButton.TButton' as base for flashing.
        # (2025-08-01) Change: Updated button texts to PAUSE and RESUME.
        # (2025-08-01) Change: Updated version to 20250801.5.
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/scan_controler_button_logic.py - {current_version}"
        debug_print(f"Attempting to toggle pause/resume. Current is_scanning: {self.is_scanning}, is_paused: {self.is_paused}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        if self.is_scanning:
            if not self.is_paused:
                # PAUSE LOGIC
                self.pause_scan_event.set() # Signal pause
                self.is_paused = True
                # Change text and style for resume state (flashing will override)
                self.pause_resume_button.config(text="RESUME", style='FlashingGreen.TButton')
                self._start_flashing() # Start the flashing when paused
                self.console_print_func("⏸️ Scan Paused. Click RESUME to continue.")
                debug_print("Scan paused.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            else:
                # RESUME LOGIC
                self.pause_scan_event.clear() # Signal resume
                self.is_paused = False
                # Change text and style back to pause state (non-flashing)
                self.pause_resume_button.config(text="PAUSE", style='BigScanButton.Orange.TButton') # Revert to default BigScanButton style
                self._stop_flashing() # Stop the flashing when resumed
                self.console_print_func("▶️ Scan Resumed.")
                debug_print("Scan resumed.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            # Update GUI elements via app_instance's wrapper
            self.app_instance.update_connection_status(self.app_instance.inst is not None)
        else:
            self.console_print_func("ℹ️ No active scan to pause/resume. You're clicking nothing, you fool!")
            debug_print("No active scan to pause/resume.", file=current_file, function=current_function, console_print_func=self.console_print_func)

    def _start_flashing(self):
        # This function descriotion tells me what this function does
        # Initiates a flashing effect on the `pause_resume_button`.
        # It repeatedly toggles the button's style between 'FlashingGreen.TButton'
        # and 'FlashingDark.TButton' using `after` calls.
        #
        # Inputs to this function
        #   None (operates on self).
        #
        # Process of this function
        #   1. Clears any existing flashing `after` calls to prevent conflicts.
        #   2. Defines the two styles for flashing, which are now based on BigScanButton.
        #   3. Toggles the button's style.
        #   4. Schedules the next toggle using `self.app_instance.after` and stores the ID
        #      in `self.flash_id` for later cancellation.
        #
        # Outputs of this function
        #   None. Modifies the button's visual style over time.
        #
        # Date / time of changes made to this file: 2025-08-01
        # (2025-08-01) Change: Updated to use 'FlashingGreen.TButton' and 'FlashingDark.TButton' styles.
        # (2025-08-01) Change: Updated version to 20250801.5.
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/scan_controler_button_logic.py - {current_version}"
        debug_print("Starting button flashing.", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Ensure any existing flashing is stopped before starting a new one
        self._stop_flashing()

        # Define the two styles for flashing, now using the dedicated flashing styles
        style1 = 'FlashingGreen.TButton' # The "Resume Scan" color
        style2 = 'FlashingDark.TButton' # A contrasting color for flashing

        # Get the current style to determine the next one
        current_style = self.pause_resume_button.cget("style")

        if current_style == style1:
            self.pause_resume_button.config(style=style2)
        else:
            self.pause_resume_button.config(style=style1)
        
        # Schedule the next toggle
        self.flash_id = self.app_instance.after(500, self._start_flashing) # Flash every 500 ms (0.5 seconds)

    def _stop_flashing(self):
        # This function descriotion tells me what this function does
        # Stops any active flashing effect on the `pause_resume_button`.
        # It cancels the scheduled `after` call and resets the button's
        # style to its default 'BigScanButton.TButton' for the "Pause Scan" state
        # or 'FlashingGreen.TButton' if still paused.
        #
        # Inputs to this function
        #   None (operates on self).
        #
        # Process of this function
        #   1. Checks if a flashing `after` call ID exists (`self.flash_id`).
        #   2. If an ID exists, it cancels the scheduled call using `self.app_instance.after_cancel`.
        #   3. Resets `self.flash_id` to None.
        #   4. Ensures the button's style is set back to its non-flashing state
        #      based on whether the scan is still paused or fully resumed/stopped.
        #
        # Outputs of this function
        #   None. Resets the button's visual style.
        #
        # Date / time of changes made to this file: 2025-08-01
        # (2025-08-01) Change: Adjusted to use 'BigScanButton.TButton' and 'FlashingGreen.TButton' for final states.
        # (2025-08-01) Change: Updated version to 20250801.5.
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/scan_controler_button_logic.py - {current_version}"
        debug_print("Stopping button flashing.", file=current_file, function=current_function, console_print_func=self.console_print_func)

        if self.flash_id:
            self.app_instance.after_cancel(self.flash_id)
            self.flash_id = None
        # Ensure the button is set back to its non-flashing state
        if self.is_scanning and self.is_paused:
            # If still paused but flashing stopped (e.g., manual intervention), keep it in resume style
            self.pause_resume_button.config(style='FlashingGreen.TButton') # Keep the green style for "Resume Scan"
        elif not self.is_paused:
            # If not paused, it should be in the normal 'Pause Scan' style (default BigScanButton)
            self.pause_resume_button.config(style='BigScanButton.Orange.TButton') # Use the specific orange style


    def _stop_scan(self):
        # This function descriotion tells me what this function does
        # Signals the running scan thread to stop its operation gracefully.
        # It waits for the thread to finish before resetting the scan state.
        #
        # Inputs to this function
        #   None (operates on self).
        #
        # Process of this function
        #   1. Checks if a scan is currently in progress.
        #   2. Sets the stop event to signal the background thread to terminate.
        #   3. Clears the pause event and resets the is_paused flag.
        #   4. Stops any active flashing on the pause/resume button.
        #   5. Resets the pause/resume button text and style.
        #   6. Prints a message indicating the scan is stopping.
        #   7. Attempts to join the scan thread with a timeout to ensure it finishes.
        #   8. Resets the is_scanning flag to False.
        #   9. Updates the GUI's connection status.
        #   10. Prints a confirmation message that the scan has stopped.
        #   11. If no scan is active, prints an informational message.
        #
        # Outputs of this function
        #   None. Modifies internal state and GUI elements related to scan stopping.
        #
        # Date / time of changes made to this file: 2025-07-30 18:00:00
        # (2025-08-01) Change: Added current_version to debug_print calls.
        # (2025-08-01) Change: Ensures flashing is stopped and button text/style is reset upon stop.
        # (2025-08-01) Change: Reset pause_resume_button style to 'BigScanButton.TButton' upon stop.
        # (2025-08-01) Change: Updated button text to STOP.
        # (2025-08-01) Change: Updated version to 20250801.5.
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/scan_controler_button_logic.py - {current_version}"
        debug_print("Attempting to stop scan.", file=current_file, function=current_function, console_print_func=self.console_print_func)

        if self.is_scanning:
            self.stop_scan_event.set() # Signal stop
            self.pause_scan_event.clear() # Ensure it's not paused if stopping
            self.is_paused = False # Reset pause state
            
            self._stop_flashing() # Stop flashing immediately on stop
            # Reset button to default BigScanButton style
            self.pause_resume_button.config(text="PAUSE", style='BigScanButton.Orange.TButton')
            
            self.console_print_func("🛑 Stopping scan. Please wait...")
            debug_print("Stop event set. Waiting for scan thread to finish.", file=current_file, function=current_function, console_print_func=self.console_print_func)

            # Join the thread to ensure it finishes before resetting state, with a timeout
            if self.scan_thread and self.scan_thread.is_alive():
                self.scan_thread.join(timeout=5) # Wait up to 5 seconds
                if self.scan_thread.is_alive():
                    self.console_print_func("⚠️ Warning: Scan thread did not terminate gracefully. This damn thing is stubborn!")
                    debug_print("Scan thread join timed out.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            
            self.is_scanning = False # Reset scanning state
            # Update GUI elements via app_instance's wrapper
            self.app_instance.update_connection_status(self.app_instance.inst is not None)
            self.console_print_func("✅ Scan stopped. Finally, some peace and quiet!")
            debug_print("Scan stopped and states reset.", file=current_file, function=current_function, console_print_func=self.console_print_func)
        else:
            self.console_print_func("ℹ️ No active scan to stop. What are you trying to stop, thin air?!")
            debug_print("No active scan to stop.", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def _run_scan(self):
        # This function descriotion tells me what this function does
        # Executes the main scan process in a separate thread. It retrieves
        # scan parameters from the GUI, iterates through scan cycles,
        # calls the core instrument scanning logic (scan_bands), and
        # handles post-scan data processing (stitching).
        # It also manages pause/stop events.
        #
        # Inputs to this function
        #   None (operates on self).
        #
        # Process of this function
        #   1. Prints debug messages on entry.
        #   2. Initializes variables for scan data storage (scan_name, all_raw_scans_data_for_stitching).
        #   3. Retrieves all necessary scan parameters (e.g., scan name, output folder,
        #      number of cycles, RBW, reference level, etc.) from the app_instance's
        #      Tkinter variables.
        #   4. Retrieves selected frequency bands from app_instance.
        #   5. Performs checks: if no bands are selected or no instrument is connected,
        #      it logs an error and exits.
        #   6. Enters a loop for the specified number of scan cycles.
        #   7. Inside the loop:
        #      a. Checks for stop signals.
        #      b. Calls the `scan_bands` function (from `utils.scan_instrument`)
        #         to perform the actual instrument interaction and data collection for the current cycle.
        #      c. Appends collected `raw_scan_data` to `all_raw_scans_data_for_stitching`.
        #      d. Handles pause events (waits if paused).
        #      e. Waits for a specified `cycle_wait_time_seconds` between cycles.
        #   8. After the scan cycles complete (or are stopped):
        #      a. If `all_raw_scans_data_for_stitching` contains data, it proceeds to:
        #         i. Converts raw data to a pandas DataFrame.
        #         ii. Calls `process_and_stitch_scan_data` to combine and aggregate scans.
        #         iii. Stores the processed data (stitched, aggregated, individual)
        #              in `app_instance` for access by other tabs.
        #      b. If no scan data was collected, it logs an informational message.
        #   9. Includes robust error handling (AttributeError, general Exception)
        #      to catch issues during parameter retrieval or scan execution.
        #   10. Ensures that `is_scanning` and `is_paused` flags are reset in a `finally` block,
        #       guaranteeing state cleanup even if errors occur.
        #
        # Outputs of this function
        #   None. Collects and processes scan data, and updates application state.
        #
        # Date / time of changes made to this file: 2025-07-30 18:00:00
        # (2025-08-01) Change: Added current_version to debug_print calls.
        # (2025-08-01) Change: Updated version to 20250801.5.
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/scan_controler_button_logic.py - {current_version}"
        self.console_print_func("Debug: Entered _run_scan method (thread started successfully).")
        debug_print("Entered _run_scan method (thread started successfully).", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Initialize scan_name here so it's always available in finally block
        scan_name = "Last Scan" # Default value
        all_raw_scans_data_for_stitching = [] # Initialize here for finally block access

        try:
            # --- DEBUGGING START ---
            self.console_print_func(f"DEBUG: Type of self.app_instance in _run_scan: {type(self.app_instance)}")
            debug_print(f"DEBUG: Type of self.app_instance in _run_scan: {type(self.app_instance)}", file=current_file, function=current_function, console_print_func=self.console_print_func)
            
            if not hasattr(self.app_instance, 'general_debug_enabled_var'):
                self.console_print_func("ERROR: self.app_instance does NOT have 'general_debug_enabled_var' attribute! This is a **fucking nightmare**!")
                debug_print("ERROR: self.app_instance does NOT have 'general_debug_enabled_var' attribute!", file=current_file, function=current_function, console_print_func=self.console_print_func)
                # Re-raise the error to make it clear in the log if this is the case
                raise AttributeError("'_tkinter.tkapp' object has no attribute 'debug_enabled_var' - Confirmed in _run_scan, this is broken as hell!")
            # --- DEBUGGING END ---

            # Get current settings from app_instance Tkinter variables
            scan_name = self.app_instance.scan_name_var.get()
            output_folder = self.app_instance.output_folder_var.get()
            num_scan_cycles = self.app_instance.num_scan_cycles_var.get()
            rbw_step_size_hz = float(self.app_instance.rbw_step_size_hz_var.get())
            cycle_wait_time_seconds = float(self.app_instance.cycle_wait_time_seconds_var.get())
            maxhold_time_seconds = float(self.app_instance.maxhold_time_seconds_var.get())
            scan_rbw_hz = float(self.app_instance.scan_rbw_hz_var.get())
            reference_level_dbm = float(self.app_instance.reference_level_dbm_var.get())
            freq_shift_hz = float(self.app_instance.freq_shift_hz_var.get())
            maxhold_enabled = self.app_instance.maxhold_enabled_var.get()
            high_sensitivity = self.app_instance.high_sensitivity_var.get()
            preamp_on = self.app_instance.preamp_on_var.get()
            scan_rbw_segmentation = float(self.app_instance.scan_rbw_segmentation_var.get())

            # These are the variables that were causing the error
            general_debug_enabled = self.app_instance.general_debug_enabled_var.get()
            log_visa_commands_enabled = self.app_instance.log_visa_commands_enabled_var.get()

            # Get selected bands from the app_instance's band_vars
            selected_bands = [
                band_item["band"] for band_item in self.app_instance.band_vars
                if band_item["var"].get()
            ]

            if not selected_bands:
                self.app_instance.after(0, lambda: self.console_print_func("⚠️ No frequency bands selected for scan. Please select bands in 'Scan Configuration' tab. This is useless without bands, you dumbass!"))
                debug_print("No bands selected for scan.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                return # Exit if no bands are selected

            if not self.app_instance.inst:
                self.app_instance.after(0, lambda: self.console_print_func("❌ Instrument not connected. Cannot start scan. Connect the damn thing first!"))
                debug_print("Instrument not connected for scan.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                return # Exit if instrument is not connected

            # Initialize lists to store scan data for plotting and saving
            # all_raw_scans_data_for_stitching is already initialized above
            all_markers_data_from_scans = [] # Placeholder for markers extracted during scan

            # Loop for multiple scan cycles
            for cycle_num in range(num_scan_cycles):
                if self.stop_scan_event.is_set():
                    self.app_instance.after(0, lambda: self.console_print_func(f"Scan stopped by user after {cycle_num} cycles. Good riddance!"))
                    debug_print(f"Scan stopped by user after {cycle_num} cycles.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                    break

                self.app_instance.after(0, lambda: self.console_print_func(f"\n--- Starting Scan Cycle {cycle_num + 1} of {num_scan_cycles} ---"))
                debug_print(f"Starting scan cycle {cycle_num + 1}.", file=current_file, function=current_function, console_print_func=self.console_print_func)

                # Call the core scanning logic
                last_successful_band_index, raw_scan_data, markers_data = scan_bands(
                    app_instance_ref=self.app_instance, # Pass the app_instance_ref
                    inst=self.app_instance.inst,
                    selected_bands=selected_bands,
                    rbw_hz=scan_rbw_hz,
                    ref_level_dbm=reference_level_dbm,
                    freq_shift_hz=freq_shift_hz,
                    maxhold_enabled=maxhold_enabled,
                    high_sensitivity=high_sensitivity,
                    preamp_on=preamp_on,
                    rbw_step_size_hz=rbw_step_size_hz,
                    max_hold_time_seconds=maxhold_time_seconds,
                    scan_name=scan_name,
                    output_folder=output_folder,
                    stop_event=self.stop_scan_event,
                    pause_event=self.pause_scan_event,
                    log_visa_commands_enabled=log_visa_commands_enabled,
                    general_debug_enabled=general_debug_enabled,
                    app_console_update_func=self.console_print_func
                )
                
                # Explicitly check if raw_scan_data is not None and is a list (or has length)
                if raw_scan_data is not None and isinstance(raw_scan_data, list) and len(raw_scan_data) > 0:
                    all_raw_scans_data_for_stitching.extend(raw_scan_data)
                    # For now, markers_data is a placeholder, but if it contained data, you'd extend it here
                    all_markers_data_from_scans.extend(markers_data)
                    debug_print(f"Collected {len(raw_scan_data)} points for cycle {cycle_num + 1}.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                else:
                    self.app_instance.after(0, lambda: self.console_print_func(f"⚠️ No data collected for cycle {cycle_num + 1}. Scan may have been stopped or encountered an error. What a waste!"))
                    debug_print(f"No data collected for cycle {cycle_num + 1}.", file=current_file, function=current_function, console_print_func=self.console_print_func)

                if cycle_num < num_scan_cycles - 1 and not self.stop_scan_event.is_set():
                    self.app_instance.after(0, lambda: self.console_print_func(f"Waiting {cycle_wait_time_seconds} seconds before next cycle... Get a move on!"))
                    debug_print(f"Waiting {cycle_wait_time_seconds} seconds before next cycle.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                    time.sleep(cycle_wait_time_seconds)
                
                if self.stop_scan_event.is_set():
                    self.app_instance.after(0, lambda: self.console_print_func(f"Scan stopped by user during wait after cycle {cycle_num + 1}. Don't be a quitter!"))
                    debug_print(f"Scan stopped by user during wait after cycle {cycle_num + 1}.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                    break


            # --- Post-scan processing ---
            # Changed `if all_raw_scans_data_for_stitching:` to explicitly check if the list is not empty
            if all_raw_scans_data_for_stitching:
                self.app_instance.after(0, lambda: self.console_print_func("\n--- Processing and Stitching Scan Data ---"))
                debug_print("Processing and stitching scan data.", file=current_file, function=current_function, console_print_func=self.console_print_func)

                # Convert list of lists of tuples to a single DataFrame for stitching
                combined_raw_df = pd.DataFrame([point for sublist in all_raw_scans_data_for_stitching for point in sublist], columns=['Frequency (Hz)', 'Power (dBm)'])
                
                # Perform stitching and aggregation
                # Debug print the types of arguments being passed to process_and_stitch_scan_data
                debug_print(f"DEBUG: Calling process_and_stitch_scan_data with types:", file=current_file, function=current_function, console_print_func=self.console_print_func)
                debug_print(f"  combined_raw_df: {type(combined_raw_df)}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                debug_print(f"  self.app_instance.SCAN_BAND_RANGES: {type(self.app_instance.SCAN_BAND_RANGES)}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                debug_print(f"  self.app_instance.MHZ_TO_HZ: {type(self.app_instance.MHZ_TO_HZ)}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                debug_print(f"  self.console_print_func: {type(self.console_print_func)}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                
                # Corrected call to process_and_stitch_scan_data
                # Assuming the signature is (df, band_ranges, mhz_to_hz, console_print_func)
                # If scan_rbw_segmentation is needed, it must be accessed differently (e.g., from app_instance)
                stitched_df, aggregated_df, individual_scan_dfs_with_names = process_and_stitch_scan_data(
                    combined_raw_df,
                    self.app_instance.SCAN_BAND_RANGES,
                    self.app_instance.MHZ_TO_HZ,
                    self.console_print_func
                )

                # Store stitched data in app_instance for plotting tab (still useful if other parts of the app plot)
                self.app_instance.collected_scans_dataframes = [
                    {'df': stitched_df, 'name': scan_name, 'type': 'stitched'}
                ]
                # Store individual scan data for multi-trace plotting (might be removed later if no plotting uses this)
                self.app_instance.individual_scan_dfs_for_plotting = individual_scan_dfs_with_names
                # Store aggregated data for plotting (might be removed later if no plotting uses this)
                self.app_instance.aggregated_scan_dataframe = aggregated_df
                self.app_instance.last_scan_markers = all_markers_data_from_scans # Store collected markers

                self.app_instance.after(0, lambda: self.console_print_func("✅ Scan data processed. Finally, some progress!"))
                debug_print("Scan data processed.", file=current_file, function=current_function, console_print_func=self.console_print_func)

                # Store the scan_name for button update and future plotting (kept for now, if _plot_last_scan is added back)
                self.app_instance.last_scan_name_for_plot = scan_name 

            else:
                self.app_instance.after(0, lambda: self.console_print_func("ℹ️ No scan data collected to process. What's the point of this then?!"))
                debug_print("No scan data collected for processing.", file=current_file, function=current_function, console_print_func=self.console_print_func)


        except AttributeError as e:
            self.is_scanning = False
            self.is_paused = False
            self.app_instance.after(0, lambda: self.console_print_func(f"❌ An AttributeError occurred during scan: {e}. This might indicate a missing Tkinter variable or incorrect object reference. This is a **fucking nightmare**!"))
            debug_print(f"AttributeError during scan: {e}", file=current_file, function=current_function, console_print_func=self.console_print_func)
            self.app_instance.after(0, self.app_instance.update_connection_status, self.app_instance.inst is not None)
        except Exception as e:
            self.is_scanning = False
            self.is_paused = False
            self.app_instance.after(0, lambda: self.console_print_func(f"❌ An error occurred during scan: {e}. This is some serious **bullshit**!"))
            debug_print(f"Error during scan: {e}", file=current_file, function=current_function, console_print_func=self.console_print_func)
            self.app_instance.after(0, self.app_instance.update_connection_status, self.app_instance.inst is not None)
        finally:
            self.is_scanning = False
            self.is_paused = False
            self.app_instance.after(0, lambda: self.console_print_func("\n--- Scan process finished. Thank the lord! ---"))
            debug_print("Scan process finished in finally block.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            self.app_instance.after(0, self.app_instance.update_connection_status, self.app_instance.inst is not None)
