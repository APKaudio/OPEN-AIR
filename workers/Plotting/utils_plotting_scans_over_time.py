# utils/utils_plotting_scans_over_time.py
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
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250801.2245.1 (Refactored debug_print to use debug_log and console_log.)

current_version = "20250801.2245.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250801 * 2245 * 1 # Example hash, adjust as needed

import pandas as pd
import plotly.graph_objects as go
import plotly.colors as pcolors # For color scales
import webbrowser
import os
import re
import inspect
from datetime import datetime

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

# Import constants from frequency_bands.py - CORRECTED PATH
try:
    from ref.ref_frequency_bands import MHZ_TO_HZ
except ImportError:
    debug_log("Error: frequency_bands.py not found in 'ref' or current directory. Using default MHZ_TO_HZ. This is a goddamn mess!",
                file=__file__,
                version=current_version,
                function=inspect.currentframe().f_code.co_name)
    MHZ_TO_HZ = 1_000_000 # Default fallback


def plot_Scans_over_time(grouped_csv_files, selected_group_prefix, output_folder,
                         amplitude_threshold_dbm, console_print_func):
    """
    Function Description:
    Generates an interactive 3D Plotly plot of spectrum analyzer scan data over time.
    It visualizes frequency, amplitude, and the time of each scan, with amplitude
    color-coded based on a user-defined threshold.

    Inputs to this function:
        grouped_csv_files (dict): A dictionary where keys are group prefixes (str) and values are
                                  lists of full file paths to CSV scan data.
        selected_group_prefix (str): The prefix of the group to be plotted.
        output_folder (str): The directory where the HTML plot file will be saved.
        amplitude_threshold_dbm (float): The amplitude threshold (in dBm) for color-coding.
        console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
        1. Checks if the selected group exists and contains files.
        2. Initializes lists to store frequency, power, and time data.
        3. Iterates through each CSV file in the selected group:
           a. Reads the CSV into a Pandas DataFrame, assuming 'Frequency (Hz)' and 'Power (dBm)' columns.
           b. Extracts frequency, power, and a timestamp for each scan.
           c. Appends the data to the respective lists.
        4. Creates a Pandas DataFrame from the collected data (Frequency, Power, Time).
        5. Creates a 3D scatter plot using `plotly.graph_objects.Scatter3d`.
           - X-axis: Frequency (Hz)
           - Y-axis: Time (numerical representation for plotting)
           - Z-axis: Power (dBm)
           - Color: Based on `Power (dBm)` relative to `amplitude_threshold_dbm`.
        6. Configures the 3D plot layout (title, axis labels, camera settings).
        7. Saves the figure to an HTML file in the specified `output_folder`.
        8. Logs progress and errors to the console and debug log.

    Outputs of this function:
        tuple: (go.Figure, str or None) - The Plotly figure object and the path to the saved HTML file (or None).

    (2025-07-31) Change: Initial implementation for 3D plotting.
    (2025-08-01) Change: Updated debug_print to debug_log.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function} for group '{selected_group_prefix}' with threshold {amplitude_threshold_dbm} dBm.",
                file=__file__,
                version=current_version,
                function=current_function)

    files_to_plot = grouped_csv_files.get(selected_group_prefix)
    if not files_to_plot:
        console_print_func(f"Error: No files found for group '{selected_group_prefix}'. What the hell am I supposed to plot?!")
        debug_log(f"No files found for group '{selected_group_prefix}'. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return None, None

    all_frequencies = []
    all_powers = []
    all_times = []
    time_labels = [] # To store human-readable time labels for hover text

    # Sort files by creation time to ensure correct time progression
    files_to_plot.sort(key=os.path.getctime)

    start_time = None

    for file_path in files_to_plot:
        try:
            df = pd.read_csv(file_path, header=None, names=['Frequency (Hz)', 'Power (dBm)'])
            # Extract timestamp from filename or file modification time
            # Assuming filename format like "PREFIX_YYYYMMDD_HHMMSS.csv" or similar
            filename = os.path.basename(file_path)
            match = re.search(r'(\d{8}_\d{6})', filename)
            if match:
                timestamp_str = match.group(1)
                scan_datetime = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
            else:
                # Fallback to file modification time if no timestamp in filename
                scan_datetime = datetime.fromtimestamp(os.path.getmtime(file_path))
                debug_log(f"No timestamp in filename for {filename}. Using file modification time. This is a bit of a mess!",
                            file=__file__,
                            version=current_version,
                            function=current_function)

            if start_time is None:
                start_time = scan_datetime

            # Calculate time difference in seconds from the first scan
            time_diff_seconds = (scan_datetime - start_time).total_seconds()

            all_frequencies.extend(df['Frequency (Hz)'].tolist())
            all_powers.extend(df['Power (dBm)'].tolist())
            all_times.extend([time_diff_seconds] * len(df))
            time_labels.extend([scan_datetime.strftime('%Y-%m-%d %H:%M:%S')] * len(df))

            debug_log(f"Processed file: {filename}, Scan Time: {scan_datetime.strftime('%H:%M:%S')}, Time Offset: {time_diff_seconds:.2f}s",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        except Exception as e:
            console_print_func(f"❌ Error processing file {os.path.basename(file_path)} for 3D plot: {e}. This file is a stubborn bastard!")
            debug_log(f"Error processing {file_path} for 3D plot: {e}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            continue

    if not all_frequencies:
        console_print_func("No valid scan data found to create 3D plot. This is utterly useless!")
        debug_log("No valid scan data for 3D plot.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return None, None

    df_3d = pd.DataFrame({
        'Frequency (Hz)': all_frequencies,
        'Power (dBm)': all_powers,
        'Time (s)': all_times,
        'Time Label': time_labels
    })

    # Create a color scale based on the amplitude threshold
    colorscale = [
        [0, 'blue'], # Below threshold
        [max(0.0, (amplitude_threshold_dbm + 100) / 100), 'green'], # Around threshold (adjust 100 based on expected power range)
        [max(0.0, (amplitude_threshold_dbm + 50) / 100), 'yellow'],
        [max(0.0, (amplitude_threshold_dbm + 20) / 100), 'orange'],
        [1, 'red'] # Above threshold
    ]
    # Normalize the threshold to 0-1 range for colorscale mapping. Assuming power range -100 to 0 dBm
    # This might need adjustment based on typical power ranges.
    normalized_threshold = (amplitude_threshold_dbm + 100) / 100.0
    colorscale = [
        [0, 'blue'],
        [max(0.0, normalized_threshold - 0.05), 'green'], # Slightly below threshold
        [normalized_threshold, 'yellow'], # At threshold
        [min(1.0, normalized_threshold + 0.05), 'red'], # Slightly above threshold
        [1, 'darkred'] # Significantly above threshold
    ]
    # Ensure the colorscale points are ordered correctly
    colorscale.sort(key=lambda x: x[0])
    debug_log(f"Generated colorscale: {colorscale}",
                file=__file__,
                version=current_version,
                function=current_function)


    # Create the 3D scatter plot
    fig = go.Figure(data=[go.Scatter3d(
        x=df_3d['Frequency (Hz)'],
        y=df_3d['Time (s)'],
        z=df_3d['Power (dBm)'],
        mode='markers',
        marker=dict(
            size=3,
            color=df_3d['Power (dBm)'], # Color by power
            colorscale=colorscale, # Apply custom colorscale
            colorbar=dict(title='Power (dBm)'),
            cmin=-100, # Adjust based on expected min power
            cmax=0 # Adjust based on expected max power
        ),
        hoverinfo='text',
        hovertext=[
            f"Freq: {f/MHZ_TO_HZ:.3f} MHz<br>Power: {p:.2f} dBm<br>Time: {t_label}"
            for f, p, t_label in zip(df_3d['Frequency (Hz)'], df_3d['Power (dBm)'], df_3d['Time Label'])
        ]
    )])
    debug_log("Plotly 3D Scatter3d trace created.",
                file=__file__,
                version=current_version,
                function=current_function)

    # Update layout
    fig.update_layout(
        title={
            'text': f"3D Scans Over Time: {selected_group_prefix} (Threshold: {amplitude_threshold_dbm} dBm)",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        scene=dict(
            xaxis_title='Frequency (Hz)',
            yaxis_title='Time (seconds from start)',
            zaxis_title='Power (dBm)',
            xaxis=dict(
                type='linear', # Can also be 'log' if frequencies span wide range
                tickformat=".3s", # Format ticks nicely
                tickangle=-45,
                nticks=10,
                backgroundcolor="#2d2d2d", # Dark background for axes
                gridcolor="#444444",
                zerolinecolor="#666666"
            ),
            yaxis=dict(
                type='linear',
                backgroundcolor="#2d2d2d",
                gridcolor="#444444",
                zerolinecolor="#666666"
            ),
            zaxis=dict(
                type='linear',
                backgroundcolor="#2d2d2d",
                gridcolor="#444444",
                zerolinecolor="#666666"
            ),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5) # Initial camera position
            )
        ),
        paper_bgcolor="#222222", # Dark background for the plot area
        plot_bgcolor="#222222", # Dark background for the plot itself
        font=dict(color="#cccccc"), # Font color for titles, labels, etc.
        # Removed the legend dictionary entirely to turn off the legend
        margin=dict(l=50, r=50, t=80, b=50),
        height=None,
        width=None,
        autosize=True,
        showlegend=False # Explicitly set showlegend to False to turn off the legend
    )
    debug_log("Plotly 3D layout updated.",
                file=__file__,
                version=current_version,
                function=current_function)

    output_html_path = os.path.join(output_folder, f"{selected_group_prefix}_3D_Scans_Over_Time_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

    if output_html_path:
        output_dir = os.path.dirname(output_html_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            debug_log(f"Created directory for plot: {output_html_path}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        debug_log(f"Saving 3D plot to: {output_html_path}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        fig.write_html(output_html_path, auto_open=False)
        console_print_func(f"✅ 3D plot saved to: {output_html_path}. Fucking brilliant!")
        debug_log(f"✅ 3D plot saved to: {output_html_path}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Output HTML path not provided, skipping saving 3D plot to file. What a waste!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    debug_log(f"Exiting {current_function}",
                file=__file__,
                version=current_version,
                function=current_function)
    return fig, output_html_path
