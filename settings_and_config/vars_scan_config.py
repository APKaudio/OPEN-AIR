# settings_and_config/vars_scan_config.py
#
# This module defines and initializes Tkinter variables for scan-related
# settings and configurations.
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
# Version 20250821.220500.1
# NEW: Created a new file to house scan configuration variables.

import tkinter as tk
import inspect
import os
from display.debug_logic import debug_log
from ref.ref_program_default_values import DEFAULT_CONFIG
from ref.ref_frequency_bands import SCAN_BAND_RANGES

# --- Version Information ---
current_version = "20250821.220500.1"
current_version_hash = (20250821 * 220500 * 1)
current_file = f"{os.path.basename(__file__)}"


def setup_scan_config_vars(app_instance):
    """
    Initializes all the Tkinter variables for scan configuration settings.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"⚙️ 🟢 Entering {current_function} to set up scan configuration variables. ⚡",
                file=current_file,
                version=current_version,
                function=current_function)

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

    debug_log(f"⚙️ ✅ Exiting {current_function}",
                file=current_file,
                version=current_version,
                function=current_function)