# src/settings_and_config/program_default_values.py
#
# This file contains the default configuration settings for the application.
# It defines the structure and initial values for the config.ini file,
# ensuring that the application has a valid configuration to start with.
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
# Version 20250823.140000.1
# FIXED: The BASE_DIR calculation has been corrected to properly point to the
#        root 'OPEN-AIR' directory, resolving the 'config.ini' pathing error.
# UPDATED: Added new MarkerTab configuration keys for a more comprehensive default state.

import os
from datetime import datetime

# Import the main frequency bands data
from ref.frequency_bands import SCAN_BAND_RANGES

# --- Version Information ---
w = 20250823
x_str = '140000'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"{w}.{x_str}.{y}"
current_version_hash = w * x * y


# --- Path Constants ---
# CORRECTED: The BASE_DIR calculation is now relative to the parent of the `src` folder.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_FOLDER_PATH = os.path.join(BASE_DIR, 'DATA')
CONFIG_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'config.ini')
PRESETS_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'PRESETS.CSV')
MARKERS_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'MARKERS.CSV')
VISA_COMMANDS_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'visa_commands.csv')
DEBUG_COMMANDS_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'DEBUG_SOFTWARE.log')

# --- Default Settings ---
DEFAULT_CONFIG = {
    'Application': {
        'geometry': '1600x900+100+100',
        'window_state': 'normal',
        'last_config_save_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'paned_window_sash_position_percentage': '45',
    },
    'Debug': {
        'general_debug_enabled': 'True',
        'debug_to_gui_console': 'True',
        'debug_to_terminal': 'False',
        'debug_to_file': 'True',
        'include_console_messages_to_debug_file': 'True',
        'log_visa_commands_enabled': 'False',
        'log_truncation_enabled': 'True',
        'include_visa_messages_to_debug_file': 'True',
    },
    'Instrument': {
        'visa_resource': 'TCPIP0::192.168.1.100::inst0::INSTR',
    },
    'InstrumentSettings': {
        'center_freq_mhz': '1500',
        'span_freq_mhz': '3000',
        'start_freq_mhz': '0',
        'stop_freq_mhz': '3000',
        'rbw_mhz': '1',
        'vbw_mhz': '1',
        'vbw_auto_on': 'True',
        'initiate_continuous_on': 'True',
        'ref_level_dbm': '-30',
        'preamp_on': 'False',
        'power_attenuation_db': '10',
        'high_sensitivity_on': 'False',
        'trace1_mode': 'WRITE',
        'trace2_mode': 'MAXHOLD',
        'trace3_mode': 'BLANK',
        'trace4_mode': 'BLANK',
        'marker1_on': 'False',
        'marker2_on': 'False',
        'marker3_on': 'False',
        'marker4_on': 'False',
        'marker5_on': 'False',
        'marker6_on': 'False',
    },
    'MarkerTab': {
        'span_hz': '1000000',
        'rbw_hz': '100000',
        'trace_live': 'True',
        'trace_max_hold': 'False',
        'trace_min_hold': 'False',
        'buffer_mhz': '3.0',
        'poke_freq_mhz': '444.444444',
        'buffered_start_var': '0.0',
        'buffered_stop_var': '0.0',
        'zone_selected': 'None',
        'zone_zoom_button_selected_name': '',
        'zone_zoom_label': '',
        'zone_zoom_start': '',
        'zone_zoom_stop': '',
        'zone_device_count': '0',
        'zone_group_count': '0',
        'group_selected': 'None',
        'group_zoom_button_selected': '',
        'group_zoom_label': '',
        'group_zoom_start': '',
        'group_zoom_stop': '',
        'group_device_count': '0',
        'device_selected_name': '',
        'device_selected_device_type': '',
        'device_selected_center': '',
    },
    'Scan': {
        'output_folder': os.path.join(DATA_FOLDER_PATH, 'SCANS'),
        'scan_name': 'DefaultScan',
        'rbw_step_size_hz': '20000',
        'num_scan_cycles': '1',
        'cycle_wait_time_seconds': '0',
        'maxhold_enabled': 'False',
        'maxhold_time_seconds': '10',
        'desired_default_focus_width': '5000000',
        'create_html': 'True',
        'open_html_after_complete': 'True',
        'include_markers': 'True',
        'include_gov_markers': 'True',
        'include_tv_markers': 'True',
        'include_scan_intermod_markers': 'True',
        'math_average': 'True',
        'math_median': 'True',
        'math_variance': 'True',
        'math_standard_deviation': 'True',
        'math_range': 'True',
        'math_psd': 'True',
        'last_scan_configuration__selected_bands_levels': ','.join(
            [f"{band['Band Name']}=1" for band in SCAN_BAND_RANGES]
        ),
    },
    'Antenna': {
        'selected_antenna_type': 'Generic',
        'antenna_description': 'Broadband Omni',
        'antenna_use': 'General Purpose',
        'antenna_mount': 'Tripod',
        'antenna_amplifier': 'None',
    },
    'Amplifier': {
        'selected_amplifier_type': 'Generic',
        'amplifier_description': 'Inline LNA',
        'amplifier_use': 'Compensate for cable loss',
    },
    'Report': {
        'operator_name': 'RF Technician',
        'operator_contact': 'tech@example.com',
        'venue_name': 'Default Venue',
        'address_field': '123 Main St',
        'city': 'Anytown',
        'province': 'ON',
        'venue_postal_code': 'A1B 2C3',
        'notes': 'This is a default report generated by the OPEN-AIR software.',
        'freq_shift': '0',
        'scanner_type': 'Generic RF Scanner',
    },
    'Plotting': {
        'current_style_theme': 'dark',
        'plot_grid_on': 'True',
        'plot_grid_alpha': '0.5',
        'plot_grid_color': 'gray',
    },
}