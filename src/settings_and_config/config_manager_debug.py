# src/settings_and_config/config_manager_debug.py
#
# This file provides the backend logic for saving debug-related settings.
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
# REFACTORED: Created a new, dedicated module for saving debug settings.

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


def _save_debug_settings(config, app_instance, console_print_func):
    """Saves debug-related settings."""
    current_function = inspect.currentframe().f_code.co_name
    changed_count = 0
    section = 'Debug'
    if not config.has_section(section):
        config.add_section(section)

    try:
        if hasattr(app_instance, 'general_debug_enabled_var'):
            new_value = str(app_instance.general_debug_enabled_var.get())
            if config.get(section, 'general_debug_enabled', fallback=None) != new_value:
                config.set(section, 'general_debug_enabled', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'general_debug_enabled' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'debug_to_gui_console_var'):
            new_value = str(app_instance.debug_to_gui_console_var.get())
            if config.get(section, 'debug_to_gui_console', fallback=None) != new_value:
                config.set(section, 'debug_to_gui_console', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'debug_to_gui_console' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'debug_to_terminal_var'):
            new_value = str(app_instance.debug_to_terminal_var.get())
            if config.get(section, 'debug_to_terminal', fallback=None) != new_value:
                config.set(section, 'debug_to_terminal', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'debug_to_terminal' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'debug_to_file_var'):
            new_value = str(app_instance.debug_to_file_var.get())
            if config.get(section, 'debug_to_file', fallback=None) != new_value:
                config.set(section, 'debug_to_file', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'debug_to_file' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'include_console_messages_to_debug_file_var'):
            new_value = str(app_instance.include_console_messages_to_debug_file_var.get())
            if config.get(section, 'include_console_messages_to_debug_file', fallback=None) != new_value:
                config.set(section, 'include_console_messages_to_debug_file', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'include_console_messages_to_debug_file' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'log_visa_commands_enabled_var'):
            new_value = str(app_instance.log_visa_commands_enabled_var.get())
            if config.get(section, 'log_visa_commands_enabled', fallback=None) != new_value:
                config.set(section, 'log_visa_commands_enabled', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'log_visa_commands_enabled' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1

        if changed_count > 0:
            debug_log(f"🔧💾🔧💾✅ Debug settings saved.", file=current_file, version=current_version, function=current_function)
        else:
            debug_log(f"🔧💾😴 No changes to save in Debug settings.", file=current_file, version=current_version, function=current_function)
    except Exception as e:
        debug_log(f"🔧💾❌ Error saving {section} settings: {e}", file=current_file, version=current_version, function=current_function)