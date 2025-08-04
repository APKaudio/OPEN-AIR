# src/settings_logic.py
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
# Version 20250802.0045.1 (Refactored debug_print to debug_log; updated imports and flair.)
# Version 20250804.022251.0 (FIXED: Added logic to load selected bands in restore_last_used_settings_logic.)

current_version = "20250804.022251.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 45 * 1 # Example hash, adjust as needed

import tkinter as tk
import inspect
import os

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Import config management functions
from src.settings_and_config.config_manager import load_config, save_config # Import save_config


def restore_default_settings_logic(app_instance, console_print_func=None):
    """
    Function Description:
    Restores all application settings to their default values as defined in config.ini.
    This function updates the Tkinter variables and then saves these defaults to
    the LAST_USED_SETTINGS section, effectively resetting the user's saved preferences.

    Inputs:
    - app_instance (object): The main application instance, providing access to
                             its `config` object and `setting_var_map`.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Prints a debug message.
    2. Iterates through `app_instance.setting_var_map`.
    3. For each setting, retrieves its default value from the `DEFAULT_SETTINGS` section
       of `app_instance.config`.
    4. Converts the default value to the appropriate Tkinter variable type (Boolean, Int, Double, String).
    5. Sets the Tkinter variable to the default value.
    6. Updates the `LAST_USED_SETTINGS` section in `app_instance.config` with these defaults.
    7. Handles special cases for `notes_var`, `band_vars`, `selected_antenna_type_var`,
       `selected_amplifier_type_var`, `output_folder_var`, and `scan_name_var`.
    8. Saves the modified configuration using `save_config`.
    9. Calls `app_instance.reset_setting_colors_logic` to clear any visual indicators.
    10. Logs success or failure.

    Outputs of this function:
    - None. Modifies Tkinter variables and the configuration file.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Attempting to restore default settings... Wiping the slate clean!",
                file=__file__,
                version=current_version,
                function=current_function)

    # Iterate through the setting_var_map and set each Tkinter variable
    # to its default value from the DEFAULT_SETTINGS section.
    for tk_var_name, (last_key, default_key, tk_var_instance) in app_instance.setting_var_map.items():
        if default_key: # Only restore if a default_key is defined
            default_value_str = app_instance.config.get('DEFAULT_SETTINGS', default_key, fallback=None)
            if default_value_str is not None:
                try:
                    # Convert to appropriate type based on Tkinter variable type
                    if isinstance(tk_var_instance, tk.BooleanVar):
                        value = default_value_str.lower() == 'true'
                    elif isinstance(tk_var_instance, tk.IntVar):
                        value = int(float(default_value_str)) # Handle floats stored as ints
                    elif isinstance(tk_var_instance, tk.DoubleVar):
                        value = float(default_value_str)
                    else: # tk.StringVar
                        value = default_value_str
                    tk_var_instance.set(value)
                    # Also update LAST_USED_SETTINGS immediately
                    app_instance.config.set('LAST_USED_SETTINGS', last_key, str(value))
                    debug_log(f"Restored '{tk_var_name}' to default '{value}'.",
                                file=__file__,
                                version=current_version,
                                function=current_function)
                except ValueError as e:
                    error_msg = f"❌ Error converting default value for '{tk_var_name}': {default_value_str} - {e}. Data type mismatch!"
                    console_print_func(error_msg)
                    debug_log(error_msg,
                                file=__file__,
                                version=current_version,
                                function=current_function)
                except Exception as e:
                    error_msg = f"❌ An unexpected error occurred setting default for '{tk_var_name}': {e}. This is a problem!"
                    console_print_func(error_msg)
                    debug_log(error_msg,
                                file=__file__,
                                version=current_version,
                                function=current_function)
            else:
                debug_log(f"No default value found for '{tk_var_name}' in config. Skipping.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        else:
            debug_log(f"'{tk_var_name}' has no default_key defined. Skipping default restore for this setting.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    # Special handling for notes_var and band_vars (not in setting_var_map)
    default_notes = app_instance.config.get('DEFAULT_SETTINGS', 'notes', fallback='')
    app_instance.notes_var.set(default_notes)
    app_instance.config.set('LAST_USED_SETTINGS', 'notes', default_notes)
    debug_log(f"Restored notes to default: '{default_notes}'",
                file=__file__,
                version=current_version,
                function=current_function)

    # Reset selected bands to default (usually all unchecked or a specific default set)
    # Assuming default is no bands selected unless specified otherwise in DEFAULT_SETTINGS
    default_selected_bands_str = app_instance.config.get('DEFAULT_SETTINGS', 'last_scan_configuration__selected_bands', fallback='')
    default_selected_band_names = [name.strip() for name in default_selected_bands_str.split(',') if name.strip()]
    for band_item in app_instance.band_vars:
        band_name = band_item["band"]["Band Name"]
        band_item["var"].set(band_name in default_selected_band_names)
    app_instance.config.set('LAST_USED_SETTINGS', 'last_scan_configuration__selected_bands', ",".join(default_selected_band_names))
    debug_log(f"Restored selected bands to default: {default_selected_band_names}",
                file=__file__,
                version=current_version,
                function=current_function)

    # Restore Antenna Type
    default_antenna_type = app_instance.config.get('DEFAULT_SETTINGS', 'antenna_type', fallback='')
    app_instance.selected_antenna_type_var.set(default_antenna_type)
    app_instance.config.set('LAST_USED_SETTINGS', 'antenna_type', default_antenna_type)
    debug_log(f"Restored antenna type to default: '{default_antenna_type}'",
                file=__file__,
                version=current_version,
                function=current_function)

    # Restore Antenna Amplifier Type
    default_amplifier_type = app_instance.config.get('DEFAULT_SETTINGS', 'antenna_amplifier_type', fallback='')
    app_instance.selected_amplifier_type_var.set(default_amplifier_type)
    app_instance.config.set('LAST_USED_SETTINGS', 'antenna_amplifier_type', default_amplifier_type)
    debug_log(f"Restored amplifier type to default: '{default_amplifier_type}'",
                file=__file__,
                version=current_version,
                function=current_function)

    # Restore Output Folder
    default_output_folder = app_instance.config.get('DEFAULT_SETTINGS', 'output_folder', fallback=os.path.join(os.getcwd(), 'scan_data'))
    app_instance.output_folder_var.set(default_output_folder)
    app_instance.config.set('LAST_USED_SETTINGS', 'output_folder', default_output_folder)
    debug_log(f"Restored output folder to default: '{default_output_folder}'",
                file=__file__,
                version=current_version,
                function=current_function)

    # Restore Scan Name
    default_scan_name = app_instance.config.get('DEFAULT_SETTINGS', 'scan_name', fallback='New Scan')
    app_instance.scan_name_var.set(default_scan_name)
    app_instance.config.set('LAST_USED_SETTINGS', 'scan_name', default_scan_name)
    debug_log(f"Restored scan name to default: '{default_scan_name}'",
                file=__file__,
                version=current_version,
                function=current_function)


    # Save the updated config (with defaults now in LAST_USED_SETTINGS)
    save_config(app_instance.config, app_instance.CONFIG_FILE_PATH, console_print_func, app_instance)

    # Reset setting colors (e.g., remove any "changed" highlights)
    if hasattr(app_instance, 'reset_setting_colors_logic'):
        app_instance.reset_setting_colors_logic()
    
    console_print_func("✅ All settings restored to default values. Fresh start!")
    debug_log("Default settings restored and saved. UI reset!",
                file=__file__,
                version=current_version,
                function=current_function,
                special=True)


def restore_last_used_settings_logic(app_instance, console_print_func=None):
    """
    Function Description:
    Restores all application settings to their last-used values as saved in config.ini.
    This function updates the Tkinter variables from the `LAST_USED_SETTINGS` section.

    Inputs:
    - app_instance (object): The main application instance, providing access to
                             its `config` object, `setting_var_map`, and other Tkinter variables.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Prints a debug message.
    2. Iterates through `app_instance.setting_var_map`.
    3. For each setting, retrieves its last-used value from the `LAST_USED_SETTINGS` section
       of `app_instance.config`.
    4. Converts the value to the appropriate Tkinter variable type.
    5. Sets the Tkinter variable to the last-used value.
    6. Handles special cases for `notes_var`, `band_vars`, `selected_antenna_type_var`,
       `selected_amplifier_type_var`, `output_folder_var`, and `scan_name_var`.
    7. Calls `app_instance._set_initial_slider_positions` if available, to update sliders.
    8. Calls `app_instance.reset_setting_colors_logic` to clear any visual indicators.
    9. Logs success or failure.

    Outputs of this function:
    - None. Modifies Tkinter variables.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Attempting to restore last used settings... Bringing back the old setup!",
                file=__file__,
                version=current_version,
                function=current_function)

    # Iterate through the setting_var_map and set each Tkinter variable
    # to its last used value from the LAST_USED_SETTINGS section.
    for tk_var_name, (last_key, default_key, tk_var_instance) in app_instance.setting_var_map.items():
        last_value_str = app_instance.config.get('LAST_USED_SETTINGS', last_key, fallback=None)
        if last_value_str is not None:
            try:
                # Convert to appropriate type based on Tkinter variable type
                if isinstance(tk_var_instance, tk.BooleanVar):
                    value = last_value_str.lower() == 'true'
                elif isinstance(tk_var_instance, tk.IntVar):
                    value = int(float(last_value_str)) # Handle floats stored as ints
                elif isinstance(tk_var_instance, tk.DoubleVar):
                    value = float(last_value_str)
                else: # tk.StringVar
                    value = last_value_str
                tk_var_instance.set(value)
                debug_log(f"Restored '{tk_var_name}' to last used '{value}'.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            except ValueError as e:
                error_msg = f"❌ Error converting last used value for '{tk_var_name}': {last_value_str} - {e}. Data type mismatch!"
                console_print_func(error_msg)
                debug_log(error_msg,
                            file=__file__,
                            version=current_version,
                            function=current_function)
            except Exception as e:
                error_msg = f"❌ An unexpected error occurred setting last used for '{tk_var_name}': {e}. This is a problem!"
                console_print_func(error_msg)
                debug_log(error_msg,
                            file=__file__,
                            version=current_version,
                            function=current_function)
        else:
            debug_log(f"No last used value found for '{tk_var_name}' in config. Skipping.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    # Special handling for notes_var and band_vars (not in setting_var_map)
    notes_from_config = app_instance.config.get('LAST_USED_SETTINGS', 'notes', fallback='')
    app_instance.notes_var.set(notes_from_config)
    debug_log(f"Restored notes: '{notes_from_config}'",
                file=__file__,
                version=current_version,
                function=current_function)

    # --- NEW/FIXED: Restore selected bands from config ---
    last_selected_bands_str = app_instance.config.get('LAST_USED_SETTINGS', 'last_scan_configuration__selected_bands', fallback='')
    last_selected_band_names = [name.strip() for name in last_selected_bands_str.split(',') if name.strip()]
    if last_selected_band_names:
        for band_item in app_instance.band_vars:
            band_name = band_item["band"]["Band Name"]
            band_item["var"].set(band_name in last_selected_band_names)
        debug_log(f"Restored selected bands to last used: {last_selected_band_names}. Bands loaded!",
                    file=__file__,
                    version=current_version,
                    function=current_function, special=True)
    else:
        # If no last_selected_bands in config, ensure all are deselected
        for band_item in app_instance.band_vars:
            band_item["var"].set(False) # Default to unchecked if no last used bands
        debug_log("No last_selected_bands in config.ini. All bands set to unchecked. Starting fresh!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    # Restore Antenna Type
    last_antenna_type = app_instance.config.get('LAST_USED_SETTINGS', 'antenna_type', fallback='')
    app_instance.selected_antenna_type_var.set(last_antenna_type)
    debug_log(f"Restored antenna type: '{last_antenna_type}'",
                file=__file__,
                version=current_version,
                function=current_function)

    # Restore Antenna Amplifier Type
    last_amplifier_type = app_instance.config.get('LAST_USED_SETTINGS', 'antenna_amplifier_type', fallback='')
    app_instance.selected_amplifier_type_var.set(last_amplifier_type)
    debug_log(f"Restored amplifier type: '{last_amplifier_type}'",
                file=__file__,
                version=current_version,
                function=current_function)

    # Restore Output Folder
    last_output_folder = app_instance.config.get('LAST_USED_SETTINGS', 'output_folder', fallback=os.path.join(os.getcwd(), 'scan_data'))
    app_instance.output_folder_var.set(last_output_folder)
    debug_log(f"Restored output folder: '{last_output_folder}'",
                file=__file__,
                version=current_version,
                function=current_function)

    # Restore Scan Name
    last_scan_name = app_instance.config.get('LAST_USED_SETTINGS', 'scan_name', fallback='New Scan')
    app_instance.scan_name_var.set(last_scan_name)
    debug_log(f"Restored scan name: '{last_scan_name}'",
                file=__file__,
                version=current_version,
                function=current_function)

    # Update sliders to reflect new last-used values
    if hasattr(app_instance, '_set_initial_slider_positions'):
        app_instance._set_initial_slider_positions() # Assuming this method exists and correctly updates sliders
        debug_log("Called _set_initial_slider_positions to update sliders. Sliders adjusted!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    else:
        debug_log("App instance does not have _set_initial_slider_positions method. Skipping slider update.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    # Reset setting colors (e.g., remove any "changed" highlights)
    if hasattr(app_instance, 'reset_setting_colors_logic'):
        app_instance.reset_setting_colors_logic()
    
    console_print_func("✅ All settings restored to last used values. Back in business!")
    debug_log("Last used settings restored. UI synced!",
                file=__file__,
                version=current_version,
                function=current_function,
                special=True)