# tabs/Markers/utils_markers_file_handling.py
#
# This file contains functions for handling file-related operations, specifically
# for the MARKERS.CSV file. It centralizes the logic for loading, saving, and
# processing marker data.
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
# Version 20250814.153000.1

current_version = "20250814.153000.1"
current_version_hash = (20250814 * 153000 * 1)

import os
import inspect
import pandas as pd
import numpy as np

from display.debug_logic import debug_log

def load_and_process_markers(app_instance, console_print_func):
    # [A brief, one-sentence description of the function's purpose.]
    # This is the main orchestrator function that loads the CSV and processes it
    # into the two data structures required by the Showtime tab.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Orchestrating the loading and processing of MARKERS.CSV.",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)

    df, success, message = load_markers_data(app_instance, console_print_func)
    console_print_func(message)

    if not success or df.empty:
        return {}, {} # Return empty dicts on failure

    # 1. Create the markers_data dictionary (keyed by unique name)
    markers_data_dict = {}
    df['NAME'] = df['NAME'].fillna(pd.Series([f"Unnamed_{i}" for i in range(len(df))]))

    for index, row in df.iterrows():
        unique_name = row['NAME']
        try:
            freq_mhz = float(row.get('FREQ', 0))
        except (ValueError, TypeError):
            freq_mhz = 0
        
        markers_data_dict[unique_name] = {
            'frequency_mhz': freq_mhz,
            'zone': row.get('ZONE', 'Unknown'),
            'group': row.get('GROUP', 'Ungrouped'),
            'device': row.get('DEVICE', ''),
            'peak': row.get('Peak', None)
        }

    # 2. Create the zones dictionary using the helper function
    zones_dict = _group_by_zone_and_group(df)

    debug_log(f"✅ Successfully parsed CSV into {len(markers_data_dict)} devices and {len(zones_dict)} zones.",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)
              
    return markers_data_dict, zones_dict


def load_markers_data(app_instance, console_print_func):
    # [A brief, one-sentence description of the function's purpose.]
    # Loads marker data from the internal MARKERS.CSV file.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Loading markers data from CSV. Let's see what we've got!",
              file=f"{os.path.basename(__file__)} & {current_version}",
              version=current_version,
              function=current_function)

    markers_data = pd.DataFrame()
    
    if app_instance and hasattr(app_instance, 'MARKERS_FILE_PATH'):
        path = app_instance.MARKERS_FILE_PATH
        debug_log(f"Attempting to load markers from path: {path}",
                  file=f"{os.path.basename(__file__)} & {current_version}",
                  version=current_version,
                  function=current_function)
        if os.path.exists(path):
            try:
                markers_data = pd.read_csv(path)
                return markers_data, True, f"✅ Loaded {len(markers_data)} markers from MARKERS.CSV."
            except pd.errors.EmptyDataError:
                return pd.DataFrame(), False, "⚠️ MARKERS.CSV is empty. No marker data to display."
            except Exception as e:
                return pd.DataFrame(), False, f"❌ Error loading MARKERS.CSV: {e}"
        else:
            return pd.DataFrame(), False, "ℹ️ MARKERS.CSV not found. Please create one."
    
    return pd.DataFrame(), False, "❌ Application instance or file path not available."


def _group_by_zone_and_group(data):
    # [A brief, one-sentence description of the function's purpose.]
    # Groups marker data by zone and then by group.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Grouping marker data by zone and group.",
              file=f"{os.path.basename(__file__)} & {current_version}",
              version=current_version,
              function=current_function)

    if data.empty:
        return {}

    data['GROUP'] = data['GROUP'].fillna('No Group')
    data['ZONE'] = data['ZONE'].fillna('No Zone')

    zones = {}
    for zone, zone_data in data.groupby('ZONE'):
        groups = {group: group_data['NAME'].tolist() for group, group_data in zone_data.groupby('GROUP')}
        
        min_freq = zone_data['FREQ'].min()
        max_freq = zone_data['FREQ'].max()
        if pd.notna(min_freq) and pd.notna(max_freq) and max_freq > min_freq:
            span_hz = (max_freq - min_freq) * 1_000_000 
        else:
            span_hz = 1_000_000 # Default span
        
        groups['span_hz'] = span_hz
        zones[zone] = groups
    
    debug_log(f"✅ Successfully grouped data into {len(zones)} zones.",
              file=f"{os.path.basename(__file__)} & {current_version}",
              version=current_version,
              function=current_function)

    return zones