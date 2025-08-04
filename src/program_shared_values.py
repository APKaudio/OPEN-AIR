# src/program_shared_values.py
#
# This module centralizes the definition and initialization of all Tkinter variables
# used throughout the RF Spectrum Analyzer Controller application. It provides a
# single source for managing application-wide settings, instrument parameters,
# scan configurations, and plotting preferences.
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
# Version 20250803.234000.0 (REWRITTEN: Restored robust, nested dictionary processing to fix ImportError.)
# Version 20250803.204901.0 (REFACTORED: Removed trace callback creation to break circular import with config_manager.)
# Version 20250804.000004.0 (ADDED: Explicit initialization for global display Tkinter variables (last_loaded_preset_X).)
# Version 20250804.020800.1 (FIXED: Correctly populating app_instance.setting_var_map for all config values.)
# Version 20250804.021015.0 (FIXED: Added paned_window_sash_position_var to app_instance.setting_var_map.)
# Version 20250804.021100.1 (FIXED: Included last_config_save_time_var in app_instance variables for display.)
# Version 20250804.025000.0 (FIXED: Added initialization for current_X_var display variables for instrument settings.)
# Version 20250804.025800.0 (REMOVED: current_freq_shift_var initialization as per user request.)

current_version = "20250804.025800.0" # Incremented version

import tkinter as tk
import inspect
import os
from src.debug_logic import debug_log
from src.program_default_values import DEFAULT_CONFIG
from ref.frequency_bands import SCAN_BAND_RANGES


def setup_tkinter_variables(app_instance):
    # This function description tells me what this function does
    # Initializes all Tkinter variables for the application by reading from the
    # DEFAULT_CONFIG dictionary. It creates `tk.StringVar`, `tk.BooleanVar`,
    # `tk.IntVar`, or `tk.DoubleVar` instances as appropriate for each setting
    # and attaches them as attributes to the `app_instance` (e.g., `app_instance.scan_name_var`).
    # Crucially, it also populates `app_instance.setting_var_map` with a mapping
    # of each config key to its Tkinter variable instance and its corresponding
    # section in the configuration file. This map is used by `config_manager`
    # to save and load settings persistently. It also initializes special
    # application-wide variables like `is_connected` and `band_vars`.
    #
    # Inputs to this function
    #   app_instance (object): The main application instance (an instance of `App`),
    #                          to which all Tkinter variables will be attached as attributes.
    #
    # Process of this function
    #   1. Logs entry with debug information.
    #   2. Initializes `app_instance.setting_var_map` as an empty dictionary.
    #   3. Iterates through each `section` and `key-value` pair in `DEFAULT_CONFIG`.
    #   4. For each `key-value` pair, it determines the appropriate Tkinter variable type:
    #      - `tk.BooleanVar` if the value is 'true' or 'false' (case-insensitive).
    #      - `tk.IntVar` if the key contains 'Hz', 'cycles', or 'seconds' AND the value is numeric.
    #      - `tk.DoubleVar` if the value contains a decimal point.
    #      - `tk.StringVar` for all other cases.
    #   5. Creates the Tkinter variable instance with the `app_instance` as master
    #      and assigns the default `value`.
    #   6. Dynamically sets an attribute on `app_instance` using a convention
    #      (e.g., `app_instance.scan_name_var = tk.StringVar(...)`).
    #   7. Adds an entry to `app_instance.setting_var_map` in the format
    #      `{'config_key': (tk_var_instance, 'ConfigSection')}`.
    #   8. Initializes additional non-config-backed Tkinter variables like
    #      `is_connected`, `connected_instrument_model`, `inst`, and display variables
    #      for the last loaded preset.
    #   9. Populates `app_instance.band_vars` with `tk.BooleanVar` instances for each
    #      band defined in `SCAN_BAND_RANGES`, alongside their band data.
    #   10. Logs exit with debug information and the total count of variables set.
    #
    # Outputs of this function
    #   None. Modifies the `app_instance` by adding Tkinter variable attributes and populating `setting_var_map`.
    #
    # (2025-08-04.020800.1) Change: Refined variable type detection and corrected how setting_var_map is populated.
    # (2025-08-04.021015.0) Change: Added paned_window_sash_position_var to app_instance.setting_var_map.
    # (2025-08-04.021100.1) Change: Included last_config_save_time_var in app_instance variables for display.
    # (2025-08-04.025000.0) Change: Added initialization for current_X_var display variables for instrument settings.
    # (2025-08-04.025800.0) Change: Removed current_freq_shift_var initialization as per user request.
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Setting up all application Tkinter variables from default config. Getting the gears in motion!",
                file=os.path.basename(__file__), function=current_function, version=current_version)

    # Initialize the setting_var_map for use by config_manager.py
    # Format: {'config_key': (tk_var_instance, 'ConfigSection')}
    app_instance.setting_var_map = {}

    # Iterate through the nested default config dictionary to create variables
    for section, settings in DEFAULT_CONFIG.items():
        for key, value_str in settings.items():
            tk_var_instance = None
            
            # Special handling for 'geometry' as it's set directly on the root window
            if key == 'geometry':
                continue

            # Determine variable type and create Tkinter variable
            if value_str.lower() in ['true', 'false']:
                tk_var_instance = tk.BooleanVar(app_instance, value=(value_str.lower() == 'true'))
            elif key == 'paned_window_sash_position': # Explicitly handle sash position as an IntVar
                try:
                    tk_var_instance = tk.IntVar(app_instance, value=int(float(value_str)))
                except ValueError:
                    tk_var_instance = tk.StringVar(app_instance, value=value_str) # Fallback
            elif ('hz' in key or 'cycles' in key or 'seconds' in key or 'dbm' in key or key == 'span' or key == 'rbw' or 'width' in key or key == 'freq_shift') and value_str.replace('.', '', 1).replace('-', '', 1).isdigit(): # Added freq_shift, handle negative for dbm
                if '.' in value_str:
                    try:
                        tk_var_instance = tk.DoubleVar(app_instance, value=float(value_str))
                    except ValueError:
                        tk_var_instance = tk.StringVar(app_instance, value=value_str) # Fallback
                else:
                    try:
                        tk_var_instance = tk.IntVar(app_instance, value=int(float(value_str))) # Use float then int to handle "20.0"
                    except ValueError:
                        tk_var_instance = tk.StringVar(app_instance, value=value_str) # Fallback
            else: # Default to StringVar for everything else
                tk_var_instance = tk.StringVar(app_instance, value=value_str)
            
            # Dynamically set attribute on app_instance
            # Convention: config_key -> config_key_var (e.g., scan_name -> scan_name_var)
            setattr(app_instance, f"{key}_var", tk_var_instance)
            
            # Add to the setting_var_map for config saving/loading
            # Note: For 'last_config_save_time', we want it to be part of the map for loading,
            # but it's updated dynamically in save_config, not via UI input.
            app_instance.setting_var_map[key] = (tk_var_instance, section)

    # --- Handle special, non-config variables, or variables whose values are managed differently ---
    app_instance.is_connected = tk.BooleanVar(app_instance, value=False)
    app_instance.connected_instrument_model = tk.StringVar(app_instance, value="")
    app_instance.inst = None # This will hold the PyVISA instrument object
    
    # NEW: Global Tkinter variables for displaying last loaded preset details
    app_instance.last_selected_preset_name_var = tk.StringVar(app_instance, value="None")
    app_instance.last_loaded_preset_center_freq_mhz_var = tk.StringVar(app_instance, value="N/A")
    app_instance.last_loaded_preset_span_mhz_var = tk.StringVar(app_instance, value="N/A")
    app_instance.last_loaded_preset_rbw_hz_var = tk.StringVar(app_instance, value="N/A")

    # NEW: Tkinter variables for displaying current instrument settings (excluding freq_shift_var)
    app_instance.current_center_freq_var = tk.StringVar(app_instance, value="N/A")
    app_instance.current_span_var = tk.StringVar(app_instance, value="N/A")
    app_instance.current_rbw_var = tk.StringVar(app_instance, value="N/A")
    app_instance.current_ref_level_var = tk.StringVar(app_instance, value="N/A")
    # REMOVED: app_instance.current_freq_shift_var = tk.StringVar(app_instance, value="N/A")
    app_instance.current_trace_mode_var = tk.StringVar(app_instance, value="N/A")
    app_instance.current_preamp_status_var = tk.StringVar(app_instance, value="N/A")


    # --- Band Selection Variables ---
    # These are handled separately because they are a list of BooleanVars
    app_instance.band_vars = []
    if SCAN_BAND_RANGES:
        for band in SCAN_BAND_RANGES:
            # We explicitly want a BooleanVar for each band
            var = tk.BooleanVar(app_instance, value=False)
            app_instance.band_vars.append({"band": band, "var": var})
            # Note: Band selection state is saved/loaded manually in restore_settings_logic
            # not via setting_var_map directly.

    debug_log(f"Finished setting up {len(app_instance.setting_var_map)} Tkinter variables. The brain is fully operational! Version: {current_version}",
                file=os.path.basename(__file__), function=current_function, version=current_version)