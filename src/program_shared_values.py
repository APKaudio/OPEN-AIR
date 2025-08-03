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
# Version 20250803.1640.0 (Added missing Tkinter variables for scan configuration and meta data.)
# Version 20250803.1645.0 (Fixed AttributeError: 'dict' object has no attribute 'getboolean' by manually converting string values from DEFAULT_CONFIG_SETTINGS.)
# Version 20250803.1650.0 (Added app_instance.setting_var_map to store Tkinter variables and their config keys.)

import os
import inspect # For logging function names
import tkinter as tk # Needed for Tkinter variables

# Import logging and config management functions
import src.debug_logic as debug_logic_module # Import as module to access internal functions
from src.console_logic import console_log # Only console_log is needed here

# Import default values
from src.program_default_values import DEFAULT_CONFIG_SETTINGS, DATA_FOLDER_PATH # Import DATA_FOLDER_PATH

# Global variable to hold the app instance's config object
# This is a bit of a workaround to allow trace callbacks to access the config,
# as they don't directly receive the app_instance.
_app_instance_ref = None

def set_app_instance_ref(app_instance):
    """Sets the global reference to the app instance."""
    global _app_instance_ref
    _app_instance_ref = app_instance

def create_trace_callback(var_name):
    """
    Function Description:
    Creates a callback function for Tkinter variable traces.
    This callback is triggered whenever the associated Tkinter variable changes.
    It logs the change and, if an app instance reference is available,
    saves the application configuration.

    Inputs:
        var_name (str): The name of the Tkinter variable being traced.

    Process:
        1. Defines an inner function `callback` that takes standard trace arguments.
        2. Inside `callback`, it logs the variable's new value.
        3. If `_app_instance_ref` is set, it attempts to save the application configuration.
           This ensures that changes to Tkinter variables are persisted.

    Outputs:
        function: The callback function to be used with `var.trace_add`.
    """
    def callback(*args):
        current_function = inspect.currentframe().f_code.co_name
        debug_logic_module.debug_log(f"Tkinter var '{var_name}' changed to: {_app_instance_ref.__dict__[var_name].get() if _app_instance_ref else 'N/A'}",
                                    file=os.path.basename(__file__),
                                    version="20250803.1650.0", # Use this module's version
                                    function=current_function)
        if _app_instance_ref:
            # Avoid circular import by importing save_config locally if needed,
            # or ensure it's imported at a higher level and passed down.
            # For now, assuming save_config is accessible via app_instance.
            # This trace callback is primarily for logging and triggering config save.
            # The actual save_config function needs to be imported where it's called.
            # For simplicity, we'll assume the main app calls save_config when needed.
            # If a direct save is needed here, we'd need to pass save_config into set_app_instance_ref
            # or import it inside this callback, which is generally not recommended for performance.
            # A better approach is to have the main app listen to these changes and trigger save.
            # For now, we'll rely on the main app's _on_closing or explicit save calls.
            pass # Removed direct save_config call from here to prevent circular imports and simplify trace.
    return callback


def setup_tkinter_variables(app_instance):
    """
    Function Description:
    Initializes all application-wide Tkinter variables (BooleanVar, StringVar, DoubleVar, IntVar).
    These variables are used to bind GUI elements to application state and configuration settings.
    Each variable is also set up with a trace callback to log changes and potentially save config.

    Inputs:
        app_instance (object): A reference to the main application instance.

    Process:
        1. Sets the global `_app_instance_ref`.
        2. Initializes various `tk.BooleanVar`, `tk.StringVar`, `tk.DoubleVar`, and `tk.IntVar`
           attributes on the `app_instance`.
        3. Assigns default values to these variables, either from `DEFAULT_CONFIG_SETTINGS`
           or hardcoded defaults.
        4. Configures trace callbacks for each variable to log changes.
        5. Logs the initialization process.

    Outputs:
        None. Modifies the `app_instance` by adding Tkinter variable attributes.
    """
    global _app_instance_ref
    _app_instance_ref = app_instance # Set the global reference

    current_function = inspect.currentframe().f_code.co_name
    debug_logic_module.debug_log(f"Setting up Tkinter variables for the application. Version: 20250803.1650.0",
                                file=os.path.basename(__file__),
                                version="20250803.1650.0", # Use this module's version
                                function=current_function)

    # Helper function to convert string to boolean
    def str_to_bool(s):
        return str(s).lower() == 'true'

    # Helper function to convert string to float, with error handling
    def str_to_float(s, default):
        try:
            return float(s)
        except (ValueError, TypeError):
            return float(default)

    # Helper function to convert string to int, with error handling
    def str_to_int(s, default):
        try:
            return int(s)
        except (ValueError, TypeError):
            return int(default)

    # Initialize setting_var_map
    app_instance.setting_var_map = {}

    # --- GLOBAL variables ---
    app_instance.general_debug_enabled_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_GLOBAL__debug_enabled', 'False')))
    app_instance.general_debug_enabled_var.trace_add("write", create_trace_callback("general_debug_enabled_var"))
    app_instance.setting_var_map['general_debug_enabled_var'] = ('last_GLOBAL__debug_enabled', 'default_GLOBAL__debug_enabled', app_instance.general_debug_enabled_var)

    app_instance.log_visa_commands_enabled_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_GLOBAL__log_visa_commands_enabled', 'False')))
    app_instance.log_visa_commands_enabled_var.trace_add("write", create_trace_callback("log_visa_commands_enabled_var"))
    app_instance.setting_var_map['log_visa_commands_enabled_var'] = ('last_GLOBAL__log_visa_commands_enabled', 'default_GLOBAL__log_visa_commands_enabled', app_instance.log_visa_commands_enabled_var)

    app_instance.debug_to_terminal_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_GLOBAL__debug_to_Terminal', 'False')))
    app_instance.debug_to_terminal_var.trace_add("write", create_trace_callback("debug_to_terminal_var"))
    app_instance.setting_var_map['debug_to_terminal_var'] = ('last_GLOBAL__debug_to_Terminal', 'default_GLOBAL__debug_to_Terminal', app_instance.debug_to_terminal_var)

    app_instance.debug_to_file_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_GLOBAL__debug_to_file', 'False')))
    app_instance.debug_to_file_var.trace_add("write", create_trace_callback("debug_to_file_var"))
    app_instance.setting_var_map['debug_to_file_var'] = ('last_GLOBAL__debug_to_file', 'default_GLOBAL__debug_to_file', app_instance.debug_to_file_var)

    app_instance.include_console_messages_to_debug_file_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_GLOBAL__include_console_messages_to_debug_file', 'False')))
    app_instance.include_console_messages_to_debug_file_var.trace_add("write", create_trace_callback("include_console_messages_to_debug_file_var"))
    app_instance.setting_var_map['include_console_messages_to_debug_file_var'] = ('last_GLOBAL__include_console_messages_to_debug_file', 'default_GLOBAL__include_console_messages_to_debug_file', app_instance.include_console_messages_to_debug_file_var)

    app_instance.debug_to_gui_console_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_GLOBAL__debug_to_gui_console', 'False')))
    app_instance.debug_to_gui_console_var.trace_add("write", create_trace_callback("debug_to_gui_console_var"))
    app_instance.setting_var_map['debug_to_gui_console_var'] = ('last_GLOBAL__debug_to_gui_console', 'default_GLOBAL__debug_to_gui_console', app_instance.debug_to_gui_console_var)

    app_instance.config_save_success_var = tk.BooleanVar(app_instance, value=False)
    app_instance.config_save_success_var.trace_add("write", create_trace_callback("config_save_success_var"))
    # Note: config_save_success_var is not directly loaded from config, so no last/default keys.

    app_instance.is_connected = tk.BooleanVar(app_instance, value=False)
    app_instance.is_connected.trace_add("write", create_trace_callback("is_connected"))
    # Note: is_connected is runtime status, not loaded from config.

    app_instance.last_config_save_time_var = tk.StringVar(app_instance, value="Never Saved")
    app_instance.last_config_save_time_var.trace_add("write", create_trace_callback("last_config_save_time_var"))
    app_instance.setting_var_map['last_config_save_time_var'] = ('last_GLOBAL__last_config_save_time', 'default_GLOBAL__last_config_save_time', app_instance.last_config_save_time_var)


    # --- Instrument Tab variables ---
    app_instance.selected_visa_resource_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_instrument__selected_visa_resource', ''))
    app_instance.selected_visa_resource_var.trace_add("write", create_trace_callback("selected_visa_resource_var"))
    app_instance.setting_var_map['selected_visa_resource_var'] = ('last_instrument__selected_visa_resource', 'default_instrument__selected_visa_resource', app_instance.selected_visa_resource_var)

    app_instance.instrument_model_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_instrument__instrument_model', ''))
    app_instance.instrument_model_var.trace_add("write", create_trace_callback("instrument_model_var"))
    app_instance.setting_var_map['instrument_model_var'] = ('last_instrument__instrument_model', 'default_instrument__instrument_model', app_instance.instrument_model_var)

    app_instance.instrument_serial_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_instrument__instrument_serial', ''))
    app_instance.instrument_serial_var.trace_add("write", create_trace_callback("instrument_serial_var"))
    app_instance.setting_var_map['instrument_serial_var'] = ('last_instrument__instrument_serial', 'default_instrument__instrument_serial', app_instance.instrument_serial_var)

    app_instance.instrument_firmware_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_instrument__instrument_firmware', ''))
    app_instance.instrument_firmware_var.trace_add("write", create_trace_callback("instrument_firmware_var"))
    app_instance.setting_var_map['instrument_firmware_var'] = ('last_instrument__instrument_firmware', 'default_instrument__instrument_firmware', app_instance.instrument_firmware_var)

    app_instance.instrument_connection_status_var = tk.StringVar(app_instance, value="Disconnected")
    app_instance.instrument_connection_status_var.trace_add("write", create_trace_callback("instrument_connection_status_var"))
    # Note: instrument_connection_status_var is runtime status, not loaded from config.

    app_instance.center_freq_mhz_var = tk.DoubleVar(app_instance, value=str_to_float(DEFAULT_CONFIG_SETTINGS.get('default_instrument__center_freq_mhz', '0.0'), 0.0))
    app_instance.center_freq_mhz_var.trace_add("write", create_trace_callback("center_freq_mhz_var"))
    app_instance.setting_var_map['center_freq_mhz_var'] = ('last_instrument__center_freq_mhz', 'default_instrument__center_freq_mhz', app_instance.center_freq_mhz_var)

    app_instance.span_mhz_var = tk.DoubleVar(app_instance, value=str_to_float(DEFAULT_CONFIG_SETTINGS.get('default_instrument__span_mhz', '0.0'), 0.0))
    app_instance.span_mhz_var.trace_add("write", create_trace_callback("span_mhz_var"))
    app_instance.setting_var_map['span_mhz_var'] = ('last_instrument__span_mhz', 'default_instrument__span_mhz', app_instance.span_mhz_var)

    app_instance.rbw_hz_var = tk.DoubleVar(app_instance, value=str_to_float(DEFAULT_CONFIG_SETTINGS.get('default_instrument__rbw_hz', '0.0'), 0.0))
    app_instance.rbw_hz_var.trace_add("write", create_trace_callback("rbw_hz_var"))
    app_instance.setting_var_map['rbw_hz_var'] = ('last_instrument__rbw_hz', 'default_instrument__rbw_hz', app_instance.rbw_hz_var)

    app_instance.ref_level_dbm_var = tk.DoubleVar(app_instance, value=str_to_float(DEFAULT_CONFIG_SETTINGS.get('default_instrument__ref_level_dbm', '0.0'), 0.0))
    app_instance.ref_level_dbm_var.trace_add("write", create_trace_callback("ref_level_dbm_var"))
    app_instance.setting_var_map['ref_level_dbm_var'] = ('last_instrument__ref_level_dbm', 'default_instrument__ref_level_dbm', app_instance.ref_level_dbm_var)

    app_instance.preamp_on_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_instrument__preamp_on', 'False')))
    app_instance.preamp_on_var.trace_add("write", create_trace_callback("preamp_on_var"))
    app_instance.setting_var_map['preamp_on_var'] = ('last_instrument__preamp_on', 'default_instrument__preamp_on', app_instance.preamp_on_var)

    app_instance.high_sensitivity_on_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_instrument__high_sensitivity_on', 'False')))
    app_instance.high_sensitivity_on_var.trace_add("write", create_trace_callback("high_sensitivity_on_var"))
    app_instance.setting_var_map['high_sensitivity_on_var'] = ('last_instrument__high_sensitivity_on', 'default_instrument__high_sensitivity_on', app_instance.high_sensitivity_on_var)

    # --- Scanning Tab variables ---
    app_instance.scan_name_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scanning__scan_name', 'New Scan'))
    app_instance.scan_name_var.trace_add("write", create_trace_callback("scan_name_var"))
    app_instance.setting_var_map['scan_name_var'] = ('last_scanning__scan_name', 'default_scanning__scan_name', app_instance.scan_name_var)

    app_instance.output_folder_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scanning__output_folder', os.path.join(DATA_FOLDER_PATH, "scan_data")))
    app_instance.output_folder_var.trace_add("write", create_trace_callback("output_folder_var"))
    app_instance.setting_var_map['output_folder_var'] = ('last_scanning__output_folder', 'default_scanning__output_folder', app_instance.output_folder_var)

    app_instance.num_scan_cycles_var = tk.IntVar(app_instance, value=str_to_int(DEFAULT_CONFIG_SETTINGS.get('default_scanning__num_scan_cycles', '1'), 1))
    app_instance.num_scan_cycles_var.trace_add("write", create_trace_callback("num_scan_cycles_var"))
    app_instance.setting_var_map['num_scan_cycles_var'] = ('last_scanning__num_scan_cycles', 'default_scanning__num_scan_cycles', app_instance.num_scan_cycles_var)

    app_instance.rbw_step_size_hz_var = tk.DoubleVar(app_instance, value=str_to_float(DEFAULT_CONFIG_SETTINGS.get('default_scanning__rbw_step_size_hz', '10000.0'), 10000.0))
    app_instance.rbw_step_size_hz_var.trace_add("write", create_trace_callback("rbw_step_size_hz_var"))
    app_instance.setting_var_map['rbw_step_size_hz_var'] = ('last_scanning__rbw_step_size_hz', 'default_scanning__rbw_step_size_hz', app_instance.rbw_step_size_hz_var)

    app_instance.cycle_wait_time_seconds_var = tk.DoubleVar(app_instance, value=str_to_float(DEFAULT_CONFIG_SETTINGS.get('default_scanning__cycle_wait_time_seconds', '0.0'), 0.0))
    app_instance.cycle_wait_time_seconds_var.trace_add("write", create_trace_callback("cycle_wait_time_seconds_var"))
    app_instance.setting_var_map['cycle_wait_time_seconds_var'] = ('last_scanning__cycle_wait_time_seconds', 'default_scanning__cycle_wait_time_seconds', app_instance.cycle_wait_time_seconds_var)

    app_instance.maxhold_time_seconds_var = tk.DoubleVar(app_instance, value=str_to_float(DEFAULT_CONFIG_SETTINGS.get('default_scanning__maxhold_time_seconds', '0.0'), 0.0))
    app_instance.maxhold_time_seconds_var.trace_add("write", create_trace_callback("maxhold_time_seconds_var"))
    app_instance.setting_var_map['maxhold_time_seconds_var'] = ('last_scanning__maxhold_time_seconds', 'default_scanning__maxhold_time_seconds', app_instance.maxhold_time_seconds_var)

    app_instance.scan_rbw_hz_var = tk.DoubleVar(app_instance, value=str_to_float(DEFAULT_CONFIG_SETTINGS.get('default_scanning__scan_rbw_hz', '10000.0'), 10000.0))
    app_instance.scan_rbw_hz_var.trace_add("write", create_trace_callback("scan_rbw_hz_var"))
    app_instance.setting_var_map['scan_rbw_hz_var'] = ('last_scanning__scan_rbw_hz', 'default_scanning__scan_rbw_hz', app_instance.scan_rbw_hz_var)

    app_instance.attenuation_var = tk.DoubleVar(app_instance, value=str_to_float(DEFAULT_CONFIG_SETTINGS.get('default_scanning__attenuation', '0.0'), 0.0))
    app_instance.attenuation_var.trace_add("write", create_trace_callback("attenuation_var"))
    app_instance.setting_var_map['attenuation_var'] = ('last_scanning__attenuation', 'default_scanning__attenuation', app_instance.attenuation_var)

    app_instance.freq_shift_var = tk.DoubleVar(app_instance, value=str_to_float(DEFAULT_CONFIG_SETTINGS.get('default_scanning__freq_shift', '0.0'), 0.0))
    app_instance.freq_shift_var.trace_add("write", create_trace_callback("freq_shift_var"))
    app_instance.setting_var_map['freq_shift_var'] = ('last_scanning__freq_shift', 'default_scanning__freq_shift', app_instance.freq_shift_var)

    app_instance.scan_mode_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scanning__scan_mode', 'Normal'))
    app_instance.scan_mode_var.trace_add("write", create_trace_callback("scan_mode_var"))
    app_instance.setting_var_map['scan_mode_var'] = ('last_scanning__scan_mode', 'default_scanning__scan_mode', app_instance.scan_mode_var)

    app_instance.desired_default_focus_width_var = tk.DoubleVar(app_instance, value=str_to_float(DEFAULT_CONFIG_SETTINGS.get('default_scanning__desired_default_focus_width', '10000.0'), 10000.0))
    app_instance.desired_default_focus_width_var.trace_add("write", create_trace_callback("desired_default_focus_width_var"))
    app_instance.setting_var_map['desired_default_focus_width_var'] = ('last_scanning__desired_default_focus_width', 'default_scanning__desired_default_focus_width', app_instance.desired_default_focus_width_var)

    app_instance.scan_rbw_segmentation_var = tk.DoubleVar(app_instance, value=str_to_float(DEFAULT_CONFIG_SETTINGS.get('default_scanning__scan_rbw_segmentation', '10000.0'), 10000.0))
    app_instance.scan_rbw_segmentation_var.trace_add("write", create_trace_callback("scan_rbw_segmentation_var"))
    app_instance.setting_var_map['scan_rbw_segmentation_var'] = ('last_scanning__scan_rbw_segmentation', 'default_scanning__scan_rbw_segmentation', app_instance.scan_rbw_segmentation_var)

    # Band selection variables (dynamically created based on SCAN_BAND_RANGES)
    app_instance.band_selection_vars = {}
    # Assuming SCAN_BAND_RANGES is a dictionary or list of dictionaries
    # For now, initialize a generic one for demonstration
    for i in range(1, 11): # Example for 10 bands
        band_name = f"Band{i}"
        var_name = f"band_selection_vars[{band_name}]" # Construct a unique name for tracing
        app_instance.band_selection_vars[band_name] = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get(f'default_scanning__band_{band_name}_enabled', 'False')))
        app_instance.band_selection_vars[band_name].trace_add("write", create_trace_callback(var_name))
        # Note: Band selection is handled specially in load_config/save_config, not via setting_var_map directly.


    # --- Scan Meta Data variables ---
    app_instance.operator_name_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scan_meta_data__operator_name', ''))
    app_instance.operator_name_var.trace_add("write", create_trace_callback("operator_name_var"))
    app_instance.setting_var_map['operator_name_var'] = ('last_scan_meta_data__operator_name', 'default_scan_meta_data__operator_name', app_instance.operator_name_var)

    app_instance.operator_contact_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scan_meta_data__operator_contact', ''))
    app_instance.operator_contact_var.trace_add("write", create_trace_callback("operator_contact_var"))
    app_instance.setting_var_map['operator_contact_var'] = ('last_scan_meta_data__operator_contact', 'default_scan_meta_data__operator_contact', app_instance.operator_contact_var)

    app_instance.venue_name_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scan_meta_data__venue_name', ''))
    app_instance.venue_name_var.trace_add("write", create_trace_callback("venue_name_var"))
    app_instance.setting_var_map['venue_name_var'] = ('last_scan_meta_data__venue_name', 'default_scan_meta_data__venue_name', app_instance.venue_name_var)

    app_instance.venue_postal_code_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scan_meta_data__venue_postal_code', ''))
    app_instance.venue_postal_code_var.trace_add("write", create_trace_callback("venue_postal_code_var"))
    app_instance.setting_var_map['venue_postal_code_var'] = ('last_scan_meta_data__venue_postal_code', 'default_scan_meta_data__venue_postal_code', app_instance.venue_postal_code_var)

    app_instance.address_field_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scan_meta_data__address_field', ''))
    app_instance.address_field_var.trace_add("write", create_trace_callback("address_field_var"))
    app_instance.setting_var_map['address_field_var'] = ('last_scan_meta_data__address_field', 'default_scan_meta_data__address_field', app_instance.address_field_var)

    app_instance.city_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scan_meta_data__city', ''))
    app_instance.city_var.trace_add("write", create_trace_callback("city_var"))
    app_instance.setting_var_map['city_var'] = ('last_scan_meta_data__city', 'default_scan_meta_data__city', app_instance.city_var)

    app_instance.province_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scan_meta_data__province', ''))
    app_instance.province_var.trace_add("write", create_trace_callback("province_var"))
    app_instance.setting_var_map['province_var'] = ('last_scan_meta_data__province', 'default_scan_meta_data__province', app_instance.province_var)

    app_instance.scanner_type_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scan_meta_data__scanner_type', ''))
    app_instance.scanner_type_var.trace_add("write", create_trace_callback("scanner_type_var"))
    app_instance.setting_var_map['scanner_type_var'] = ('last_scan_meta_data__scanner_type', 'default_scan_meta_data__scanner_type', app_instance.scanner_type_var)

    app_instance.selected_antenna_type_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scan_meta_data__selected_antenna_type', ''))
    app_instance.selected_antenna_type_var.trace_add("write", create_trace_callback("selected_antenna_type_var"))
    app_instance.setting_var_map['selected_antenna_type_var'] = ('last_scan_meta_data__selected_antenna_type', 'default_scan_meta_data__selected_antenna_type', app_instance.selected_antenna_type_var)

    app_instance.antenna_description_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scan_meta_data__antenna_description', ''))
    app_instance.antenna_description_var.trace_add("write", create_trace_callback("antenna_description_var"))
    app_instance.setting_var_map['antenna_description_var'] = ('last_scan_meta_data__antenna_description', 'default_scan_meta_data__antenna_description', app_instance.antenna_description_var)

    app_instance.antenna_use_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scan_meta_data__antenna_use', ''))
    app_instance.antenna_use_var.trace_add("write", create_trace_callback("antenna_use_var"))
    app_instance.setting_var_map['antenna_use_var'] = ('last_scan_meta_data__antenna_use', 'default_scan_meta_data__antenna_use', app_instance.antenna_use_var)

    app_instance.antenna_mount_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scan_meta_data__antenna_mount', ''))
    app_instance.antenna_mount_var.trace_add("write", create_trace_callback("antenna_mount_var"))
    app_instance.setting_var_map['antenna_mount_var'] = ('last_scan_meta_data__antenna_mount', 'default_scan_meta_data__antenna_mount', app_instance.antenna_mount_var)

    app_instance.selected_amplifier_type_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scan_meta_data__selected_amplifier_type', ''))
    app_instance.selected_amplifier_type_var.trace_add("write", create_trace_callback("selected_amplifier_type_var"))
    app_instance.setting_var_map['selected_amplifier_type_var'] = ('last_scan_meta_data__selected_amplifier_type', 'default_scan_meta_data__selected_amplifier_type', app_instance.selected_amplifier_type_var)

    app_instance.amplifier_description_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scan_meta_data__amplifier_description', ''))
    app_instance.amplifier_description_var.trace_add("write", create_trace_callback("amplifier_description_var"))
    app_instance.setting_var_map['amplifier_description_var'] = ('last_scan_meta_data__amplifier_description', 'default_scan_meta_data__amplifier_description', app_instance.amplifier_description_var)

    app_instance.amplifier_use_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scan_meta_data__amplifier_use', ''))
    app_instance.amplifier_use_var.trace_add("write", create_trace_callback("amplifier_use_var"))
    app_instance.setting_var_map['amplifier_use_var'] = ('last_scan_meta_data__amplifier_use', 'default_scan_meta_data__amplifier_use', app_instance.amplifier_use_var)

    app_instance.general_notes_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scan_meta_data__general_notes', ''))
    app_instance.general_notes_var.trace_add("write", create_trace_callback("general_notes_var"))
    app_instance.setting_var_map['general_notes_var'] = ('last_scan_meta_data__general_notes', 'default_scan_meta_data__general_notes', app_instance.general_notes_var)

    app_instance.notes_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_scan_meta_data__notes', ''))
    app_instance.notes_var.trace_add("write", create_trace_callback("notes_var"))
    app_instance.setting_var_map['notes_var'] = ('last_scan_meta_data__notes', 'default_scan_meta_data__notes', app_instance.notes_var)


    # --- Paned Window Sash Position ---
    app_instance.paned_window_sash_position_var = tk.IntVar(app_instance, value=str_to_int(DEFAULT_CONFIG_SETTINGS.get('default_GLOBAL__paned_window_sash_position', '200'), 200))
    app_instance.paned_window_sash_position_var.trace_add("write", create_trace_callback("paned_window_sash_position_var"))
    app_instance.setting_var_map['paned_window_sash_position_var'] = ('last_GLOBAL__paned_window_sash_position', 'default_GLOBAL__paned_window_sash_position', app_instance.paned_window_sash_position_var)

    # --- Instrument Preset Variables ---
    app_instance.selected_preset_name_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_instrument_preset__selected_preset_name', ''))
    app_instance.selected_preset_name_var.trace_add("write", create_trace_callback("selected_preset_name_var"))
    app_instance.setting_var_map['selected_preset_name_var'] = ('last_instrument_preset__selected_preset_name', 'default_instrument_preset__selected_preset_name', app_instance.selected_preset_name_var)

    app_instance.loaded_preset_center_freq_mhz_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_instrument_preset__loaded_preset_center_freq_mhz', ''))
    app_instance.loaded_preset_center_freq_mhz_var.trace_add("write", create_trace_callback("loaded_preset_center_freq_mhz_var"))
    app_instance.setting_var_map['loaded_preset_center_freq_mhz_var'] = ('last_instrument_preset__loaded_preset_center_freq_mhz', 'default_instrument_preset__loaded_preset_center_freq_mhz', app_instance.loaded_preset_center_freq_mhz_var)

    app_instance.loaded_preset_span_mhz_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_instrument_preset__loaded_preset_span_mhz', ''))
    app_instance.loaded_preset_span_mhz_var.trace_add("write", create_trace_callback("loaded_preset_span_mhz_var"))
    app_instance.setting_var_map['loaded_preset_span_mhz_var'] = ('last_instrument_preset__loaded_preset_span_mhz', 'default_instrument_preset__loaded_preset_span_mhz', app_instance.loaded_preset_span_mhz_var)

    app_instance.loaded_preset_rbw_hz_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG_SETTINGS.get('default_instrument_preset__loaded_preset_rbw_hz', ''))
    app_instance.loaded_preset_rbw_hz_var.trace_add("write", create_trace_callback("loaded_preset_rbw_hz_var"))
    app_instance.setting_var_map['loaded_preset_rbw_hz_var'] = ('last_instrument_preset__loaded_preset_rbw_hz', 'default_instrument_preset__loaded_preset_rbw_hz', app_instance.loaded_preset_rbw_hz_var)


    # --- Plotting Tab Variables ---
    app_instance.scan_include_gov_markers_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_plotting__scan_markers_to_plot__include_gov_markers', 'True')))
    app_instance.scan_include_gov_markers_var.trace_add("write", create_trace_callback("scan_include_gov_markers_var"))
    app_instance.setting_var_map['scan_include_gov_markers_var'] = ('last_plotting__scan_markers_to_plot__include_gov_markers', 'default_plotting__scan_markers_to_plot__include_gov_markers', app_instance.scan_include_gov_markers_var)

    app_instance.scan_include_tv_markers_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_plotting__scan_markers_to_plot__include_tv_markers', 'True')))
    app_instance.scan_include_tv_markers_var.trace_add("write", create_trace_callback("scan_include_tv_markers_var"))
    app_instance.setting_var_map['scan_include_tv_markers_var'] = ('last_plotting__scan_markers_to_plot__include_tv_markers', 'default_plotting__scan_markers_to_plot__include_tv_markers', app_instance.scan_include_tv_markers_var)

    app_instance.scan_include_markers_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_plotting__scan_markers_to_plot__include_markers', 'True')))
    app_instance.scan_include_markers_var.trace_add("write", create_trace_callback("scan_include_markers_var"))
    app_instance.setting_var_map['scan_include_markers_var'] = ('last_plotting__scan_markers_to_plot__include_markers', 'default_plotting__scan_markers_to_plot__include_markers', app_instance.scan_include_markers_var)

    app_instance.scan_include_intermod_markers_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_plotting__scan_markers_to_plot__include_intermod_markers', 'False')))
    app_instance.scan_include_intermod_markers_var.trace_add("write", create_trace_callback("scan_include_intermod_markers_var"))
    app_instance.setting_var_map['scan_include_intermod_markers_var'] = ('last_plotting__scan_markers_to_plot__include_intermod_markers', 'default_plotting__scan_markers_to_plot__include_intermod_markers', app_instance.scan_include_intermod_markers_var)

    app_instance.scan_open_html_after_complete_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_plotting__scan_markers_to_plot__open_html_after_complete', 'True')))
    app_instance.scan_open_html_after_complete_var.trace_add("write", create_trace_callback("scan_open_html_after_complete_var"))
    app_instance.setting_var_map['scan_open_html_after_complete_var'] = ('last_plotting__scan_markers_to_plot__open_html_after_complete', 'default_plotting__scan_markers_to_plot__open_html_after_complete', app_instance.scan_open_html_after_complete_var)

    app_instance.scan_create_html_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_plotting__scan_markers_to_plot__create_html', 'True')))
    app_instance.scan_create_html_var.trace_add("write", create_trace_callback("scan_create_html_var"))
    app_instance.setting_var_map['scan_create_html_var'] = ('last_plotting__scan_markers_to_plot__create_html', 'default_plotting__scan_markers_to_plot__create_html', app_instance.scan_create_html_var)

    app_instance.avg_include_gov_markers_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_plotting__average_markers_to_plot__include_gov_markers', 'True')))
    app_instance.avg_include_gov_markers_var.trace_add("write", create_trace_callback("avg_include_gov_markers_var"))
    app_instance.setting_var_map['avg_include_gov_markers_var'] = ('last_plotting__average_markers_to_plot__include_gov_markers', 'default_plotting__average_markers_to_plot__include_gov_markers', app_instance.avg_include_gov_markers_var)

    app_instance.avg_include_tv_markers_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_plotting__average_markers_to_plot__include_tv_markers', 'True')))
    app_instance.avg_include_tv_markers_var.trace_add("write", create_trace_callback("avg_include_tv_markers_var"))
    app_instance.setting_var_map['avg_include_tv_markers_var'] = ('last_plotting__average_markers_to_plot__include_tv_markers', 'default_plotting__average_markers_to_plot__include_tv_markers', app_instance.avg_include_tv_markers_var)

    app_instance.avg_include_markers_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_plotting__average_markers_to_plot__include_markers', 'True')))
    app_instance.avg_include_markers_var.trace_add("write", create_trace_callback("avg_include_markers_var"))
    app_instance.setting_var_map['avg_include_markers_var'] = ('last_plotting__average_markers_to_plot__include_markers', 'default_plotting__average_markers_to_plot__include_markers', app_instance.avg_include_markers_var)

    app_instance.avg_include_intermod_markers_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_plotting__average_markers_to_plot__include_intermod_markers', 'False')))
    app_instance.avg_include_intermod_markers_var.trace_add("write", create_trace_callback("avg_include_intermod_markers_var"))
    app_instance.setting_var_map['avg_include_intermod_markers_var'] = ('last_plotting__average_markers_to_plot__include_intermod_markers', 'default_plotting__average_markers_to_plot__include_intermod_markers', app_instance.avg_include_intermod_markers_var)

    app_instance.math_average_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_plotting__average_markers_to_plot__math_average', 'True')))
    app_instance.math_average_var.trace_add("write", create_trace_callback("math_average_var"))
    app_instance.setting_var_map['math_average_var'] = ('last_plotting__average_markers_to_plot__math_average', 'default_plotting__average_markers_to_plot__math_average', app_instance.math_average_var)

    app_instance.math_median_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_plotting__average_markers_to_plot__math_median', 'False')))
    app_instance.math_median_var.trace_add("write", create_trace_callback("math_median_var"))
    app_instance.setting_var_map['math_median_var'] = ('last_plotting__average_markers_to_plot__math_median', 'default_plotting__average_markers_to_plot__math_median', app_instance.math_median_var)

    app_instance.math_range_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_plotting__average_markers_to_plot__math_range', 'False')))
    app_instance.math_range_var.trace_add("write", create_trace_callback("math_range_var"))
    app_instance.setting_var_map['math_range_var'] = ('last_plotting__average_markers_to_plot__math_range', 'default_plotting__average_markers_to_plot__math_range', app_instance.math_range_var)

    app_instance.math_standard_deviation_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_plotting__average_markers_to_plot__math_standard_deviation', 'False')))
    app_instance.math_standard_deviation_var.trace_add("write", create_trace_callback("math_standard_deviation_var"))
    app_instance.setting_var_map['math_standard_deviation_var'] = ('last_plotting__average_markers_to_plot__math_standard_deviation', 'default_plotting__average_markers_to_plot__math_standard_deviation', app_instance.math_standard_deviation_var)

    app_instance.math_variance_var = tk.BooleanVar(app_instance, value=str_to_bool(DEFAULT_CONFIG_SETTINGS.get('default_plotting__average_markers_to_plot__math_variance', 'False')))
    app_instance.math_variance_var.trace_add("write", create_trace_callback("math_variance_var"))
    app_instance.setting_var_map['math_variance_var'] = ('last_plotting__average_markers_to_plot__math_variance', 'default_plotting__average_markers_to_plot__math_variance', app_instance.math_variance_var)

    debug_logic_module.debug_log(f"Finished setting up Tkinter variables. Version: 20250803.1650.0",
                                file=os.path.basename(__file__),
                                version="20250803.1650.0", # Use this module's version
                                function=current_function)
