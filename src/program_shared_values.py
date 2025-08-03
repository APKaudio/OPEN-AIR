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
# Version 20250803.1430.0 (Initial creation: Centralized data directory creation, config loading, and debug setup.)
# Version 20250803.1440.0 (FIXED: AttributeError: 'function' object has no attribute '_write_to_debug_file' by correcting reference to debug_logic_module._write_to_debug_file.)
# Version 20250803.1445.0 (Moved _setup_tkinter_vars content from main_app.py to a new function: setup_tkinter_variables.)
# Version 20250803.1450.0 (Moved setup_tkinter_variables from program_initialization.py to this file.)
# Version 20250803.1845.0 (FIXED: AttributeError: '_tkinter.tkapp' object has no attribute 'band_vars' by initializing band_vars.)
# Version 20250803.1850.0 (FIXED: ImportError for 'create_trace_callback' by moving it to top-level.)

import tkinter as tk
import inspect
import os # For os.path.basename
from src.debug_logic import debug_log # Import debug_log
import src.debug_logic as debug_logic_module # Alias for direct access to module functions
from src.console_logic import console_log # Import console_log
from src.program_default_values import DEFAULT_CONFIG_SETTINGS # Import default settings
from ref.frequency_bands import SCAN_BAND_RANGES # Import SCAN_BAND_RANGES

current_version = "20250803.1850.0" # this variable should always be defined below the header to make the debugging better

def str_to_bool(s):
    """Converts a string to a boolean."""
    return s.lower() in ('true', '1', 't', 'y', 'yes')

def create_trace_callback(app_instance, var_name):
    """
    Creates a callback function for Tkinter variable traces to save config.
    This function is now a top-level function.
    """
    def callback(*args):
        # This import needs to be here to avoid circular dependency
        from src.settings_and_config.config_manager import save_config
        debug_log(f"Tkinter variable '{var_name}' changed to {app_instance.setting_var_map[var_name][2].get()}. Triggering config save. Version: {current_version}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name) # Use inspect for current function
        save_config(app_instance.config, app_instance.CONFIG_FILE_PATH, console_log, app_instance)
    return callback


def setup_tkinter_variables(app_instance):
    """
    Initializes all Tkinter variables for the application and attaches them
    to the main application instance. This function is called once during
    application startup.

    Inputs:
        app_instance (object): The main application instance (tk.Tk).

    Process of this function:
        1. Initializes various Tkinter variables (StringVar, BooleanVar, DoubleVar, IntVar)
           for global settings, instrument parameters, scan configurations, and plotting.
        2. Sets their initial values based on `DEFAULT_CONFIG_SETTINGS` or hardcoded defaults.
        3. Attaches these variables as attributes to `app_instance`.
        4. Sets up trace callbacks for variables that need to trigger configuration saves.
        5. Initializes `app_instance.band_vars` with BooleanVars for each scan band.

    Outputs of this function:
        None. Modifies the `app_instance` in place.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Setting up Tkinter variables. Preparing the application's brain! Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    # Dictionary to map setting keys to their Tkinter variables and default values
    # This is used by config_manager to load/save settings
    app_instance.setting_var_map = {}

    # --- GLOBAL SETTINGS ---
    app_instance.general_debug_enabled_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('GLOBAL__debug_enabled', 'False')))
    app_instance.general_debug_enabled_var.trace_add("write", create_trace_callback(app_instance, "general_debug_enabled_var"))
    app_instance.setting_var_map['general_debug_enabled_var'] = ('last_GLOBAL__debug_enabled', 'GLOBAL__debug_enabled', app_instance.general_debug_enabled_var)

    app_instance.log_visa_commands_enabled_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('GLOBAL__log_visa_commands_enabled', 'False')))
    app_instance.log_visa_commands_enabled_var.trace_add("write", create_trace_callback(app_instance, "log_visa_commands_enabled_var"))
    app_instance.setting_var_map['log_visa_commands_enabled_var'] = ('last_GLOBAL__log_visa_commands_enabled', 'GLOBAL__log_visa_commands_enabled', app_instance.log_visa_commands_enabled_var)

    app_instance.paned_window_sash_position_var = tk.IntVar(app_instance, value=int(DEFAULT_CONFIG_SETTINGS.get('GLOBAL__paned_window_sash_position', '700')))
    app_instance.paned_window_sash_position_var.trace_add("write", create_trace_callback(app_instance, "paned_window_sash_position_var"))
    app_instance.setting_var_map['paned_window_sash_position_var'] = ('last_GLOBAL__paned_window_sash_position', 'GLOBAL__paned_window_sash_position', app_instance.paned_window_sash_position_var)

    app_instance.debug_to_terminal_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('GLOBAL__debug_to_terminal', 'False')))
    app_instance.debug_to_terminal_var.trace_add("write", create_trace_callback(app_instance, "debug_to_terminal_var"))
    app_instance.setting_var_map['debug_to_terminal_var'] = ('last_GLOBAL__debug_to_terminal', 'GLOBAL__debug_to_terminal', app_instance.debug_to_terminal_var)

    app_instance.debug_to_file_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('GLOBAL__debug_to_file', 'True')))
    app_instance.debug_to_file_var.trace_add("write", create_trace_callback(app_instance, "debug_to_file_var"))
    app_instance.setting_var_map['debug_to_file_var'] = ('last_GLOBAL__debug_to_file', 'GLOBAL__debug_to_file', app_instance.debug_to_file_var)

    app_instance.include_console_messages_to_debug_file_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('GLOBAL__include_console_messages_to_debug_file', 'True')))
    app_instance.include_console_messages_to_debug_file_var.trace_add("write", create_trace_callback(app_instance, "include_console_messages_to_debug_file_var"))
    app_instance.setting_var_map['include_console_messages_to_debug_file_var'] = ('last_GLOBAL__include_console_messages_to_debug_file', 'GLOBAL__include_console_messages_to_debug_file', app_instance.include_console_messages_to_debug_file_var)

    app_instance.debug_to_gui_console_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('GLOBAL__debug_to_gui_console', 'True')))
    app_instance.debug_to_gui_console_var.trace_add("write", create_trace_callback(app_instance, "debug_to_gui_console_var"))
    app_instance.setting_var_map['debug_to_gui_console_var'] = ('last_GLOBAL__debug_to_gui_console', 'GLOBAL__debug_to_gui_console', app_instance.debug_to_gui_console_var)


    # --- INSTRUMENT CONNECTION SETTINGS ---
    app_instance.visa_resource_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('instrument_connection__visa_resource', 'N/A'))
    app_instance.visa_resource_var.trace_add("write", create_trace_callback(app_instance, "visa_resource_var"))
    app_instance.setting_var_map['visa_resource_var'] = ('last_instrument_connection__visa_resource', 'instrument_connection__visa_resource', app_instance.visa_resource_var)

    app_instance.is_connected = tk.BooleanVar(app_instance, value=False) # Not saved to config, reflects current state
    app_instance.connected_instrument_model = tk.StringVar(app_instance, value="") # Not saved to config, reflects current state

    # --- SCAN CONFIGURATION SETTINGS ---
    app_instance.scan_name_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('scan_configuration__scan_name', 'ThisIsMyScan'))
    app_instance.scan_name_var.trace_add("write", create_trace_callback(app_instance, "scan_name_var"))
    app_instance.setting_var_map['scan_name_var'] = ('last_scan_configuration__scan_name', 'scan_configuration__scan_name', app_instance.scan_name_var)

    app_instance.output_folder_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('scan_configuration__scan_directory', 'scan_data'))
    app_instance.output_folder_var.trace_add("write", create_trace_callback(app_instance, "output_folder_var"))
    app_instance.setting_var_map['output_folder_var'] = ('last_scan_configuration__scan_directory', 'scan_configuration__scan_directory', app_instance.output_folder_var)

    app_instance.num_scan_cycles_var = tk.IntVar(app_instance, value=int(DEFAULT_CONFIG_SETTINGS.get('scan_configuration__num_scan_cycles', '1')))
    app_instance.num_scan_cycles_var.trace_add("write", create_trace_callback(app_instance, "num_scan_cycles_var"))
    app_instance.setting_var_map['num_scan_cycles_var'] = ('last_scan_configuration__num_scan_cycles', 'scan_configuration__num_scan_cycles', app_instance.num_scan_cycles_var)

    app_instance.rbw_step_size_hz_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG_SETTINGS.get('scan_configuration__rbw_step_size_hz', '10000')))
    app_instance.rbw_step_size_hz_var.trace_add("write", create_trace_callback(app_instance, "rbw_step_size_hz_var"))
    app_instance.setting_var_map['rbw_step_size_hz_var'] = ('last_scan_configuration__rbw_step_size_hz', 'scan_configuration__rbw_step_size_hz', app_instance.rbw_step_size_hz_var)

    app_instance.cycle_wait_time_seconds_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG_SETTINGS.get('scan_configuration__cycle_wait_time_seconds', '0.5')))
    app_instance.cycle_wait_time_seconds_var.trace_add("write", create_trace_callback(app_instance, "cycle_wait_time_seconds_var"))
    app_instance.setting_var_map['cycle_wait_time_seconds_var'] = ('last_scan_configuration__cycle_wait_time_seconds', 'scan_configuration__cycle_wait_time_seconds', app_instance.cycle_wait_time_seconds_var)

    app_instance.maxhold_time_seconds_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG_SETTINGS.get('scan_configuration__maxhold_time_seconds', '3')))
    app_instance.maxhold_time_seconds_var.trace_add("write", create_trace_callback(app_instance, "maxhold_time_seconds_var"))
    app_instance.setting_var_map['maxhold_time_seconds_var'] = ('last_scan_configuration__maxhold_time_seconds', 'scan_configuration__maxhold_time_seconds', app_instance.maxhold_time_seconds_var)

    app_instance.scan_rbw_hz_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG_SETTINGS.get('scan_configuration__scan_rbw_hz', '10000')))
    app_instance.scan_rbw_hz_var.trace_add("write", create_trace_callback(app_instance, "scan_rbw_hz_var"))
    app_instance.setting_var_map['scan_rbw_hz_var'] = ('last_scan_configuration__scan_rbw_hz', 'scan_configuration__scan_rbw_hz', app_instance.scan_rbw_hz_var)

    app_instance.reference_level_dbm_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG_SETTINGS.get('scan_configuration__reference_level_dbm', '-40')))
    app_instance.reference_level_dbm_var.trace_add("write", create_trace_callback(app_instance, "reference_level_dbm_var"))
    app_instance.setting_var_map['reference_level_dbm_var'] = ('last_scan_configuration__reference_level_dbm', 'scan_configuration__reference_level_dbm', app_instance.reference_level_dbm_var)

    app_instance.freq_shift_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG_SETTINGS.get('scan_configuration__freq_shift_hz', '0')))
    app_instance.freq_shift_var.trace_add("write", create_trace_callback(app_instance, "freq_shift_var"))
    app_instance.setting_var_map['freq_shift_var'] = ('last_scan_configuration__freq_shift_hz', 'scan_configuration__freq_shift_hz', app_instance.freq_shift_var)

    app_instance.maxhold_enabled_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('scan_configuration__maxhold_enabled', 'True')))
    app_instance.maxhold_enabled_var.trace_add("write", create_trace_callback(app_instance, "maxhold_enabled_var"))
    app_instance.setting_var_map['maxhold_enabled_var'] = ('last_scan_configuration__maxhold_enabled', 'scan_configuration__maxhold_enabled', app_instance.maxhold_enabled_var)

    app_instance.high_sensitivity_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('scan_configuration__sensitivity', 'True')))
    app_instance.high_sensitivity_var.trace_add("write", create_trace_callback(app_instance, "high_sensitivity_var"))
    app_instance.setting_var_map['high_sensitivity_var'] = ('last_scan_configuration__sensitivity', 'scan_configuration__sensitivity', app_instance.high_sensitivity_var)

    app_instance.preamp_on_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('scan_configuration__preamp_on', 'True')))
    app_instance.preamp_on_var.trace_add("write", create_trace_callback(app_instance, "preamp_on_var"))
    app_instance.setting_var_map['preamp_on_var'] = ('last_scan_configuration__preamp_on', 'scan_configuration__preamp_on', app_instance.preamp_on_var)

    app_instance.scan_rbw_segmentation_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG_SETTINGS.get('scan_configuration__scan_rbw_segmentation', '1000000.0')))
    app_instance.scan_rbw_segmentation_var.trace_add("write", create_trace_callback(app_instance, "scan_rbw_segmentation_var"))
    app_instance.setting_var_map['scan_rbw_segmentation_var'] = ('last_scan_configuration__scan_rbw_segmentation', 'scan_configuration__scan_rbw_segmentation', app_instance.scan_rbw_segmentation_var)

    app_instance.desired_default_focus_width_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG_SETTINGS.get('scan_configuration__default_focus_width', '10000')))
    app_instance.desired_default_focus_width_var.trace_add("write", create_trace_callback(app_instance, "desired_default_focus_width_var"))
    app_instance.setting_var_map['desired_default_focus_width_var'] = ('last_scan_configuration__default_focus_width', 'scan_configuration__default_focus_width', app_instance.desired_default_focus_width_var)

    app_instance.scan_mode_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('scan_configuration__scan_mode', 'SWEEP'))
    app_instance.scan_mode_var.trace_add("write", create_trace_callback(app_instance, "scan_mode_var"))
    app_instance.setting_var_map['scan_mode_var'] = ('last_scan_configuration__scan_mode', 'scan_configuration__scan_mode', app_instance.scan_mode_var)

    # --- SCAN META DATA SETTINGS ---
    app_instance.operator_name_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('scan_meta_data__operator_name', 'Anthony P. Kuzub'))
    app_instance.operator_name_var.trace_add("write", create_trace_callback(app_instance, "operator_name_var"))
    app_instance.setting_var_map['operator_name_var'] = ('last_scan_meta_data__operator_name', 'scan_meta_data__operator_name', app_instance.operator_name_var)

    app_instance.venue_name_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('scan_meta_data__venue_name', 'The Opera House'))
    app_instance.venue_name_var.trace_add("write", create_trace_callback(app_instance, "venue_name_var"))
    app_instance.setting_var_map['venue_name_var'] = ('last_scan_meta_data__venue_name', 'scan_meta_data__venue_name', app_instance.venue_name_var)

    app_instance.venue_address_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('scan_meta_data__venue_address', '735 Queen Street East'))
    app_instance.venue_address_var.trace_add("write", create_trace_callback(app_instance, "venue_address_var"))
    app_instance.setting_var_map['venue_address_var'] = ('last_scan_meta_data__venue_address', 'scan_meta_data__venue_address', app_instance.venue_address_var)

    app_instance.venue_city_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('scan_meta_data__venue_city', 'Toronto'))
    app_instance.venue_city_var.trace_add("write", create_trace_callback(app_instance, "venue_city_var"))
    app_instance.setting_var_map['venue_city_var'] = ('last_scan_meta_data__venue_city', 'scan_meta_data__venue_city', app_instance.venue_city_var)

    app_instance.venue_province_state_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('scan_meta_data__venue_province_state', 'Ontario'))
    app_instance.venue_province_state_var.trace_add("write", create_trace_callback(app_instance, "venue_province_state_var"))
    app_instance.setting_var_map['venue_province_state_var'] = ('last_scan_meta_data__venue_province_state', 'scan_meta_data__venue_province_state', app_instance.venue_province_state_var)

    app_instance.venue_postal_zip_code_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('scan_meta_data__venue_postal_zip_code', 'M4M 1H1'))
    app_instance.venue_postal_zip_code_var.trace_add("write", create_trace_callback(app_instance, "venue_postal_zip_code_var"))
    app_instance.setting_var_map['venue_postal_zip_code_var'] = ('last_scan_meta_data__venue_postal_zip_code', 'scan_meta_data__venue_postal_zip_code', app_instance.venue_postal_zip_code_var)

    app_instance.venue_country_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('scan_meta_data__venue_country', 'Canada'))
    app_instance.venue_country_var.trace_add("write", create_trace_callback(app_instance, "venue_country_var"))
    app_instance.setting_var_map['venue_country_var'] = ('last_scan_meta_data__venue_country', 'scan_meta_data__venue_country', app_instance.venue_country_var)

    app_instance.antenna_type_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('scan_meta_data__antenna_type', 'Omnidirectional (Dipole)'))
    app_instance.antenna_type_var.trace_add("write", create_trace_callback(app_instance, "antenna_type_var"))
    app_instance.setting_var_map['antenna_type_var'] = ('last_scan_meta_data__antenna_type', 'scan_meta_data__antenna_type', app_instance.antenna_type_var)

    app_instance.antenna_description_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('scan_meta_data__antenna_description', ''))
    app_instance.antenna_description_var.trace_add("write", create_trace_callback(app_instance, "antenna_description_var"))
    app_instance.setting_var_map['antenna_description_var'] = ('last_scan_meta_data__antenna_description', 'scan_meta_data__antenna_description', app_instance.antenna_description_var)

    app_instance.antenna_use_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('scan_meta_data__antenna_use', ''))
    app_instance.antenna_use_var.trace_add("write", create_trace_callback(app_instance, "antenna_use_var"))
    app_instance.setting_var_map['antenna_use_var'] = ('last_scan_meta_data__antenna_use', 'scan_meta_data__antenna_use', app_instance.antenna_use_var)

    app_instance.amplifier_type_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('scan_meta_data__amplifier_type', 'In-line Amplifier (Line Amplifier)'))
    app_instance.amplifier_type_var.trace_add("write", create_trace_callback(app_instance, "amplifier_type_var"))
    app_instance.setting_var_map['amplifier_type_var'] = ('last_scan_meta_data__amplifier_type', 'scan_meta_data__amplifier_type', app_instance.amplifier_type_var)

    app_instance.amplifier_description_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('scan_meta_data__amplifier_description', ''))
    app_instance.amplifier_description_var.trace_add("write", create_trace_callback(app_instance, "amplifier_description_var"))
    app_instance.setting_var_map['amplifier_description_var'] = ('last_scan_meta_data__amplifier_description', 'scan_meta_data__amplifier_description', app_instance.amplifier_description_var)

    app_instance.amplifier_use_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('scan_meta_data__amplifier_use', ''))
    app_instance.amplifier_use_var.trace_add("write", create_trace_callback(app_instance, "amplifier_use_var"))
    app_instance.setting_var_map['amplifier_use_var'] = ('last_scan_meta_data__amplifier_use', 'scan_meta_data__amplifier_use', app_instance.amplifier_use_var)

    app_instance.notes_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('scan_meta_data__notes', ''))
    app_instance.notes_var.trace_add("write", create_trace_callback(app_instance, "notes_var"))
    app_instance.setting_var_map['notes_var'] = ('last_scan_meta_data__notes', 'scan_meta_data__notes', app_instance.notes_var)

    # --- PLOTTING SETTINGS (SCAN MARKERS) ---
    app_instance.plot_scan_gov_markers_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('plotting__scan_markers_to_plot__include_gov_markers', 'True')))
    app_instance.plot_scan_gov_markers_var.trace_add("write", create_trace_callback(app_instance, "plot_scan_gov_markers_var"))
    app_instance.setting_var_map['plot_scan_gov_markers_var'] = ('last_plotting__scan_markers_to_plot__include_gov_markers', 'plotting__scan_markers_to_plot__include_gov_markers', app_instance.plot_scan_gov_markers_var)

    app_instance.plot_scan_tv_markers_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('plotting__scan_markers_to_plot__include_tv_markers', 'True')))
    app_instance.plot_scan_tv_markers_var.trace_add("write", create_trace_callback(app_instance, "plot_scan_tv_markers_var"))
    app_instance.setting_var_map['plot_scan_tv_markers_var'] = ('last_plotting__scan_markers_to_plot__include_tv_markers', 'plotting__scan_markers_to_plot__include_tv_markers', app_instance.plot_scan_tv_markers_var)

    app_instance.plot_scan_markers_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('plotting__scan_markers_to_plot__include_markers', 'True')))
    app_instance.plot_scan_markers_var.trace_add("write", create_trace_callback(app_instance, "plot_scan_markers_var"))
    app_instance.setting_var_map['plot_scan_markers_var'] = ('last_plotting__scan_markers_to_plot__include_markers', 'plotting__scan_markers_to_plot__include_markers', app_instance.plot_scan_markers_var)

    app_instance.plot_scan_intermod_markers_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('plotting__scan_markers_to_plot__include_intermod_markers', 'False')))
    app_instance.plot_scan_intermod_markers_var.trace_add("write", create_trace_callback(app_instance, "plot_scan_intermod_markers_var"))
    app_instance.setting_var_map['plot_scan_intermod_markers_var'] = ('last_plotting__scan_markers_to_plot__include_intermod_markers', 'plotting__scan_markers_to_plot__include_intermod_markers', app_instance.plot_scan_intermod_markers_var)

    app_instance.open_html_after_complete_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('plotting__scan_markers_to_plot__open_html_after_complete', 'True')))
    app_instance.open_html_after_complete_var.trace_add("write", create_trace_callback(app_instance, "open_html_after_complete_var"))
    app_instance.setting_var_map['open_html_after_complete_var'] = ('last_plotting__scan_markers_to_plot__open_html_after_complete', 'plotting__scan_markers_to_plot__open_html_after_complete', app_instance.open_html_after_complete_var)

    app_instance.create_html_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('plotting__scan_markers_to_plot__create_html', 'True')))
    app_instance.create_html_var.trace_add("write", create_trace_callback(app_instance, "create_html_var"))
    app_instance.setting_var_map['create_html_var'] = ('last_plotting__scan_markers_to_plot__create_html', 'plotting__scan_markers_to_plot__create_html', app_instance.create_html_var)


    # --- PLOTTING SETTINGS (AVERAGE MARKERS) ---
    app_instance.plot_average_gov_markers_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('plotting__average_markers_to_plot__include_gov_markers', 'True')))\
    # This variable is duplicated in default_settings.py, keeping it for now as per original
    app_instance.plot_average_gov_markers_var.trace_add("write", create_trace_callback(app_instance, "plot_average_gov_markers_var"))
    app_instance.setting_var_map['plot_average_gov_markers_var'] = ('last_plotting__average_markers_to_plot__include_gov_markers', 'plotting__average_markers_to_plot__include_gov_markers', app_instance.plot_average_gov_markers_var)

    app_instance.plot_average_tv_markers_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('plotting__average_markers_to_plot__include_tv_markers', 'True')))
    app_instance.plot_average_tv_markers_var.trace_add("write", create_trace_callback(app_instance, "plot_average_tv_markers_var"))
    app_instance.setting_var_map['plot_average_tv_markers_var'] = ('last_plotting__average_markers_to_plot__include_tv_markers', 'plotting__average_markers_to_plot__include_tv_markers', app_instance.plot_average_tv_markers_var)

    app_instance.plot_average_markers_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('plotting__average_markers_to_plot__include_markers', 'True')))
    app_instance.plot_average_markers_var.trace_add("write", create_trace_callback(app_instance, "plot_average_markers_var"))
    app_instance.setting_var_map['plot_average_markers_var'] = ('last_plotting__average_markers_to_plot__include_markers', 'plotting__average_markers_to_plot__include_markers', app_instance.plot_average_markers_var)

    app_instance.plot_average_intermod_markers_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('plotting__average_markers_to_plot__include_intermod_markers', 'False')))
    app_instance.plot_average_intermod_markers_var.trace_add("write", create_trace_callback(app_instance, "plot_average_intermod_markers_var"))
    app_instance.setting_var_map['plot_average_intermod_markers_var'] = ('last_plotting__average_markers_to_plot__include_intermod_markers', 'plotting__average_markers_to_plot__include_intermod_markers', app_instance.plot_average_intermod_markers_var)

    app_instance.math_average_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('plotting__average_markers_to_plot__math_average', 'True')))
    app_instance.math_average_var.trace_add("write", create_trace_callback(app_instance, "math_average_var"))
    app_instance.setting_var_map['math_average_var'] = ('last_plotting__average_markers_to_plot__math_average', 'plotting__average_markers_to_plot__math_average', app_instance.math_average_var)

    app_instance.math_median_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('plotting__average_markers_to_plot__math_median', 'True')))
    app_instance.math_median_var.trace_add("write", create_trace_callback(app_instance, "math_median_var"))
    app_instance.setting_var_map['math_median_var'] = ('last_plotting__average_markers_to_plot__math_median', 'plotting__average_markers_to_plot__math_median', app_instance.math_median_var)

    app_instance.math_min_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('plotting__average_markers_to_plot__math_min', 'True')))
    app_instance.math_min_var.trace_add("write", create_trace_callback(app_instance, "math_min_var"))
    app_instance.setting_var_map['math_min_var'] = ('last_plotting__average_markers_to_plot__math_min', 'plotting__average_markers_to_plot__math_min', app_instance.math_min_var)

    app_instance.math_max_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('plotting__average_markers_to_plot__math_max', 'True')))
    app_instance.math_max_var.trace_add("write", create_trace_callback(app_instance, "math_max_var"))
    app_instance.setting_var_map['math_max_var'] = ('last_plotting__average_markers_to_plot__math_max', 'plotting__average_markers_to_plot__math_max', app_instance.math_max_var)

    app_instance.math_range_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('plotting__average_markers_to_plot__math_range', 'True')))
    app_instance.math_range_var.trace_add("write", create_trace_callback(app_instance, "math_range_var"))
    app_instance.setting_var_map['math_range_var'] = ('last_plotting__average_markers_to_plot__math_range', 'plotting__average_markers_to_plot__math_range', app_instance.math_range_var)

    app_instance.math_standard_deviation_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('plotting__average_markers_to_plot__math_standard_deviation', 'False')))
    app_instance.math_standard_deviation_var.trace_add("write", create_trace_callback(app_instance, "math_standard_deviation_var"))
    app_instance.setting_var_map['math_standard_deviation_var'] = ('last_plotting__average_markers_to_plot__math_standard_deviation', 'plotting__average_markers_to_plot__math_standard_deviation', app_instance.math_standard_deviation_var)

    app_instance.math_variance_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('plotting__average_markers_to_plot__math_variance', 'False')))
    app_instance.math_variance_var.trace_add("write", create_trace_callback(app_instance, "math_variance_var"))
    app_instance.setting_var_map['math_variance_var'] = ('last_plotting__average_markers_to_plot__math_variance', 'plotting__average_markers_to_plot__math_variance', app_instance.math_variance_var)

    # --- INSTRUMENT PRESET SETTINGS ---
    app_instance.last_selected_preset_name_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_instrument_preset__selected_preset_name', ''))
    app_instance.last_selected_preset_name_var.trace_add("write", create_trace_callback(app_instance, "last_selected_preset_name_var"))
    app_instance.setting_var_map['last_selected_preset_name_var'] = ('last_default_instrument_preset__selected_preset_name', 'default_instrument_preset__selected_preset_name', app_instance.last_selected_preset_name_var)

    app_instance.last_loaded_preset_center_freq_mhz_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_instrument_preset__loaded_preset_center_freq_mhz', ''))
    app_instance.last_loaded_preset_center_freq_mhz_var.trace_add("write", create_trace_callback(app_instance, "last_loaded_preset_center_freq_mhz_var"))
    app_instance.setting_var_map['last_loaded_preset_center_freq_mhz_var'] = ('last_default_instrument_preset__loaded_preset_center_freq_mhz', 'default_instrument_preset__loaded_preset_center_freq_mhz', app_instance.last_loaded_preset_center_freq_mhz_var)

    app_instance.last_loaded_preset_span_mhz_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_instrument_preset__loaded_preset_span_mhz', ''))
    app_instance.last_loaded_preset_span_mhz_var.trace_add("write", create_trace_callback(app_instance, "last_loaded_preset_span_mhz_var"))
    app_instance.setting_var_map['last_loaded_preset_span_mhz_var'] = ('last_default_instrument_preset__loaded_preset_span_mhz', 'default_instrument_preset__loaded_preset_span_mhz', app_instance.last_loaded_preset_span_mhz_var)

    app_instance.last_loaded_preset_rbw_hz_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_instrument_preset__loaded_preset_rbw_hz', ''))
    app_instance.last_loaded_preset_rbw_hz_var.trace_add("write", create_trace_callback(app_instance, "last_loaded_preset_rbw_hz_var"))
    app_instance.setting_var_map['last_loaded_preset_rbw_hz_var'] = ('last_default_instrument_preset__loaded_preset_rbw_hz', 'default_instrument_preset__loaded_preset_rbw_hz', app_instance.last_loaded_preset_rbw_hz_var)

    # --- BAND SELECTION VARIABLES ---
    app_instance.band_vars = []
    for band in SCAN_BAND_RANGES:
        var = tk.BooleanVar(app_instance, value=False) # Default to False
        # Get initial value from config if it exists
        config_key = f"last_scan_configuration__band__{band['Band Name'].replace(' ', '_').replace('/', '_').replace('-', '_')}"
        initial_value_from_config = DEFAULT_CONFIG_SETTINGS.get('scan_configuration__' + config_key, 'False')
        var.set(str_to_bool(initial_value_from_config))

        var.trace_add("write", create_trace_callback(app_instance, f"band__{band['Band Name']}"))
        app_instance.band_vars.append({"band": band, "var": var})
        app_instance.setting_var_map[f"band__{band['Band Name']}"] = (config_key, f"scan_configuration__{config_key}", var)


    debug_log(f"Finished setting up Tkinter variables. Ready to rock! Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
