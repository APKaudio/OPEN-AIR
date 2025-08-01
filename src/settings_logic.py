# src/settings_logic.py
import tkinter as tk
import inspect
import os

# Import necessary functions/constants from utils
from utils.utils_instrument_control import debug_print
from src.config_manager import load_config, save_config # Import save_config

def restore_default_settings_logic(app_instance, console_print_func):
    """
    Restores all application settings to their default values as defined in config.ini.
    This function updates the Tkinter variables and then saves these defaults to
    the LAST_USED_SETTINGS section, effectively resetting the user's saved preferences.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__

    debug_print("Attempting to restore default settings...", file=current_file, function=current_function, console_print_func=console_print_func)

    # Iterate through the setting_var_map and set each Tkinter variable
    # to its default value from the DEFAULT_SETTINGS section.
    for tk_var_name, (last_key, default_key, tk_var_instance) in app_instance.setting_var_map.items():
        if default_key: # Only restore if a default_key is defined
            default_value_str = app_instance.config.get('DEFAULT_SETTINGS', default_key, fallback=None)
            if default_value_str is not None:
                try:
                    # Convert to appropriate type based on Tkinter variable type
                    if isinstance(tk_var_instance, tk.BooleanVar):
                        tk_var_instance.set(default_value_str.lower() == 'true')
                    elif isinstance(tk_var_instance, tk.IntVar):
                        tk_var_instance.set(int(float(default_value_str))) # Handle floats that are integers
                    elif isinstance(tk_var_instance, tk.DoubleVar):
                        tk_var_instance.set(float(default_value_str))
                    elif isinstance(tk_var_instance, tk.StringVar):
                        tk_var_instance.set(default_value_str)
                    debug_print(f"Set {tk_var_name} to default: '{default_value_str}'", file=current_file, function=current_function, console_print_func=console_print_func)
                except ValueError as e:
                    console_print_func(f"❌ Error converting default value for {tk_var_name}: {default_value_str} - {e}")
                    debug_print(f"Error converting default value for {tk_var_name}: {default_value_str} - {e}", file=current_file, function=current_function, console_print_func=console_print_func)
            else:
                debug_print(f"No default value found for {tk_var_name} in config.ini", file=current_file, function=current_function, console_print_func=console_print_func)
        else:
            debug_print(f"Skipping {tk_var_name}: No default_key defined in setting_var_map.", file=current_file, function=current_function, console_print_func=console_print_func)


    # Restore selected bands from default_selected_bands
    default_selected_bands_str = app_instance.config.get('DEFAULT_SETTINGS', 'default_selected_bands', fallback='')
    if default_selected_bands_str:
        default_selected_band_names = [name.strip() for name in default_selected_bands_str.split(',') if name.strip()]
        for band_item in app_instance.band_vars:
            band_item["var"].set(band_item["band"]["Band Name"] in default_selected_band_names)
        debug_print(f"Restored selected bands to default: {default_selected_band_names}", file=current_file, function=current_function, console_print_func=console_print_func)
    else:
        # If no default_selected_bands in config, ensure all are selected
        for band_item in app_instance.band_vars:
            band_item["var"].set(True) # Default to all checked if no default bands
        debug_print("No default_selected_bands in config.ini. All bands set to checked.", file=current_file, function=current_function, console_print_func=console_print_func)


    # Update sliders to reflect new default values
    # Assuming _set_initial_slider_positions handles all relevant Tkinter variables
    # and updates the associated slider widgets.
    if hasattr(app_instance, '_set_initial_slider_positions'):
        app_instance._set_initial_slider_positions()
        debug_print("Called _set_initial_slider_positions to update sliders.", file=current_file, function=current_function, console_print_func=console_print_func)
    else:
        debug_print("App instance does not have _set_initial_slider_positions method.", file=current_file, function=current_function, console_print_func=console_print_func)

    # Reset setting colors (e.g., remove any "changed" highlights)
    app_instance.reset_setting_colors_logic()

    # Save the restored default settings to LAST_USED_SETTINGS
    save_config(app_instance) # This will save the current state of Tkinter vars to LAST_USED_SETTINGS

    console_print_func("✅ All settings restored to defaults and saved.")
    debug_print("Default settings restored and saved.", file=current_file, function=current_function, console_print_func=console_print_func)


def restore_last_used_settings_logic(app_instance, console_print_func):
    """
    Restores all application settings to their last used values from config.ini.
    This function updates the Tkinter variables based on the 'LAST_USED_SETTINGS'
    section.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__

    debug_print("Attempting to restore last used settings...", file=current_file, function=current_function, console_print_func=console_print_func)

    # Iterate through the setting_var_map and set each Tkinter variable
    # to its last used value from the LAST_USED_SETTINGS section.
    for tk_var_name, (last_key, default_key, tk_var_instance) in app_instance.setting_var_map.items():
        if last_key: # Only restore if a last_key is defined
            last_value_str = app_instance.config.get('LAST_USED_SETTINGS', last_key, fallback=None)
            if last_value_str is not None:
                try:
                    # Convert to appropriate type based on Tkinter variable type
                    if isinstance(tk_var_instance, tk.BooleanVar):
                        tk_var_instance.set(last_value_str.lower() == 'true')
                    elif isinstance(tk_var_instance, tk.IntVar):
                        tk_var_instance.set(int(float(last_value_str))) # Handle floats that are integers
                    elif isinstance(tk_var_instance, tk.DoubleVar):
                        tk_var_instance.set(float(last_value_str))
                    elif isinstance(tk_var_instance, tk.StringVar):
                        tk_var_instance.set(last_value_str)
                    debug_print(f"Set {tk_var_name} to last used: '{last_value_str}'", file=current_file, function=current_function, console_print_func=console_print_func)
                except ValueError as e:
                    console_print_func(f"❌ Error converting last used value for {tk_var_name}: {last_value_str} - {e}")
                    debug_print(f"Error converting last used value for {tk_var_name}: {last_value_str} - {e}", file=current_file, function=current_function, console_print_func=console_print_func)
            else:
                debug_print(f"No last used value found for {tk_var_name} in config.ini", file=current_file, function=current_function, console_print_func=console_print_func)
        else:
            debug_print(f"Skipping {tk_var_name}: No last_key defined in setting_var_map.", file=current_file, function=current_function, console_print_func=console_print_func)

    # Restore selected bands from last_selected_bands
    last_selected_bands_str = app_instance.config.get('LAST_USED_SETTINGS', 'last_selected_bands', fallback='')
    if last_selected_bands_str:
        last_selected_band_names = [name.strip() for name in last_selected_bands_str.split(',') if name.strip()]
        for band_item in app_instance.band_vars:
            band_item["var"].set(band_item["band"]["Band Name"] in last_selected_band_names)
        debug_print(f"Restored selected bands to last used: {last_selected_band_names}", file=current_file, function=current_function, console_print_func=console_print_func)
    else:
        # If no last_selected_bands in config, ensure all are selected
        for band_item in app_instance.band_vars:
            band_item["var"].set(False) # Default to unchecked if no last used bands
        debug_print("No last_selected_bands in config.ini. All bands set to unchecked.", file=current_file, function=current_function, console_print_func=console_print_func)

    # Update sliders to reflect new last-used values
    if hasattr(app_instance, '_set_initial_slider_positions'):
        app_instance._set_initial_slider_positions() # Assuming this method exists and correctly updates sliders
        debug_print("Called _set_initial_slider_positions to update sliders.", file=current_file, function=current_function, console_print_func=console_print_func)
    else:
        debug_print("App instance does not have _set_initial_slider_positions method.", file=current_file, function=current_function, console_print_func=console_print_func)

    # Reset setting colors (e.g., remove any "changed" highlights)
    app_instance.reset_setting_colors_logic()
    
    console_print_func("✅ All settings restored to last used values.")
    debug_print("Last used settings restored.", file=current_file, function=current_function, console_print_func=console_print_func)