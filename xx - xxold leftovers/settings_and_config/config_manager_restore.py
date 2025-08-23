# settings_and_config/config_manager_restore.py
#
# This file contains the core logic for managing application settings,
# including restoring default settings, restoring last-used settings,
# and resetting the visual indicators of changed settings in the GUI.
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
# Version 20250821.212500.1 (FIXED: Replaced debug_log with print for startup safety)

import tkinter as tk
import inspect
import os
from configparser import ConfigParser
from datetime import datetime

# --- REMOVED: debug_log import to prevent circular dependency on startup ---
# from display.debug_logic import debug_log 
from display.console_logic import console_log

# Import the correct, renamed config management functions
from settings_and_config.config_manager_save import load_program_config, save_program_config


# --- Versioning ---
w = 20250821
x_str = '212500'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_file = f"{os.path.basename(__file__)}"


def restore_default_settings(app_instance, console_print_func):
    """
    Resets the application settings to their factory default values.
    
    Args:
        app_instance: The main application instance containing the state variables.
        console_print_func: A function to print messages to the GUI console.
    """
    current_function = inspect.currentframe().f_code.co_name
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # --- FIXED: Use print() for startup-critical logging ---
    print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ⚙️🟢 Entering function to restore default settings.")
    
    console_print_func("⚠️ Restoring all settings to factory defaults.")
    
    from ref.ref_program_default_values import DEFAULT_CONFIG

    try:
        default_config = ConfigParser()
        default_config.read_dict(DEFAULT_CONFIG)
        
        save_program_config(default_config)
        
        app_instance.program_config = load_program_config()
        restore_last_used_settings(app_instance, console_print_func)

        console_print_func("✅ All settings have been restored to their factory defaults.")
        print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ✅ Default settings restoration completed.")
        
    except Exception as e:
        error_msg = f"❌ An error occurred while restoring default settings: {e}"
        console_print_func(error_msg)
        print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - {error_msg}")

def restore_last_used_settings(app_instance, console_print_func):
    """
    Loads and restores the application settings from the last-used configuration file.
    
    Args:
        app_instance: The main application instance containing the state variables.
        console_print_func: A function to print messages to the GUI console.
    """
    current_function = inspect.currentframe().f_code.co_name
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # --- FIXED: Use print() for startup-critical logging ---
    print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ⚙️🟢 Entering function to restore last used settings.")
    
    console_print_func("✅ Attempting to restore last used settings...")
    
    try:
        config = app_instance.program_config
        
        # Restore MarkerTab settings
        if 'MarkerTab' in config and hasattr(app_instance, 'showtime_parent_tab') and app_instance.showtime_parent_tab is not None:
            showtime_tab = app_instance.showtime_parent_tab

            if config.has_option('MarkerTab', 'poke_freq_mhz'):
                poke_freq_str = config.get('MarkerTab', 'poke_freq_mhz')
                showtime_tab.poke_freq_var.set(poke_freq_str)
            
            for trace_type in ['live', 'max', 'min']:
                trace_key = f'trace_{trace_type}'
                if config.has_option('MarkerTab', trace_key):
                    trace_state = config.getboolean('MarkerTab', trace_key)
                    if hasattr(showtime_tab, 'trace_modes') and trace_type in showtime_tab.trace_modes:
                        showtime_tab.trace_modes[trace_type].set(trace_state)

            if config.has_option('MarkerTab', 'span_hz'):
                showtime_tab.span_var.set(config.get('MarkerTab', 'span_hz'))
            if config.has_option('MarkerTab', 'rbw_hz'):
                showtime_tab.rbw_var.set(config.get('MarkerTab', 'rbw_hz'))
            if config.has_option('MarkerTab', 'buffer_mhz'):
                showtime_tab.buffer_var.set(config.get('MarkerTab', 'buffer_mhz'))

        console_print_func("✅ All settings restored to last used values.")
        print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ✅ Last used settings restored.")
            
    except Exception as e:
        error_msg = f"❌ An error occurred while restoring last used settings: {e}."
        console_print_func(error_msg)
        print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - {error_msg}")
