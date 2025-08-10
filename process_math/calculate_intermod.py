# process_math/calculate_intermod.py
#
# This module provides functions for calculating intermodulation distortion (IMD)
# products from a set of wireless microphone frequencies across multiple zones.
# It includes logic for determining IMD frequencies, their order (3rd, 5th),
# and their severity based on proximity to other active frequencies.
# It also handles filtering for in-band products and exporting results to CSV.
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
# Version 20250802.0100.1 (Refactored debug_print to debug_log; updated imports and flair.)

current_version = "20250802.0100.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 100 * 1 # Example hash, adjust as needed

import pandas as pd
import math
from typing import Dict, List, Tuple
import inspect # Used for enhanced debug printing context

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log # Added for console_print_func


# Define a type alias for better clarity:
# ZoneData maps zone names (str) to a tuple:
#  - a list of (frequency (float), device_name (str)) tuples
#  - a position in 2D space (Tuple[float, float]) (e.g., coordinates in meters)
ZoneData = Dict[str, Tuple[List[Tuple[float, str]], Tuple[float, float]]]

# Distance limit in meters for considering cross-zone intermodulation effects.
# Beyond this distance, cross-zone IMD products are ignored.
DISTANCE_LIMIT_METERS = 100

def euclidean_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """
    Function Description:
    Calculates the Euclidean distance between two 2D points.

    Inputs:
    - pos1 (Tuple[float, float]): The coordinates of the first point (x, y).
    - pos2 (Tuple[float, float]): The coordinates of the second point (x, y).

    Process of this function:
    1. Extracts x and y coordinates from both input tuples.
    2. Calculates the squared difference for x and y.
    3. Sums the squared differences and takes the square root to find the Euclidean distance.
    4. Logs the calculation using `debug_log`.

    Outputs of this function:
    - float: The Euclidean distance between the two points.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Calculating Euclidean distance! pos1: {pos1}, pos2: {pos2}. Version: {current_version}",
                file=current_file, version=current_version, function=current_function)

    # Ensure pos1 and pos2 are tuples of two floats
    if not (isinstance(pos1, tuple) and len(pos1) == 2 and
            isinstance(pos2, tuple) and len(pos2) == 2 and
            all(isinstance(coord, (int, float)) for coord in pos1 + pos2)):
        debug_log(f"Invalid input types for euclidean_distance. pos1: {type(pos1)}, pos2: {type(pos2)}. Expected tuples of floats!",
                    file=current_file, version=current_version, function=current_function)
        raise ValueError("pos1 and pos2 must be tuples of two numeric values.")

    dist = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    debug_log(f"Calculated distance: {dist:.2f} meters. Distance found! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    return dist

def _get_severity(order_label: str) -> str:
    """
    Function Description:
    Determines the severity level of an intermodulation product based on its order label.

    Inputs:
    - order_label (str): The label of the intermodulation product (e.g., "2f1-f2", "3f1-2f2").

    Process of this function:
    1. Checks if the label corresponds to a 3rd order IMD.
    2. Checks if the label corresponds to a 5th order IMD.
    3. Assigns "High" for 3rd order, "Medium" for 5th order, and "Low" for others.
    4. Logs the severity determination.

    Outputs of this function:
    - str: The severity level ("High", "Medium", "Low").
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Determining severity for: {order_label}. Version: {current_version}",
                file=current_file, version=current_version, function=current_function)

    if order_label in ["2f1-f2", "2f2-f1"]:
        severity = "High"
    elif order_label in ["3f1-2f2", "3f2-2f1"]:
        severity = "Medium"
    else:
        severity = "Low" # For 7th order and higher, or other types
    
    debug_log(f"Severity for {order_label} is: {severity}. Severity determined! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    return severity

def multi_zone_intermods(
    zones: ZoneData,
    in_band_low_freq: float,
    in_band_high_freq: float,
    export_csv: str,
    include_3rd_order: bool = True,
    include_5th_order: bool = True,
    include_cross_zone_imd: bool = True,
    console_print_func=None
) -> pd.DataFrame:
    """
    Function Description:
    Calculates intermodulation distortion (IMD) products for frequencies within and
    between multiple defined zones. It filters results based on order, in-band criteria,
    and inter-zone distance.

    Inputs:
    - zones (ZoneData): Dictionary mapping zone names to (frequencies, position).
    - in_band_low_freq (float): Lower frequency limit (in MHz) for in-band filtering.
    - in_band_high_freq (float): Upper frequency limit (in MHz) for in-band filtering.
    - export_csv (str): Full path to the CSV file where the results will be saved.
    - include_3rd_order (bool): If True, includes 3rd order IMD products.
    - include_5th_order (bool): If True, includes 5th order IMD products.
    - include_cross_zone_imd (bool): If True, includes cross-zone IMD products based on distance.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Initializes an empty list to store IMD results.
    2. Iterates through each zone to calculate intra-zone IMD products.
       a. For each pair of frequencies (f1, f2) within the zone, calculates 3rd and 5th order IMDs.
       b. Filters IMDs based on `include_3rd_order`, `include_5th_order`, and `in_band` criteria.
       c. Appends valid IMDs to the results list.
    3. If `include_cross_zone_imd` is True, iterates through pairs of zones to calculate cross-zone IMD products.
       a. Calculates Euclidean distance between zone centers.
       b. If distance is within `DISTANCE_LIMIT_METERS`, calculates IMDs for all frequency pairs
          between the two zones.
       c. Filters IMDs based on order and `in_band` criteria.
       d. Appends valid IMDs to the results list.
    4. Converts the results list to a Pandas DataFrame.
    5. Exports the DataFrame to a CSV file.
    6. Logs the process and results.

    Outputs of this function:
    - pandas.DataFrame: A DataFrame containing the calculated IMD products.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Calculating multi-zone intermodulation products! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"In-band range: {in_band_low_freq}-{in_band_high_freq} MHz. Filters active!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Include 3rd order: {include_3rd_order}, 5th order: {include_5th_order}, Cross-zone: {include_cross_zone_imd}. Options set!",
                file=current_file, version=current_version, function=current_function)

    results = []

    zone_names = list(zones.keys())
    
    # --- Intra-zone IMD calculations ---
    for zone_name in zone_names:
        freq_device_pairs, _ = zones[zone_name]
        frequencies = [f[0] for f in freq_device_pairs]
        devices = {f[0]: f[1] for f in freq_device_pairs} # Map frequency to device name

        num_freqs = len(frequencies)
        debug_log(f"Processing intra-zone IMD for Zone: {zone_name} with {num_freqs} frequencies. Starting calculations!",
                    file=current_file, version=current_version, function=current_function)

        for i in range(num_freqs):
            for j in range(i + 1, num_freqs):
                f1 = frequencies[i]
                f2 = frequencies[j]
                dev1 = devices[f1]
                dev2 = devices[f2]

                # Ensure f1 is always smaller for consistent calculation and labeling
                if f1 > f2:
                    f1, f2 = f2, f1
                    dev1, dev2 = dev2, dev1

                # 3rd Order IMD
                imd3_1 = (2 * f1) - f2
                imd3_2 = (2 * f2) - f1

                # 5th Order IMD
                imd5_1 = (3 * f1) - (2 * f2)
                imd5_2 = (3 * f2) - (2 * f1)

                imd_products = {
                    "2f1-f2": imd3_1,
                    "2f2-f1": imd3_2,
                    "3f1-2f2": imd5_1,
                    "3f2-2f1": imd5_2
                }
                
                for label, freq in imd_products.items():
                    # Check if IMD product is within the desired frequency range (in-band)
                    if in_band_low_freq <= freq <= in_band_high_freq:
                        is_3rd_order = label in ["2f1-f2", "2f2-f1"]
                        is_5th_order = label in ["3f1-2f2", "3f2-2f1"]

                        if (include_3rd_order and is_3rd_order) or \
                           (include_5th_order and is_5th_order):
                            results.append({
                                "Zone_1": zone_name,
                                "Zone_2": zone_name, # Same zone for intra-zone
                                "Type": "Intra-Zone",
                                "Order": label,
                                "Distance": 0.0, # Distance is 0 for intra-zone
                                "Frequency_MHz": round(freq, 3),
                                "Severity": _get_severity(label),
                                "Device_1": dev1,
                                "Device_2": dev2,
                                "Parent_Freq1": round(f1, 3), # ADDED
                                "Parent_Freq2": round(f2, 3)   # ADDED
                            })
                            debug_log(f"  Added intra-zone IMD: {label} @ {freq:.3f} MHz in {zone_name}. Found one!",
                                        file=current_file, version=current_version, function=current_function)
                    else:
                        debug_log(f"  Skipping intra-zone IMD {label} @ {freq:.3f} MHz (out of band). Not relevant!",
                                    file=current_file, version=current_version, function=current_function)

    # --- Cross-zone IMD calculations ---
    if include_cross_zone_imd:
        num_zones = len(zone_names)
        debug_log(f"Starting cross-zone IMD calculations. Total zones: {num_zones}. Bridging the gaps!",
                    file=current_file, version=current_version, function=current_function)

        for i in range(num_zones):
            for j in range(i + 1, num_zones):
                zone1_name = zone_names[i]
                zone2_name = zone_names[j]

                _, pos1 = zones[zone1_name]
                _, pos2 = zones[zone2_name]

                dist = euclidean_distance(pos1, pos2)
                debug_log(f"  Distance between {zone1_name} and {zone2_name}: {dist:.2f} meters. Checking proximity!",
                            file=current_file, version=current_version, function=current_function)

                if dist <= DISTANCE_LIMIT_METERS:
                    freq_device_pairs1, _ = zones[zone1_name]
                    freq_device_pairs2, _ = zones[zone2_name]

                    frequencies1 = [f[0] for f in freq_device_pairs1]
                    devices1 = {f[0]: f[1] for f in freq_device_pairs1}

                    frequencies2 = [f[0] for f in freq_device_pairs2]
                    devices2 = {f[0]: f[1] for f in freq_device_pairs2}

                    debug_log(f"  Calculating cross-zone IMD between {zone1_name} ({len(frequencies1)} freqs) and {zone2_name} ({len(frequencies2)} freqs). Interacting!",
                                file=current_file, version=current_version, function=current_function)

                    for f1 in frequencies1:
                        for f2 in frequencies2:
                            dev1 = devices1[f1]
                            dev2 = devices2[f2]

                            # Ensure f1 is always smaller for consistent calculation and labeling
                            if f1 > f2: # This is for the IMD calculation itself, not the parent freqs
                                # No need to swap dev1, dev2 here, they refer to devices in their original zones
                                pass # Keep f1, f2 as they are from different zones

                            # 3rd Order IMD
                            imd3_1 = (2 * f1) - f2
                            imd3_2 = (2 * f2) - f1

                            # 5th Order IMD
                            imd5_1 = (3 * f1) - (2 * f2)
                            imd5_2 = (3 * f2) - (2 * f1)

                            imd_products = {
                                "2f1-f2": imd3_1,
                                "2f2-f1": imd3_2,
                                "3f1-2f2": imd5_1,
                                "3f2-2f1": imd5_2
                            }

                            for label, freq in imd_products.items():
                                if in_band_low_freq <= freq <= in_band_high_freq:
                                    is_3rd_order = label in ["2f1-f2", "2f2-f1"]
                                    is_5th_order = label in ["3f1-2f2", "3f2-2f1"]

                                    if (include_3rd_order and is_3rd_order) or \
                                       (include_5th_order and is_5th_order):
                                        results.append({
                                            "Zone_1": zone1_name,
                                            "Zone_2": zone2_name,
                                            "Type": "Cross-Zone",
                                            "Order": label,
                                            "Distance": round(dist, 2),
                                            "Frequency_MHz": round(freq, 3),
                                            "Severity": _get_severity(label),
                                            "Device_1": dev1,
                                            "Device_2": dev2,
                                            "Parent_Freq1": round(f1, 3), # ADDED
                                            "Parent_Freq2": round(f2, 3)   # ADDED
                                        })
                                        debug_log(f"    Added cross-zone IMD: {label} @ {freq:.3f} MHz between {zone1_name} and {zone2_name}. Collision detected!",
                                                    file=current_file, version=current_version, function=current_function)
                                else:
                                    debug_log(f"    Skipping cross-zone IMD {label} @ {freq:.3f} MHz (out of band). Not relevant!",
                                                file=current_file, version=current_version, function=current_function)
                else:
                    debug_log(f"  Skipping cross-zone IMD between {zone1_name} and {zone2_name}: Distance {dist:.2f}m > {DISTANCE_LIMIT_METERS}m. Too far apart!",
                                file=current_file, version=current_version, function=current_function)


    # Export final results sorted by frequency
    df = pd.DataFrame(results).sort_values(by="Frequency_MHz")
    
    # Ensure the output directory exists
    output_dir = os.path.dirname(export_csv)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        debug_log(f"Created directory for IMD report: {output_dir}. Folder ready!",
                    file=current_file, version=current_version, function=current_function)

    try:
        df.to_csv(export_csv, index=False)
        console_print_func(f"📁 Intermod report exported to: {export_csv}. Success!")
        debug_log(f"Intermod report exported to: {export_csv}. File saved!",
                    file=current_file, version=current_version, function=current_function)
    except Exception as e:
        console_print_func(f"❌ Error exporting intermod report to CSV: {e}. This is a disaster!")
        debug_log(f"Error exporting intermod report to CSV: {e}. Export failed!",
                    file=current_file, version=current_version, function=current_function)
        # Re-raise the exception to be handled by the caller, or return an empty DataFrame
        raise

    debug_log(f"Exiting {current_function}. Total IMD products: {len(df)}. Calculation complete! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    return df
