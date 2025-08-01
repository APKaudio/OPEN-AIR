# process_math/calculate_intermod.py
import pandas as pd
import math
from typing import Dict, List, Tuple
import inspect # Used for enhanced debug printing context
from utils.utils_instrument_control import debug_print # Custom debug print for logging

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
    Calculates the Euclidean distance between two 2D points.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering euclidean_distance. pos1 type: {type(pos1)}, pos1: {pos1}", file=current_file, function=current_function)
    debug_print(f"pos2 type: {type(pos2)}, pos2: {pos2}", file=current_file, function=current_function)

    # Ensure pos1 and pos2 are tuples before accessing elements
    if not isinstance(pos1, tuple) or not isinstance(pos2, tuple):
        debug_print(f"Error: pos1 or pos2 is not a tuple in euclidean_distance. pos1 type: {type(pos1)}, pos2 type: {type(pos2)}", file=current_file, function=current_function)
        raise TypeError("Positions must be tuples (x, y).")

    # Ensure elements within tuples are numeric
    if not all(isinstance(coord, (int, float)) for coord in pos1) or \
       not all(isinstance(coord, (int, float)) for coord in pos2):
        debug_print(f"Error: Coordinates within position tuples are not numeric. pos1: {pos1}, pos2: {pos2}", file=current_file, function=current_function)
        raise TypeError("Coordinates within position tuples must be numeric.")

    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def _get_severity(order: str) -> str:
    """
    Maps intermodulation product orders to a severity rating.
    """
    if order in ["2f1-f2", "2f2-f1"]:
        return "High"
    elif order in ["3f1-2f2", "3f2-2f1"]:
        return "Medium"
    else:
        return "Low"

def calculate_intermods(freq_device_pairs: List[Tuple[float, str]]) -> List[Dict]:
    """
    Calculates 3rd and 5th order intermodulation products for a given list of (frequency, device) pairs.
    Returns a list of dictionaries, each representing an IMD product, including parent frequencies and devices.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering calculate_intermods. Freq-Device Pairs type: {type(freq_device_pairs)}, Pairs: {freq_device_pairs}", file=current_file, function=current_function)

    # Ensure freq_device_pairs is always a list of tuples
    if not isinstance(freq_device_pairs, list):
        debug_print(f"Invalid freq_device_pairs type {type(freq_device_pairs)}; expected list. Returning empty.", file=current_file, function=current_function)
        return []
    for item in freq_device_pairs:
        if not (isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], (int, float)) and isinstance(item[1], str)):
            debug_print(f"Invalid item in freq_device_pairs: {item}. Expected (float, str). Returning empty.", file=current_file, function=current_function)
            return []

    imd_products = []
    # Sort by frequency to ensure consistent results and avoid redundant calculations
    freq_device_pairs = sorted(freq_device_pairs, key=lambda x: x[0])
    debug_print(f"Freq-Device Pairs after sorting: {freq_device_pairs}", file=current_file, function=current_function)

    # 3rd Order IMD (2f1 - f2, 2f2 - f1)
    for i in range(len(freq_device_pairs)):
        for j in range(len(freq_device_pairs)):
            if i == j: continue

            f1, dev1 = freq_device_pairs[i]
            f2, dev2 = freq_device_pairs[j]

            debug_print(f"  Calculating 3rd order for f1={f1} ({dev1}), f2={f2} ({dev2})", file=current_file, function=current_function)

            # 2f1 - f2
            im3_1 = round(2 * f1 - f2, 3)
            if im3_1 > 0:
                imd_products.append({
                    "Order": "2f1-f2",
                    "Frequency_MHz": im3_1,
                    "Severity": _get_severity("2f1-f2"),
                    "Parent_Freq1": f1,
                    "Parent_Freq2": f2,
                    "Device_1": dev1,
                    "Device_2": dev2
                })
                debug_print(f"    Appended 3rd order IMD: 2f1-f2 at {im3_1} MHz from {dev1} and {dev2}", file=current_file, function=current_function)

            # 2f2 - f1
            im3_2 = round(2 * f2 - f1, 3)
            if im3_2 > 0:
                imd_products.append({
                    "Order": "2f2-f1",
                    "Frequency_MHz": im3_2,
                    "Severity": _get_severity("2f2-f1"),
                    "Parent_Freq1": f2,
                    "Parent_Freq2": f1,
                    "Device_1": dev2,
                    "Device_2": dev1
                })
                debug_print(f"    Appended 3rd order IMD: 2f2-f1 at {im3_2} MHz from {dev2} and {dev1}", file=current_file, function=current_function)

    # 5th Order IMD (3f1 - 2f2, 3f2 - 2f1)
    for i in range(len(freq_device_pairs)):
        for j in range(len(freq_device_pairs)):
            if i == j: continue

            f1, dev1 = freq_device_pairs[i]
            f2, dev2 = freq_device_pairs[j]

            debug_print(f"  Calculating 5th order for f1={f1} ({dev1}), f2={f2} ({dev2})", file=current_file, function=current_function)

            # 3f1 - 2f2
            im5_1 = round(3 * f1 - 2 * f2, 3)
            if im5_1 > 0:
                imd_products.append({
                    "Order": "3f1-2f2",
                    "Frequency_MHz": im5_1,
                    "Severity": _get_severity("3f1-2f2"),
                    "Parent_Freq1": f1,
                    "Parent_Freq2": f2,
                    "Device_1": dev1,
                    "Device_2": dev2
                })
                debug_print(f"    Appended 5th order IMD: 3f1-2f2 at {im5_1} MHz from {dev1} and {dev2}", file=current_file, function=current_function)

            # 3f2 - 2f1
            im5_2 = round(3 * f2 - 2 * f1, 3)
            if im5_2 > 0:
                imd_products.append({
                    "Order": "3f2-2f1",
                    "Frequency_MHz": im5_2,
                    "Severity": _get_severity("3f2-2f1"),
                    "Parent_Freq1": f2,
                    "Parent_Freq2": f1,
                    "Device_1": dev2,
                    "Device_2": dev1
                })
                debug_print(f"    Appended 5th order IMD: 3f2-2f1 at {im5_2} MHz from {dev2} and {dev1}", file=current_file, function=current_function)

    debug_print(f"Exiting calculate_intermods. Found {len(imd_products)} products.", file=current_file, function=current_function)
    return imd_products


def multi_zone_intermods(
    zones: ZoneData, # ZoneData now includes device info
    include_cross_zone: bool = True,
    export_csv: str = "intermod_results.csv",
    filter_in_band: bool = False,
    in_band_min_freq: float = 0.0,
    in_band_max_freq: float = 1000.0,
    include_3rd_order: bool = True,
    include_5th_order: bool = True
) -> pd.DataFrame:
    """
    Calculates intermodulation products for multiple spatial zones.
    Now includes parent device information for each IMD product.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering multi_zone_intermods. Filter in band: {filter_in_band}, Range: {in_band_min_freq}-{in_band_max_freq} MHz", file=current_file, function=current_function)
    debug_print(f"Zones data received: {zones}", file=current_file, function=current_function)


    print("\n=== Intermodulation Report (Per Zone) ===\n")
    results = []

    # Process intra-zone IMDs: IMDs generated within the same zone
    for zone_name, (freq_device_pairs, pos) in zones.items(): # Unpack freq_device_pairs
        debug_print(f"Processing intra-zone IMD for zone '{zone_name}'. Freq-Device Pairs type: {type(freq_device_pairs)}, Pairs: {freq_device_pairs}. Position type: {type(pos)}, Position: {pos}", file=current_file, function=current_function)
        imd_products = calculate_intermods(freq_device_pairs) # Pass freq_device_pairs
        for imd in imd_products:
            debug_print(f"  Checking IMD product in multi_zone_intermods: {imd}", file=current_file, function=current_function)
            # Apply order filter
            is_3rd_order = imd["Order"] in ["2f1-f2", "2f2-f1"]
            is_5th_order = imd["Order"] in ["3f1-2f2", "3f2-2f1"]

            if (include_3rd_order and is_3rd_order) or \
               (include_5th_order and is_5th_order):
                # Apply in-band filter
                if not filter_in_band or \
                   (in_band_min_freq <= imd["Frequency_MHz"] <= in_band_max_freq):
                    results.append({
                        "Zone_1": zone_name,
                        "Zone_2": zone_name,
                        "Type": "Intra-Zone",
                        "Order": imd["Order"],
                        "Distance": 0.0,
                        "Frequency_MHz": imd["Frequency_MHz"],
                        "Severity": imd["Severity"],
                        "Device_1": imd["Device_1"],
                        "Device_2": imd["Device_2"],
                        "Parent_Freq1": imd["Parent_Freq1"], # ADDED
                        "Parent_Freq2": imd["Parent_Freq2"]  # ADDED
                    })

    # Process cross-zone IMDs: IMDs generated from frequencies in different zones
    if include_cross_zone:
        print("=== Cross-Zone Intermod Products (Distance-Aware) ===\n")
        zone_keys = list(zones.keys())

        for i in range(len(zone_keys)):
            for j in range(i + 1, len(zone_keys)):
                zone1_name = zone_keys[i]
                zone2_name = zone_keys[j]

                # Ensure we are unpacking correctly and logging types
                freq_device_pairs1, pos1 = zones[zone1_name] # Unpack freq_device_pairs
                freq_device_pairs2, pos2 = zones[zone2_name] # Unpack freq_device_pairs

                debug_print(f"Processing cross-zone IMD between '{zone1_name}' (Freq-Device Pairs type: {type(freq_device_pairs1)}, Pos type: {type(pos1)}) and '{zone2_name}' (Freq-Device Pairs type: {type(freq_device_pairs2)}, Pos type: {type(pos2)})", file=current_file, function=current_function)
                debug_print(f"Zone1 Pairs: {freq_device_pairs1}, Pos: {pos1}", file=current_file, function=current_function)
                debug_print(f"Zone2 Pairs: {freq_device_pairs2}, Pos: {pos2}", file=current_file, function=current_function)

                dist = euclidean_distance(pos1, pos2)
                debug_print(f"  Distance between {zone1_name} and {zone2_name}: {dist:.2f}m", file=current_file, function=current_function)

                if dist > DISTANCE_LIMIT_METERS:
                    debug_print(f"  Skipping cross-zone for {zone1_name}-{zone2_name} due to distance ({dist:.2f}m > {DISTANCE_LIMIT_METERS}m)", file=current_file, function=current_function)
                    continue

                for f1_pair in freq_device_pairs1: # Iterate over pairs
                    f1, dev1 = f1_pair # Unpack frequency and device
                    for f2_pair in freq_device_pairs2: # Iterate over pairs
                        f2, dev2 = f2_pair # Unpack frequency and device

                        debug_print(f"    Calculating cross-IMD for f1={f1} ({dev1}), f2={f2} ({dev2})", file=current_file, function=current_function)
                        cross_imds = {
                            "2f1-f2": round(2*f1 - f2, 3),
                            "2f2-f1": round(2*f2 - f1, 3),
                            "3f1-2f2": round(3*f1 - 2*f2, 3),
                            "3f2-2f1": round(3*f2 - 2*f1, 3),
                        }
                        for label, freq in cross_imds.items():
                            debug_print(f"      Checking cross_imds product: label={label}, freq type: {type(freq)}, freq: {freq}", file=current_file, function=current_function)
                            if freq > 0:
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
                                        "Frequency_MHz": freq,
                                        "Severity": _get_severity(label),
                                        "Device_1": dev1,
                                        "Device_2": dev2,
                                        "Parent_Freq1": f1, # ADDED
                                        "Parent_Freq2": f2   # ADDED
                                    })

    # Export final results sorted by frequency
    df = pd.DataFrame(results).sort_values(by="Frequency_MHz")
    df.to_csv(export_csv, index=False)
    print(f"📁 Intermod report exported to: {export_csv}")
    debug_print(f"Exiting multi_zone_intermods. Total IMD products: {len(df)}", file=current_file, function=current_function)

    return df
