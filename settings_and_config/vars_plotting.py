# settings_and_config/vars_plotting.py
#
# This module defines and initializes Tkinter variables for plotting-related
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
# NEW: Created a new file to house plotting variables.

import tkinter as tk
import inspect
import os
from display.debug_logic import debug_log
from ref.ref_program_default_values import DEFAULT_CONFIG

# --- Version Information ---
current_version = "20250821.220500.1"
current_version_hash = (20250821 * 220500 * 1)
current_file = f"{os.path.basename(__file__)}"

def setup_plotting_vars(app_instance):
    """
    Initializes all the Tkinter variables for plotting settings.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"⚙️ 🟢 Entering {current_function} to set up plotting variables. 📈",
                file=current_file,
                version=current_version,
                function=current_function)

    # --- Plotting Variables ---
    app_instance.current_style_theme_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Plotting']['current_style_theme'])
    app_instance.plot_grid_on_var = tk.BooleanVar(app_instance, value=DEFAULT_CONFIG['Plotting']['plot_grid_on'] == 'True')
    app_instance.plot_grid_alpha_var = tk.DoubleVar(app_instance, value=float(DEFAULT_CONFIG['Plotting']['plot_grid_alpha']))
    app_instance.plot_grid_color_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Plotting']['plot_grid_color'])
    
    debug_log(f"⚙️ ✅ Exiting {current_function}",
                version=current_version,
                function=current_function)