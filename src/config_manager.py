# src/config_manager.py
#
# This file contains functions for loading and saving application configuration
# settings to and from a `config.ini` file. It ensures that default settings
# are present and handles the persistence of user-modified settings.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
#
#
# Version 20250731.2 (Improved config loading for dropdown values)

current_version = "20250731.2" # this variable should always be defined below the header to make the debuggin better

import configparser
import os
import tkinter as tk # Import tkinter for update_idletasks
from utils.utils_instrument_control import debug_print # Import debug_print
import inspect # Import inspect module for debug_print

# NEW: Import all necessary dropdown lists for value lookup during loading
from ref.ref_scanner_setting_lists import (
    graph_quality_drop_down,
    dwell_time_drop_down,
    cycle_wait_time_presets,
    reference_level_drop_down,
    frequency_shift_presets,
    number_of_scans_presets,
    rbw_presets
)

def load_config(app_instance):
    # This function descriotion tells me what this function does
    # Loads configuration settings from `config.ini`.
    # If the file or sections are missing, it ensures default settings are present.
    # This function is called during application initialization to restore
    # the last-used settings or apply defaults. It populates Tkinter variables
    # based on the loaded configuration.
    #
    # Inputs to this function
    #   app_instance (App): The main application instance, providing access to its config object,
    #                       Tkinter variables, and other necessary attributes like SCAN_BAND_RANGES.
    #
    # Process of this function
    #   1. Reads `app_instance.CONFIG_FILE` into `app_instance.config` using `configparser`.
    #   2. Ensures `DEFAULT_SETTINGS` and `LAST_USED_SETTINGS` sections exist, creating them if not.
    #   3. Defines a comprehensive dictionary `default_values` for all application settings,
    #      including new meta data and equipment fields.
    #   4. Populates `DEFAULT_SETTINGS` with any missing default values.
    #   5. Dynamically generates and sets default selected bands if missing.
    #   6. Ensures `last_GLOBAL__window_geometry` is set.
    #   7. Iterates through `app_instance.setting_var_map` to load values from `config.ini`
    #      into the corresponding Tkinter variables, handling type conversions (Boolean, Int, Float, String).
    #      Crucially, it now attempts to convert old string labels from dropdowns into their
    #      numeric equivalents if direct conversion fails.
    #   8. Includes robust error handling for type conversion failures.
    #   9. Loads the last selected bands and updates `app_instance.band_vars`.
    #   10. Prints debug messages throughout the process, including the final config contents.
    #
    # Outputs of this function
    #   None. Modifies the `app_instance.config` object and populates `app_instance` Tkinter variables.
    #
    # (2025-07-30) Change: Added new default values for postal code lookup results and
    #                      antenna/amplifier details. Removed `map_location` and
    #                      old `antenna_type` defaults.
    # (2025-07-30) Change: Added default values for amplifier description and use.
    # (2025-07-31) Change: Added default for `GLOBAL__paned_window_sash_position`.
    # (2025-07-31) Change: Updated header.
    # (2025-07-31) Change: Improved loading logic for dropdown-backed numeric StringVars.
    #                      Now attempts to convert string labels (e.g., "Standard") to their
    #                      numeric values (e.g., 1.0) using the imported setting lists.
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__

    debug_print(f"Attempting to load configuration from {app_instance.CONFIG_FILE}...", file=current_file, function=current_function)
    app_instance.config.read(app_instance.CONFIG_FILE)

    if 'DEFAULT_SETTINGS' not in app_instance.config:
        app_instance.config['DEFAULT_SETTINGS'] = {}
        debug_print("Created missing 'DEFAULT_SETTINGS' section.", file=current_file, function=current_function)

    if 'LAST_USED_SETTINGS' not in app_instance.config:
        app_instance.config['LAST_USED_SETTINGS'] = {}
        debug_print("Created missing 'LAST_USED_SETTINGS' section.", file=current_file, function=current_function)

    # Define default values for all settings using the new prefixed style
    default_values = {
        'GLOBAL__window_geometry': '1400x780+100+100',
        'GLOBAL__debug_enabled': 'False',
        'GLOBAL__log_visa_commands_enabled': 'False',
        'GLOBAL__paned_window_sash_position': '700', # NEW: Default sash position

        'instrument_connection__visa_resource': 'N/A',

        'scan_configuration__scan_name': 'ThisIsMyScan',
        'scan_configuration__scan_directory': 'scan_data',
        'scan_configuration__num_scan_cycles': '1',
        'scan_configuration__rbw_step_size_hz': '10000',
        'scan_configuration__cycle_wait_time_seconds': '0.5',
        'scan_configuration__maxhold_time_seconds': '3',
        'scan_configuration__scan_rbw_hz': '10000',
        'scan_configuration__reference_level_dbm': '-40',
        'scan_configuration__freq_shift_hz': '0',
        'scan_configuration__maxhold_enabled': 'True',
        'scan_configuration__sensitivity': 'True', # Renamed from high_sensitivity
        'scan_configuration__preamp_on': 'True',
        'scan_configuration__scan_rbw_segmentation': '1000000.0',
        'scan_configuration__default_focus_width': '10000.0',
        # 'scan_configuration__selected_bands' is dynamically generated below

        'scan_meta_data__operator_name': 'Anthony Peter Kuzub',
        'scan_meta_data__contact': 'I@Like.audio',
        'scan_meta_data__name': 'Garage', # Renamed from venue_name
        
        # NEW: Default values for postal code lookup and new antenna/amplifier fields
        'scan_meta_data__venue_postal_code': '',
        'scan_meta_data__address_field': '',
        'scan_meta_data__city': 'Whitby', # Still used for City
        'scan_meta_data__province': '', # NEW: For Province
        # Removed: 'scan_meta_data__map_location': '',

        'scan_meta_data__scanner_type': 'Unknown',
        
        # NEW: Default values for antenna and amplifier dropdowns
        'scan_meta_data__selected_antenna_type': '', # Default to empty, will be set on first selection
        'scan_meta_data__antenna_description': '',
        'scan_meta_data__antenna_use': '',
        'scan_meta_data__antenna_mount': '',
        'scan_meta_data__selected_amplifier_type': '', # Default to empty, will be set on first selection
        'scan_meta_data__antenna_amplifier': '', # This will store the final selected amplifier name
        'scan_meta_data__amplifier_description': '', # NEW: Default for amplifier description
        'scan_meta_data__amplifier_use': '',         # NEW: Default for amplifier use

        'scan_meta_data__notes': '',

        'plotting__scan_markers_to_plot__include_gov_markers': 'True',
        'plotting__scan_markers_to_plot__include_tv_markers': 'True',
        'plotting__scan_markers_to_plot__include_markers': 'True',
        'plotting__scan_markers_to_plot__include_intermod_markers': 'False', # NEW
        'plotting__scan_markers_to_plot__open_html_after_complete': 'True',
        'plotting__scan_markers_to_plot__create_html': 'True', # New plotting setting

        'plotting__average_markers_to_plot__include_gov_markers': 'True',
        'plotting__average_markers_to_plot__include_tv_markers': 'True',
        'plotting__average_markers_to_plot__include_tv_markers': 'True', # Duplicated, keeping for now as per original
        'plotting__average_markers_to_plot__include_markers': 'True',
        'plotting__average_markers_to_plot__include_intermod_markers': 'False', # NEW
        'plotting__average_markers_to_plot__math_average': 'True',
        'plotting__average_markers_to_plot__math_median': 'True',
        'plotting__average_markers_to_plot__math_range': 'True',
        'plotting__average_markers_to_plot__math_standard_deviation': 'True',
        'plotting__average_markers_to_plot__math_variance': 'True',
        'plotting__average_markers_to_plot__math_psd': 'True',
    }

    # Ensure all default settings are present
    for key, value in default_values.items():
        if f"default_{key}" not in app_instance.config['DEFAULT_SETTINGS']:
            app_instance.config['DEFAULT_SETTINGS'][f"default_{key}"] = value
            debug_print(f"Added missing default setting: default_{key}={value}", file=current_file, function=current_function)

    # Dynamically generate default_scan_configuration__selected_bands if missing
    if 'default_scan_configuration__selected_bands' not in app_instance.config['DEFAULT_SETTINGS']:
        default_bands_str = ",".join([band["Band Name"] for band in app_instance.SCAN_BAND_RANGES])
        app_instance.config['DEFAULT_SETTINGS']['default_scan_configuration__selected_bands'] = default_bands_str
        debug_print(f"Generated default_scan_configuration__selected_bands: {default_bands_str}", file=current_file, function=current_function)

    # Ensure last_GLOBAL__window_geometry is set in LAST_USED_SETTINGS
    if 'last_GLOBAL__window_geometry' not in app_instance.config['LAST_USED_SETTINGS']:
        default_geometry = app_instance.config['DEFAULT_SETTINGS'].get('default_GLOBAL__window_geometry', '1400x780+100+100')
        app_instance.config['LAST_USED_SETTINGS']['last_GLOBAL__window_geometry'] = default_geometry
        debug_print(f"Set last_GLOBAL__window_geometry to default: {default_geometry}", file=current_file, function=current_function)

    # Helper to get config value, with fallback to default, then hardcoded default
    def _get_config_value(section, key_prefix, key_suffix, hardcoded_fallback=None):
        # Construct the full key name for LAST_USED_SETTINGS
        last_key = f"last_{key_prefix}__{key_suffix}"
        if app_instance.config.has_option(section, last_key):
            return app_instance.config.get(section, last_key)
        
        # Construct the full key name for DEFAULT_SETTINGS
        default_key = f"default_{key_prefix}__{key_suffix}"
        if app_instance.config.has_option('DEFAULT_SETTINGS', default_key):
            return app_instance.config.get('DEFAULT_SETTINGS', default_key)
        
        return hardcoded_fallback

    # Mapping from config key suffix to the dropdown list and its value key
    dropdown_value_maps = {
        'rbw_step_size_hz': {'list': graph_quality_drop_down, 'value_key': 'resolution_hz'},
        'cycle_wait_time_seconds': {'list': cycle_wait_time_presets, 'value_key': 'time_sec'}, # Changed to wait_time_presets
        'maxhold_time_seconds': {'list': dwell_time_drop_down, 'value_key': 'time_sec'}, # Changed to dwell_time_drop_down
        'scan_rbw_hz': {'list': rbw_presets, 'value_key': 'rbw_hz'},
        'reference_level_dbm': {'list': reference_level_drop_down, 'value_key': 'level_dbm'},
        'freq_shift_hz': {'list': frequency_shift_presets, 'value_key': 'shift_hz'},
        'num_scan_cycles': {'list': number_of_scans_presets, 'value_key': 'scans'},
    }


    # Load settings into Tkinter variables using the mapping
    for tk_var_name, (last_key_full, default_key_full, tk_var) in app_instance.setting_var_map.items():
        # Extract prefix and suffix from the full default_key string
        # Assuming default_key_full is like "default_SECTION__KEY"
        parts = default_key_full.split('__', 1) # Split only on the first '__'
        if len(parts) < 2: # Handle cases like 'default_window_geometry' which don't have a prefix
            key_prefix = 'GLOBAL' # Assume 'GLOBAL' for old non-prefixed keys
            key_suffix = default_key_full.replace('default_', '')
        else:
            key_prefix = parts[0].replace('default_', '') # e.g., 'scan_configuration'
            key_suffix = parts[1] # e.g., 'scan_name'

        value_str = _get_config_value('LAST_USED_SETTINGS', key_prefix, key_suffix, default_values.get(f"{key_prefix}__{key_suffix}", ''))

        if value_str is None: # If no value found, use the hardcoded default from default_values
            value_str = default_values.get(f"{key_prefix}__{key_suffix}", '')

        # Special handling for dropdown-backed numeric StringVars
        if key_suffix in dropdown_value_maps and isinstance(tk_var, tk.StringVar):
            dropdown_info = dropdown_value_maps[key_suffix]
            dropdown_list = dropdown_info['list']
            value_key = dropdown_info['value_key']

            try:
                # Try to convert to float/int directly (for values saved as numbers)
                if value_key == 'time_sec': # Dwell time can be float
                    numeric_value = float(value_str)
                else: # Others are ints
                    numeric_value = int(float(value_str)) # Use float first to handle "10000.0"
                tk_var.set(str(numeric_value)) # Set as string for StringVar
                debug_print(f"Loading '{last_key_full}' (Type: {type(tk_var).__name__}): '{tk_var.get()}' (Direct Numeric). Version: {current_version}", file=current_file, function=current_function)

            except ValueError:
                # If direct conversion fails, it means value_str might be an old label
                found_numeric_value = None
                for item in dropdown_list:
                    if item["label"] == value_str:
                        found_numeric_value = item[value_key]
                        break
                
                if found_numeric_value is not None:
                    tk_var.set(str(found_numeric_value))
                    debug_print(f"Loading '{last_key_full}' (Type: {type(tk_var).__name__}): '{tk_var.get()}' (Label Converted). Version: {current_version}", file=current_file, function=current_function)
                else:
                    # Fallback to default numeric value if label not found or conversion failed
                    default_val_for_type = default_values.get(f"{key_prefix}__{key_suffix}", '')
                    debug_print(f"Warning: Could not convert '{value_str}' or find label for {last_key_full}. Falling back to default: {default_val_for_type}. Version: {current_version}", file=current_file, function=current_function)
                    tk_var.set(default_val_for_type)
        else:
            # Original handling for other variable types
            try:
                if isinstance(tk_var, tk.BooleanVar):
                    tk_var.set(value_str.lower() == 'true')
                elif isinstance(tk_var, tk.IntVar):
                    tk_var.set(int(float(value_str))) # Use float first to handle "100.0"
                elif isinstance(tk_var, tk.DoubleVar):
                    tk_var.set(float(value_str))
                elif isinstance(tk_var, tk.StringVar):
                    tk_var.set(value_str)
                debug_print(f"Loading '{last_key_full}' (Type: {type(tk_var).__name__}): '{tk_var.get()}' (Standard). Version: {current_version}", file=current_file, function=current_function)
            except ValueError as e:
                debug_print(f"Warning: Could not convert '{value_str}' to {type(tk_var).__name__} for {last_key_full}. Using default. Error: {e}. Version: {current_version}", file=current_file, function=current_function)
                # Fallback to default value from default_values if conversion fails
                default_val_for_type = default_values.get(f"{key_prefix}__{key_suffix}", '')
                if isinstance(tk_var, tk.BooleanVar):
                    tk_var.set(default_val_for_type.lower() == 'true')
                elif isinstance(tk_var, tk.IntVar):
                    tk_var.set(int(float(default_val_for_type)))
                elif isinstance(tk_var, tk.DoubleVar):
                    tk_var.set(float(default_val_for_type))
                elif isinstance(tk_var, tk.StringVar):
                    tk_var.set(default_val_for_type)


    # Load the last selected bands and update Tkinter BooleanVars
    last_selected_bands_str = _get_config_value('LAST_USED_SETTINGS', 'scan_configuration', 'selected_bands', '')
    debug_print(f"Loading 'last_scan_configuration__selected_bands': '{last_selected_bands_str}'. Version: {current_version}", file=current_file, function=current_function)

    selected_bands_list = [band.strip() for band in last_selected_bands_str.split(',') if band.strip()]

    # Update app_instance.band_vars based on loaded selection
    for band_item in app_instance.band_vars:
        if band_item["band"]["Band Name"] in selected_bands_list:
            band_item["var"].set(True)
        else:
            band_item["var"].set(False)

    debug_print("Configuration loaded.", file=current_file, function=current_function)
    debug_print("--- Current ConfigParser Contents (After Loading) ---", file=current_file, function=current_function)
    # Print all sections and their items
    for section in app_instance.config.sections():
        debug_print(f"[{section}]", file=current_file, function=current_function)
        for key, value in app_instance.config.items(section):
            debug_print(f"  {key} = {value}", file=current_file, function=current_function)
    debug_print("--- End ConfigParser Contents ---", file=current_file, function=current_function)


def save_config(app_instance):
    # This function descriotion tells me what this function does
    # Saves the current application settings from Tkinter variables to `config.ini`.
    # This function is called when the application is closing or when a setting changes,
    # ensuring that the last-used settings are preserved. It iterates through the
    # `setting_var_map` to persist all configured Tkinter variables.
    #
    # Inputs to this function
    #   app_instance (App): The main application instance, providing access to its config object
    #                       and Tkinter variables.
    #
    # Process of this function
    #   1. Prints a debug message indicating the start of saving.
    #   2. Ensures the `LAST_USED_SETTINGS` section exists in the config.
    #   3. Iterates through `app_instance.setting_var_map` to save the current value of each
    #      Tkinter variable to the `LAST_USED_SETTINGS` section, using the new prefixed key style.
    #   4. Specifically handles saving the currently selected frequency bands.
    #   5. Updates and saves the current window geometry.
    #   6. Writes the updated configuration to `app_instance.CONFIG_FILE`.
    #   7. Includes error handling for file I/O and other exceptions.
    #   8. Prints debug messages throughout the process, including the final config contents.
    #
    # Outputs of this function
    #   None. Persists application settings to a file.
    #
    # (2025-07-30) Change: Updated to save new Tkinter variables for postal code lookup results and
    #                      antenna/amplifier details. Removed `map_location` and
    #                      old `antenna_type` from saving logic.
    # (2025-07-30) Change: Added default values for amplifier description and use.
    # (2025-07-30) Change: Added detailed debug prints for each variable being saved.
    # (2025-07-31) Change: Updated header.
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__

    debug_print(f"Attempting to save configuration to {app_instance.CONFIG_FILE}...", file=current_file, function=current_function)

    if 'LAST_USED_SETTINGS' not in app_instance.config:
        app_instance.config['LAST_USED_SETTINGS'] = {}
        debug_print("Created missing 'LAST_USED_SETTINGS' section during save.", file=current_file, function=current_function)

    # Save general settings using the map and new prefixed keys
    for var_name, (last_key_full, default_key_full, tk_var) in app_instance.setting_var_map.items():
        # Extract prefix and suffix from the full default_key string
        # Assuming default_key_full is like "default_SECTION__KEY"
        parts = default_key_full.split('__', 1)
        if len(parts) < 2:
            key_prefix = 'GLOBAL' # Assume 'GLOBAL' for old non-prefixed keys
            key_suffix = default_key_full.replace('default_', '')
        else:
            key_prefix = parts[0].replace('default_', '')
            key_suffix = parts[1]

        # Construct the full key name for LAST_USED_SETTINGS
        last_key_to_save = f"last_{key_prefix}__{key_suffix}"
        
        # --- NEW DEBUG PRINT ---
        try:
            value_to_save = str(tk_var.get())
            app_instance.config['LAST_USED_SETTINGS'][last_key_to_save] = value_to_save
            debug_print(f"Saving '{last_key_to_save}': '{value_to_save}' (from TkVar: {var_name})", file=current_file, function=current_function)
        except Exception as e:
            debug_print(f"❌ Error getting value for '{var_name}' (mapped to '{last_key_to_save}'): {e}", file=current_file, function=current_function)
            # If there's an error getting the value, ensure it's still saved as an empty string or default
            app_instance.config['LAST_USED_SETTINGS'][last_key_to_save] = ''


    # Save selected bands
    selected_band_names = [item["band"]["Band Name"] for item in app_instance.band_vars if item["var"].get()]
    bands_to_save = ",".join(selected_band_names)
    app_instance.config['LAST_USED_SETTINGS']['last_scan_configuration__selected_bands'] = bands_to_save
    debug_print(f"Saving 'last_scan_configuration__selected_bands': '{bands_to_save}'", file=current_file, function=current_function)

    # Force update of window geometry before saving
    app_instance.update_idletasks() # IMPORTANT: Ensure geometry is up-to-date
    current_geometry = app_instance.winfo_geometry()
    app_instance.config['LAST_USED_SETTINGS']['last_GLOBAL__window_geometry'] = current_geometry
    debug_print(f"Saving 'last_GLOBAL__window_geometry': '{current_geometry}'", file=current_file, function=current_function)

    try:
        with open(app_instance.CONFIG_FILE, 'w') as configfile:
            app_instance.config.write(configfile)
        debug_print(f"Configuration successfully written to {app_instance.CONFIG_FILE}", file=current_file, function=current_function)
    except IOError as e:
        debug_print(f"❌ I/O Error saving configuration to {app_instance.CONFIG_FILE}: {e}", file=current_file, function=current_function)
    except Exception as e:
        debug_print(f"❌ An unexpected error occurred while saving configuration: {e}", file=current_file, function=current_function)


def save_config_as_new_file(config_obj, file_path, console_print_func):
    # This function descriotion tells me what this function does
    # Saves a given ConfigParser object to a specified file path.
    # This is typically used for "Save As" functionality for configuration files.
    #
    # Inputs to this function
    #   config_obj (configparser.ConfigParser): The ConfigParser object to save.
    #   file_path (str): The full path to the file where the config will be saved.
    #   console_print_func (function): Function to print messages to the GUI console.
    #
    # Process of this function
    #   1. Prints a debug message indicating the attempt to save.
    #   2. Opens the specified file in write mode (`'w'`).
    #   3. Writes the `config_obj` to the file.
    #   4. Prints a success message.
    #   5. Includes error handling for `IOError` and other exceptions, re-raising them
    #      for the calling function to handle.
    #
    # Outputs of this function
    #   None. Writes data to a file.
    #
    # (2025-07-30) Change: No functional change, just updated header.
    # (2025-07-31) Change: Updated header.
    """
    Saves a given ConfigParser object to a specified file path.

    Inputs:
        config_obj (configparser.ConfigParser): The ConfigParser object to save.
        file_path (str): The full path to the file where the config will be saved.
        console_print_func (function): Function to print messages to the GUI console.
    Outputs: None
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__

    debug_print(f"Attempting to save configuration to new file: {file_path}", file=current_file, function=current_function, console_print_func=console_print_func)
    try:
        with open(file_path, 'w') as configfile:
            config_obj.write(configfile)
        debug_print(f"Configuration successfully saved to {file_path}", file=current_file, function=current_function, console_print_func=console_print_func)
    except IOError as e:
        debug_print(f"❌ I/O Error saving configuration to {file_path}: {e}", file=current_file, function=current_function, console_print_func=console_print_func)
        raise # Re-raise to be caught by the calling function
    except Exception as e:
        debug_print(f"❌ An unexpected error occurred while saving configuration to {file_path}: {e}", file=current_file, function=current_function, console_print_func=console_print_func)
        raise # Re-raise to be caught by the calling function
