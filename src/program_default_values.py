# src/program_default_values.py
#
# This module centralizes the definition of default values and file paths
# used throughout the RF Spectrum Analyzer Controller application.
# This helps in maintaining a single source of truth for these configurations,
# making the application more maintainable and easier to update.
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
# Version 20250803.1515.0 (Initial creation: Moved constant declarations from main_app.py)
# Version 20250803.1520.0 (Removed CURRENT_APP_VERSION_STRING and CURRENT_APP_VERSION_HASH_VALUE as they are dynamic and belong in main_app.py.)
# Version 20250803.1545.0 (Moved DEFAULT_CONFIG_SETTINGS from config_manager.py to this file.)

import os

# Get the directory of the current script (program_default_values.py)
_script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the root directory of the OPEN-AIR application (one level up from src)
OPEN_AIR_ROOT_DIR = os.path.abspath(os.path.join(_script_dir, os.pardir))

# Define paths relative to the OPEN-AIR_ROOT_DIR
DATA_FOLDER_PATH = os.path.join(OPEN_AIR_ROOT_DIR, 'DATA')
CONFIG_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'config.ini')
PRESETS_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'PRESETS.CSV')
MARKERS_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'MARKERS.CSV')
VISA_COMMANDS_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'VISA_COMMANDS.CSV')
DEBUG_COMMANDS_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'Debug.log')

# Default window geometry for the main application window
DEFAULT_WINDOW_GEOMETRY = "1400x780+100+100"

# Default configuration settings for the application
DEFAULT_CONFIG_SETTINGS = {
    'default_GLOBAL__debug_enabled': 'False',
    'default_GLOBAL__log_visa_commands_enabled': 'False',
    'default_GLOBAL__debug_to_Terminal': 'False',
    'default_GLOBAL__paned_window_sash_position': '700',
    'default_GLOBAL__window_geometry': '1400x780+100+100',
    'default_GLOBAL__last_config_save_time': 'Never',
    'default_GLOBAL__include_console_messages_to_debug_file': 'False',

    'default_instrument_connection__visa_resource': '',

    'default_scan_configuration__scan_name': 'New Scan',
    'default_scan_configuration__scan_directory': os.path.join(os.path.expanduser('~'), 'Documents', 'OPEN-AIR-Scans'),
    'default_scan_configuration__num_scan_cycles': '1',
    'default_scan_configuration__rbw_step_size_hz': '10000',
    'default_scan_configuration__cycle_wait_time_seconds': '0.5',
    'default_scan_configuration__maxhold_time_seconds': '3',
    'default_scan_configuration__scan_rbw_hz': '10000',
    'default_scan_configuration__reference_level_dbm': '-40',
    'default_scan_configuration__freq_shift_hz': '0',
    'default_scan_configuration__maxhold_enabled': 'True',
    'default_scan_configuration__sensitivity': 'True',
    'default_scan_configuration__preamp_on': 'True',
    'default_scan_configuration__scan_rbw_segmentation': '1000000.0',
    'default_scan_configuration__default_focus_width': '10000.0',
    'default_scan_configuration__selected_bands': '[]',

    'default_scan_meta_data__operator_name': 'Anthony Peter Kuzub',
    'default_scan_meta_data__contact': 'I@Like.audio',
    'default_scan_meta_data__name': 'My Venue',
    'default_scan_meta_data__venue_postal_code': '',
    'default_scan_meta_data__address_field': '',
    'default_scan_meta_data__city': 'Whitby',
    'default_scan_meta_data__province': 'Ontario',
    'default_scan_meta_data__scanner_type': 'Unknown',
    'default_scan_meta_data__selected_antenna_type': '',
    'default_scan_meta_data__antenna_description': '',
    'default_scan_meta_data__antenna_use': '',
    'default_scan_meta_data__antenna_mount': '',
    'default_scan_meta_data__selected_amplifier_type': '',
    'default_scan_meta_data__antenna_amplifier': '',
    'default_scan_meta_data__amplifier_description': '',
    'default_scan_meta_data__amplifier_use': '',
    'default_scan_meta_data__notes': 'Enter any notes about the scan here.',

    'default_instrument_preset__selected_preset_name': '',
    'default_instrument_preset__loaded_preset_center_freq_mhz': '',
    'default_instrument_preset__loaded_preset_span_mhz': '',
    'default_instrument_preset__loaded_preset_rbw_hz': '',

    'default_plotting__scan_markers_to_plot__include_gov_markers': 'True',
    'default_plotting__scan_markers_to_plot__include_tv_markers': 'True',
    'default_plotting__scan_markers_to_plot__include_markers': 'True',
    'default_plotting__scan_markers_to_plot__include_intermod_markers': 'False',
    'default_plotting__scan_markers_to_plot__open_html_after_complete': 'True',
    'default_plotting__scan_markers_to_plot__create_html': 'True',

    'default_plotting__average_markers_to_plot__include_gov_markers': 'True',
    'default_plotting__average_markers_to_plot__include_tv_markers': 'True',
    'default_plotting__average_markers_to_plot__include_markers': 'True',
    'default_plotting__average_markers_to_plot__include_intermod_markers': 'False',
    'default_plotting__average_markers_to_plot__math_average': 'True',
    'default_plotting__average_markers_to_plot__math_median': 'True',
    'default_plotting__average_markers_to_plot__math_range': 'True',
    'default_plotting__average_markers_to_plot__math_standard_deviation': 'True',
    'default_plotting__average_markers_to_plot__math_variance': 'True',
    'default_plotting__average_markers_to_plot__math_psd': 'True',
}
