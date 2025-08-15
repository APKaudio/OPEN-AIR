# tabs/Plotting/tab_plotting_child_3D.py
#
# This file defines a Tkinter Frame for generating 3D plots of scans over time.
# It includes functionality for selecting a folder, identifying series of scans,
# and generating the interactive 3D plot.
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
# Version 20250801.2250.1 (Refactored debug_print to use debug_log and console_log.)

current_version = "20250801.2250.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250801 * 2250 * 1 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import pandas as pd
import inspect
import webbrowser # For opening HTML plot in browser
import re # Added for regex in file grouping
import platform # For opening folder cross-platform
import glob # For finding files with specific patterns
from datetime import datetime # Import datetime for timestamping plots
import numpy as np # Added for PSD calculation

# CORRECTED: Import plotting functions and _open_plot_in_browser directly from utils.plotting_utils
from tabs.Plotting.utils_plotting_scans_over_time import plot_Scans_over_time

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log


class Plotting3DTab(ttk.Frame):
    """
    A Tkinter Frame that provides functionality for generating 3D plots of scans over time.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the Plotting3DTab.

        Inputs:
            master (tk.Widget): The parent widget.
            app_instance (App): The main application instance, used for accessing
                                shared state like collected_scans_dataframes and output directory.
            console_print_func (function): Function to print messages to the GUI console.
            **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        """
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log # Use provided func or console_log
        self.last_opened_folder = None # To remember the last opened folder for 3D plotting
        self.grouped_csv_files = {} # Dictionary to store grouped CSV files for 3D plotting
        self.selected_group_prefix = None # Stores the prefix of the currently selected group for 3D plotting

        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        self._create_widgets()
        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    def _create_widgets(self):
        """
        Function Description:
        Creates and arranges all the widgets for the Plotting3DTab.

        Inputs to this function:
            None.

        Process of this function:
            1. Creates the main LabelFrame for "3D Scans Over Time Plotting".
            2. Adds a button to open a folder for 3D plotting.
            3. Creates a LabelFrame to display discovered series of scans with dynamic buttons.
            4. Adds an entry and label for Amplitude Threshold.
            5. Adds a button for generating the 3D plot.
            6. Configures grid weights for responsive layout.

        Outputs of this function:
            None. Populates the tab with GUI elements.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # --- 3D Scans Over Time Plotting Section ---
        self.plot_3d_frame = ttk.LabelFrame(self, text="3D Scans Over Time Plotting", padding="10")
        self.plot_3d_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Open Folder for 3D Plotting Button
        self.open_folder_3d_button = ttk.Button(self.plot_3d_frame, text="Open Folder for 3D Plotting", command=self._open_folder_for_3d_plotting)
        self.open_folder_3d_button.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Discovered Series of Scans Frame for 3D plots
        self.discovered_series_3d_frame = ttk.LabelFrame(self.plot_3d_frame, text="Discovered Series of Scans (for 3D)", padding="10")
        self.discovered_series_3d_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.dynamic_3d_buttons_frame = ttk.Frame(self.discovered_series_3d_frame) # This frame will hold dynamically created buttons.
        self.dynamic_3d_buttons_frame.pack(fill="both", expand=True) # Use pack for dynamic buttons within this frame

        # Amplitude Threshold
        amplitude_threshold_frame = ttk.Frame(self.plot_3d_frame)
        amplitude_threshold_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        amplitude_threshold_frame.grid_columnconfigure(1, weight=1) # Make entry expand

        ttk.Label(amplitude_threshold_frame, text="Amplitude Threshold (dBm):", style='TLabel').grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.amplitude_threshold_var = tk.DoubleVar(self, value=-80.0) # Default threshold
        ttk.Entry(amplitude_threshold_frame, textvariable=self.amplitude_threshold_var, style='TEntry').grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        # Generate 3D Plot Button
        self.generate_plot_scans_over_time_button = ttk.Button(self.plot_3d_frame, text="Generate 3D Plot of Scans Over Time", command=self._generate_plot_scans_over_time)
        self.generate_plot_scans_over_time_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.generate_plot_scans_over_time_button.config(state=tk.DISABLED) # Disable until group is selected


        # Configure column weights for resizing
        self.grid_columnconfigure(0, weight=1)
        self.plot_3d_frame.grid_columnconfigure(0, weight=1)
        self.plot_3d_frame.grid_columnconfigure(1, weight=1)
        self.discovered_series_3d_frame.grid_columnconfigure(0, weight=1)
        self.dynamic_3d_buttons_frame.grid_columnconfigure(0, weight=1) # Ensure dynamic buttons expand

        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    def _open_folder_for_3d_plotting(self):
        """
        Function Description:
        Opens a file dialog to allow the user to select a folder containing CSV files for 3D plotting.
        Upon selection, it calls `_find_and_group_csv_files_3d` and enables relevant buttons.

        Inputs to this function:
            None.

        Process of this function:
            1. Opens a directory selection dialog, defaulting to the last opened folder.
            2. If a folder is selected, stores it as `self.last_opened_folder`.
            3. Calls `_find_and_group_csv_files_3d` to process the CSVs in the selected folder.
            4. Enables the 3D plotting button if groups are found.
            5. If no folder is selected, disables the button.

        Outputs of this function:
            None. Updates GUI state and initiates file grouping.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        folder_path = filedialog.askdirectory(initialdir=self.last_opened_folder)
        debug_log(f"Selected folder_path for 3D plotting: {folder_path}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        if folder_path:
            self.last_opened_folder = folder_path
            self.console_print_func(f"Selected folder for 3D plotting: {folder_path}")
            self._find_and_group_csv_files_3d(folder_path)
            # Enable 3D plotting button if groups are found
            if self.grouped_csv_files: # Only enable if groups were successfully found
                self.generate_plot_scans_over_time_button.config(state=tk.NORMAL)
                debug_log("3D plotting button enabled (folder selected and groups found).",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            else:
                self.generate_plot_scans_over_time_button.config(state=tk.DISABLED)
                debug_log("3D plotting button disabled (no groups found in folder).",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        else:
            self.console_print_func("Folder selection cancelled for 3D plotting.")
            self.generate_plot_scans_over_time_button.config(state=tk.DISABLED)
            debug_log("Folder selection cancelled. 3D plotting button disabled.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _find_and_group_csv_files_3d(self, folder_path):
        """
        Function Description:
        Scans the selected folder for CSV files and groups them based on a common naming prefix
        for 3D plotting. It then creates dynamic buttons for each identified group.

        Inputs to this function:
            folder_path (str): The path to the folder containing CSV files.

        Process of this function:
            1. Lists all CSV files in the given `folder_path`.
            2. If no CSVs are found, clears dynamic buttons and returns.
            3. Iterates through each CSV, attempting to extract a common prefix using regex.
               The regex is designed to be flexible, looking for a pattern before RBW/HOLD/timestamp.
            4. Stores files in `file_groups` dictionary, where keys are prefixes and values are lists of file paths.
            5. Clears any existing dynamic group selection buttons.
            6. Creates a new `ttk.Button` for each identified group, allowing the user to select it.
            7. Configures button styles.

        Outputs of this function:
            None. Populates `self.grouped_csv_files` and updates the GUI with group selection buttons.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function} with folder_path: {folder_path}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
        debug_log(f"Found CSV files for 3D plotting: {csv_files}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        if not csv_files:
            self.console_print_func("No CSV files found in the selected folder for 3D plotting. FUCK! Where did they go?!")
            self._clear_dynamic_3d_buttons()
            self.grouped_csv_files = {} # Clear groups if no files
            debug_log(f"Exiting {current_function} (no CSVs)",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        file_groups = {}
        for filename in csv_files:
            base_name = os.path.splitext(filename)[0]
            # Updated regex for grouping: be more flexible with the ending part before date/time
            # It tries to capture the main prefix before any RBW/HOLD/timestamp.
            match = re.match(r"([^\d_ -]+(?:[_ -][^\d_ -]+)*?)_RBW\d+K?_HOLD\d+.*", base_name)
            prefix = base_name # Default to full base name if no clear pattern
            if match:
                prefix = match.group(1).strip() # Get the part before RBW/HOLD
                # Refine prefix: remove trailing underscores/hyphens if they were part of the non-digit group
                prefix = re.sub(r"[_ -]+$", "", prefix)
            else:
                # Fallback if the more specific pattern doesn't match (e.g., for INTERMOD.csv or simpler names)
                # Try to split by common delimiters if no complex pattern is found
                if '_' in base_name:
                    prefix = base_name.split('_')[0]
                elif '-' in base_name:
                    prefix = base_name.split('-')[0]
                else:
                    prefix = base_name # Use full name if no common delimiters

            if not prefix: # Ensure prefix is not empty
                prefix = base_name # Fallback to full base name

            if prefix not in file_groups:
                file_groups[prefix] = []
            file_groups[prefix].append(os.path.join(folder_path, filename))
        debug_log(f"Grouped CSV files for 3D plotting: {file_groups}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        self._clear_dynamic_3d_buttons() # Clear any previous buttons

        if not file_groups:
            self.console_print_func("No identifiable groups of CSV files found for 3D plotting. This is a bloody mess!")
            self.grouped_csv_files = {} # Clear groups if no files
            debug_log(f"Exiting {current_function} (no file groups)",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        self.console_print_func(f"Found {len(file_groups)} groups of similar CSV files for 3D plotting. Let's get this show on the road!")

        self.grouped_csv_files = file_groups
        self.selected_group_prefix = None

        row_start = 0
        for i, (prefix, files) in enumerate(file_groups.items()):
            group_text = f"Group '{prefix}' ({len(files)} files)"
            btn = ttk.Button(self.dynamic_3d_buttons_frame, text=group_text,
                             command=lambda p=prefix: self._select_group_for_3d_plotting(p))
            btn.grid(row=row_start + i, column=0, padx=5, pady=2, sticky="ew")
            btn.config(style='Orange.TButton') # Use a distinct style if desired

        try:
            style = ttk.Style()
            style.configure('Orange.TButton', background='orange', foreground='black')
        except Exception as e:
            debug_log(f"Could not apply orange style for 3D plotting buttons: {e}. Damn you, Tkinter styles!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    def _select_group_for_3d_plotting(self, prefix):
        """
        Function Description:
        Sets the `selected_group_prefix` for 3D plotting and visually highlights the selected group button.

        Inputs to this function:
            prefix (str): The prefix of the selected group of files.

        Process of this function:
            1. Stores the `prefix` in `self.selected_group_prefix`.
            2. Updates the console with the selected group.
            3. Iterates through all dynamic group buttons:
               a. If the button's text matches the selected prefix, sets its relief to "sunken" and applies a "SelectedOrange.TButton" style.
               b. Otherwise, resets its relief to "raised" and applies the default "Orange.TButton" style.
            4. Attempts to configure the "SelectedOrange.TButton" style.

        Outputs of this function:
            None. Updates `self.selected_group_prefix` and GUI button appearance.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function} with prefix: {prefix}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        self.selected_group_prefix = prefix
        self.console_print_func(f"Selected group for 3D plotting: '{prefix}'")
        debug_log(f"Selected group for 3D plotting: '{prefix}'",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        for widget in self.dynamic_3d_buttons_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                if widget.cget("text").startswith(f"Group '{prefix}'"):
                    widget.config(relief="sunken", style='SelectedOrange.TButton')
                    debug_log(f"Highlighted button for group: {prefix}",
                                file=__file__,
                                version=current_version,
                                function=current_function)
                else:
                    widget.config(relief="raised", style='Orange.TButton')
        try:
            style = ttk.Style()
            style.configure('SelectedOrange.TButton', background='darkorange', foreground='white')
        except Exception as e:
            debug_log(f"Could not apply selected orange style for 3D plotting buttons: {e}. This style system is a real pain in the ass!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    def _clear_dynamic_3d_buttons(self):
        """
        Function Description:
        Destroys all dynamically created group selection buttons for 3D plotting from the GUI.

        Inputs to this function:
            None.

        Process of this function:
            1. Iterates through all child widgets in `self.dynamic_3d_buttons_frame`.
            2. Calls `destroy()` on each widget.

        Outputs of this function:
            None. Clears the dynamic button area in the GUI.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        for widget in self.dynamic_3d_buttons_frame.winfo_children():
            widget.destroy()
        debug_log(f"Cleared dynamic 3D plotting buttons.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    def _generate_plot_scans_over_time(self):
        """
        Function Description:
        Generates and opens the 3D Plotly HTML plot for scans over time.
        It utilizes the `plot_Scans_over_time` utility function.

        Inputs to this function:
            None.

        Process of this function:
            1. Checks if `grouped_csv_files` and `selected_group_prefix` are set.
            2. Retrieves the amplitude threshold from the Tkinter variable.
            3. Determines the output folder for the plot.
            4. Calls `plot_Scans_over_time` with the collected parameters.
            5. If the plot is generated successfully, logs success and optionally opens it in a browser.
            6. Logs failure messages to the console.

        Outputs of this function:
            None. Generates an HTML plot file.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if not hasattr(self, 'grouped_csv_files') or not self.grouped_csv_files:
            self.console_print_func("Warning: No data. Please select a folder and identify CSV file groups for 3D plotting first. What the hell are you trying to plot?")
            debug_log(f"Exiting {current_function} (no grouped_csv_files)",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        if not self.selected_group_prefix:
            self.console_print_func("Warning: No group selected. Please click on one of the group buttons to select files for 3D plotting. Pick one, for crying out loud!")
            debug_log(f"Exiting {current_function} (no selected_group_prefix)",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        amplitude_threshold = self.amplitude_threshold_var.get()
        output_dir = self.app_instance.output_folder_var.get() # Use the main app's output folder

        self.console_print_func(f"Generating 3D plot for group '{self.selected_group_prefix}' with threshold {amplitude_threshold} dBm. This may take some time. Don't go anywhere!")
        debug_log(f"Calling plot_Scans_over_time for group '{self.selected_group_prefix}'",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        try:
            fig, plot_html_path = plot_Scans_over_time(
                self.grouped_csv_files,
                self.selected_group_prefix,
                output_dir,
                amplitude_threshold,
                self.console_print_func
            )

            if fig:
                self.console_print_func(f"✅ 3D plot generated and saved to: {plot_html_path}. BOOM! Nailed it!")
                debug_log(f"3D plot generated and saved to: {plot_html_path}",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                if self.app_instance.open_html_after_complete_var.get():
                    self.console_print_func(f"Opening 3D plot in browser: {plot_html_path}")
                    webbrowser.open_new_tab(plot_html_path)
                    debug_log(f"3D plot opened in browser: {plot_html_path}",
                                file=__file__,
                                version=current_version,
                                function=current_function)
            else:
                self.console_print_func("🚫 3D Plotly figure was not generated. Fucking hell, not again!")
                debug_log("3D Plotly figure not generated.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        except Exception as e:
            self.console_print_func(f"❌ Error generating 3D plot: {e}. This is a nightmare!")
            debug_log(f"Error generating 3D plot: {e}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _on_tab_selected(self, event):
        """
        Function Description:
        Callback for when this tab is selected.
        This can be used to refresh data or update UI elements specific to this tab.

        Inputs to this function:
            event (tkinter.Event): The event object that triggered the tab selection.

        Process of this function:
            1. Logs a debug message indicating the tab selection.
            2. Enables/Disables the "Generate 3D Plot of Scans Over Time" button
               based on whether a folder has been opened and groups of CSV files have been identified.

        Outputs of this function:
            None. Updates the state of various GUI buttons.

        (2025-07-31) Change: Initial implementation for Plotting3DTab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        debug_log("3D Plotting Tab selected.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Enable/Disable 3D plotting button based on last_opened_folder and grouped_csv_files
        if hasattr(self, 'last_opened_folder') and self.last_opened_folder and \
           hasattr(self, 'grouped_csv_files') and self.grouped_csv_files:
            self.generate_plot_scans_over_time_button.config(state=tk.NORMAL)
            debug_log("3D plotting button enabled (folder and groups exist).",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            self.generate_plot_scans_over_time_button.config(state=tk.DISABLED)
            debug_log("3D plotting button disabled (no folder or groups).",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)