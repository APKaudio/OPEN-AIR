# tabs/Start_Pause_Stop/scan_control_display.py
#
# This file defines the Tkinter Frame for controlling spectrum scans,
# including starting, pausing, and stopping scans. It manages the GUI
# elements and delegates the core scanning logic to a separate module.
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
# Version 20250802.1701.17 (Refactored to separate display from logic.)

current_version = "20250802.1701.17" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 1701 * 17 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk, filedialog
import threading
import inspect
import os # For os.path.basename(__file__)

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Import the new scan control logic functions
from tabs.Start_Pause_Stop.scan_control_logic import start_scan_logic, toggle_pause_resume_logic, stop_scan_logic

# Import connection status logic
from src.connection_status_logic import update_connection_status_logic


class ScanControlTab(ttk.Frame):
    """
    A Tkinter Frame that provides controls for starting, pausing, and stopping spectrum scans.
    It manages the GUI elements and delegates the core scanning logic to a separate module.
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

        current_file = f"{os.path.basename(__file__)} - {current_version}" # Define current_file for debug_log
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing ScanControlTab. Version: {current_version}. Setting up scan controls!",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        self.scan_thread = None # This will now be managed by scan_control_logic, but we keep a reference
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        # self.is_paused_by_user is now managed by app_instance directly

        self._create_widgets()
        self._update_button_states() # Initial state update

        debug_log(f"ScanControlTab initialized. Version: {current_version}. Scan controls ready!",
                    file=current_file,
                    version=current_version,
                    function=current_function)


    def _create_widgets(self):
        """
        Creates and arranges the buttons for scan control (Start, Pause, Stop).
        """
        current_file = f"{os.path.basename(__file__)} - {current_version}" # Define current_file for debug_log
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating ScanControlTab widgets... Building the scan control buttons! Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1) # Center buttons horizontally

        # Start Scan Button
        self.start_button = ttk.Button(self, text="Start Scan", command=self._start_scan_action, style='Green.TButton')
        self.start_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Pause/Resume Button
        self.pause_resume_button = ttk.Button(self, text="Pause Scan", command=self._toggle_pause_resume_action, style='Orange.TButton')
        self.pause_resume_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Stop Scan Button
        self.stop_button = ttk.Button(self, text="Stop Scan", command=self._stop_scan_action, style='Red.TButton')
        self.stop_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Progress Bar
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Progress Label
        self.progress_label = ttk.Label(self, text="Scan Progress: 0%", style='TLabel')
        self.progress_label.grid(row=4, column=0, padx=10, pady=2, sticky="ew")

        debug_log(f"ScanControlTab widgets created. Buttons are in place! Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)


    def _update_button_states(self):
        """
        Updates the state of the scan control buttons based on connection and scan status.
        This function is called by connection_status_logic.py
        """
        current_file = f"{os.path.basename(__file__)} - {current_version}" # Define current_file for debug_log
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating scan button states. Connected: {self.app_instance.inst is not None}, Scanning: {self.app_instance.scan_thread and self.app_instance.scan_thread.is_alive()}. Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        is_connected = self.app_instance.inst is not None
        is_scanning = self.app_instance.scan_thread and self.app_instance.scan_thread.is_alive()

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
                    file=current_file,
                    version=current_version,
                    function=current_function)


    def _start_scan_action(self):
        """
        Action triggered by the Start Scan button. Calls the logic function.
        """
        current_file = f"{os.path.basename(__file__)} - {current_version}" # Define current_file for debug_log
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Start Scan button pressed. Calling scan logic. Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        
        # Pass self._update_progress as the callback for logic to update GUI
        if start_scan_logic(self.app_instance, self.console_print_func, self.stop_event, self.pause_event, self._update_progress):
            self._update_button_states() # Update UI immediately after starting thread
            update_connection_status_logic(self.app_instance, True, True, self.console_print_func) # Update main app status


    def _toggle_pause_resume_action(self):
        """
        Action triggered by the Pause/Resume button. Calls the logic function.
        """
        current_file = f"{os.path.basename(__file__)} - {current_version}" # Define current_file for debug_log
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Pause/Resume button pressed. Calling toggle pause/resume logic. Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        toggle_pause_resume_logic(self.app_instance, self.console_print_func, self.pause_event)
        self._update_button_states() # Update UI immediately


    def _stop_scan_action(self):
        """
        Action triggered by the Stop Scan button. Calls the logic function.
        """
        current_file = f"{os.path.basename(__file__)} - {current_version}" # Define current_file for debug_log
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Stop Scan button pressed. Calling stop scan logic. Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        stop_scan_logic(self.app_instance, self.console_print_func, self.stop_event, self.pause_event)
        self._update_button_states() # Update UI immediately after stopping


    def _update_progress(self, value):
        """
        Updates the progress bar and label on the GUI.
        This method is called from the scanning thread (via after()), so it updates the GUI safely.
        """
        # Ensure GUI updates are done on the main thread
        self.app_instance.after(0, lambda: self.progress_bar.config(value=value))
        self.app_instance.after(0, lambda: self.progress_label.config(text=f"Scan Progress: {value:.1f}%"))

    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Ensures button states are refreshed.
        """
        current_file = f"{os.path.basename(__file__)} - {current_version}" # Define current_file for debug_log
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Scan Control Tab selected. Refreshing button states! Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        self._update_button_states()
        # Also ensure the main app's connection status logic is run to update other tabs
        is_connected = self.app_instance.inst is not None
        is_scanning = self.app_instance.scan_thread and self.app_instance.scan_thread.is_alive()
        update_connection_status_logic(self.app_instance, is_connected, is_scanning, self.console_print_func)

