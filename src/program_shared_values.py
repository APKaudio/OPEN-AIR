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
# Version 20250803.190500.1 (FIXED: Added last_config_save_time_var to prevent AttributeError.)
# Version 20250803.184500.0 (FIXED: AttributeError by initializing app_instance.inst to None.)
# Version 20250803.184400.0 (FIXED: Added all missing Tkinter variables for the Plotting Average tab.)
# Version 20250803.184200.0 (FIXED: Renamed plotting variables to match UI expectations.)
# Version 20250803.184100.1 (FIXED: NameError by defining current_function variable.)


import tkinter as tk
import inspect
import os
from src.debug_logic import debug_log
from src.settings_and_config.config_manager import save_config
from src.program_default_values import DEFAULT_CONFIG_SETTINGS
from ref.frequency_bands import SCAN_BAND_RANGES

current_version = "20250803.190500.1"

def str_to_bool(s):
    """Converts a string to a boolean."""
    return str(s).lower() in ('true', '1', 't', 'y', 'yes')

def create_trace_callback(app_instance, var_name):
    """Creates a callback function for Tkinter variable traces to save config."""
    def callback(*args):
        debug_log(f"Variable '{var_name}' changed. Saving config.", file=os.path.basename(__file__), function="trace_callback")
        save_config(app_instance.config, app_instance.CONFIG_FILE_PATH, app_instance.console_log_func, app_instance)
    return callback

def setup_tkinter_variables(app_instance):
    """Initializes all Tkinter variables for the application."""
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Setting up all application Tkinter variables.", file=os.path.basename(__file__), function=current_function)

    app_instance.setting_var_map = {}

    def add_variable(var_name, var_type, default_key, last_key):
        default_value = DEFAULT_CONFIG_SETTINGS.get(default_key)
        
        if var_type == tk.BooleanVar:
            var = var_type(app_instance, value=str_to_bool(default_value))
        elif var_type == tk.IntVar:
            var = var_type(app_instance, value=int(float(default_value)))
        elif var_type == tk.DoubleVar:
            var = var_type(app_instance, value=float(default_value))
        else: # Default to StringVar
            var = tk.StringVar(app_instance, value=default_value)
            
        setattr(app_instance, var_name, var)
        var.trace_add("write", create_trace_callback(app_instance, var_name))
        app_instance.setting_var_map[var_name] = (last_key, default_key, var)

    # --- GLOBAL SETTINGS ---
    add_variable("general_debug_enabled_var", tk.BooleanVar, 'default_GLOBAL__debug_enabled', 'last_GLOBAL__debug_enabled')
    add_variable("log_visa_commands_enabled_var", tk.BooleanVar, 'default_GLOBAL__log_visa_commands_enabled', 'last_GLOBAL__log_visa_commands_enabled')
    add_variable("paned_window_sash_position_var", tk.IntVar, 'default_GLOBAL__paned_window_sash_position', 'last_GLOBAL__paned_window_sash_position')
    add_variable("debug_to_terminal_var", tk.BooleanVar, 'default_GLOBAL__debug_to_Terminal', 'last_GLOBAL__debug_to_Terminal')
    add_variable("debug_to_file_var", tk.BooleanVar, 'default_GLOBAL__debug_to_file', 'last_GLOBAL__debug_to_file')
    add_variable("include_console_messages_to_debug_file_var", tk.BooleanVar, 'default_GLOBAL__include_console_messages_to_debug_file', 'last_GLOBAL__include_console_messages_to_debug_file')
    add_variable("debug_to_gui_console_var", tk.BooleanVar, 'default_GLOBAL__debug_to_gui_console', 'last_GLOBAL__debug_to_gui_console')
    add_variable("last_config_save_time_var", tk.StringVar, 'default_GLOBAL__last_config_save_time', 'last_GLOBAL__last_config_save_time')

    # --- INSTRUMENT CONNECTION ---
    add_variable("visa_resource_var", tk.StringVar, 'default_instrument_connection__visa_resource', 'last_instrument_connection__visa_resource')
    app_instance.is_connected = tk.BooleanVar(app_instance, value=False)
    app_instance.connected_instrument_model = tk.StringVar(app_instance, value="")
    app_instance.inst = None

    # --- SCAN CONFIGURATION ---
    add_variable("scan_name_var", tk.StringVar, 'default_scan_configuration__scan_name', 'last_scan_configuration__scan_name')
    add_variable("output_folder_var", tk.StringVar, 'default_scan_configuration__scan_directory', 'last_scan_configuration__scan_directory')
    add_variable("num_scan_cycles_var", tk.IntVar, 'default_scan_configuration__num_scan_cycles', 'last_scan_configuration__num_scan_cycles')
    add_variable("rbw_step_size_hz_var", tk.DoubleVar, 'default_scan_configuration__rbw_step_size_hz', 'last_scan_configuration__rbw_step_size_hz')
    add_variable("cycle_wait_time_seconds_var", tk.DoubleVar, 'default_scan_configuration__cycle_wait_time_seconds', 'last_scan_configuration__cycle_wait_time_seconds')
    add_variable("maxhold_time_seconds_var", tk.DoubleVar, 'default_scan_configuration__maxhold_time_seconds', 'last_scan_configuration__maxhold_time_seconds')
    add_variable("scan_rbw_hz_var", tk.DoubleVar, 'default_scan_configuration__scan_rbw_hz', 'last_scan_configuration__scan_rbw_hz')
    add_variable("reference_level_dbm_var", tk.DoubleVar, 'default_scan_configuration__reference_level_dbm', 'last_scan_configuration__reference_level_dbm')
    add_variable("freq_shift_var", tk.DoubleVar, 'default_scan_configuration__freq_shift_hz', 'last_scan_configuration__freq_shift_hz')
    add_variable("maxhold_enabled_var", tk.BooleanVar, 'default_scan_configuration__maxhold_enabled', 'last_scan_configuration__maxhold_enabled')
    add_variable("high_sensitivity_var", tk.BooleanVar, 'default_scan_configuration__sensitivity', 'last_scan_configuration__sensitivity')
    add_variable("preamp_on_var", tk.BooleanVar, 'default_scan_configuration__preamp_on', 'last_scan_configuration__preamp_on')
    add_variable("scan_rbw_segmentation_var", tk.DoubleVar, 'default_scan_configuration__scan_rbw_segmentation', 'last_scan_configuration__scan_rbw_segmentation')
    add_variable("desired_default_focus_width_var", tk.DoubleVar, 'default_scan_configuration__default_focus_width', 'last_scan_configuration__default_focus_width')
    add_variable("scan_mode_var", tk.StringVar, 'default_scan_configuration__scan_mode', 'last_scan_configuration__scan_mode')

    # --- SCAN META DATA SETTINGS ---
    add_variable("operator_name_var", tk.StringVar, 'default_scan_meta_data__operator_name', 'last_scan_meta_data__operator_name')
    add_variable("operator_contact_var", tk.StringVar, 'default_scan_meta_data__contact', 'last_scan_meta_data__contact')
    add_variable("venue_name_var", tk.StringVar, 'default_scan_meta_data__name', 'last_scan_meta_data__name')
    add_variable("venue_postal_code_var", tk.StringVar, 'default_scan_meta_data__venue_postal_code', 'last_scan_meta_data__venue_postal_code')
    add_variable("address_field_var", tk.StringVar, 'default_scan_meta_data__address_field', 'last_scan_meta_data__address_field')
    add_variable("city_var", tk.StringVar, 'default_scan_meta_data__city', 'last_scan_meta_data__city')
    add_variable("province_var", tk.StringVar, 'default_scan_meta_data__province', 'last_scan_meta_data__province')
    add_variable("scanner_type_var", tk.StringVar, 'default_scan_meta_data__scanner_type', 'last_scan_meta_data__scanner_type')
    add_variable("selected_antenna_type_var", tk.StringVar, 'default_scan_meta_data__selected_antenna_type', 'last_scan_meta_data__selected_antenna_type')
    add_variable("antenna_description_var", tk.StringVar, 'default_scan_meta_data__antenna_description', 'last_scan_meta_data__antenna_description')
    add_variable("antenna_use_var", tk.StringVar, 'default_scan_meta_data__antenna_use', 'last_scan_meta_data__antenna_use')
    add_variable("antenna_mount_var", tk.StringVar, 'default_scan_meta_data__antenna_mount', 'last_scan_meta_data__antenna_mount')
    add_variable("selected_amplifier_type_var", tk.StringVar, 'default_scan_meta_data__selected_amplifier_type', 'last_scan_meta_data__selected_amplifier_type')
    add_variable("antenna_amplifier_var", tk.StringVar, 'default_scan_meta_data__antenna_amplifier', 'last_scan_meta_data__antenna_amplifier')
    add_variable("amplifier_description_var", tk.StringVar, 'default_scan_meta_data__amplifier_description', 'last_scan_meta_data__amplifier_description')
    add_variable("amplifier_use_var", tk.StringVar, 'default_scan_meta_data__amplifier_use', 'last_scan_meta_data__amplifier_use')
    add_variable("notes_var", tk.StringVar, 'default_scan_meta_data__notes', 'last_scan_meta_data__notes')
    
    # --- PLOTTING (SINGLE SCAN) ---
    add_variable("include_gov_markers_var", tk.BooleanVar, 'default_plotting__scan_markers_to_plot__include_gov_markers', 'last_plotting__scan_markers_to_plot__include_gov_markers')
    add_variable("include_tv_markers_var", tk.BooleanVar, 'default_plotting__scan_markers_to_plot__include_tv_markers', 'last_plotting__scan_markers_to_plot__include_tv_markers')
    add_variable("include_markers_var", tk.BooleanVar, 'default_plotting__scan_markers_to_plot__include_markers', 'last_plotting__scan_markers_to_plot__include_markers')
    add_variable("include_scan_intermod_markers_var", tk.BooleanVar, 'default_plotting__scan_markers_to_plot__include_intermod_markers', 'last_plotting__scan_markers_to_plot__include_intermod_markers')
    add_variable("open_html_after_complete_var", tk.BooleanVar, 'default_plotting__scan_markers_to_plot__open_html_after_complete', 'last_plotting__scan_markers_to_plot__open_html_after_complete')
    add_variable("create_html_var", tk.BooleanVar, 'default_plotting__scan_markers_to_plot__create_html', 'last_plotting__scan_markers_to_plot__create_html')

    # --- PLOTTING (AVERAGE) ---
    add_variable("avg_include_gov_markers_var", tk.BooleanVar, 'default_plotting__average_markers_to_plot__include_gov_markers', 'last_plotting__average_markers_to_plot__include_gov_markers')
    add_variable("avg_include_tv_markers_var", tk.BooleanVar, 'default_plotting__average_markers_to_plot__include_tv_markers', 'last_plotting__average_markers_to_plot__include_tv_markers')
    add_variable("avg_include_markers_var", tk.BooleanVar, 'default_plotting__average_markers_to_plot__include_markers', 'last_plotting__average_markers_to_plot__include_markers')
    add_variable("avg_include_intermod_markers_var", tk.BooleanVar, 'default_plotting__average_markers_to_plot__include_intermod_markers', 'last_plotting__average_markers_to_plot__include_intermod_markers')
    add_variable("math_average_var", tk.BooleanVar, 'default_plotting__average_markers_to_plot__math_average', 'last_plotting__average_markers_to_plot__math_average')
    add_variable("math_median_var", tk.BooleanVar, 'default_plotting__average_markers_to_plot__math_median', 'last_plotting__average_markers_to_plot__math_median')
    add_variable("math_range_var", tk.BooleanVar, 'default_plotting__average_markers_to_plot__math_range', 'last_plotting__average_markers_to_plot__math_range')
    add_variable("math_standard_deviation_var", tk.BooleanVar, 'default_plotting__average_markers_to_plot__math_standard_deviation', 'last_plotting__average_markers_to_plot__math_standard_deviation')
    add_variable("math_variance_var", tk.BooleanVar, 'default_plotting__average_markers_to_plot__math_variance', 'last_plotting__average_markers_to_plot__math_variance')
    add_variable("math_psd_var", tk.BooleanVar, 'default_plotting__average_markers_to_plot__math_psd', 'last_plotting__average_markers_to_plot__math_psd')

    # --- BAND SELECTION VARIABLES ---
    app_instance.band_vars = []
    for band in SCAN_BAND_RANGES:
        var = tk.BooleanVar(app_instance, value=False)
        app_instance.band_vars.append({"band": band, "var": var})

    debug_log(f"Finished setting up Tkinter variables. The brain is fully operational! Version: {current_version}", file=os.path.basename(__file__), function=current_function)
