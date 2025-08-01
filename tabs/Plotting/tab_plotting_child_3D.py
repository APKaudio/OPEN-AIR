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
#
#
# Version 20250801.1044.1 (Updated header and imports for new folder structure)

current_version = "20250801.1044.1" # this variable should always be defined below the header to make the debugging better

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
from tabs.Plotting.utils_plotting import _open_plot_in_browser
from tabs.Plotting.utils_plotting_scans_over_time import plot_Scans_over_time # NEW import for 3D plot

from utils.utils_instrument_control import debug_print


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
        self.console_print_func = console_print_func if console_print_func else print # Use provided func or print
        self.current_plot_file = None # To store the path of the last generated plot HTML
        self.last_opened_folder = None # To remember the last opened folder for 3D plotting
        self.grouped_csv_files = {} # Dictionary to store grouped CSV files
        self.selected_group_prefix = None # Stores the prefix of the currently selected group

        current_function = inspect.currentframe().f_code.co_name
        current_file = f"tabs/tab_plotting_child_3D.py - {current_version}"
        debug_print(f"Entering {current_function}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        self._create_widgets()
        debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=self.console_print_func)

    def _create_widgets(self):
        """
        Function Description:
        Creates and arranges all the widgets for the Plotting3DTab.

        Inputs to this function:
            None.

        Process of this function:
            1. Creates the main LabelFrame for "3D Plotting - Scans Over Time".
            2. Adds a button to open a folder containing scan data.
            3. Creates a LabelFrame to display discovered series of scans with dynamic buttons.
            4. Adds a button to generate the 3D plot of scans over time.
            5. Adds a button to open the last generated plot.
            6. Configures grid weights for responsive layout.

        Outputs of this function:
            None. Populates the tab with GUI elements.

        (2025-07-31) Change: Initial widget creation for Plotting3DTab.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"tabs/tab_plotting_child_3D.py - {current_version}"
        debug_print(f"Entering {current_function}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # --- 3D Plotting - Scans Over Time Section ---
        self.plotting_3d_frame = ttk.LabelFrame(self, text="3D Plotting - Scans Over Time", padding="10")
        self.plotting_3d_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Open Folder for 3D Plotting Button (Top of this section)
        self.open_folder_button = ttk.Button(self.plotting_3d_frame, text="Open Folder for 3D Plotting", command=self._open_folder_for_3d_plotting)
        self.open_folder_button.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Discovered Series of Scans Frame
        self.discovered_series_frame = ttk.LabelFrame(self.plotting_3d_frame, text="Discovered Series of Scans", padding="10")
        self.discovered_series_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.dynamic_group_buttons_frame = ttk.Frame(self.discovered_series_frame) # This frame will hold dynamically created buttons.
        self.dynamic_group_buttons_frame.pack(fill="both", expand=True) # Use pack for dynamic buttons within this frame

        # Plotting Buttons
        self.generate_plot_scans_over_time_button = ttk.Button(self.plotting_3d_frame, text="Generate 3D Plot of Scans Over Time", command=self._generate_plot_scans_over_time)
        self.generate_plot_scans_over_time_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.generate_plot_scans_over_time_button.config(state=tk.DISABLED) # Disable until group is selected

        self.open_last_plot_button = ttk.Button(self.plotting_3d_frame, text="Open Last Plot", command=self._open_last_plot)
        self.open_last_plot_button.grid(row=3, column=0, padx=5, pady=5, sticky="ew")


        # Configure column weights for resizing
        self.grid_columnconfigure(0, weight=1)
        self.plotting_3d_frame.grid_columnconfigure(0, weight=1)
        self.plotting_3d_frame.grid_columnconfigure(1, weight=1) # For the two columns inside
        self.discovered_series_frame.grid_columnconfigure(0, weight=1)
        self.dynamic_group_buttons_frame.grid_columnconfigure(0, weight=1) # Ensure dynamic buttons expand


        debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=self.console_print_func)

    def _open_folder_for_3d_plotting(self):
        """
        Function Description:
        Opens a file dialog to allow the user to select a folder containing CSV files for 3D plotting.
        Upon selection, it calls `_find_and_group_csv_files` and enables relevant buttons.

        Inputs to this function:
            None.

        Process of this function:
            1. Opens a directory selection dialog, defaulting to the last opened folder.
            2. If a folder is selected, stores it as `self.last_opened_folder`.
            3. Calls `_find_and_group_csv_files` to process the CSVs in the selected folder.
            4. Enables the 3D plot generation button.
            5. If no folder is selected, disables the button.

        Outputs of this function:
            None. Updates GUI state and initiates file grouping.

        (2025-07-31) Change: Adapted from _open_folder_for_averaging in tab_plotting_child_Average.py.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"tabs/tab_plotting_child_3D.py - {current_version}"
        debug_print(f"Entering {current_function}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        folder_path = filedialog.askdirectory(initialdir=self.last_opened_folder)
        debug_print(f"Selected folder_path: {folder_path}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        if folder_path:
            self.last_opened_folder = folder_path
            self.console_print_func(f"Selected folder for 3D plotting: {folder_path}")
            self._find_and_group_csv_files(folder_path)
            # Enable relevant buttons after a folder is selected and groups are found
            self.generate_plot_scans_over_time_button.config(state=tk.NORMAL)
            debug_print("3D plotting button enabled (folder selected).", file=current_file, function=current_function, console_print_func=self.console_print_func)
        else:
            self.console_print_func("Folder selection cancelled. No 3D plot for you, you coward!")
            # Disable buttons if folder selection is cancelled
            self.generate_plot_scans_over_time_button.config(state=tk.DISABLED)
            debug_print("Folder selection cancelled. 3D plotting button disabled.", file=current_file, function=current_function, console_print_func=self.console_print_func)
        debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=self.console_print_func)


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

        (2025-07-31) Change: Adapted from _find_and_group_csv_files in tab_plotting_child_Average.py.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"tabs/tab_plotting_child_3D.py - {current_version}"
        debug_print(f"Entering {current_function} with folder_path: {folder_path}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
        debug_print(f"Found CSV files: {csv_files}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        if not csv_files:
            self.console_print_func("No CSV files found in the selected folder. FUCK! Where did they go?!")
            self._clear_dynamic_buttons()
            debug_print(f"Exiting {current_function} (no CSVs)", file=current_file, function=current_function, console_print_func=self.console_print_func)
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
        debug_print(f"Grouped CSV files: {file_groups}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        self._clear_dynamic_buttons() # Clear any previous buttons

        if not file_groups:
            self.console_print_func("No identifiable groups of CSV files found. This is a bloody mess!")
            debug_print(f"Exiting {current_function} (no file groups)", file=current_file, function=current_function, console_print_func=self.console_print_func)
            return

        self.console_print_func(f"Found {len(file_groups)} groups of similar CSV files. Let's get this show on the road!")

        self.grouped_csv_files = file_groups
        self.selected_group_prefix = None

        row_start = 0
        for i, (prefix, files) in enumerate(file_groups.items()):
            group_text = f"Group '{prefix}' ({len(files)} files)"
            btn = ttk.Button(self.dynamic_group_buttons_frame, text=group_text,
                             command=lambda p=prefix: self._select_group_for_plotting(p))
            btn.grid(row=row_start + i, column=0, padx=5, pady=2, sticky="ew")
            btn.config(style='Orange.TButton')

        try:
            style = ttk.Style()
            style.configure('Orange.TButton', background='orange', foreground='black')
        except Exception as e:
            debug_print(f"Could not apply orange style: {e}. Damn you, Tkinter styles!", file=current_file, function=current_function, console_print_func=self.console_print_func)
        debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=self.console_print_func)


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

        (2025-07-31) Change: Adapted from _select_group_for_plotting in tab_plotting_child_Average.py.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"tabs/tab_plotting_child_3D.py - {current_version}"
        debug_print(f"Entering {current_function} with prefix: {prefix}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        self.selected_group_prefix = prefix
        self.console_print_func(f"Selected group for 3D plotting: '{prefix}'")
        debug_print(f"Selected group for 3D plotting: '{prefix}'", file=current_file, function=current_function, console_print_func=self.console_print_func)

        for widget in self.dynamic_group_buttons_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                if widget.cget("text").startswith(f"Group '{prefix}'"):
                    widget.config(relief="sunken", style='SelectedOrange.TButton')
                    debug_print(f"Highlighted button for group: {prefix}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                else:
                    widget.config(relief="raised", style='Orange.TButton')
        try:
            style = ttk.Style()
            style.configure('SelectedOrange.TButton', background='darkorange', foreground='white')
        except Exception as e:
            debug_print(f"Could not apply selected orange style: {e}. This style system is a real pain in the ass!", file=current_file, function=current_function, console_print_func=self.console_print_func)
        debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def _clear_dynamic_buttons(self):
        """
        Function Description:
        Destroys all dynamically created group selection buttons from the GUI.

        Inputs to this function:
            None.

        Process of this function:
            1. Iterates through all child widgets in `self.dynamic_group_buttons_frame`.
            2. Calls `destroy()` on each widget.

        Outputs of this function:
            None. Clears the dynamic button area in the GUI.

        (2025-07-31) Change: Adapted from _clear_dynamic_buttons in tab_plotting_child_Average.py.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"tabs/tab_plotting_child_3D.py - {current_version}"
        debug_print(f"Entering {current_function}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        for widget in self.dynamic_group_buttons_frame.winfo_children():
            widget.destroy()
        debug_print(f"Cleared dynamic buttons.", file=current_file, function=current_function, console_print_func=self.console_print_func)
        debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def _generate_plot_scans_over_time(self):
        """
        Function Description:
        Generates a 3D plot of scans over time for the currently selected group of CSV files.

        Inputs to this function:
            None.

        Process of this function:
            1. Checks if `grouped_csv_files` and `selected_group_prefix` are set.
            2. Retrieves the list of files to plot from the selected group.
            3. Loads each individual scan CSV into a DataFrame, performing data validation.
            4. If no valid scan data is found, logs an error and returns.
            5. Constructs the plot title and output HTML filename.
            6. Calls `plot_Scans_over_time` from `utils.plot_scans_over_time` to generate the 3D plot.
            7. Stores the path of the generated HTML plot in `self.current_plot_file`.
            8. Logs success or failure messages to the console and optionally opens the plot in a browser.

        Outputs of this function:
            None. Generates a 3D HTML plot file and updates `self.current_plot_file`.

        (2025-07-31) Change: Moved from tab_plotting_child_Average.py.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"tabs/tab_plotting_child_3D.py - {current_version}"
        debug_print(f"Entering {current_function}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        if not hasattr(self, 'grouped_csv_files') or not self.grouped_csv_files:
            self.console_print_func("Warning: No data. Please select a folder and identify CSV file groups first. Where are the damn files?!")
            debug_print(f"Exiting {current_function} (no grouped_csv_files)", file=current_file, function=current_function, console_print_func=self.console_print_func)
            return

        if not self.selected_group_prefix:
            self.console_print_func("Warning: No group selected. Please click on one of the group buttons to select files for plotting over time. Pick a group, you numbskull!")
            debug_print(f"Exiting {current_function} (no selected_group_prefix)", file=current_file, function=current_function, console_print_func=self.console_print_func)
            return

        files_to_plot = self.grouped_csv_files[self.selected_group_prefix]
        debug_print(f"Files to plot over time for selected group '{self.selected_group_prefix}': {files_to_plot}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        if not files_to_plot:
            self.console_print_func("Error: No files found for the selected group to plot over time. This is just great!")
            debug_print(f"Exiting {current_function} (files_to_plot is empty)", file=current_file, function=current_function, console_print_func=self.console_print_func)
            return

        self.console_print_func(f"Generating 3D plot of scans over time for selected series. This may take some time depending on the number and size of scans. Don't touch anything!")

        individual_scan_dfs_with_names = []
        for f_path in files_to_plot:
            try:
                # Explicitly define column names and data types, assuming no header.
                # Use 'Frequency (MHz)' directly as the column name.
                scan_df = pd.read_csv(f_path, header=None, names=['Frequency (MHz)', 'Power (dBm)'],
                                      dtype={'Frequency (MHz)': float, 'Power (dBm)': float})
                
                debug_print(f"DEBUG: After reading {os.path.basename(f_path)}: df_scan.empty={scan_df.empty}, columns={scan_df.columns.tolist()}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                debug_print(f"DEBUG: First 5 rows of {os.path.basename(f_path)}:\n{scan_df.head()}", file=current_file, function=current_function, console_print_func=self.console_print_func)

                # Validate DataFrame content after reading
                if scan_df.empty:
                    self.console_print_func(f"Warning: Skipping scan '{os.path.basename(f_path)}' due to empty DataFrame after read. What a waste of time!")
                    debug_print(f"Skipping scan '{os.path.basename(f_path)}': Empty DataFrame.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                    continue

                # Check for the explicitly named columns
                if 'Frequency (MHz)' not in scan_df.columns or 'Power (dBm)' not in scan_df.columns:
                    self.console_print_func(f"Warning: Skipping scan '{os.path.basename(f_path)}' due to missing expected columns ('Frequency (MHz)' or 'Power (dBm)'). Found columns: {scan_df.columns.tolist()}. This is infuriating!")
                    debug_print(f"Skipping scan '{os.path.basename(f_path)}': Missing expected columns.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                    continue

                # Ensure columns are numeric after potential parsing issues
                if not pd.api.types.is_numeric_dtype(scan_df['Frequency (MHz)']) or \
                   not pd.api.types.is_numeric_dtype(scan_df['Power (dBm)']):
                    self.console_print_func(f"Warning: Skipping scan '{os.path.basename(f_path)}' due to non-numeric data in 'Frequency (MHz)' or 'Power (dBm)' columns after parsing. Are you serious?!")
                    debug_print(f"Skipping scan '{os.path.basename(f_path)}': Non-numeric data found in essential columns.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                    continue

                scan_name = os.path.splitext(os.path.basename(f_path))[0]
                individual_scan_dfs_with_names.append((scan_df, scan_name))
                debug_print(f"Loaded individual scan for 3D plot: {scan_name}", file=current_file, function=current_function, console_print_func=self.console_print_func)
            except Exception as e:
                self.console_print_func(f"Warning: Could not load individual scan {os.path.basename(f_path)} for 3D plot. Error: {e}. What a monumental failure!")
                debug_print(f"Could not load individual scan {os.path.basename(f_path)} for 3D plot: {e}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        
        if not individual_scan_dfs_with_names:
            self.console_print_func("Error: No valid scan data found to generate 3D plot over time. This is utterly hopeless!")
            debug_print("No valid scan data for 3D plot over time.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            return

        plot_title = f"{self.selected_group_prefix} - Scans Over Time"
        output_dir = self.app_instance.output_folder_var.get()
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            debug_print(f"Created output directory: {output_dir}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        html_filename = os.path.join(output_dir, f"{self.selected_group_prefix}_ScansOverTime_Plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

        try:
            fig, plot_html_path_return = plot_Scans_over_time(
                individual_scan_dfs_with_names,
                plot_title,
                output_html_path=html_filename if self.app_instance.create_html_var.get() else None,
                console_print_func=self.console_print_func,
                scan_data_folder=self.last_opened_folder # Pass the folder where scans were opened
            )

            if fig:
                self.current_plot_file = plot_html_path_return
                if self.app_instance.create_html_var.get():
                    self.console_print_func(f"✅ 3D plot of scans over time saved to: {self.current_plot_file}. Take that, you pesky bugs!")
                    debug_print(f"3D plot of scans over time saved to: {self.current_plot_file}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                else:
                    self.console_print_func("✅ 3D plot of scans over time data processed (HTML not saved as per setting).")
                    debug_print("3D plot data processed, HTML not saved.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                
                if self.app_instance.open_html_after_complete_var.get() and self.app_instance.create_html_var.get() and plot_html_path_return:
                    _open_plot_in_browser(plot_html_path_return, self.console_print_func)
            else:
                self.console_print_func("🚫 Plotly figure was not generated for 3D scans over time. Are you kidding me?!")
                debug_print("Plotly figure not generated for 3D scans over time.", file=current_file, function=current_function, console_print_func=self.console_print_func)

        except Exception as e:
            self.console_print_func(f"❌ Error generating 3D plot of scans over time: {e}. This is truly messed up!")
            debug_print(f"Error generating 3D plot of scans over time: {e}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def _open_last_plot(self):
        """
        Function Description:
        Opens the last generated HTML plot in the default web browser.

        Inputs to this function:
            None.

        Process of this function:
            1. Checks if `self.current_plot_file` is set and the file exists.
            2. If so, opens the file in a new browser tab using `_open_plot_in_browser`.
            3. Otherwise, logs an error message to the console.

        Outputs of this function:
            None. Opens a web browser tab.

        (2025-07-31) Change: Adapted from _open_last_plot in tab_plotting_child_Single.py.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"tabs/tab_plotting_child_3D.py - {current_version}"
        debug_print(f"Entering {current_function}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        if self.current_plot_file and os.path.exists(self.current_plot_file):
            self.console_print_func(f"Opening last plot: {self.current_plot_file}")
            _open_plot_in_browser(self.current_plot_file, self.console_print_func) # Pass console_print_func
            debug_print(f"Opened last plot: {self.current_plot_file}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        else:
            self.console_print_func("Error: No plot available or file not found. Please generate a plot first. What's the point of this button then?!")
            debug_print("No plot available or file not found.", file=current_file, function=current_function, console_print_func=self.console_print_func)
        debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=self.console_print_func)

    def _on_tab_selected(self, event):
        """
        Function Description:
        Callback for when this tab is selected.
        This can be used to refresh data or update UI elements specific to this tab.

        Inputs to this function:
            event (tkinter.Event): The event object that triggered the tab selection.

        Process of this function:
            1. Logs a debug message indicating the tab selection.
            2. Enables/Disables the 3D plotting button based on whether a folder has been opened
               and groups of CSV files have been identified.

        Outputs of this function:
            None. Updates the state of various GUI buttons.

        (2025-07-31) Change: Initial implementation for Plotting3DTab.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"tabs/tab_plotting_child_3D.py - {current_version}"
        debug_print(f"Entering {current_function}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        debug_print("3D Plotting Tab selected.", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Enable/Disable 3D plotting button based on last_opened_folder and grouped_csv_files
        if hasattr(self, 'last_opened_folder') and self.last_opened_folder and \
           hasattr(self, 'grouped_csv_files') and self.grouped_csv_files:
            self.generate_plot_scans_over_time_button.config(state=tk.NORMAL)
            debug_print("3D plotting button enabled (folder and groups exist).", file=current_file, function=current_function, console_print_func=self.console_print_func)
        else:
            self.generate_plot_scans_over_time_button.config(state=tk.DISABLED)
            debug_print("3D plotting button disabled (no folder or groups).", file=current_file, function=current_function, console_print_func=self.console_print_func)

        debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=self.console_print_func)
