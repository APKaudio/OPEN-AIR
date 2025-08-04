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
# application can benegotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250803.234000.0 (REWRITTEN: Restored robust, nested dictionary processing to fix ImportError.)
# Version 20250803.204901.0 (REFACTORED: Removed trace callback creation to break circular import with config_manager.)
# Version 20250804.000004.0 (ADDED: Explicit initialization for global display Tkinter variables (last_loaded_preset_X).)

import tkinter as tk
import inspect
import os
from src.debug_logic import debug_log
from src.program_default_values import DEFAULT_CONFIG
from ref.frequency_bands import SCAN_BAND_RANGES

current_version = "20250804.000004.0" # Incremented version

def setup_tkinter_variables(app_instance):
    """Initializes all Tkinter variables for the application from the default config."""
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Setting up all application Tkinter variables from default config.", file=os.path.basename(__file__), function=current_function)

    app_instance.setting_var_map = {}

    # Iterate through the nested default config dictionary to create variables
    for section, settings in DEFAULT_CONFIG.items():
        for key, value in settings.items():
            # Determine variable type based on common conventions or explicit checks
            if value.lower() in ['true', 'false']:
                var = tk.BooleanVar(app_instance, value=(value.lower() == 'true'), name=f"{section}_{key}")
            else:
                var = tk.StringVar(app_instance, value=value, name=f"{section}_{key}")
            
            # Store the variable on the app_instance (e.g., app_instance.geometry_var)
            setattr(app_instance, f"{key}_var", var)
            
            # Map the key to its variable and section for saving later
            app_instance.setting_var_map[key] = (var, section)

    # --- Handle special, non-config variables ---
    app_instance.is_connected = tk.BooleanVar(app_instance, value=False)
    app_instance.connected_instrument_model = tk.StringVar(app_instance, value="")
    app_instance.inst = None # This will hold the PyVISA instrument object
    
    # NEW: Global Tkinter variables for displaying last loaded preset details
    app_instance.last_selected_preset_name_var = tk.StringVar(app_instance, value="None")
    app_instance.last_loaded_preset_center_freq_mhz_var = tk.StringVar(app_instance, value="N/A")
    app_instance.last_loaded_preset_span_mhz_var = tk.StringVar(app_instance, value="N/A")
    app_instance.last_loaded_preset_rbw_hz_var = tk.StringVar(app_instance, value="N/A")

    # --- Band Selection Variables ---
    app_instance.band_vars = []
    if SCAN_BAND_RANGES:
        for band in SCAN_BAND_RANGES:
            var = tk.BooleanVar(app_instance, value=False)
            app_instance.band_vars.append({"band": band, "var": var})

    debug_log(f"Finished setting up {len(app_instance.setting_var_map)} Tkinter variables. The brain is fully operational! Version: {current_version}", file=os.path.basename(__file__), function=current_function)