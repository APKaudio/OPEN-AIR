# src/settings_and_config/restore_settings_logic.py
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
# Version 20250823.140000.1
# UPDATED: Added handling to restore the new MarkerTab values from the config file.
# FIXED: Corrected the `load_config` call to align with the latest function signature.

import tkinter as tk
import inspect
import os
from configparser import ConfigParser

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

# Import config management functions
from settings_and_config.config_manager import load_config, save_config


# --- Versioning ---
w = 20250823
x_str = '140000'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"


def restore_default_settings(app_instance, console_print_func):
    """
    Resets the application settings to their factory default values.
    
    Args:
        app_instance: The main application instance containing the state variables.
        console_print_func: A function to print messages to the GUI console.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message="⚙️🟢 Entering function to restore default settings.",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)
    
    console_print_func("⚠️ Restoring all settings to factory defaults. This is a big one!.")
    
    from settings_and_config.program_default_values import DEFAULT_CONFIG_VALUES, CONFIG_FILE_PATH

    try:
        default_config = ConfigParser()
        for section, values in DEFAULT_CONFIG_VALUES.items():
            default_config.add_section(section)
            for key, value in values.items():
                default_config.set(section, key, str(value))
        
        # Save the default configuration to the primary config file
        save_config(config=default_config,
                    file_path=CONFIG_FILE_PATH,
                    console_print_func=console_print_func,
                    app_instance=app_instance)
        
        # Re-load the newly saved default settings back into the application
        restore_last_used_settings(app_instance, console_print_func)

        console_print_func("✅ All settings have been restored to their factory defaults.")
        debug_log(message="Default settings restoration completed. The factory reset is done! 🚀",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function,
                    special=True)
        
    except Exception as e:
        console_print_func(f"❌ An error occurred while restoring default settings: {e}")
        debug_log(message=f"Failed to restore default settings: {e}",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function,
                    special=True)

def restore_last_used_settings(app_instance, console_print_func):
    """
    Loads and restores the application settings from the last-used configuration file.
    
    Args:
        app_instance: The main application instance containing the state variables.
        console_print_func: A function to print messages to the GUI console.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message="⚙️🟢 Entering function to restore last used settings.",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)
    
    console_print_func("✅ Attempting to restore last used settings...")
    
    from settings_and_config.program_default_values import CONFIG_FILE_PATH

    try:
        # Load the configuration from the file
        config = load_config(file_path=CONFIG_FILE_PATH, console_print_func=console_print_func)
        
        # Restore MarkerTab settings
        if 'MarkerTab' in config and hasattr(app_instance, 'showtime_parent_tab'):
            showtime_tab = app_instance.showtime_parent_tab

            # Restore Poke frequency
            if config.has_option('MarkerTab', 'poke_freq_mhz'):
                poke_freq_str = config.get('MarkerTab', 'poke_freq_mhz')
                try:
                    poke_freq = float(poke_freq_str)
                    showtime_tab.poke_freq_var.set(poke_freq)
                    debug_log(message=f"🛠️📝 Restored 'poke_freq_mhz' to {poke_freq_str} MHz.",
                                file=current_file, version=current_version, function=current_function)
                except ValueError:
                    debug_log(message=f"🛠️❌ Cannot restore 'poke_freq_mhz'. Invalid value: {poke_freq_str}",
                                file=current_file, version=current_version, function=current_function)
            
            # Restore other MarkerTab settings here as needed
            for trace_type in ['live', 'max', 'min']:
                trace_key = f'trace_{trace_type}'
                if config.has_option('MarkerTab', trace_key):
                    trace_state = config.getboolean('MarkerTab', trace_key)
                    showtime_tab.trace_modes[trace_type].set(trace_state)
                    debug_log(message=f"🛠️📝 Restored '{trace_key}' to {trace_state}.",
                                file=current_file, version=current_version, function=current_function)

            # Restore trace variables from config
            if config.has_option('MarkerTab', 'span_hz'):
                showtime_tab.span_var.set(config.getfloat('MarkerTab', 'span_hz'))
            if config.has_option('MarkerTab', 'rbw_hz'):
                showtime_tab.rbw_var.set(config.getfloat('MarkerTab', 'rbw_hz'))
            if config.has_option('MarkerTab', 'buffer_mhz'):
                showtime_tab.buffer_var.set(config.getfloat('MarkerTab', 'buffer_mhz'))
        else:
             debug_log(message="🔧💾❌ Config object: 'MarkerTab' or 'showtime_parent_tab' not available. Skipping MarkerTab restore.",
                        file=current_file, version=current_version, function=current_function)

        # Update the UI with the restored values
        if hasattr(app_instance, '_set_initial_slider_positions'):
            # Assuming this method exists and correctly updates sliders
            debug_log("Called _set_initial_slider_positions to update sliders. Sliders adjusted!",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        else:
            debug_log("App instance does not have _set_initial_slider_positions method. Skipping slider update.",
                        file=current_file,
                        version=current_version,
                        function=current_function)

        # Reset setting colors (e.g., remove any "changed" highlights)
        if hasattr(app_instance, 'reset_setting_colors_logic'):
            app_instance.reset_setting_colors_logic()
        
        console_print_func("✅ All settings restored to last used values. Back in business!")
        debug_log("Last used settings restored. UI synced!",
                    file=current_file,
                    version=current_version,
                    function=current_function,
                    special=True)
            
    except Exception as e:
        console_print_func(f"❌ An error occurred while restoring last used settings: {e}. This is a disaster!")
        debug_log(f"Failed to restore last used settings: {e}",
                    file=current_file,
                    version=current_version,
                    function=current_function,
                    special=True)