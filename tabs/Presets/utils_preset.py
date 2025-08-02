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
# Version 20250802.0225.1 (Addressed elusive SyntaxError by re-typing and verifying structure.)

current_version = "20250802.0225.1" # this variable should always be defined below the header to make the debugging better
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

# Import necessary functions from instrument_logic and frequency_bands
from src.instrument_logic import query_current_instrument_settings_logic
from ref.frequency_bands import MHZ_TO_HZ

# Define constants
PRESETS_CSV_FILENAME = "PRESETS.CSV"
VBW_RBW_RATIO = 3 # Moved this to a module-level constant for better practice and to resolve potential syntax issues.

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
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Loading user presets from CSV. Let's see what we've got!",
                file=__file__,
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
                                file=__file__,
                                version=current_version,
                                function=current_function)
        console_print_func(f"✅ Loaded {len(presets)} user presets from {csv_path}.")
        debug_log(f"Successfully loaded {len(presets)} user presets from {csv_path}.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    except FileNotFoundError:
        console_print_func(f"ℹ️ User presets file not found at {csv_path}. Creating a new one.")
        debug_log(f"User presets file not found. Creating new file at {csv_path}.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        # Create the file with headers
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Filename', 'Center', 'Span', 'RBW', 'NickName']) # Add other headers if needed
        console_print_func("✅ New user presets file created with headers.")
        debug_log("New user presets file created.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    except IOError as e:
        console_print_func(f"❌ I/O Error loading user presets from {csv_path}: {e}. This is a disaster!")
        debug_log(f"IOError loading user presets: {e}. Fucking hell!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred loading user presets: {e}. What a mess!")
        debug_log(f"Unexpected error loading user presets: {e}. This is a pain in the ass!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    return presets

def save_user_preset_to_csv(preset_data, config_file_path, console_print_func):
    """
    Function Description:
    Saves a new user-defined preset to the PRESETS.CSV file.
    Appends the new preset data as a new row to the CSV.

    Inputs to this function:
      preset_data (dict): A dictionary containing the preset details (e.g., 'Filename', 'Center', 'Span', 'RBW', 'NickName').
      config_file_path (str): The full path to the application's configuration file,
                              used to derive the CSV path.
      console_print_func (function): A function to print messages to the GUI console.

    Process of this function:
      1. Prints debug messages.
      2. Gets the full CSV file path using `get_presets_csv_path`.
      3. Determines if the file exists to decide whether to write headers.
      4. Opens the CSV file in append mode.
      5. Uses `csv.DictWriter` to write the `preset_data` as a new row.
      6. Handles potential `IOError` or general `Exception`.

    Outputs of this function:
      None. Appends data to the CSV file.

    (2025-07-30) Change: Initial implementation.
    (2025-07-31) Change: Added error handling for CSV writing.
    (2025-08-01 1920.1) Change: No functional changes.
    (2025-08-01 2305.1) Change: Refactored debug_print to use debug_log.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Saving user preset to CSV: {preset_data.get('NickName', 'Unnamed')}. Don't mess this up!",
                file=__file__,
                version=current_version,
                function=current_function)

    csv_path = get_presets_csv_path(config_file_path, console_print_func)
    file_exists = os.path.exists(csv_path)

    try:
        with open(csv_path, mode='a', newline='', encoding='utf-8') as file:
            fieldnames = ['Filename', 'Center', 'Span', 'RBW', 'NickName'] # Ensure all expected fields are here
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader() # Write header only if file didn't exist

            writer.writerow(preset_data)
        console_print_func(f"✅ Preset '{preset_data.get('NickName', 'Unnamed')}' saved to {csv_path}.")
        debug_log(f"Preset '{preset_data.get('NickName', 'Unnamed')}' successfully saved to {csv_path}.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    except IOError as e:
        console_print_func(f"❌ I/O Error saving user preset to {csv_path}: {e}. This is a disaster!")
        debug_log(f"IOError saving user preset: {e}. Fucking hell!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred saving user preset: {e}. What a mess!")
        debug_log(f"Unexpected error saving user preset: {e}. This is a pain in the ass!",
                    file=__file__,
                    version=current_version,
                    function=current_function)


def query_device_presets_logic(app_instance, console_print_func=None):
    """
    Function Description:
    Queries the connected instrument for its saved presets and returns a list of their names.

    Inputs:
    - app_instance (object): The main application instance, used to access `inst`.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Prints a debug message.
    2. Checks if an instrument is connected. If not, logs an error and returns an empty list.
    3. Queries the instrument for its state catalog using `:MMEMory:CATalog:STATe?`.
    4. Parses the response to extract preset names.
    5. Handles potential errors during query or parsing.

    Outputs of this function:
    - list: A list of strings, where each string is the name of a device preset.
            Returns an empty list if no instrument is connected or an error occurs.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Querying device presets. Let's see what the instrument has stored!",
                file=__file__,
                version=current_version,
                function=current_function)

    if not app_instance.inst:
        console_print_func("⚠️ Not connected to an instrument. Cannot query device presets.")
        debug_log("No instrument connected for querying device presets. Aborting.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return []

    try:
        # Query the instrument's state catalog
        response = query_safe(app_instance.inst, ":MMEMory:CATalog:STATe?", console_print_func)
        if response:
            # Response is typically a comma-separated string of preset names
            # Example: "DEFAULT,USER1,USER2"
            presets = [p.strip().strip("'\"") for p in response.split(',') if p.strip()]
            console_print_func(f"✅ Found {len(presets)} device presets: {', '.join(presets)}.")
            debug_log(f"Device presets found: {presets}. Awesome!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return presets
        else:
            console_print_func("ℹ️ No device presets found or empty response from instrument.")
            debug_log("Empty response for device presets query.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return []
    except Exception as e:
        console_print_func(f"❌ Error querying device presets: {e}. This is a disaster!")
        debug_log(f"Error querying device presets: {e}. Fucking hell!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return []


def load_selected_preset_logic(app_instance, selected_preset_name, console_print_func=None):
    """
    Function Description:
    Loads a selected preset from the instrument (if connected) or from user-defined CSV.
    Updates the GUI's Tkinter variables with the loaded settings.

    Inputs:
    - app_instance (object): The main application instance, used to access `inst`,
                             `config`, and various Tkinter variables for settings.
    - selected_preset_name (str): The name of the preset to load.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Prints a debug message.
    2. Determines if the preset is a device preset or a user preset.
    3. If device preset and instrument is connected:
       a. Sends `:MMEMory:LOAD:STATe` command to the instrument.
       b. Queries the instrument for its new settings (Center Freq, Span, RBW, Ref Level).
       c. Updates the GUI's Tkinter variables with these values.
    4. If user preset:
       a. Loads all user presets from CSV.
       b. Finds the matching preset data.
       c. Updates the GUI's Tkinter variables with the loaded values.
    5. Saves the loaded preset name to config.
    6. Logs success or failure.

    Outputs of this function:
    - tuple: (bool, float, float, float) - (success, center_freq_hz, span_hz, rbw_hz).
             Returns (False, 0.0, 0.0, 0.0) on failure.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Loading selected preset: {selected_preset_name}. Let's make this happen!",
                file=__file__,
                version=current_version,
                function=current_function)

    center_freq_hz = 0.0
    span_hz = 0.0
    rbw_hz = 0.0

    try:
        # Check if it's a device preset (usually uppercase, no path)
        # This is a heuristic; a more robust solution might involve querying device presets first
        if app_instance.inst and selected_preset_name.isupper() and "::" not in selected_preset_name:
            console_print_func(f"Attempting to load device preset: {selected_preset_name} from instrument.")
            write_safe(app_instance.inst, f":MMEMory:LOAD:STATe '{selected_preset_name}'", console_print_func)
            time.sleep(1) # Give instrument time to load the preset

            # After loading, query the instrument for its new settings
            success = query_current_instrument_settings_logic(app_instance, console_print_func)
            if success:
                center_freq_hz = app_instance.center_freq_hz_var.get()
                span_hz = app_instance.span_hz_var.get()
                rbw_hz = app_instance.rbw_hz_var.get()
                console_print_func(f"✅ Device preset '{selected_preset_name}' loaded and GUI updated.")
                debug_log(f"Device preset '{selected_preset_name}' loaded. UI synced!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            else:
                console_print_func(f"❌ Failed to query settings after loading device preset '{selected_preset_name}'.")
                debug_log(f"Failed to query settings after loading device preset '{selected_preset_name}'. What a pain!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                return False, 0.0, 0.0, 0.0
        else:
            # Assume it's a user preset from CSV
            console_print_func(f"Attempting to load user preset: {selected_preset_name} from CSV.")
            user_presets = load_user_presets_from_csv(app_instance.CONFIG_FILE_PATH, console_print_func)
            found_preset = next((p for p in user_presets if p.get('NickName') == selected_preset_name), None)

            if found_preset:
                center_freq_hz = found_preset.get('Center', 0.0)
                span_hz = found_preset.get('Span', 0.0)
                rbw_hz = found_preset.get('RBW', 0.0)

                # Update Tkinter variables in app_instance
                app_instance.center_freq_hz_var.set(center_freq_hz)
                app_instance.span_hz_var.set(span_hz)
                app_instance.rbw_hz_var.set(rbw_hz)
                # VBW will be set based on RBW if ratio is applied, or default
                app_instance.vbw_hz_var.set(rbw_hz * VBW_RBW_RATIO) # Apply default ratio or load from preset if available
                
                # Update other settings if they are part of the user preset data
                # For now, only basic settings are handled.
                # Ref Level, Freq Shift, High Sensitivity are not updated here
                # as this function is for basic settings only. They are handled by query_current_instrument_settings_logic.
            
            console_print_func(f"GUI settings updated from preset: Center Freq={center_freq_hz / MHZ_TO_HZ:.3f} MHz, Span={span_hz / MHZ_TO_HZ:.3f} MHz, RBW={rbw_hz:.0f} Hz. Looking good!")
            debug_log(f"GUI settings updated from loaded preset. Success!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            
            return True, center_freq_hz, span_hz, rbw_hz

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
