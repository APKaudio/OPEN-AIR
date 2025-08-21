# settings_and_config/vars_app_and_debug.py
#
# This module defines and initializes Tkinter variables for application-wide
# settings, including window state and debug controls.
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
# NEW: Created a new file to house application-wide and debugging variables.

import tkinter as tk
import inspect
import os
from datetime import datetime
from display.debug_logic import debug_log
from ref.ref_program_default_values import DEFAULT_CONFIG

# --- Version Information ---
current_version = "20250821.220500.1"
current_version_hash = (20250821 * 220500 * 1)
current_file = f"{os.path.basename(__file__)}"

def setup_app_and_debug_vars(app_instance):
    """
    Initializes application and debugging-related Tkinter variables.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"⚙️ 🟢 Entering {current_function} to set up application and debug variables.",
                file=current_file,
                version=current_version,
                function=current_function)

    # --- Application Variables ---
    app_instance.is_connected = tk.BooleanVar(app_instance, value=False)
    app_instance.is_running = tk.BooleanVar(app_instance, value=False)
    app_instance.last_config_save_time_var = tk.StringVar(app_instance, value="")
    app_instance.geometry_string = DEFAULT_CONFIG['Application']['geometry']
    app_instance.window_state_string = DEFAULT_CONFIG['Application']['window_state']
    app_instance.paned_window_sash_position_percentage_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Application']['paned_window_sash_position_percentage'])
    app_instance.last_config_save_time_var.set(DEFAULT_CONFIG['Application']['last_config_save_time'])
    
    # --- Debugging Variables ---
    app_instance.general_debug_enabled_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['general_debug_enabled'] == 'True')
    app_instance.debug_to_gui_console_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['debug_to_gui_console'] == 'True')
    app_instance.debug_to_terminal_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['debug_to_terminal'] == 'True')
    app_instance.debug_to_file_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['debug_to_file'] == 'True')
    app_instance.include_console_messages_to_debug_file_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['include_console_messages_to_debug_file'] == 'True')
    app_instance.log_visa_commands_enabled_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['log_visa_commands_enabled'] == 'True')
    app_instance.log_truncation_enabled_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['log_truncation_enabled'] == 'True')
    app_instance.include_visa_messages_to_debug_file_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Debug']['include_visa_messages_to_debug_file'] == 'True')
    
    debug_log(f"⚙️ ✅ Exiting {current_function}",
                file=current_file,
                version=current_version,
                function=current_function)