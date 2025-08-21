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
# Version 20250821.143200.2
# FIXED: The load_config function now correctly ensures the directory exists before
#        attempting to write the config file, resolving the FileNotFoundError.
# UPDATED: The load_config function now returns only the config object.

import os
import inspect
from configparser import ConfigParser
from display.debug_logic import debug_log
from display.console_logic import console_log

# Import the new modular save functions
from .config_manager_application import _save_application_settings
from .config_manager_debug import _save_debug_settings
from .config_manager_instruments import _save_instrument_settings
from .config_manager_marker import _save_marker_tab_settings
from .config_manager_scan import _save_scan_info_settings
from .config_manager_plotting import _save_plotting_settings
from .config_manager_report import _save_report_settings
from .config_manager_instruments import _save_amplifier_settings, _save_antenna_settings
from ref.ref_file_paths import DATA_FOLDER_PATH, CONFIG_FILE_PATH # ADDED IMPORT

# --- Version Information ---
w = 20250821
x_str = '143200'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 2
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"

def load_config(default_config, file_path=CONFIG_FILE_PATH):
    """
    Loads the configuration from the config file. If the file does not exist,
    or if sections/options are missing, it creates them with default values.
    
    Args:
        default_config (dict): A dictionary containing the default settings.
        file_path (str): The path to the configuration file.

    Returns:
        ConfigParser: The populated ConfigParser object.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"⚙️🟢 Entering {current_function} to load configuration.",
                file=current_file, version=current_version, function=current_function)
    
    config = ConfigParser()

    # FIXED: Ensure the directory exists before trying to open the file.
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Check if file exists, if not, create it with defaults
    if not os.path.exists(file_path):
        debug_log(f"⚙️📁 Config file not found at {file_path}. Creating new file with default settings.",
                  file=current_file, version=current_version, function=current_function)
        config.read_dict(default_config)
        with open(file_path, 'w') as configfile:
            config.write(configfile)
    else:
        debug_log(f"⚙️📂 Found config file at {file_path}. Loading settings.",
                  file=current_file, version=current_version, function=current_function)
        config.read(file_path)

        # Ensure all default sections and options exist
        for section, options in default_config.items():
            if not config.has_section(section):
                config.add_section(section)
            for option, default_value in options.items():
                if not config.has_option(section, option):
                    config.set(section, option, str(default_value))
        
    debug_log(f"⚙️✅ Configuration loaded successfully. Exiting {current_function}",
                file=current_file, version=current_version, function=current_function)
    return config

# UPDATED: The function now only takes the config object and console print function.
def save_config(config, console_print_func, app_instance=None):
    """
    Saves all application settings to the specified configuration file.
    It calls modular save functions for each section.
    
    Args:
        config (ConfigParser): The ConfigParser object to save.
        console_print_func (function): The function to use for console output.
    """
    current_function = inspect.currentframe().f_code.co_name
    file_path = CONFIG_FILE_PATH # Use the global constant
    debug_log(f"🔧💾🟢 Saving configuration to {os.path.basename(file_path)}... All hands on deck! ⚙️",
              file=current_file, version=current_version, function=current_function)
    try:
        # Create a new ConfigParser to ensure a clean save
        new_config = ConfigParser()

        # Call all the modular save functions
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
                    file=current_file, version=current_version, function=current_function)