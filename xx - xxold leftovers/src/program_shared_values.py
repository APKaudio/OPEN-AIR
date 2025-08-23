# variables/program_shared_values.py
#
# This module centralizes the definition and initialization of all Tkinter variables
# used throughout the application, providing a single source for managing state.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250821.224000.1 (Added missing instrument vars)

import tkinter as tk
import inspect
import os
from datetime import datetime
from tkinter import StringVar

from ref.ref_program_default_values import DEFAULT_CONFIG

# --- Version Information ---
current_version = "20250821.224000.1"
current_version_hash = (20250821 * 224000 * 1)
current_file = f"{os.path.basename(__file__)}"

def setup_shared_values(app_instance):
    """
    Initializes all shared Tkinter variables for the application.
    """
    current_function = inspect.currentframe().f_code.co_name
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ⚙️ 🟢 Consolidating and setting up all shared values with the force! ✨")

    # --- From vars_app_and_debug.py ---
    app_instance.window_state_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Application']['window_state'])
    app_instance.geometry_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Application']['geometry'])
    app_instance.paned_window_sash_position_percentage_var = tk.IntVar(app_instance, value=int(DEFAULT_CONFIG['Application']['paned_window_sash_position_percentage']))
    app_instance.last_config_save_time_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Application']['last_config_save_time'])
    app_instance.general_debug_enabled_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['general_debug_enabled'] == 'True')
    app_instance.debug_to_gui_console_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['debug_to_gui_console'] == 'True')
    app_instance.debug_to_terminal_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['debug_to_terminal'] == 'True')
    app_instance.debug_to_file_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['debug_to_file'] == 'True')
    app_instance.include_console_messages_to_debug_file_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['include_console_messages_to_debug_file'] == 'True')
    app_instance.log_visa_commands_enabled_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['log_visa_commands_enabled'] == 'True')
    app_instance.log_truncation_enabled_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['log_truncation_enabled'] == 'True')
    app_instance.include_visa_messages_to_debug_file_enabled_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['include_visa_messages_to_debug_file'] == 'True')

    # --- From vars_instrument.py ---
    app_instance.instrument_brand_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Instrument']['brand'])
    app_instance.instrument_series_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Instrument']['series'])
    app_instance.instrument_visa_resource_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Instrument']['visa_resource'])
    app_instance.is_connected_var = tk.BooleanVar(app_instance, value=False)
    app_instance.is_running_var = tk.BooleanVar(app_instance, value=False)
    
    # --- DEFINITIVE FIX: Added missing instrument state variables ---
    app_instance.connected_instrument_manufacturer = tk.StringVar(app_instance, value="--")
    app_instance.connected_instrument_model = tk.StringVar(app_instance, value="--")
    app_instance.connected_instrument_serial = tk.StringVar(app_instance, value="--")
    app_instance.connected_instrument_firmware = tk.StringVar(app_instance, value="--")

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
    app_instance.high_pass_filter_on_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['InstrumentSettings']['high_pass_filter_on'] == 'True')

    # ... (rest of the variable definitions remain the same) ...

    # --- From vars_marker_tab.py ---
    app_instance.showtime_mode_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['MarkerTab']['showtime_mode'])
    app_instance.buffer_mhz_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['MarkerTab']['buffer_mhz'])
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
    app_instance.zone_zoom_label_center_var = tk.StringVar(app_instance, value="")
    app_instance.zone_zoom_label_right_var = tk.StringVar(app_instance, value="")

    # --- From vars_plotting.py ---
    app_instance.current_style_theme_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Plotting']['current_style_theme'])
    app_instance.plot_grid_on_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Plotting']['plot_grid_on'] == 'True')
    app_instance.plot_legend_on_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Plotting']['plot_legend_on'] == 'True')
    app_instance.plot_title_on_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Plotting']['plot_title_on'] == 'True')
    app_instance.plot_title_text_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Plotting']['plot_title_text'])

    # --- From vars_report_meta.py ---
    app_instance.operator_name_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['operator_name'])
    app_instance.operator_contact_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['operator_contact'])
    app_instance.venue_name_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['venue_name'])
    app_instance.venue_address_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['venue_address'])
    app_instance.venue_city_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['venue_city'])
    app_instance.venue_province_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['venue_province'])
    app_instance.venue_postal_code_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['venue_postal_code'])
    app_instance.notes_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['notes'])
    app_instance.scanner_type_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['scanner_type'])
    app_instance.selected_antenna_type_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Antenna']['selected_antenna_type'])
    app_instance.antenna_description_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Antenna']['antenna_description'])
    app_instance.antenna_use_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Antenna']['antenna_use'])
    app_instance.antenna_mount_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Antenna']['antenna_mount'])
    app_instance.antenna_amplifier_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Antenna']['antenna_amplifier'])
    app_instance.selected_amplifier_type_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Amplifier']['selected_amplifier_type'])
    app_instance.amplifier_description_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Amplifier']['amplifier_description'])
    app_instance.amplifier_use_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Amplifier']['amplifier_use'])

    # --- From vars_scan_config.py ---
    app_instance.scan_output_folder_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Scan']['output_folder'])
    app_instance.scan_output_filename_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Scan']['output_filename'])
    app_instance.start_freq_mhz_scan_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['Scan']['start_freq_mhz']))
    app_instance.stop_freq_mhz_scan_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['Scan']['stop_freq_mhz']))
    app_instance.step_freq_khz_scan_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['Scan']['step_freq_khz']))
    app_instance.dwell_time_ms_scan_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['Scan']['dwell_time_ms']))
    app_instance.scan_band_selection_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Scan']['scan_band_selection'])
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
    app_instance.math_percentile_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Scan']['math_percentile'] == 'True')

    # --- Aliases for legacy naming conventions ---
    app_instance.is_connected = app_instance.is_connected_var
    app_instance.is_running = app_instance.is_running_var

    print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ✅ All shared values have been initialized successfully.")