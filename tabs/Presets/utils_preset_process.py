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

current_version = "20250802.1701.11" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 1701 * 11 # Example hash, adjust as needed

import pyvisa
import time
import inspect
import os
from datetime import datetime
import csv

# Updated imports for new logging functions
from src.debug_logic import debug_log, log_visa_command
from src.console_logic import console_log

# Removed the following imports as they are not needed in this specific file
# from tabs.Instrument.instrument_logic import query_current_instrument_settings_logic
# from ref.frequency_bands import MHZ_TO_HZ

# Define constants
PRESETS_CSV_FILENAME = "PRESETS.CSV"
VBW_RBW_RATIO = 3 # Moved this to a module-level constant for better practice and to resolve potential syntax issues.

def get_presets_csv_path(config_file_path, console_print_func):
    """
    Function Description:
    Determines the full path to the PRESETS.CSV file.
    It assumes the CSV file is in the same directory as the main application's config file.

    Inputs to this function:
      config_file_path (str): The full path to the application's configuration file.
      console_print_func (function): A function to print messages to the GUI console.

    Process of this function:
      1. Prints debug messages.
      2. Extracts the directory from `config_file_path`.
      3. Joins the directory with `PRESETS_CSV_FILENAME` to form the full path.
      4. Returns the constructed path.

    Outputs of this function:
      str: The full path to the PRESETS.CSV file.

    (2025-07-30) Change: No functional change, just updated header.
    (2025-08-01 1920.1) Change: No functional changes.
    (2025-08-01 2305.1) Change: Refactored debug_print to use debug_log.
    (2025-08-02) Change: Updated debug file name to use `os.path.basename(__file__)`.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Determining CSV path based on config file: {config_file_path}",
                file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                version=current_version,
                function=current_function)
    config_dir = os.path.dirname(config_file_path)
    csv_path = os.path.join(config_dir, PRESETS_CSV_FILENAME)
    debug_log(f"CSV path determined: {csv_path}. Looks good!",
                file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                version=current_version,
                function=current_function)
    return csv_path

def load_user_presets_from_csv(config_file_path, console_print_func):
    """
    Function Description:
    Loads user-defined preset details from the PRESETS.CSV file.
    This function reads the CSV, parses each row into a dictionary,
    and returns a list of these dictionaries. It handles file not found
    by creating a new one with headers, and parsing errors gracefully.

    Inputs to this function:
      config_file_path (str): The full path to the application's configuration file,
                              used to derive the CSV path.
      console_print_func (function): A function to print messages to the GUI console.

    Process of this function:
      1. Prints debug messages.
      2. Gets the full CSV file path using `get_presets_csv_path`.
      3. Initializes an empty list `presets`.
      4. Attempts to open and read the CSV file:
         a. Uses `csv.DictReader` to read rows as dictionaries.
         b. Iterates through rows, converting numeric fields (Center, Span, RBW)
            to floats and handling potential `ValueError` during conversion.
         c. Appends each processed row to the `presets` list.
      5. If `FileNotFoundError` occurs, creates a new CSV file with headers.
      6. Handles other potential `IOError` or general `Exception`.

    Outputs of this function:
      list: A list of dictionaries, each representing a user-defined preset.
            Returns an empty list if no presets are found or an error occurs.

    (2025-07-30) Change: Initial implementation.
    (2025-07-31) Change: Added error handling for CSV parsing and file not found.
    (2025-08-01 1920.1) Change: No functional changes.
    (2025-08-01 2305.1) Change: Refactored debug_print to use debug_log.
    (2025-08-02) Change: Updated debug file name to use `os.path.basename(__file__)`.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Loading user presets from CSV. Let's see what we've got!",
                file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                version=current_version,
                function=current_function)

    csv_path = get_presets_csv_path(config_file_path, console_print_func)
    presets = []
    try:
        with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Convert numeric fields to appropriate types
                    row['Center'] = float(row.get('Center', 0.0))
                    row['Span'] = float(row.get('Span', 0.0))
                    row['RBW'] = float(row.get('RBW', 0.0))
                    # Add other numeric fields here if they exist in your CSV
                    presets.append(row)
                except ValueError as ve:
                    console_print_func(f"❌ Error parsing row in CSV: {row} - {ve}. Skipping this one!")
                    debug_log(f"ValueError parsing row in CSV: {row} - {ve}. This is a problem!",
                                file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                                version=current_version,
                                function=current_function)
        console_print_func(f"✅ Loaded {len(presets)} user presets from {csv_path}.")
        debug_log(f"Successfully loaded {len(presets)} user presets from {csv_path}.",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)
    except FileNotFoundError:
        console_print_func(f"ℹ️ User presets file not found at {csv_path}. Creating a new one.")
        debug_log(f"User presets file not found. Creating new file at {csv_path}.",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)
        # Create the file with headers
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Filename', 'Center', 'Span', 'RBW', 'NickName']) # Add other headers if needed
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

def save_user_preset_to_csv(preset_data, config_file_path, console_print_func):
    """
    Function Description:
    Appends a new user-defined preset to the PRESETS.CSV file.

    Inputs to this function:
      preset_data (dict): A dictionary containing the preset's details (e.g., 'Filename', 'Center', 'Span', 'RBW', 'NickName').
      config_file_path (str): The full path to the application's configuration file,
                              used to derive the CSV path.
      console_print_func (function): A function to print messages to the GUI console.

    Process of this function:
      1. Prints debug messages.
      2. Gets the full CSV file path.
      3. Checks if the file exists; if not, creates it with headers.
      4. Appends the `preset_data` as a new row to the CSV file.
      5. Handles potential `IOError` or general `Exception`.

    Outputs of this function:
      bool: True if the preset is saved successfully, False otherwise.

    (2025-07-30) Change: Initial implementation.
    (2025-07-31) Change: Added error handling for CSV writing.
    (2025-08-01 1920.1) Change: No functional changes.
    (2025-08-01 2305.1) Change: Refactored debug_print to use debug_log.
    (2025-08-02) Change: Updated debug file name to use `os.path.basename(__file__)`.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Saving user preset to CSV: {preset_data.get('NickName', 'Unnamed')}. Storing the goods!",
                file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                version=current_version,
                function=current_function)

    csv_path = get_presets_csv_path(config_file_path, console_print_func)
    try:
        # Check if file exists to decide whether to write headers
        file_exists = os.path.exists(csv_path)
        with open(csv_path, mode='a', newline='', encoding='utf-8') as file:
            fieldnames = ['Filename', 'Center', 'Span', 'RBW', 'NickName'] # Ensure all expected fields are here
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader() # Write header only if file is new

            writer.writerow(preset_data)
        console_print_func(f"✅ User preset '{preset_data.get('NickName', 'Unnamed')}' saved to {csv_path}.")
        debug_log(f"User preset '{preset_data.get('NickName', 'Unnamed')}' saved successfully.",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)
        return True
    except IOError as e:
        console_print_func(f"❌ I/O Error saving user preset to {csv_path}: {e}. This is a disaster!")
        debug_log(f"IOError saving user preset: {e}. Fucking hell!",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)
        return False
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred saving user preset: {e}. What a mess!")
        debug_log(f"Unexpected error saving user preset: {e}. This is a pain in the ass!",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)
        return False
