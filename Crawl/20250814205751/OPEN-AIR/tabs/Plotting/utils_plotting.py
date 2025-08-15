# utils/utils_plotting.py
#
# This module provides functions for generating interactive plots of spectrum analyzer data
# using Plotly. It supports plotting single scan traces, as well as aggregated data
# (average, median, range, standard deviation, variance, PSD) with historical overlays.
# It also includes functionalities for adding frequency band markers (TV, Government)
# and saving plots to HTML files.
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
# Version 20250810.140800.1 (FIXED: Removed top-level import of frequency_bands.py constants to resolve startup error. The constants will now be passed to the functions that need them.)

current_version = "20250810.140800.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250810 * 140800 * 1 # Example hash, adjust as needed

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import webbrowser
import os
import re # Added import for regular expressions
import csv # New: Import csv for MARKERS.CSV
import inspect # Import inspect for debug_log

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

# The `frequency_bands` constants are now passed to the functions that need them.
# The previous `try...except` block has been removed, resolving the startup error.

def _open_plot_in_browser(html_file_path, console_print_func):
    """
    Function Description:
    Opens the generated HTML plot in the default web browser.

    Inputs to this function:
        html_file_path (str): The full path to the HTML plot file.
        console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
        1. Checks if the HTML file exists.
        2. If it exists, uses `webbrowser.open_new_tab` to open it.
        3. Logs success or failure to the console and debug log.

    Outputs of this function:
        None. Opens a web browser tab.

    (2025-07-31) Change: Moved from main_app.py to utils_plotting.py.
    (2025-08-01) Change: Updated debug_print to debug_log.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to open plot in browser: {html_file_path}",
                file=__file__,
                version=current_version,
                function=current_function)
    if os.path.exists(html_file_path):
        try:
            webbrowser.open_new_tab(html_file_path)
            console_print_func(f"✅ Plot opened in browser: {os.path.basename(html_file_path)}")
            debug_log(f"Plot opened successfully: {html_file_path}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except Exception as e:
            console_print_func(f"❌ Error opening plot in browser: {e}. This is a goddamn mess!")
            debug_log(f"Error opening plot {html_file_path} in browser: {e}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
    else:
        console_print_func(f"❌ Error: Plot file not found at {html_file_path}. What the hell?!")
        debug_log(f"Plot file not found: {html_file_path}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


def _add_band_markers(fig, markers_dict, line_color, line_dash, band_name_suffix, MHZ_TO_HZ, console_print_func):
    """
    Function Description:
    Adds rectangular shape annotations to a Plotly figure to represent frequency bands.

    Inputs to this function:
        fig (go.Figure): The Plotly figure object to which markers will be added.
        markers_dict (dict): A dictionary where keys are band names (str) and values are
                             lists of [min_freq_MHz, max_freq_MHz].
        line_color (str): The color for the band outlines (e.g., 'rgba(255, 0, 0, 0.5)').
        line_dash (str): The dash style for the band outlines (e.g., 'dot', 'dash').
        band_name_suffix (str): A suffix to add to the band names for legend clarity (e.g., " (TV)").
        MHZ_TO_HZ (float): The conversion factor from MHz to Hz.
        console_print_func (function): Function to print messages to the GUI console.

    Outputs of this function:
        Modifies the `fig` object by adding shapes.

    (2025-07-31) Change: Moved from main_app.py to utils_plotting.py.
    (2025-08-01) Change: Updated debug_print to debug_log.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Adding band markers with suffix '{band_name_suffix}'...",
                file=__file__,
                version=current_version,
                function=current_function)
    for band_name, freq_range_mhz in markers_dict.items():
        min_freq_hz = freq_range_mhz[0] * MHZ_TO_HZ
        max_freq_hz = freq_range_mhz[1] * MHZ_TO_HZ
        fig.add_shape(
            type="rect",
            xref="x", yref="paper",
            x0=min_freq_hz, y0=0, x1=max_freq_hz, y1=1,
            line=dict(color=line_color, width=1, dash=line_dash),
            fillcolor=line_color.replace('0.5', '0.1'), # Lighter fill
            layer="below",
            name=f"{band_name}{band_name_suffix}",
            # Add a legend group to show these as distinct items in the legend
            # but still allow toggling them together if desired by Plotly's default behavior
            legendgroup=f"{band_name_suffix.strip()}_bands",
            showlegend=True # Ensure they appear in the legend
        )
        # Add a dummy trace for the legend entry if the shape's name doesn't show up correctly
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='lines',
            line=dict(color=line_color, width=1, dash=line_dash),
            name=f"{band_name}{band_name_suffix}",
            legendgroup=f"{band_name_suffix.strip()}_bands",
            showlegend=True
        ))
        debug_log(f"Added band marker: {band_name}{band_name_suffix} ({min_freq_hz/MHZ_TO_HZ:.2f}-{max_freq_hz/MHZ_TO_HZ:.2f} MHz)",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    debug_log(f"Finished adding band markers with suffix '{band_name_suffix}'.",
                file=__file__,
                version=current_version,
                function=current_function)


def _add_markers_from_csv(fig, markers_csv_path, MHZ_TO_HZ, console_print_func):
    """
    Function Description:
    Reads markers from a specified CSV file and adds vertical line annotations to a Plotly figure.
    The CSV is expected to have 'FREQ' and 'NAME' columns.

    Inputs to this function:
        fig (go.Figure): The Plotly figure object to which markers will be added.
        markers_csv_path (str): The path to the CSV file containing marker data.
        MHZ_TO_HZ (float): The conversion factor from MHz to Hz.
        console_print_func (function): Function to print messages to the GUI console.

    Outputs of this function:
        Modifies the `fig` object by adding vertical lines and text annotations.

    (2025-07-31) Change: Moved from main_app.py to utils_plotting.py.
    (2025-08-01) Change: Updated debug_print to debug_log.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to add markers from CSV: {markers_csv_path}",
                file=__file__,
                version=current_version,
                function=current_function)
    if not os.path.exists(markers_csv_path):
        console_print_func(f"⚠️ Warning: Markers CSV file not found at {markers_csv_path}. Cannot add markers. What the hell?!")
        debug_log(f"Markers CSV not found: {markers_csv_path}. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return

    try:
        df_markers = pd.read_csv(markers_csv_path)
        if 'FREQ' not in df_markers.columns or 'NAME' not in df_markers.columns:
            console_print_func(f"❌ Error: Markers CSV '{markers_csv_path}' must contain 'FREQ' and 'NAME' columns. This is a goddamn mess!")
            debug_log(f"Markers CSV '{markers_csv_path}' missing required columns.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        for index, row in df_markers.iterrows():
            freq_hz = row['FREQ']
            marker_name = row['NAME']
            fig.add_vline(x=freq_hz, line_width=1, line_dash="dash", line_color="purple",
                          annotation_text=marker_name, annotation_position="top right")
            debug_log(f"Added marker from CSV: {marker_name} at {freq_hz/MHZ_TO_HZ:.3f} MHz",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        console_print_func(f"✅ Added markers from {os.path.basename(markers_csv_path)}.")
    except Exception as e:
        console_print_func(f"❌ Error reading or adding markers from CSV {os.path.basename(markers_csv_path)}: {e}. This CSV is a stubborn bastard!")
        debug_log(f"Error reading or adding markers from CSV {markers_csv_path}: {e}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


def _add_intermodulation_markers(fig, intermod_csv_path, MHZ_TO_HZ, console_print_func):
    """
    Function Description:
    Reads intermodulation product frequencies from a specified CSV file and adds
    vertical line annotations to a Plotly figure. The CSV is expected to have
    a 'Frequency_MHz' column.

    Inputs to this function:
        fig (go.Figure): The Plotly figure object to which markers will be added.
        intermod_csv_path (str): The path to the CSV file containing intermodulation data.
        MHZ_TO_HZ (float): The conversion factor from MHz to Hz.
        console_print_func (function): Function to print messages to the GUI console.

    Outputs of this function:
        Modifies the `fig` object by adding vertical lines and text annotations.

    (2025-08-01) Change: New function to add intermodulation markers.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to add intermodulation markers from CSV: {intermod_csv_path}",
                file=__file__,
                version=current_version,
                function=current_function)
    if not os.path.exists(intermod_csv_path):
        console_print_func(f"⚠️ Warning: Intermodulation CSV file not found at {intermod_csv_path}. Cannot add IMD markers. What the hell?!")
        debug_log(f"Intermodulation CSV not found: {intermod_csv_path}. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return

    try:
        df_intermod = pd.read_csv(intermod_csv_path)
        if 'Frequency_MHz' not in df_intermod.columns:
            console_print_func(f"❌ Error: Intermodulation CSV '{intermod_csv_path}' must contain 'Frequency_MHz' column. This is a goddamn mess!")
            debug_log(f"Intermodulation CSV '{intermod_csv_path}' missing required 'Frequency_MHz' column.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        for index, row in df_intermod.iterrows():
            freq_mhz = row['Frequency_MHz']
            freq_hz = freq_mhz * MHZ_TO_HZ
            # Create a descriptive name for the IMD marker
            imd_name = f"IMD {row.get('Order', '')} ({row.get('Type', '')}) from {row.get('Parent_Freq1', 'N/A')} & {row.get('Parent_Freq2', 'N/A')} MHz"
            fig.add_vline(x=freq_hz, line_width=1, line_dash="solid", line_color="red",
                          annotation_text=f"IMD {freq_mhz:.3f} MHz", annotation_position="bottom right")
            debug_log(f"Added intermodulation marker: {imd_name} at {freq_mhz:.3f} MHz",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        console_print_func(f"✅ Added intermodulation markers from {os.path.basename(intermod_csv_path)}.")
    except Exception as e:
        console_print_func(f"❌ Error reading or adding intermodulation markers from CSV {os.path.basename(intermod_csv_path)}: {e}. This IMD CSV is a stubborn bastard!")
        debug_log(f"Error reading or adding intermodulation markers from CSV {intermod_csv_path}: {e}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


def _create_spectrum_plot(data_traces, plot_title, include_tv_markers, include_gov_markers,
                          include_markers, include_intermod_markers, output_html_path,
                          y_range_min_override, y_range_max_override, console_print_func,
                          scan_data_folder, MHZ_TO_HZ, TV_BAND_MARKERS_MHZ, GOVERNMENT_BAND_MARKERS_MHZ,
                          DEFAULT_MARKERS_FILE, DEFAULT_INTERMOD_FILE):
    """
    Function Description:
    Generates a Plotly HTML interactive plot for spectrum analyzer data.
    This is a core plotting function that can handle multiple traces (e.g., current, historical, averages).
    It includes options for adding TV, Government, and custom markers.

    Inputs to this function:
        data_traces (list of dict): A list where each dict represents a trace to plot, e.g.:
                                    `{'df': DataFrame, 'name': 'Trace Name', 'color': 'blue', 'width': 2, 'dash': 'solid', 'show_legend': True, 'y_column_name': 'Power (dBm)'}`
        plot_title (str): The title of the plot.
        include_tv_markers (bool): If True, TV band markers are added.
        include_gov_markers (bool): If True, Government band markers are added.
        include_markers (bool): If True, custom markers from MARKERS.csv are added.
        include_intermod_markers (bool): If True, intermodulation markers from INTERMOD.csv are added.
        output_html_path (str or None): If a string, saves the plot to this HTML file. If None, does not save.
        y_range_min_override (float or None): Optional minimum Y-axis value.
        y_range_max_override (float or None): Optional maximum Y-axis value.
        console_print_func (function): Function to print messages to the GUI console.
        scan_data_folder (str): The folder where scan data (and potentially MARKERS.csv/INTERMOD.csv) resides.
        MHZ_TO_HZ (float): The conversion factor from MHz to Hz.
        TV_BAND_MARKERS_MHZ (dict): Dictionary of TV band markers.
        GOVERNMENT_BAND_MARKERS_MHZ (dict): Dictionary of Government band markers.
        DEFAULT_MARKERS_FILE (str): Default filename for markers CSV.
        DEFAULT_INTERMOD_FILE (str): Default filename for intermodulation CSV.

    Process of this function:
        1. Initializes an empty Plotly figure.
        2. Adds each trace from `data_traces` to the figure.
        3. Configures the layout (title, axes labels, hover mode).
        4. Conditionally adds TV, Government, custom, and intermodulation band markers.
        5. Sets Y-axis range if overrides are provided.
        6. If `output_html_path` is provided, saves the figure to an HTML file.
        7. Logs debug information throughout the process.

    Outputs of this function:
        tuple: (go.Figure, str or None) - The Plotly figure object and the path to the saved HTML file (or None).

    (2025-07-31) Change: Consolidated plotting logic from plot_single_scan_data and plot_multi_trace_data.
    (2025-07-31) Change: Added y_range_min_override and y_range_max_override parameters.
    (2025-08-01) Change: Added include_intermod_markers parameter and call to _add_intermodulation_markers.
    (2025-08-01) Change: Updated debug_print to debug_log.
    (2025-08-10) Change: Updated function signature to accept constants as arguments.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Creating spectrum plot: '{plot_title}'",
                file=__file__,
                version=current_version,
                function=current_function)

    fig = go.Figure()

    for trace_data in data_traces:
        df = trace_data['df']
        name = trace_data['name']
        color = trace_data['color']
        width = trace_data['width']
        dash = trace_data['dash']
        show_legend = trace_data['show_legend']
        y_column_name = trace_data['y_column_name'] # Use this to select the Y-axis column

        if df.empty or 'Frequency (Hz)' not in df.columns or y_column_name not in df.columns:
            debug_log(f"Skipping trace '{name}': Invalid DataFrame or missing columns. What a bummer!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            continue

        fig.add_trace(go.Scatter(
            x=df['Frequency (Hz)'],
            y=df[y_column_name],
            mode='lines',
            name=name,
            line=dict(color=color, width=width, dash=dash),
            showlegend=show_legend
        ))
        debug_log(f"Added trace: '{name}' with Y-column '{y_column_name}'",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    fig.update_layout(
        title={
            'text': plot_title,
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="Frequency (Hz)",
        yaxis_title="Power (dBm)", # Default Y-axis title
        hovermode="x unified",
        template="plotly_dark",
        margin=dict(l=50, r=50, t=80, b=50),
        height=700,
        width=1000,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    debug_log("Plot layout updated.",
                file=__file__,
                version=current_version,
                function=current_function)

    # Conditionally add markers
    if include_tv_markers:
        _add_band_markers(fig, TV_BAND_MARKERS_MHZ, 'rgba(0, 255, 0, 0.5)', 'dot', ' (TV)', MHZ_TO_HZ, console_print_func)
    if include_gov_markers:
        _add_band_markers(fig, GOVERNMENT_BAND_MARKERS_MHZ, 'rgba(255, 165, 0, 0.5)', 'dash', ' (Gov)', MHZ_TO_HZ, console_print_func)
    if include_markers and scan_data_folder:
        markers_csv_path = os.path.join(scan_data_folder, DEFAULT_MARKERS_FILE)
        _add_markers_from_csv(fig, markers_csv_path, MHZ_TO_HZ, console_print_func)
    if include_intermod_markers and scan_data_folder:
        intermod_csv_path = os.path.join(scan_data_folder, DEFAULT_INTERMOD_FILE)
        _add_intermodulation_markers(fig, intermod_csv_path, MHZ_TO_HZ, console_print_func)


    # Apply Y-axis range override if provided
    if y_range_min_override is not None and y_range_max_override is not None:
        fig.update_yaxes(range=[y_range_min_override, y_range_max_override])
        debug_log(f"Y-axis range overridden to: [{y_range_min_override}, {y_range_max_override}]",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    elif y_range_max_override is not None: # Only max override
        fig.update_yaxes(range=[fig.layout.yaxis.range[0], y_range_max_override])
        debug_log(f"Y-axis max range overridden to: {y_range_max_override}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    elif y_range_min_override is not None: # Only min override
        fig.update_yaxes(range=[y_range_min_override, fig.layout.yaxis.range[1]])
        debug_log(f"Y-axis min range overridden to: {y_range_min_override}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    plot_html_path_return = None
    if output_html_path:
        output_dir = os.path.dirname(output_html_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            debug_log(f"Created output directory for plot: {output_html_path}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        debug_log(f"Saving plot to: {output_html_path}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        fig.write_html(output_html_path, auto_open=False)
        plot_html_path_return = output_html_path
        debug_log(f"Plot saved to: {output_html_path}. Fucking brilliant!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Output HTML path not provided, skipping saving plot to file. What a waste!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    debug_log(f"Exiting {current_function}",
                file=__file__,
                version=current_version,
                function=current_function)
    return fig, plot_html_path_return


def plot_single_scan_data(df_scan, plot_title, include_tv_markers, include_gov_markers,
                          include_markers, include_intermod_markers, output_html_path, console_print_func,
                          scan_data_folder, MHZ_TO_HZ, TV_BAND_MARKERS_MHZ, GOVERNMENT_BAND_MARKERS_MHZ,
                          DEFAULT_MARKERS_FILE, DEFAULT_INTERMOD_FILE):
    """
    Function Description:
    Plots a single spectrum analyzer scan. This is a wrapper around `_create_spectrum_plot`.

    Inputs to this function:
        df_scan (pd.DataFrame): DataFrame containing 'Frequency (Hz)' and 'Power (dBm)'.
        plot_title (str): The title for the plot.
        include_tv_markers (bool): If True, TV band markers are added.
        include_gov_markers (bool): If True, Government band markers are added.
        include_markers (bool): If True, custom markers from MARKERS.csv are added.
        include_intermod_markers (bool): If True, intermodulation markers from INTERMOD.csv are added.
        output_html_path (str or None): If a string, saves the plot to this HTML file. If None, does not save.
        console_print_func (function): Function to print messages to the GUI console.
        scan_data_folder (str): The folder where scan data (and potentially MARKERS.csv/INTERMOD.csv) resides.
        MHZ_TO_HZ (float): The conversion factor from MHz to Hz.
        TV_BAND_MARKERS_MHZ (dict): Dictionary of TV band markers.
        GOVERNMENT_BAND_MARKERS_MHZ (dict): Dictionary of Government band markers.
        DEFAULT_MARKERS_FILE (str): Default filename for markers CSV.
        DEFAULT_INTERMOD_FILE (str): Default filename for intermodulation CSV.

    Outputs of this function:
        tuple: (go.Figure, str or None) - The Plotly figure object and the path to the saved HTML file (or None).

    (2025-07-31) Change: Simplified to be a wrapper for _create_spectrum_plot.
    (2025-08-01) Change: Added include_intermod_markers parameter.
    (2025-08-01) Change: Updated debug_print to debug_log.
    (2025-08-10) Change: Updated function signature to accept constants as arguments.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Plotting single scan data for '{plot_title}'...",
                file=__file__,
                version=current_version,
                function=current_function)

    data_traces = [{
        'df': df_scan,
        'name': 'Current Scan',
        'color': 'blue',
        'width': 2,
        'dash': 'solid',
        'show_legend': True,
        'y_column_name': 'Power (dBm)'
    }]

    fig, html_path = _create_spectrum_plot(
        data_traces,
        plot_title,
        include_tv_markers,
        include_gov_markers,
        include_markers,
        include_intermod_markers, # Pass the new parameter
        output_html_path,
        y_range_min_override=None,
        y_range_max_override=None,
        console_print_func=console_print_func,
        scan_data_folder=scan_data_folder,
        MHZ_TO_HZ=MHZ_TO_HZ,
        TV_BAND_MARKERS_MHZ=TV_BAND_MARKERS_MHZ,
        GOVERNMENT_BAND_MARKERS_MHZ=GOVERNMENT_BAND_MARKERS_MHZ,
        DEFAULT_MARKERS_FILE=DEFAULT_MARKERS_FILE,
        DEFAULT_INTERMOD_FILE=DEFAULT_INTERMOD_FILE
    )
    debug_log(f"Finished plotting single scan data for '{plot_title}'.",
                file=__file__,
                version=current_version,
                function=current_function)
    return fig, html_path


def plot_multi_trace_data(df_aggregated, plot_title, include_tv_markers, include_gov_markers,
                          include_markers, include_intermod_markers, historical_dfs_with_names,
                          individual_scan_dfs_with_names, output_html_path,
                          y_range_min_override, y_range_max_override, console_print_func,
                          scan_data_folder, MHZ_TO_HZ, TV_BAND_MARKERS_MHZ, GOVERNMENT_BAND_MARKERS_MHZ,
                          DEFAULT_MARKERS_FILE, DEFAULT_INTERMOD_FILE):
    """
    Function Description:
    Plots multiple traces on a single Plotly graph, including an aggregated trace (e.g., average)
    and optional historical or individual scan overlays. This is a wrapper around `_create_spectrum_plot`.

    Inputs to this function:
        df_aggregated (pd.DataFrame): DataFrame for the main aggregated trace (e.g., current average).
                                      Expected to have 'Frequency (Hz)' and other calculated columns.
        plot_title (str): The title for the plot.
        include_tv_markers (bool): If True, TV band markers are added.
        include_gov_markers (bool): If True, Government band markers are added.
        include_markers (bool): If True, custom markers from MARKERS.csv are added.
        include_intermod_markers (bool): If True, intermodulation markers from INTERMOD.csv are added.
        historical_dfs_with_names (list of tuples or None): List of (DataFrame, name) for historical overlays.
                                                            Each DataFrame should have 'Frequency (Hz)' and 'Power (dBm)'.
        individual_scan_dfs_with_names (list of tuples or None): List of (DataFrame, name) for individual scan overlays.
                                                                  Each DataFrame should have 'Frequency (Hz)' and 'Power (dBm)'.
        output_html_path (str or None): If a string, saves the plot to this HTML file. If None, does not save.
        y_range_min_override (float or None): Optional minimum Y-axis value.
        y_range_max_override (float or None): Optional maximum Y-axis value.
        console_print_func (function): Function to print messages to the GUI console.
        scan_data_folder (str): The folder where scan data (and potentially MARKERS.csv/INTERMOD.csv) resides.
        MHZ_TO_HZ (float): The conversion factor from MHz to Hz.
        TV_BAND_MARKERS_MHZ (dict): Dictionary of TV band markers.
        GOVERNMENT_BAND_MARKERS_MHZ (dict): Dictionary of Government band markers.
        DEFAULT_MARKERS_FILE (str): Default filename for markers CSV.
        DEFAULT_INTERMOD_FILE (str): Default filename for intermodulation CSV.

    Outputs of this function:
        tuple: (go.Figure, str or None) - The Plotly figure object and the path to the saved HTML file (or None).

    (2025-07-31) Change: Consolidated plotting logic into _create_spectrum_plot.
    (2025-07-31) Change: Added y_range_min_override and y_range_max_override parameters.
    (2025-08-01) Change: Added include_intermod_markers parameter.
    (2025-08-01) Change: Updated debug_print to debug_log.
    (2025-08-10) Change: Updated function signature to accept constants as arguments.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Plotting multi-trace data for '{plot_title}'...",
                file=__file__,
                version=current_version,
                function=current_function)

    data_traces = []

    # Add the main aggregated trace (e.g., Average, Median, etc.)
    # The y_column_name for the main aggregated trace will be the first data column after Frequency (Hz)
    # This assumes df_aggregated columns are ['Frequency (Hz)', 'Average', 'Median', ...]
    if not df_aggregated.empty and 'Frequency (Hz)' in df_aggregated.columns and len(df_aggregated.columns) > 1:
        # Get all columns except 'Frequency (Hz)' as y-axis columns
        y_cols = [col for col in df_aggregated.columns if col != 'Frequency (Hz)']
        for y_col in y_cols:
            data_traces.append({
                'df': df_aggregated,
                'name': y_col, # Use the column name as the trace name
                'color': px.colors.qualitative.Plotly[y_cols.index(y_col) % len(px.colors.qualitative.Plotly)], # Cycle through colors
                'width': 3,
                'dash': 'solid',
                'show_legend': True,
                'y_column_name': y_col # Specify the column to use for Y-axis
            })
        debug_log(f"Added aggregated trace(s) from columns: {y_cols}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Aggregated DataFrame is empty or invalid. Skipping aggregated trace. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    # Add historical overlays if provided
    if historical_dfs_with_names:
        debug_log(f"Adding {len(historical_dfs_with_names)} historical overlays.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        for i, (df_hist, name) in enumerate(historical_dfs_with_names):
            if not df_hist.empty and 'Frequency (Hz)' in df_hist.columns and 'Power (dBm)' in df_hist.columns:
                data_traces.append({
                    'df': df_hist,
                    'name': f'{name} (Historical)',
                    'color': f'rgba(100, 100, 100, {max(0, 0.8 - i * 0.1)})', # Faded gray for historical
                    'width': 1,
                    'dash': 'dot',
                    'show_legend': True,
                    'y_column_name': 'Power (dBm)' # Historical scans will have 'Power (dBm)'
                })
            else:
                debug_log(f"Skipping historical DF '{name}': Invalid DataFrame. What a pain!",
                            file=__file__,
                            version=current_version,
                            function=current_function)

    # Add individual scan overlays if provided
    if individual_scan_dfs_with_names:
        debug_log(f"Adding {len(individual_scan_dfs_with_names)} individual scan overlays.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        for i, (df_scan_plot, name) in enumerate(individual_scan_dfs_with_names):
            debug_log(f"Preparing individual scan overlay: {name}",
                        file=__file__,
                        version=current_version,
                        function=current_function)

            if not df_scan_plot.empty and 'Frequency (Hz)' in df_scan_plot.columns and 'Power (dBm)' in df_scan_plot.columns:
                data_traces.append({
                    'df': df_scan_plot,
                    'name': f'{name} (Scan)',
                    'color': f'rgba(0, 200, 255, {max(0, 0.5 - i * 0.05)})', # Clamped alpha value
                    'width': 1,
                    'dash': 'dot',
                    'show_legend': True,
                    'y_column_name': 'Power (dBm)' # Individual scans will have 'Power (dBm)'
                })
            else:
                debug_log(f"Skipping individual scan DF '{name}': Invalid DataFrame. Fucking useless!",
                            file=__file__,
                            version=current_version,
                            function=current_function)

    if not data_traces:
        console_print_func("No valid data to plot in multi-trace function. This is a goddamn mess!")
        debug_log("No valid data traces prepared for multi-trace plot.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return None, None

    return _create_spectrum_plot(
        data_traces,
        plot_title,
        include_tv_markers,
        include_gov_markers,
        include_markers,
        include_intermod_markers, # Pass the new parameter
        output_html_path,
        y_range_min_override,
        y_range_max_override,
        console_print_func,
        scan_data_folder,
        MHZ_TO_HZ=MHZ_TO_HZ,
        TV_BAND_MARKERS_MHZ=TV_BAND_MARKERS_MHZ,
        GOVERNMENT_BAND_MARKERS_MHZ=GOVERNMENT_BAND_MARKERS_MHZ,
        DEFAULT_MARKERS_FILE=DEFAULT_MARKERS_FILE,
        DEFAULT_INTERMOD_FILE=DEFAULT_INTERMOD_FILE
    )