# utils/utils_preset.py
#
# This module provides utility functions for interacting with instrument presets,
# including querying available presets from the device and loading selected presets.
# It abstracts the low-level SCPI commands for preset management.
# It also now handles saving and loading user-defined presets to/from a CSV file.
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
# Version 20250801.2305.1 (Refactored debug_print to use debug_log and console_log.)

current_version = "20250801.2305.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250801 * 2305 * 1 # Example hash, adjust as needed

import pyvisa
import time
import inspect
import os
from datetime import datetime
import csv

# Updated imports for new logging functions
from src.debug_logic import debug_log, log_visa_command
from src.console_logic import console_log

# Import necessary functions from instrument_logic and frequency_bands - CORRECTED PATHS
from src.instrument_logic import query_basic_instrument_settings_logic, query_current_instrument_settings_logic
from ref.frequency_bands import MHZ_TO_HZ

# Define the CSV filename for user-saved presets
PRESETS_CSV_FILENAME = "PRESETS.CSV"

# Helper functions for instrument communication, using the new logging
def write_safe(inst, command, console_print_func):
    """
    Function Description:
    Safely writes a SCPI command to the instrument.
    Logs the command and handles potential errors.

    Inputs to this function:
    - inst (pyvisa.resources.Resource): The PyVISA instrument object.
    - command (str): The SCPI command string to write.
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Checks if the instrument is connected.
    2. Attempts to write the command.
    3. Logs success or failure to the console and debug log.

    Outputs of this function:
    - bool: True if the command was written successfully, False otherwise.

    (2025-08-01) Change: Refactored to use new logging.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to write command: {command}",
                file=__file__,
                version=current_version,
                function=current_function)
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot write command.")
        debug_log("Instrument not connected. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False
    try:
        inst.write(command)
        log_visa_command(command, "SENT") # Log the VISA command
        return True
    except Exception as e:
        console_print_func(f"❌ Error writing command '{command}': {e}")
        debug_log(f"Error writing command '{command}': {e}. This thing is a pain in the ass!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False

def query_safe(inst, command, console_print_func):
    """
    Function Description:
    Safely queries the instrument with a SCPI command and returns the response.
    Logs the command and response, and handles potential errors.

    Inputs to this function:
    - inst (pyvisa.resources.Resource): The PyVISA instrument object.
    - command (str): The SCPI query command string.
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Checks if the instrument is connected.
    2. Attempts to query the instrument.
    3. Logs the command, response, and handles errors.

    Outputs of this function:
    - str or None: The instrument's response if successful, None otherwise.

    (2025-08-01) Change: Refactored to use new logging.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to query command: {command}",
                file=__file__,
                version=current_version,
                function=current_function)
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot query command.")
        debug_log("Instrument not connected. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return None
    try:
        response = inst.query(command).strip()
        log_visa_command(command, "SENT") # Log the VISA command
        log_visa_command(response, "RECEIVED") # Log the VISA response
        return response
    except Exception as e:
        console_print_func(f"❌ Error querying command '{command}': {e}")
        debug_log(f"Error querying command '{command}': {e}. This goddamn thing is broken!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return None


def get_presets_csv_path(config_file_path, console_print_func):
    # Function Description:
    # Determines the full path to the PRESETS.CSV file.
    # It assumes the CSV file is in the same directory as the main application's config file.
    #
    # Inputs to this function:
    #   config_file_path (str): The full path to the application's configuration file.
    #   console_print_func (function): A function to print messages to the GUI console.
    #
    # Process of this function:
    #   1. Prints debug messages.
    #   2. Extracts the directory from `config_file_path`.
    #   3. Joins the directory with `PRESETS_CSV_FILENAME` to form the full path.
    #   4. Returns the constructed path.
    #
    # Outputs of this function:
    #   str: The full path to the PRESETS.CSV file.
    #
    # (2025-07-30) Change: No functional change, just updated header.
    # (2025-08-01 1920.1) Change: No functional changes.
    # (2025-08-01 2305.1) Change: Refactored debug_print to use debug_log.
    """
    Determines the full path to the PRESETS.CSV file.
    It assumes the CSV file is in the same directory as the main application's config file.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Determining CSV path based on config file: {config_file_path}",
                file=__file__,
                version=current_version,
                function=current_function)
    config_dir = os.path.dirname(config_file_path)
    csv_path = os.path.join(config_dir, PRESETS_CSV_FILENAME)
    debug_log(f"CSV path determined: {csv_path}. Looks good!",
                file=__file__,
                version=current_version,
                function=current_function)
    return csv_path

def load_user_presets_from_csv(config_file_path, console_print_func):
    # Function Description:
    # Loads user-defined preset details from the PRESETS.CSV file.
    # This function reads the CSV, parses each row into a dictionary,
    # and returns a list of these dictionaries. It handles file not found
    # by creating a new one with headers, and parsing errors gracefully.
    #
    # Inputs to this function:
    #   config_file_path (str): The full path to the application's configuration file,
    #                           used to derive the CSV path.
    #   console_print_func (function): A function to print messages to the GUI console.
    #
    # Process of this function:
    #   1. Prints debug messages.
    #   2. Gets the full CSV file path using `get_presets_csv_path`.
    #   3. Initializes an empty list `presets`.
    #   4. Attempts to open and read the CSV file:
    #      a. Uses `csv.DictReader` to read rows as dictionaries.
    #      b. Iterates through rows, converting numeric fields (Center, Span, RBW)
    #         to floats and handling potential `ValueError` during conversion.
    #      c. Appends each processed row to the `presets` list.
    #   5. Handles `FileNotFoundError`:
    #      a. Logs an info message.
    #      b. Ensures the directory for the CSV exists.
    #      c. Creates a new empty CSV file with the predefined headers.
    #      d. Logs success or error for the creation.
    #      e. Returns an empty list, as no presets were loaded.
    #   6. Handles other `Exception`s during file processing, logging an error.
    #   7. Prints success message with the number of loaded presets.
    #   8. Returns the list of loaded presets.
    #
    # Outputs of this function:
    #   list: A list of dictionaries, each representing a user preset.
    #
    # (2025-07-31) Change: Added logic to create empty CSV with headers if FileNotFoundError occurs.
    # (2025-07-31) Change: Stripped whitespace from 'Filename' when reading from CSV.
    # (2025-08-01 1920.1) Change: No functional changes.
    # (2025-08-01 2305.1) Change: Refactored debug_print to use debug_log.
    """
    Loads user-defined preset details from the PRESETS.CSV file.
    Returns a list of dictionaries, each representing a preset.
    If the file is not found, it creates an empty one with headers.
    """
    current_function = inspect.currentframe().f_code.co_name
    csv_file_path = get_presets_csv_path(config_file_path, console_print_func)
    console_print_func(f"Attempting to load presets from CSV file: {csv_file_path}")
    debug_log(f"Attempting to load presets from CSV file: {csv_file_path}. Let's see what's in there!",
                file=__file__,
                version=current_version,
                function=current_function)

    presets = []
    try:
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Strip whitespace from Filename when reading
                if 'Filename' in row and row['Filename'] is not None:
                    row['Filename'] = row['Filename'].strip()

                # Convert numeric values back to float/int
                try:
                    if 'Center' in row and row['Center'] is not None:
                        row['Center'] = float(row['Center'])
                    if 'Span' in row and row['Span'] is not None:
                        row['Span'] = float(row['Span'])
                    if 'RBW' in row and row['RBW'] is not None:
                        row['RBW'] = float(row['RBW']) # Store as float, convert to int for display if needed
                except ValueError as ve:
                    console_print_func(f"❌ Error converting numeric value in CSV row: {row}. Error: {ve}. Skipping row. This is a mess!")
                    debug_log(f"Error converting numeric value in CSV row: {row}. Error: {ve}. Skipping this problematic row!",
                                file=__file__,
                                version=current_version,
                                function=current_function)
                    continue # Skip this row if conversion fails
                presets.append(row)
        console_print_func(f"✅ Loaded {len(presets)} user presets from {csv_file_path}. Success!")
        debug_log(f"Loaded {len(presets)} user presets from {csv_file_path}. Data acquired!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    except FileNotFoundError:
        console_print_func(f"ℹ️ Info: PRESETS.CSV not found at {csv_file_path}. Attempting to create a new one. Where did it go?!")
        debug_log(f"PRESETS.CSV not found at {csv_file_path}. Creating a fresh one!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        # Create the file with headers if it doesn't exist
        try:
            fieldnames = ['Filename', 'Center', 'Span', 'RBW', 'NickName']
            os.makedirs(os.path.dirname(csv_file_path), exist_ok=True) # Ensure directory exists
            with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
            console_print_func(f"✅ Created empty PRESETS.CSV with headers at {csv_file_path}. Done!")
            debug_log(f"Created empty PRESETS.CSV with headers at {csv_file_path}. Fresh start!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except Exception as create_e:
            console_print_func(f"❌ Error creating empty PRESETS.CSV: {create_e}. This is a disaster!")
            debug_log(f"Error creating empty PRESETS.CSV: {create_e}. Fucking hell!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
    except Exception as e:
        console_print_func(f"❌ Error loading presets from CSV: {e}. This is a nightmare!")
        debug_log(f"Error loading presets from CSV: {e}. What the hell happened?!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    return presets

def save_user_preset_to_csv(preset_data, config_file_path, console_print_func):
    # Function Description:
    # Saves a single user-defined preset's details to the PRESETS.CSV file.
    # If the preset already exists (based on 'Filename'), it updates the existing entry.
    # Otherwise, it appends a new entry. It handles file creation and ensures headers.
    #
    # Inputs to this function:
    #   preset_data (dict): A dictionary containing the preset's details,
    #                       must include 'Filename', 'Center', 'Span', 'RBW', 'NickName'.
    #   config_file_path (str): The full path to the application's configuration file,
    #                           used to derive the CSV path.
    #   console_print_func (function): A function to print messages to the GUI console.
    #
    # Process of this function:
    #   1. Prints debug messages.
    #   2. Gets the full CSV file path.
    #   3. Loads all existing presets from the CSV.
    #   4. Checks if the `preset_data['Filename']` already exists in the loaded presets.
    #   5. If it exists, updates the corresponding entry.
    #   6. If it doesn't exist, appends the new `preset_data`.
    #   7. Defines the CSV fieldnames.
    #   8. Opens the CSV file in write mode, ensuring a newline character is used.
    #   9. Creates a `csv.DictWriter` with the defined fieldnames.
    #   10. Writes the header row if the file is new or empty.
    #   11. Writes all (updated) presets back to the CSV.
    #   12. Prints success or error messages.
    #
    # Outputs of this function:
    #   None. Modifies the PRESETS.CSV file.
    #
    # (2025-07-30) Change: No functional change, just updated header.
    # (2025-07-31) Change: Added debug prints to trace Filename comparison for update logic.
    # (2025-07-31) Change: Ensured stripping of whitespace for filenames during comparison.
    # (2025-08-01 1920.1) Change: No functional changes.
    # (2025-08-01 2305.1) Change: Refactored debug_print to use debug_log.
    """
    Saves a single user-defined preset's details to the PRESETS.CSV file.
    If the preset already exists (based on 'Filename'), it updates the existing entry.
    Otherwise, it appends a new entry.
    """
    current_function = inspect.currentframe().f_code.co_name
    console_print_func(f"Attempting to save user preset: {preset_data.get('Filename', 'N/A')}")
    debug_log(f"Attempting to save user preset: {preset_data.get('Filename', 'N/A')}. Let's get this saved!",
                file=__file__,
                version=current_version,
                function=current_function)

    csv_file_path = get_presets_csv_path(config_file_path, console_print_func)
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

    all_presets = load_user_presets_from_csv(config_file_path, console_print_func)
    
    found = False
    # Ensure the new preset's filename is stripped for consistent comparison
    new_preset_filename = preset_data.get('Filename', '').strip() 
    debug_log(f"Normalized new preset filename for comparison: '{new_preset_filename}'",
                file=__file__,
                version=current_version,
                function=current_function)

    for i, p in enumerate(all_presets):
        existing_filename = p.get('Filename', '').strip() # Strip existing filename too
        debug_log(f"Comparing new preset '{new_preset_filename}' with existing preset '{existing_filename}'",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        if existing_filename == new_preset_filename:
            all_presets[i] = preset_data # Update existing entry
            found = True
            console_print_func(f"✅ Updated existing preset '{new_preset_filename}' in CSV data. Nice!")
            debug_log(f"Found existing preset '{new_preset_filename}'. Updated its data. Success!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            break
    
    if not found:
        all_presets.append(preset_data) # Add new preset
        console_print_func(f"✅ Added new preset '{new_preset_filename}' to CSV data. Welcome aboard!")
        debug_log(f"Preset '{new_preset_filename}' not found. Appending as new entry. Fresh data!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    fieldnames = ['Filename', 'Center', 'Span', 'RBW', 'NickName']

    try:
        debug_log(f"Writing {len(all_presets)} presets to CSV file: {csv_file_path}. Almost there!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_presets)
        
        console_print_func(f"✅ User preset '{preset_data.get('Filename', 'N/A')}' successfully saved/updated in PRESETS.CSV. Done and done!")
        debug_log(f"User preset '{preset_data.get('Filename', 'N/A')}' saved/updated to {csv_file_path}. Mission accomplished!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    except Exception as e:
        console_print_func(f"❌ Error saving user preset to CSV: {e}. This is a nightmare!")
        debug_log(f"Error saving user preset to CSV: {e}. Fucking hell!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

def query_device_presets(inst, console_print_func):
    # Function Description:
    # Queries the connected instrument for a list of available preset files (.STA).
    # This is a low-level function that sends the SCPI command and parses the response.
    #
    # Inputs to this function:
    #   inst (pyvisa.resources.Resource): The connected PyVISA instrument instance.
    #   console_print_func (function): A function to print messages to the GUI console.
    #
    # Process of this function:
    #   1. Prints debug messages.
    #   2. Sends the `:MMEMory:CATalog? "C:\\PRESETS\\"` SCPI command to the instrument.
    #   3. Parses the raw response string, splitting by commas.
    #   4. Filters the parts to find filenames ending with ".STA".
    #   5. Returns a sorted list of unique .STA filenames.
    #   6. Handles `pyvisa.errors.VisaIOError` and other exceptions, returning None on error.
    #
    # Outputs of this function:
    #   list or None: A sorted list of .STA preset filenames, or None if an error occurs.
    #
    # (2025-07-30) Change: No functional change, just updated header.
    # (2025-08-01 2305.1) Change: Refactored debug_print to use debug_log.
    """
    Queries the connected instrument for a list of available preset files (.STA).
    Returns a list of these filenames.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Instrument instance (inside preset_utils): {inst}. Ready to query!",
                file=__file__,
                version=current_version,
                function=current_function)
    console_print_func("Querying device preset files from C:\\PRESETS\\... Hold tight!")
    debug_log("Querying device preset files from C:\\PRESETS\\...",
                file=__file__,
                version=current_version,
                function=current_function)

    try:
        # Query the instrument for a catalog of files in the C:\PRESETS directory
        command = ':MMEMory:CATalog? "C:\\PRESETS\\"'
        debug_log(f"Attempting query: '{command}'. Sending the command!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        raw_response = query_safe(inst, command, console_print_func)

        if not raw_response:
            console_print_func("❌ No response or empty response from instrument for preset catalog. What the hell?!")
            debug_log("Empty response from instrument for preset catalog. Fucking useless!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return None

        debug_log(f"Response from instrument (with path): '{raw_response}'. Got some data!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Parse the response string
        # The response is typically a comma-separated list of values, including filenames
        parts = raw_response.split(',')
        preset_files = []
        for i, part in enumerate(parts):
            if part.strip().lower().endswith(".sta"):
                # Ensure we get the full filename, not just a partial match
                preset_files.append(part.strip())
        
        # Remove duplicates and sort
        unique_preset_files = sorted(list(set(preset_files)))
        
        console_print_func(f"✅ Found {len(unique_preset_files)} '.STA' preset files on the instrument. Success!")
        debug_log(f"Found {len(unique_preset_files)} '.STA' preset files. That's a lot of presets!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return unique_preset_files

    except pyvisa.errors.VisaIOError as e:
        console_print_func(f"❌ VISA error while querying device presets: {e}. This is a nightmare!")
        debug_log(f"VISA Error querying device presets: {e}. Fucking hell!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return None
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred while querying device presets: {e}. This is a disaster!")
        debug_log(f"An unexpected error occurred while querying device presets: {e}. What the hell happened?!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return None

def query_device_presets_logic(app_instance, console_print_func):
    # Function Description:
    # Orchestrates the querying of device presets, handling the instrument instance
    # and populating the GUI with the found presets.
    #
    # Inputs to this function:
    #   app_instance (object): Reference to the main application instance
    #                          to access the instrument instance (`app_instance.inst`)
    #                          and the preset files tab (`app_instance.preset_files_tab`).
    #   console_print_func (function): A function to print messages to the GUI console.
    #
    # Process of this function:
    #   1. Prints debug messages.
    #   2. Checks if an instrument is connected (`app_instance.inst`).
    #   3. If connected, calls `query_device_presets` to get the list of presets.
    #   4. If presets are found, populates the `preset_files_tab` with them.
    #   5. Logs success or failure messages.
    #   6. Returns the list of presets or None.
    #
    # Outputs of this function:
    #   list or None: A list of preset names if successful, None otherwise.
    #
    # (2025-07-30) Change: No functional change, just updated header.
    # (2025-08-01 2305.1) Change: Refactored debug_print to use debug_log.
    """
    Orchestrates the querying of device presets, handling the instrument instance
    and populating the GUI with the found presets.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Calling query_device_presets_logic... Let's see what the device has!",
                file=__file__,
                version=current_version,
                function=current_function)
    
    if not app_instance.inst:
        console_print_func("⚠️ Warning: No instrument connected. Cannot query device presets. Connect the damn thing first!")
        debug_log("No instrument connected, cannot query device presets. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        if hasattr(app_instance, 'presets_parent_tab') and hasattr(app_instance.presets_parent_tab, 'preset_files_tab'):
            app_instance.presets_parent_tab.preset_files_tab.populate_instrument_preset_buttons([]) # Clear buttons if no instrument
        return None
    
    # Add debug print for app_instance.inst before calling query_device_presets
    console_print_func(f"Instrument instance in query_device_presets_logic: {app_instance.inst}. Ready to go!")
    debug_log(f"Instrument instance in query_device_presets_logic: {app_instance.inst}. It's alive!",
                file=__file__,
                version=current_version,
                function=current_function)

    # Directly call the query_device_presets function within this module
    presets = query_device_presets(app_instance.inst, console_print_func)
    
    if presets is not None:
        if hasattr(app_instance, 'presets_parent_tab') and hasattr(app_instance.presets_parent_tab, 'preset_files_tab'):
            # FIX: Corrected function name and removed redundant 'source' argument
            app_instance.presets_parent_tab.preset_files_tab.populate_instrument_preset_buttons(presets)
        console_print_func(f"✅ Queried {len(presets)} presets from device. Success!")
        debug_log(f"Queried {len(presets)} presets from device. That's a good haul!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return presets # Return the list of presets
    else:
        console_print_func("❌ Failed to query presets from device. This is frustrating!")
        debug_log("Failed to query presets from device. What a pain!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        if hasattr(app_instance, 'presets_parent_tab') and hasattr(app_instance.presets_parent_tab, 'preset_files_tab'):
            app_instance.presets_parent_tab.preset_files_tab.populate_instrument_preset_buttons([]) # Clear buttons on failure
        return None

def load_selected_preset(inst, preset_name, console_print_func):
    # Function Description:
    # Loads a specified preset file onto the instrument.
    # This is a low-level function that sends the SCPI command and parses the response.
    #
    # Inputs to this function:
    #   inst (pyvisa.resources.Resource): The connected PyVISA instrument instance.
    #   preset_name (str): The name of the preset file (e.g., "MY_PRESET.STA") to load.
    #   console_print_func (function): A function to print messages to the GUI console.
    #
    # Process of this function:
    #   1. Prints debug messages.
    #   2. Constructs the SCPI command to load the preset.
    #   3. Sends the command to the instrument using `write_safe`.
    #   4. Logs success or failure messages.
    #   5. Returns True on success, False on failure.
    #
    # Outputs of this function:
    #   bool: True if the preset load command was sent successfully, False otherwise.
    #
    # (2025-07-30) Change: No functional change, just updated header.
    # (2025-08-01 2305.1) Change: Refactored debug_print to use debug_log.
    """
    Loads a specified preset file onto the instrument.
    Returns True on success, False on failure.
    """
    current_function = inspect.currentframe().f_code.co_name
    console_print_func(f"Attempting to load preset: {preset_name}")
    debug_log(f"Attempting to load preset: {preset_name}. Let's get this loaded!",
                file=__file__,
                version=current_version,
                function=current_function)

    try:
        # The instrument expects the path with double backslashes
        # Example: ':MMEMory:LOAD STA,"C:\\PRESETS\\MY_PRESET.STA"'
        # Ensure the preset_name includes the .STA extension
        full_preset_path = f"C:\\PRESETS\\{preset_name}"
        command = f':MMEMory:LOAD STA,"{full_preset_path}"'
        debug_log(f"Command to send: '{command}'. Sending the load command!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        
        success = write_safe(inst, command, console_print_func)
        if success:
            console_print_func(f"✅ Preset '{preset_name}' load command sent successfully. Done!")
            debug_log(f"Preset '{preset_name}' load command sent successfully. BOOM!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return True
        else:
            console_print_func(f"❌ Failed to send load command for preset '{preset_name}'. This is a nightmare!")
            debug_log(f"Failed to send load command for preset '{preset_name}'. What the hell happened?!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return False
    except pyvisa.errors.VisaIOError as e:
        console_print_func(f"❌ VISA error while loading preset '{preset_name}': {e}. This is a disaster!")
        debug_log(f"VISA Error loading preset '{preset_name}': {e}. Fucking hell!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred while loading preset '{preset_name}': {e}. This is frustrating!")
        debug_log(f"An unexpected error occurred while loading preset '{preset_name}': {e}. What a pain!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False

def load_selected_preset_logic(app_instance, selected_preset_name, console_print_func):
    # Function Description:
    # Orchestrates the loading of a selected preset onto the instrument.
    # This function first sends the command to load the preset, then
    # queries the instrument for its *actual* current settings (Center, Span, RBW)
    # using the dedicated `query_basic_instrument_settings_logic` function.
    # It returns these queried values to the caller for GUI updates and caching.
    #
    # Inputs to this function:
    #   app_instance (object): Reference to the main application instance
    #                          to access the instrument instance (`app_instance.inst`).
    #   selected_preset_name (str): The name of the preset file to load.
    #   console_print_func (function): A function to print messages to the GUI console.
    #
    # Process of this function:
    #   1. Prints debug messages.
    #   2. Checks if an instrument is connected; if not, logs a warning and returns False with default values.
    #   3. Calls `load_selected_preset` to send the load command to the instrument.
    #   4. If the load command is successful, calls `query_basic_instrument_settings_logic`
    #      to get the actual current settings (Center, Span, RBW) from the instrument.
    #   5. Updates `app_instance`'s current settings display variables (Center, Span, RBW).
    #   6. Returns True and the queried settings on success, or False and default values on failure.
    #   7. Handles exceptions during the process.
    #
    # Outputs of this function:
    #   tuple: (success_status, center_freq_hz, span_hz, rbw_hz)
    #          success_status (bool): True if preset loaded and settings queried, False otherwise.
    #          center_freq_hz (float): Center frequency in Hz after load, or 0.0 on failure.
    #          span_hz (float): Span in Hz after load, or 0.0 on failure.
    #          rbw_hz (float): RBW in Hz after load, or 0.0 on failure.
    #
    # (2025-07-30) Change: Now calls `query_basic_instrument_settings_logic` instead of `query_current_instrument_settings_logic`.
    # (2025-08-01 2305.1) Change: Refactored debug_print to use debug_log.
    """
    Orchestrates the loading of a selected preset onto the instrument.
    After loading, it queries the instrument for its actual current settings
    (Center, Span, RBW) and returns them.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Calling load_selected_preset_logic for: {selected_preset_name}. Let's get this done!",
                file=__file__,
                version=current_version,
                function=current_function)

    if not app_instance.inst:
        console_print_func("⚠️ Warning: No instrument connected. Cannot load preset. Connect the damn thing first!")
        debug_log("No instrument connected, cannot load preset. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False, 0.0, 0.0, 0.0

    try:
        # First, send the command to load the preset
        load_success = load_selected_preset(app_instance.inst, selected_preset_name, console_print_func)
        
        if load_success:
            # After loading, query the instrument for the actual current settings
            # Use the new, focused query_basic_instrument_settings_logic
            center_freq_hz, span_hz, rbw_hz = query_basic_instrument_settings_logic(app_instance, console_print_func)

            # Update app_instance's current settings display variables
            # These are for the main Instrument tab's display, not the preset buttons
            if hasattr(app_instance, 'instrument_parent_tab') and hasattr(app_instance.instrument_parent_tab, 'instrument_connection_tab'):
                app_instance.instrument_parent_tab.instrument_connection_tab.current_center_freq_var.set(f"{center_freq_hz / MHZ_TO_HZ:.3f}")
                app_instance.instrument_parent_tab.instrument_connection_tab.current_span_var.set(f"{span_hz / MHZ_TO_HZ:.3f}")
                app_instance.instrument_parent_tab.instrument_connection_tab.current_rbw_var.set(f"{rbw_hz:.0f}")
                # The other variables (Ref Level, Freq Shift, High Sensitivity) are not updated here
                # as this function is for basic settings only. They are handled by query_current_instrument_settings_logic.
            
            console_print_func(f"GUI settings updated from preset: Center Freq={center_freq_hz / MHZ_TO_HZ:.3f} MHz, Span={span_hz / MHZ_TO_HZ:.3f} MHz, RBW={rbw_hz:.0f} Hz. Looking good!")
            debug_log(f"GUI settings updated from loaded preset. Success!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            
            return True, center_freq_hz, span_hz, rbw_hz
        else:
            console_print_func(f"❌ Failed to load preset '{selected_preset_name}'. This is frustrating!")
            debug_log(f"Failed to load preset '{selected_preset_name}'. What a pain!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return False, 0.0, 0.0, 0.0

    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred in load_selected_preset_logic: {e}. This is a disaster!")
        debug_log(f"An unexpected error occurred in load_selected_preset_logic: {e}. Fucking hell!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False, 0.0, 0.0, 0.0
