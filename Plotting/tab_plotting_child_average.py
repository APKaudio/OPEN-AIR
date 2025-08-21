# tabs/Plotting/tab_plotting_child_average.py
#
# This file defines a Tkinter Frame for plotting averaged scan data from folders.
# It handles selecting folders, grouping CSV files, generating averaged CSVs,
# and plotting various statistical analyses (Average, Median, Range, Std Dev, Variance, PSD).
# The 3D plotting functionality has been moved to tab_plotting_child_3D.py.
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
# Version 20250801.2225.1 (Refactored debug_print to use debug_log and console_log.)

current_version = "20250801.2225.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250801 * 2225 * 1 # Example hash, adjust as needed

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
from .utils_plotting import plot_multi_trace_data, _open_plot_in_browser

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

from process_math.averaging_utils import average_scan # NEW import
# Removed: from utils.plot_scans_over_time import plot_Scans_over_time # Moved to tab_plotting_child_3D.py


class AveragingTab(ttk.Frame):
    """
    A Tkinter Frame that provides functionality for plotting averaged scan data from folders.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the AveragingTab.

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
        self.current_plot_file = None # To store the path of the last generated plot HTML
        self.last_opened_folder = None # To remember the last opened folder for averaging
        self.last_applied_math_folder = None # To store the path of the last folder created by applied math
        self.grouped_csv_files = {} # Dictionary to store grouped CSV files
        self.selected_group_prefix = None # Stores the prefix of the currently selected group

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
        Creates and arranges all the widgets for the AveragingTab.

        Inputs to this function:
            None.

        Process of this function:
            1. Creates the main LabelFrame for "Plotting Averages from Folder".
            2. Adds a button to open a folder for averaging.
            3. Creates a LabelFrame to display discovered series of scans with dynamic buttons.
            4. Creates a frame for "Apply Math" checkboxes (Average, Median, etc.).
            5. Creates a frame for "Markers to Plot" checkboxes specific to averaged plots.
            6. Adds buttons for generating CSVs, opening the applied math folder,
               and generating plots of averages (with/without scans).
            7. Configures grid weights for responsive layout.

        Outputs of this function:
            None. Populates the tab with GUI elements.

        (2025-07-31) Change: Removed "Generate Plot of Scans Over Time" button.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # --- Plotting Averages from Folder Section ---
        self.averaging_folder_frame = ttk.LabelFrame(self, text="Plotting Averages from Folder", padding="10")
        self.averaging_folder_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Open Folder to Average Button (Top of this section)
        self.open_folder_button = ttk.Button(self.averaging_folder_frame, text="Open Folder to Average", command=self._open_folder_for_averaging)
        self.open_folder_button.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Discovered Series of Scans Frame
        self.discovered_series_frame = ttk.LabelFrame(self.averaging_folder_frame, text="Discovered Series of Scans", padding="10")
        self.discovered_series_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.dynamic_avg_buttons_frame = ttk.Frame(self.discovered_series_frame) # This frame will hold dynamically created buttons.
        self.dynamic_avg_buttons_frame.pack(fill="both", expand=True) # Use pack for dynamic buttons within this frame

        # Math and Markers Container Frame (for 50/50 split)
        math_and_markers_frame = ttk.Frame(self.averaging_folder_frame)
        math_and_markers_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        math_and_markers_frame.grid_columnconfigure(0, weight=1) # Make columns expandable
        math_and_markers_frame.grid_columnconfigure(1, weight=1)

        # Apply Math Frame
        apply_math_frame = ttk.LabelFrame(math_and_markers_frame, text="Apply Math", padding="10")
        apply_math_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        apply_math_frame.grid_columnconfigure(0, weight=1) # Make column expandable

        # Link to app_instance variables
        self.avg_type_vars = {
            "Average": self.app_instance.math_average_var,
            "Median": self.app_instance.math_median_var,
            "Range": self.app_instance.math_range_var,
            "Standard Deviation": self.app_instance.math_standard_deviation_var,
            "Variance": self.app_instance.math_variance_var,
            "Power Spectral Density (PSD)": self.app_instance.math_psd_var
        }

        # Tooltip definitions (example, you'd integrate a proper tooltip class)
        tooltip_texts = {
            "Average": "Calculates the arithmetic mean of power levels across all scans.",
            "Median": "Calculates the median (middle value) of power levels across all scans.",
            "Range": "Calculates the difference between the maximum and minimum power levels for each frequency point.",
            "Standard Deviation": "Measures the dispersion of power levels around the mean for each frequency point.",
            "Variance": "Measures the squared deviation from the mean, indicating the spread of power levels.",
            "Power Spectral Density (PSD)": "Normalizes power to a 1 Hz bandwidth, useful for comparing noise floors."
        }

        for i, (text, var) in enumerate(self.avg_type_vars.items()):
            chk = ttk.Checkbutton(apply_math_frame, text=text, variable=var,
                                  command=self._on_avg_type_checkbox_changed)
            chk.grid(row=i, column=0, padx=5, pady=2, sticky="w")

            # --- Tooltip Integration Suggestion ---
            # To add tooltips, you would typically use a custom Tooltip class
            # or bind to <Enter> and <Leave> events to show/hide a Label.
            # Example (conceptual, requires Tooltip class definition):
            # Tooltip(chk, text=tooltip_texts.get(text, "No description available."))
            # ------------------------------------

        # Markers to Plot Frame (Includes TV, Government, General, and Intermodulations)
        markers_to_plot_frame = ttk.LabelFrame(math_and_markers_frame, text="Markers to Plot", padding="10")
        markers_to_plot_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        markers_to_plot_frame.grid_columnconfigure(0, weight=1) # Make column expandable

        # Link to app_instance variables for average markers
        ttk.Checkbutton(markers_to_plot_frame, text="Include TV Band Markers", variable=self.app_instance.include_tv_markers_var,
                        command=self._on_multi_file_marker_checkbox_changed).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(markers_to_plot_frame, text="Include Government Band Markers", variable=self.app_instance.include_gov_markers_var,
                        command=self._on_multi_file_marker_checkbox_changed).grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(markers_to_plot_frame, text="Include Markers", variable=self.app_instance.include_markers_var,
                        command=self._on_multi_file_marker_checkbox_changed).grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(markers_to_plot_frame, text="Include Intermodulations", variable=self.app_instance.include_scan_intermod_markers_var,
                        command=self._on_multi_file_marker_checkbox_changed).grid(row=3, column=0, padx=5, pady=2, sticky="w")


        # Make Averages Frame
        make_averages_frame = ttk.LabelFrame(self.averaging_folder_frame, text="Make Averages", padding="10")
        make_averages_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        make_averages_frame.grid_columnconfigure(0, weight=1) # Make column expandable

        self.generate_csv_button = ttk.Button(make_averages_frame, text="Generate CSV of Selected Series of Scan", command=self._generate_csv_selected_series)
        self.generate_csv_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.generate_csv_button.config(state=tk.DISABLED) # Disable until group is selected

        self.open_applied_math_folder_button = ttk.Button(make_averages_frame, text="Open Folder of Applied Math", command=self._open_applied_math_folder)
        self.open_applied_math_folder_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.open_applied_math_folder_button.config(state=tk.DISABLED) # Disable until a folder is created

        self.generate_plot_averages_button = ttk.Button(make_averages_frame, text="Generate Plot of Averages", command=lambda: self._generate_multi_average_plot(include_scans=False))
        self.generate_plot_averages_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.generate_plot_averages_button.config(state=tk.DISABLED) # Disable until group is selected

        self.generate_plot_averages_with_scan_button = ttk.Button(make_averages_frame, text="Generate Plot of Averages with Scan", command=lambda: self._generate_multi_average_plot(include_scans=True))
        self.generate_plot_averages_with_scan_button.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        self.generate_plot_averages_with_scan_button.config(state=tk.DISABLED) # Disable until group is selected

        # Removed: self.generate_plot_scans_over_time_button = ttk.Button(make_averages_frame, text="Generate Plot of Scans Over Time", command=self._generate_plot_scans_over_time)
        # Removed: self.generate_plot_scans_over_time_button.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        # Removed: self.generate_plot_scans_over_time_button.config(state=tk.DISABLED) # Disable until group is selected


        # Configure column weights for resizing
        self.grid_columnconfigure(0, weight=1)
        self.averaging_folder_frame.grid_columnconfigure(0, weight=1)
        self.averaging_folder_frame.grid_columnconfigure(1, weight=1) # For the two columns inside
        self.discovered_series_frame.grid_columnconfigure(0, weight=1)
        self.dynamic_avg_buttons_frame.grid_columnconfigure(0, weight=1) # Ensure dynamic buttons expand
        make_averages_frame.grid_columnconfigure(0, weight=1)


        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    def _on_avg_type_checkbox_changed(self):
        """
        Function Description:
        Callback function for when an "Apply Math" checkbox is changed.
        It logs the currently selected average types to the console.

        Inputs to this function:
            None.

        Process of this function:
            1. Retrieves the state of all "math_average_var" Tkinter variables from app_instance.
            2. Filters out unselected types.
            3. Logs the selected types to the debug log and the GUI console.

        Outputs of this function:
            None. Updates console output.

        (2025-07-31) Change: Moved from tab_plotting_child_Single.py.
        (2025-08-01) Change: Updated debug_print to debug_log.
        """
        current_function = inspect.currentframe().f_code.co_name
        # Now directly use app_instance variables as they are linked
        selected_types = [
            "Average" if self.app_instance.math_average_var.get() else None,
            "Median" if self.app_instance.math_median_var.get() else None,
            "Range" if self.app_instance.math_range_var.get() else None,
            "Standard Deviation" if self.app_instance.math_standard_deviation_var.get() else None,
            "Variance" if self.app_instance.math_variance_var.get() else None,
            "Power Spectral Density (PSD)" if self.app_instance.math_psd_var.get() else None
        ]
        selected_types = [t for t in selected_types if t is not None]
        debug_log(f"Checkbox changed. Currently selected average types: {selected_types}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        self.console_print_func(f"Selected average types: {', '.join(selected_types) if selected_types else 'None'}")

    def _on_multi_file_marker_checkbox_changed(self):
        """
        Function Description:
        Callback function for when a "Markers to Plot" checkbox (for multi-file plots) is changed.
        It logs the currently selected marker types to the console.

        Inputs to this function:
            None.

        Process of this function:
            1. Retrieves the state of all "avg_include_..." Tkinter variables from app_instance.
            2. Builds a list of selected marker types.
            3. Logs the selected types to the debug log and the GUI console.

        Outputs of this function:
            None. Updates console output.

        (2025-07-31) Change: Moved from tab_plotting_child_Single.py.
        (2025-08-01) Change: Updated debug_print to debug_log.
        """
        current_function = inspect.currentframe().f_code.co_name
        selected_markers = []
        if self.app_instance.avg_include_tv_markers_var.get(): # NEW variable
            selected_markers.append("TV Band Markers")
        if self.app_instance.avg_include_gov_markers_var.get(): # NEW variable
            selected_markers.append("Government Band Markers")
        if self.app_instance.avg_include_markers_var.get(): # NEW variable
            selected_markers.append("General Markers")
        if self.app_instance.avg_include_intermod_markers_var.get(): # NEW variable
            selected_markers.append("Intermodulations")

        debug_log(f"Multi-File Plotting - Selected markers: {selected_markers}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        self.console_print_func(f"Multi-File Plotting - Markers: {', '.join(selected_markers) if selected_markers else 'None'}")

    def _open_folder_for_averaging(self):
        """
        Function Description:
        Opens a file dialog to allow the user to select a folder containing CSV files for averaging.
        Upon selection, it calls `_find_and_group_csv_files` and enables relevant buttons.

        Inputs to this function:
            None.

        Process of this function:
            1. Opens a directory selection dialog, defaulting to the last opened folder.
            2. If a folder is selected, stores it as `self.last_opened_folder`.
            3. Calls `_find_and_group_csv_files` to process the CSVs in the selected folder.
            4. Enables the CSV generation and plotting buttons.
            5. If no folder is selected, disables the buttons.

        Outputs of this function:
            None. Updates GUI state and initiates file grouping.

        (2025-07-31) Change: Moved from tab_plotting_child_Single.py.
        (2025-08-01) Change: Updated debug_print to debug_log.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        folder_path = filedialog.askdirectory(initialdir=self.last_opened_folder)
        debug_log(f"Selected folder_path: {folder_path}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        if folder_path:
            self.last_opened_folder = folder_path
            self.console_print_func(f"Selected folder for averaging: {folder_path}")
            self._find_and_group_csv_files(folder_path)
            # Enable relevant buttons after a folder is selected and groups are found
            self.generate_csv_button.config(state=tk.NORMAL)
            self.generate_plot_averages_button.config(state=tk.NORMAL)
            self.generate_plot_averages_with_scan_button.config(state=tk.NORMAL)
            # Removed: self.generate_plot_scans_over_time_button.config(state=tk.NORMAL)
            debug_log("Averaging buttons enabled (folder selected).",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            self.console_print_func("Folder selection cancelled.")
            # Disable buttons if folder selection is cancelled
            self.generate_csv_button.config(state=tk.DISABLED)
            self.generate_plot_averages_button.config(state=tk.DISABLED)
            self.generate_plot_averages_with_scan_button.config(state=tk.DISABLED)
            # Removed: self.generate_plot_scans_over_time_button.config(state=tk.DISABLED)
            debug_log("Folder selection cancelled. Averaging buttons disabled.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _find_and_group_csv_files(self, folder_path):
        """
        Function Description:
        Scans the selected folder for CSV files and groups them based on a common naming prefix.
        It then creates dynamic buttons for each identified group.

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

        (2025-07-31) Change: Moved from tab_plotting_child_Single.py.
        (2025-08-01) Change: Updated debug_print to debug_log.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function} with folder_path: {folder_path}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
        debug_log(f"Found CSV files: {csv_files}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        if not csv_files:
            self.console_print_func("No CSV files found in the selected folder. FUCK! Where did they go?!")
            self._clear_dynamic_buttons()
            debug_log(f"Exiting {current_function} (no CSVs)",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        file_groups = {}
        for filename in csv_files:
            base_name = os.path.splitext(filename)[0]
            # Updated regex for grouping: be more flexible with the ending part before date/time
            # It tries to capture the main prefix before any RBW/HOLD/Offset/timestamp.
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
        debug_log(f"Grouped CSV files: {file_groups}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        self._clear_dynamic_buttons() # Clear any previous buttons

        if not file_groups:
            self.console_print_func("No identifiable groups of CSV files found. This is a bloody mess!")
            debug_log(f"Exiting {current_function} (no file groups)",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        self.console_print_func(f"Found {len(file_groups)} groups of similar CSV files. Let's get this show on the road!")

        self.grouped_csv_files = file_groups
        self.selected_group_prefix = None

        row_start = 0
        for i, (prefix, files) in enumerate(file_groups.items()):
            group_text = f"Group '{prefix}' ({len(files)} files)"
            btn = ttk.Button(self.dynamic_avg_buttons_frame, text=group_text,
                             command=lambda p=prefix: self._select_group_for_plotting(p))
            btn.grid(row=row_start + i, column=0, padx=5, pady=2, sticky="ew")
            btn.config(style='Orange.TButton')

        try:
            style = ttk.Style()
            style.configure('Orange.TButton', background='orange', foreground='black')
        except Exception as e:
            debug_log(f"Could not apply orange style: {e}. Damn you, Tkinter styles!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _select_group_for_plotting(self, prefix):
        """
        Function Description:
        Sets the `selected_group_prefix` and visually highlights the selected group button.

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

        (2025-07-31) Change: Moved from tab_plotting_child_Single.py.
        (2025-08-01) Change: Updated debug_print to debug_log.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function} with prefix: {prefix}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        self.selected_group_prefix = prefix
        self.console_print_func(f"Selected group for plotting: '{prefix}'")
        debug_log(f"Selected group for plotting: '{prefix}'",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        for widget in self.dynamic_avg_buttons_frame.winfo_children():
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
            debug_log(f"Could not apply selected orange style: {e}. This style system is a real pain in the ass!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _clear_dynamic_buttons(self):
        """
        Function Description:
        Destroys all dynamically created group selection buttons from the GUI.

        Inputs to this function:
            None.

        Process of this function:
            1. Iterates through all child widgets in `self.dynamic_avg_buttons_frame`.
            2. Calls `destroy()` on each widget.

        Outputs of this function:
            None. Clears the dynamic button area in the GUI.

        (2025-07-31) Change: Moved from tab_plotting_child_Single.py.
        (2025-08-01) Change: Updated debug_print to debug_log.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        for widget in self.dynamic_avg_buttons_frame.winfo_children():
            widget.destroy()
        debug_log(f"Cleared dynamic buttons.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _generate_csv_selected_series(self):
        """
        Function Description:
        Generates CSV files containing the selected average types for the currently selected group of scans.
        It utilizes the `average_scan` utility function.

        Inputs to this function:
            None.

        Process of this function:
            1. Checks if `grouped_csv_files` and `selected_group_prefix` are set. If not, logs a warning and returns.
            2. Retrieves the list of files to average for the selected group.
            3. Retrieves the currently selected average types from `app_instance` variables.
            4. If no average types are selected, logs a warning and returns.
            5. Calls the `average_scan` function with the collected parameters.
            6. If CSV generation is successful, stores the `output_folder_path` in `self.last_applied_math_folder`
               and enables the "Open Folder of Applied Math" button. Otherwise, disables it.

        Outputs of this function:
            None. Creates CSV files and updates GUI button state.

        (2025-07-31) Change: Moved from tab_plotting_child_Single.py.
        (2025-08-01) Change: Updated debug_print to debug_log.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if not hasattr(self, 'grouped_csv_files') or not self.grouped_csv_files:
            self.console_print_func("Warning: No data. Please select a folder and identify CSV file groups first. What the hell are you trying to average?")
            debug_log(f"Exiting {current_function} (no grouped_csv_files)",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        if not self.selected_group_prefix:
            self.console_print_func("Warning: No group selected. Please click on one of the group buttons to select files for averaging. Pick one, for crying out loud!")
            debug_log(f"Exiting {current_function} (no selected_group_prefix)",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        files_to_average = self.grouped_csv_files[self.selected_group_prefix]
        debug_log(f"Files to average for selected group '{self.selected_group_prefix}': {files_to_average}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        if not files_to_average:
            self.console_print_func("Error: No files found for the selected group. This is utterly useless!")
            debug_log(f"Exiting {current_function} (files_to_average is empty)",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        # Get selected average types from app_instance variables
        selected_avg_types = [
            "Average" if self.app_instance.math_average_var.get() else None,
            "Median" if self.app_instance.math_median_var.get() else None,
            "Range" if self.app_instance.math_range_var.get() else None,
            "Standard Deviation" if self.app_instance.math_standard_deviation_var.get() else None,
            "Variance" if self.app_instance.math_variance_var.get() else None,
            "Power Spectral Density (PSD)" if self.app_instance.math_psd_var.get() else None
        ]
        selected_avg_types = [t for t in selected_avg_types if t is not None]

        debug_log(f"Selected average types BEFORE check: {selected_avg_types}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if not selected_avg_types:
            self.console_print_func("Warning: No average type selected. Please select at least one type of average to generate CSVs (e.g., Average, Median). Are you even trying?!")
            debug_log(f"Exiting {current_function} (no selected_avg_types)",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        self.console_print_func(f"Generating CSVs for selected series. This may take some time depending on the number and size of scans. Don't go anywhere!")

        output_dir_base = self.last_opened_folder # Use the folder where files were opened as base for new subfolder

        # Call the new average_scan function
        aggregated_df, output_folder_path = average_scan(
            file_paths=files_to_average,
            selected_avg_types=selected_avg_types,
            plot_title_prefix=self.selected_group_prefix,
            output_html_path_base=output_dir_base,
            console_print_func=self.console_print_func
        )

        if output_folder_path:
            self.last_applied_math_folder = output_folder_path
            self.console_print_func(f"CSV files generated in: {output_folder_path}")
            self.open_applied_math_folder_button.config(state=tk.NORMAL) # Enable the button
            self.console_print_func("🎉 CSV generation complete! Now that's what I call progress! 🎉")
        else:
            self.console_print_func("🚫 CSV generation failed. FML, this is frustrating!")
            self.open_applied_math_folder_button.config(state=tk.DISABLED)
        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _open_applied_math_folder(self):
        """
        Function Description:
        Opens the folder where the applied math (averaged CSVs and plots) were saved.
        It uses platform-specific commands to open the folder in the file explorer.

        Inputs to this function:
            None.

        Process of this function:
            1. Checks if `self.last_applied_math_folder` is set and exists.
            2. If so, attempts to open the folder using `os.startfile` (Windows),
               `subprocess.Popen(["open", ...])` (macOS), or `subprocess.Popen(["xdg-open", ...])` (Linux).
            3. If an error occurs, logs it to the console.
            4. If no folder is available, logs a message to the console.

        Outputs of this function:
            None. Opens a file explorer window.

        (2025-07-31) Change: Moved from tab_plotting_child_Single.py.
        (2025-08-01) Change: Updated debug_print to debug_log.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if self.last_applied_math_folder and os.path.exists(self.last_applied_math_folder):
            self.console_print_func(f"Opening folder: {self.last_applied_math_folder}")
            try:
                if platform.system() == "Windows":
                    os.startfile(self.last_applied_math_folder)
                elif platform.system() == "Darwin": # macOS
                    import subprocess
                    subprocess.Popen(["open", self.last_applied_math_folder])
                else: # Linux and other Unix-like systems
                    import subprocess
                    subprocess.Popen(["xdg-open", self.last_applied_math_folder])
            except Exception as e:
                self.console_print_func(f"❌ Error opening folder: {e}. Are you kidding me?!")
                debug_log(f"Error opening folder {self.last_applied_math_folder}: {e}",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        else:
            self.console_print_func("No folder of applied math available. Please generate CSVs first. What did you expect, magic?")
            debug_log("No applied math folder to open.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _generate_multi_average_plot(self, include_scans=False):
        """
        Function Description:
        Generates a plot of selected averages from the 'COMPLETE_MATH' CSV,
        optionally overlaying individual scan data.

        Inputs to this function:
            include_scans (bool): If True, individual scan data will be overlaid on the plot.

        Process of this function:
            1. Checks for the existence of `self.last_applied_math_folder` and `self.selected_group_prefix`.
            2. Constructs a path to find the `COMPLETE_MATH` CSV file within the applied math folder.
            3. Loads the `COMPLETE_MATH` CSV into a Pandas DataFrame.
            4. Filters the DataFrame to include only the selected average types for plotting.
            5. If `include_scans` is True, loads individual scan CSVs from the original folder
               and prepares them for overlay.
            6. Determines the plot title and output HTML filename.
            7. Dynamically sets the y-axis range override based on the selected average types.
            8. Calls `plot_multi_trace_data` from `utils.plotting_utils` to generate the plot.
            9. Stores the path of the generated HTML plot in `self.current_plot_file`.
            10. Logs success or failure messages to the console.

        Outputs of this function:
            None. Generates an HTML plot file and updates `self.current_plot_file`.

        (2025-07-31) Change: Moved from tab_plotting_child_Single.py.
        (2025-08-01) Change: Updated debug_print to debug_log.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function} with include_scans={include_scans}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if not self.last_applied_math_folder or not os.path.exists(self.last_applied_math_folder):
            self.console_print_func("Error: No 'Applied Math' folder found. Please generate CSVs first. What the hell are you trying to plot?")
            debug_log("No 'Applied Math' folder found.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        if not self.selected_group_prefix:
            self.console_print_func("Warning: No group selected. Please click on one of the group buttons to select files for averaging. Pick a damn group!")
            debug_log(f"Exiting {current_function} (no selected_group_prefix)",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        self.console_print_func(f"Generating plot for selected series. This may take some time depending on the number and size of scans. Patience, my friend, patience!")

        # Construct the path to the COMPLETE_MATH CSV
        complete_math_csv_pattern = os.path.join(self.last_applied_math_folder, f"COMPLETE_MATH_{self.selected_group_prefix}_MultiFileAverage_*.csv")
        complete_math_csv_files = glob.glob(complete_math_csv_pattern)

        if not complete_math_csv_files:
            self.console_print_func(f"Error: No COMPLETE_MATH CSV found in '{self.last_applied_math_folder}' for group '{self.selected_group_prefix}'. This is a nightmare!")
            debug_log(f"No COMPLETE_MATH CSV found for group '{self.selected_group_prefix}'.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        # Take the most recent COMPLETE_MATH CSV if multiple exist
        complete_math_csv_path = max(complete_math_csv_files, key=os.path.getctime)
        self.console_print_func(f"Loaded COMPLETE_MATH CSV from: {complete_math_csv_path}")
        debug_log(f"Loaded COMPLETE_MATH CSV from: {complete_math_csv_path}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        try:
            # Read the COMPLETE_MATH CSV. Assuming the first column is Frequency (Hz) and others are data.
            # Use header=True to correctly read the column names (Average, Median, etc.)
            aggregated_df = pd.read_csv(complete_math_csv_path)
            debug_log(f"Loaded aggregated_df columns: {aggregated_df.columns.tolist()}",
                        file=__file__,
                        version=current_version,
                        function=current_function)

            # Filter aggregated_df to include only selected average types for plotting
            selected_avg_types = [
                "Average" if self.app_instance.math_average_var.get() else None,
                "Median" if self.app_instance.math_median_var.get() else None,
                "Range" if self.app_instance.math_range_var.get() else None,
                "Standard Deviation" if self.app_instance.math_standard_deviation_var.get() else None,
                "Variance" if self.app_instance.math_variance_var.get() else None,
                "Power Spectral Density (PSD)" if self.app_instance.math_psd_var.get() else None
            ]
            selected_avg_types = [t for t in selected_avg_types if t is not None]

            # Map the full names back to the column names in the CSV if they are different
            # (e.g., "Standard Deviation" -> "Std Dev")
            column_name_map = {
                "Average": "Average",
                "Median": "Median",
                "Range": "Range",
                "Standard Deviation": "Std Dev",
                "Variance": "Variance",
                "Power Spectral Density (PSD)": "PSD (dBm/Hz)"
            }
            plot_columns = ['Frequency (Hz)'] + [column_name_map[t] for t in selected_avg_types if column_name_map[t] in aggregated_df.columns]

            if not plot_columns or len(plot_columns) < 2: # Need at least Frequency and one data column
                self.console_print_func("Error: No selected average types found in the loaded COMPLETE_MATH CSV for plotting. This is a goddamn travesty!")
                debug_log("No selected average types found in COMPLETE_MATH CSV.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                return

            aggregated_df_for_plot = aggregated_df[plot_columns].copy()
            debug_log(f"DataFrame for plotting (selected averages) columns: {aggregated_df_for_plot.columns.tolist()}",
                        file=__file__,
                        version=current_version,
                        function=current_function)

            individual_scan_dfs_for_overlay = []
            if include_scans:
                self.console_print_func("Loading individual scans for overlay... This better work!")
                files_to_overlay = self.grouped_csv_files[self.selected_group_prefix]
                for f_path in files_to_overlay:
                    try:
                        scan_df = pd.read_csv(f_path, header=None, names=['Frequency (Hz)', 'Power (dBm)'])
                        scan_name = os.path.splitext(os.path.basename(f_path))[0]
                        individual_scan_dfs_for_overlay.append((scan_df, scan_name))
                        debug_log(f"Loaded individual scan for overlay: {scan_name}",
                                    file=__file__,
                                    version=current_version,
                                    function=current_function)
                    except Exception as e:
                        self.console_print_func(f"Warning: Could not load individual scan {os.path.basename(f_path)} for overlay: {e}. What a pain!")
                        debug_log(f"Could not load individual scan {os.path.basename(f_path)}: {e}",
                                    file=__file__,
                                    version=current_version,
                                    function=current_function)

            # Define historical_dfs_with_names as None before the debug print
            historical_dfs_with_names = None

            plot_title_suffix = ", ".join(selected_avg_types)
            plot_title = f"{self.selected_group_prefix} - {plot_title_suffix} (Multi-File Average)"
            if include_scans:
                plot_title += " with Individual Scans"

            # Determine y_range_max_override based on selected average types
            y_range_max_override_val = 0 # Default for power plots
            # Check if any of the statistical measures are selected
            if any(avg_type in selected_avg_types for avg_type in ["Range", "Standard Deviation", "Variance", "Power Spectral Density (PSD)"]):
                y_range_max_override_val = 30 # Set to 30 for these statistical plots

            # --- DEEPER DEBUGGING FOR plot_multi_trace_data CALL ---
            debug_log(f"DEBUG: Calling plot_multi_trace_data with the following arguments:",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            debug_log(f"  aggregated_df_for_plot (shape): {aggregated_df_for_plot.shape}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            debug_log(f"  plot_title: {plot_title}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            debug_log(f"  include_tv_markers: {self.app_instance.avg_include_tv_markers_var.get()}",
                        file=__file__,
                        version=current_version,
                        function=current_function) # Use app_instance var
            debug_log(f"  include_gov_markers: {self.app_instance.avg_include_gov_markers_var.get()}",
                        file=__file__,
                        version=current_version,
                        function=current_function) # Use app_instance var
            debug_log(f"  include_markers: {self.app_instance.avg_include_markers_var.get()}",
                        file=__file__,
                        version=current_version,
                        function=current_function) # Use app_instance var
            debug_log(f"  include_intermod_markers: {self.app_instance.avg_include_intermod_markers_var.get()}",
                        file=__file__,
                        version=current_version,
                        function=current_function) # NEW
            debug_log(f"  historical_dfs_with_names: {historical_dfs_with_names is not None}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            debug_log(f"  individual_scan_dfs_with_names (count): {len(individual_scan_dfs_for_overlay) if individual_scan_dfs_for_overlay else 0}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            debug_log(f"  output_html_path: {os.path.join(self.last_applied_math_folder, f'{self.selected_group_prefix}_MultiFileAverage_Plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html')}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            debug_log(f"  y_range_max_override: {y_range_max_override_val}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            debug_log(f"  scan_data_folder: {self.last_opened_folder}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            # --- END DEEPER DEBUGGING ---

            fig, plot_html_path_return = plot_multi_trace_data(
                aggregated_df_for_plot, # Pass the filtered DataFrame
                plot_title,
                include_tv_markers=self.app_instance.avg_include_tv_markers_var.get(), # Use app_instance var
                include_gov_markers=self.app_instance.avg_include_gov_markers_var.get(), # Use app_instance var
                include_markers=self.app_instance.avg_include_markers_var.get(), # Use app_instance var
                include_intermod_markers=self.app_instance.avg_include_intermod_markers_var.get(), # NEW
                historical_dfs_with_names=None, # No historical overlays for this multi-file average from external folder
                individual_scan_dfs_with_names=individual_scan_dfs_for_overlay if include_scans else None,
                output_html_path=os.path.join(self.last_applied_math_folder, f"{self.selected_group_prefix}_MultiFileAverage_Plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"),
                y_range_min_override=None, # Let the plotting function determine min
                y_range_max_override=y_range_max_override_val, # Pass the dynamically set override
                console_print_func=self.console_print_func,
                # CORRECTED: Pass the original folder where scans were opened for MARKERS.CSV
                scan_data_folder=self.last_opened_folder
            )

            if fig:
                self.current_plot_file = plot_html_path_return
                if self.app_instance.create_html_var.get():
                    self.console_print_func(f"✅ Multi-file averaged plot saved to: {self.current_plot_file}. BOOM! Nailed it!")
                    debug_log(f"Multi-file averaged plot saved to: {self.current_plot_file}",
                                file=__file__,
                                version=current_version,
                                function=current_function)
                else:
                    self.console_print_func("✅ Multi-file averaged plot data processed (HTML not saved as per setting).")
                    debug_log("Plot data processed, HTML not saved.",
                                file=__file__,
                                version=current_version,
                                function=current_function)

                if self.app_instance.open_html_after_complete_var.get() and self.app_instance.create_html_var.get() and plot_html_path_return:
                    _open_plot_in_browser(plot_html_path_return, self.console_print_func)
            else:
                self.console_print_func("🚫 Plotly figure was not generated for multi-file averaged data. Fucking hell, not again!")
                debug_log("Plotly figure not generated for multi-file averaged data.",
                            file=__file__,
                            version=current_version,
                            function=current_function)

        except Exception as e:
            self.console_print_func(f"❌ Error generating plot: {e}. This is a nightmare!")
            debug_log(f"Error generating plot: {e}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    # Removed: _generate_plot_scans_over_time - Moved to tab_plotting_child_3D.py


    def _on_tab_selected(self, event):
        """
        Function Description:
        Callback for when this tab is selected.
        This can be used to refresh data or update UI elements specific to this tab.

        Inputs to this function:
            event (tkinter.Event): The event object that triggered the tab selection.

        Process of this function:
            1. Logs a debug message indicating the tab selection.
            2. Enables/Disables multi-file averaging buttons based on whether a folder has been opened
               and groups of CSV files have been identified.
            3. Enables/Disables the "Open Applied Math Folder" button based on whether a folder
               for applied math exists.

        Outputs of this function:
            None. Updates the state of various GUI buttons.

        (2025-07-31) Change: Moved from tab_plotting_child_Single.py and adapted for AveragingTab. Removed 3D plot button state management.
        (2025-08-01) Change: Updated debug_print to debug_log.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        debug_log("Averaging Tab selected.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Enable/Disable multi-file averaging buttons based on last_opened_folder and grouped_csv_files
        if hasattr(self, 'last_opened_folder') and self.last_opened_folder and \
           hasattr(self, 'grouped_csv_files') and self.grouped_csv_files:
            self.generate_csv_button.config(state=tk.NORMAL)
            self.generate_plot_averages_button.config(state=tk.NORMAL)
            self.generate_plot_averages_with_scan_button.config(state=tk.NORMAL)
            # Removed: self.generate_plot_scans_over_time_button.config(state=tk.NORMAL)
            debug_log("Multi-file averaging buttons enabled (folder and groups exist).",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            self.generate_csv_button.config(state=tk.DISABLED)
            self.generate_plot_averages_button.config(state=tk.DISABLED)
            self.generate_plot_averages_with_scan_button.config(state=tk.DISABLED)
            # Removed: self.generate_plot_scans_over_time_button.config(state=tk.DISABLED)
            debug_log("Multi-file averaging buttons disabled (no folder or groups).",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Enable/Disable "Open Applied Math Folder" button
        if self.last_applied_math_folder and os.path.exists(self.last_applied_math_folder):
            self.open_applied_math_folder_button.config(state=tk.NORMAL)
            debug_log("Open Applied Math Folder button enabled.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            self.open_applied_math_folder_button.config(state=tk.DISABLED)
            debug_log("Open Applied Math Folder button disabled.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
