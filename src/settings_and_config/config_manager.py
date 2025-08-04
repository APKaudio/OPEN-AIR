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
# Version 20250803.233512.0 (ADDED: New function 'save_config_as_new_file' to resolve ImportError.)
# Version 20250803.233130.0 (FIXED: Corrected import name from DEFAULT_CONFIG_SETTINGS to DEFAULT_CONFIG.)
# Version 20250803.1115.0 (REFACTORED: Moved from root to subfolder. Updated imports.)
# Version 20250804.021740.0 (DEBUGGING: Added verbose logging in save_config for paned_window_sash_position.)
# Version 20250804.022000.0 (DEBUGGING: Added more granular checks for paned_window existence in save_config.)
# Version 20250804.022251.0 (FIXED: Explicitly saving selected bands from app_instance.band_vars.)

current_version = "20250804.022251.0" # Incremented version

import configparser
import os
import inspect
from datetime import datetime

# Local application imports
from src.debug_logic import debug_log
from src.console_logic import console_log

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
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        config.read_dict(DEFAULT_CONFIG)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, 'w') as configfile:
                config.write(configfile)
            console_print_func("✅ Default configuration file created successfully.")
            debug_log("Default config file created.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        except Exception as e:
            error_msg = f"❌ Error creating default config file: {e}. This is a problem!"
            console_print_func(error_msg)
            debug_log(error_msg,
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
    else:
        try:
            config.read(file_path)
            console_print_func(f"✅ Configuration loaded from '{file_path}'.")
            debug_log(f"Config loaded from: {file_path}",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        except configparser.Error as e:
            console_print_func(f"❌ Error reading config file: {e}. Starting with default settings.")
            debug_log(f"Config read error: {e}. Reverting to defaults.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            config = configparser.ConfigParser(interpolation=None)
            config.read_dict(DEFAULT_CONFIG)

    return config

def save_config(config, file_path, console_print_func, app_instance):
    """
    Saves the current application settings to the default config.ini file.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to save configuration to {file_path}. Initiating config dump!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    try:
        # Update specific non-variable settings
        app_geometry = app_instance.geometry()
        config.set('Application', 'geometry', app_geometry)
        debug_log(f"Config object: Set 'geometry' to '{app_geometry}'.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        config.set('Application', 'last_config_save_time', current_time)
        debug_log(f"Config object: Set 'last_config_save_time' to '{current_time}'.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        debug_log(f"Checking for 'paned_window' on app_instance (hasattr: {hasattr(app_instance, 'paned_window')}).",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        if hasattr(app_instance, 'paned_window'):
            debug_log(f"'paned_window' attribute exists. Is it None? ({app_instance.paned_window is None}). Type: {type(app_instance.paned_window)}",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            if app_instance.paned_window: # Ensure it's not None
                try:
                    sash_pos = app_instance.paned_window.sashpos(0)
                    config.set('Application', 'paned_window_sash_position', str(sash_pos))
                    debug_log(f"Config object: SUCCESSFULLY SET 'paned_window_sash_position' to '{sash_pos}'. This should be the correct value!",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function, special=True)
                except Exception as e:
                    debug_log(f"ERROR: Failed to get sash position or set it in config: {e}. What the hell is going on?!",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function, special=True)
            else:
                debug_log("Config object: 'app_instance.paned_window' is None. Skipping sash position save.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
        else:
            debug_log("Config object: 'app_instance.paned_window' attribute does NOT exist. Skipping sash position save.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

        # Update settings from the setting_var_map
        if hasattr(app_instance, 'setting_var_map'):
            for key, (var, section) in app_instance.setting_var_map.items():
                if not config.has_section(section):
                    config.add_section(section)
                # Removed the old special handling for band_vars here.
                # It will be handled by the explicit block below.
                if key != 'last_scan_configuration__selected_bands': # Skip if this key, handled separately
                    config_value = str(var.get())
                    config.set(section, key, config_value)
                    debug_log(f"Config object: Set '{section}/{key}' to '{config_value}'.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
        
        # --- NEW/FIXED: Explicitly save selected bands from app_instance.band_vars ---
        if hasattr(app_instance, 'band_vars') and app_instance.band_vars:
            selected_bands = [item["band"]["Band Name"] for item in app_instance.band_vars if item["var"].get()]
            selected_bands_str = ",".join(selected_bands)
            if not config.has_section('Scan'):
                config.add_section('Scan')
            config.set('Scan', 'last_scan_configuration__selected_bands', selected_bands_str)
            debug_log(f"Config object: Explicitly set 'Scan/last_scan_configuration__selected_bands' to '{selected_bands_str}'. Bands saved!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function, special=True)
        else:
            debug_log("Config object: 'app_instance.band_vars' not available or empty. Skipping band selection save.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

        # FINAL CHECK: What does the config object itself think is the sash position just before writing?
        final_sash_pos_in_config = config.get('Application', 'paned_window_sash_position', fallback='NOT SET IN CONFIG OBJECT')
        debug_log(f"Config object reports 'paned_window_sash_position' as '{final_sash_pos_in_config}' just before file write. Is this the right value? This better work!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function, special=True)

        with open(file_path, 'w') as configfile:
            config.write(configfile)
            
        console_print_func("✅ Configuration saved successfully. Persistence achieved!")
        debug_log(f"Configuration successfully written to {file_path}. Mission accomplished!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function, special=True)
        
    except Exception as e:
        error_message = f"❌ Failed to save configuration: {e}. This is a critical failure! Fucking hell!"
        console_print_func(error_message)
        debug_log(error_message,
                    file=f"{os.path.basename(__file__)} - {current_version}",
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
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function_name)
    
    try:
        # Populate settings from the app's setting_var_map
        if hasattr(app_instance, 'setting_var_map'):
            for key, (var, section) in app_instance.setting_var_map.items():
                if not new_config.has_section(section):
                    new_config.add_section(section)
                # Special handling for band_vars (for new file save)
                if key != 'last_scan_configuration__selected_bands': # Skip if this key, handled separately
                    new_config.set(section, key, str(var.get()))

        # Explicitly save selected bands from app_instance.band_vars for new file save
        if hasattr(app_instance, 'band_vars') and app_instance.band_vars:
            selected_bands = [item["band"]["Band Name"] for item in app_instance.band_vars if item["var"].get()]
            selected_bands_str = ",".join(selected_bands)
            if not new_config.has_section('Scan'):
                new_config.add_section('Scan')
            new_config.set('Scan', 'last_scan_configuration__selected_bands', selected_bands_str)

        # Update specific non-variable settings
        if not new_config.has_section('Application'):
            new_config.add_section('Application')
        new_config.set('Application', 'geometry', app_instance.geometry())
        new_config.set('Application', 'last_config_save_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        if hasattr(app_instance, 'paned_window') and app_instance.paned_window:
             sash_pos = app_instance.paned_window.sashpos(0)
             new_config.set('Application', 'paned_window_sash_position', str(sash_pos))

        # Write the new config object to the specified new file
        with open(new_file_path, 'w') as configfile:
            new_config.write(configfile)
        
        console_log(f"✅ Configuration saved successfully as '{os.path.basename(new_file_path)}'. New file created!")
        debug_log(f"New configuration file created: {new_file_path}.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function_name)

    except Exception as e:
        error_message = f"❌ Failed to save new configuration file: {e}. This is a problem!"
        console_log(error_message)
        debug_log(error_message,
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function_name)