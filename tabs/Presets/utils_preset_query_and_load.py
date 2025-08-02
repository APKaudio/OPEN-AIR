# utils/utils_preset_query_and_load.py
#
# This module provides utility functions for querying available presets from the
# connected instrument and loading selected presets (both device and user-defined).
# It abstracts the low-level SCPI commands for preset management and integrates
# with the GUI's state to update settings.
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
# Version 20250802.1701.10 (Refactored from utils_preset.py to handle query and load logic.)

current_version = "20250802.1701.10" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 1701 * 10 # Example hash, adjust as needed

import pyvisa
import time
import inspect
import os
from datetime import datetime
import csv

# Updated imports for new logging functions
from src.debug_logic import debug_log, log_visa_command
from src.console_logic import console_log

# Import necessary functions from the new, specialized utility modules
from tabs.Instrument.utils_instrument_read_and_write import query_safe, write_safe
from tabs.Instrument.utils_instrument_query_settings import query_current_instrument_settings
from tabs.Presets.utils_preset_process import load_user_presets_from_csv # Import from the new processing file

# Constants for frequency conversion (needed by this module)
# Assuming MHZ_TO_HZ is now available via app_instance or a global constant
# from ref.frequency_bands import MHZ_TO_HZ # Removed as it should be accessed via app_instance.MHZ_TO_HZ

# Define constants
PRESETS_CSV_FILENAME = "PRESETS.CSV"
VBW_RBW_RATIO = 3 # Moved this to a module-level constant for better practice and to resolve potential syntax issues.

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
                file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                version=current_version,
                function=current_function)

    if not app_instance.inst:
        console_print_func("⚠️ Not connected to an instrument. Cannot query device presets.")
        debug_log("No instrument connected for querying device presets. Aborting.",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
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
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
            return presets
        else:
            console_print_func("ℹ️ No device presets found or empty response from instrument.")
            debug_log("Empty response for device presets query.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
            return []
    except Exception as e:
        console_print_func(f"❌ Error querying device presets: {e}. This is a disaster!")
        debug_log(f"Error querying device presets: {e}. Fucking hell!",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
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
                file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
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
            # Using the new query_current_instrument_settings from utils_instrument_query_settings
            center_freq_mhz, span_mhz, rbw_hz_queried = query_current_instrument_settings(
                app_instance.inst, app_instance.MHZ_TO_HZ, console_print_func
            )
            if center_freq_mhz is not None:
                center_freq_hz = center_freq_mhz * app_instance.MHZ_TO_HZ
                span_hz = span_mhz * app_instance.MHZ_TO_HZ
                rbw_hz = rbw_hz_queried
                console_print_func(f"✅ Device preset '{selected_preset_name}' loaded and GUI updated.")
                debug_log(f"Device preset '{selected_preset_name}' loaded. UI synced!",
                            file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                            version=current_version,
                            function=current_function)
            else:
                console_print_func(f"❌ Failed to query settings after loading device preset '{selected_preset_name}'.")
                debug_log(f"Failed to query settings after loading device preset '{selected_preset_name}'. What a pain!",
                            file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                            version=current_version,
                            function=current_function)
                return False, 0.0, 0.0, 0.0
        else:
            # Assume it's a user preset from CSV
            console_print_func(f"Attempting to load user preset: {selected_preset_name} from CSV.")
            user_presets = load_user_presets_from_csv(app_instance.CONFIG_FILE_PATH, console_print_func)
            found_preset = next((p for p in user_presets if p.get('NickName') == selected_preset_name), None)

            if found_preset:
                center_freq_hz = float(found_preset.get('Center', 0.0))
                span_hz = float(found_preset.get('Span', 0.0))
                rbw_hz = float(found_preset.get('RBW', 0.0))

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

            console_print_func(f"GUI settings updated from preset: Center Freq={center_freq_hz / app_instance.MHZ_TO_HZ:.3f} MHz, Span={span_hz / app_instance.MHZ_TO_HZ:.3f} MHz, RBW={rbw_hz:.0f} Hz. Looking good!")
            debug_log(f"GUI settings updated from loaded preset. Success!",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)

            return True, center_freq_hz, span_hz, rbw_hz

        console_print_func(f"❌ Failed to load preset '{selected_preset_name}'. This is frustrating!")
        debug_log(f"Failed to load preset '{selected_preset_name}'. What a pain!",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)
        return False, 0.0, 0.0, 0.0

    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred in load_selected_preset_logic: {e}. This is a disaster!")
        debug_log(f"An unexpected error occurred in load_selected_preset_logic: {e}. Fucking hell!",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)
        return False, 0.0, 0.0, 0.0
