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
# Version 20250821.094100.1
# REFACTORED: Refactored main save_config function to use modular save functions.

import os
import inspect
from configparser import ConfigParser
from display.debug_logic import debug_log
from display.console_logic import console_log

# Import the new modular save functions
from .config_manager_application import _save_application_settings
from .config_manager_debug import _save_debug_settings
from .config_manager_instruments import _save_instrument_settings, _save_amplifier_settings
from .config_manager_marker import _save_marker_tab_settings
from .config_manager_plotting import _save_plotting_settings
from .config_manager_report import _save_report_settings
from .config_manager_scan import _save_scan_info_settings

# --- Versioning ---
w = 20250821
x_str = '094100'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"

def load_config(file_path, console_print_func):
    """Loads settings from a specified config file."""
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🔧💾🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
    
    config = ConfigParser()
    if os.path.exists(file_path):
        console_print_func(f"🔧💾📂 Reading configuration from {os.path.basename(file_path)}")
        config.read(file_path)
        debug_log(message=f"🔧💾📂 Found and read config file: {file_path}", file=current_file, version=current_version, function=current_function)
    else:
        from src.settings_and_config.program_default_values import DEFAULT_CONFIG
        console_print_func(f"❌ Configuration file not found at {file_path}. The file has vanished! Restoring to defaults.")
        debug_log(message=f"🔧💾❌ Config file not found, creating from defaults.", file=current_file, version=current_version, function=current_function)
        config = ConfigParser()
        for section, values in DEFAULT_CONFIG.items():
            config.add_section(section)
            for key, value in values.items():
                config.set(section, key, str(value))
    debug_log(message=f"🔧💾🟢 Exiting {current_function}", file=current_file, version=current_version, function=current_function)
    return config

def save_config(config, file_path, console_print_func, app_instance):
    """
    Saves the application's current configuration to a file using modular functions.
    
    Args:
        config (ConfigParser): The config object to save.
        file_path (str): The path to the config file.
        console_print_func (function): The function to print to the GUI console.
        app_instance: The main application instance.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🔧💾🟢 Attempting to save configuration to {file_path} via modular approach.",
              file=current_file, version=current_version, function=current_function)

    try:
        # Create a new ConfigParser to avoid issues with in-memory changes
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

        with open(file_path, 'w') as configfile:
            new_config.write(configfile)
        
        console_print_func(f"🔧💾✅ Configuration successfully written to {os.path.basename(file_path)}. Mission accomplished!")
        debug_log(message=f"🔧💾✅ Configuration successfully written to {file_path}. Mission accomplished!",
                    file=current_file, version=current_version, function=current_function, special=True)
        
    except Exception as e:
        console_print_func(f"❌ Error saving configuration to {file_path}: {e}")
        debug_log(message=f"🔧💾❌ Failed to save configuration. Error: {e}",
                    file=current_file, version=current_version, function=current_function)