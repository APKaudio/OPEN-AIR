# tabs/Experiments/tab_experiments_child_intermod.py
#
# This file defines the InterModTab, a Tkinter Frame for Intermodulation Distortion analysis.
# It allows users to select a markers CSV file, calculate IMD products based on various
# options (e.g., 3rd/5th order, in-band filtering), display results in a Treeview,
# and generate/open an HTML plot of the intermodulation zones.
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
# Version 20250801.2150.1 (Refactored debug_print to use debug_log and console_log.)

current_version = "20250801.2150.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250801 * 2150 * 1 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import inspect
import pandas as pd
import os
import subprocess
from typing import Dict, List, Tuple
from tkinter.font import Font
import sys

# Import the intermodulation calculation and plotting functions - CORRECTED PATHS
from process_math.calculate_intermod import multi_zone_intermods, ZoneData
from process_math.ploting_intermod_zones import plot_zones

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

class InterModTab(ttk.Frame):
    """
    A Tkinter Frame that contains controls and display for Intermodulation Distortion analysis.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the InterModTab.
        """
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log # Use console_log as default

        self.markers_file_path_var = tk.StringVar(self, value="")
        self.intermod_results_csv_path = "INTERMOD.csv"
        self.zones_dashboard_html_path = "zones_dashboard.html"

        self.filter_in_band_enabled_var = tk.BooleanVar(self, value=False)
        self.in_band_min_freq_var = tk.DoubleVar(self, value=470.0)
        self.in_band_max_freq_var = tk.DoubleVar(self, value=608.0)
        self.include_3rd_order_var = tk.BooleanVar(self, value=True)
        self.include_5th_order_var = tk.BooleanVar(self, value=True)
        self.color_code_severity_var = tk.BooleanVar(self, value=True)
        self.export_filtered_csv_var = tk.BooleanVar(self, value=True)

        # Variable to store the last loaded/generated DataFrame for sorting/plotting
        self.last_imd_df = pd.DataFrame()

        self._create_widgets()

    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Inter Mod tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log
        debug_log("Creating widgets for InterModTab...",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=1)

        # --- CSV File Selection Frame ---
        file_selection_frame = ttk.LabelFrame(self, text="Marker CSV File Selection", style='Dark.TLabelframe')
        file_selection_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        file_selection_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(file_selection_frame, text="Markers CSV Path:", style='TLabel').grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(file_selection_frame, textvariable=self.markers_file_path_var, style='TEntry', state='readonly').grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(file_selection_frame, text="Browse MARKERS.CSV", command=self._browse_markers_file, style='Blue.TButton').grid(row=0, column=2, padx=5, pady=2)

        # --- IMD Calculation Options Frame ---
        options_frame = ttk.LabelFrame(self, text="Intermodulation Calculation Options", style='Dark.TLabelframe')
        options_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        options_frame.grid_columnconfigure(0, weight=1)
        options_frame.grid_columnconfigure(1, weight=1)

        row_idx = 0
        ttk.Checkbutton(options_frame, text="Filter In-Band (MHz)", variable=self.filter_in_band_enabled_var, style='TCheckbutton').grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
        in_band_frame = ttk.Frame(options_frame, style='Dark.TFrame')
        in_band_frame.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=2)
        in_band_frame.grid_columnconfigure(0, weight=1)
        in_band_frame.grid_columnconfigure(1, weight=1)
        ttk.Label(in_band_frame, text="Min:", style='TLabel').grid(row=0, column=0, sticky="w")
        ttk.Entry(in_band_frame, textvariable=self.in_band_min_freq_var, style='TEntry', width=8).grid(row=0, column=0, sticky="e", padx=(0,5))
        ttk.Label(in_band_frame, text="Max:", style='TLabel').grid(row=0, column=1, sticky="w")
        ttk.Entry(in_band_frame, textvariable=self.in_band_max_freq_var, style='TEntry', width=8).grid(row=0, column=1, sticky="e")
        row_idx += 1

        ttk.Checkbutton(options_frame, text="Include 3rd Order IMD (2f1-f2, 2f2-f1)", variable=self.include_3rd_order_var, style='TCheckbutton').grid(row=row_idx, column=0, columnspan=2, sticky="w", padx=5, pady=2); row_idx += 1
        ttk.Checkbutton(options_frame, text="Include 5th Order IMD (3f1-2f2, 3f2-2f1)", variable=self.include_5th_order_var, style='TCheckbutton').grid(row=row_idx, column=0, columnspan=2, sticky="w", padx=5, pady=2); row_idx += 1
        ttk.Checkbutton(options_frame, text="Color-Code Plot by Severity", variable=self.color_code_severity_var, style='TCheckbutton').grid(row=row_idx, column=0, columnspan=2, sticky="w", padx=5, pady=2); row_idx += 1
        ttk.Checkbutton(options_frame, text="Export Filtered CSV", variable=self.export_filtered_csv_var, style='TCheckbutton').grid(row=row_idx, column=0, columnspan=2, sticky="w", padx=5, pady=2); row_idx += 1


        # --- Action Buttons Frame ---
        action_buttons_frame = ttk.Frame(self, style='Dark.TFrame')
        action_buttons_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        action_buttons_frame.grid_columnconfigure(0, weight=1)
        action_buttons_frame.grid_columnconfigure(1, weight=1)
        action_buttons_frame.grid_columnconfigure(2, weight=1)
        action_buttons_frame.grid_columnconfigure(3, weight=1) # Added for new buttons

        ttk.Button(action_buttons_frame, text="Calculate IMD", command=self._process_imd, style='Green.TButton').grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(action_buttons_frame, text="Open Intermod CSV", command=self._open_intermod_csv, style='Blue.TButton').grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(action_buttons_frame, text="Plot Results", command=self._plot_imd_results, style='Purple.TButton').grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ttk.Button(action_buttons_frame, text="Load Intermod CSV", command=self._load_intermod_csv, style='Orange.TButton').grid(row=0, column=3, padx=5, pady=5, sticky="ew")


        # --- Treeview for IMD Results Display ---
        results_frame = ttk.LabelFrame(self, text="Intermodulation Results (INTERMOD.csv)", style='Dark.TLabelframe')
        results_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        self.imd_treeview = ttk.Treeview(results_frame, show="headings")
        self.imd_treeview.grid(row=0, column=0, sticky="nsew")

        # Scrollbars for Treeview
        tree_scrollbar_y = ttk.Scrollbar(results_frame, orient="vertical", command=self.imd_treeview.yview)
        tree_scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.imd_treeview.configure(yscrollcommand=tree_scrollbar_y.set)

        tree_scrollbar_x = ttk.Scrollbar(results_frame, orient="horizontal", command=self.imd_treeview.xview)
        tree_scrollbar_x.grid(row=1, column=0, sticky="ew")
        self.imd_treeview.configure(xscrollcommand=tree_scrollbar_x.set)

        # Bind click event for column sorting
        self.imd_treeview.bind("<Button-1>", self._on_treeview_header_click)

        debug_log("InterModTab widgets created.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    def _browse_markers_file(self):
        """Opens a file dialog to select the MARKERS.CSV file."""
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log
        file_path = filedialog.askopenfilename(
            title="Select MARKERS.CSV",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            self.markers_file_path_var.set(file_path)
            self.console_print_func(f"Selected Markers CSV: {file_path}")
            debug_log(f"Selected Markers CSV: {file_path}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            self.console_print_func("No Markers CSV file selected.")
            debug_log("No Markers CSV file selected. What a waste of a click!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    def _parse_markers_csv(self, csv_path: str) -> ZoneData:
        """
        Parses the markers CSV file to extract zone data, including frequencies and associated devices.
        Returns:
            zones_data: dict
              Keys = zone names from 'ZONE' column
              Values = tuple of (list of (frequency, device_name) tuples, (x, y) coordinates)
        """
        import random
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log
        debug_log(f"Parsing {csv_path}...",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        zones_data = {}
        try:
            df = pd.read_csv(csv_path)

            # Ensure required columns exist
            required_columns = ["ZONE", "FREQ", "DEVICE", "NAME"]
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"CSV must contain columns: {', '.join(required_columns)}")

            for zone_name in df["ZONE"].unique():
                zone_df = df[df["ZONE"] == zone_name].dropna(subset=["FREQ"])

                # Combine DEVICE and NAME for a more descriptive device_name
                # Handle cases where DEVICE or NAME might be missing/NaN
                freq_device_pairs = []
                for _, row in zone_df.iterrows():
                    freq = row["FREQ"]
                    device = str(row["DEVICE"]) if pd.notna(row["DEVICE"]) else "Unknown Device"
                    name = str(row["NAME"]) if pd.notna(row["NAME"]) else "Unknown Name"

                    # If both DEVICE and NAME are "None - None - G10" or similar, just use the NAME
                    if "None - None" in device and "None" in name:
                        device_name = name
                    elif "None - None" in device:
                        device_name = name
                    elif "None" in name:
                        device_name = device
                    else:
                        device_name = f"{device} - {name}"

                    freq_device_pairs.append((freq, device_name))

                # Assign dummy coordinates if not available in CSV
                # You should replace this with your actual coordinate lookup if available!
                x = hash(zone_name) % 100
                y = (hash(zone_name) // 100) % 100
                zones_data[zone_name] = (freq_device_pairs, (x, y))

            self.console_print_func(f"Successfully parsed {len(zones_data)} zones from CSV.")
            debug_log(f"Parsed zones data: {zones_data}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return zones_data

        except Exception as e:
            self.console_print_func(f"❌ Failed to parse markers CSV: {e}")
            debug_log(f"Error parsing markers CSV: {e}. This CSV is a stubborn bastard!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return {}

    def _display_imd_results(self, df: pd.DataFrame):
        """Displays the intermodulation results DataFrame in the Treeview."""
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log
        debug_log(f"Displaying IMD results. DataFrame has {len(df)} rows.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Clear existing data
        for item in self.imd_treeview.get_children():
            self.imd_treeview.delete(item)

        if df.empty:
            self.console_print_func("No IMD results to display.")
            debug_log("IMD DataFrame is empty, no results to display. Fucking empty!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        # Define the desired order of columns for display
        display_columns = [
            "Zone_1", "Device_1", "Parent_Freq1",
            "Zone_2", "Device_2", "Parent_Freq2",
            "Type", "Order", "Distance", "Frequency_MHz", "Severity"
        ]

        # Ensure all display_columns exist in the DataFrame, add missing ones if necessary
        for col in display_columns:
            if col not in df.columns:
                df[col] = "N/A"

        # Set columns for Treeview
        self.imd_treeview["columns"] = display_columns
        for col in display_columns:
            self.imd_treeview.heading(col, text=col.replace('_', ' '), anchor="center")
            self.imd_treeview.column(col, width=Font().measure(col.replace('_', ' ')) + 15, anchor="center")

        # Insert data and adjust column widths
        for index, row in df.iterrows():
            try:
                values_to_insert = []
                for col in display_columns:
                    value = row[col]
                    if isinstance(value, (int, float)):
                        if col == "Frequency_MHz" or col == "Parent_Freq1" or col == "Parent_Freq2":
                            str_value = f"{value:.3f}"
                        elif col == "Distance":
                            str_value = f"{value:.2f}"
                        else:
                            str_value = str(value)
                    else:
                        str_value = str(value)

                    values_to_insert.append(str_value)

                    current_width = self.imd_treeview.column(col, "width")
                    new_width = Font().measure(str_value) + 15
                    if new_width > current_width:
                        self.imd_treeview.column(col, width=new_width)

                self.imd_treeview.insert("", "end", values=values_to_insert)
            except Exception as e:
                self.console_print_func(f"❌ Error displaying IMD row (index {index}): {row.to_dict()} - {e}")
                debug_log(f"Error inserting row into Treeview (index {index}): {row.to_dict()} - {e}. This row is a pain in the ass!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                continue
        self.console_print_func(f"Displayed {len(df)} IMD products.")
        self.last_imd_df = df.copy()


    def _process_imd(self):
        """
        Initiates the IMD calculation and plot generation based on selected options.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log
        self.console_print_func("\n--- Starting IMD Calculation & Plot Generation ---")
        debug_log("Starting IMD Calculation & Plot Generation...",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        markers_csv_path = self.markers_file_path_var.get()
        if not markers_csv_path or not os.path.exists(markers_csv_path):
            self.console_print_func("Error: Please select a valid MARKERS.CSV file first.")
            debug_log("No valid Markers CSV selected. Fucking useless!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        try:
            # 1. Parse Markers CSV to ZoneData
            zones = self._parse_markers_csv(markers_csv_path)
            if not zones:
                self.console_print_func("IMD calculation aborted due to empty or invalid zone data.")
                debug_log("Empty or invalid zone data after parsing. What the hell?!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                return

            # Determine output paths relative to the markers CSV
            output_dir = os.path.dirname(markers_csv_path)
            intermod_csv_output = os.path.join(output_dir, self.intermod_results_csv_path)
            zones_html_output = os.path.join(output_dir, self.zones_dashboard_html_path)

            # 2. Calculate Intermodulation Products
            self.console_print_func("Calculating intermodulation products...")
            debug_log(f"Calling multi_zone_intermods with zones: {zones}",
                        file=__file__,
                        version=current_version,
                        function=current_function)

            imd_results_df = multi_zone_intermods(
                zones=zones,
                include_cross_zone=True,
                export_csv=intermod_csv_output,
                filter_in_band=self.filter_in_band_enabled_var.get(),
                in_band_min_freq=self.in_band_min_freq_var.get(),
                in_band_max_freq=self.in_band_max_freq_var.get(),
                include_3rd_order=self.include_3rd_order_var.get(),
                include_5th_order=self.include_5th_order_var.get()
            )
            debug_log(f"multi_zone_intermods returned DataFrame. Type: {type(imd_results_df)}, Shape: {imd_results_df.shape}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            debug_log(f"First 5 rows of IMD DataFrame:\n{imd_results_df.head().to_string()}",
                        file=__file__,
                        version=current_version,
                        function=current_function)


            self.console_print_func(f"IMD calculation complete. Results saved to: {intermod_csv_output}")
            self.console_print_func(f"Total IMD products found (after filters): {len(imd_results_df)}")

            # 3. Display results in Treeview
            self._display_imd_results(imd_results_df)
            self.console_print_func("✅ IMD analysis results displayed.")

            self.console_print_func("--- IMD Analysis Complete! ---")
            debug_log("IMD Analysis Complete. Fucking awesome!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        except Exception as e:
            self.console_print_func(f"❌ An error occurred during IMD analysis: {e}")
            debug_log(f"Error during IMD analysis: {e}. This bugger is being problematic!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    def _open_intermod_map(self):
        """
        Opens the generated HTML intermod map in the default web browser.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log

        markers_csv_path = self.markers_file_path_var.get()
        if not markers_csv_path:
            self.console_print_func("Error: Please select a Markers CSV file and run IMD calculation first to generate the map.")
            debug_log("No Markers CSV selected, cannot open map. Fucking useless!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        output_dir = os.path.dirname(markers_csv_path)
        html_file_path = os.path.join(output_dir, self.zones_dashboard_html_path)

        if not os.path.exists(html_file_path):
            self.console_print_func(f"Error: Intermod map HTML file not found at {html_file_path}. Please run IMD calculation first.")
            debug_log(f"HTML map not found: {html_file_path}. Where the hell is it?!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        try:
            if sys.platform == "win32":
                os.startfile(html_file_path)
            elif sys.platform == "darwin": # macOS
                subprocess.Popen(["open", html_file_path])
            else: # Linux
                subprocess.Popen(["xdg-open", html_file_path])
            self.console_print_func(f"✅ Opened Intermod Map: {html_file_path}")
            debug_log(f"Opened Intermod Map: {html_file_path}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except Exception as e:
            self.console_print_func(f"❌ Failed to open Intermod Map: {e}")
            debug_log(f"Error opening Intermod Map: {e}. This is a goddamn mess!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    def _open_intermod_csv(self):
        """
        Opens the generated INTERMOD.csv file in the default associated application.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log

        markers_csv_path = self.markers_file_path_var.get()
        if not markers_csv_path:
            self.console_print_func("Error: Please select a Markers CSV file and run IMD calculation first to generate the CSV.")
            debug_log("No Markers CSV selected, cannot open intermod CSV. Fucking useless!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        output_dir = os.path.dirname(markers_csv_path)
        csv_file_path = os.path.join(output_dir, self.intermod_results_csv_path)

        if not os.path.exists(csv_file_path):
            self.console_print_func(f"Error: Intermod CSV file not found at {csv_file_path}. Please run IMD calculation first.")
            debug_log(f"Intermod CSV file not found: {csv_file_path}. Where the hell is it?!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        try:
            if sys.platform == "win32":
                os.startfile(csv_file_path)
            elif sys.platform == "darwin": # macOS
                subprocess.Popen(["open", csv_file_path])
            else: # Linux
                subprocess.Popen(["xdg-open", csv_file_path])
            self.console_print_func(f"✅ Opened Intermod CSV: {csv_file_path}")
            debug_log(f"Opened Intermod CSV: {csv_file_path}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except Exception as e:
            self.console_print_func(f"❌ Failed to open Intermod CSV: {e}")
            debug_log(f"Error opening Intermod CSV: {e}. This is a goddamn mess!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    def _plot_imd_results(self):
        """
        Generates and opens the Plotly HTML dashboard based on the last calculated/loaded IMD results.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log

        if self.last_imd_df.empty:
            self.console_print_func("Error: No IMD results available to plot. Please calculate or load results first.")
            debug_log("No IMD data to plot. Fucking empty!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        markers_csv_path = self.markers_file_path_var.get()
        if not markers_csv_path or not os.path.exists(markers_csv_path):
            self.console_print_func("Error: Markers CSV path is required to generate the plot (for zone coordinates). Please select it.")
            debug_log("Markers CSV path missing for plotting. Fucking useless!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        try:
            zones = self._parse_markers_csv(markers_csv_path)
            if not zones:
                self.console_print_func("Error: Cannot plot without valid zone data from Markers CSV.")
                debug_log("No zones parsed for plotting. What the hell?!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                return

            output_dir = os.path.dirname(markers_csv_path)
            zones_html_output = os.path.join(output_dir, self.zones_dashboard_html_path)

            self.console_print_func("Generating Plotly dashboard...")
            plot_zones(
                zones=zones,
                imd_df=self.last_imd_df,
                html_filename=zones_html_output,
                color_code_severity=self.color_code_severity_var.get()
            )
            self.console_print_func(f"Plotly dashboard generated: {zones_html_output}")
            self._open_intermod_map() # Reuse existing method to open the HTML
            self.console_print_func("✅ Intermodulation map opened in browser.")

        except Exception as e:
            self.console_print_func(f"❌ An error occurred during plot generation: {e}")
            debug_log(f"Error during plot generation: {e}. This bugger is being problematic!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    def _load_intermod_csv(self):
        """
        Loads an existing INTERMOD.csv file into the Treeview for display and makes it available for plotting.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log

        file_path = filedialog.askopenfilename(
            title="Select Intermod Results CSV",
            filetypes=[("CSV files", "*.csv")],
            initialdir=os.path.dirname(self.markers_file_path_var.get()) if self.markers_file_path_var.get() else os.getcwd()
        )
        if not file_path:
            self.console_print_func("No Intermod CSV file selected for loading.")
            debug_log("No Intermod CSV selected for loading. Fucking useless!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        try:
            df = pd.read_csv(file_path)
            self._display_imd_results(df)
            self.console_print_func(f"✅ Loaded IMD results from: {file_path}")
            debug_log(f"Loaded IMD results from: {file_path}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except Exception as e:
            self.console_print_func(f"❌ Failed to load Intermod CSV: {e}")
            debug_log(f"Error loading Intermod CSV: {e}. This CSV is a stubborn bastard!",
                        file=__file__,
                        version=current_version,
                        function=current_function)


    def _on_treeview_header_click(self, event):
        """
        Handles clicks on Treeview column headers to sort the data.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log

        region = self.imd_treeview.identify("region", event.x, event.y)
        if region == "heading":
            col = self.imd_treeview.identify_column(event.x)
            column_id = int(col.replace('#', '')) - 1

            if 0 <= column_id < len(self.imd_treeview["columns"]):
                column_name = self.imd_treeview["columns"][column_id]
                debug_log(f"Header '{column_name}' clicked for sorting.",
                            file=__file__,
                            version=current_version,
                            function=current_function)

                if not hasattr(self, '_sort_order'):
                    self._sort_order = {}

                current_sort_order = self._sort_order.get(column_name, 'ascending')
                new_sort_order = 'descending' if current_sort_order == 'ascending' else 'ascending'
                self._sort_order[column_name] = new_sort_order

                self._sort_treeview(column_name, new_sort_order)
            else:
                debug_log(f"Clicked column ID {column_id} is out of bounds for current columns. What the hell?!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        else:
            debug_log(f"Click not on heading region: {region}. Fucking useless click!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    def _sort_treeview(self, col_name, order):
        """
        Sorts the Treeview content by the given column and order.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log
        debug_log(f"Sorting Treeview by column '{col_name}' in '{order}' order.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if self.last_imd_df.empty:
            self.console_print_func("No data to sort.")
            debug_log("No data in last_imd_df to sort. Fucking empty!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        if col_name not in self.last_imd_df.columns:
            self.console_print_func(f"Error: Cannot sort by column '{col_name}' as it does not exist in the data.")
            debug_log(f"Column '{col_name}' not found for sorting. What the hell?!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        ascending = (order == 'ascending')

        numeric_cols = ["Frequency_MHz", "Parent_Freq1", "Parent_Freq2", "Distance"]
        for num_col in numeric_cols:
            if num_col in self.last_imd_df.columns:
                self.last_imd_df[num_col] = pd.to_numeric(self.last_imd_df[num_col], errors='coerce')

        sorted_df = self.last_imd_df.sort_values(by=col_name, ascending=ascending, na_position='last')

        self._display_imd_results(sorted_df)
        self.console_print_func(f"Sorted results by '{col_name}' ({order}).")

    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Can be used to refresh data or update UI elements specific to this tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        # current_file will be derived from __file__ in debug_log
        debug_log("Inter Mod Tab selected.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
