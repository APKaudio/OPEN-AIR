# FolderName/config_manager_application.py
#
# This file provides the backend logic for saving application-level settings like
# window geometry and state to the configuration file. It is designed to be
# modular and self-contained, handling only its specific domain.
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
# Version 20250821.093800.6
# REFACTORED: The save_application_settings function was updated to correctly reference
#             the geometry and window state from the main app instance.

import os
import inspect
from configparser import ConfigParser
from datetime import datetime
from display.debug_logic import debug_log
from display.console_logic import console_log

# --- Versioning ---
w = 20250821
x_str = '093800'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 6
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"

def _save_application_settings(config, app_instance, console_print_func):
    """Saves application-level settings like window geometry and state."""
    current_function = inspect.currentframe().f_code.co_name
    changed_count = 0
    section = 'Application'
    if not config.has_section(section):
        config.add_section(section)

    try:
        # FIXED: Corrected the variables to correctly get the window geometry and state.
        # The app.geometry() and app.state() methods return the current values.
        current_geometry = app_instance.geometry()
        current_state = app_instance.state()
        
        # Check and save geometry
        new_value = current_geometry
        if config.get(section, 'geometry', fallback=None) != new_value:
            config.set(section, 'geometry', new_value)
            debug_log(f"🔧💾📝 {section} - Changed 'geometry' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
            changed_count += 1
        
        # Check and save window state
        new_value = current_state
        if config.get(section, 'window_state', fallback=None) != new_value:
            config.set(section, 'window_state', new_value)
            debug_log(f"🔧💾📝 {section} - Changed 'window_state' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
            changed_count += 1
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        config.set(section, 'last_config_save_time', current_time)
        debug_log(f"🔧💾📝 {section} - Updated 'last_config_save_time' to '{current_time}' from {current_function}", file=current_file, version=current_version, function=current_function)
        if hasattr(app_instance, 'last_config_save_time_var'):
            app_instance.last_config_save_time_var.set(current_time)
        changed_count += 1

        if hasattr(app_instance, 'paned_window') and app_instance.paned_window and app_instance.winfo_width() > 0:
            sash_pos = app_instance.paned_window.sashpos(0)
            sash_pos_percentage = int((sash_pos / app_instance.winfo_width()) * 100)
            sash_pos_percentage_str = str(sash_pos_percentage)
            # FIX: Removed the conditional check to ensure the value is always saved.
            config.set(section, 'paned_window_sash_position_percentage', sash_pos_percentage_str)
            debug_log(f"🔧💾📝 {section} - Set 'paned_window_sash_position_percentage' to '{sash_pos_percentage_str}' from {current_function}", file=current_file, version=current_version, function=current_function)
            changed_count += 1

        if changed_count > 0:
            debug_log(f"🔧💾🔧💾✅ Application settings saved.", file=current_file, version=current_version, function=current_function)
        else:
            debug_log(f"🔧💾😴 No changes to save in Application settings.", file=current_file, version=current_version, function=current_function)
            
    except Exception as e:
        debug_log(f"🔧💾❌ Error saving {section} settings: {e}", file=current_file, version=current_version, function=current_function)