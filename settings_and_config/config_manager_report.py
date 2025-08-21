# src/settings_and_config/config_manager_report.py
#
# This file provides the backend logic for saving report-related settings.
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
# REFACTORED: Created a new, dedicated module for saving report settings.

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


def _save_report_settings(config, app_instance, console_print_func):
    """Saves report-related settings."""
    current_function = inspect.currentframe().f_code.co_name
    changed_count = 0
    section = 'Report'
    if not config.has_section(section):
        config.add_section(section)
    
    try:
        if hasattr(app_instance, 'operator_name_var'):
            new_value = str(app_instance.operator_name_var.get())
            if config.get(section, 'operator_name', fallback=None) != new_value:
                config.set(section, 'operator_name', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'operator_name' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'operator_contact_var'):
            new_value = str(app_instance.operator_contact_var.get())
            if config.get(section, 'operator_contact', fallback=None) != new_value:
                config.set(section, 'operator_contact', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'operator_contact' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'venue_name_var'):
            new_value = str(app_instance.venue_name_var.get())
            if config.get(section, 'venue_name', fallback=None) != new_value:
                config.set(section, 'venue_name', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'venue_name' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'address_field_var'):
            new_value = str(app_instance.address_field_var.get())
            if config.get(section, 'address_field', fallback=None) != new_value:
                config.set(section, 'address_field', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'address_field' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'city_var'):
            new_value = str(app_instance.city_var.get())
            if config.get(section, 'city', fallback=None) != new_value:
                config.set(section, 'city', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'city' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'province_var'):
            new_value = str(app_instance.province_var.get())
            if config.get(section, 'province', fallback=None) != new_value:
                config.set(section, 'province', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'province' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'venue_postal_code_var'):
            new_value = str(app_instance.venue_postal_code_var.get())
            if config.get(section, 'venue_postal_code', fallback=None) != new_value:
                config.set(section, 'venue_postal_code', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'venue_postal_code' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'notes_var'):
            new_value = str(app_instance.notes_var.get())
            if config.get(section, 'notes', fallback=None) != new_value:
                config.set(section, 'notes', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'notes' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1

        if changed_count > 0:
            debug_log(f"🔧💾🔧💾✅ Report settings saved.", file=current_file, version=current_version, function=current_function)
        else:
            debug_log(f"🔧💾😴 No changes to save in Report settings.", file=current_file, version=current_version, function=current_function)
    except Exception as e:
        debug_log(f"🔧💾❌ Error saving {section} settings: {e}", file=current_file, version=current_version, function=current_function)