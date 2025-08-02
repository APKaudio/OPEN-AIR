# process_math/ploting_intermod_zones.py
#
# This module provides a function for generating an interactive 3D Plotly plot
# of wireless microphone zones and optionally overlays intermodulation collisions.
# It visualizes the spatial arrangement of zones and highlights potential IMD issues.
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
# Version 20250802.0115.1 (Refactored debug_print to debug_log; updated imports and flair.)

current_version = "20250802.0115.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 115 * 1 # Example hash, adjust as needed

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple
import inspect # For debug_log
import os # For path manipulation

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log # Added for console_print_func

# Define ZoneData type for clarity (needs to be consistent with calculate_intermod.py)
ZoneData = Dict[str, Tuple[List[Tuple[float, str]], Tuple[float, float]]]

def plot_zones(
    zones: ZoneData,
    imd_df: pd.DataFrame = None, # Pass the DataFrame directly
    html_filename: str = "zones_dashboard.html",
    color_code_severity: bool = True,
    console_print_func=None
) -> None:
    """
    Function Description:
    Plots wireless microphone zones and optionally overlays intermodulation collisions in 3D.

    Inputs:
    - zones (ZoneData): Dictionary mapping zone names to (list of (frequency, device_name) tuples, position tuple).
    - imd_df (pd.DataFrame): DataFrame containing intermodulation products,
                             including 'Frequency_MHz', 'Zone_1', 'Zone_2', 'Order', 'Severity',
                             'Device_1', 'Device_2', 'Parent_Freq1', 'Parent_Freq2'.
    - html_filename (str): Filename for the output HTML plot.
    - color_code_severity (bool): If True, color-code IMD collision annotations by severity.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Prepares zone data for plotting (positions, frequencies).
    2. Creates a 3D scatter plot for zones, with device frequencies as text labels.
    3. If `imd_df` is provided:
       a. Filters IMD products by severity (High/Medium) if `color_code_severity` is True.
       b. Adds annotations for IMD collision points, color-coded by severity.
       c. Adds lines connecting parent zones for cross-zone IMDs.
    4. Configures the 3D plot layout (title, axes labels, camera).
    5. Saves the plot to an HTML file.
    6. Logs the plotting process and success/failure.

    Outputs of this function:
    - None. Generates and saves an HTML plot file.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Plotting intermodulation zones! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"HTML filename: {html_filename}, Color code severity: {color_code_severity}. Plot settings ready!",
                file=current_file, version=current_version, function=current_function)

    # Plot zone positions
    zone_data_for_df = []
    for z, (freq_device_pairs, pos) in zones.items():
        frequencies_only = [f[0] for f in freq_device_pairs]
        device_names = [f[1] for f in freq_device_pairs]
        
        # Create a combined label for all devices in the zone
        device_labels = "<br>".join([f"{f:.3f} MHz ({d})" for f, d in freq_device_pairs])

        zone_data_for_df.append({
            'Zone': z,
            'X': pos[0],
            'Y': pos[1],
            'Z': sum(frequencies_only) / len(frequencies_only) if frequencies_only else 0, # Average frequency for Z-axis
            'Text': f"<b>{z}</b><br>{device_labels}",
            'Size': max(5, len(frequencies_only) * 2) # Size based on number of devices
        })
    
    if not zone_data_for_df:
        console_print_func("No zone data provided for plotting. Cannot generate plot. Nothing to visualize!")
        debug_log("No zone data for plotting. Plotting aborted!",
                    file=current_file, version=current_version, function=current_function)
        return

    zones_df = pd.DataFrame(zone_data_for_df)
    debug_log(f"Zones DataFrame created. Shape: {zones_df.shape}. Zones prepared!",
                file=current_file, version=current_version, function=current_function)

    fig = px.scatter_3d(zones_df,
                        x='X', y='Y', z='Z',
                        text='Text',
                        size='Size', # Use the calculated size
                        size_max=30, # Max size for bubbles
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                        title="Wireless Microphone Zones and Intermodulation Collisions")

    fig.update_traces(textposition='top center',
                      marker=dict(symbol='circle', opacity=0.8, line=dict(width=1, color='DarkSlateGrey')))

    # Add IMD collision points and annotations
    if imd_df is not None and not imd_df.empty:
        debug_log(f"IMD DataFrame provided. Shape: {imd_df.shape}. Overlaying IMD products!",
                    file=current_file, version=current_version, function=current_function)
        
        # Filter IMD products based on severity if color_code_severity is True
        if color_code_severity:
            imd_df_filtered = imd_df[imd_df['Severity'].isin(['High', 'Medium'])]
            debug_log(f"IMD DataFrame filtered by severity (High/Medium). Filtered count: {len(imd_df_filtered)}. Focusing on critical issues!",
                        file=current_file, version=current_version, function=current_function)
        else:
            imd_df_filtered = imd_df
            debug_log("IMD DataFrame not filtered by severity. Showing all IMDs!",
                        file=current_file, version=current_version, function=current_function)

        severity_colors = {
            "High": "red",
            "Medium": "orange",
            "Low": "yellow"
        }

        for _, row in imd_df_filtered.iterrows():
            imd_freq = row['Frequency_MHz']
            imd_order = row['Order']
            imd_type = row['Type']
            imd_severity = row['Severity']
            zone1_name = row['Zone_1']
            zone2_name = row['Zone_2']
            dist = row['Distance']
            dev1 = row['Device_1']
            dev2 = row['Device_2']
            parent_freq1 = row['Parent_Freq1']
            parent_freq2 = row['Parent_Freq2']

            # Find the position of Zone_1 (or Zone_2 if it's an intra-zone IMD)
            target_zone_name = zone1_name if imd_type == "Intra-Zone" else zone1_name # For cross-zone, use Zone_1's position for annotation
            
            if target_zone_name in zones:
                _, imd_pos = zones[target_zone_name]
                
                # Use the IMD frequency for the Z-axis position
                imd_z = imd_freq # Use actual frequency for Z-axis

                # Add IMD collision point
                fig.add_trace(go.Scatter3d(
                    x=[imd_pos[0]],
                    y=[imd_pos[1]],
                    z=[imd_z],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=severity_colors.get(imd_severity, 'grey'),
                        symbol='diamond',
                        opacity=0.9,
                        line=dict(width=1, color='black')
                    ),
                    name=f"IMD {imd_order} ({imd_severity})",
                    hoverinfo='text',
                    hovertext=f"<b>IMD Collision:</b> {imd_order}<br>"
                              f"Frequency: {imd_freq:.3f} MHz<br>"
                              f"Severity: {imd_severity}<br>"
                              f"Type: {imd_type}<br>"
                              f"Parent Freqs: {parent_freq1:.3f} MHz ({dev1}), {parent_freq2:.3f} MHz ({dev2})<br>"
                              f"Zone 1: {zone1_name}<br>"
                              f"Zone 2: {zone2_name}<br>"
                              f"Distance: {dist:.2f} m",
                    showlegend=False # Don't show legend for individual points
                ))
                debug_log(f"  Added IMD point: {imd_order} @ {imd_freq:.3f} MHz (Severity: {imd_severity}). Point placed!",
                            file=current_file, version=current_version, function=current_function)
            else:
                debug_log(f"  Skipping IMD point for {imd_order} at {imd_freq:.3f} MHz: Target zone '{target_zone_name}' not found. Zone missing!",
                            file=current_file, version=current_version, function=current_function)

            # Add lines connecting zones for cross-zone IMDs in 3D (only for high severity cross-zone IMDs)
            if imd_type == "Cross-Zone" and imd_severity in ["High", "Medium"]:
                if zone1_name in zones and zone2_name in zones:
                    x1, y1 = zones[zone1_name][1]
                    # Use the actual parent frequencies for Z-axis connections
                    z1 = parent_freq1
                    
                    x2, y2 = zones[zone2_name][1]
                    z2 = parent_freq2

                    fig.add_trace(go.Scatter3d(
                        x=[x1, x2],
                        y=[y1, y2],
                        z=[z1, z2],
                        mode='lines',
                        line=dict(color='lightgrey', width=2, dash='dot'),
                        name=f"Cross-Zone IMD Link ({imd_order})",
                        hoverinfo='text',
                        hovertext=f"<b>Cross-Zone Link:</b> {zone1_name} to {zone2_name}<br>"
                                  f"IMD: {imd_order} @ {imd_freq:.3f} MHz<br>"
                                  f"Distance: {dist:.2f} m",
                        showlegend=False
                    ))
                    debug_log(f"  Added cross-zone IMD link between {zone1_name} and {zone2_name} for {imd_order}. Link drawn!",
                                file=current_file, version=current_version, function=current_function)
                else:
                    debug_log(f"  Skipping cross-zone IMD link for {imd_order}: One or both zones ({zone1_name}, {zone2_name}) not found. Link missing!",
                                file=current_file, version=current_version, function=current_function)

    # Update layout for 3D plot
    fig.update_layout(
        scene=dict(
            xaxis_title='X Position (meters)',
            yaxis_title='Y Position (meters)',
            zaxis_title='Frequency (MHz)',
            bgcolor="#2e2e2e", # Dark background
            xaxis=dict(backgroundcolor="#3a3a3a", gridcolor="#4a4a4a"),
            yaxis=dict(backgroundcolor="#3a3a3a", gridcolor="#4a4a4a"),
            zaxis=dict(backgroundcolor="#3a3a3a", gridcolor="#4a4a4a"),
        ),
        font=dict(color="white"), # Font color for titles, labels, etc.
        title_font_color="white",
        paper_bgcolor="#2e2e2e", # Background of the entire plot area
        plot_bgcolor="#2e2e2e", # Background of the plotting area
        margin=dict(l=50, r=50, t=80, b=50),
        height=700, # Fixed height for better viewing
        width=1000, # Fixed width
        autosize=False, # Set to False when height/width are fixed
        showlegend=True # Show legend for zone types and IMD severity
    )
    debug_log("Plotly 3D layout updated. Aesthetics applied!",
                file=current_file, version=current_version, function=current_function)

    # Save the plot to HTML
    try:
        output_dir = os.path.dirname(html_filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            console_print_func(f"Created directory for IMD plot: {output_dir}.")
            debug_log(f"Created directory for IMD plot: {output_dir}. Folder ready!",
                        file=current_file, version=current_version, function=current_function)
        
        fig.write_html(html_filename, auto_open=False)
        console_print_func(f"✅ 3D Intermod Zone plot saved to: {html_filename}. Success!")
        debug_log(f"3D Intermod Zone plot saved to: {html_filename}. File exported!",
                    file=current_file, version=current_version, function=current_function)
    except Exception as e:
        console_print_func(f"❌ Error saving 3D Intermod Zone plot to HTML: {e}. This is a disaster!")
        debug_log(f"Error saving 3D Intermod Zone plot to HTML: {e}. Export failed!",
                    file=current_file, version=current_version, function=current_function)
        # Re-raise the exception to be handled by the caller, or return None
        raise

    debug_log(f"Exiting {current_function}. IMD zone plotting complete! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
