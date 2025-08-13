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
# Version 20250812.165100.1 (FIXED: The load_config function now correctly handles empty or non-existent config files by defaulting to the internal configuration.)

current_version = "20250812.165100.1"
current_version_hash = (20250812 * 165100 * 1)

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
    Loads the configuration from the specified INI file. If the file doesn't exist
    or is empty, it creates it with default settings.
    """
    current_function = inspect.currentframe().f_code.co_name
    config = configparser.ConfigParser(interpolation=None)
    
    # Check if file doesn't exist OR if it exists but is empty
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        if not os.path.exists(file_path):
            console_print_func(f"Configuration file not found at '{file_path}'. Creating with default settings.")
            debug_log(f"Config file not found: {file_path}. Initializing with defaults.",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
        else: # File exists but is empty
            console_print_func(f"Configuration file at '{file_path}' is empty. Overwriting with default settings.")
            debug_log(f"Config file is empty: {file_path}. Overwriting with defaults.",
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
        'window_state',
        'last_config_save_time',
        'paned_window_sash_position_percentage',
        'last_scan_configuration__selected_bands',
        'last_scan_configuration__selected_bands_levels',
    ]

    try:
        # --- Explicitly handle geometry and window_state ---
        app_geometry = app_instance.geometry()
        config.set('Application', 'geometry', app_geometry)
        debug_log(f"Config object: Set 'geometry' to '{app_geometry}'.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        window_state = 'zoomed' if app_instance.state() == 'zoomed' else 'normal'
        config.set('Application', 'window_state', window_state)
        debug_log(f"Config object: Set 'window_state' to '{window_state}'.",
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

        # --- Explicitly handle paned_window_sash_position_percentage ---
        if hasattr(app_instance, 'paned_window') and app_instance.paned_window and app_instance.winfo_width() > 0:
            try:
                sash_pos = app_instance.paned_window.sashpos(0)
                # Calculate percentage and convert to string for config file
                sash_pos_percentage = int((sash_pos / app_instance.winfo_width()) * 100)
                config.set('Application', 'paned_window_sash_position_percentage', str(sash_pos_percentage))
                debug_log(f"Config object: SUCCESSFULLY SET 'paned_window_sash_position_percentage' to '{sash_pos_percentage}%' from pixel value '{sash_pos}'. This is a goddamn good idea!",
                            file=os.path.basename(__file__),
                            version=current_version,
                            function=current_function, special=True)
            except Exception as e:
                debug_log(f"ERROR: Failed to get sash position or set it in config: {e}. What the hell is going on?!",
                            file=os.path.basename(__file__),
                            version=current_version,
                            function=current_function, special=True)
        else:
            debug_log("Config object: 'app_instance.paned_window' attribute does NOT exist, or window width is zero. Skipping sash position percentage save.",
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

        final_sash_pos_in_config = config.get('Application', 'paned_window_sash_position_percentage', fallback=50)
        debug_log(f"Config object reports 'paned_window_sash_position_percentage' as '{final_sash_pos_in_config}' just before file write. Is this the right value? This better work!",
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
        'window_state',
        'last_config_save_time',
        'paned_window_sash_position_percentage',
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
        new_config.set('Application', 'window_state', 'zoomed' if app_instance.state() == 'zoomed' else 'normal')
        new_config.set('Application', 'last_config_save_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # FIXED: Calculate and save sash position as a percentage
        if hasattr(app_instance, 'paned_window') and app_instance.paned_window and app_instance.winfo_width() > 0:
            sash_pos = app_instance.paned_window.sashpos(0)
            sash_pos_percentage = int((sash_pos / app_instance.winfo_width()) * 100)
            new_config.set('Application', 'paned_window_sash_position_percentage', str(sash_pos_percentage))
        
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
