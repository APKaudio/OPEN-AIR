
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
# Version 20250814.215500.1 (FIXED: Added initialization for new debug-related Tkinter variables to resolve AttributeError on startup.)


import tkinter as tk
import inspect
import os
from datetime import datetime

from display.debug_logic import debug_log
from ref.frequency_bands import SCAN_BAND_RANGES

# --- Version Information ---
current_version = "20250814.215500.1"
current_version_hash = (20250814 * 215500 * 1)


def setup_shared_values(app_instance):
    """
    Initializes all the shared Tkinter variables for the application.
    This function should be called once during program initialization.
    
    Args:
        app_instance: The main application instance (tk.Tk()).
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"⚙️ 🟢 Setting up shared values with the force! ✨",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)

    # Lazily import DEFAULT_CONFIG to break circular dependency
    from src.settings_and_config.program_default_values import DEFAULT_CONFIG

    # --- Application & Debugging Variables ---
    app_instance.is_connected = tk.BooleanVar(app_instance, value=False)
    app_instance.is_running = tk.BooleanVar(app_instance, value=False)
    app_instance.last_config_save_time_var = tk.StringVar(app_instance, value="")
    app_instance.general_debug_enabled_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['general_debug_enabled'] == 'True')
    app_instance.debug_to_gui_console_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['debug_to_gui_console'] == 'True')
    app_instance.debug_to_terminal_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['debug_to_terminal'] == 'True')
    app_instance.debug_to_file_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['debug_to_file'] == 'True')
    app_instance.include_console_messages_to_debug_file_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['include_console_messages_to_debug_file'] == 'True')
    app_instance.log_visa_commands_enabled_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['log_visa_commands_enabled'] == 'True')
    app_instance.log_truncation_enabled_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['log_truncation_enabled'] == 'True')
    app_instance.include_visa_messages_to_debug_file_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['include_visa_messages_to_debug_file'] == 'True')



    app_instance.general_geometry_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Application']['geometry'] == '1600x900+100+100')
    app_instance.window_state_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Application']['window_state'] == 'normal')
    app_instance.last_config_save_time_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Application']['window_state'] == '')
    app_instance.paned_window_sash_position_percentage_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Application']['paned_window_sash_position_percentage'] == '45')

    app_instance.connected_instrument_manufacturer = tk.StringVar(app_instance, value="N/A")
    app_instance.connected_instrument_model = tk.StringVar(app_instance, value="N/A")
    app_instance.connected_instrument_serial = tk.StringVar(app_instance, value="N/A")
    app_instance.connected_instrument_version = tk.StringVar(app_instance, value="N/A")

    # --- Marker Tab Variables ---
    app_instance.span_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['MarkerTab']['span_hz'])
    app_instance.rbw_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['MarkerTab']['rbw_hz'])
    app_instance.buffer_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['MarkerTab']['buffer_mhz'])
    app_instance.poke_freq_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['MarkerTab']['poke_freq_mhz']))
    app_instance.trace_modes = {
        'live': tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['MarkerTab']['trace_live'] == 'True'),
        'max': tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['MarkerTab']['trace_max_hold'] == 'True'),
        'min': tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['MarkerTab']['trace_min_hold'] == 'True'),
    }
    app_instance.buffered_start_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['MarkerTab']['buffered_start_var']))
    app_instance.buffered_stop_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['MarkerTab']['buffered_stop_var']))
    
    app_instance.selected_zone = None
    app_instance.selected_zone_info = {}
    app_instance.selected_group = None
    app_instance.selected_group_info = {}
    app_instance.selected_device_info = None
    app_instance.last_selected_type = None

    app_instance.zone_zoom_label_left_var = tk.StringVar(app_instance, value="")
    app_instance.zone_zoom_label_center_var = tk.StringVar(app_instance, value="N/A")
    app_instance.zone_zoom_label_right_var = tk.StringVar(app_instance, value="")

    # --- Instrument Variables ---
    app_instance.instrument_visa_resource_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Instrument']['visa_resource'])
    app_instance.center_freq_mhz_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['InstrumentSettings']['center_freq_mhz']))
    app_instance.span_freq_mhz_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['InstrumentSettings']['span_freq_mhz']))
    app_instance.start_freq_mhz_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['InstrumentSettings']['start_freq_mhz']))
    app_instance.stop_freq_mhz_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['InstrumentSettings']['stop_freq_mhz']))
    app_instance.rbw_mhz_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['InstrumentSettings']['rbw_mhz']))
    app_instance.vbw_mhz_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['InstrumentSettings']['vbw_mhz']))
    app_instance.vbw_auto_on_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['InstrumentSettings']['vbw_auto_on'] == 'True')
    app_instance.initiate_continuous_on_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['InstrumentSettings']['initiate_continuous_on'] == 'True')
    app_instance.ref_level_dbm_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['InstrumentSettings']['ref_level_dbm']))
    app_instance.preamp_on_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['InstrumentSettings']['preamp_on'] == 'True')
    app_instance.power_attenuation_db_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['InstrumentSettings']['power_attenuation_db']))
    app_instance.high_sensitivity_on_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['InstrumentSettings']['high_sensitivity_on'] == 'True')
    app_instance.connected_instrument_instance = None # Placeholder for the VISA connection object

    # --- Scan Configuration Variables ---
    app_instance.scan_name_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Scan']['scan_name'])
    app_instance.output_folder_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Scan']['output_folder'])
    app_instance.rbw_step_size_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['Scan']['rbw_step_size_hz']))
    app_instance.num_scan_cycles_var = tk.IntVar(app_instance, value=int(DEFAULT_CONFIG['Scan']['num_scan_cycles']))
    app_instance.cycle_wait_time_seconds_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['Scan']['cycle_wait_time_seconds']))
    app_instance.maxhold_enabled_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Scan']['maxhold_enabled'] == 'True')
    app_instance.maxhold_time_seconds_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['Scan']['maxhold_time_seconds']))
    app_instance.desired_default_focus_width_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['Scan']['desired_default_focus_width']))
    app_instance.create_html_report_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Scan']['create_html'] == 'True')
    app_instance.open_html_after_complete_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Scan']['open_html_after_complete'] == 'True')
    app_instance.include_markers_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Scan']['include_markers'] == 'True')
    app_instance.include_gov_markers_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Scan']['include_gov_markers'] == 'True')
    app_instance.include_tv_markers_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Scan']['include_tv_markers'] == 'True')
    app_instance.include_scan_intermod_markers_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Scan']['include_scan_intermod_markers'] == 'True')
    app_instance.math_average_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Scan']['math_average'] == 'True')
    app_instance.math_median_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Scan']['math_median'] == 'True')
    app_instance.math_variance_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Scan']['math_variance'] == 'True')
    app_instance.math_standard_deviation_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Scan']['math_standard_deviation'] == 'True')
    app_instance.math_range_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Scan']['math_range'] == 'True')
    app_instance.math_psd_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Scan']['math_psd'] == 'True')
    app_instance.selected_bands_levels = []

    # --- Antenna Variables ---
    app_instance.selected_antenna_type_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Antenna']['selected_antenna_type'])
    app_instance.antenna_description_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Antenna']['antenna_description'])
    app_instance.antenna_use_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Antenna']['antenna_use'])
    app_instance.antenna_mount_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Antenna']['antenna_mount'])
    app_instance.antenna_amplifier_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Antenna']['antenna_amplifier'])

    # --- Amplifier Variables ---
    app_instance.selected_amplifier_type_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Amplifier']['selected_amplifier_type'])
    app_instance.amplifier_description_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Amplifier']['amplifier_description'])
    app_instance.amplifier_use_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Amplifier']['amplifier_use'])
    
    # --- Report Variables ---
    app_instance.operator_name_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['operator_name'])
    app_instance.operator_contact_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['operator_contact'])
    app_instance.venue_name_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['venue_name'])
    app_instance.address_field_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['address_field'])
    app_instance.city_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['city'])
    app_instance.province_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['province'])
    app_instance.venue_postal_code_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['venue_postal_code'])
    app_instance.notes_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['notes'])
    app_instance.scanner_type_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['scanner_type'])    
    
    # --- Plotting Variables ---
    app_instance.current_style_theme_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Plotting']['current_style_theme'])
    app_instance.plot_grid_on_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Plotting']['plot_grid_on'] == 'True')
    app_instance.plot_grid_alpha_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['Plotting']['plot_grid_alpha']))
    app_instance.plot_grid_color_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Plotting']['plot_grid_color'])
    
    debug_log(f"⚙️ ✅ Exiting {current_function}",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)