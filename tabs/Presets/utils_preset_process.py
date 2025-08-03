# utils/utils_preset_process.py
#
# This module provides utility functions for processing user-defined presets,
# including determining the CSV file path, loading presets from the CSV,
# and saving presets to the CSV. It handles file operations and data parsing
# for local preset storage.
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
# Version 20250802.1701.11 (Refactored from utils_preset.py to handle preset processing logic.)
# Version 20250802.1800.7 (Added 'Markers' column, and overwrite_user_presets_csv function.)

current_version = "20250802.1800.7" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 1800 * 7 # Example hash, adjust as needed

import pyvisa
import time
import inspect
import os
from datetime import datetime
import csv

# Updated imports for new logging functions
from src.debug_logic import debug_log, log_visa_command
from src.console_logic import console_log

# Removed the following imports as they are now in utils_preset_query_and_load.py
# from tabs.Instrument.utils_instrument_read_and_write import query_safe, write_safe
# from tabs.Instrument.utils_instrument_initialize import initialize_instrument_settings
# from tabs.Instrument.utils_instrument_query_settings import query_current_instrument_settings
# from tabs.Instrument.utils_instrument_connection import connect_instrument, disconnect_instrument, list_visa_resources

def get_presets_csv_path(config_file_path):
    """
    Determines the full path to the PRESETS.CSV file.
    It assumes PRESETS.CSV is in the same directory as config.ini (DATA folder).

    Inputs:
        config_file_path (str): The full path to the config.ini file.

    Outputs:
        str: The full path to the PRESETS.CSV file.
    """
    current_function = inspect.currentframe().f_code.co_name
    config_dir = os.path.dirname(config_file_path)
    presets_csv_path = os.path.join(config_dir, "PRESETS.CSV")
    debug_log(f"Determined presets CSV path: {presets_csv_path}.",
                file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                version=current_version,
                function=current_function)
    return presets_csv_path

def load_user_presets_from_csv(config_file_path, console_print_func):
    """
    Loads user-defined presets from the PRESETS.CSV file.
    If the file does not exist, it creates it with a header.

    Inputs:
        config_file_path (str): The full path to the config.ini file (used to derive CSV path).
        console_print_func (function): Function to print messages to the GUI console.

    Outputs:
        list: A list of dictionaries, where each dictionary represents a preset row.
    """
    current_function = inspect.currentframe().f_code.co_name
    presets = []
    csv_path = get_presets_csv_path(config_file_path)

    try:
        if os.path.exists(csv_path):
            debug_log(f"Loading user presets from existing file: {csv_path}. Let's get this data!",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
            with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Ensure 'Markers' column exists, default to empty string if not
                    if 'Markers' not in row:
                        row['Markers'] = ''
                    presets.append(row)
            console_print_func(f"✅ Loaded {len(presets)} user presets from {os.path.basename(csv_path)}.")
            debug_log(f"User presets loaded successfully: {len(presets)} entries.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
        else:
            console_print_func(f"ℹ️ User presets file not found at {csv_path}. Creating a new one.")
            debug_log(f"User presets file not found. Creating new file at {csv_path}.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
            # Create the file with headers
            with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
                # Updated fieldnames for new CSV format
                fieldnames = [
                    'Filename', 'NickName', 'Center', 'Span', 'RBW', 'VBW',
                    'RefLevel', 'Attenuation', 'MaxHold', 'HighSens', 'PreAmp',
                    'Trace1Mode', 'Trace2Mode', 'Trace3Mode', 'Trace4Mode',
                    'Marker1Max', 'Marker2Max', 'Marker3Max', 'Marker4Max',
                    'Marker5Max', 'Marker6Max'
                ]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
            console_print_func("✅ New user presets file created with headers.")
            debug_log("New user presets file created.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
    except IOError as e:
        console_print_func(f"❌ I/O Error loading user presets from {csv_path}: {e}. This is a disaster!")
        debug_log(f"IOError loading user presets: {e}. Fucking hell!",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred loading user presets: {e}. What a mess!")
        debug_log(f"Unexpected error loading user presets: {e}. This is a pain in the ass!",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)
    return presets

def overwrite_user_presets_csv(config_file_path, all_presets_data, console_print_func):
    """
    Overwrites the PRESETS.CSV file with the provided list of preset dictionaries.
    This function is intended for saving the current state of user presets.

    Inputs:
        config_file_path (str): The full path to the config.ini file (used to derive CSV path).
        all_presets_data (list): A list of dictionaries, each representing a preset row
                                 to be written to the CSV.
        console_print_func (function): Function to print messages to the GUI console.

    Outputs:
        bool: True if presets were overwritten successfully, False otherwise.
    """
    current_function = inspect.currentframe().f_code.co_name
    csv_path = get_presets_csv_path(config_file_path)

    debug_log(f"Attempting to overwrite user presets CSV at: {csv_path}. Let's do this!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    try:
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            # Updated fieldnames for new CSV format
            fieldnames = [
                'Filename', 'NickName', 'Center', 'Span', 'RBW', 'VBW',
                'RefLevel', 'Attenuation', 'MaxHold', 'HighSens', 'PreAmp',
                'Trace1Mode', 'Trace2Mode', 'Trace3Mode', 'Trace4Mode',
                'Marker1Max', 'Marker2Max', 'Marker3Max', 'Marker4Max',
                'Marker5Max', 'Marker6Max'
            ]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_presets_data)
        console_print_func(f"✅ Overwrote PRESETS.CSV with {len(all_presets_data)} entries. All changes saved!")
        debug_log(f"User presets CSV overwritten successfully.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return True
    except IOError as e:
        console_print_func(f"❌ I/O Error overwriting presets to {csv_path}: {e}. This is a disaster!")
        debug_log(f"IOError overwriting user presets: {e}. Fucking hell!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred overwriting presets: {e}. What a mess!")
        debug_log(f"Unexpected error overwriting user presets: {e}. This is a pain in the ass!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False