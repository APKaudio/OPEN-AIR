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
# Version 20250802.0010.1 (Refactored debug_print to use debug_log and console_log; added flair.)

current_version = "20250802.0010.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 10 * 1 # Example hash, adjust as needed

import configparser
import os
import tkinter as tk # Import tkinter for update_idletasks (still needed for Tkinter variable updates)
import inspect # Import inspect module for debug_log

# Updated imports for new logging functions
from src.debug_logic import set_debug_mode, set_log_visa_commands_mode, set_debug_to_terminal_mode, debug_log
from src.console_logic import console_log

# NEW: Import default settings structure
from ref.default_settings import DEFAULT_SETTINGS_STRUCTURE

def load_config(config_file_path, app_instance, console_print_func=None):
    """
    Function Description:
    Loads application configuration from `config.ini`. If the file does not exist,
    it creates it with default settings. It also ensures that all expected sections
    and keys from `DEFAULT_SETTINGS_STRUCTURE` are present, adding missing ones.

    Inputs:
    - config_file_path (str): The path to the configuration file (e.g., 'config.ini').
    - app_instance (object): Reference to the main application instance, used to access
                             its `config` object and Tkinter variables.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Initializes a `ConfigParser` object.
    2. Checks if `config_file_path` exists.
    3. If it exists, reads the configuration from the file.
    4. If it does not exist or if `force_defaults` is True, it populates the `ConfigParser`
       with values from `DEFAULT_SETTINGS_STRUCTURE`.
    5. Iterates through `DEFAULT_SETTINGS_STRUCTURE` to ensure all default sections and keys
       are present in the loaded configuration, adding any missing ones.
    6. Saves the (potentially updated) configuration back to the file.
    7. Populates Tkinter variables in `app_instance` from the loaded configuration.

    Outputs of this function:
    - configparser.ConfigParser: The loaded and validated configuration object.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to load configuration from {config_file_path}. Let's get our settings in order!",
                file=__file__,
                version=current_version,
                function=current_function)

    config = configparser.ConfigParser()
    config_exists = os.path.exists(config_file_path)

    if config_exists:
        try:
            config.read(config_file_path)
            console_print_func(f"✅ Configuration loaded from {config_file_path}.")
            debug_log(f"Successfully read existing config file: {config_file_path}. Found it!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except configparser.Error as e:
            error_msg = f"❌ Error reading config file {config_file_path}: {e}. Corrupted file?"
            console_print_func(error_msg)
            debug_log(error_msg,
                        file=__file__,
                        version=current_version,
                        function=current_function)
            # Fallback to defaults if file is corrupted
            config = configparser.ConfigParser()
            config_exists = False # Treat as if file didn't exist to force defaults
    
    if not config_exists:
        console_print_func("ℹ️ config.ini not found or corrupted. Creating with default settings.")
        debug_log("Config file not found or corrupted. Creating with defaults. Starting fresh!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        
        # Populate with default settings structure
        for section, keys in DEFAULT_SETTINGS_STRUCTURE.items():
            if section not in config:
                config[section] = {}
            for key, default_value in keys.items():
                config[section][key] = str(default_value) # Ensure all values are strings

        # Ensure LAST_USED_SETTINGS are also populated with defaults on first creation
        if 'LAST_USED_SETTINGS' not in config:
            config['LAST_USED_SETTINGS'] = {}
        for key, default_value in DEFAULT_SETTINGS_STRUCTURE.get('DEFAULT_SETTINGS', {}).items():
            if key not in config['LAST_USED_SETTINGS']:
                config['LAST_USED_SETTINGS'][key] = str(default_value)
        
        console_print_func("✅ Default configuration created.")
        debug_log("Default configuration created and populated. Ready to roll!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    # Ensure all default settings are present in the loaded config (for updates)
    for section, keys in DEFAULT_SETTINGS_STRUCTURE.items():
        if section not in config:
            config[section] = {}
            debug_log(f"Added missing section: [{section}] to config.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        for key, default_value in keys.items():
            if key not in config[section]:
                config[section][key] = str(default_value)
                debug_log(f"Added missing key '{key}' to section [{section}] with default value '{default_value}'.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
    
    # Save the config back to ensure any newly added defaults are written
    save_config(config, config_file_path, console_print_func, app_instance) # Pass app_instance for saving Tkinter vars

    # Populate Tkinter variables from the loaded config
    # This must happen AFTER config is loaded/created and potentially updated
    if app_instance:
        debug_log("Populating Tkinter variables from config...",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        for tk_var_name, (last_key, default_key, tk_var_instance) in app_instance.setting_var_map.items():
            try:
                # Prioritize LAST_USED_SETTINGS, fallback to DEFAULT_SETTINGS
                value_str = config.get('LAST_USED_SETTINGS', last_key, fallback=None)
                if value_str is None and default_key:
                    value_str = config.get('DEFAULT_SETTINGS', default_key, fallback=None)

                if value_str is not None:
                    # Convert to appropriate type based on Tkinter variable type
                    if isinstance(tk_var_instance, tk.BooleanVar):
                        value = value_str.lower() == 'true'
                    elif isinstance(tk_var_instance, tk.IntVar):
                        value = int(float(value_str)) # Handle floats stored as ints
                    elif isinstance(tk_var_instance, tk.DoubleVar):
                        value = float(value_str)
                    else: # tk.StringVar
                        value = value_str
                    tk_var_instance.set(value)
                    debug_log(f"Set Tkinter var '{tk_var_name}' to '{value}'.",
                                file=__file__,
                                version=current_version,
                                function=current_function)
                else:
                    debug_log(f"No value found for Tkinter var '{tk_var_name}' in config. Skipping.",
                                file=__file__,
                                version=current_version,
                                function=current_function)
            except ValueError as e:
                error_msg = f"❌ Error converting config value for '{tk_var_name}': {value_str} - {e}. Data type mismatch!"
                console_print_func(error_msg)
                debug_log(error_msg,
                            file=__file__,
                            version=current_version,
                            function=current_function)
            except Exception as e:
                error_msg = f"❌ An unexpected error occurred setting Tkinter var '{tk_var_name}': {e}. This is a problem!"
                console_print_func(error_msg)
                debug_log(error_msg,
                            file=__file__,
                            version=current_version,
                            function=current_function)
        
        # Special handling for notes_var and band_vars as they are not in setting_var_map
        # Notes
        notes_from_config = config.get('LAST_USED_SETTINGS', 'notes', fallback='')
        app_instance.notes_var.set(notes_from_config)
        debug_log(f"Loaded notes: '{notes_from_config}'",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Selected Bands
        last_selected_bands_str = config.get('LAST_USED_SETTINGS', 'last_scan_configuration__selected_bands', fallback='')
        last_selected_band_names = [name.strip() for name in last_selected_bands_str.split(',') if name.strip()]
        for band_item in app_instance.band_vars:
            band_name = band_item["band"]["Band Name"]
            band_item["var"].set(band_name in last_selected_band_names)
        debug_log(f"Loaded selected bands: {last_selected_band_names}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Antenna Type
        selected_antenna_type = config.get('LAST_USED_SETTINGS', 'antenna_type', fallback='')
        app_instance.selected_antenna_type_var.set(selected_antenna_type)
        debug_log(f"Loaded antenna type: '{selected_antenna_type}'",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Antenna Amplifier Type
        selected_amplifier_type = config.get('LAST_USED_SETTINGS', 'antenna_amplifier_type', fallback='')
        app_instance.selected_amplifier_type_var.set(selected_amplifier_type)
        debug_log(f"Loaded amplifier type: '{selected_amplifier_type}'",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Output Folder
        output_folder = config.get('LAST_USED_SETTINGS', 'output_folder', fallback=os.path.join(os.getcwd(), 'scan_data'))
        app_instance.output_folder_var.set(output_folder)
        debug_log(f"Loaded output folder: '{output_folder}'",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Scan Name
        scan_name = config.get('LAST_USED_SETTINGS', 'scan_name', fallback='New Scan')
        app_instance.scan_name_var.set(scan_name)
        debug_log(f"Loaded scan name: '{scan_name}'",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        console_print_func("✅ All Tkinter variables updated from configuration.")
        debug_log("All Tkinter variables populated from config. UI should be in sync!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    return config


def save_config(config_obj, config_file_path, console_print_func=None, app_instance=None):
    """
    Function Description:
    Saves the current application configuration to the `config.ini` file.
    It updates the `LAST_USED_SETTINGS` section with the current values from
    the Tkinter variables in `app_instance` before writing the file.

    Inputs:
    - config_obj (configparser.ConfigParser): The configuration object to save.
    - config_file_path (str): The path to the configuration file.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.
    - app_instance (object, optional): Reference to the main application instance,
                                       used to retrieve current Tkinter variable values.

    Process of this function:
    1. Prints a debug message.
    2. If `app_instance` is provided, it iterates through `app_instance.setting_var_map`
       and updates the `LAST_USED_SETTINGS` section of `config_obj` with the current
       values from the Tkinter variables.
    3. Handles special cases like `notes_var`, `band_vars`, `selected_antenna_type_var`,
       `selected_amplifier_type_var`, `output_folder_var`, and `scan_name_var`
       to ensure they are also saved.
    4. Writes the `config_obj` to the specified `config_file_path`.
    5. Logs success or failure.

    Outputs of this function:
    - None. Saves the configuration to a file.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to save configuration to {config_file_path}. Preserving settings!",
                file=__file__,
                version=current_version,
                function=current_function)

    if app_instance:
        # Ensure LAST_USED_SETTINGS section exists
        if 'LAST_USED_SETTINGS' not in config_obj:
            config_obj['LAST_USED_SETTINGS'] = {}
            debug_log("Created missing 'LAST_USED_SETTINGS' section.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Update LAST_USED_SETTINGS from Tkinter variables
        for tk_var_name, (last_key, default_key, tk_var_instance) in app_instance.setting_var_map.items():
            try:
                config_obj['LAST_USED_SETTINGS'][last_key] = str(tk_var_instance.get())
                debug_log(f"Saved '{tk_var_name}' to config as '{last_key}': '{tk_var_instance.get()}'.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            except Exception as e:
                error_msg = f"❌ Error saving Tkinter var '{tk_var_name}' to config: {e}. This is a problem!"
                console_print_func(error_msg)
                debug_log(error_msg,
                            file=__file__,
                            version=current_version,
                            function=current_function)

        # Special handling for notes_var and band_vars (not in setting_var_map)
        config_obj['LAST_USED_SETTINGS']['notes'] = app_instance.notes_var.get()
        debug_log(f"Saved notes: '{app_instance.notes_var.get()}'",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Save selected bands
        selected_band_names = [band_item["band"]["Band Name"] for band_item in app_instance.band_vars if band_item["var"].get()]
        config_obj['LAST_USED_SETTINGS']['last_scan_configuration__selected_bands'] = ",".join(selected_band_names)
        debug_log(f"Saved selected bands: {selected_band_names}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Save Antenna Type
        config_obj['LAST_USED_SETTINGS']['antenna_type'] = app_instance.selected_antenna_type_var.get()
        debug_log(f"Saved antenna type: '{app_instance.selected_antenna_type_var.get()}'",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Save Antenna Amplifier Type
        config_obj['LAST_USED_SETTINGS']['antenna_amplifier_type'] = app_instance.selected_amplifier_type_var.get()
        debug_log(f"Saved amplifier type: '{app_instance.selected_amplifier_type_var.get()}'",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Save Output Folder
        config_obj['LAST_USED_SETTINGS']['output_folder'] = app_instance.output_folder_var.get()
        debug_log(f"Saved output folder: '{app_instance.output_folder_var.get()}'",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Save Scan Name
        config_obj['LAST_USED_SETTINGS']['scan_name'] = app_instance.scan_name_var.get()
        debug_log(f"Saved scan name: '{app_instance.scan_name_var.get()}'",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        debug_log("Updated 'LAST_USED_SETTINGS' from app_instance variables. Ready to write!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    try:
        with open(config_file_path, 'w') as configfile:
            config_obj.write(configfile)
        console_print_func(f"✅ Configuration saved to: {config_file_path}. Success!")
        debug_log(f"Configuration successfully saved to {config_file_path}. Mission accomplished!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    except IOError as e:
        error_msg = f"❌ I/O Error saving configuration to {config_file_path}: {e}. This is a disaster!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=__file__,
                    version=current_version,
                    function=current_function)
        raise # Re-raise to be caught by the calling function
    except Exception as e:
        error_msg = f"❌ An unexpected error occurred while saving configuration to {config_file_path}: {e}. What a mess!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=__file__,
                    version=current_version,
                    function=current_function)
        raise # Re-raise to be caught by the calling function


def save_config_as_new_file(config_obj, file_path, console_print_func=None):
    """
    Function Description:
    Saves the provided configuration object to a new file at the specified path.
    This function is used when the user explicitly wants to save the current
    configuration to a different file, rather than just updating the default `config.ini`.

    Inputs:
    - config_obj (configparser.ConfigParser): The configuration object to save.
    - file_path (str): The full path to the new configuration file.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Prints a debug message.
    2. Attempts to write the `config_obj` to the `file_path`.
    3. Handles and logs any `IOError` or general `Exception`.

    Outputs of this function:
    - None. Saves the configuration to a new file.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to save configuration to new file: {file_path}. Creating a fresh copy!",
                file=__file__,
                version=current_version,
                function=current_function)
    try:
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
