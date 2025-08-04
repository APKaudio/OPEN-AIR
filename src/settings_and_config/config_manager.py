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

current_version = "20250803.233512.0"

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
    config = configparser.ConfigParser(interpolation=None)
    if not os.path.exists(file_path):
        console_print_func(f"Configuration file not found at '{file_path}'. Creating with default settings.")
        config.read_dict(DEFAULT_CONFIG)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as configfile:
            config.write(configfile)
    else:
        try:
            config.read(file_path)
        except configparser.Error as e:
            console_print_func(f"❌ Error reading config file: {e}. Starting with default settings.")
            config = configparser.ConfigParser(interpolation=None)
            config.read_dict(DEFAULT_CONFIG)

    return config

def save_config(config, file_path, console_print_func, app_instance):
    """
    Saves the current application settings to the default config.ini file.
    """
    try:
        # Update specific non-variable settings
        config.set('Application', 'geometry', app_instance.geometry())
        config.set('Application', 'last_config_save_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        if hasattr(app_instance, 'paned_window'):
             sash_pos = app_instance.paned_window.sashpos(0)
             config.set('Application', 'paned_window_sash_position', str(sash_pos))

        # Update settings from the setting_var_map
        if hasattr(app_instance, 'setting_var_map'):
            for key, (var, section) in app_instance.setting_var_map.items():
                if not config.has_section(section):
                    config.add_section(section)
                config.set(section, key, str(var.get()))

        with open(file_path, 'w') as configfile:
            config.write(configfile)
            
        console_print_func("✅ Configuration saved successfully.")
        
    except Exception as e:
        error_message = f"❌ Failed to save configuration: {e}"
        console_print_func(error_message)
        debug_log(error_message,
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=inspect.currentframe().f_code.co_name)

def save_config_as_new_file(app_instance, new_file_path):
    """
    Saves the current application settings to a NEW specified .ini file.
    This creates a snapshot of the current configuration.
    """
    new_config = configparser.ConfigParser(interpolation=None)
    current_function_name = inspect.currentframe().f_code.co_name
    
    try:
        # Populate settings from the app's setting_var_map
        if hasattr(app_instance, 'setting_var_map'):
            for key, (var, section) in app_instance.setting_var_map.items():
                if not new_config.has_section(section):
                    new_config.add_section(section)
                new_config.set(section, key, str(var.get()))

        # Update specific non-variable settings
        if not new_config.has_section('Application'):
            new_config.add_section('Application')
        new_config.set('Application', 'geometry', app_instance.geometry())
        new_config.set('Application', 'last_config_save_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        if hasattr(app_instance, 'paned_window'):
             sash_pos = app_instance.paned_window.sashpos(0)
             new_config.set('Application', 'paned_window_sash_position', str(sash_pos))

        # Write the new config object to the specified new file
        with open(new_file_path, 'w') as configfile:
            new_config.write(configfile)
        
        console_log(f"✅ Configuration saved successfully as '{os.path.basename(new_file_path)}'.")

    except Exception as e:
        error_message = f"❌ Failed to save new configuration file: {e}"
        console_log(error_message)
        debug_log(error_message,
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function_name)