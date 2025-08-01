# process_math/ploting_intermod_zones.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple

# Define ZoneData type for clarity (needs to be consistent with calculate_intermod.py)
ZoneData = Dict[str, Tuple[List[Tuple[float, str]], Tuple[float, float]]]

def plot_zones(
    zones: ZoneData,
    imd_df: pd.DataFrame = None, # Pass the DataFrame directly
    html_filename: str = "zones_dashboard.html",
    color_code_severity: bool = True
) -> None:
    """
    Plots wireless microphone zones and optionally overlays intermodulation collisions in 3D.

    Args:
        zones (ZoneData): Dictionary mapping zone names to (list of (frequency, device_name) tuples, position tuple).
        imd_df (pd.DataFrame): DataFrame containing intermodulation products,
                                including 'Frequency_MHz', 'Zone_1', 'Zone_2', 'Order', 'Severity',
                                'Device_1', 'Device_2', 'Parent_Freq1', 'Parent_Freq2'.
        html_filename (str): Filename for the output HTML plot.
        color_code_severity (bool): If True, color-code IMD collision annotations by severity.
    """

    # Plot zone positions
    zone_data_for_df = []
    for z, (freq_device_pairs, pos) in zones.items():
        frequencies_only = [f[0] for f in freq_device_pairs]
        device_names_only = [f[1] for f in freq_device_pairs]

        # Calculate average frequency for the zone to use as its Z-coordinate
        avg_freq = sum(frequencies_only) / len(frequencies_only) if frequencies_only else 0
        z_scaled = avg_freq / 100 # Scale for better visualization on Z-axis

        zone_data_for_df.append({
            "Zone": z,
            "Horizontal (m)": pos[0],
            "Vertical (m)": pos[1],
            "Z": z_scaled, # New Z-coordinate for the zone
            "Average_Frequency_MHz": avg_freq, # For hover info
            "Frequencies": ", ".join(f"{f:.1f}" for f in frequencies_only),
            "Devices": ", ".join(device_names_only)
        })
    zone_df = pd.DataFrame(zone_data_for_df)

    # Use px.scatter_3d for the initial zone plot
    fig = px.scatter_3d(zone_df, x="Horizontal (m)", y="Vertical (m)", z="Z", text="Zone",
                     color="Zone", 
                     # Include average frequency, full frequencies, and devices in hover data
                     hover_data=["Average_Frequency_MHz", "Frequencies", "Devices"],
                     title="Wireless Mic Zones — Horizontal vs Vertical Distance (3D)",
                     height=700)

    fig.update_traces(textposition='top center', marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')))
    fig.update_layout(
        legend_title_text='Zones',
        xaxis_title="Horizontal (m)",
        yaxis_title="Vertical (m)",
        scene=dict(
            zaxis_title="Average Frequency (MHz / 100)" # Label for the new Z-axis
        )
    )

    # Define colors for severity
    severity_colors = {
        "High": "red",
        "Medium": "orange",
        "Low": "green",
        "Unknown": "grey"
    }

    # Add collisions as scatter annotations if imd_df is provided
    if imd_df is not None and not imd_df.empty:
        # Filter for only 'High' severity IMD products
        high_severity_imd_df = imd_df[imd_df['Severity'] == 'High'].copy()
        
        # Filter for Cross-Zone IMDs from the high_severity_imd_df for plotting connections between zones
        cross_zone_imd_df = high_severity_imd_df[high_severity_imd_df['Type'] == "Cross-Zone"].copy()

        # Add trace for IMD collision points (midpoints)
        imd_points_data = []
        for _, row in high_severity_imd_df.iterrows(): # Iterate over high severity IMDs
            zone1_name = row["Zone_1"]
            zone2_name = row["Zone_2"]
            freq = row["Frequency_MHz"]
            order = row["Order"]
            severity = row["Severity"]
            device1 = row.get("Device_1", "N/A")
            device2 = row.get("Device_2", "N/A")

            # For intra-zone IMDs, we can use the zone's own coordinates for plotting the point
            # For cross-zone, use midpoint as before
            if row["Type"] == "Intra-Zone":
                if zone1_name in zones:
                    x, y = zones[zone1_name][1]
                    # For intra-zone, the IMD point is at the zone's location
                    # Use the actual IMD frequency for the Z-axis
                    imd_points_data.append({
                        "x": x,
                        "y": y,
                        "z": freq / 100, # Z-coordinate for IMD point, scaled
                        "text": f"{freq:.1f} MHz",
                        "order": order,
                        "severity": severity,
                        "tooltip": f"Order: {order}<br>Freq: {freq:.3f} MHz<br>Severity: {severity}<br>From: {device1} & {device2}"
                    })
            elif row["Type"] == "Cross-Zone":
                if zone1_name in zones and zone2_name in zones:
                    x1, y1 = zones[zone1_name][1]
                    x2, y2 = zones[zone2_name][1]
                    xm, ym = (x1 + x2) / 2, (y1 + y2) / 2  # midpoint

                    imd_points_data.append({
                        "x": xm,
                        "y": ym,
                        "z": freq / 100, # Z-coordinate for IMD point, scaled
                        "text": f"{freq:.1f} MHz",
                        "order": order,
                        "severity": severity,
                        "tooltip": f"Order: {order}<br>Freq: {freq:.3f} MHz<br>Severity: {severity}<br>From: {device1} & {device2}"
                    })


        if imd_points_data:
            imd_points_df = pd.DataFrame(imd_points_data)

            # Create 3D scatter plot for IMD points
            fig.add_trace(go.Scatter3d(
                x=imd_points_df["x"],
                y=imd_points_df["y"],
                z=imd_points_df["z"],
                mode='markers+text',
                marker=dict(
                    size=8,
                    symbol='diamond', # Changed from 'star' to 'diamond'
                    color=[severity_colors.get(s, 'grey') for s in imd_points_df["severity"]] if color_code_severity else 'purple',
                    line=dict(width=1, color='DarkSlateGrey')
                ),
                text=imd_points_df["text"],
                textposition='top center',
                textfont=dict(size=8),
                hovertemplate=imd_points_df["tooltip"] + "<extra></extra>",
                showlegend=True,
                name="High Severity IMD Collisions"
            ))

            # Add lines connecting zones for cross-zone IMDs in 3D (only for high severity cross-zone IMDs)
            for _, row in cross_zone_imd_df.iterrows():
                zone1_name = row["Zone_1"]
                zone2_name = row["Zone_2"]
                if zone1_name in zones and zone2_name in zones:
                    x1, y1 = zones[zone1_name][1]
                    freq_device_pairs1 = zones[zone1_name][0]
                    frequencies_only1 = [f[0] for f in freq_device_pairs1]
                    avg_freq1 = sum(frequencies_only1) / len(frequencies_only1) if frequencies_only1 else 0
                    z1_scaled = avg_freq1 / 100

                    x2, y2 = zones[zone2_name][1]
                    freq_device_pairs2 = zones[zone2_name][0]
                    frequencies_only2 = [f[0] for f in freq_device_pairs2]
                    avg_freq2 = sum(frequencies_only2) / len(frequencies_only2) if frequencies_only2 else 0
                    z2_scaled = avg_freq2 / 100

                    fig.add_trace(go.Scatter3d(
                        x=[x1, x2],
                        y=[y1, y2],
                        z=[z1_scaled, z2_scaled],
                        mode='lines',
                        line=dict(color='lightgrey', width=1, dash='dot'),
                        hoverinfo='skip',
                        showlegend=False
                    ))

    fig.write_html(html_filename)
    print(f"\n📁 Dashboard saved as: {html_filename}")
