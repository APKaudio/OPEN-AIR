# settings_and_config/vars_marker_tab.py
#
# This module defines and initializes Tkinter variables for the Marker tab,
# including state variables for selections, displays, and controls.
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
# NEW: Created a new file to house Marker tab variables.

import tkinter as tk
import inspect
import os
from display.debug_logic import debug_log
from ref.ref_program_default_values import DEFAULT_CONFIG

# --- Version Information ---
current_version = "20250821.220500.1"
current_version_hash = (20250821 * 220500 * 1)
current_file = f"{os.path.basename(__file__)}"

def setup_marker_tab_vars(app_instance):
    """
    Initializes all the Tkinter variables for the Marker tab.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"⚙️ 🟢 Entering {current_function} to set up Marker tab variables. 🗺️",
                file=current_file,
                version=current_version,
                function=current_function)

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
    
    debug_log(f"⚙️ ✅ Exiting {current_function}",
                file=current_file,
                version=current_version,
                function=current_function)