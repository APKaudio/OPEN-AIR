# src/settings_and_config/config_manager_scan.py
#
# This file provides the backend logic for saving scan-related settings.
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
# REFACTORED: Created a new, dedicated module for saving scan settings.

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


def _save_scan_info_settings(config, app_instance, console_print_func):
    """Saves scan-related settings."""
    current_function = inspect.currentframe().f_code.co_name
    changed_count = 0
    section = 'ScanConfiguration'
    if not config.has_section(section):
        config.add_section(section)

    try:
        if hasattr(app_instance, 'output_folder_var'):
            new_value = str(app_instance.output_folder_var.get())
            if config.get(section, 'output_folder', fallback=None) != new_value:
                config.set(section, 'output_folder', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'output_folder' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'scan_name_var'):
            new_value = str(app_instance.scan_name_var.get())
            if config.get(section, 'scan_name', fallback=None) != new_value:
                config.set(section, 'scan_name', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'scan_name' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'rbw_step_size_var'):
            new_value = str(app_instance.rbw_step_size_var.get())
            if config.get(section, 'rbw_step_size_hz', fallback=None) != new_value:
                config.set(section, 'rbw_step_size_hz', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'rbw_step_size_hz' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'num_scan_cycles_var'):
            new_value = str(app_instance.num_scan_cycles_var.get())
            if config.get(section, 'num_scan_cycles', fallback=None) != new_value:
                config.set(section, 'num_scan_cycles', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'num_scan_cycles' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'cycle_wait_time_seconds_var'):
            new_value = str(app_instance.cycle_wait_time_seconds_var.get())
            if config.get(section, 'cycle_wait_time_seconds', fallback=None) != new_value:
                config.set(section, 'cycle_wait_time_seconds', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'cycle_wait_time_seconds' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'maxhold_enabled_var'):
            new_value = str(app_instance.maxhold_enabled_var.get())
            if config.get(section, 'maxhold_enabled', fallback=None) != new_value:
                config.set(section, 'maxhold_enabled', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'maxhold_enabled' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'maxhold_time_seconds_var'):
            new_value = str(app_instance.maxhold_time_seconds_var.get())
            if config.get(section, 'maxhold_time_seconds', fallback=None) != new_value:
                config.set(section, 'maxhold_time_seconds', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'maxhold_time_seconds' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'desired_default_focus_width_var'):
            new_value = str(app_instance.desired_default_focus_width_var.get())
            if config.get(section, 'desired_default_focus_width', fallback=None) != new_value:
                config.set(section, 'desired_default_focus_width', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'desired_default_focus_width' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'create_html_report_var'):
            new_value = str(app_instance.create_html_report_var.get())
            if config.get(section, 'create_html', fallback=None) != new_value:
                config.set(section, 'create_html', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'create_html' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'open_html_after_complete_var'):
            new_value = str(app_instance.open_html_after_complete_var.get())
            if config.get(section, 'open_html_after_complete', fallback=None) != new_value:
                config.set(section, 'open_html_after_complete', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'open_html_after_complete' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'include_markers_var'):
            new_value = str(app_instance.include_markers_var.get())
            if config.get(section, 'include_markers', fallback=None) != new_value:
                config.set(section, 'include_markers', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'include_markers' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'include_gov_markers_var'):
            new_value = str(app_instance.include_gov_markers_var.get())
            if config.get(section, 'include_gov_markers', fallback=None) != new_value:
                config.set(section, 'include_gov_markers', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'include_gov_markers' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'include_tv_markers_var'):
            new_value = str(app_instance.include_tv_markers_var.get())
            if config.get(section, 'include_tv_markers', fallback=None) != new_value:
                config.set(section, 'include_tv_markers', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'include_tv_markers' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'include_scan_intermod_markers_var'):
            new_value = str(app_instance.include_scan_intermod_markers_var.get())
            if config.get(section, 'include_scan_intermod_markers', fallback=None) != new_value:
                config.set(section, 'include_scan_intermod_markers', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'include_scan_intermod_markers' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'math_average_var'):
            new_value = str(app_instance.math_average_var.get())
            if config.get(section, 'math_average', fallback=None) != new_value:
                config.set(section, 'math_average', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'math_average' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'math_median_var'):
            new_value = str(app_instance.math_median_var.get())
            if config.get(section, 'math_median', fallback=None) != new_value:
                config.set(section, 'math_median', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'math_median' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'math_variance_var'):
            new_value = str(app_instance.math_variance_var.get())
            if config.get(section, 'math_variance', fallback=None) != new_value:
                config.set(section, 'math_variance', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'math_variance' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'math_standard_deviation_var'):
            new_value = str(app_instance.math_standard_deviation_var.get())
            if config.get(section, 'math_standard_deviation', fallback=None) != new_value:
                config.set(section, 'math_standard_deviation', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'math_standard_deviation' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'math_range_var'):
            new_value = str(app_instance.math_range_var.get())
            if config.get(section, 'math_range', fallback=None) != new_value:
                config.set(section, 'math_range', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'math_range' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'math_psd_var'):
            new_value = str(app_instance.math_psd_var.get())
            if config.get(section, 'math_psd', fallback=None) != new_value:
                config.set(section, 'math_psd', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'math_psd' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        
        if hasattr(app_instance, 'band_vars') and app_instance.band_vars:
            selected_bands_with_levels = [f"{item['band']['Band Name']}={item.get('level', 0)}" for item in app_instance.band_vars]
            selected_bands_str = ",".join(selected_bands_with_levels)
            if config.get(section, 'last_scan_configuration__selected_bands_levels', fallback=None) != selected_bands_str:
                config.set(section, 'last_scan_configuration__selected_bands_levels', selected_bands_str)
                debug_log(f"🔧💾📝 {section} - Changed 'last_scan_configuration__selected_bands_levels' to '{selected_bands_str}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1

        if changed_count > 0:
            debug_log(f"🔧💾🔧💾✅ Scan settings saved.", file=current_file, version=current_version, function=current_function)
        else:
            debug_log(f"🔧💾😴 No changes to save in Scan settings.", file=current_file, version=current_version, function=current_function)
    except Exception as e:
        debug_log(f"🔧💾❌ Error saving {section} settings: {e}", file=current_file, version=current_version, function=current_function)