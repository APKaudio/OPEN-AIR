# tabs/Experiments/tab_experiments_child_JSON_api.py
#
# This file defines the JsonApiTab, a Tkinter Frame that provides controls for
# starting/stopping a Flask-based JSON API. This API allows external access to
# scan data and marker data, including real-time scan-in-progress data.
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
# Version 20250801.2155.1 (Refactored debug_print to use debug_log and console_log.)

current_version = "20250801.2155.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250801 * 2155 * 1 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import os
import inspect
import webbrowser # For opening API links in browser
import subprocess # For running the Flask JSON API
import threading # For running the Flask JSON API in a separate thread
import time # For brief pauses
import sys # Explicitly import sys for use with sys.executable
import requests # For making HTTP requests to the Flask API

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log


class JsonApiTab(ttk.Frame):
    """
    A Tkinter Frame that provides controls for starting/stopping a JSON API
    and accessing scan data and marker data via that API.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the JsonApiTab.

        Inputs:
            master (tk.Widget): The parent widget.
            app_instance (App): The main application instance, used for accessing
                                shared state like collected_scans_dataframes and output directory.
            console_print_func (function): Function to print messages to the GUI console.
            **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        """
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
        self.json_api_process = None # To store the subprocess for the JSON API
        self.json_api_port = 5000 # Default port for the Flask API
        self.json_api_url_base = f"http://127.0.0.1:{self.json_api_port}"

        self._create_widgets()
        # Ensure API buttons are updated on startup
        self._update_api_button_states()

    def _create_widgets(self):
        """
        Creates and arranges the widgets for the JSON API tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log
        debug_log("Creating JsonApiTab widgets...",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # JSON API Controls
        self.api_control_frame = ttk.LabelFrame(self, text="JSON API Controls", style='Dark.TLabelframe')
        self.api_control_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.api_control_frame.grid_columnconfigure(0, weight=1)
        self.api_control_frame.grid_columnconfigure(1, weight=1)

        self.start_api_button = ttk.Button(self.api_control_frame, text="Start API", command=self._start_json_api, style='Green.TButton')
        self.start_api_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.stop_api_button = ttk.Button(self.api_control_frame, text="Stop API", command=self._stop_json_api, style='Red.TButton', state=tk.DISABLED)
        self.stop_api_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.view_all_scans_button = ttk.Button(self.api_control_frame, text="View All API Scans", command=self._open_all_api_scans, style='Purple.TButton', state=tk.DISABLED)
        self.view_all_scans_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Updated: This button now points to the static /api/latest_scan_data endpoint
        self.view_latest_scan_api_button = ttk.Button(self.api_control_frame, text="View Latest API Scan", command=self._open_latest_api_scan, style='Purple.TButton', state=tk.DISABLED)
        self.view_latest_scan_api_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # New button for scan in progress
        self.view_in_progress_api_button = ttk.Button(self.api_control_frame, text="View Scan In Progress API", command=self._open_scan_in_progress_api, style='Blue.TButton', state=tk.DISABLED)
        self.view_in_progress_api_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.view_markers_api_button = ttk.Button(self.api_control_frame, text="View Markers API", command=self._open_markers_api, style='Orange.TButton', state=tk.DISABLED)
        self.view_markers_api_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Frame for dynamically generated scan buttons
        # This frame's row is now adjusted to be below all static API control buttons
        self.dynamic_scan_buttons_frame = ttk.LabelFrame(self, text="Available API Scans", style='Dark.TLabelframe')
        self.dynamic_scan_buttons_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.dynamic_scan_buttons_frame.grid_columnconfigure(0, weight=1)
        self.dynamic_scan_buttons_frame.grid_remove()

        debug_log("JsonApiTab widgets created.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    def _run_json_api_thread_target(self):
        """
        Target function for the thread that runs the Flask JSON API.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log
        debug_log("JSON API thread target started.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        script_path = os.path.join(self.app_instance._script_dir, 'process_math', 'json_host.py')

        try:
            self.json_api_process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.DETACHED_PROCESS if os.name == 'nt' else 0
            )
            self.app_instance.after(100, self._update_api_button_states)
            self.console_print_func(f"▶️ JSON API started on {self.json_api_url_base}")
            debug_log(f"JSON API subprocess started with PID: {self.json_api_process.pid}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except FileNotFoundError:
            self.console_print_func(f"❌ Error: Python interpreter not found at {sys.executable}. Ensure Python is in your PATH.")
            debug_log(f"Python interpreter not found: {sys.executable}. Fucking useless!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except Exception as e:
            self.console_print_func(f"❌ Error starting JSON API: {e}")
            debug_log(f"Error starting JSON API: {e}. This thing is a pain in the ass!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        debug_log("JSON API thread target finished.",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _start_json_api(self):
        """
        Starts the Flask JSON API in a separate thread.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log
        debug_log("Attempting to start JSON API...",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if self.json_api_process and self.json_api_process.poll() is None:
            self.console_print_func("ℹ️ JSON API is already running.")
            debug_log("JSON API already running. Fucking redundant!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        api_thread = threading.Thread(target=self._run_json_api_thread_target)
        api_thread.daemon = True
        api_thread.start()

    def _stop_json_api(self):
        """
        Stops the Flask JSON API subprocess.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log
        debug_log("Attempting to stop JSON API...",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if self.json_api_process and self.json_api_process.poll() is None:
            try:
                self.json_api_process.terminate()
                self.json_api_process.wait(timeout=2)
                if self.json_api_process.poll() is None:
                    self.json_api_process.kill()
                    self.console_print_func("⚠️ JSON API process killed (forcefully terminated).")
                    debug_log("JSON API process forcefully killed. Take that, you bastard!",
                                file=__file__,
                                version=current_version,
                                function=current_function)
                self.console_print_func("⏹️ JSON API stopped.")
                debug_log("JSON API process terminated.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            except Exception as e:
                self.console_print_func(f"❌ Error stopping JSON API: {e}")
                debug_log(f"Error stopping JSON API: {e}. This thing refuses to die!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            finally:
                self.json_api_process = None
                self.app_instance.after(100, self._update_api_button_states)
        else:
            self.console_print_func("ℹ️ JSON API is not running.")
            debug_log("JSON API not running. Fucking pointless to stop what's not there!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            self._update_api_button_states()


    def _update_api_button_states(self):
        """
        Updates the state of the JSON API related buttons based on API process status.
        """
        is_api_running = self.json_api_process and self.json_api_process.poll() is None
        self.start_api_button.config(state=tk.DISABLED if is_api_running else tk.NORMAL)
        self.stop_api_button.config(state=tk.NORMAL if is_api_running else tk.DISABLED)
        self.view_all_scans_button.config(state=tk.NORMAL if is_api_running else tk.DISABLED)
        self.view_markers_api_button.config(state=tk.NORMAL if is_api_running else tk.DISABLED)

        # Check if scan_control_tab exists and is_scanning is True
        is_scanning = getattr(self.app_instance, 'scan_control_tab', None) and self.app_instance.scan_control_tab.is_scanning
        self.view_in_progress_api_button.config(state=tk.NORMAL if is_api_running and is_scanning else tk.DISABLED)

        # "View Latest API Scan" is always enabled if API is running, as the endpoint handles finding the latest.
        self.view_latest_scan_api_button.config(state=tk.NORMAL if is_api_running else tk.DISABLED)


    def _open_all_api_scans(self):
        """
        Fetches the list of scan files from the API and creates dynamic buttons for each.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log
        debug_log("Attempting to fetch all API scans and display buttons...",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if not (self.json_api_process and self.json_api_process.poll() is None):
            self.console_print_func("⚠️ JSON API is not running. Please start it first to view available scans.")
            debug_log("JSON API not running for _open_all_api_scans. Fucking useless!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        # Clear existing buttons
        for widget in self.dynamic_scan_buttons_frame.winfo_children():
            widget.destroy()
        self.dynamic_scan_buttons_frame.grid_remove() # Hide frame until populated

        def fetch_and_display():
            try:
                response = requests.get(f"{self.json_api_url_base}/api/list_scans")
                response.raise_for_status()
                scan_files = response.json()

                if scan_files:
                    self.app_instance.after(0, lambda: self.console_print_func(f"✅ Found {len(scan_files)} scan files from API."))
                    self.app_instance.after(0, lambda: self.dynamic_scan_buttons_frame.grid())

                    for i, filename in enumerate(scan_files):
                        button = ttk.Button(
                            self.dynamic_scan_buttons_frame,
                            text=filename,
                            command=lambda f=filename: self._open_api_scan_data(f),
                            style='Blue.TButton'
                        )
                        button.grid(row=i, column=0, padx=2, pady=2, sticky="ew")
                        self.dynamic_scan_buttons_frame.grid_columnconfigure(0, weight=1)
                else:
                    self.app_instance.after(0, lambda: self.console_print_func("ℹ️ No scan files found via API."))
                    self.app_instance.after(0, lambda: self.dynamic_scan_buttons_frame.grid_remove())
                    debug_log("No scan files found via API. Fucking empty!",
                                file=__file__,
                                version=current_version,
                                function=current_function)

            except requests.exceptions.ConnectionError:
                self.app_instance.after(0, lambda: self.console_print_func("❌ Error: Could not connect to JSON API. Is it running?"))
                debug_log("ConnectionError to JSON API. What the hell?!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            except requests.exceptions.RequestException as e:
                self.app_instance.after(0, lambda: self.console_print_func(f"❌ Error fetching scan list from API: {e}"))
                debug_log(f"RequestException fetching scan list: {e}. This thing is a pain in the ass!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            except Exception as e:
                self.app_instance.after(0, lambda: self.console_print_func(f"❌ An unexpected error occurred while fetching scan list: {e}"))
                debug_log(f"Unexpected error fetching scan list: {e}. This is a goddamn mess!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            finally:
                self.app_instance.after(0, self._update_api_button_states)

        api_call_thread = threading.Thread(target=fetch_and_display)
        api_call_thread.daemon = True
        api_call_thread.start()


    def _open_api_scan_data(self, filename):
        """
        Opens the API endpoint for a specific scan file in the browser.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log
        debug_log(f"Attempting to open API scan data for: {filename}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if not (self.json_api_process and self.json_api_process.poll() is None):
            self.console_print_func("⚠️ JSON API is not running. Please start it first.")
            debug_log("JSON API not running for _open_api_scan_data. Fucking useless!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        api_link = f"{self.json_api_url_base}/api/scan_data/{filename}"
        try:
            webbrowser.open_new_tab(api_link)
            self.console_print_func(f"✅ Opened API link for scan: {filename}")
            debug_log(f"Opened {api_link}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except Exception as e:
            self.console_print_func(f"❌ Error opening API scan link for {filename}: {e}")
            debug_log(f"Error opening API scan link for {filename}: {e}. This is a goddamn mess!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    def _open_markers_api(self):
        """
        Opens the API endpoint for MARKERS.csv in the browser.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log
        debug_log("Attempting to open Markers API link...",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if not (self.json_api_process and self.json_api_process.poll() is None):
            self.console_print_func("⚠️ JSON API is not running. Please start it first.")
            debug_log("JSON API not running for _open_markers_api. Fucking useless!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        api_link = f"{self.json_api_url_base}/api/markers_data"
        try:
            webbrowser.open_new_tab(api_link)
            self.console_print_func("✅ Opened API link for MARKERS.csv data.")
            debug_log(f"Opened {api_link}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except Exception as e:
            self.console_print_func(f"❌ Error opening Markers API link: {e}")
            debug_log(f"Error opening Markers API link: {e}. This is a goddamn mess!",
                        file=__file__,
                        version=current_version,
                        function=current_function)


    def _open_latest_api_scan(self):
        """
        Opens the API endpoint for the latest scan data in the browser.
        This endpoint is static and the API handles finding the latest file.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log
        debug_log("Attempting to open latest API scan link...",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if not (self.json_api_process and self.json_api_process.poll() is None):
            self.console_print_func("⚠️ JSON API is not running. Please start it first.")
            debug_log("JSON API not running for _open_latest_api_scan. Fucking useless!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        api_link = f"{self.json_api_url_base}/api/latest_scan_data" # Static URL for latest scan
        try:
            webbrowser.open_new_tab(api_link)
            self.console_print_func(f"✅ Opened API link for latest scan data.")
            debug_log(f"Opened {api_link}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except Exception as e:
            self.console_print_func(f"❌ Error opening latest API scan link: {e}")
            debug_log(f"Error opening latest API scan link: {e}. This is a goddamn mess!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    def _open_scan_in_progress_api(self):
        """
        Opens the API endpoint for the scan in progress data in the browser.
        This endpoint is static.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log
        debug_log("Attempting to open scan in progress API link...",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if not (self.json_api_process and self.json_api_process.poll() is None):
            self.console_print_func("⚠️ JSON API is not running. Please start it first.")
            debug_log("JSON API not running for _open_scan_in_progress_api. Fucking useless!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        # Check if a scan is actually in progress
        is_scanning = getattr(self.app_instance, 'scan_control_tab', None) and self.app_instance.scan_control_tab.is_scanning
        if not is_scanning:
            self.console_print_func("ℹ️ No scan is currently in progress.")
            debug_log("No scan in progress for _open_scan_in_progress_api. Fucking pointless!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        api_link = f"{self.json_api_url_base}/api/scan_in_progress_data" # Static URL for scan in progress
        try:
            webbrowser.open_new_tab(api_link)
            self.console_print_func(f"✅ Opened API link for scan in progress data.")
            debug_log(f"Opened {api_link}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except Exception as e:
            self.console_print_func(f"❌ Error opening scan in progress API link: {e}")
            debug_log(f"Error opening scan in progress API link: {e}. This is a goddamn mess!",
                        file=__file__,
                        version=current_version,
                        function=current_function)


    def _on_tab_selected(self, event):
        """
        Callback for when this tab is selected.
        This can be used to refresh data or update UI elements specific to this tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log
        debug_log("JSON API Tab selected.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Update API button states when the tab is selected
        self._update_api_button_states()