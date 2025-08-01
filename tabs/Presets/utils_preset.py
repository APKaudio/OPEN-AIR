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
#
# Version 20250801.1056.1 (Updated header and verified imports for new folder structure)

current_version = "20250801.1056.1" # this variable should always be defined below the header to make the debugging better

import pyvisa
import time
import inspect
import os
from datetime import datetime
import csv

# Import necessary functions from instrument_control and frequency_bands - CORRECTED PATHS
from utils.utils_instrument_control import debug_print, query_safe, write_safe, query_current_instrument_settings
from ref.frequency_bands import MHZ_TO_HZ

# NEW: Import query_basic_instrument_settings_logic from instrument_logic - CORRECTED PATH
# This is needed by load_selected_preset_logic
from src.instrument_logic import query_basic_instrument_settings_logic, query_current_instrument_settings_logic

# Define the CSV filename for user-saved presets
PRESETS_CSV_FILENAME = "PRESETS.CSV"

def get_presets_csv_path(config_file_path, console_print_func):
    # Function Description:
    # Determines the full path to the PRESETS.CSV file.
    # It assumes the CSV file is in the same directory as the main application's config file.
    #
    # Inputs to this function:
    #   config_file_path (str): The full path to the application's configuration file.
    #   console_print_func (function): A function to print messages to the console.
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
    """
    Determines the full path to the PRESETS.CSV file.
    It assumes the CSV file is in the same directory as the main application's config file.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Determining CSV path based on config file: {config_file_path}", file=current_file, function=current_function, console_print_func=console_print_func)
    config_dir = os.path.dirname(config_file_path)
    csv_path = os.path.join(config_dir, PRESETS_CSV_FILENAME)
    debug_print(f"CSV path determined: {csv_path}", file=current_file, function=current_function, console_print_func=console_print_func)
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
    #   console_print_func (function): A function to print messages to the console.
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
    """
    Loads user-defined preset details from the PRESETS.CSV file.
    Returns a list of dictionaries, each representing a preset.
    If the file is not found, it creates an empty one with headers.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    csv_file_path = get_presets_csv_path(config_file_path, console_print_func)
    console_print_func(f"Attempting to load presets from CSV file: {csv_file_path}")
    debug_print(f"Attempting to load presets from CSV file: {csv_file_path}", file=current_file, function=current_function, console_print_func=console_print_func)

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
                    console_print_func(f"❌ Error converting numeric value in CSV row: {row}. Error: {ve}. Skipping row.")
                    debug_print(f"Error converting numeric value in CSV row: {row}. Error: {ve}", file=current_file, function=current_function, console_print_func=console_print_func)
                    continue # Skip this row if conversion fails
                presets.append(row)
        console_print_func(f"✅ Loaded {len(presets)} user presets from {csv_file_path}.")
        debug_print(f"Loaded {len(presets)} user presets from {csv_file_path}.", file=current_file, function=current_function, console_print_func=console_print_func)
    except FileNotFoundError:
        console_print_func(f"ℹ️ Info: PRESETS.CSV not found at {csv_file_path}. Attempting to create a new one.")
        debug_print(f"PRESETS.CSV not found at {csv_file_path}.", file=current_file, function=current_function, console_print_func=console_print_func)
        # Create the file with headers if it doesn't exist
        try:
            fieldnames = ['Filename', 'Center', 'Span', 'RBW', 'NickName']
            os.makedirs(os.path.dirname(csv_file_path), exist_ok=True) # Ensure directory exists
            with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
            console_print_func(f"✅ Created empty PRESETS.CSV with headers at {csv_file_path}.")
            debug_print(f"Created empty PRESETS.CSV with headers at {csv_file_path}.", file=current_file, function=current_function, console_print_func=console_print_func)
        except Exception as create_e:
            console_print_func(f"❌ Error creating empty PRESETS.CSV: {create_e}")
            debug_print(f"Error creating empty PRESETS.CSV: {create_e}", file=current_file, function=current_function, console_print_func=console_print_func)
    except Exception as e:
        console_print_func(f"❌ Error loading presets from CSV: {e}")
        debug_print(f"Error loading presets from CSV: {e}", file=current_file, function=current_function, console_print_func=console_print_func)
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
    #   console_print_func (function): A function to print messages to the console.
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
    """
    Saves a single user-defined preset's details to the PRESETS.CSV file.
    If the preset already exists (based on 'Filename'), it updates the existing entry.
    Otherwise, it appends a new entry.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    console_print_func(f"Attempting to save user preset: {preset_data.get('Filename', 'N/A')}")
    debug_print(f"Attempting to save user preset: {preset_data.get('Filename', 'N/A')}", file=current_file, function=current_function, console_print_func=console_print_func)

    csv_file_path = get_presets_csv_path(config_file_path, console_print_func)
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

    all_presets = load_user_presets_from_csv(config_file_path, console_print_func)
    
    found = False
    # Ensure the new preset's filename is stripped for consistent comparison
    new_preset_filename = preset_data.get('Filename', '').strip() 
    debug_print(f"Normalized new preset filename for comparison: '{new_preset_filename}'", file=current_file, function=current_function, console_print_func=console_print_func)

    for i, p in enumerate(all_presets):
        existing_filename = p.get('Filename', '').strip() # Strip existing filename too
        debug_print(f"Comparing new preset '{new_preset_filename}' with existing preset '{existing_filename}'", file=current_file, function=current_function, console_print_func=console_print_func)
        if existing_filename == new_preset_filename:
            all_presets[i] = preset_data # Update existing entry
            found = True
            console_print_func(f"✅ Updated existing preset '{new_preset_filename}' in CSV data.")
            debug_print(f"Found existing preset '{new_preset_filename}'. Updated its data.", file=current_file, function=current_function, console_print_func=console_print_func)
            break
    
    if not found:
        all_presets.append(preset_data) # Add new preset
        console_print_func(f"✅ Added new preset '{new_preset_filename}' to CSV data.")
        debug_print(f"Preset '{new_preset_filename}' not found. Appending as new entry.", file=current_file, function=current_function, console_print_func=console_print_func)

    fieldnames = ['Filename', 'Center', 'Span', 'RBW', 'NickName']

    try:
        debug_print(f"Writing {len(all_presets)} presets to CSV file: {csv_file_path}", file=current_file, function=current_function, console_print_func=console_print_func)
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_presets)
        
        console_print_func(f"✅ User preset '{preset_data.get('Filename', 'N/A')}' successfully saved/updated in PRESETS.CSV.")
        debug_print(f"User preset '{preset_data.get('Filename', 'N/A')}' saved/updated to {csv_file_path}", file=current_file, function=current_function, console_print_func=console_print_func)

    except Exception as e:
        console_print_func(f"❌ Error saving user preset to CSV: {e}")
        debug_print(f"Error saving user preset to CSV: {e}", file=current_file, function=current_function, console_print_func=console_print_func)

def query_device_presets(inst, console_print_func):
    # Function Description:
    # Queries the connected instrument for a list of available preset files (.STA).
    # This is a low-level function that sends the SCPI command and parses the response.
    #
    # Inputs to this function:
    #   inst (pyvisa.resources.Resource): The connected PyVISA instrument instance.
    #   console_print_func (function): A function to print messages to the console.
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
    """
    Queries the connected instrument for a list of available preset files (.STA).
    Returns a list of these filenames.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Instrument instance (inside preset_utils): {inst}", file=current_file, function=current_function, console_print_func=console_print_func)
    console_print_func("Querying device preset files from C:\\PRESETS\\...")
    debug_print("Querying device preset files from C:\\PRESETS\\...", file=current_file, function=current_function, console_print_func=console_print_func)

    try:
        # Query the instrument for a catalog of files in the C:\PRESETS directory
        command = ':MMEMory:CATalog? "C:\\PRESETS\\"'
        debug_print(f"Attempting query: '{command}'", file=current_file, function=current_function, console_print_func=console_print_func)
        raw_response = query_safe(inst, command, console_print_func)

        if not raw_response:
            console_print_func("❌ No response or empty response from instrument for preset catalog.")
            debug_print("Empty response from instrument for preset catalog.", file=current_file, function=current_function, console_print_func=console_print_func)
            return None

        debug_print(f"Response from instrument (with path): '{raw_response}'", file=current_file, function=current_function, console_print_func=console_print_func)

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
        
        console_print_func(f"✅ Found {len(unique_preset_files)} '.STA' preset files on the instrument.")
        debug_print(f"Found {len(unique_preset_files)} '.STA' preset files.", file=current_file, function=current_function, console_print_func=console_print_func)
        return unique_preset_files

    except pyvisa.errors.VisaIOError as e:
        console_print_func(f"❌ VISA error while querying device presets: {e}")
        debug_print(f"VISA Error querying device presets: {e}", file=current_file, function=current_function, console_print_func=console_print_func)
        return None
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred while querying device presets: {e}")
        debug_print(f"An unexpected error occurred while querying device presets: {e}", file=current_file, function=current_function, console_print_func=console_print_func)
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
    #   console_print_func (function): A function to print messages to the console.
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
    """
    Orchestrates the querying of device presets, handling the instrument instance
    and populating the GUI with the found presets.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print("Calling query_device_presets_logic...", file=current_file, function=current_function, console_print_func=console_print_func)
    
    if not app_instance.inst:
        console_print_func("⚠️ Warning: No instrument connected. Cannot query device presets.")
        debug_print("No instrument connected, cannot query device presets.", file=current_file, function=current_function, console_print_func=console_print_func)
        if hasattr(app_instance, 'preset_files_tab'):
            app_instance.preset_files_tab.populate_instrument_preset_buttons([]) # Clear buttons if no instrument
        return None
    
    # Add debug print for app_instance.inst before calling query_device_presets
    console_print_func(f"Instrument instance in query_device_presets_logic: {app_instance.inst}")
    debug_print(f"Instrument instance in query_device_presets_logic: {app_instance.inst}", file=current_file, function=current_function, console_print_func=console_print_func)

    # Directly call the query_device_presets function within this module
    presets = query_device_presets(app_instance.inst, console_print_func)
    
    if presets is not None:
        if hasattr(app_instance, 'preset_files_tab'):
            # FIX: Corrected function name and removed redundant 'source' argument
            app_instance.preset_files_tab.populate_instrument_preset_buttons(presets)
        console_print_func(f"✅ Queried {len(presets)} presets from device.")
        debug_print(f"Queried {len(presets)} presets from device.", file=current_file, function=current_function, console_print_func=console_print_func)
        return presets # Return the list of presets
    else:
        console_print_func("❌ Failed to query presets from device.")
        debug_print("Failed to query presets from device.", file=current_file, function=current_function, console_print_func=console_print_func)
        if hasattr(app_instance, 'preset_files_tab'):
            app_instance.preset_files_tab.populate_instrument_preset_buttons([]) # Clear buttons on failure
        return None

def load_selected_preset(inst, preset_name, console_print_func):
    # Function Description:
    # Loads a specified preset file onto the instrument.
    # This is a low-level function that sends the SCPI command and parses the response.
    #
    # Inputs to this function:
    #   inst (pyvisa.resources.Resource): The connected PyVISA instrument instance.
    #   preset_name (str): The name of the preset file (e.g., "MY_PRESET.STA") to load.
    #   console_print_func (function): A function to print messages to the console.
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
    """
    Loads a specified preset file onto the instrument.
    Returns True on success, False on failure.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    console_print_func(f"Attempting to load preset: {preset_name}")
    debug_print(f"Attempting to load preset: {preset_name}", file=current_file, function=current_function, console_print_func=console_print_func)

    try:
        # The instrument expects the path with double backslashes
        # Example: ':MMEMory:LOAD STA,"C:\\PRESETS\\MY_PRESET.STA"'
        # Ensure the preset_name includes the .STA extension
        full_preset_path = f"C:\\PRESETS\\{preset_name}"
        command = f':MMEMory:LOAD STA,"{full_preset_path}"'
        debug_print(f"Command to send: '{command}'", file=current_file, function=current_function, console_print_func=console_print_func)
        
        success = write_safe(inst, command, console_print_func)
        if success:
            console_print_func(f"✅ Preset '{preset_name}' load command sent successfully.")
            debug_print(f"Preset '{preset_name}' load command sent successfully.", file=current_file, function=current_function, console_print_func=console_print_func)
            return True
        else:
            console_print_func(f"❌ Failed to send load command for preset '{preset_name}'.")
            debug_print(f"Failed to send load command for preset '{preset_name}'.", file=current_file, function=current_function, console_print_func=console_print_func)
            return False
    except pyvisa.errors.VisaIOError as e:
        console_print_func(f"❌ VISA error while loading preset '{preset_name}': {e}")
        debug_print(f"VISA Error loading preset '{preset_name}': {e}", file=current_file, function=current_function, console_print_func=console_print_func)
        return False
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred while loading preset '{preset_name}': {e}")
        debug_print(f"An unexpected error occurred while loading preset '{preset_name}': {e}", file=current_file, function=current_function, console_print_func=console_print_func)
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
    #   console_print_func (function): A function to print messages to the console.
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
    """
    Orchestrates the loading of a selected preset onto the instrument.
    After loading, it queries the instrument for its actual current settings
    (Center, Span, RBW) and returns them.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Calling load_selected_preset_logic for: {selected_preset_name}", file=current_file, function=current_function, console_print_func=console_print_func)

    if not app_instance.inst:
        console_print_func("⚠️ Warning: No instrument connected. Cannot load preset.")
        debug_print("No instrument connected, cannot load preset.", file=current_file, function=current_function, console_print_func=console_print_func)
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
            if hasattr(app_instance, 'instrument_tab'):
                app_instance.instrument_tab.current_center_freq_var.set(f"{center_freq_hz / MHZ_TO_HZ:.3f}")
                app_instance.instrument_tab.current_span_var.set(f"{span_hz / MHZ_TO_HZ:.3f}")
                app_instance.instrument_tab.current_rbw_var.set(f"{rbw_hz:.0f}")
                # The other variables (Ref Level, Freq Shift, High Sensitivity) are not updated here
                # as this function is for basic settings only. They are handled by query_current_instrument_settings_logic.
            
            console_print_func(f"GUI settings updated from preset: Center Freq={center_freq_hz / MHZ_TO_HZ:.3f} MHz, Span={span_hz / MHZ_TO_HZ:.3f} MHz, RBW={rbw_hz:.0f} Hz")
            debug_print(f"GUI settings updated from loaded preset.", file=current_file, function=current_function, console_print_func=console_print_func)
            
            return True, center_freq_hz, span_hz, rbw_hz
        else:
            console_print_func(f"❌ Failed to load preset '{selected_preset_name}'.")
            debug_print(f"Failed to load preset '{selected_preset_name}'.", file=current_file, function=current_function, console_print_func=console_print_func)
            return False, 0.0, 0.0, 0.0

    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred in load_selected_preset_logic: {e}")
        debug_print(f"An unexpected error occurred in load_selected_preset_logic: {e}", file=current_file, function=current_function, console_print_func=console_print_func)
        return False, 0.0, 0.0, 0.0
