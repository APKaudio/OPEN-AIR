# utils/plot_scans_over_time.py
#
# This module provides a function for generating an interactive 3D Plotly plot
# of spectrum analyzer scan data over time. It visualizes frequency, amplitude,
# and the time of each scan, with amplitude color-coded based on user-defined
# thresholds.
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
import plotly.graph_objects as go
import plotly.colors as pcolors # For color scales
import webbrowser
import os
import re
import inspect
from datetime import datetime

# Import constants from frequency_bands.py
try:
    from ref.frequency_bands import MHZ_TO_HZ
except ImportError:
    print("Error: frequency_bands.py not found in 'ref' or current directory. Using default MHZ_TO_HZ.")
    MHZ_TO_HZ = 1_000_000

# Assuming debug_print exists or define a dummy one for standalone testing
try:
    from utils.instrument_control import debug_print
except ImportError:
    print("Warning: debug_print not found in utils.instrument_control. Using dummy.")
    def debug_print(*args, **kwargs):
        pass # Dummy function


def plot_Scans_over_time(
    individual_scan_dfs_with_names, # List of (DataFrame, str) - crucial for this plot
    plot_title,
    output_html_path=None,
    console_print_func=None,
    scan_data_folder=None # Used for finding MARKERS.CSV if needed, though not directly for 3D plot data
):
    """
    Generates a 3D interactive Plotly HTML plot showing individual spectrum scans over time.

    X-axis: Frequency (MHz)
    Y-axis: Time of the scan (derived from filename timestamp)
    Z-axis: Amplitude (Power in dBm)

    Amplitude is color-coded:
    - Red: >= 80% of max power for that particular scan
    - Orange: >= 50% and < 80% of max power for that particular scan
    - Green: < 50% of max power for that particular scan

    Inputs:
        individual_scan_dfs_with_names (list): A list of tuples, where each tuple contains
                                              (pandas.DataFrame, str). The DataFrame must have
                                              'Frequency (MHz)' and 'Power (dBm)' columns.
                                              The string is the scan's filename/identifier,
                                              expected to contain a YYYYMMDD_HHMMSS timestamp.
        plot_title (str): Title of the plot.
        output_html_path (str, optional): Full path to save the HTML plot.
        console_print_func (function, optional): Function to print messages to the GUI console.
        scan_data_folder (str, optional): Path to the folder containing scan data.

    Returns:
        tuple: A tuple containing the Plotly figure object and the output HTML path,
               or (None, None) if an error occurs or no valid data is provided.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering {current_function} with plot_title: {plot_title}", file=current_file, function=current_function, console_print_func=console_print_func)

    if not individual_scan_dfs_with_names:
        if console_print_func:
            console_print_func("No individual scan data provided for 3D plot.")
        debug_print("No individual scan data provided.", file=current_file, function=current_function, console_print_func=console_print_func)
        return None, None

    fig = go.Figure()
    
    # Collect all power data to determine global min/max for Z-axis range if needed
    all_power_data = []
    all_frequencies = [] # To collect all frequencies for the slider range

    # Process each individual scan
    for i, (df_scan, name) in enumerate(individual_scan_dfs_with_names):
        # Ensure 'Frequency (MHz)' and 'Power (dBm)' columns exist
        if df_scan.empty or 'Frequency (MHz)' not in df_scan.columns or 'Power (dBm)' not in df_scan.columns:
            if console_print_func:
                console_print_func(f"Warning: Skipping scan '{name}' due to empty DataFrame or missing required columns.")
            debug_print(f"Skipping scan '{name}': Invalid DataFrame.", file=current_file, function=current_function, console_print_func=console_print_func)
            continue

        # Extract timestamp for Y-axis
        # Assuming name format like "scan_name_YYYYMMDD_HHMMSS"
        time_value = i # Default to index if timestamp not found
        timestamp_str_match = re.search(r'(\d{8}_\d{6})', name)
        if timestamp_str_match:
            timestamp_str = timestamp_str_match.group(1)
            try:
                dt_object = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                # Use Unix timestamp (seconds since epoch) for numerical Y-axis
                time_value = dt_object.timestamp()
            except ValueError:
                if console_print_func:
                    console_print_func(f"Warning: Could not parse timestamp from '{name}'. Using sequential index for Y-axis.")
                debug_print(f"Could not parse timestamp from '{name}'. Using sequential index.", file=current_file, function=current_function, console_print_func=console_print_func)
        
        # Determine color based on amplitude thresholds for THIS scan
        max_power_this_scan = df_scan['Power (dBm)'].max()
        min_power_this_scan = df_scan['Power (dBm)'].min()

        # Handle cases where max_power_this_scan might be problematic (e.g., all same values)
        if max_power_this_scan == min_power_this_scan:
            red_threshold = max_power_this_scan
            orange_threshold = max_power_this_scan
        else:
            red_threshold = min_power_this_scan + (max_power_this_scan - min_power_this_scan) * 0.80
            orange_threshold = min_power_this_scan + (max_power_this_scan - min_power_this_scan) * 0.50

        colors = []
        for power_val in df_scan['Power (dBm)']:
            if power_val >= red_threshold:
                colors.append('red')
            elif power_val >= orange_threshold:
                colors.append('orange')
            else:
                colors.append('green')
        
        # Add the 3D trace for this scan
        fig.add_trace(go.Scatter3d(
            x=df_scan['Frequency (MHz)'], # Use the correct column name
            y=[time_value] * len(df_scan), # Y-axis is constant for each scan line
            z=df_scan['Power (dBm)'],
            mode='lines',
            name=name, # Use the full name for the legend
            line=dict(width=2, color=colors), # Apply per-point coloring
            showlegend=True # Keep this true for individual traces to appear in the legend
        ))
        debug_print(f"Added 3D trace for scan: '{name}' (Time: {time_value})", file=current_file, function=current_function, console_print_func=console_print_func)
        all_power_data.extend(df_scan['Power (dBm)'].tolist())
        all_frequencies.extend(df_scan['Frequency (MHz)'].tolist()) # Collect frequencies

    if not all_power_data:
        if console_print_func:
            console_print_func("No valid power data found across all scans. Cannot create 3D plot.")
        debug_print("No valid power data for 3D plot.", file=current_file, function=current_function, console_print_func=console_print_func)
        return None, None

    # Determine Z-axis range based on all collected power data
    z_min = min(all_power_data) - 5 # Add some padding
    z_max = max(all_power_data) + 5 # Add some padding

    # Determine X-axis range based on all collected frequencies
    x_min = min(all_frequencies) if all_frequencies else 0
    x_max = max(all_frequencies) if all_frequencies else 1

    # Create a custom tick format for the Y-axis (time)
    # This will convert Unix timestamps back to readable datetime strings
    # We need to find the min and max time values to set the range and ticks
    y_values = [trace.y[0] for trace in fig.data if trace.y] # Get the time value for each trace, ensure trace.y is not empty
    y_min_time = min(y_values) if y_values else 0
    y_max_time = max(y_values) if y_values else 1

    # Generate tick labels for time (e.g., every 10 minutes or hour depending on span)
    # For simplicity, we'll just show the start and end, and maybe a few in between
    # A more advanced approach would dynamically determine tick frequency.
    y_tickvals = sorted(list(set(y_values))) # Unique time values
    y_ticktext = [datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') for ts in y_tickvals]

    fig.update_layout(
        title={'text': plot_title, 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
        scene=dict(
            xaxis_title="Frequency (MHz)",
            yaxis_title="Time of Scan",
            zaxis_title="Power (dBm)",
            xaxis=dict(
                backgroundcolor="black",
                gridcolor="white",
                showbackground=True,
                zerolinecolor="white",
                range=[x_min, x_max], # Set initial X-axis range
                # Removed rangeslider and rangeselector as they are not supported in 3D scene.xaxis
            ),
            yaxis=dict(
                backgroundcolor="black",
                gridcolor="white",
                showbackground=True,
                zerolinecolor="white",
                tickmode='array',
                tickvals=y_tickvals,
                ticktext=y_ticktext,
                dtick=(y_max_time - y_min_time) / 5 if (y_max_time - y_min_time) > 0 else None # Attempt to get 5 ticks
            ),
            zaxis=dict(
                backgroundcolor="black",
                gridcolor="white",
                showbackground=True,
                zerolinecolor="white",
                range=[z_min, z_max] # Apply calculated Z-axis range
            ),
            bgcolor="black", # Scene background color
        ),
        paper_bgcolor="black", # Plot background color
        font=dict(color="white"), # Font color for titles, labels, etc.
        # Removed the legend dictionary entirely to turn off the legend
        margin=dict(l=50, r=50, t=80, b=50),
        height=None,
        width=None,
        autosize=True,
        showlegend=False # Explicitly set showlegend to False to turn off the legend
    )
    debug_print("Plotly 3D layout updated.", file=current_file, function=current_function, console_print_func=console_print_func)

    if output_html_path:
        output_dir = os.path.dirname(output_html_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            debug_print(f"Created directory for plot: {output_html_path}", file=current_file, function=current_function, console_print_func=console_print_func)
        debug_print(f"Saving 3D plot to: {output_html_path}", file=current_file, function=current_function, console_print_func=console_print_func)
        fig.write_html(output_html_path, auto_open=False)
        if console_print_func:
            console_print_func(f"✅ 3D plot saved to: {output_html_path}")
        debug_print(f"✅ 3D plot saved to: {output_html_path}", file=current_file, function=current_function, console_print_func=console_print_func)
        return fig, output_html_path
    else:
        debug_print("No output_html_path provided, returning figure object only.", file=current_file, function=current_function, console_print_func=console_print_func)
        return fig, None
