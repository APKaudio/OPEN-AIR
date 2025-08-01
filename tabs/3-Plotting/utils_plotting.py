# utils/plotting_utils.py
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
#
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import webbrowser
import os
import re # Added import for regular expressions
import csv # New: Import csv for MARKERS.CSV
import inspect # Import inspect for debug_print

# Import constants from frequency_bands.py
try:
    from ref.frequency_bands import ( # Changed to relative import
        MHZ_TO_HZ,
        TV_PLOT_BAND_MARKERS,
        GOV_PLOT_BAND_MARKERS
    )
except ImportError:
    # Fallback if frequency_bands.py is not in ref, assume it's directly accessible
    try:
        from ref.frequency_bands import (
            MHZ_TO_HZ,
            TV_PLOT_BAND_MARKERS,
            GOV_PLOT_BAND_MARKERS
        )
    except ImportError:
        print("Error: frequency_bands.py not found in 'ref' or current directory.")
        # Define placeholders to prevent errors if file is completely missing
        MHZ_TO_HZ = 1_000_000
        TV_PLOT_BAND_MARKERS = []
        GOV_PLOT_BAND_MARKERS = []

# Assuming debug_print exists or define a dummy one for standalone testing
# This needs to be imported from utils.instrument_control if that's the standard
try:
    from utils.instrument_control import debug_print
except ImportError:
    print("Warning: debug_print not found in utils.instrument_control. Using dummy.")
    def debug_print(*args, **kwargs):
        pass # Dummy function


def _open_plot_in_browser(html_file_path, console_print_func=None):
    """
    Opens the generated HTML plot in the default web browser.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering {current_function} with html_file_path: {html_file_path}", file=current_file, function=current_function, console_print_func=console_print_func)
    try:
        if os.path.exists(html_file_path):
            webbrowser.open_new_tab(html_file_path)
            if console_print_func:
                console_print_func(f"Plot opened in browser: {html_file_path}")
            debug_print(f"Successfully opened plot: {html_file_path}", file=current_file, function=current_function, console_print_func=console_print_func)
        else:
            if console_print_func:
                console_print_func(f"Error: HTML file not found at {html_file_path}")
            debug_print(f"Error: HTML file not found at {html_file_path}", file=current_file, function=current_function, console_print_func=console_print_func)
    except Exception as e:
        if console_print_func:
            console_print_func(f"Failed to open plot in browser: {e}")
        debug_print(f"Failed to open plot in browser: {e}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)


def _load_custom_markers(data_df, console_print_func=None, scan_data_folder=None):
    """
    Loads custom markers from MARKERS.CSV (expected in 'ref' directory or scan_data_folder)
    and prepares them as Plotly shapes and annotations.
    Markers are filtered based on the frequency range of the provided data_df.

    Returns:
        tuple: A tuple containing two lists: (list of shapes, list of annotations).
               Returns ([], []) if an error occurs or no markers are found.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)

    # IMPORTANT: Ensure data_df has 'Frequency (MHz)' column before proceeding
    if data_df.empty or 'Frequency (MHz)' not in data_df.columns:
        if console_print_func:
            console_print_func("Warning: Data for custom markers is empty or missing 'Frequency (MHz)' column. Skipping custom markers.")
        debug_print("Data for custom markers is invalid. Skipping.", file=current_file, function=current_function, console_print_func=console_print_func)
        debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
        return [], []

    markers_file_path = None
    # Prioritize scan_data_folder if provided
    if scan_data_folder and os.path.exists(os.path.join(scan_data_folder, 'MARKERS.CSV')):
        markers_file_path = os.path.join(scan_data_folder, 'MARKERS.CSV')
        debug_print(f"Attempting to load MARKERS.CSV from scan_data_folder: {markers_file_path}", file=current_file, function=current_function, console_print_func=console_print_func)
    else:
        # Fallback to ref directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        potential_path = os.path.join(script_dir, '..', 'ref', 'MARKERS.CSV')
        if os.path.exists(potential_path):
            markers_file_path = potential_path
            debug_print(f"Attempting to load MARKERS.CSV from ref directory: {markers_file_path}", file=current_file, function=current_function, console_print_func=console_print_func)
        else:
            if console_print_func:
                console_print_func(f"Info: MARKERS.CSV not found in scan data folder or 'ref' directory. Skipping custom markers.")
            debug_print(f"MARKERS.CSV not found. Skipping custom markers.", file=current_file, function=current_function, console_print_func=console_print_func)
            debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
            return [], []

    parsed_markers = [] # Renamed to avoid conflict with 'markers' in the loop

    if not markers_file_path:
        debug_print(f"No valid markers_file_path determined. Exiting {current_function}.", file=current_file, function=current_function, console_print_func=console_print_func)
        return [], []

    try:
        debug_print(f"Attempting to open MARKERS.CSV from: {markers_file_path}", file=current_file, function=current_function, console_print_func=console_print_func)
        with open(markers_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            debug_print(f"MARKERS.CSV headers found: {reader.fieldnames}", file=current_file, function=current_function, console_print_func=console_print_func)

            # Check for expected columns based on the user's provided MARKERS.CSV structure
            expected_columns = ['ZONE', 'GROUP', 'DEVICE', 'NAME', 'FREQ']
            if not all(col in reader.fieldnames for col in expected_columns):
                if console_print_func:
                    console_print_func(f"Error: MARKERS.CSV at {markers_file_path} is missing one or more expected columns ({', '.join(expected_columns)}). Headers found: {reader.fieldnames}. Skipping custom markers.")
                debug_print(f"MARKERS.CSV missing required columns. Skipping.", file=current_file, function=current_function, console_print_func=console_print_func)
                debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
                return [], []

            for row in reader:
                debug_print(f"Processing marker row: {row}", file=current_file, function=current_function, console_print_func=console_print_func)
                try:
                    # The 'FREQ' column in MARKERS.CSV is assumed to be in MHz based on user's data snippet.
                    marker_freq_mhz = float(row['FREQ'])
                    
                    # Combine relevant information for the marker name/annotation
                    marker_name_parts = []
                    if 'ZONE' in row and row['ZONE'].strip():
                        marker_name_parts.append(row['ZONE'].strip())
                    if 'GROUP' in row and row['GROUP'].strip():
                        marker_name_parts.append(row['GROUP'].strip())
                    if 'DEVICE' in row and row['DEVICE'].strip():
                        marker_name_parts.append(row['DEVICE'].strip())
                    if 'NAME' in row and row['NAME'].strip():
                        marker_name_parts.append(row['NAME'].strip())
                    
                    # Create a multi-line annotation text
                    # Concatenate up to the first 3 parts, then add frequency
                    display_parts = marker_name_parts[:3] # Take up to the first 3 parts
                    marker_annotation_text = "<br>".join(display_parts) + f"<br>{marker_freq_mhz:.3f} MHz"


                    parsed_markers.append({'freq_mhz': marker_freq_mhz, 'name': marker_annotation_text})
                    debug_print(f"Parsed marker: {{'freq_mhz': {marker_freq_mhz}, 'name': '{marker_annotation_text}'}}", file=current_file, function=current_function, console_print_func=console_print_func)
                except ValueError as ve:
                    debug_print(f"Warning: Skipping row in MARKERS.CSV due to invalid frequency/data: {row} - {ve}", file=current_file, function=current_function, console_print_func=console_print_func)
    except Exception as e:
        if console_print_func:
            console_print_func(f"Error reading MARKERS.CSV: {e}")
        debug_print(f"Error reading MARKERS.CSV: {e}", file=current_file, function=current_function, console_print_func=console_print_func)
        debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
        return [], []

    plot_shapes = []
    plot_annotations = []

    if parsed_markers:
        plot_min_freq_mhz = data_df['Frequency (MHz)'].min()
        plot_max_freq_mhz = data_df['Frequency (MHz)'].max()
        debug_print(f"Plot frequency range: {plot_min_freq_mhz:.3f} MHz to {plot_max_freq_mhz:.3f} MHz", file=current_file, function=current_function, console_print_func=console_print_func)
        debug_print(f"All parsed markers array: {parsed_markers}", file=current_file, function=current_function, console_print_func=console_print_func)


        # Add vertical lines and annotations for custom markers
        # Define a list of colors for custom markers
        custom_marker_colors = [
            "purple", "red", "orange", "gold", "yellow", "lime", "green", "cyan", "blue", "magenta",
            "darkred", "darkorange", "darkgoldenrod", "olivedrab", "seagreen", "teal", "steelblue",
            "darkblue", "indigo", "darkmagenta"
        ]
        
        # Staggered Y-offset levels for text markers (relative to plot height)
        # Using a fixed set of Y-offsets to prevent overlap
        y_offset_levels = [0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50] # Relative to the top of the plot

        current_marker_index = 0
        for marker in parsed_markers:
            marker_freq_mhz = marker['freq_mhz']
            marker_annotation_text = marker['name'] # This now contains multi-line text

            if plot_min_freq_mhz <= marker_freq_mhz <= plot_max_freq_mhz:
                # Cycle through colors and y-offsets
                color_to_use = custom_marker_colors[current_marker_index % len(custom_marker_colors)]
                y_offset_ratio = y_offset_levels[current_marker_index % len(y_offset_levels)]

                # Add vertical line as a shape
                plot_shapes.append(
                    dict(
                        type="line",
                        x0=marker_freq_mhz, y0=0, x1=marker_freq_mhz, y1=1,
                        xref="x", yref="paper",
                        line=dict(color=color_to_use, width=1, dash="dash")
                    )
                )
                
                # Add annotation
                plot_annotations.append(
                    dict(
                        x=marker_freq_mhz,
                        yref="paper", # Reference to the paper (plot area) height
                        y=y_offset_ratio, # Position relative to the top of the plot area
                        text=marker_annotation_text,
                        showarrow=False,
                        font=dict(color=color_to_use, size=8),
                        xanchor="left", # Anchor text to the left of the marker line
                        yanchor="top", # Anchor text to the top of the y-position
                        bgcolor="rgba(0,0,0,0.7)",
                        bordercolor=color_to_use,
                        borderwidth=0.5,
                        align="left" # Align text to the left within its box
                    )
                )
                debug_print(f"Prepared custom marker: {marker_annotation_text} at {marker_freq_mhz:.3f} MHz with color {color_to_use} and y_offset {y_offset_ratio}", file=current_file, function=current_function, console_print_func=console_print_func)
                current_marker_index += 1
        
        if console_print_func:
            console_print_func(f"Prepared {current_marker_index} custom markers from MARKERS.CSV within plot range.")
    else:
        if console_print_func:
            console_print_func("No valid custom markers found in MARKERS.CSV or none within plot range.")
        debug_print("No valid custom markers found or none within plot range.", file=current_file, function=current_function, console_print_func=console_print_func)

    debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
    return plot_shapes, plot_annotations


def _create_spectrum_plot(
    data_traces, # List of dicts: [{'df': DataFrame, 'name': str, 'color': str, 'dash': str, 'width': int, 'show_legend': bool, 'y_column_name': str}]
    plot_title,
    include_tv_markers=False,
    include_gov_markers=False,
    include_markers=True,
    include_intermod_markers=False,
    output_html_path=None,
    y_range_min_override=None,
    y_range_max_override=0,
    console_print_func=None,
    scan_data_folder=None
):
    """
    Generates an interactive Plotly HTML plot for spectrum analyzer data.
    This is a unified function to handle both single and multi-trace plots.

    Inputs:
        data_traces (list): A list of dictionaries, each describing a trace to plot.
                            Each dict should contain:
                            - 'df' (pd.DataFrame): DataFrame with 'Frequency (MHz)' and a specified Y-axis column.
                            - 'name' (str): Name for the trace (used in legend).
                            - 'color' (str): Line color (e.g., 'blue', 'rgba(150, 150, 150, 0.5)').
                            - 'dash' (str, optional): Line dash style (e.g., 'solid', 'dot', 'dash').
                            - 'width' (int, optional): Line width.
                            - 'show_legend' (bool, optional): Whether to show this trace in the legend.
                            - 'y_column_name' (str): The name of the column to use for the Y-axis (e.g., 'Power (dBm)', 'Average').
        plot_title (str): Title of the plot.
        include_tv_markers (bool): Whether to include TV channel markers.
        include_gov_markers (bool): Whether to include Government band markers.
        include_markers (bool): Whether to include custom markers from MARKERS.CSV.
        include_intermod_markers (bool): Whether to include Intermodulation markers (logic to be implemented).
        output_html_path (str, optional): Full path to save the HTML plot.
        y_range_min_override (float, optional): If provided, overrides the calculated minimum Y-axis value.
        y_range_max_override (float, optional): If provided, overrides the calculated maximum Y-axis value (default 0).
        console_print_func (function, optional): Function to print messages to the GUI console.
        scan_data_folder (str, optional): Path to the folder containing scan data, used for finding MARKERS.CSV.

    Returns:
        tuple: A tuple containing the Plotly figure object and the output HTML path,
               or (None, None) if an error occurs.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering {current_function} with plot_title: {plot_title}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Data traces for plotting: {[{'name': t['name'], 'y_column_name': t['y_column_name'], 'df_head': t['df'].head().to_dict('records')} for t in data_traces if not t['df'].empty]}", file=current_file, function=current_function, console_print_func=console_print_func)


    if not data_traces:
        if console_print_func:
            console_print_func("No data traces provided, cannot create plot.")
        debug_print("No data traces provided, cannot create plot.", file=current_file, function=current_function, console_print_func=console_print_func)
        return None, None

    fig = go.Figure()
    all_power_data = []
    min_freq_overall = float('inf')
    max_freq_overall = float('-inf')

    # Add all data traces to the figure
    for trace_info in data_traces:
        df = trace_info['df']
        name = trace_info['name']
        color = trace_info.get('color', 'blue')
        dash = trace_info.get('dash', 'solid')
        width = trace_info.get('width', 2)
        show_legend = trace_info.get('show_legend', True)
        y_column_name = trace_info.get('y_column_name', 'Power (dBm)') # Default to 'Power (dBm)'

        # Check for correct column names before plotting
        if df.empty or 'Frequency (MHz)' not in df.columns or y_column_name not in df.columns:
            if console_print_func:
                console_print_func(f"Warning: Skipping trace '{name}' due to empty DataFrame or missing 'Frequency (MHz)'/'{y_column_name}' columns.")
            debug_print(f"Skipping trace '{name}': Invalid DataFrame (missing 'Frequency (MHz)' or '{y_column_name}').", file=current_file, function=current_function, console_print_func=console_print_func)
            continue

        fig.add_trace(go.Scatter(
            x=df['Frequency (MHz)'],
            y=df[y_column_name], # Use the specified y_column_name
            mode='lines',
            name=name,
            line=dict(color=color, width=width, dash=dash),
            showlegend=show_legend
        ))
        debug_print(f"Added trace: '{name}' (Y-axis: '{y_column_name}') with color '{color}'.", file=current_file, function=current_function, console_print_func=console_print_func)

        all_power_data.extend(df[y_column_name].tolist())
        min_freq_overall = min(min_freq_overall, df['Frequency (MHz)'].min())
        max_freq_overall = max(max_freq_overall, df['Frequency (MHz)'].max())

    if not all_power_data:
        if console_print_func:
            console_print_func("No valid data points found across all traces. Cannot create plot.")
        debug_print("No valid data points to plot.", file=current_file, function=current_function, console_print_func=console_print_func)
        return None, None

    shapes = []
    annotations = []

    # Determine Y-axis range for markers, if not overridden
    data_y_min = min(all_power_data)
    data_y_max = max(all_power_data)

    y_plot_min = y_range_min_override if y_range_min_override is not None else data_y_min - 5 # Add some padding
    y_plot_max = y_range_max_override if y_range_max_override is not None else data_y_max + 5 # Add some padding

    # Ensure a reasonable default range if data is flat or single point
    if y_plot_max <= y_plot_min:
        y_plot_min = -100
        y_plot_max = 0

    # Staggered Y-offset levels for text markers (relative to plot height)
    y_offset_levels_tv_gov = [0.05, 0.10, 0.15, 0.20, 0.25] # Relative to the top of the plot
    # y_offset_levels_custom = [0.01, 0.03, 0.05, 0.07, 0.09] # Smaller offsets for custom markers to stack tightly

    if include_tv_markers:
        debug_print("Adding TV Band Markers.", file=current_file, function=current_function, console_print_func=console_print_func)
        for i, band in enumerate(TV_PLOT_BAND_MARKERS):
            # Corrected keys to match frequency_bands.py
            if 'Start MHz' in band and 'Stop MHz' in band:
                start_mhz = band['Start MHz']
                end_mhz = band['Stop MHz']
                shapes.append(
                    dict(
                        type="rect", xref="x", yref="paper", x0=start_mhz, y0=0, x1=end_mhz, y1=1,
                        fillcolor=band.get('fill_color', "rgba(255, 165, 0, 0.1)"), line=dict(color=band.get('line_color', "orange"), width=1),
                        opacity=0.3, layer="below"
                    )
                )
                mid_mhz = (start_mhz + end_mhz) / 2
                current_y_offset_ratio = y_offset_levels_tv_gov[i % len(y_offset_levels_tv_gov)]
                y_text_position = y_plot_max - (y_plot_max - y_plot_min) * current_y_offset_ratio

                annotations.append(
                    dict(
                        x=mid_mhz, y=y_text_position,
                        xref="x", yref="y",
                        text=band['Band Name'], showarrow=False, # Use "Band Name"
                        font=dict(color=band.get('text_color', "orange"), size=8), xanchor="center", yanchor="bottom",
                        bgcolor="rgba(0,0,0,0.5)", bordercolor="orange", borderwidth=0.5
                    )
                )
            else:
                debug_print(f"Warning: TV Band Marker {band.get('Band Name', 'Unknown')} missing 'Start MHz' or 'Stop MHz'.", file=current_file, function=current_function, console_print_func=console_print_func)


    if include_gov_markers:
        debug_print("Adding Government Band Markers.", file=current_file, function=current_function, console_print_func=console_print_func)
        for i, band in enumerate(GOV_PLOT_BAND_MARKERS):
            # Corrected keys to match frequency_bands.py
            if 'Start MHz' in band and 'Stop MHz' in band:
                start_mhz = band['Start MHz']
                end_mhz = band['Stop MHz']
                shapes.append(
                    dict(
                        type="rect", xref="x", yref="paper", x0=start_mhz, y0=0, x1=end_mhz, y1=1,
                        fillcolor=band.get('fill_color', "rgba(144, 238, 144, 0.1)"), line=dict(color=band.get('line_color', "lightgreen"), width=1),
                        opacity=0.3, layer="below"
                    )
                )
                mid_mhz = (start_mhz + end_mhz) / 2
                current_y_offset_ratio = y_offset_levels_tv_gov[(i + 1) % len(y_offset_levels_tv_gov)]
                y_text_position = y_plot_max - (y_plot_max - y_plot_min) * current_y_offset_ratio

                annotations.append(
                    dict(
                        x=mid_mhz, y=y_text_position,
                        xref="x", yref="y",
                        text=band['Band Name'], showarrow=False, # Use "Band Name"
                        font=dict(color=band.get('text_color', "lightgreen"), size=8), xanchor="center", yanchor="bottom",
                        bgcolor="rgba(0,0,0,0.5)", bordercolor="lightgreen", borderwidth=0.5
                    )
                )
            else:
                debug_print(f"Warning: Government Band Marker {band.get('Band Name', 'Unknown')} missing 'Start MHz' or 'Stop MHz'.", file=current_file, function=current_function, console_print_func=console_print_func)

    if include_markers:
        debug_print("Adding custom markers from MARKERS.CSV.", file=current_file, function=current_function, console_print_func=console_print_func)
        # Pass the current figure and a representative dataframe for range filtering
        # For multi-trace, we can use the first dataframe, or a combined one for range.
        # Here, we pass the first dataframe from data_traces.
        if data_traces:
            custom_shapes, custom_annotations = _load_custom_markers(data_traces[0]['df'], console_print_func, scan_data_folder)
            shapes.extend(custom_shapes)
            annotations.extend(custom_annotations)


    if include_intermod_markers:
        debug_print("Adding Intermodulation markers (logic to be implemented).", file=current_file, function=current_function, console_print_func=console_print_func)
        # TODO: Implement logic to load and add intermodulation markers here
        pass


    fig.update_layout(
        title={'text': plot_title, 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
        xaxis_title="Frequency (MHz)",
        yaxis_title="Power (dBm)", # Default Y-axis title
        hovermode="x unified",
        template="plotly_dark",
        margin=dict(l=50, r=50, t=80, b=50),
        # Set height and width to None for responsiveness
        height=None,
        width=None,
        autosize=True, # Enable autosize for responsiveness
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.98, bgcolor="rgba(0,0,0,0.5)", bordercolor="white", borderwidth=1, font=dict(size=9)),
        shapes=shapes,
        annotations=annotations
    )
    debug_print("Plotly layout updated with shapes and annotations.", file=current_file, function=current_function, console_print_func=console_print_func)

    # Apply Y-axis range
    fig.update_yaxes(range=[y_plot_min, y_plot_max])
    debug_print(f"Applied Y-axis range: {[y_plot_min, y_plot_max]}", file=current_file, function=current_function, console_print_func=console_print_func)


    if output_html_path:
        output_dir = os.path.dirname(output_html_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            debug_print(f"Created directory for plot: {output_html_path}", file=current_file, function=current_function, console_print_func=console_print_func)
        debug_print(f"Saving plot to: {output_html_path}", file=current_file, function=current_function, console_print_func=console_print_func)
        fig.write_html(output_html_path, auto_open=False)
        debug_print(f"✅ Plot saved to: {output_html_path}", file=current_file, function=current_function, console_print_func=console_print_func)
        debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
        return fig, output_html_path
    else:
        debug_print("No output_html_path provided, returning figure object only.", file=current_file, function=current_function, console_print_func=console_print_func)
        debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
        return fig, None


def plot_single_scan_data(
    df,
    plot_title,
    include_tv_markers=False,
    include_gov_markers=False,
    include_markers=True,
    include_intermod_markers=False,
    output_html_path=None,
    y_range_min_override=None,
    y_range_max_override=0,
    console_print_func=None,
    scan_data_folder=None
):
    """
    Generates an interactive Plotly HTML plot for a single scan's frequency vs. amplitude data.
    This function is a wrapper for the unified _create_spectrum_plot.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Calling _create_spectrum_plot for single scan: {plot_title}", file=current_file, function=current_function, console_print_func=console_print_func)

    if df.empty:
        if console_print_func:
            console_print_func("DataFrame is empty, cannot plot single scan.")
        debug_print("DataFrame is empty, cannot plot single scan.", file=current_file, function=current_function, console_print_func=console_print_func)
        return None, None

    # Ensure 'Frequency (MHz)' column exists for plotting
    df_plot = df.copy()
    if 'Frequency (Hz)' in df_plot.columns: # If 'Frequency (Hz)' column exists, assume it contains MHz values and rename
        df_plot.rename(columns={'Frequency (Hz)': 'Frequency (MHz)'}, inplace=True)
        debug_print("Renamed 'Frequency (Hz)' column to 'Frequency (MHz)' as it appears to contain MHz values.", file=current_file, function=current_function, console_print_func=console_print_func)
    elif 'Frequency (MHz)' not in df_plot.columns: # If neither Hz nor MHz column is found
        if console_print_func:
            console_print_func("Error: Input DataFrame for single scan plot is missing 'Frequency (Hz)' or 'Frequency (MHz)' column.")
        debug_print("Input DataFrame for single scan plot is missing frequency column.", file=current_file, function=current_function, console_print_func=console_print_func)
        return None, None
    
    # Prepare data for the unified plotting function
    data_traces = [{
        'df': df_plot,
        'name': 'Current Scan',
        'color': 'blue',
        'width': 2,
        'dash': 'solid',
        'show_legend': True,
        'y_column_name': 'Power (dBm)' # Specify the Y-axis column name
    }]

    return _create_spectrum_plot(
        data_traces,
        plot_title,
        include_tv_markers,
        include_gov_markers,
        include_markers,
        include_intermod_markers,
        output_html_path,
        y_range_min_override,
        y_range_max_override,
        console_print_func,
        scan_data_folder
    )


def plot_multi_trace_data(
    aggregated_df,
    plot_title,
    include_tv_markers=False,
    include_gov_markers=False,
    include_markers=True,
    include_intermod_markers=False,
    historical_dfs_with_names=None, # List of {'df': DataFrame, 'name': str}
    individual_scan_dfs_with_names=None, # List of (DataFrame, str)
    output_html_path=None,
    y_range_min_override=None,
    y_range_max_override=0,
    console_print_func=None,
    scan_data_folder=None
):
    """
    Generates an interactive Plotly HTML plot for aggregated scan data and historical/individual overlays.
    This function is a wrapper for the unified _create_spectrum_plot.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Calling _create_spectrum_plot for multi-trace plot: {plot_title}", file=current_file, function=current_function, console_print_func=console_print_func)

    data_traces = []

    # Prepare aggregated_df for plotting: convert Frequency (Hz) to (MHz) if necessary
    aggregated_df_plot = aggregated_df.copy()
    # If 'Frequency (Hz)' column exists, assume it contains MHz values and rename
    if 'Frequency (Hz)' in aggregated_df_plot.columns:
        aggregated_df_plot.rename(columns={'Frequency (Hz)': 'Frequency (MHz)'}, inplace=True)
        debug_print("Renamed 'Frequency (Hz)' column to 'Frequency (MHz)' in aggregated_df_plot as it appears to contain MHz values.", file=current_file, function=current_function, console_print_func=console_print_func)
    elif 'Frequency (MHz)' not in aggregated_df_plot.columns:
        if console_print_func:
            console_print_func("Error: Aggregated DataFrame for multi-trace plot is missing 'Frequency (Hz)' or 'Frequency (MHz)' column.")
        debug_print("Aggregated DataFrame for multi-trace plot is missing frequency column.", file=current_file, function=current_function, console_print_func=console_print_func)
        return None, None

    # Determine which columns from aggregated_df_plot to plot as traces
    # These are the "power-like" columns from the COMPLETE_MATH CSV
    # Exclude 'Frequency (MHz)' itself
    plot_value_columns = [col for col in aggregated_df_plot.columns if col != 'Frequency (MHz)']

    if not aggregated_df_plot.empty and plot_value_columns:
        for column in plot_value_columns:
            # Assign colors and dash styles based on column name
            color_map = {
                'Average': 'lime',
                'Median': 'yellow',
                'Range': 'orange',
                'Std Dev': 'magenta', # Corrected from 'Standard Deviation' to match CSV
                'Variance': 'purple',
                'PSD (dBm/Hz)': 'red' # Corrected from 'Power Spectral Density (PSD)' to match CSV
            }
            dash_map = {
                'Average': 'solid',
                'Median': 'dot',
                'Range': 'dash',
                'Std Dev': 'longdash',
                'Variance': 'dot', # Changed from 'shortdot' to 'dot'
                'PSD (dBm/Hz)': 'solid'
            }
            
            data_traces.append({
                'df': aggregated_df_plot,
                'name': column, # Use the actual column name for the legend
                'color': color_map.get(column, 'white'),
                'width': 2 if column == 'Average' else 1,
                'dash': dash_map.get(column, 'solid'),
                'show_legend': True,
                'y_column_name': column # Specify the column to use for Y-axis
            })
    else:
        if console_print_func:
            console_print_func("Warning: Aggregated DataFrame is empty or has no plotable columns. Skipping main aggregated traces.")
        debug_print("Aggregated DataFrame empty or no plotable columns.", file=current_file, function=current_function, console_print_func=console_print_func)


    # Add historical overlays (ensure frequency conversion if needed)
    if historical_dfs_with_names:
        for i, item in enumerate(historical_dfs_with_names):
            df_hist = item['df'].copy()
            if 'Frequency (Hz)' in df_hist.columns: # If 'Frequency (Hz)' column exists, assume it contains MHz values and rename
                df_hist.rename(columns={'Frequency (Hz)': 'Frequency (MHz)'}, inplace=True)
                debug_print(f"Renamed 'Frequency (Hz)' column to 'Frequency (MHz)' in historical DF '{item['name']}' as it appears to contain MHz values.", file=current_file, function=current_function, console_print_func=console_print_func)
            
            name = item['name']
            if not df_hist.empty and 'Frequency (MHz)' in df_hist.columns and 'Power (dBm)' in df_hist.columns:
                data_traces.append({
                    'df': df_hist,
                    'name': f'{name} (Historical)',
                    'color': f'rgba(150, 150, 150, {max(0, 0.5 - i * 0.1)})', # Clamped alpha value
                    'width': 1,
                    'dash': 'solid',
                    'show_legend': True,
                    'y_column_name': 'Power (dBm)' # Historical scans will have 'Power (dBm)'
                })
            else:
                debug_print(f"Skipping historical DF '{name}': Invalid DataFrame.", file=current_file, function=current_function, console_print_func=console_print_func)

    # Add individual scan overlays (ensure frequency conversion if needed)
    if individual_scan_dfs_with_names:
        for i, (df_scan, name) in enumerate(individual_scan_dfs_with_names):
            df_scan_plot = df_scan.copy()
            if 'Frequency (Hz)' in df_scan_plot.columns: # If 'Frequency (Hz)' column exists, assume it contains MHz values and rename
                df_scan_plot.rename(columns={'Frequency (Hz)': 'Frequency (MHz)'}, inplace=True)
                debug_print(f"Renamed 'Frequency (Hz)' column to 'Frequency (MHz)' in individual scan DF '{name}' as it appears to contain MHz values.", file=current_file, function=current_function, console_print_func=console_print_func)

            if not df_scan_plot.empty and 'Frequency (MHz)' in df_scan_plot.columns and 'Power (dBm)' in df_scan_plot.columns:
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
                debug_print(f"Skipping individual scan DF '{name}': Invalid DataFrame.", file=current_file, function=current_function, console_print_func=console_print_func)

    if not data_traces:
        if console_print_func:
            console_print_func("No valid data to plot in multi-trace function.")
        debug_print("No valid data traces prepared for multi-trace plot.", file=current_file, function=current_function, console_print_func=console_print_func)
        return None, None

    return _create_spectrum_plot(
        data_traces,
        plot_title,
        include_tv_markers,
        include_gov_markers,
        include_markers,
        include_intermod_markers,
        output_html_path,
        y_range_min_override,
        y_range_max_override,
        console_print_func,
        scan_data_folder
    )
