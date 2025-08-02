# tabs/Plotting/tab_plotting_child_Single.py
#
# This file defines a Tkinter Frame that provides functionality for plotting single scan data
# and current cycle averaged data. It handles file selection, plotting options,
# and opening generated HTML plots.
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
# Version 20250801.2230.1 (Refactored debug_print to use debug_log and console_log.)

current_version = "20250801.2230.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250801 * 2230 * 1 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import pandas as pd
import inspect
import webbrowser # For opening HTML plot in browser
from datetime import datetime # Import datetime for timestamping plots
import numpy as np # Added for PSD calculation in _plot_current_cycle_average

# CORRECTED: Import plotting functions and _open_plot_in_browser directly from utils.utils_plotting
from tabs.Plotting.utils_plotting import plot_single_scan_data, plot_multi_trace_data, _open_plot_in_browser

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Removed: from process_math.averaging_utils import average_scan
# Removed: from utils.plot_scans_over_time import plot_Scans_over_time


class PlottingTab(ttk.Frame):
    """
    A Tkinter Frame that provides functionality for plotting single scan data and current cycle averages.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the PlottingTab.

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
        # Removed: self.last_opened_folder = None # No longer needed here
        # Removed: self.last_applied_math_folder = None # No longer needed here

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
        Creates and arranges all the widgets for the PlottingTab.

        Inputs to this function:
            None.

        Process of this function:
            1. Creates the main LabelFrame for "SCAN Plotting Options".
            2. Adds HTML Output Options (checkboxes for creating and opening HTML).
            3. Adds Scan Markers to Plot options (checkboxes for various markers).
            4. Adds buttons for plotting a single scan, plotting current cycle average,
               and opening the last generated plot.
            5. Configures grid weights for responsive layout.

        Outputs of this function:
            None. Populates the tab with GUI elements.

        (2025-07-31) Change: Removed "Plotting Averages from Folder" section.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # SCAN Plotting Options Frame (for single scan and current cycle average)
        plotting_options_frame = ttk.LabelFrame(self, text="SCAN Plotting Options", padding="10")
        plotting_options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Inner frame for 50/50 split
        scan_options_inner_frame = ttk.Frame(plotting_options_frame)
        scan_options_inner_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew", columnspan=2)
        scan_options_inner_frame.grid_columnconfigure(0, weight=1)
        scan_options_inner_frame.grid_columnconfigure(1, weight=1)

        # Left 50% - HTML Output Options
        html_output_options_frame = ttk.LabelFrame(scan_options_inner_frame, text="HTML Output Options", padding="10")
        html_output_options_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        html_output_options_frame.grid_columnconfigure(0, weight=1)

        # Link to app_instance variables
        ttk.Checkbutton(html_output_options_frame, text="Plot the HTML after every scan", variable=self.app_instance.open_html_after_complete_var).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(html_output_options_frame, text="Create HTML", variable=self.app_instance.create_html_var,
                        command=self._on_create_html_checkbox_changed).grid(row=1, column=0, padx=5, pady=2, sticky="w")


        # Right 50% - Scan Markers to Plot
        scan_markers_to_plot_frame = ttk.LabelFrame(scan_options_inner_frame, text="Scan Markers to Plot", padding="10")
        scan_markers_to_plot_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        scan_markers_to_plot_frame.grid_columnconfigure(0, weight=1)

        # Link to app_instance variables
        ttk.Checkbutton(scan_markers_to_plot_frame, text="Include TV Band Markers", variable=self.app_instance.include_tv_markers_var,
                        command=self._on_scan_marker_checkbox_changed).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(scan_markers_to_plot_frame, text="Include Government Band Markers", variable=self.app_instance.include_gov_markers_var,
                        command=self._on_scan_marker_checkbox_changed).grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(scan_markers_to_plot_frame, text="Include Markers", variable=self.app_instance.include_markers_var,
                        command=self._on_scan_marker_checkbox_changed).grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(scan_markers_to_plot_frame, text="Include Intermodulations", variable=self.app_instance.include_scan_intermod_markers_var,
                        command=self._on_scan_marker_checkbox_changed).grid(row=3, column=0, padx=5, pady=2, sticky="w")


        # Plotting Buttons below the split frames
        self.plot_button = ttk.Button(plotting_options_frame, text="Plot Single Scan", command=self._plot_single_scan)
        self.plot_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew") # Adjusted row
        # self.plot_button.config(state=tk.DISABLED) # This line is commented out, so it's not disabled here.

        self.plot_average_button = ttk.Button(plotting_options_frame, text="Plot Current Cycle Average (All Traces)", command=self._plot_current_cycle_average)
        self.plot_average_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew") # Adjusted row
        self.plot_average_button.config(state=tk.DISABLED) # Disable until data is available

        self.open_last_plot_button = ttk.Button(plotting_options_frame, text="Open Last Plot", command=self._open_last_plot)
        self.open_last_plot_button.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

        # Configure column weights for resizing
        self.grid_columnconfigure(0, weight=1)
        plotting_options_frame.grid_columnconfigure(0, weight=1)

        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    # Removed: _on_avg_type_checkbox_changed - moved to tab_plotting_child_Average.py

    def _on_create_html_checkbox_changed(self):
        """
        Function Description:
        Callback function for when the "Create HTML" checkbox is changed.
        It logs the current state of the checkbox to the console.

        Inputs to this function:
            None.

        Process of this function:
            1. Retrieves the boolean state of `self.app_instance.create_html_var`.
            2. Logs the state to the debug log and the GUI console.

        Outputs of this function:
            None. Updates console output.

        (2025-07-31) Change: Maintained in tab_plotting_child_Single.py.
        (2025-08-01) Change: Updated debug_print to debug_log.
        """
        current_function = inspect.currentframe().f_code.co_name
        state = "Enabled" if self.app_instance.create_html_var.get() else "Disabled"
        debug_log(f"Create HTML checkbox changed. State: {state}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        self.console_print_func(f"Create HTML: {state}")


    def _on_scan_marker_checkbox_changed(self):
        """
        Function Description:
        Callback function for when a "Scan Markers to Plot" checkbox is changed.
        It logs the currently selected marker types for single scan plots to the console.

        Inputs to this function:
            None.

        Process of this function:
            1. Retrieves the state of all `include_..._markers_var` Tkinter variables from `app_instance`.
            2. Builds a list of selected marker types.
            3. Logs the selected types to the debug log and the GUI console.

        Outputs of this function:
            None. Updates console output.

        (2025-07-31) Change: Maintained in tab_plotting_child_Single.py.
        (2025-08-01) Change: Updated debug_print to debug_log.
        """
        current_function = inspect.currentframe().f_code.co_name
        selected_markers = []
        if self.app_instance.include_tv_markers_var.get():
            selected_markers.append("TV Band Markers")
        if self.app_instance.include_gov_markers_var.get():
            selected_markers.append("Government Band Markers")
        if self.app_instance.include_markers_var.get():
            selected_markers.append("General Markers")
        if self.app_instance.include_scan_intermod_markers_var.get(): # NEW variable
            selected_markers.append("Intermodulations")

        debug_log(f"SCAN Plotting Options - Selected markers: {selected_markers}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        self.console_print_func(f"SCAN Plotting Options - Markers: {', '.join(selected_markers) if selected_markers else 'None'}")

    # Removed: _on_multi_file_marker_checkbox_changed - moved to tab_plotting_child_Average.py


    def _plot_single_scan(self):
        """
        Function Description:
        Prompts the user to select a single CSV file and then plots its scan data.

        Inputs to this function:
            None.

        Process of this function:
            1. Opens a file dialog to select a CSV file.
            2. If a file is selected, reads it into a Pandas DataFrame.
            3. Determines the output directory and HTML filename for the plot.
            4. Calls `plot_single_scan_data` from `utils.plotting_utils` to generate the plot.
            5. Stores the path of the generated HTML plot in `self.current_plot_file`.
            6. Logs success or failure messages to the console and optionally opens the plot in a browser.

        Outputs of this function:
            None. Generates an HTML plot file and updates `self.current_plot_file`.

        (2025-07-31) Change: Maintained in tab_plotting_child_Single.py.
        (2025-08-01) Change: Updated debug_print to debug_log.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        file_path = filedialog.askopenfilename(
            title="Select a CSV file to plot",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            self.console_print_func("File selection cancelled. No single scan plot generated. Damn it!")
            debug_log("File selection cancelled for single plot.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        try:
            df = pd.read_csv(file_path, header=None, names=['Frequency (Hz)', 'Power (dBm)']) # Ensure column names match plot_logic
            scan_name = os.path.splitext(os.path.basename(file_path))[0]
            self.console_print_func(f"Plotting single scan from: {scan_name}")
            debug_log(f"Plotting single scan for: {scan_name}",
                        file=__file__,
                        version=current_version,
                        function=current_function)

            # Use app_instance.output_folder_var for output directory
            output_dir = self.app_instance.output_folder_var.get()
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                debug_log(f"Created output directory: {output_dir}",
                            file=__file__,
                            version=current_version,
                            function=current_function)

            html_filename = os.path.join(output_dir, f"{scan_name.replace(' ', '_')}_single_scan_plot.html")
            debug_log(f"Output HTML filename: {html_filename}",
                        file=__file__,
                        version=current_version,
                        function=current_function)

            fig, plot_html_path_return = plot_single_scan_data(
                df,
                f"Single Scan: {scan_name}",
                include_tv_markers=self.app_instance.include_tv_markers_var.get(),
                include_gov_markers=self.app_instance.include_gov_markers_var.get(),
                include_markers=self.app_instance.include_markers_var.get(), # Pass general markers
                include_intermod_markers=self.app_instance.include_scan_intermod_markers_var.get(), # NEW
                output_html_path=html_filename if self.app_instance.create_html_var.get() else None, # Only create HTML if checkbox is checked
                console_print_func=self.console_print_func,
                scan_data_folder=os.path.dirname(file_path) # Pass the folder of the selected scan
            )

            if fig:
                self.current_plot_file = plot_html_path_return
                if self.app_instance.create_html_var.get():
                    self.console_print_func(f"✅ Single scan plot saved to: {self.current_plot_file}")
                    debug_log(f"Plot saved successfully to: {self.current_plot_file}",
                                file=__file__,
                                version=current_version,
                                function=current_function)
                else:
                    self.console_print_func("✅ Single scan plot data processed (HTML not saved as per setting).")
                    debug_log("Plot data processed, HTML not saved.",
                                file=__file__,
                                version=current_version,
                                function=current_function)

                if self.app_instance.open_html_after_complete_var.get() and self.app_instance.create_html_var.get() and plot_html_path_return:
                    self.console_print_func(f"Opening plot in browser: {self.current_plot_file}")
                    webbrowser.open_new_tab(self.current_plot_file)
                    debug_log(f"Plot opened in browser: {self.current_plot_file}",
                                file=__file__,
                                version=current_version,
                                function=current_function)
                elif self.app_instance.open_html_after_complete_var.get() and not self.app_instance.create_html_var.get():
                    self.console_print_func("HTML plot not opened because 'Create HTML' is unchecked. What a waste of a click!")
                    debug_log("HTML not opened as 'Create HTML' is unchecked.",
                                file=__file__,
                                version=current_version,
                                function=current_function)
            else:
                self.console_print_func("🚫 Plotly figure was not generated for single scan. Fucking useless!")
                debug_log("Plotly figure not generated for single scan.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        except Exception as e:
            self.console_print_func(f"❌ Error plotting single scan: {e}. This is a goddamn disaster!")
            debug_log(f"Error plotting single scan: {e}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _plot_current_cycle_average(self):
        """
        Function Description:
        Generates a plot of the current cycle's collected scan data, applying selected average types.

        Inputs to this function:
            None.

        Process of this function:
            1. Checks if `self.app_instance.collected_scans_dataframes` contains any data.
            2. Determines the output directory for the plot.
            3. Retrieves the currently selected average types from `app_instance` variables.
            4. If no average types are selected, logs a warning and returns.
            5. Aggregates and aligns all collected scan dataframes to a common frequency reference.
            6. Calculates the selected average types (Average, Median, Range, Std Dev, Variance, PSD)
               across the aligned scan data.
            7. Determines the plot title and output HTML filename.
            8. Dynamically sets the y-axis range override based on the selected average types.
            9. Calls `plot_multi_trace_data` from `utils.plotting_utils` to generate the plot.
            10. Stores the path of the generated HTML plot in `self.current_plot_file`.
            11. Logs success or failure messages to the console and optionally opens the plot in a browser.

        Outputs of this function:
            None. Generates an HTML plot file and updates `self.current_plot_file`.

        (2025-07-31) Change: Maintained in tab_plotting_child_Single.py.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if not self.app_instance.collected_scans_dataframes:
            self.console_print_func("No collected scan dataframes to average. What the hell am I supposed to plot?!")
            debug_log("No collected scan dataframes for current cycle average.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            debug_log(f"Exiting {current_function} (no data)",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        # Use app_instance.output_folder_var for output directory
        output_dir = self.app_instance.output_folder_var.get()
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            debug_log(f"Created output directory: {output_dir}",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Get selected average types for current cycle plot from app_instance variables
        selected_avg_types = [
            "Average" if self.app_instance.math_average_var.get() else None,
            "Median" if self.app_instance.math_median_var.get() else None,
            "Range" if self.app_instance.math_range_var.get() else None,
            "Standard Deviation" if self.app_instance.math_standard_deviation_var.get() else None,
            "Variance" if self.app_instance.math_variance_var.get() else None,
            "Power Spectral Density (PSD)" if self.app_instance.math_psd_var.get() else None
        ]
        selected_avg_types = [t for t in selected_avg_types if t is not None]

        if not selected_avg_types:
            self.console_print_func("Warning: No average type selected for current cycle plot. Please select at least one type. Come on, pick something!")
            debug_log(f"Exiting {current_function} (no selected_avg_types for current cycle)",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        self.console_print_func("Processing current cycle average plot. This may take a moment depending on the number of scans. Don't touch that dial!")
        debug_log(f"Calling generate_current_cycle_average_csv_and_plot with {len(self.app_instance.collected_scans_dataframes)} dataframes and selected types: {selected_avg_types}.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Aggregate the current cycle scans into a single DataFrame for plotting
        all_frequencies_current_cycle = pd.Series(dtype=float)
        power_levels_current_cycle_list = []
        rbw_values_current_cycle = [] # Collect RBW for PSD calculation

        for df_scan in self.app_instance.collected_scans_dataframes:
            if 'Frequency (Hz)' in df_scan.columns and 'Power (dBm)' in df_scan.columns:
                all_frequencies_current_cycle = pd.concat([all_frequencies_current_cycle, df_scan['Frequency (Hz)']])
                power_levels_current_cycle_list.append(df_scan.set_index('Frequency (Hz)')['Power (dBm)'])
                # Use the app_instance.scan_rbw_hz_var for RBW
                rbw_value = float(self.app_instance.scan_rbw_hz_var.get())
                rbw_values_current_cycle.append(rbw_value)
            else:
                self.console_print_func("Warning: Collected scan missing 'Frequency (Hz)' or 'Power (dBm)'. Skipping for current cycle average. What a mess!")
                debug_log("Collected scan missing freq/power columns.",
                            file=__file__,
                            version=current_version,
                            function=current_function)

        if not power_levels_current_cycle_list:
            self.console_print_func("No valid collected scans to average for current cycle. This is pointless!")
            debug_log("No valid collected scans for current cycle average.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        # Create a master reference frequency for current cycle
        reference_freq_current_cycle = all_frequencies_current_cycle.sort_values().drop_duplicates().reset_index(drop=True)

        # Reindex and interpolate all power series to the master frequency
        aligned_power_series_current_cycle = []
        for series in power_levels_current_cycle_list:
            aligned_series = series.reindex(reference_freq_current_cycle).interpolate(method='linear', limit_direction='both')
            aligned_power_series_current_cycle.append(aligned_series)

        power_levels_df_current_cycle = pd.concat(aligned_power_series_current_cycle, axis=1)
        power_levels_df_current_cycle.columns = [f"Scan_{i+1}" for i in range(len(aligned_power_series_current_cycle))]

        # Calculate selected average types for current cycle
        aggregated_df_current_cycle = pd.DataFrame({'Frequency (Hz)': reference_freq_current_cycle})

        # Define calculation functions locally or import them if they are in averaging_utils
        # For simplicity, defining them here for now, but ideally they'd be shared.
        def _local_calculate_average(df): return df.mean(axis=1)
        def _local_calculate_median(df): return df.median(axis=1)
        def _local_calculate_range(df): return df.max(axis=1) - df.min(axis=1)
        def _local_calculate_std_dev(df): return df.std(axis=1)
        def _local_calculate_variance(df): return df.var(axis=1)
        def _local_calculate_psd(df, rbw_values_list):
            if rbw_values_list and any(r is not None and r > 0 for r in rbw_values_list):
                # Use the average RBW for the PSD calculation across multiple scans
                avg_rbw = sum([r for r in rbw_values_list if r is not None and r > 0]) / len([r for r in rbw_values_list if r is not None and r > 0])
                linear_power_mW = 10**(df / 10).mean(axis=1) # Average linear power
                return 10 * np.log10(linear_power_mW / avg_rbw)
            else:
                return pd.Series([np.nan]*len(df.index))

        calculation_functions = {
            "Average": _local_calculate_average,
            "Median": _local_calculate_median,
            "Range": _local_calculate_range,
            "Standard Deviation": _local_calculate_std_dev, # Updated key
            "Variance": _local_calculate_variance,
            "Power Spectral Density (PSD)": _local_calculate_psd # Updated key
        }

        for avg_type in selected_avg_types:
            if avg_type in calculation_functions:
                if avg_type == "Power Spectral Density (PSD)": # Updated key
                    # Pass rbw_values_current_cycle to PSD calculation
                    aggregated_df_current_cycle[avg_type] = calculation_functions[avg_type](power_levels_df_current_cycle, rbw_values_current_cycle)
                else:
                    aggregated_df_current_cycle[avg_type] = calculation_functions[avg_type](power_levels_df_current_cycle)
            else:
                self.console_print_func(f"Warning: Unknown average type '{avg_type}' requested for current cycle. Skipping. What the hell is this type?!")

        plot_title_current_cycle = f"Current Cycle Average - {', '.join(selected_avg_types)}"
        html_filename_current_cycle = os.path.join(output_dir, f"CurrentCycleAverage_Plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

        # Determine y_range_max_override for current cycle plot
        y_range_max_override_val = 0 # Default for power plots
        if any(avg_type in selected_avg_types for avg_type in ["Range", "Standard Deviation", "Variance", "Power Spectral Density (PSD)"]):
            y_range_max_override_val = 30 # Set to 30 for these statistical plots

        fig, plot_html_path_return = plot_multi_trace_data(
            aggregated_df_current_cycle,
            plot_title_current_cycle,
            include_tv_markers=self.app_instance.include_tv_markers_var.get(), # Use app_instance var
            include_gov_markers=self.app_instance.include_gov_markers_var.get(), # Use app_instance var
            include_markers=self.app_instance.include_markers_var.get(), # Use app_instance var
            include_intermod_markers=self.app_instance.include_scan_intermod_markers_var.get(), # NEW
            historical_dfs_with_names=None,
            individual_scan_dfs_with_names=[(df, f"Scan {i+1}") for i, df in enumerate(self.app_instance.collected_scans_dataframes)], # Pass individual scans
            output_html_path=html_filename_current_cycle if self.app_instance.create_html_var.get() else None, # Use app_instance var
            y_range_min_override=None, # Let the plotting function determine min
            y_range_max_override=y_range_max_override_val, # Pass the dynamically set override
            console_print_func=self.console_print_func,
            scan_data_folder=output_dir # Pass the output directory as the scan_data_folder for markers
        )

        if fig:
            self.current_plot_file = plot_html_path_return
            if self.app_instance.create_html_var.get():
                self.console_print_func(f"✅ Current cycle averaged plot saved to: {self.current_plot_file}")
                debug_log(f"Current cycle averaged plot saved to: {self.current_plot_file}",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            else:
                self.console_print_func("✅ Current cycle averaged plot data processed (HTML not saved as per setting).")
                debug_log("Plot data processed, HTML not saved.",
                            file=__file__,
                            version=current_version,
                            function=current_function)

            if self.app_instance.open_html_after_complete_var.get() and self.app_instance.create_html_var.get() and plot_html_path_return:
                _open_plot_in_browser(plot_html_path_return, self.console_print_func)
        else:
            self.console_print_func("🚫 Plotly figure was not generated for current cycle averaged data. Are you even trying?!")
            debug_log("Plotly figure not generated for current cycle averaged data.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


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

        (2025-07-31) Change: Maintained in tab_plotting_child_Single.py.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if self.current_plot_file and os.path.exists(self.current_plot_file):
            self.console_print_func(f"Opening last plot: {self.current_plot_file}")
            _open_plot_in_browser(self.current_plot_file, self.console_print_func) # Pass console_print_func
            debug_log(f"Opened last plot: {self.current_plot_file}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            self.console_print_func("Error: No plot available or file not found. Please generate a plot first. What's the point of this button then?!")
            debug_log("No plot available or file not found.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    # Removed: _open_folder_for_averaging - moved to tab_plotting_child_Average.py
    # Removed: _find_and_group_csv_files - moved to tab_plotting_child_Average.py
    # Removed: _select_group_for_plotting - moved to tab_plotting_child_Average.py
    # Removed: _clear_dynamic_buttons - moved to tab_plotting_child_Average.py
    # Removed: _generate_csv_selected_series - moved to tab_plotting_child_Average.py
    # Removed: _open_applied_math_folder - moved to tab_plotting_child_Average.py
    # Removed: _generate_multi_average_plot - moved to tab_plotting_child_Average.py
    # Removed: _generate_plot_scans_over_time - moved to tab_plotting_child_Average.py


    def _on_tab_selected(self, event):
        """
        Function Description:
        Callback for when this tab is selected.
        This can be used to refresh data or update UI elements specific to this tab.

        Inputs to this function:
            event (tkinter.Event): The event object that triggered the tab selection.

        Process of this function:
            1. Logs a debug message indicating the tab selection.
            2. Ensures the "Plot Single Scan" button is enabled.
            3. Enables/Disables the "Plot Current Cycle Average" button based on whether
               `collected_scans_dataframes` contains any data.

        Outputs of this function:
            None. Updates the state of relevant GUI buttons.

        (2025-07-31) Change: Updated to reflect removal of folder averaging functionality.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        debug_log("Plotting Tab selected.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # The 'Plot Single Scan' button should always be enabled as it opens a file dialog.
        self.plot_button.config(state=tk.NORMAL)
        debug_log("Plot Single Scan button enabled.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Enable/Disable 'Plot Current Cycle Average' button based on collected_scans_dataframes
        if self.app_instance.collected_scans_dataframes:
            self.plot_average_button.config(state=tk.NORMAL)
            debug_log("Plot Current Cycle Average button enabled (data available).",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            self.plot_average_button.config(state=tk.DISABLED)
            debug_log("Plot Current Cycle Average button disabled (no data available).",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        debug_log(f"Exiting {current_function}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
