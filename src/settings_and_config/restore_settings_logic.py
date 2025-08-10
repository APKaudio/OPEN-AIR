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
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
# Version 20250810.220100.9 (FIXED: Corrected function call to load_config to match the new signature, resolving a TypeError.)

current_version = "20250810.220100.9"
current_version_hash = 20250810 * 220100 * 9 # Example hash, adjust as needed

import tkinter as tk
import inspect
import os

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

# Import config management functions
from src.settings_and_config.config_manager import load_config, save_config # Import save_config
from src.program_default_values import DEFAULT_CONFIG # Import default values


def restore_default_settings_logic(app_instance, console_print_func):
    """
    Function Description:
    Loads the default configuration settings and applies them to the application's
    variables, effectively resetting the UI to its initial state.
    
    Inputs:
    - app_instance (object): A reference to the main application instance.
    - console_print_func (function): A function for printing to the console.
    
    Outputs of this function:
    - None. The application's state and UI are updated to default values.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = os.path.basename(__file__)
    
    debug_log(f"Restoring all settings to default. Hitting the reset button! Version: {current_version}",
                file=current_file,
                version=current_version,
                function=current_function)
    
    try:
        # Create a temporary config object with default values
        app_instance.config.clear()
        for section, settings in DEFAULT_CONFIG.items():
            if not app_instance.config.has_section(section):
                app_instance.config.add_section(section)
            for key, value in settings.items():
                app_instance.config.set(section, key, str(value))
        
        # Now, load these values into the Tkinter variables
        for var_name, var_info in app_instance.setting_var_map.items():
            section, key = var_info['section'], var_info['key']
            if app_instance.config.has_option(section, key):
                try:
                    # Get the value from the new default config object
                    value = app_instance.config.get(section, key)
                    
                    # Convert to correct type and set the Tkinter variable
                    if isinstance(var_info['var'], tk.BooleanVar):
                        value = value.lower() == 'true'
                    elif isinstance(var_info['var'], tk.DoubleVar):
                        value = float(value)
                    elif isinstance(var_info['var'], tk.IntVar):
                        value = int(value)
                    
                    var_info['var'].set(value)
                    debug_log(f"Set '{var_name}' to default value: '{value}'",
                                file=current_file,
                                version=current_version,
                                function=current_function)
                except Exception as e:
                    debug_log(f"❌ Error setting default value for '{var_name}': {e}. What a fucking mess!",
                                file=current_file,
                                version=current_version,
                                function=current_function)

        # Restore band importance levels to defaults
        bands_levels_str = app_instance.config.get('Scan', 'last_scan_configuration__selected_bands_levels', fallback='')
        if bands_levels_str:
            band_levels_dict = {}
            for item in bands_levels_str.split(','):
                try:
                    name, level = item.split('=')
                    band_levels_dict[name.strip()] = int(level.strip())
                except ValueError:
                    debug_log(f"❌ Error parsing band level item: '{item}'. Skipping.",
                                file=current_file,
                                version=current_version,
                                function=current_function)
            
            for band_item in app_instance.band_vars:
                band_name = band_item["band"]["Band Name"]
                band_item["level"] = band_levels_dict.get(band_name, 0)

            debug_log("Restored band importance levels from default config.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        
        # Save the default config to file
        save_config(app_instance.config, app_instance.CONFIG_FILE_PATH, console_print_func, app_instance)
        
        console_print_func("✅ All settings restored to program defaults. A clean slate!")
        debug_log("Program defaults restored. UI reset!",
                    file=current_file,
                    version=current_version,
                    function=current_function,
                    special=True)

    except Exception as e:
        console_print_func(f"❌ An error occurred while restoring default settings: {e}. This is a problem!")
        debug_log(f"Failed to restore default settings: {e}",
                    file=current_file,
                    version=current_version,
                    function=current_function,
                    special=True)
    

def restore_last_used_settings_logic(app_instance, console_print_func):
    """
    Function Description:
    Loads the last used configuration from the config file and applies it to the
    application's variables.

    Inputs:
    - app_instance (object): A reference to the main application instance.
    - console_print_func (function): A function for printing to the console.
    
    Outputs of this function:
    - None. The application's state and UI are updated to last used values.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = os.path.basename(__file__)
    
    debug_log(f"RESTORE_LAST_USED_SETTINGS_LOGIC HAS BEEN CALLED! Let's get back to where we were! Version: {current_version}",
                file=current_file,
                version=current_version,
                function=current_function,
                special=True)
    
    try:
        # Load the configuration from file into the app_instance.config object
        # CORRECTED: The load_config function now requires only two arguments.
        # This fixes the TypeError: load_config() takes 2 positional arguments but 3 were given
        app_instance.config = load_config(app_instance.CONFIG_FILE_PATH, console_print_func)
        
        # Restore the main Tkinter variables using the loaded config
        # We can safely assume setting_var_map has been populated by this point
        for key, var_info in app_instance.setting_var_map.items():
            section, key_name = var_info['section'], var_info['key']
            if app_instance.config.has_option(section, key_name):
                try:
                    value = app_instance.config.get(section, key_name)
                    
                    if isinstance(var_info['var'], tk.BooleanVar):
                        value = value.lower() == 'true'
                    elif isinstance(var_info['var'], tk.DoubleVar):
                        value = float(value)
                    elif isinstance(var_info['var'], tk.IntVar):
                        value = int(value)
                    
                    var_info['var'].set(value)
                    debug_log(f"Restored '{key_name}' to last used value: '{value}'",
                                file=current_file,
                                version=current_version,
                                function=current_function)
                except Exception as e:
                    debug_log(f"❌ Error restoring last used value for '{key_name}': {e}",
                                file=current_file,
                                version=current_version,
                                function=current_function)
        
        # NEW LOGIC: Restore band importance levels from the loaded config.ini file.
        bands_levels_str = app_instance.config.get('Scan', 'last_scan_configuration__selected_bands_levels', fallback='')
        debug_log(f"Attempting to restore band levels from config. Raw string: '{bands_levels_str}'",
                    file=current_file,
                    version=current_version,
                    function=current_function, special=True)
        if bands_levels_str:
            band_levels_dict = {}
            for item in bands_levels_str.split(','):
                try:
                    name, level = item.split('=')
                    band_levels_dict[name.strip()] = int(level.strip())
                except ValueError:
                    debug_log(f"❌ Error parsing band level item: '{item}'. This is fucking ridiculous. Skipping.",
                                file=current_file,
                                version=current_version,
                                function=current_function)
            
            # Now, apply these levels to the band_vars list.
            for band_item in app_instance.band_vars:
                band_name = band_item["band"]["Band Name"]
                # Use .get() to avoid key errors if a band from the config is missing.
                band_item["level"] = band_levels_dict.get(band_name, 0)
                debug_log(f"Set band '{band_name}' to level: {band_item['level']}",
                            file=current_file,
                            version=current_version,
                            function=current_function)


            debug_log("Restored band importance levels from last used config successfully!",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        else:
            debug_log("No saved band importance levels found in config. Using current defaults.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        
        # Restore the last used scan name
        last_scan_name = app_instance.config.get('Scan', 'scan_name', fallback='New Scan')
        app_instance.scan_name_var.set(last_scan_name)
        debug_log(f"Restored scan name: '{last_scan_name}'",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Update sliders to reflect new last-used values
        if hasattr(app_instance, '_set_initial_slider_positions'):
            app_instance._set_initial_slider_positions() # Assuming this method exists and correctly updates sliders
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
