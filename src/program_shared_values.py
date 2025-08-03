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

import os
import inspect # For logging function names
import tkinter as tk # Needed for Tkinter variables

# Import logging and config management functions
import src.debug_logic as debug_logic_module # Import as module to access internal functions
from src.debug_logic import debug_log # Only need debug_log here for the trace callback
from src.console_logic import console_log # Only need console_log here for the trace callback
from src.settings_and_config.config_manager import save_config # Only need save_config here for the trace callback

# Import constants and lists for Tkinter variable initialization
from ref.frequency_bands import SCAN_BAND_RANGES, MHZ_TO_HZ, VBW_RBW_RATIO
from ref.ref_scanner_setting_lists import scan_modes, attenuation_levels, frequency_shift_presets, graph_quality_drop_down, number_of_scans_presets, rbw_presets, dwell_time_drop_down, cycle_wait_time_presets, reference_level_drop_down


current_version = "20250803.1450.0" # this variable should always be defined below the header to make the debugging better

def setup_tkinter_variables(app_instance):
    """
    Function Description:
    Initializes all Tkinter variables used throughout the application.
    This centralizes the creation of `StringVar`, `BooleanVar`, `DoubleVar`,
    and `IntVar` objects, making them easily accessible and manageable.
    It also sets default values for various settings, which can then be
    overridden by loaded configuration.

    Inputs:
        app_instance (App): The main application instance, to attach variables to.

    Process:
        1. Defines a helper function `create_trace_callback` for saving config on variable changes.
        2. Initializes various Tkinter variables (BooleanVar, StringVar, DoubleVar, IntVar)
           for global settings, instrument connection/settings, scan configuration,
           scan metadata, presets, and plotting.
        3. Attaches trace callbacks to these variables to trigger config saving.
        4. Populates `app_instance.setting_var_map` with mappings for config loading/saving.

    Outputs:
        None. Populates `app_instance` with Tkinter variable attributes.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Setting up Tkinter variables in program_shared_values. Version: {current_version}.",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    # Define a helper function to add trace for saving config
    def create_trace_callback(var_name):
        def callback(*args):
            # Ensure app_instance.is_ready_to_save is checked before saving
            # This flag is set to True after all initial setup is complete in App.__init__
            if app_instance.is_ready_to_save:
                debug_log(f"Tkinter variable '{var_name}' changed. Saving config.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=inspect.currentframe().f_code.co_name)
                save_config(app_instance.config, app_instance.CONFIG_FILE_PATH, console_log, app_instance)
        return callback

    # GLOBAL variables
    app_instance.general_debug_enabled_var = tk.BooleanVar(app_instance, value=False)
    app_instance.general_debug_enabled_var.trace_add("write", create_trace_callback("general_debug_enabled_var"))

    app_instance.log_visa_commands_enabled_var = tk.BooleanVar(app_instance, value=False)
    app_instance.log_visa_commands_enabled_var.trace_add("write", create_trace_callback("log_visa_commands_enabled_var"))

    app_instance.debug_to_terminal_var = tk.BooleanVar(app_instance, value=False)
    app_instance.debug_to_terminal_var.trace_add("write", create_trace_callback("debug_to_terminal_var"))

    app_instance.debug_to_file_var = tk.BooleanVar(app_instance, value=False)
    app_instance.debug_to_file_var.trace_add("write", create_trace_callback("debug_to_file_var"))

    app_instance.include_console_messages_to_debug_file_var = tk.BooleanVar(app_instance, value=False)
    app_instance.include_console_messages_to_debug_file_var.trace_add("write", create_trace_callback("include_console_messages_to_debug_file_var"))

    app_instance.debug_to_gui_console_var = tk.BooleanVar(app_instance, value=False)
    app_instance.debug_to_gui_console_var.trace_add("write", create_trace_callback("debug_to_gui_console_var"))

    app_instance.paned_window_sash_position_var = tk.IntVar(app_instance, value=700)
    app_instance.paned_window_sash_position_var.trace_add("write", create_trace_callback("paned_window_sash_position_var"))

    app_instance.last_config_save_time_var = tk.StringVar(app_instance, value="Last Saved: Never")


    # Instrument Connection variables
    app_instance.selected_resource = tk.StringVar(app_instance)
    app_instance.selected_resource.trace_add("write", create_trace_callback("selected_resource"))

    app_instance.available_resources = tk.StringVar(app_instance)
    app_instance.available_resources.trace_add("write", create_trace_callback("available_resources"))

    app_instance.resource_names = tk.StringVar(app_instance)

    app_instance.instrument_model_var = tk.StringVar(app_instance, value="N/A")
    app_instance.instrument_model_var.trace_add("write", create_trace_callback("instrument_model_var"))

    app_instance.instrument_serial_var = tk.StringVar(app_instance, value="N/A")
    app_instance.instrument_serial_var.trace_add("write", create_trace_callback("instrument_serial_var"))

    app_instance.instrument_firmware_var = tk.StringVar(app_instance, value="N/A")
    app_instance.instrument_firmware_var.trace_add("write", create_trace_callback("instrument_firmware_var"))

    app_instance.instrument_options_var = tk.StringVar(app_instance, value="N/A")
    app_instance.instrument_options_var.trace_add("write", create_trace_callback("instrument_options_var"))


    # Instrument settings variables (used by instrument_logic.py)
    app_instance.center_freq_mhz_var = tk.DoubleVar(app_instance, value=2400000000.0)
    app_instance.center_freq_mhz_var.trace_add("write", create_trace_callback("center_freq_mhz_var"))

    app_instance.span_mhz_var = tk.DoubleVar(app_instance, value=100000000.0)
    app_instance.span_mhz_var.trace_add("write", create_trace_callback("span_mhz_var"))

    app_instance.rbw_hz_var = tk.DoubleVar(app_instance, value=10000.0)
    app_instance.rbw_hz_var.trace_add("write", create_trace_callback("rbw_hz_var"))

    app_instance.vbw_hz_var = tk.DoubleVar(app_instance, value=3000.0)
    app_instance.vbw_hz_var.trace_add("write", create_trace_callback("vbw_hz_var"))

    app_instance.sweep_time_s_var = tk.DoubleVar(app_instance, value=0.01)
    app_instance.sweep_time_s_var.trace_add("write", create_trace_callback("sweep_time_s_var"))


    # Scan Configuration variables
    app_instance.scan_name_var = tk.StringVar(app_instance, value="ThisIsMyScan")
    app_instance.scan_name_var.trace_add("write", create_trace_callback("scan_name_var"))

    app_instance.output_folder_var = tk.StringVar(app_instance, value=app_instance.DATA_FOLDER_PATH)
    app_instance.output_folder_var.trace_add("write", create_trace_callback("output_folder_var"))

    # Initialize with 'value' key from the standardized lists
    app_instance.num_scan_cycles_var = tk.IntVar(app_instance, value=number_of_scans_presets[0]["value"])
    app_instance.num_scan_cycles_var.trace_add("write", create_trace_callback("num_scan_cycles_var"))

    app_instance.rbw_step_size_hz_var = tk.StringVar(app_instance, value=str(graph_quality_drop_down[0]["value"]))
    app_instance.rbw_step_size_hz_var.trace_add("write", create_trace_callback("rbw_step_size_hz_var"))

    app_instance.cycle_wait_time_seconds_var = tk.StringVar(app_instance, value=str(cycle_wait_time_presets[0]["value"]))
    app_instance.cycle_wait_time_seconds_var.trace_add("write", create_trace_callback("cycle_wait_time_seconds_var"))

    app_instance.maxhold_time_seconds_var = tk.StringVar(app_instance, value=str(dwell_time_drop_down[0]["value"]))
    app_instance.maxhold_time_seconds_var.trace_add("write", create_trace_callback("maxhold_time_seconds_var"))

    app_instance.scan_rbw_hz_var = tk.StringVar(app_instance, value=str(rbw_presets[0]["value"]))
    app_instance.scan_rbw_hz_var.trace_add("write", create_trace_callback("scan_rbw_hz_var"))

    app_instance.reference_level_dbm_var = tk.StringVar(app_instance, value=str(reference_level_drop_down[0]["value"]))
    app_instance.reference_level_dbm_var.trace_add("write", create_trace_callback("reference_level_dbm_var"))

    app_instance.attenuation_var = tk.StringVar(app_instance, value=str(attenuation_levels[0]["value"]))
    app_instance.attenuation_var.trace_add("write", create_trace_callback("attenuation_var"))

    app_instance.freq_shift_var = tk.StringVar(app_instance, value=str(frequency_shift_presets[0]["value"]))
    app_instance.freq_shift_var.trace_add("write", create_trace_callback("freq_shift_var"))

    app_instance.scan_mode_var = tk.StringVar(app_instance, value=scan_modes[0]["value"])
    app_instance.scan_mode_var.trace_add("write", create_trace_callback("scan_mode_var"))

    app_instance.maxhold_enabled_var = tk.BooleanVar(app_instance, value=True)
    app_instance.maxhold_enabled_var.trace_add("write", create_trace_callback("maxhold_enabled_var"))

    app_instance.high_sensitivity_var = tk.BooleanVar(app_instance, value=True)
    app_instance.high_sensitivity_var.trace_add("write", create_trace_callback("high_sensitivity_var"))

    app_instance.preamp_on_var = tk.BooleanVar(app_instance, value=True)
    app_instance.preamp_on_var.trace_add("write", create_trace_callback("preamp_on_var"))

    app_instance.scan_rbw_segmentation_var = tk.StringVar(app_instance, value="1000000.0")
    app_instance.scan_rbw_segmentation_var.trace_add("write", create_trace_callback("scan_rbw_segmentation_var"))

    app_instance.desired_default_focus_width_var = tk.StringVar(app_instance, value=str(graph_quality_drop_down[0]["value"]))
    app_instance.desired_default_focus_width_var.trace_add("write", create_trace_callback("desired_default_focus_width_var"))


    # Scan Meta Data variables
    app_instance.operator_name_var = tk.StringVar(app_instance, value="Anthony Peter Kuzub")
    app_instance.operator_name_var.trace_add("write", create_trace_callback("operator_name_var"))

    app_instance.operator_contact_var = tk.StringVar(app_instance, value="I@Like.audio")
    app_instance.operator_contact_var.trace_add("write", create_trace_callback("operator_contact_var"))

    app_instance.venue_name_var = tk.StringVar(app_instance, value="Garage")
    app_instance.venue_name_var.trace_add("write", create_trace_callback("venue_name_var"))

    app_instance.venue_postal_code_var = tk.StringVar(app_instance, value="")
    app_instance.venue_postal_code_var.trace_add("write", create_trace_callback("venue_postal_code_var"))

    app_instance.address_field_var = tk.StringVar(app_instance, value="")
    app_instance.address_field_var.trace_add("write", create_trace_callback("address_field_var"))

    app_instance.city_var = tk.StringVar(app_instance, value="Whitby")
    app_instance.city_var.trace_add("write", create_trace_callback("city_var"))

    app_instance.province_var = tk.StringVar(app_instance, value="")
    app_instance.province_var.trace_add("write", create_trace_callback("province_var"))

    app_instance.scanner_type_var = tk.StringVar(app_instance, value="Unknown")
    app_instance.scanner_type_var.trace_add("write", create_trace_callback("scanner_type_var"))

    app_instance.selected_antenna_type_var = tk.StringVar(app_instance, value="")
    app_instance.selected_antenna_type_var.trace_add("write", create_trace_callback("selected_antenna_type_var"))

    app_instance.antenna_description_var = tk.StringVar(app_instance, value="")
    app_instance.antenna_description_var.trace_add("write", create_trace_callback("antenna_description_var"))

    app_instance.antenna_use_var = tk.StringVar(app_instance, value="")
    app_instance.antenna_use_var.trace_add("write", create_trace_callback("antenna_use_var"))

    app_instance.antenna_mount_var = tk.StringVar(app_instance, value="")
    app_instance.antenna_mount_var.trace_add("write", create_trace_callback("antenna_mount_var"))

    app_instance.selected_amplifier_type_var = tk.StringVar(app_instance, value="")
    app_instance.selected_amplifier_type_var.trace_add("write", create_trace_callback("selected_amplifier_type_var"))

    app_instance.antenna_amplifier_var = tk.StringVar(app_instance, value="Ground Plane")
    app_instance.antenna_amplifier_var.trace_add("write", create_trace_callback("antenna_amplifier_var"))

    app_instance.amplifier_description_var = tk.StringVar(app_instance, value="")
    app_instance.amplifier_description_var.trace_add("write", create_trace_callback("amplifier_description_var"))

    app_instance.amplifier_use_var = tk.StringVar(app_instance, value="")
    app_instance.amplifier_use_var.trace_add("write", create_trace_callback("amplifier_use_var"))

    app_instance.notes_var = tk.StringVar(app_instance, value="")

    app_instance.last_selected_preset_name_var = tk.StringVar(app_instance, value="")
    app_instance.last_selected_preset_name_var.trace_add("write", create_trace_callback("last_selected_preset_name_var"))

    app_instance.last_loaded_preset_center_freq_mhz_var = tk.StringVar(app_instance, value="")
    app_instance.last_loaded_preset_center_freq_mhz_var.trace_add("write", create_trace_callback("last_loaded_preset_center_freq_mhz_var"))

    app_instance.last_loaded_preset_span_mhz_var = tk.StringVar(app_instance, value="")
    app_instance.last_loaded_preset_span_mhz_var.trace_add("write", create_trace_callback("last_loaded_preset_span_mhz_var"))

    app_instance.last_loaded_preset_rbw_hz_var = tk.StringVar(app_instance, value="")
    app_instance.last_loaded_preset_rbw_hz_var.trace_add("write", create_trace_callback("last_loaded_preset_rbw_hz_var"))


    # Plotting variables (Scan Markers)
    app_instance.include_gov_markers_var = tk.BooleanVar(app_instance, value=True)
    app_instance.include_gov_markers_var.trace_add("write", create_trace_callback("include_gov_markers_var"))

    app_instance.include_tv_markers_var = tk.BooleanVar(app_instance, value=True)
    app_instance.include_tv_markers_var.trace_add("write", create_trace_callback("include_tv_markers_var"))

    app_instance.include_markers_var = tk.BooleanVar(app_instance, value=True)
    app_instance.include_markers_var.trace_add("write", create_trace_callback("include_markers_var"))

    app_instance.include_scan_intermod_markers_var = tk.BooleanVar(app_instance, value=False)
    app_instance.include_scan_intermod_markers_var.trace_add("write", create_trace_callback("include_scan_intermod_markers_var"))

    app_instance.open_html_after_complete_var = tk.BooleanVar(app_instance, value=True)
    app_instance.open_html_after_complete_var.trace_add("write", create_trace_callback("open_html_after_complete_var"))

    app_instance.create_html_var = tk.BooleanVar(app_instance, value=True)
    app_instance.create_html_var.trace_add("write", create_trace_callback("create_html_var"))

    # Plotting variables (Average Markers)
    app_instance.avg_include_gov_markers_var = tk.BooleanVar(app_instance, value=True)
    app_instance.avg_include_gov_markers_var.trace_add("write", create_trace_callback("avg_include_gov_markers_var"))

    app_instance.avg_include_tv_markers_var = tk.BooleanVar(app_instance, value=True)
    app_instance.avg_include_tv_markers_var.trace_add("write", create_trace_callback("avg_include_tv_markers_var"))

    app_instance.avg_include_markers_var = tk.BooleanVar(app_instance, value=True)
    app_instance.avg_include_markers_var.trace_add("write", create_trace_callback("avg_include_markers_var"))

    app_instance.avg_include_intermod_markers_var = tk.BooleanVar(app_instance, value=False)
    app_instance.avg_include_intermod_markers_var.trace_add("write", create_trace_callback("avg_include_intermod_markers_var"))

    app_instance.math_average_var = tk.BooleanVar(app_instance, value=True)
    app_instance.math_average_var.trace_add("write", create_trace_callback("math_average_var"))

    app_instance.math_median_var = tk.BooleanVar(app_instance, value=True)
    app_instance.math_median_var.trace_add("write", create_trace_callback("math_median_var"))

    app_instance.math_range_var = tk.BooleanVar(app_instance, value=True)
    app_instance.math_range_var.trace_add("write", create_trace_callback("math_range_var"))

    app_instance.math_standard_deviation_var = tk.BooleanVar(app_instance, value=True)
    app_instance.math_standard_deviation_var.trace_add("write", create_trace_callback("math_standard_deviation_var"))

    app_instance.math_variance_var = tk.BooleanVar(app_instance, value=True)
    app_instance.math_variance_var.trace_add("write", create_trace_callback("math_variance_var"))

    app_instance.math_psd_var = tk.BooleanVar(app_instance, value=True)
    app_instance.math_psd_var.trace_add("write", create_trace_callback("math_psd_var"))

    # Tkinter variables for band selection checkboxes
    app_instance.band_vars = []
    for band in SCAN_BAND_RANGES:
        band_var = tk.BooleanVar(app_instance, value=False)
        band_var.trace_add("write", create_trace_callback(f"band_var_{band['Band Name']}"))
        app_instance.band_vars.append({"band": band, "var": band_var})

    # Map Tkinter variables to config.ini keys using the new prefixed style
    app_instance.setting_var_map = {
        'general_debug_enabled_var': ('last_GLOBAL__debug_enabled', 'default_GLOBAL__debug_enabled', app_instance.general_debug_enabled_var),
        'log_visa_commands_enabled_var': ('last_GLOBAL__log_visa_commands_enabled', 'default_GLOBAL__log_visa_commands_enabled', app_instance.log_visa_commands_enabled_var),
        'debug_to_terminal_var': ('last_GLOBAL__debug_to_Terminal', 'default_GLOBAL__debug_to_Terminal', app_instance.debug_to_terminal_var),
        'debug_to_file_var': ('last_GLOBAL__debug_to_File', 'default_GLOBAL__debug_to_File', app_instance.debug_to_file_var),
        'include_console_messages_to_debug_file_var': ('last_GLOBAL__include_console_messages_to_debug_file', 'default_GLOBAL__include_console_messages_to_debug_file', app_instance.include_console_messages_to_debug_file_var),
        'debug_to_gui_console_var': ('last_GLOBAL__debug_to_GUI_Console', 'default_GLOBAL__debug_to_GUI_Console', app_instance.debug_to_gui_console_var),
        'paned_window_sash_position_var': ('last_GLOBAL__paned_window_sash_position', 'default_GLOBAL__paned_window_sash_position', app_instance.paned_window_sash_position_var),
        'last_config_save_time_var': ('last_GLOBAL__last_config_save_time', 'default_GLOBAL__last_config_save_time', app_instance.last_config_save_time_var),
        'selected_resource': ('last_instrument_connection__visa_resource', 'default_instrument_connection__visa_resource', app_instance.selected_resource),
        'available_resources': ('last_instrument_connection__available_resources', 'default_instrument_connection__available_resources', app_instance.available_resources),

        'instrument_model_var': ('last_instrument_info__model', 'default_instrument_info__model', app_instance.instrument_model_var),
        'instrument_serial_var': ('last_instrument_info__serial', 'default_instrument_info__serial', app_instance.instrument_serial_var),
        'instrument_firmware_var': ('last_instrument_info__firmware', 'default_instrument_info__firmware', app_instance.instrument_firmware_var),
        'instrument_options_var': ('last_instrument_info__options', 'default_instrument_info__options', app_instance.instrument_options_var),


        'center_freq_mhz_var': ('last_instrument_settings__center_freq_hz', 'default_instrument_settings__center_freq_hz', app_instance.center_freq_mhz_var),
        'span_mhz_var': ('last_instrument_settings__span_hz', 'default_instrument_settings__span_hz', app_instance.span_mhz_var),
        'rbw_hz_var': ('last_instrument_settings__rbw_hz', 'default_instrument_settings__rbw_hz', app_instance.rbw_hz_var),
        'vbw_hz_var': ('last_instrument_settings__vbw_hz', 'default_instrument_settings__vbw_hz', app_instance.vbw_hz_var),
        'sweep_time_s_var': ('last_instrument_settings__sweep_time_s', 'default_instrument_settings__sweep_time_s', app_instance.sweep_time_s_var),

        'scan_name_var': ('last_scan_configuration__scan_name', 'default_scan_configuration__scan_name', app_instance.scan_name_var),
        'output_folder_var': ('last_scan_configuration__scan_directory', 'default_scan_configuration__scan_directory', app_instance.output_folder_var),
        'num_scan_cycles_var': ('last_scan_configuration__num_scan_cycles', 'default_scan_configuration__num_scan_cycles', app_instance.num_scan_cycles_var),
        'rbw_step_size_hz_var': ('last_scan_configuration__rbw_step_size_hz', 'default_scan_configuration__rbw_step_size_hz', app_instance.rbw_step_size_hz_var),
        'cycle_wait_time_seconds_var': ('last_scan_configuration__cycle_wait_time_seconds', 'default_scan_configuration__cycle_wait_time_seconds', app_instance.cycle_wait_time_seconds_var),
        'maxhold_time_seconds_var': ('last_scan_configuration__maxhold_time_seconds', 'default_scan_configuration__maxhold_time_seconds', app_instance.maxhold_time_seconds_var),
        'scan_rbw_hz_var': ('last_scan_configuration__scan_rbw_hz', 'default_scan_configuration__scan_rbw_hz', app_instance.scan_rbw_hz_var),
        'reference_level_dbm_var': ('last_scan_configuration__reference_level_dbm', 'default_scan_configuration__reference_level_dbm', app_instance.reference_level_dbm_var),
        'attenuation_var': ('last_scan_configuration__attenuation', 'default_scan_configuration__attenuation', app_instance.attenuation_var),
        'freq_shift_var': ('last_scan_configuration__freq_shift_hz', 'default_scan_configuration__freq_shift_hz', app_instance.freq_shift_var),
        'scan_mode_var': ('last_scan_configuration__scan_mode', 'default_scan_configuration__scan_mode', app_instance.scan_mode_var),
        'maxhold_enabled_var': ('last_scan_configuration__maxhold_enabled', 'default_scan_configuration__maxhold_enabled', app_instance.maxhold_enabled_var),
        'high_sensitivity_var': ('last_scan_configuration__sensitivity', 'default_scan_configuration__sensitivity', app_instance.high_sensitivity_var),
        'preamp_on_var': ('last_scan_configuration__preamp_on', 'default_scan_configuration__preamp_on', app_instance.preamp_on_var),
        'scan_rbw_segmentation_var': ('last_scan_configuration__scan_rbw_segmentation', 'default_scan_configuration__scan_rbw_segmentation', app_instance.scan_rbw_segmentation_var),
        'desired_default_focus_width_var': ('last_scan_configuration__default_focus_width', 'default_scan_configuration__default_focus_width', app_instance.desired_default_focus_width_var),


        'operator_name_var': ('last_scan_meta_data__operator_name', 'default_scan_meta_data__operator_name', app_instance.operator_name_var),
        'operator_contact_var': ('last_scan_meta_data__contact', 'default_scan_meta_data__contact', app_instance.operator_contact_var),
        'venue_name_var': ('last_scan_meta_data__name', 'default_scan_meta_data__name', app_instance.venue_name_var),

        'venue_postal_code_var': ('last_scan_meta_data__venue_postal_code', 'default_scan_meta_data__venue_postal_code', app_instance.venue_postal_code_var),
        'address_field_var': ('last_scan_meta_data__address_field', 'default_scan_meta_data__address_field', app_instance.address_field_var),
        'city_var': ('last_scan_meta_data__city', 'default_scan_meta_data__city', app_instance.city_var),
        'province_var': ('last_scan_meta_data__province', 'default_scan_meta_data__province', app_instance.province_var),
        'scanner_type_var': ('last_scan_meta_data__scanner_type', 'default_scan_meta_data__scanner_type', app_instance.scanner_type_var),

        'selected_antenna_type_var': ('last_scan_meta_data__selected_antenna_type', 'default_scan_meta_data__selected_antenna_type', app_instance.selected_antenna_type_var),
        'antenna_description_var': ('last_scan_meta_data__antenna_description', 'default_scan_meta_data__antenna_description', app_instance.antenna_description_var),
        'antenna_use_var': ('last_scan_meta_data__antenna_use', 'default_scan_meta_data__antenna_use', app_instance.antenna_use_var),
        'antenna_mount_var': ('last_scan_meta_data__antenna_mount', 'default_scan_meta_data__antenna_mount', app_instance.antenna_mount_var),
        'selected_amplifier_type_var': ('last_scan_meta_data__selected_amplifier_type', 'default_scan_meta_data__selected_amplifier_type', app_instance.selected_amplifier_type_var),
        'antenna_amplifier_var': ('last_scan_meta_data__antenna_amplifier', 'default_scan_meta_data__antenna_amplifier', app_instance.antenna_amplifier_var),
        'amplifier_description_var': ('last_scan_meta_data__amplifier_description', 'default_scan_meta_data__amplifier_description', app_instance.amplifier_description_var),
        'amplifier_use_var': ('last_scan_meta_data__amplifier_use', 'default_scan_meta_data__amplifier_use', app_instance.amplifier_use_var),

        'notes_var': ('last_scan_meta_data__notes', 'default_scan_meta_data__notes', app_instance.notes_var),

        'last_selected_preset_name_var': ('last_instrument_preset__selected_preset_name', 'default_instrument_preset__selected_preset_name', app_instance.last_selected_preset_name_var),
        'last_loaded_preset_center_freq_mhz_var': ('last_instrument_preset__loaded_preset_center_freq_mhz', 'default_instrument_preset__loaded_preset_center_freq_mhz', app_instance.last_loaded_preset_center_freq_mhz_var),
        'last_loaded_preset_span_mhz_var': ('last_instrument_preset__loaded_preset_span_mhz', 'default_instrument_preset__loaded_preset_span_mhz', app_instance.last_loaded_preset_span_mhz_var),
        'last_loaded_preset_rbw_hz_var': ('last_instrument_preset__loaded_preset_rbw_hz', 'default_instrument_preset__loaded_preset_rbw_hz', app_instance.last_loaded_preset_rbw_hz_var),


        'include_gov_markers_var': ('last_plotting__scan_markers_to_plot__include_gov_markers', 'default_plotting__scan_markers_to_plot__include_gov_markers', app_instance.include_gov_markers_var),
        'include_tv_markers_var': ('last_plotting__scan_markers_to_plot__include_tv_markers', 'default_plotting__scan_markers_to_plot__include_tv_markers', app_instance.include_tv_markers_var),
        'include_markers_var': ('last_plotting__scan_markers_to_plot__include_markers', 'default_plotting__scan_markers_to_plot__include_markers', app_instance.include_markers_var),
        'include_scan_intermod_markers_var': ('last_plotting__scan_markers_to_plot__include_intermod_markers', 'default_plotting__scan_markers_to_plot__include_intermod_markers', app_instance.include_scan_intermod_markers_var),
        'open_html_after_complete_var': ('last_plotting__scan_markers_to_plot__open_html_after_complete', 'default_plotting__scan_markers_to_plot__open_html_after_complete', app_instance.open_html_after_complete_var),
        'create_html_var': ('last_plotting__scan_markers_to_plot__create_html', 'default_plotting__scan_markers_to_plot__create_html', app_instance.create_html_var),

        'avg_include_gov_markers_var': ('last_plotting__average_markers_to_plot__include_gov_markers', 'default_plotting__average_markers_to_plot__include_gov_markers', app_instance.avg_include_gov_markers_var),
        'avg_include_tv_markers_var': ('last_plotting__average_markers_to_plot__include_tv_markers', 'default_plotting__average_markers_to_plot__include_tv_markers', app_instance.avg_include_tv_markers_var),
        'avg_include_markers_var': ('last_plotting__average_markers_to_plot__include_markers', 'default_plotting__average_markers_to_plot__include_markers', app_instance.avg_include_markers_var),
        'avg_include_intermod_markers_var': ('last_plotting__average_markers_to_plot__include_intermod_markers', 'default_plotting__average_markers_to_plot__include_intermod_markers', app_instance.avg_include_intermod_markers_var),
        'math_average_var': ('last_plotting__average_markers_to_plot__math_average', 'default_plotting__average_markers_to_plot__math_average', app_instance.math_average_var),
        'math_median_var': ('last_plotting__average_markers_to_plot__math_median', 'default_plotting__average_markers_to_plot__math_median', app_instance.math_median_var),
        'math_range_var': ('last_plotting__average_markers_to_plot__math_range', 'default_plotting__average_markers_to_plot__math_range', app_instance.math_range_var),
        'math_standard_deviation_var': ('last_plotting__average_markers_to_plot__math_standard_deviation', 'default_plotting__average_markers_to_plot__math_standard_deviation', app_instance.math_standard_deviation_var),
        'math_variance_var': ('last_plotting__average_markers_to_plot__math_variance', 'default_plotting__average_markers_to_plot__math_variance', app_instance.math_variance_var),
        'math_psd_var': ('last_plotting__average_markers_to_plot__math_psd', 'default_plotting__average_markers_to_plot__math_psd', app_instance.math_psd_var),
    }
