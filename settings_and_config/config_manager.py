# src/settings_and_config/config_manager.py
#
# This file handles loading and saving application settings to the 'config.ini' file.
# It has been refactored to serve as a central orchestrator, importing and calling
# modular functions for each configuration section to improve maintainability.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250821.112000.1
# REFACTORED: Refactored main save_config function to use modular save functions.
# FIXED: The load_config function now correctly creates missing sections and defaults,
#        preventing a truncated config file from being saved.
# FIXED: Corrected the load_config function signature to accept the `config_file_path`
#        keyword argument, which resolves the TypeError.

import os
import inspect
from configparser import ConfigParser
from display.debug_logic import debug_log
from display.console_logic import console_log

# Import the new modular save functions
from .config_manager_application import _save_application_settings
from .config_manager_debug import _save_debug_settings
from .config_manager_instruments import _save_instrument_settings, _save_amplifier_settings, _save_antenna_settings
from .config_manager_marker import _save_marker_tab_settings
from .config_manager_plotting import _save_plotting_settings
from .config_manager_report import _save_report_settings
from .config_manager_scan import _save_scan_info_settings
from .program_default_values import DEFAULT_CONFIG, CONFIG_FILE_PATH, DATA_FOLDER_PATH


# --- Versioning ---
w = 20250821
x_str = '112000'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"{w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"


def load_config(default_config, config_file_path):
    """
    Loads the configuration from a file, creating it with default values if it doesn't exist.
    It will also check for and add any missing keys from the default config.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"⚙️🟢 Entering {current_function} to load configuration.",
              file=current_file, version=current_version, function=current_function)

    config = ConfigParser()
    
    # Check if config file exists
    if os.path.exists(config_file_path):
        debug_log(message=f"⚙️📂 Found config file at {config_file_path}. Reading...",
                  file=current_file, version=current_version, function=current_function)
        try:
            config.read(config_file_path)
        except Exception as e:
            console_log(f"❌ Error reading config file: {e}. A new one will be created.")
            debug_log(message=f"❌ Failed to read config file: {e}. Creating a new one from defaults.",
                      file=current_file, version=current_version, function=current_function)
            config = ConfigParser()

    # Merge with default configuration to ensure all keys exist
    for section, defaults in default_config.items():
        if not config.has_section(section):
            config.add_section(section)
            debug_log(message=f"⚙️📦 Adding missing section: [{section}].",
                      file=current_file, version=current_version, function=current_function)
        
        for key, value in defaults.items():
            if not config.has_option(section, key):
                config.set(section, key, str(value))
                debug_log(message=f"⚙️📝 Adding missing key '{key}' to section [{section}] with default value.",
                          file=current_file, version=current_version, function=current_function)

    # Save the merged config back to ensure it's complete
    try:
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)
        console_log(f"✅ Configuration loaded and saved to: {os.path.basename(config_file_path)}")
        debug_log(message=f"⚙️✅ Configuration file loaded and updated with all default values. All systems are go!",
                  file=current_file, version=current_version, function=current_function)
    except Exception as e:
        console_log(f"❌ Fatal Error: Could not write to config file: {e}. Check file permissions.")
        debug_log(message=f"❌ Fatal Error: Failed to write config file after merging: {e}",
                  file=current_file, version=current_version, function=current_function)
        # We can't continue if we can't save the config, so we exit.
        raise

    debug_log(message=f"⚙️✅ Exiting {current_function}. Configuration fully loaded.",
              file=current_file, version=current_version, function=current_function)

    return config, CONFIG_FILE_PATH, DATA_FOLDER_PATH


def save_config(config, file_path, console_print_func, app_instance):
    """
    Saves the application's configuration to a file. This is the main orchestrating
    function that calls each modular save function to update the config object.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🔧💾🟢 Entering {current_function} to save configuration.",
                file=current_file, version=current_version, function=current_function)
    
    try:
        # Before saving, reload the file to ensure we don't overwrite manual changes
        # Then we'll merge our in-memory changes
        new_config = ConfigParser()
        new_config.read(file_path)

        # Call each modular save function
        _save_application_settings(new_config, app_instance, console_print_func)
        _save_debug_settings(new_config, app_instance, console_print_func)
        _save_instrument_settings(new_config, app_instance, console_print_func)
        _save_marker_tab_settings(new_config, app_instance, console_print_func)
        _save_scan_info_settings(new_config, app_instance, console_print_func)
        _save_plotting_settings(new_config, app_instance, console_print_func)
        _save_report_settings(new_config, app_instance, console_print_func)
        _save_amplifier_settings(new_config, app_instance, console_print_func)
        _save_antenna_settings(new_config, app_instance, console_print_func)

        with open(file_path, 'w') as configfile:
            new_config.write(configfile)
        
        console_print_func(f"🔧💾✅ Configuration successfully written to {os.path.basename(file_path)}. Mission accomplished!")
        debug_log(message=f"🔧💾✅ Configuration successfully written to {file_path}. Mission accomplished!",
                    file=current_file, version=current_version, function=current_function, special=True)
        
    except Exception as e:
        console_print_func(f"❌ Error saving configuration to {file_path}: {e}")
        debug_log(message=f"❌🔴 Arrr, the config file be un-writable! Error: {e}",
                    file=current_file, version=current_version, function=current_function, special=True)
        
    debug_log(message=f"🔧💾✅ Exiting {current_function}",
              file=current_file, version=current_version, function=current_function)