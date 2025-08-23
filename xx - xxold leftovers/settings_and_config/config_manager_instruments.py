# src/settings_and_config/config_manager_instruments.py
#
# This file provides the backend logic for saving instrument-related settings.
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
# Version 20250821.135600.2
# FIXED: Updated the variable name from 'visa_resource_var' to 'instrument_visa_resource_var'
#        to align with the new modular variable system, preventing an AttributeError.

import os
import inspect
from configparser import ConfigParser
from display.debug_logic import debug_log
from display.console_logic import console_log

# --- Versioning ---
w = 20250821
x_str = '135600'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 2
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"


def _save_instrument_settings(config, app_instance, console_print_func):
    """Saves Instrument and InstrumentSettings section."""
    current_function = inspect.currentframe().f_code.co_name
    changed_count = 0
    section_inst = 'Instrument'
    section_settings = 'InstrumentSettings'
    if not config.has_section(section_inst):
        config.add_section(section_inst)
    if not config.has_section(section_settings):
        config.add_section(section_settings)
    
    try:
        # Save Instrument values
        # FIXED: Corrected variable name from visa_resource_var
        if hasattr(app_instance, 'instrument_visa_resource_var'):
            new_value = str(app_instance.instrument_visa_resource_var.get())
            if config.get(section_inst, 'visa_resource', fallback=None) != new_value:
                config.set(section_inst, 'visa_resource', new_value)
                debug_log(f"🔧💾📝 {section_inst} - Changed 'visa_resource' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        
        # Save InstrumentSettings values
        if hasattr(app_instance, 'center_freq_mhz_var'):
            new_value = str(app_instance.center_freq_mhz_var.get())
            if config.get(section_settings, 'center_freq_mhz', fallback=None) != new_value:
                config.set(section_settings, 'center_freq_mhz', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'center_freq_mhz' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        
        if hasattr(app_instance, 'span_freq_mhz_var'):
            new_value = str(app_instance.span_freq_mhz_var.get())
            if config.get(section_settings, 'span_freq_mhz', fallback=None) != new_value:
                config.set(section_settings, 'span_freq_mhz', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'span_freq_mhz' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
                
        if hasattr(app_instance, 'start_freq_mhz_var'):
            new_value = str(app_instance.start_freq_mhz_var.get())
            if config.get(section_settings, 'start_freq_mhz', fallback=None) != new_value:
                config.set(section_settings, 'start_freq_mhz', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'start_freq_mhz' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1

        if hasattr(app_instance, 'stop_freq_mhz_var'):
            new_value = str(app_instance.stop_freq_mhz_var.get())
            if config.get(section_settings, 'stop_freq_mhz', fallback=None) != new_value:
                config.set(section_settings, 'stop_freq_mhz', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'stop_freq_mhz' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        
        if hasattr(app_instance, 'rbw_mhz_var'):
            new_value = str(app_instance.rbw_mhz_var.get())
            if config.get(section_settings, 'rbw_mhz', fallback=None) != new_value:
                config.set(section_settings, 'rbw_mhz', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'rbw_mhz' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1

        if hasattr(app_instance, 'vbw_mhz_var'):
            new_value = str(app_instance.vbw_mhz_var.get())
            if config.get(section_settings, 'vbw_mhz', fallback=None) != new_value:
                config.set(section_settings, 'vbw_mhz', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'vbw_mhz' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        
        if hasattr(app_instance, 'vbw_auto_on_var'):
            new_value = str(app_instance.vbw_auto_on_var.get())
            if config.get(section_settings, 'vbw_auto_on', fallback=None) != new_value:
                config.set(section_settings, 'vbw_auto_on', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'vbw_auto_on' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1

        if hasattr(app_instance, 'initiate_continuous_on_var'):
            new_value = str(app_instance.initiate_continuous_on_var.get())
            if config.get(section_settings, 'initiate_continuous_on', fallback=None) != new_value:
                config.set(section_settings, 'initiate_continuous_on', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'initiate_continuous_on' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1

        if hasattr(app_instance, 'ref_level_dbm_var'):
            new_value = str(app_instance.ref_level_dbm_var.get())
            if config.get(section_settings, 'ref_level_dbm', fallback=None) != new_value:
                config.set(section_settings, 'ref_level_dbm', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'ref_level_dbm' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1

        if hasattr(app_instance, 'preamp_on_var'):
            new_value = str(app_instance.preamp_on_var.get())
            if config.get(section_settings, 'preamp_on', fallback=None) != new_value:
                config.set(section_settings, 'preamp_on', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'preamp_on' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
                
        if hasattr(app_instance, 'power_attenuation_db_var'):
            new_value = str(app_instance.power_attenuation_db_var.get())
            if config.get(section_settings, 'power_attenuation_db', fallback=None) != new_value:
                config.set(section_settings, 'power_attenuation_db', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'power_attenuation_db' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
                
        if hasattr(app_instance, 'high_sensitivity_on_var'):
            new_value = str(app_instance.high_sensitivity_on_var.get())
            if config.get(section_settings, 'high_sensitivity_on', fallback=None) != new_value:
                config.set(section_settings, 'high_sensitivity_on', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'high_sensitivity_on' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1

        if changed_count > 0:
            debug_log(f"🔧💾🔧💾✅ Instrument settings saved.", file=current_file, version=current_version, function=current_function)
        else:
            debug_log(f"🔧💾😴 No changes to save in Instrument settings.", file=current_file, version=current_version, function=current_function)
    except Exception as e:
        debug_log(f"🔧💾❌ Error saving {section_inst} or {section_settings} settings: {e}", file=current_file, version=current_version, function=current_function)


def _save_antenna_settings(config, app_instance, console_print_func):
    """Saves antenna settings."""
    current_function = inspect.currentframe().f_code.co_name
    changed_count = 0
    section = 'Antenna'
    if not config.has_section(section):
        config.add_section(section)
    
    try:
        if hasattr(app_instance, 'antenna_type_var'):
            new_value = str(app_instance.antenna_type_var.get())
            if config.get(section, 'selected_antenna_type', fallback=None) != new_value:
                config.set(section, 'selected_antenna_type', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'selected_antenna_type' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'antenna_description_var'):
            new_value = str(app_instance.antenna_description_var.get())
            if config.get(section, 'antenna_description', fallback=None) != new_value:
                config.set(section, 'antenna_description', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'antenna_description' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'antenna_use_var'):
            new_value = str(app_instance.antenna_use_var.get())
            if config.get(section, 'antenna_use', fallback=None) != new_value:
                config.set(section, 'antenna_use', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'antenna_use' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'antenna_mount_var'):
            new_value = str(app_instance.antenna_mount_var.get())
            if config.get(section, 'antenna_mount', fallback=None) != new_value:
                config.set(section, 'antenna_mount', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'antenna_mount' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'antenna_amplifier_var'):
            new_value = str(app_instance.antenna_amplifier_var.get())
            if config.get(section, 'antenna_amplifier', fallback=None) != new_value:
                config.set(section, 'antenna_amplifier', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'antenna_amplifier' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        
        if changed_count > 0:
            debug_log(f"🔧💾🔧💾✅ Antenna settings saved.", file=current_file, version=current_version, function=current_function)
        else:
            debug_log(f"🔧💾😴 No changes to save in Antenna settings.", file=current_file, version=current_version, function=current_function)
    except Exception as e:
        debug_log(f"🔧💾❌ Error saving {section} settings: {e}", file=current_file, version=current_version, function=current_function)

def _save_amplifier_settings(config, app_instance, console_print_func):
    """Saves amplifier settings."""
    current_function = inspect.currentframe().f_code.co_name
    changed_count = 0
    section = 'Amplifier'
    if not config.has_section(section):
        config.add_section(section)
        
    try:
        if hasattr(app_instance, 'amplifier_type_var'):
            new_value = str(app_instance.amplifier_type_var.get())
            if config.get(section, 'selected_amplifier_type', fallback=None) != new_value:
                config.set(section, 'selected_amplifier_type', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'selected_amplifier_type' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'amplifier_description_var'):
            new_value = str(app_instance.amplifier_description_var.get())
            if config.get(section, 'amplifier_description', fallback=None) != new_value:
                config.set(section, 'amplifier_description', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'amplifier_description' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'amplifier_use_var'):
            new_value = str(app_instance.amplifier_use_var.get())
            if config.get(section, 'amplifier_use', fallback=None) != new_value:
                config.set(section, 'amplifier_use', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'amplifier_use' to '{new_value}' from {current_function}", file=current_file, version=current_version, function=current_function)
                changed_count += 1
        
        if changed_count > 0:
            debug_log(f"🔧💾🔧💾✅ Amplifier settings saved.", file=current_file, version=current_version, function=current_function)
        else:
            debug_log(f"🔧💾😴 No changes to save in Amplifier settings.", file=current_file, version=current_version, function=current_function)
    except Exception as e:
        debug_log(f"🔧💾❌ Error saving {section} settings: {e}", file=current_file, version=current_version, function=current_function)