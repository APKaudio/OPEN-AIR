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
# Version 20250813.005800.1
#
#
# Version 20250813.001600.3


import tkinter as tk
import inspect
import os
from datetime import datetime

from display.debug_logic import debug_log
from src.program_default_values import DEFAULT_CONFIG
from ref.frequency_bands import SCAN_BAND_RANGES

# --- Version Information ---
current_version = "20250813.005800.1"
current_version_hash = (20250813 * 5800 * 1)


def setup_tkinter_variables(app_instance):
    # Function Description
    # Initializes all Tkinter variables for the application by reading from the
    # DEFAULT_CONFIG dictionary and maps them for the config manager.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Setting up all application Tkinter variables from default config. Getting the gears in motion!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                function=current_function)

    app_instance.setting_var_map = {}

    for section, settings in DEFAULT_CONFIG.items():
        for key, value_str in settings.items():
            
            if key == 'last_scan_configuration__selected_bands_levels' or key == 'geometry':
                continue

            tk_var_instance = None
            
            # IMPROVED: Detect boolean values from 'true'/'false' as well as 'on'/'off'
            if value_str.lower() in ['true', 'false', 'on', 'off']:
                tk_var_instance = tk.BooleanVar(app_instance, value=(value_str.lower() in ['true', 'on']))
            elif key == 'paned_window_sash_position_percentage':
                try:
                    tk_var_instance = tk.IntVar(app_instance, value=int(float(value_str)))
                except ValueError:
                    tk_var_instance = tk.StringVar(app_instance, value=value_str)
            elif ('hz' in key or 'mhz' in key or 'db' in key or 'dbm' in key or 'cycles' in key or 'seconds' in key or key == 'span' or key == 'rbw' or 'width' in key or key == 'freq_shift') and value_str.replace('.', '', 1).replace('-', '', 1).isdigit():
                if '.' in value_str:
                    try:
                        tk_var_instance = tk.DoubleVar(app_instance, value=float(value_str))
                    except ValueError:
                        tk_var_instance = tk.StringVar(app_instance, value=value_str)
                else:
                    try:
                        tk_var_instance = tk.IntVar(app_instance, value=int(value_str))
                    except ValueError:
                        tk_var_instance = tk.StringVar(app_instance, value=value_str)
            else:
                tk_var_instance = tk.StringVar(app_instance, value=value_str)
            
            setattr(app_instance, f"{key}_var", tk_var_instance)
            app_instance.setting_var_map[key] = {'var': tk_var_instance, 'section': section, 'key': key}

    # --- Handle special, non-config variables, or variables whose values are managed differently ---
    app_instance.is_connected = tk.BooleanVar(app_instance, value=False)
    app_instance.connected_instrument_manufacturer = tk.StringVar(app_instance, value="")
    app_instance.connected_instrument_model = tk.StringVar(app_instance, value="")
    app_instance.connected_instrument_serial = tk.StringVar(app_instance, value="")
    app_instance.connected_instrument_version = tk.StringVar(app_instance, value="")
    app_instance.inst = None
    
    # Global Tkinter variables for displaying last loaded preset details
    app_instance.last_selected_preset_name_var = tk.StringVar(app_instance, value="None")
    app_instance.last_loaded_preset_center_freq_mhz_var = tk.StringVar(app_instance, value="N/A")
    app_instance.last_loaded_preset_span_mhz_var = tk.StringVar(app_instance, value="N/A")
    app_instance.last_loaded_preset_rbw_hz_var = tk.StringVar(app_instance, value="N/A")
    
    # Variables for instrument initialization that might not be in the config map
    app_instance.ref_level_dbm_var = tk.DoubleVar(app_instance, value=-20.0)
    app_instance.high_sensitivity_on_var = tk.BooleanVar(app_instance, value=False)
    app_instance.preamp_on_var = tk.BooleanVar(app_instance, value=False)
    # The following variables were causing a conflict. They should be created from the config file now.
    # app_instance.rbw_hz_var = tk.IntVar(app_instance, value=100000)
    # app_instance.vbw_hz_var = tk.IntVar(app_instance, value=100000)

    # Tkinter variables for displaying current instrument settings
    app_instance.current_center_freq_var = tk.StringVar(app_instance, value="N/A")
    app_instance.current_span_var = tk.StringVar(app_instance, value="N/A")
    app_instance.current_rbw_var = tk.StringVar(app_instance, value="N/A")
    app_instance.current_ref_level_var = tk.StringVar(app_instance, value="N/A")
    app_instance.current_trace_mode_var = tk.StringVar(app_instance, value="N/A")
    app_instance.current_preamp_status_var = tk.StringVar(app_instance, value="N/A")

    # --- Band Selection Variables ---
    app_instance.band_vars = []
    if SCAN_BAND_RANGES:
        for band in SCAN_BAND_RANGES:
            app_instance.band_vars.append({"band": band, "level": 0})
    
    debug_log(f"Finished setting up all Tkinter variables. The application's brain is now fully wired! ✅",
                file=f"{os.path.basename(__file__)} - {current_version}",
                function=current_function)