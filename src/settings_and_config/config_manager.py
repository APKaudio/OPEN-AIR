# src/settings_and_config/config_manager.py
#
# This file handles loading and saving application settings to the 'config.ini' file.
# It uses the configparser library to manage the configuration data, ensuring that
# user settings are preserved between sessions.
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
# Version 20250810.220100.20 (FIXED: The save_config function now removes the trailing decimal from integer-like float values for cleaner config files.)

current_version = "20250810.220100.20"
current_version_hash = 20250810 * 220100 * 20 # Example hash, adjust as needed

import configparser
import os
import inspect
from datetime import datetime

# Local application imports
from display.debug_logic import debug_log
from display.console_logic import console_log

# Use the correct variable name 'DEFAULT_CONFIG'
from src.program_default_values import DEFAULT_CONFIG


def load_config(file_path, console_print_func):
    """
    Loads the configuration from the specified INI file. If the file doesn't exist,
    it creates it with default settings.
    """
    current_function = inspect.currentframe().f_code.co_name
    config = configparser.ConfigParser(interpolation=None)
    if not os.path.exists(file_path):
        console_print_func(f"Configuration file not found at '{file_path}'. Creating with default settings.")
        debug_log(f"Config file not found: {file_path}. Initializing with defaults.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        config.read_dict(DEFAULT_CONFIG)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, 'w') as configfile:
                config.write(configfile)
            console_print_func("✅ Default configuration file created successfully.")
            debug_log("Default config file created.",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
        except Exception as e:
            error_msg = f"❌ Error creating default config file: {e}. This is a problem!"
            console_print_func(error_msg)
            debug_log(error_msg,
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
    else:
        try:
            config.read(file_path)
            console_print_func(f"✅ Configuration loaded from '{file_path}'.")
            debug_log(f"Config loaded from: {file_path}",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
        except configparser.Error as e:
            console_print_func(f"❌ Error reading config file: {e}. Starting with default settings.")
            debug_log(f"Config read error: {e}. Reverting to defaults.",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            config.read_dict(DEFAULT_CONFIG)

    return config

def save_config(config, file_path, console_print_func, app_instance):
    """
    Saves the current application settings to the default config.ini file.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to save configuration to {file_path}. Initiating config dump!",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)

    # List of keys that are handled explicitly (not via setting_var_map iteration)
    EXPLICITLY_HANDLED_KEYS = [
        'geometry',
        'last_config_save_time',
        'paned_window_sash_position',
        'last_scan_configuration__selected_bands',
        'last_scan_configuration__selected_bands_levels',
    ]

    try:
        # --- Explicitly handle geometry and last_config_save_time ---
        app_geometry = app_instance.geometry()
        config.set('Application', 'geometry', app_geometry)
        debug_log(f"Config object: Set 'geometry' to '{app_geometry}'.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        config.set('Application', 'last_config_save_time', current_time)
        debug_log(f"Config object: Set 'last_config_save_time' to '{current_time}'.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        if hasattr(app_instance, 'last_config_save_time_var'):
            app_instance.last_config_save_time_var.set(current_time)

        # --- Explicitly handle paned_window_sash_position ---
        if hasattr(app_instance, 'paned_window') and app_instance.paned_window:
            try:
                sash_pos = app_instance.paned_window.sashpos(0)
                config.set('Application', 'paned_window_sash_position', str(sash_pos))
                debug_log(f"Config object: SUCCESSFULLY SET 'paned_window_sash_position' to '{sash_pos}'. This should be the correct value!",
                            file=os.path.basename(__file__),
                            version=current_version,
                            function=current_function, special=True)
            except Exception as e:
                debug_log(f"ERROR: Failed to get sash position or set it in config: {e}. What the hell is going on?!",
                            file=os.path.basename(__file__),
                            version=current_version,
                            function=current_function, special=True)
        else:
            debug_log("Config object: 'app_instance.paned_window' attribute does NOT exist. Skipping sash position save.",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)

        # --- Update settings from the setting_var_map ---
        if hasattr(app_instance, 'setting_var_map'):
            for key, var_info in app_instance.setting_var_map.items():
                if key in EXPLICITLY_HANDLED_KEYS:
                    debug_log(f"Skipping setting '{var_info['section']}/{key}' from setting_var_map as it's handled explicitly.",
                                file=os.path.basename(__file__),
                                version=current_version,
                                function=current_function)
                    continue

                if not config.has_section(var_info['section']):
                    config.add_section(var_info['section'])
                
                # NEW LOGIC: Check if the value is a float that is a whole number.
                # If so, save it as an integer string to remove the decimal point.
                value_to_save = var_info['var'].get()
                if isinstance(value_to_save, float) and value_to_save.is_integer():
                    config_value = str(int(value_to_save))
                else:
                    config_value = str(value_to_save)
                
                config.set(var_info['section'], key, config_value)
                debug_log(f"Config object: Set '{var_info['section']}/{key}' to '{config_value}'.",
                            file=os.path.basename(__file__),
                            version=current_version,
                            function=current_function)
        
        # --- Explicitly save selected bands from app_instance.band_vars ---
        if hasattr(app_instance, 'band_vars') and app_instance.band_vars:
            selected_bands_with_levels = [
                f"{item['band']['Band Name']}={item.get('level', 0)}" for item in app_instance.band_vars
            ]
            selected_bands_str = ",".join(selected_bands_with_levels)
            
            if not config.has_section('Scan'):
                config.add_section('Scan')
            config.set('Scan', 'last_scan_configuration__selected_bands_levels', selected_bands_str)
            debug_log(f"Config object: Explicitly set 'Scan/last_scan_configuration__selected_bands_levels' to '{selected_bands_str}'. Bands with levels saved!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function, special=True)
        else:
            debug_log("Config object: 'app_instance.band_vars' not available or empty. Skipping band selection save.",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)

        final_sash_pos_in_config = config.get('Application', 'paned_window_sash_position', fallback='NOT SET IN CONFIG OBJECT')
        debug_log(f"Config object reports 'paned_window_sash_position' as '{final_sash_pos_in_config}' just before file write. Is this the right value? This better work!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function, special=True)

        with open(file_path, 'w') as configfile:
            config.write(configfile)
            
        console_print_func("✅ Configuration saved successfully. Persistence achieved!")
        debug_log(f"Configuration successfully written to {file_path}. Mission accomplished!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function, special=True)
        
    except Exception as e:
        error_message = f"❌ Failed to save configuration: {e}. This is a critical failure! Fucking hell!"
        console_print_func(error_message)
        debug_log(error_message,
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)


def save_config_as_new_file(app_instance, new_file_path):
    """
    Saves the current application settings to a NEW specified .ini file.
    This creates a snapshot of the current configuration.
    """
    new_config = configparser.ConfigParser(interpolation=None)
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to save configuration as new file to {new_file_path}. Creating snapshot!",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function_name)
    
    # List of keys that are handled explicitly (not via setting_var_map iteration)
    EXPLICITLY_HANDLED_KEYS_FOR_NEW_FILE = [
        'geometry',
        'last_config_save_time',
        'paned_window_sash_position',
        'last_scan_configuration__selected_bands',
        'last_scan_configuration__selected_bands_levels',
    ]

    try:
        # Populate settings from the app's setting_var_map
        if hasattr(app_instance, 'setting_var_map'):
            for key, var_info in app_instance.setting_var_map.items():
                if key in EXPLICITLY_HANDLED_KEYS_FOR_NEW_FILE:
                    continue
                
                if not new_config.has_section(var_info['section']):
                    new_config.add_section(var_info['section'])
                new_config.set(var_info['section'], key, str(var_info['var'].get()))


        # Explicitly handle non-variable based values for the new config file
        if not new_config.has_section('Application'):
            new_config.add_section('Application')
        new_config.set('Application', 'geometry', app_instance.geometry())
        new_config.set('Application', 'last_config_save_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        if hasattr(app_instance, 'paned_window') and app_instance.paned_window:
             sash_pos = app_instance.paned_window.sashpos(0)
             new_config.set('Application', 'paned_window_sash_position', str(sash_pos))
        
        # Explicitly save selected bands from app_instance.band_vars for new file save
        if hasattr(app_instance, 'band_vars') and app_instance.band_vars:
            selected_bands_with_levels = [
                f"{item['band']['Band Name']}={item.get('level', 0)}" for item in app_instance.band_vars
            ]
            selected_bands_str = ",".join(selected_bands_with_levels)
            if not new_config.has_section('Scan'):
                new_config.add_section('Scan')
            new_config.set('Scan', 'last_scan_configuration__selected_bands_levels', selected_bands_str)

        # Write the new config object to the specified new file
        with open(new_file_path, 'w') as configfile:
            new_config.write(configfile)
        
        console_log(f"✅ Configuration saved successfully as '{os.path.basename(new_file_path)}'. New file created!")
        debug_log(f"New configuration file created: {new_file_path}.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function_name)

    except Exception as e:
        error_message = f"❌ Failed to save new configuration file: {e}. This is a problem!"
        console_log(error_message)
        debug_log(error_message,
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function_name)
