# tabs.Markers/showtime/utils_markers_files_zone_groups_devices.py
#
# This new utility file centralizes all logic for parsing the MARKERS.CSV file,
# structuring the data into zones, groups, and devices, and providing helper
# functions for the UI, like the progress bar.
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
# Version 20250821.210000.1
# FIXED: Replaced inplace operations on DataFrame slices to remove FutureWarning messages.
# NEW: Added debug logging for reads and writes of file data.

import os
import inspect
import pandas as pd
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log
from src.program_default_values import DATA_FOLDER_PATH

# Define the path to the markers file
MARKERS_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'MARKERS.CSV')

def load_and_structure_markers_data():
    # The main function to load, parse, and structure data from MARKERS.CSV.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Entering {current_function}. Time to wrangle that CSV data! 📂", file=f"{os.path.basename(__file__)}", version="20250821.210000.1", function=current_function)

    if not os.path.exists(MARKERS_FILE_PATH):
        console_log(f"❌ MARKERS.CSV not found at path: {MARKERS_FILE_PATH}", "ERROR")
        debug_log(message=f"Marker CSV not found. What a disaster!", file=f"{os.path.basename(__file__)}", version="20250821.210000.1", function=current_function)
        return None
    try:
        # 📂 Read File: Reading the marker CSV data.
        debug_log(message=f"📂 Read File: Reading marker data from {MARKERS_FILE_PATH}", file=f"{os.path.basename(__file__)}", version="20250821.210000.1", function=current_function)
        df = pd.read_csv(MARKERS_FILE_PATH)
        
        # --- Data Cleaning and Structuring ---
        df.columns = [col.upper().strip() for col in df.columns]
        
        # Define potential column names and map them to our desired names
        column_mapping = {
            'ZONE': 'ZONE',
            'GROUP': 'GROUP',
            'NAME': 'NAME',
            'DEVICE': 'DEVICE',
            'FREQ CENTER (MHZ)': 'CENTER',
            'FREQ': 'CENTER', # Alternate name for center frequency
            'PEAK (DBM)': 'PEAK',
            'PEAK': 'PEAK' # Alternate name for peak
        }
        
        # Rename columns based on the mapping
        df.rename(columns=column_mapping, inplace=True)

        # Ensure essential columns exist, fill missing with defaults
        for col in ['ZONE', 'GROUP', 'NAME', 'DEVICE', 'CENTER', 'PEAK']:
            if col not in df.columns:
                df[col] = 'N/A' if col != 'PEAK' else -120

        # FIXED: Corrected the fillna operations to avoid FutureWarning in pandas 3.0
        # Replaces df['GROUP'].fillna('Ungrouped', inplace=True)
        df.loc[:, 'GROUP'] = df['GROUP'].fillna('Ungrouped')
        # Replaces df['ZONE'].fillna('Unzoned', inplace=True)
        df.loc[:, 'ZONE'] = df['ZONE'].fillna('Unzoned')

        # --- Hierarchical Structuring ---
        structured_data = {}
        for zone_name, zone_df in df.groupby('ZONE'):
            zone_dict = {}
            for group_name, group_df in zone_df.groupby('GROUP'):
                device_list = []
                for index, row in group_df.iterrows():
                    device_list.append({
                        'NAME': row['NAME'],
                        'DEVICE': row['DEVICE'],
                        'CENTER': row['CENTER'],
                        'PEAK': row['PEAK']
                    })
                zone_dict[group_name] = device_list
            structured_data[zone_name] = zone_dict
        
        # 📊 Processed Data: Log the result of the data transformation.
        console_log(f"✅ Successfully loaded and structured {len(df)} devices into {len(structured_data)} zones.", "SUCCESS")
        debug_log(message=f"📊 Processed Data: Successfully loaded and structured {len(df)} devices into {len(structured_data)} zones. We got the data! 🎣", file=f"{os.path.basename(__file__)}", version="20250821.210000.1", function=current_function)
        return structured_data

    except Exception as e:
        console_log(f"❌ Failed to parse MARKERS.CSV. Error: {e}", "ERROR")
        debug_log(message=f"Full traceback for CSV parsing error: {e}. This bugger is being problematic!", file=f"{os.path.basename(__file__)}", version="20250821.210000.1", function=current_function)
        return None