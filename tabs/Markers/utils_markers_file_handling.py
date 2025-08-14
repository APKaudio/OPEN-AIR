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
# Version 20250814.005950.2

current_version = "20250814.005950.2"
current_version_hash = (20250814 * 5950 * 2)

import os
import inspect
import pandas as pd
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log


def load_markers_data(app_instance, console_print_func):
    # Function Description:
    # Loads marker data from the internal MARKERS.CSV file. This function is
    # now completely decoupled from the GUI. It returns the loaded DataFrame and
    # a status message.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Loading markers data from CSV. It's time to get some data!",
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
                # FIXED: Do NOT fill NaN with empty strings. Let pandas handle missing data correctly.
                # markers_data.fillna('', inplace=True) 
                debug_log(f"✅ Successfully read {len(markers_data)} markers from file.",
                          file=f"{os.path.basename(__file__)} & {current_version}",
                          version=current_version,
                          function=current_function)
                return markers_data, True, f"✅ Loaded {len(markers_data)} markers from MARKERS.CSV."
            except pd.errors.EmptyDataError:
                debug_log(f"⚠️ The CSV file is empty.",
                          file=f"{os.path.basename(__file__)} & {current_version}",
                          version=current_version,
                          function=current_function)
                return pd.DataFrame(), False, "⚠️ MARKERS.CSV is empty. No marker data to display."
            except Exception as e:
                debug_log(f"❌ An unexpected error occurred while loading the CSV: {e}",
                          file=f"{os.path.basename(__file__)} & {current_version}",
                          version=current_version,
                          function=current_function)
                return pd.DataFrame(), False, f"❌ Error loading MARKERS.CSV: {e}"
        else:
            debug_log(f"ℹ️ File not found at path: {path}",
                      file=f"{os.path.basename(__file__)} & {current_version}",
                      version=current_version,
                      function=current_function)
            return pd.DataFrame(), False, "ℹ️ MARKERS.CSV not found. Please create one."
    
    debug_log(f"❌ Application instance or file path not available.",
              file=f"{os.path.basename(__file__)} & {current_version}",
              version=current_version,
              function=current_function)
    return pd.DataFrame(), False, "❌ Application instance or file path not available."


def _group_by_zone_and_group(data):
    # Function Description:
    # Groups marker data by zone and then by group. This is a pure data processing
    # function with no ties to the GUI.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Grouping marker data by zone and group. The data is a mess, let's clean it up!",
              file=f"{os.path.basename(__file__)} & {current_version}",
              version=current_version,
              function=current_function)

    if data.empty:
        debug_log(f"No data to group. Returning an empty dictionary.",
                  file=f"{os.path.basename(__file__)} & {current_version}",
                  version=current_version,
                  function=current_function)
        return {}

    # Fill any empty 'GROUP' cells with a placeholder
    data['GROUP'] = data['GROUP'].fillna('No Group')

    zones = {}
    for zone, zone_data in data.groupby('ZONE'):
        groups = {group: group_data.to_dict('records') for group, group_data in zone_data.groupby('GROUP')}
        zones[zone] = groups
    
    debug_log(f"✅ Successfully grouped data into {len(zones)} zones.",
              file=f"{os.path.basename(__file__)} & {current_version}",
              version=current_version,
              function=current_function)

    return zones