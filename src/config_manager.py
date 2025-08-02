# src/config_manager.py
#
# This file contains functions for loading and saving application configuration
# settings to and from a `config.ini` file. It ensures that default settings
# are present and handles the persistence of user-modified settings.
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
# Version 20250802.0015.1 (Updated load_config to accept app_instance, and added save_config_as_new_file.)

current_version = "20250802.0015.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 15 * 1 # Example hash, adjust as needed

import configparser
import os
import tkinter as tk # Import tkinter for update_idletasks (still needed for Tkinter variable updates)
import inspect # Import inspect module for debug_log

# Updated imports for new logging functions
from src.debug_logic import set_debug_mode, set_log_visa_commands_mode, set_debug_to_terminal_mode, debug_log
from src.console_logic import console_log # Added for console_print_func


def load_config(config_obj, file_path, console_print_func, app_instance):
    """
    Function Description:
    Loads configuration settings from a specified INI file into a ConfigParser object
    and updates the corresponding Tkinter variables in the application instance.
    If the file does not exist, it initializes default settings.

    Inputs:
        config_obj (configparser.ConfigParser): The ConfigParser object to load settings into.
        file_path (str): The full path to the configuration file (e.g., 'config.ini').
        console_print_func (function): Function to print messages to the GUI console.
        app_instance (object): The main application instance, used to access Tkinter variables
                                and the setting_var_map.

    Process of this function:
        1. Prints debug messages.
        2. Sets default configuration values within the `config_obj`.
        3. Attempts to read the configuration file.
        4. If the file is not found, logs a warning and proceeds with defaults.
        5. Iterates through the `app_instance.setting_var_map` to:
           a. Retrieve the corresponding value from `config_obj` (last used or default).
           b. Convert the string value to the appropriate Python type (bool, int, float, str).
           c. Set the value of the associated Tkinter variable.
           d. Handles potential `ValueError` during type conversion.
        6. Special handling for band selection checkboxes, updating them based on loaded config.
        7. Prints success or error messages to the console.

    Outputs of this function:
        None. Modifies `config_obj` and `app_instance`'s Tkinter variables.

    (2025-07-30) Change: Added `app_instance` parameter to pass the main app object.
    (2025-07-30) Change: Updated `load_config` to use `app_instance.setting_var_map` for mapping
                         config values to Tkinter variables.
    (2025-07-31) Change: Added handling for `debug_to_terminal_var` and `paned_window_sash_position_var`.
    (2025-07-31) Change: Added band selection loading logic.
    (2025-08-01 1900.1) Change: No functional changes.
    (2025-08-01 1900.2) Change: No functional changes.
    (2025-08-01 2045.1) Change: Updated to use debug_log consistently.
    (2025-08-02 0015.1) Change: Updated version number.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Loading configuration from {file_path}. Let's get this config loaded!",
                file=__file__,
                version=current_version,
                function=current_function)

    # Set default configuration values
    config_obj['DEFAULT_SETTINGS'] = {
        'default_GLOBAL__debug_enabled': 'False',
        'default_GLOBAL__log_visa_commands_enabled': 'False',
        'default_GLOBAL__debug_to_Terminal': 'False', # NEW
        'default_GLOBAL__paned_window_sash_position': '700', # NEW
        'default_GLOBAL__window_geometry': '1400x780+100+100', # Default window size and position

        'default_instrument_connection__visa_resource': '',

        'default_scan_configuration__scan_name': 'New Scan',
        'default_scan_configuration__scan_directory': os.path.join(os.path.expanduser('~'), 'Documents', 'OPEN-AIR-Scans'), # Default to Documents
        'default_scan_configuration__num_scan_cycles': '1',
        'default_scan_configuration__rbw_step_size_hz': '10000',
        'default_scan_configuration__cycle_wait_time_seconds': '0.5',
        'default_scan_configuration__maxhold_time_seconds': '3',
        'default_scan_configuration__scan_rbw_hz': '10000',
        'default_scan_configuration__reference_level_dbm': '-40',
        'default_scan_configuration__freq_shift_hz': '0',
        'default_scan_configuration__maxhold_enabled': 'True',
        'default_scan_configuration__sensitivity': 'True', # Corresponds to high_sensitivity_var
        'default_scan_configuration__preamp_on': 'True',
        'default_scan_configuration__scan_rbw_segmentation': '1000000.0',
        'default_scan_configuration__default_focus_width': '10000.0',
        'default_scan_configuration__selected_bands': '[]', # Store as JSON string of list of band names

        'default_scan_meta_data__operator_name': 'Anthony Peter Kuzub',
        'default_scan_meta_data__contact': 'I@Like.audio',
        'default_scan_meta_data__name': 'My Venue', # Corresponds to venue_name_var
        'default_scan_meta_data__venue_postal_code': '', # NEW
        'default_scan_meta_data__address_field': '', # NEW
        'default_scan_meta_data__city': 'Whitby',
        'default_scan_meta_data__province': 'Ontario', # NEW
        'default_scan_meta_data__scanner_type': 'Unknown',
        'default_scan_meta_data__selected_antenna_type': '', # NEW
        'default_scan_meta_data__antenna_description': '', # NEW
        'default_scan_meta_data__antenna_use': '', # NEW
        'default_scan_meta_data__antenna_mount': '', # NEW
        'default_scan_meta_data__selected_amplifier_type': '', # NEW
        'default_scan_meta_data__antenna_amplifier': '', # NEW
        'default_scan_meta_data__amplifier_description': '', # NEW
        'default_scan_meta_data__amplifier_use': '', # NEW
        'default_scan_meta_data__notes': 'Enter any notes about the scan here.',

        'default_instrument_preset__selected_preset_name': '', # NEW
        'default_instrument_preset__loaded_preset_center_freq_mhz': '', # NEW
        'default_instrument_preset__loaded_preset_span_mhz': '', # NEW
        'default_instrument_preset__loaded_preset_rbw_hz': '', # NEW

        'default_plotting__scan_markers_to_plot__include_gov_markers': 'True',
        'default_plotting__scan_markers_to_plot__include_tv_markers': 'True',
        'default_plotting__scan_markers_to_plot__include_markers': 'True',
        'default_plotting__scan_markers_to_plot__include_intermod_markers': 'False', # NEW
        'default_plotting__scan_markers_to_plot__open_html_after_complete': 'True',
        'default_plotting__scan_markers_to_plot__create_html': 'True', # NEW

        'default_plotting__average_markers_to_plot__include_gov_markers': 'True', # NEW
        'default_plotting__average_markers_to_plot__include_tv_markers': 'True', # NEW
        'default_plotting__average_markers_to_plot__include_markers': 'True', # NEW
        'default_plotting__average_markers_to_plot__include_intermod_markers': 'False', # NEW
        'default_plotting__average_markers_to_plot__math_average': 'True',
        'default_plotting__average_markers_to_plot__math_median': 'True',
        'default_plotting__average_markers_to_plot__math_range': 'True',
        'default_plotting__average_markers_to_plot__math_standard_deviation': 'True',
        'default_plotting__average_markers_to_plot__math_variance': 'True',
        'default_plotting__average_markers_to_plot__math_psd': 'True',
    }

    # Ensure LAST_USED_SETTINGS section exists or create it
    if 'LAST_USED_SETTINGS' not in config_obj:
        config_obj['LAST_USED_SETTINGS'] = {}

    try:
        config_obj.read(file_path)
        console_print_func(f"✅ Configuration loaded from {file_path}. Ready to roll!")
        debug_log(f"Configuration loaded from {file_path}.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    except configparser.Error as e:
        console_print_func(f"❌ Error reading configuration file {file_path}: {e}. Using default settings. This is a mess!")
        debug_log(f"Error reading config file {file_path}: {e}. Using defaults.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    except FileNotFoundError:
        console_print_func(f"⚠️ Configuration file not found at {file_path}. Initializing with default settings. Where the hell did it go?!")
        debug_log(f"Config file not found at {file_path}. Initializing with defaults.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        # If file not found, config_obj is already populated with defaults.
        # Ensure the directory exists before attempting to save later.
        os.makedirs(os.path.dirname(file_path), exist_ok=True)


    # Apply loaded settings to Tkinter variables
    for tk_var_name, (last_key, default_key, tk_var_instance) in app_instance.setting_var_map.items():
        try:
            # Prioritize last used setting, fallback to default setting
            value_str = config_obj.get('LAST_USED_SETTINGS', last_key, fallback=config_obj.get('DEFAULT_SETTINGS', default_key))
            
            if isinstance(tk_var_instance, tk.BooleanVar):
                tk_var_instance.set(value_str.lower() == 'true')
            elif isinstance(tk_var_instance, tk.IntVar):
                tk_var_instance.set(int(float(value_str))) # Handle potential float strings
            elif isinstance(tk_var_instance, tk.DoubleVar):
                tk_var_instance.set(float(value_str))
            elif isinstance(tk_var_instance, tk.StringVar):
                tk_var_instance.set(value_str)
            
            debug_log(f"Loaded '{tk_var_name}' with value '{value_str}'. Variable updated!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except ValueError as e:
            console_print_func(f"❌ Error converting value for {tk_var_name} ('{value_str}'): {e}. Using default. This is a mess!")
            debug_log(f"Error converting value for {tk_var_name} ('{value_str}'): {e}. Using default.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            # Fallback to default if conversion fails
            default_value_str = config_obj.get('DEFAULT_SETTINGS', default_key)
            if isinstance(tk_var_instance, tk.BooleanVar):
                tk_var_instance.set(default_value_str.lower() == 'true')
            elif isinstance(tk_var_instance, tk.IntVar):
                tk_var_instance.set(int(float(default_value_str)))
            elif isinstance(tk_var_instance, tk.DoubleVar):
                tk_var_instance.set(float(default_value_str))
            elif isinstance(tk_var_instance, tk.StringVar):
                tk_var_instance.set(default_value_str)
        except Exception as e:
            console_print_func(f"❌ An unexpected error occurred loading {tk_var_name}: {e}. This is a disaster!")
            debug_log(f"Unexpected error loading {tk_var_name}: {e}. Fucking hell!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    # Special handling for band selections, which are stored as a JSON string
    try:
        selected_bands_str = config_obj.get('LAST_USED_SETTINGS', 'last_scan_configuration__selected_bands', fallback=config_obj.get('DEFAULT_SETTINGS', 'default_scan_configuration__selected_bands'))
        import json
        selected_bands_list = json.loads(selected_bands_str)
        for band_dict in app_instance.band_vars:
            band_name = band_dict["band"]["Band Name"]
            band_dict["var"].set(band_name in selected_bands_list)
        debug_log(f"Loaded selected bands: {selected_bands_list}. Bands updated!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    except Exception as e:
        console_print_func(f"❌ Error loading selected bands from config: {e}. This is a mess!")
        debug_log(f"Error loading selected bands: {e}. What a pain!",
                    file=__file__,
                    version=current_version,
                    function=current_function)


def save_config(config_obj, file_path, console_print_func, app_instance):
    """
    Function Description:
    Saves the current application settings from Tkinter variables to the ConfigParser object
    and then writes them to the configuration file.

    Inputs:
        config_obj (configparser.ConfigParser): The ConfigParser object to save settings from.
        file_path (str): The full path to the configuration file (e.g., 'config.ini').
        console_print_func (function): Function to print messages to the GUI console.
        app_instance (object): The main application instance, used to access Tkinter variables
                                and the setting_var_map.

    Process of this function:
        1. Prints debug messages.
        2. Ensures the 'LAST_USED_SETTINGS' section exists.
        3. Iterates through `app_instance.setting_var_map` to:
           a. Get the current value from each Tkinter variable.
           b. Convert it to a string.
           c. Store it in the 'LAST_USED_SETTINGS' section of `config_obj`.
        4. Special handling for band selection checkboxes, saving their state as a JSON string.
        5. Writes the `config_obj` to the specified file.
        6. Prints success or error messages.

    Outputs of this function:
        None. Modifies `config_obj` and writes to the configuration file.

    (2025-07-30) Change: Added `app_instance` parameter to pass the main app object.
    (2025-07-30) Change: Updated `save_config` to use `app_instance.setting_var_map` for mapping
                         Tkinter variables to config values.
    (2025-07-31) Change: Added handling for `debug_to_terminal_var` and `paned_window_sash_position_var`.
    (2025-07-31) Change: Added band selection saving logic.
    (2025-08-01 1900.1) Change: No functional changes.
    (2025-08-01 1900.2) Change: No functional changes.
    (2025-08-01 2045.1) Change: Updated to use debug_log consistently.
    (2025-08-02 0015.1) Change: Updated version number.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Saving configuration to {file_path}. Persisting changes!",
                file=__file__,
                version=current_version,
                function=current_function)

    if 'LAST_USED_SETTINGS' not in config_obj:
        config_obj['LAST_USED_SETTINGS'] = {}

    # Update config_obj from Tkinter variables
    for tk_var_name, (last_key, default_key, tk_var_instance) in app_instance.setting_var_map.items():
        try:
            value = tk_var_instance.get()
            config_obj.set('LAST_USED_SETTINGS', last_key, str(value))
            debug_log(f"Saved '{tk_var_name}' with value '{value}'. Data stored!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except Exception as e:
            console_print_func(f"❌ Error saving {tk_var_name} to config: {e}. This is a disaster!")
            debug_log(f"Error saving {tk_var_name}: {e}. Fucking hell!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    # Special handling for band selections
    try:
        import json
        selected_bands = [band_dict["band"]["Band Name"] for band_dict in app_instance.band_vars if band_dict["var"].get()]
        config_obj.set('LAST_USED_SETTINGS', 'last_scan_configuration__selected_bands', json.dumps(selected_bands))
        debug_log(f"Saved selected bands: {selected_bands}. Bands persisted!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    except Exception as e:
        console_print_func(f"❌ Error saving selected bands to config: {e}. This is a mess!")
        debug_log(f"Error saving selected bands: {e}. What a pain!",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True) # Ensure directory exists
        with open(file_path, 'w') as configfile:
            config_obj.write(configfile)
        console_print_func(f"✅ Configuration successfully saved to {file_path}. Done!")
        debug_log(f"Configuration successfully saved to {file_path}. Mission accomplished!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    except IOError as e:
        error_msg = f"❌ I/O Error saving configuration to {file_path}: {e}. This is a disaster!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=__file__,
                    version=current_version,
                    function=current_function)
        raise # Re-raise to be caught by the calling function
    except Exception as e:
        error_msg = f"❌ An unexpected error occurred while saving configuration to {file_path}: {e}. What a mess!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=__file__,
                    version=current_version,
                    function=current_function)
        raise # Re-raise to be caught by the calling function


def save_config_as_new_file(config_obj, file_path, console_print_func):
    """
    Function Description:
    Saves the current in-memory ConfigParser object to a new, user-specified file path.
    This function is intended for "Save As" functionality, not for routine saving.

    Inputs:
        config_obj (configparser.ConfigParser): The ConfigParser object to save.
        file_path (str): The full path to the new configuration file.
        console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
        1. Prints debug messages.
        2. Ensures the directory for the new file exists.
        3. Writes the `config_obj` to the specified new file.
        4. Prints success or error messages.

    Outputs of this function:
        None. Creates a new configuration file.

    (2025-08-02 0015.1) Change: New function for saving config to a new file.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to save configuration to new file: {file_path}. Creating a fresh copy!",
                file=__file__,
                version=current_version,
                function=current_function)
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True) # Ensure directory exists
        with open(file_path, 'w') as configfile:
            config_obj.write(configfile)
        console_print_func(f"✅ Configuration successfully saved to {file_path}. New file created!")
        debug_log(f"Configuration successfully saved to {file_path}. Mission accomplished!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    except IOError as e:
        error_msg = f"❌ I/O Error saving configuration to {file_path}: {e}. This is a disaster!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=__file__,
                    version=current_version,
                    function=current_function)
        raise # Re-raise to be caught by the calling function
    except Exception as e:
        error_msg = f"❌ An unexpected error occurred while saving configuration to {file_path}: {e}. What a mess!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=__file__,
                    version=current_version,
                    function=current_function)
        raise # Re-raise to be caught by the calling function

