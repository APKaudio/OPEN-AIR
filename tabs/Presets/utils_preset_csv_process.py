# tabs/Presets/utils_preset_process.py
#
# This file provides utility functions for loading, saving, and managing
# user-defined presets stored in a CSV file. It handles the file path resolution
# and the actual reading/writing operations.
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
# Version 20250814.161800.1 (FIXED: The loading and saving functions were updated to correctly handle the new 'Start' and 'Stop' columns and gracefully manage potential header mismatches by using pandas for robust file operations.)

current_version = "20250814.161800.1"
current_version_hash = 20250814 * 161800 * 1

import os
import csv
import inspect
import pandas as pd # For robust CSV reading/writing
import numpy as np # For handling NaN values

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

current_version = "20250814.161800.1"
current_version_hash = 20250814 * 161800 * 1

def get_presets_csv_path(config_file_path, console_print_func=None):
    """
    Determines the full path to the PRESETS.CSV file.
    It assumes PRESETS.CSV is in the same directory as the config file,
    or in a 'DATA' subdirectory if the config file is one level up.

    Inputs:
        config_file_path (str): The full path to the application's config.ini file.
        console_print_func (function, optional): A function to use for printing messages
                                                 to the console. If None, uses standard print.
    Returns:
        str: The full path to the PRESETS.CSV file.
    """
    _print = console_print_func if console_print_func else print
    current_function = inspect.currentframe().f_code.co_name
    
    # Get the directory containing the config file
    config_dir = os.path.dirname(config_file_path)
    
    # Check if config_dir itself ends with 'DATA'
    if os.path.basename(config_dir).upper() == 'DATA':
        # If config_file_path is already within the DATA folder, use that folder directly
        presets_csv_path = os.path.join(config_dir, "PRESETS.CSV")
    else:
        # Otherwise, assume DATA is a sibling directory to config_dir
        # This might need adjustment based on your exact project structure.
        # For now, let's assume config_file_path is like ".../OPEN-AIR/config.ini"
        # and DATA is ".../OPEN-AIR/DATA/"
        app_root_dir = os.path.dirname(config_dir)
        data_folder = os.path.join(app_root_dir, "DATA")
        presets_csv_path = os.path.join(data_folder, "PRESETS.CSV")

    debug_log(f"Determined presets CSV path: {presets_csv_path}.",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    return presets_csv_path

def load_user_presets_from_csv(config_file_path, console_print_func=None):
    """
    Loads user-defined presets from the PRESETS.CSV file.
    If the file does not exist, it creates an empty one with headers.

    Inputs:
        config_file_path (str): The full path to the application's config.ini file.
        console_print_func (function, optional): A function to use for printing messages
                                                 to the console. If None, uses standard print.
    Returns:
        list: A list of dictionaries, where each dictionary represents a preset.
              Returns an empty list if the file is empty or cannot be read.
    """
    _print = console_print_func if console_print_func else print
    current_function = inspect.currentframe().f_code.co_name
    presets_csv_path = get_presets_csv_path(config_file_path, _print)
    
    # Define the expected headers for the PRESETS.CSV file
    # This list must match the columns expected by PresetEditorTab
    expected_headers = [
        'Filename', 'NickName', 'Start', 'Stop', 'Center', 'Span', 'RBW', 'VBW',
        'RefLevel', 'Attenuation', 'MaxHold', 'HighSens', 'PreAmp',
        'Trace1Mode', 'Trace2Mode', 'Trace3Mode', 'Trace4Mode',
        'Marker1Max', 'Marker2Max', 'Marker3Max', 'Marker4Max',
        'Marker5Max', 'Marker6Max'
    ]

    if not os.path.exists(presets_csv_path):
        _print(f"ℹ️ PRESETS.CSV not found at '{presets_csv_path}'. Creating a new empty file with headers.")
        debug_log(f"PRESETS.CSV not found. Creating new file.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        try:
            # Ensure the DATA directory exists
            os.makedirs(os.path.dirname(presets_csv_path), exist_ok=True)
            with open(presets_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=expected_headers)
                writer.writeheader()
            _print("✅ New PRESETS.CSV created with headers.")
            debug_log("New PRESETS.CSV created with headers.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return [] # Return empty list as the file is new and empty
        except Exception as e:
            _print(f"❌ Error creating PRESETS.CSV: {e}. Cannot load presets.")
            debug_log(f"Error creating PRESETS.CSV: {e}.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return []
    
    # Use a try/except block to handle file reading errors gracefully.
    try:
        _print(f"💬 Loading user presets from existing file: {os.path.basename(presets_csv_path)}. Let's get this data!")
        debug_log(f"Loading user presets from existing file: {presets_csv_path}.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        # Use pandas for more robust CSV reading, handling potential missing columns
        df = pd.read_csv(presets_csv_path, dtype=str, keep_default_na=False) # Read all as string, keep empty strings as empty
        
        # Ensure all expected headers are present, add missing ones with empty string values
        for header in expected_headers:
            if header not in df.columns:
                df[header] = ''

        # Reorder columns to match expected_headers
        df = df[expected_headers]

        presets = df.to_dict(orient='records')

        # Convert NaN values to empty strings after reading with pandas
        for preset in presets:
            for key, value in preset.items():
                if pd.isna(value):
                    preset[key] = ''
                # Ensure all values are strings for consistency
                elif not isinstance(value, str):
                    preset[key] = str(value)

        _print(f"✅ Loaded {len(presets)} user presets from {os.path.basename(presets_csv_path)}.")
        debug_log(f"Loaded {len(presets)} user presets.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return presets
    except pd.errors.EmptyDataError:
        _print(f"ℹ️ PRESETS.CSV at '{presets_csv_path}' is empty. Returning no presets.")
        debug_log(f"PRESETS.CSV is empty.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        # Re-create with headers if it was truly empty (not just header-only)
        try:
            with open(presets_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=expected_headers)
                writer.writeheader()
            _print("✅ Empty PRESETS.CSV re-initialized with headers.")
            debug_log("Empty PRESETS.CSV re-initialized with headers.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        except Exception as e:
            _print(f"❌ Error re-initializing empty PRESETS.CSV: {e}.")
            debug_log(f"Error re-initializing empty PRESETS.CSV: {e}.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        return []
    except Exception as e:
        _print(f"❌ Error loading presets from {os.path.basename(presets_csv_path)}: {e}. Returning no presets.")
        debug_log(f"Error loading presets: {e}. What the hell?!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return []

def overwrite_user_presets_csv(config_file_path, presets_data, console_print_func=None, fieldnames=None):
    """
    Overwrites the PRESETS.CSV file with the provided presets data.
    Ensures all dictionary keys match the fieldnames for csv.DictWriter.

    Inputs:
        config_file_path (str): The full path to the application's config.ini file.
        presets_data (list): A list of dictionaries, where each dictionary represents a preset.
        console_print_func (function, optional): A function to use for printing messages
                                                 to the console. If None, uses standard print.
        fieldnames (list, optional): A list of strings representing the CSV header order.
                                     If None, it will be derived from the keys of the first preset,
                                     or a default set if presets_data is empty.
    Returns:
        bool: True if save was successful, False otherwise.
    """
    _print = console_print_func if console_print_func else print
    current_function = inspect.currentframe().f_code.co_name
    presets_csv_path = get_presets_csv_path(config_file_path, _print)

    try:
        # Determine fieldnames if not provided
        if fieldnames is None:
            if presets_data:
                # Use keys from the first preset as fieldnames
                fieldnames = list(presets_data[0].keys())
                debug_log(f"Derived fieldnames from first preset: {fieldnames}",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            else:
                # If presets_data is empty and no fieldnames provided, use a default set
                fieldnames = [
                    'Filename', 'NickName', 'Start', 'Stop', 'Center', 'Span', 'RBW', 'VBW',
                    'RefLevel', 'Attenuation', 'MaxHold', 'HighSens', 'PreAmp',
                    'Trace1Mode', 'Trace2Mode', 'Trace3Mode', 'Trace4Mode',
                    'Marker1Max', 'Marker2Max', 'Marker3Max', 'Marker4Max',
                    'Marker5Max', 'Marker6Max'
                ]
                debug_log(f"Using default fieldnames as presets_data is empty: {fieldnames}",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)

        # Ensure all dictionaries in presets_data have all keys defined in fieldnames
        # and convert values to strings, handling NaN
        cleaned_presets_data = []
        for preset in presets_data:
            cleaned_preset = {}
            for field in fieldnames:
                value = preset.get(field, '') # Get value, default to empty string if key is missing
                if pd.isna(value):
                    cleaned_preset[field] = '' # Replace NaN with empty string
                elif isinstance(value, (float, np.float64)) and value.is_integer():
                    cleaned_preset[field] = str(int(value))
                else:
                    cleaned_preset[field] = str(value) # Ensure all values are strings
            cleaned_presets_data.append(cleaned_preset)

        with open(presets_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cleaned_presets_data)
        
        debug_log(f"Successfully overwrote PRESETS.CSV at: {presets_csv_path} with {len(cleaned_presets_data)} entries.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return True
    except Exception as e:
        _print(f"❌ An unexpected error occurred overwriting presets: {e}. What a mess!")
        debug_log(f"An unexpected error occurred overwriting presets to {presets_csv_path}: {e}.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False
