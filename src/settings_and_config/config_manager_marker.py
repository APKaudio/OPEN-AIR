# src/settings_and_config/config_manager_marker.py
#
# This file provides the backend logic for saving MarkerTab settings.
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
# REFACTORED: Created a new, dedicated module for saving MarkerTab settings.

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


def _save_marker_tab_settings(config, app_instance, console_print_func):
    """Saves all state variables related to the MarkerTab."""
    current_function = inspect.currentframe().f_code.co_name
    changed_count = 0
    section = 'MarkerTab'
    if not hasattr(app_instance, 'showtime_parent_tab'):
        debug_log("Config object: 'showtime_parent_tab' not available. Skipping MarkerTab save.", file=current_file, version=current_version, function=current_function)
        return
        
    showtime_tab = app_instance.showtime_parent_tab
    if not config.has_section(section):
        config.add_section(section)

    try:
        if hasattr(showtime_tab, 'span_var'):
            new_value = str(showtime_tab.span_var.get())
            if config.get(section, 'span_hz', fallback=None) != new_value:
                config.set(section, 'span_hz', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'span_hz' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        
        if hasattr(showtime_tab, 'rbw_var'):
            new_value = str(showtime_tab.rbw_var.get())
            if config.get(section, 'rbw_hz', fallback=None) != new_value:
                config.set(section, 'rbw_hz', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'rbw_hz' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
                
        if hasattr(showtime_tab, 'trace_modes'):
            for trace_type in ['live', 'max', 'min']:
                trace_key = f'trace_{trace_type}'
                if trace_key in showtime_tab.trace_modes and hasattr(showtime_tab.trace_modes[trace_type], 'get'):
                    new_value = str(showtime_tab.trace_modes[trace_type].get())
                    if config.get(section, trace_key, fallback=None) != new_value:
                        config.set(section, trace_key, new_value)
                        debug_log(f"🔧💾📝 {section} - Changed '{trace_key}' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                        changed_count += 1
                        
        if hasattr(showtime_tab, 'buffer_var'):
            new_value = str(showtime_tab.buffer_var.get())
            if config.get(section, 'buffer_mhz', fallback=None) != new_value:
                config.set(section, 'buffer_mhz', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'buffer_mhz' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1

        if hasattr(showtime_tab, 'poke_freq_var'):
            new_value = str(showtime_tab.poke_freq_var.get())
            if config.get(section, 'poke_freq_mhz', fallback=None) != new_value:
                config.set(section, 'poke_freq_mhz', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'poke_freq_mhz' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        
        if changed_count > 0:
            debug_log(f"🔧💾🔧💾✅ Showtime state successfully written to config.", file=current_file, version=current_version, function=current_function)
        else:
            debug_log(f"🔧💾😴 No changes to save in MarkerTab settings.", file=current_file, version=current_version, function=current_function)

    except Exception as e:
        debug_log(f"🔧💾❌ Error saving {section} settings: {e}", file=current_file, version=current_version, function=current_function)