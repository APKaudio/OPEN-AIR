# src/settings_and_config/config_manager_plotting.py
#
# This file provides the backend logic for saving plotting-related settings.
# It is designed to be modular and self-contained, handling only its specific domain.
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
# Version 20250821.093800.1
# REFACTORED: Created a new, dedicated module for saving plotting settings.

import os
import inspect
from configparser import ConfigParser
from display.debug_logic import debug_log
from display.console_logic import console_log

# --- Versioning ---
w = 20250821
x_str = '093800'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"


def _save_plotting_settings(config, app_instance, console_print_func):
    """Saves plotting-related settings."""
    current_function = inspect.currentframe().f_code.co_name
    changed_count = 0
    section = 'Plotting'
    if not config.has_section(section):
        config.add_section(section)
    
    try:
        if hasattr(app_instance, 'current_style_theme_var'):
            new_value = str(app_instance.current_style_theme_var.get())
            if config.get(section, 'current_style_theme', fallback=None) != new_value:
                config.set(section, 'current_style_theme', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'current_style_theme' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        
        if hasattr(app_instance, 'plot_grid_on_var'):
            new_value = str(app_instance.plot_grid_on_var.get())
            if config.get(section, 'plot_grid_on', fallback=None) != new_value:
                config.set(section, 'plot_grid_on', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'plot_grid_on' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
                
        if hasattr(app_instance, 'plot_grid_alpha_var'):
            new_value = str(app_instance.plot_grid_alpha_var.get())
            if config.get(section, 'plot_grid_alpha', fallback=None) != new_value:
                config.set(section, 'plot_grid_alpha', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'plot_grid_alpha' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        
        if hasattr(app_instance, 'plot_grid_color_var'):
            new_value = str(app_instance.plot_grid_color_var.get())
            if config.get(section, 'plot_grid_color', fallback=None) != new_value:
                config.set(section, 'plot_grid_color', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'plot_grid_color' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        
        if changed_count > 0:
            debug_log(f"🔧💾🔧💾✅ Plotting settings saved.", file=current_file, version=current_version, function=current_function)
        else:
            debug_log(f"🔧💾😴 No changes to save in Plotting settings.", file=current_file, version=current_version, function=current_function)

    except Exception as e:
        debug_log(f"🔧💾❌ Error saving {section} settings: {e}", file=current_file, version=current_version, function=current_function)