# src/settings_and_config/config_manager.py
#
# This file handles loading and saving application settings to the 'config.ini' file.
# It uses the configparser library to manage the configuration data, ensuring that
# user settings are preserved between sessions.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250824.101000.3
# REFACTORED: `save_config` has been refactored into modular, domain-specific functions
#             for better maintainability and clarity.
# FIXED: The logic for saving MarkerTab settings has been corrected to retrieve
#        values directly from the `showtime_parent_tab` instance, resolving the
#        `AttributeError` and ensuring state is persisted.
# NEW: Added explicit debug logging to each save function to show which variable changed and its new value.
# NEW: Implemented conditional logging: a 'saved' message is only logged for a section if
#      at least one attribute within that section has actually changed.

current_version = "20250824.101000.3"
current_version_hash = (20250824 * 101000 * 3)

import configparser
import os
import inspect
from datetime import datetime

# Local application imports
from display.debug_logic import debug_log
from display.console_logic import console_log

# Use the correct variable name 'DEFAULT_CONFIG'
from src.settings_and_config.program_default_values import DEFAULT_CONFIG


def load_config(file_path, console_print_func):
    """
    Loads the configuration from the specified INI file. If the file doesn't exist
    or is empty, it creates it with default settings.
    """
    current_function = inspect.currentframe().f_code.co_name
    config = configparser.ConfigParser(interpolation=None)
    
    # Check if file doesn't exist OR if it exists but is empty
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        if not os.path.exists(file_path):
            console_print_func(f"Configuration file not found at '{file_path}'. Creating with default settings.")
            debug_log(f"Config file not found: {file_path}. Initializing with defaults.",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
        else: # File exists but is empty
            console_print_func(f"Configuration file at '{file_path}' is empty. Overwriting with default settings.")
            debug_log(f"Config file is empty: {file_path}. Overwriting with defaults.",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            
        config.read_dict(DEFAULT_CONFIG)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, 'w') as configfile:
                config.write(configfile)
            console_print_func("🔧💾✅ Default configuration file created successfully.")
            debug_log("Default config file created.",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
        except Exception as e:
            error_msg = f"🔧💾❌ Error creating default config file: {e}. This is a problem!"
            console_print_func(error_msg)
            debug_log(error_msg,
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
    else:
        try:
            config.read(file_path)
            console_print_func(f"🔧💾✅ Configuration loaded from '{file_path}'.")
            debug_log(f"Config loaded from: {file_path}",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
        except configparser.Error as e:
            console_print_func(f"🔧💾❌ Error reading config file: {e}. Starting with default settings.")
            debug_log(f"Config read error: {e}. Reverting to defaults.",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            config.read_dict(DEFAULT_CONFIG)

    return config

def _save_application_settings(config, app_instance, console_print_func):
    """Saves application-level settings like window geometry and state."""
    current_function = inspect.currentframe().f_code.co_name
    changed_count = 0
    section = 'Application'
    if not config.has_section(section):
        config.add_section(section)

    try:
        app_geometry = app_instance.geometry()
        if config.get(section, 'geometry', fallback=None) != app_geometry:
            config.set(section, 'geometry', app_geometry)
            debug_log(f"🔧💾📝 {section} - Changed 'geometry' to '{app_geometry}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
            changed_count += 1
        
        window_state = 'zoomed' if app_instance.state() == 'zoomed' else 'normal'
        if config.get(section, 'window_state', fallback=None) != window_state:
            config.set(section, 'window_state', window_state)
            debug_log(f"🔧💾📝 {section} - Changed 'window_state' to '{window_state}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
            changed_count += 1
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if config.get(section, 'last_config_save_time', fallback=None) != current_time:
            config.set(section, 'last_config_save_time', current_time)
            debug_log(f"🔧💾📝 {section} - Changed 'last_config_save_time' to '{current_time}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
            if hasattr(app_instance, 'last_config_save_time_var'):
                app_instance.last_config_save_time_var.set(current_time)
            changed_count += 1

        if hasattr(app_instance, 'paned_window') and app_instance.paned_window and app_instance.winfo_width() > 0:
            sash_pos = app_instance.paned_window.sashpos(0)
            sash_pos_percentage = int((sash_pos / app_instance.winfo_width()) * 100)
            sash_pos_percentage_str = str(sash_pos_percentage)
            if config.get(section, 'paned_window_sash_position_percentage', fallback=None) != sash_pos_percentage_str:
                config.set(section, 'paned_window_sash_position_percentage', sash_pos_percentage_str)
                debug_log(f"🔧💾📝 {section} - Changed 'paned_window_sash_position_percentage' to '{sash_pos_percentage_str}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1

        if changed_count > 0:
            debug_log(f"🔧💾🔧💾✅ Application settings saved.", file=os.path.basename(__file__), version=current_version, function=current_function)

    except Exception as e:
        debug_log(f"🔧💾🔧💾❌ Failed to save application settings: {e}", file=os.path.basename(__file__), version=current_version, function=current_function)

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
                debug_log(f"🔧💾📝 {section} - Changed 'general_debug_enabled' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'debug_to_gui_console_var'):
            new_value = str(app_instance.debug_to_gui_console_var.get())
            if config.get(section, 'debug_to_gui_console', fallback=None) != new_value:
                config.set(section, 'debug_to_gui_console', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'debug_to_gui_console' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'debug_to_terminal_var'):
            new_value = str(app_instance.debug_to_terminal_var.get())
            if config.get(section, 'debug_to_terminal', fallback=None) != new_value:
                config.set(section, 'debug_to_terminal', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'debug_to_terminal' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'debug_to_file_var'):
            new_value = str(app_instance.debug_to_file_var.get())
            if config.get(section, 'debug_to_file', fallback=None) != new_value:
                config.set(section, 'debug_to_file', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'debug_to_file' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'include_console_messages_to_debug_file_var'):
            new_value = str(app_instance.include_console_messages_to_debug_file_var.get())
            if config.get(section, 'include_console_messages_to_debug_file', fallback=None) != new_value:
                config.set(section, 'include_console_messages_to_debug_file', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'include_console_messages_to_debug_file' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'log_visa_commands_enabled_var'):
            new_value = str(app_instance.log_visa_commands_enabled_var.get())
            if config.get(section, 'log_visa_commands_enabled', fallback=None) != new_value:
                config.set(section, 'log_visa_commands_enabled', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'log_visa_commands_enabled' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1

        if changed_count > 0:
            debug_log(f"🔧💾🔧💾✅ Debug settings saved.", file=os.path.basename(__file__), version=current_version, function=current_function)
    except Exception as e:
        debug_log(f"🔧💾🔧💾❌ Failed to save debug settings: {e}", file=os.path.basename(__file__), version=current_version, function=current_function)

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
        if hasattr(app_instance, 'visa_resource_var'):
            new_value = str(app_instance.visa_resource_var.get())
            if config.get(section_inst, 'visa_resource', fallback=None) != new_value:
                config.set(section_inst, 'visa_resource', new_value)
                debug_log(f"🔧💾📝 {section_inst} - Changed 'visa_resource' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        
        # Save InstrumentSettings values
        if hasattr(app_instance, 'center_freq_mhz_var'):
            new_value = str(app_instance.center_freq_mhz_var.get())
            if config.get(section_settings, 'center_freq_mhz', fallback=None) != new_value:
                config.set(section_settings, 'center_freq_mhz', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'center_freq_mhz' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'span_freq_mhz_var'):
            new_value = str(app_instance.span_freq_mhz_var.get())
            if config.get(section_settings, 'span_freq_mhz', fallback=None) != new_value:
                config.set(section_settings, 'span_freq_mhz', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'span_freq_mhz' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'start_freq_mhz_var'):
            new_value = str(app_instance.start_freq_mhz_var.get())
            if config.get(section_settings, 'start_freq_mhz', fallback=None) != new_value:
                config.set(section_settings, 'start_freq_mhz', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'start_freq_mhz' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'stop_freq_mhz_var'):
            new_value = str(app_instance.stop_freq_mhz_var.get())
            if config.get(section_settings, 'stop_freq_mhz', fallback=None) != new_value:
                config.set(section_settings, 'stop_freq_mhz', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'stop_freq_mhz' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'rbw_mhz_var'):
            new_value = str(app_instance.rbw_mhz_var.get())
            if config.get(section_settings, 'rbw_mhz', fallback=None) != new_value:
                config.set(section_settings, 'rbw_mhz', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'rbw_mhz' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'vbw_mhz_var'):
            new_value = str(app_instance.vbw_mhz_var.get())
            if config.get(section_settings, 'vbw_mhz', fallback=None) != new_value:
                config.set(section_settings, 'vbw_mhz', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'vbw_mhz' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'vbw_auto_on_var'):
            new_value = str(app_instance.vbw_auto_on_var.get())
            if config.get(section_settings, 'vbw_auto_on', fallback=None) != new_value:
                config.set(section_settings, 'vbw_auto_on', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'vbw_auto_on' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'initiate_continuous_on_var'):
            new_value = str(app_instance.initiate_continuous_on_var.get())
            if config.get(section_settings, 'initiate_continuous_on', fallback=None) != new_value:
                config.set(section_settings, 'initiate_continuous_on', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'initiate_continuous_on' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'ref_level_dbm_var'):
            new_value = str(app_instance.ref_level_dbm_var.get())
            if config.get(section_settings, 'ref_level_dbm', fallback=None) != new_value:
                config.set(section_settings, 'ref_level_dbm', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'ref_level_dbm' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'preamp_on_var'):
            new_value = str(app_instance.preamp_on_var.get())
            if config.get(section_settings, 'preamp_on', fallback=None) != new_value:
                config.set(section_settings, 'preamp_on', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'preamp_on' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'power_attenuation_db_var'):
            new_value = str(app_instance.power_attenuation_db_var.get())
            if config.get(section_settings, 'power_attenuation_db', fallback=None) != new_value:
                config.set(section_settings, 'power_attenuation_db', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'power_attenuation_db' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'high_sensitivity_on_var'):
            new_value = str(app_instance.high_sensitivity_on_var.get())
            if config.get(section_settings, 'high_sensitivity_on', fallback=None) != new_value:
                config.set(section_settings, 'high_sensitivity_on', new_value)
                debug_log(f"🔧💾📝 {section_settings} - Changed 'high_sensitivity_on' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
            
        # Save Trace Modes
        if hasattr(app_instance, 'trace_modes_vars') and app_instance.trace_modes_vars:
            for trace_num in range(1, 5):
                var_name = f'trace{trace_num}_mode'
                new_value = str(app_instance.trace_modes_vars[f'trace{trace_num}'].get())
                if config.get(section_settings, var_name, fallback=None) != new_value:
                    config.set(section_settings, var_name, new_value)
                    debug_log(f"🔧💾📝 {section_settings} - Changed '{var_name}' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                    changed_count += 1
        
        # Save Marker settings
        if hasattr(app_instance, 'markers_on_vars') and app_instance.markers_on_vars:
            for marker_num in range(1, 7):
                var_name = f'marker{marker_num}_on'
                new_value = str(app_instance.markers_on_vars[f'marker{marker_num}'].get())
                if config.get(section_settings, var_name, fallback=None) != new_value:
                    config.set(section_settings, var_name, new_value)
                    debug_log(f"🔧💾📝 {section_settings} - Changed '{var_name}' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                    changed_count += 1

        if changed_count > 0:
            debug_log(f"🔧💾🔧💾✅ Instrument settings saved.", file=os.path.basename(__file__), version=current_version, function=current_function)
            
    except Exception as e:
        debug_log(f"🔧💾🔧💾❌ Failed to save instrument settings: {e}. Something is fucked!", file=os.path.basename(__file__), version=current_version, function=current_function)

def _save_marker_tab_settings(config, app_instance, console_print_func):
    """Saves all state variables related to the MarkerTab."""
    current_function = inspect.currentframe().f_code.co_name
    changed_count = 0
    section = 'MarkerTab'
    if not hasattr(app_instance, 'showtime_parent_tab'):
        debug_log("Config object: 'showtime_parent_tab' not available. Skipping MarkerTab save.", file=os.path.basename(__file__), version=current_version, function=current_function)
        return
        
    showtime_tab = app_instance.showtime_parent_tab
    if not config.has_section(section):
        config.add_section(section)

    try:
        # Save all the state variables to the config file
        new_value = str(showtime_tab.span_var.get())
        if config.get(section, 'span_hz', fallback=None) != new_value:
            config.set(section, 'span_hz', new_value)
            debug_log(f"🔧💾📝 {section} - Changed 'span_hz' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
            changed_count += 1
        
        new_value = str(showtime_tab.rbw_var.get())
        if config.get(section, 'rbw_hz', fallback=None) != new_value:
            config.set(section, 'rbw_hz', new_value)
            debug_log(f"🔧💾📝 {section} - Changed 'rbw_hz' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
            changed_count += 1
        
        if hasattr(showtime_tab, 'trace_modes'):
            for mode, var in showtime_tab.trace_modes.items():
                new_value = str(var.get())
                if config.get(section, f'trace_{mode}', fallback=None) != new_value:
                    config.set(section, f'trace_{mode}', new_value)
                    debug_log(f"🔧💾📝 {section} - Changed 'trace_{mode}' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                    changed_count += 1
        
        new_value = str(showtime_tab.buffer_var.get())
        if config.get(section, 'buffer_mhz', fallback=None) != new_value:
            config.set(section, 'buffer_mhz', new_value)
            debug_log(f"🔧💾📝 {section} - Changed 'buffer_mhz' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
            changed_count += 1

        new_value = str(showtime_tab.poke_freq_var.get())
        if config.get(section, 'poke_mhz', fallback=None) != new_value:
            config.set(section, 'poke_mhz', new_value)
            debug_log(f"🔧💾📝 {section} - Changed 'poke_mhz' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
            changed_count += 1
        
        new_value = str(showtime_tab.buffered_start_var.get())
        if config.get(section, 'buffered_start_var', fallback=None) != new_value:
            config.set(section, 'buffered_start_var', new_value)
            debug_log(f"🔧💾📝 {section} - Changed 'buffered_start_var' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
            changed_count += 1

        new_value = str(showtime_tab.buffered_stop_var.get())
        if config.get(section, 'buffered_stop_var', fallback=None) != new_value:
            config.set(section, 'buffered_stop_var', new_value)
            debug_log(f"🔧💾📝 {section} - Changed 'buffered_stop_var' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
            changed_count += 1
        
        # Save selection state
        new_value = str(showtime_tab.selected_zone)
        if config.get(section, 'zone_selected', fallback=None) != new_value:
            config.set(section, 'zone_selected', new_value)
            debug_log(f"🔧💾📝 {section} - Changed 'zone_selected' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
            changed_count += 1
        
        new_value = str(showtime_tab.selected_group)
        if config.get(section, 'group_selected', fallback=None) != new_value:
            config.set(section, 'group_selected', new_value)
            debug_log(f"🔧💾📝 {section} - Changed 'group_selected' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
            changed_count += 1
        
        # We need to save device info as a string or a set of strings, not a dictionary directly
        if showtime_tab.selected_device_info:
            new_value = str(showtime_tab.selected_device_info.get('NAME', ''))
            if config.get(section, 'device_selected_name', fallback=None) != new_value:
                config.set(section, 'device_selected_name', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'device_selected_name' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1

            new_value = str(showtime_tab.selected_device_info.get('DEVICE', ''))
            if config.get(section, 'device_selected_device_type', fallback=None) != new_value:
                config.set(section, 'device_selected_device_type', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'device_selected_device_type' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1

            new_value = str(showtime_tab.selected_device_info.get('CENTER', ''))
            if config.get(section, 'device_selected_center', fallback=None) != new_value:
                config.set(section, 'device_selected_center', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'device_selected_center' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        else:
            if config.get(section, 'device_selected_name', fallback=None) != '':
                config.set(section, 'device_selected_name', '')
                debug_log(f"🔧💾📝 {section} - Changed 'device_selected_name' to '' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
            if config.get(section, 'device_selected_device_type', fallback=None) != '':
                config.set(section, 'device_selected_device_type', '')
                debug_log(f"🔧💾📝 {section} - Changed 'device_selected_device_type' to '' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
            if config.get(section, 'device_selected_center', fallback=None) != '':
                config.set(section, 'device_selected_center', '')
                debug_log(f"🔧💾📝 {section} - Changed 'device_selected_center' to '' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
            
        # Save label variables
        new_value = showtime_tab.zone_zoom_label_left_var.get()
        if config.get(section, 'zone_zoom_label_left_var', fallback=None) != new_value:
            config.set(section, 'zone_zoom_label_left_var', new_value)
            debug_log(f"🔧💾📝 {section} - Changed 'zone_zoom_label_left_var' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
            changed_count += 1
        
        new_value = showtime_tab.zone_zoom_label_center_var.get()
        if config.get(section, 'zone_zoom_label_center_var', fallback=None) != new_value:
            config.set(section, 'zone_zoom_label_center_var', new_value)
            debug_log(f"🔧💾📝 {section} - Changed 'zone_zoom_label_center_var' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
            changed_count += 1
        
        new_value = showtime_tab.zone_zoom_label_right_var.get()
        if config.get(section, 'zone_zoom_label_right_var', fallback=None) != new_value:
            config.set(section, 'zone_zoom_label_right_var', new_value)
            debug_log(f"🔧💾📝 {section} - Changed 'zone_zoom_label_right_var' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
            changed_count += 1
        
        # FIXED: Corrected the way device counts are retrieved from dictionaries
        new_value = str(showtime_tab.selected_zone_info.get('device_count', 0))
        if config.get(section, 'zone_device_count', fallback=None) != new_value:
            config.set(section, 'zone_device_count', new_value)
            debug_log(f"🔧💾📝 {section} - Changed 'zone_device_count' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
            changed_count += 1
            
        # FIXED: The previous line was incorrect, trying to get `keys()` from a potentially empty dict
        zone_groups = showtime_tab.structured_data.get(showtime_tab.selected_zone, {}) if showtime_tab.structured_data and showtime_tab.selected_zone else {}
        new_value = str(len(zone_groups.keys()) if showtime_tab.selected_zone else 0)
        if config.get(section, 'zone_group_count', fallback=None) != new_value:
            config.set(section, 'zone_group_count', new_value)
            debug_log(f"🔧💾📝 {section} - Changed 'zone_group_count' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
            changed_count += 1

        new_value = str(showtime_tab.selected_group_info.get('device_count', 0))
        if config.get(section, 'group_device_count', fallback=None) != new_value:
            config.set(section, 'group_device_count', new_value)
            debug_log(f"🔧💾📝 {section} - Changed 'group_device_count' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
            changed_count += 1
        
        if changed_count > 0:
            debug_log(f"🔧💾🔧💾✅ Showtime state successfully written to config.", file=os.path.basename(__file__), version=current_version, function=current_function)

    except Exception as e:
        console_log(f"🔧💾❌ Error saving Showtime state to config: {e}. Fucking useless!", "ERROR")
        debug_log(message=f"🛠️🔧💾🔧💾❌ Failed to save Showtime state. Error: {e}", file=os.path.basename(__file__), version=current_version, function=current_function)

def _save_scan_info_settings(config, app_instance, console_print_func):
    """Saves scan-related settings."""
    current_function = inspect.currentframe().f_code.co_name
    changed_count = 0
    section = 'Scan'
    if not config.has_section(section):
        config.add_section(section)

    try:
        if hasattr(app_instance, 'output_folder_var'):
            new_value = str(app_instance.output_folder_var.get())
            if config.get(section, 'output_folder', fallback=None) != new_value:
                config.set(section, 'output_folder', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'output_folder' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'scan_name_var'):
            new_value = str(app_instance.scan_name_var.get())
            if config.get(section, 'scan_name', fallback=None) != new_value:
                config.set(section, 'scan_name', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'scan_name' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'rbw_step_size_hz_var'):
            new_value = str(app_instance.rbw_step_size_hz_var.get())
            if config.get(section, 'rbw_step_size_hz', fallback=None) != new_value:
                config.set(section, 'rbw_step_size_hz', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'rbw_step_size_hz' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'num_scan_cycles_var'):
            new_value = str(app_instance.num_scan_cycles_var.get())
            if config.get(section, 'num_scan_cycles', fallback=None) != new_value:
                config.set(section, 'num_scan_cycles', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'num_scan_cycles' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'cycle_wait_time_seconds_var'):
            new_value = str(app_instance.cycle_wait_time_seconds_var.get())
            if config.get(section, 'cycle_wait_time_seconds', fallback=None) != new_value:
                config.set(section, 'cycle_wait_time_seconds', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'cycle_wait_time_seconds' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'maxhold_enabled_var'):
            new_value = str(app_instance.maxhold_enabled_var.get())
            if config.get(section, 'maxhold_enabled', fallback=None) != new_value:
                config.set(section, 'maxhold_enabled', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'maxhold_enabled' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'maxhold_time_seconds_var'):
            new_value = str(app_instance.maxhold_time_seconds_var.get())
            if config.get(section, 'maxhold_time_seconds', fallback=None) != new_value:
                config.set(section, 'maxhold_time_seconds', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'maxhold_time_seconds' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'desired_default_focus_width_var'):
            new_value = str(app_instance.desired_default_focus_width_var.get())
            if config.get(section, 'desired_default_focus_width', fallback=None) != new_value:
                config.set(section, 'desired_default_focus_width', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'desired_default_focus_width' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'create_html_var'):
            new_value = str(app_instance.create_html_var.get())
            if config.get(section, 'create_html', fallback=None) != new_value:
                config.set(section, 'create_html', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'create_html' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'open_html_after_complete_var'):
            new_value = str(app_instance.open_html_after_complete_var.get())
            if config.get(section, 'open_html_after_complete', fallback=None) != new_value:
                config.set(section, 'open_html_after_complete', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'open_html_after_complete' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'include_markers_var'):
            new_value = str(app_instance.include_markers_var.get())
            if config.get(section, 'include_markers', fallback=None) != new_value:
                config.set(section, 'include_markers', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'include_markers' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'include_gov_markers_var'):
            new_value = str(app_instance.include_gov_markers_var.get())
            if config.get(section, 'include_gov_markers', fallback=None) != new_value:
                config.set(section, 'include_gov_markers', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'include_gov_markers' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'include_tv_markers_var'):
            new_value = str(app_instance.include_tv_markers_var.get())
            if config.get(section, 'include_tv_markers', fallback=None) != new_value:
                config.set(section, 'include_tv_markers', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'include_tv_markers' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'include_scan_intermod_markers_var'):
            new_value = str(app_instance.include_scan_intermod_markers_var.get())
            if config.get(section, 'include_scan_intermod_markers', fallback=None) != new_value:
                config.set(section, 'include_scan_intermod_markers', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'include_scan_intermod_markers' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'math_average_var'):
            new_value = str(app_instance.math_average_var.get())
            if config.get(section, 'math_average', fallback=None) != new_value:
                config.set(section, 'math_average', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'math_average' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'math_median_var'):
            new_value = str(app_instance.math_median_var.get())
            if config.get(section, 'math_median', fallback=None) != new_value:
                config.set(section, 'math_median', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'math_median' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'math_variance_var'):
            new_value = str(app_instance.math_variance_var.get())
            if config.get(section, 'math_variance', fallback=None) != new_value:
                config.set(section, 'math_variance', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'math_variance' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'math_standard_deviation_var'):
            new_value = str(app_instance.math_standard_deviation_var.get())
            if config.get(section, 'math_standard_deviation', fallback=None) != new_value:
                config.set(section, 'math_standard_deviation', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'math_standard_deviation' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'math_range_var'):
            new_value = str(app_instance.math_range_var.get())
            if config.get(section, 'math_range', fallback=None) != new_value:
                config.set(section, 'math_range', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'math_range' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'math_psd_var'):
            new_value = str(app_instance.math_psd_var.get())
            if config.get(section, 'math_psd', fallback=None) != new_value:
                config.set(section, 'math_psd', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'math_psd' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        
        if hasattr(app_instance, 'band_vars') and app_instance.band_vars:
            selected_bands_with_levels = [f"{item['band']['Band Name']}={item.get('level', 0)}" for item in app_instance.band_vars]
            selected_bands_str = ",".join(selected_bands_with_levels)
            if config.get(section, 'last_scan_configuration__selected_bands_levels', fallback=None) != selected_bands_str:
                config.set(section, 'last_scan_configuration__selected_bands_levels', selected_bands_str)
                debug_log(f"🔧💾📝 {section} - Changed 'last_scan_configuration__selected_bands_levels' to '{selected_bands_str}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1

        if changed_count > 0:
            debug_log(f"🔧💾🔧💾✅ Scan settings saved.", file=os.path.basename(__file__), version=current_version, function=current_function)
    except Exception as e:
        debug_log(f"🔧💾🔧💾❌ Failed to save scan settings: {e}. The scanner has a mind of its own!", file=os.path.basename(__file__), version=current_version, function=current_function)

def _save_antenna_settings(config, app_instance, console_print_func):
    """Saves antenna-related settings."""
    current_function = inspect.currentframe().f_code.co_name
    changed_count = 0
    section = 'Antenna'
    if not config.has_section(section):
        config.add_section(section)

    try:
        if hasattr(app_instance, 'selected_antenna_type_var'):
            new_value = str(app_instance.selected_antenna_type_var.get())
            if config.get(section, 'selected_antenna_type', fallback=None) != new_value:
                config.set(section, 'selected_antenna_type', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'selected_antenna_type' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'antenna_description_var'):
            new_value = str(app_instance.antenna_description_var.get())
            if config.get(section, 'antenna_description', fallback=None) != new_value:
                config.set(section, 'antenna_description', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'antenna_description' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'antenna_use_var'):
            new_value = str(app_instance.antenna_use_var.get())
            if config.get(section, 'antenna_use', fallback=None) != new_value:
                config.set(section, 'antenna_use', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'antenna_use' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'antenna_mount_var'):
            new_value = str(app_instance.antenna_mount_var.get())
            if config.get(section, 'antenna_mount', fallback=None) != new_value:
                config.set(section, 'antenna_mount', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'antenna_mount' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'antenna_amplifier_var'):
            new_value = str(app_instance.antenna_amplifier_var.get())
            if config.get(section, 'antenna_amplifier', fallback=None) != new_value:
                config.set(section, 'antenna_amplifier', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'antenna_amplifier' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        
        if changed_count > 0:
            debug_log(f"🔧💾🔧💾✅ Antenna settings saved.", file=os.path.basename(__file__), version=current_version, function=current_function)
    except Exception as e:
        debug_log(f"🔧💾🔧💾❌ Failed to save antenna settings: {e}. The antenna is on the fritz!", file=os.path.basename(__file__), version=current_version, function=current_function)

def _save_amplifier_settings(config, app_instance, console_print_func):
    """Saves amplifier-related settings."""
    current_function = inspect.currentframe().f_code.co_name
    changed_count = 0
    section = 'Amplifier'
    if not config.has_section(section):
        config.add_section(section)
    
    try:
        if hasattr(app_instance, 'selected_amplifier_type_var'):
            new_value = str(app_instance.selected_amplifier_type_var.get())
            if config.get(section, 'selected_amplifier_type', fallback=None) != new_value:
                config.set(section, 'selected_amplifier_type', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'selected_amplifier_type' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'amplifier_description_var'):
            new_value = str(app_instance.amplifier_description_var.get())
            if config.get(section, 'amplifier_description', fallback=None) != new_value:
                config.set(section, 'amplifier_description', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'amplifier_description' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'amplifier_use_var'):
            new_value = str(app_instance.amplifier_use_var.get())
            if config.get(section, 'amplifier_use', fallback=None) != new_value:
                config.set(section, 'amplifier_use', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'amplifier_use' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        
        if changed_count > 0:
            debug_log(f"🔧💾🔧💾✅ Amplifier settings saved.", file=os.path.basename(__file__), version=current_version, function=current_function)
    except Exception as e:
        debug_log(f"🔧💾🔧💾❌ Failed to save amplifier settings: {e}. The amplifier is on the fritz!", file=os.path.basename(__file__), version=current_version, function=current_function)

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
                debug_log(f"🔧💾📝 {section} - Changed 'operator_name' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'operator_contact_var'):
            new_value = str(app_instance.operator_contact_var.get())
            if config.get(section, 'operator_contact', fallback=None) != new_value:
                config.set(section, 'operator_contact', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'operator_contact' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'venue_name_var'):
            new_value = str(app_instance.venue_name_var.get())
            if config.get(section, 'venue_name', fallback=None) != new_value:
                config.set(section, 'venue_name', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'venue_name' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'address_field_var'):
            new_value = str(app_instance.address_field_var.get())
            if config.get(section, 'address_field', fallback=None) != new_value:
                config.set(section, 'address_field', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'address_field' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'city_var'):
            new_value = str(app_instance.city_var.get())
            if config.get(section, 'city', fallback=None) != new_value:
                config.set(section, 'city', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'city' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'province_var'):
            new_value = str(app_instance.province_var.get())
            if config.get(section, 'province', fallback=None) != new_value:
                config.set(section, 'province', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'province' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'venue_postal_code_var'):
            new_value = str(app_instance.venue_postal_code_var.get())
            if config.get(section, 'venue_postal_code', fallback=None) != new_value:
                config.set(section, 'venue_postal_code', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'venue_postal_code' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'notes_var'):
            new_value = str(app_instance.notes_var.get())
            if config.get(section, 'notes', fallback=None) != new_value:
                config.set(section, 'notes', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'notes' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'freq_shift_var'):
            new_value = str(app_instance.freq_shift_var.get())
            if config.get(section, 'freq_shift', fallback=None) != new_value:
                config.set(section, 'freq_shift', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'freq_shift' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'scanner_type_var'):
            new_value = str(app_instance.scanner_type_var.get())
            if config.get(section, 'scanner_type', fallback=None) != new_value:
                config.set(section, 'scanner_type', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'scanner_type' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1

        if changed_count > 0:
            debug_log(f"🔧💾🔧💾✅ Report settings saved.", file=os.path.basename(__file__), version=current_version, function=current_function)
    except Exception as e:
        debug_log(f"🔧💾🔧💾❌ Failed to save report settings: {e}. The report is a jumbled mess!", file=os.path.basename(__file__), version=current_version, function=current_function)

def _save_plotting_settings(config, app_instance, console_print_func):
    """Saves plotting-related settings."""
    current_function = inspect.currentframe().f_code.co_name
    changed_count = 0
    section = 'Plotting'
    if not config.has_section(section):
        config.add_section(section)
    
    try:
        if hasattr(app_instance, 'avg_include_tv_markers_var'):
            new_value = str(app_instance.avg_include_tv_markers_var.get())
            if config.get(section, 'avg_include_tv_markers', fallback=None) != new_value:
                config.set(section, 'avg_include_tv_markers', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'avg_include_tv_markers' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'avg_include_gov_markers_var'):
            new_value = str(app_instance.avg_include_gov_markers_var.get())
            if config.get(section, 'avg_include_gov_markers', fallback=None) != new_value:
                config.set(section, 'avg_include_gov_markers', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'avg_include_gov_markers' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'avg_include_markers_var'):
            new_value = str(app_instance.avg_include_markers_var.get())
            if config.get(section, 'avg_include_markers', fallback=None) != new_value:
                config.set(section, 'avg_include_markers', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'avg_include_markers' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1
        if hasattr(app_instance, 'avg_include_intermod_markers_var'):
            new_value = str(app_instance.avg_include_intermod_markers_var.get())
            if config.get(section, 'avg_include_intermod_markers', fallback=None) != new_value:
                config.set(section, 'avg_include_intermod_markers', new_value)
                debug_log(f"🔧💾📝 {section} - Changed 'avg_include_intermod_markers' to '{new_value}' from {current_function}", file=os.path.basename(__file__), version=current_version, function=current_function)
                changed_count += 1

        if changed_count > 0:
            debug_log(f"🔧💾🔧💾✅ Plotting settings saved.", file=os.path.basename(__file__), version=current_version, function=current_function)
    except Exception as e:
        debug_log(f"🔧💾🔧💾❌ Failed to save plotting settings: {e}. The plot thickens... and fails!", file=os.path.basename(__file__), version=current_version, function=current_function)


def save_config(config, file_path, console_print_func, app_instance):
    """
    Orchestrates saving all application settings by calling modular functions.
    This is the new public API for saving the config.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to save configuration to {file_path} via modular approach.",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)
    
    try:
        _save_application_settings(config, app_instance, console_print_func)
        _save_debug_settings(config, app_instance, console_print_func)
        _save_instrument_settings(config, app_instance, console_print_func)
        _save_marker_tab_settings(config, app_instance, console_print_func)
        _save_scan_info_settings(config, app_instance, console_print_func)
        _save_antenna_settings(config, app_instance, console_print_func)
        _save_amplifier_settings(config, app_instance, console_print_func)
        _save_report_settings(config, app_instance, console_print_func)
        _save_plotting_settings(config, app_instance, console_print_func)

        with open(file_path, 'w') as configfile:
            config.write(configfile)
            
        console_print_func("🔧💾✅ Configuration saved successfully. Persistence achieved!")
        debug_log(f"Configuration successfully written to {file_path}. Mission accomplished!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function, special=True)
        
    except Exception as e:
        error_message = f"🔧💾❌ Failed to save configuration: {e}. This is a critical failure! Fucking hell!"
        console_print_func(error_message)
        debug_log(error_message,
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)


def save_config_as_new_file(app_instance, new_file_path):
    """
    Saves the current application settings to a NEW specified .ini file.
    This creates a snapshot of the current configuration.
    """
    new_config = configparser.ConfigParser(interpolation=None)
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to save configuration as new file to {new_file_path}. Creating snapshot!",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function_name)
    
    try:
        _save_application_settings(new_config, app_instance, app_instance.console_print_func)
        _save_debug_settings(new_config, app_instance, app_instance.console_print_func)
        _save_instrument_settings(new_config, app_instance, app_instance.console_print_func)
        _save_marker_tab_settings(new_config, app_instance, app_instance.console_print_func)
        _save_scan_info_settings(new_config, app_instance, app_instance.console_print_func)
        _save_antenna_settings(new_config, app_instance, app_instance.console_print_func)
        _save_amplifier_settings(new_config, app_instance, app_instance.console_print_func)
        _save_report_settings(new_config, app_instance, app_instance.console_print_func)
        _save_plotting_settings(new_config, app_instance, app_instance.console_print_func)

        with open(new_file_path, 'w') as configfile:
            new_config.write(configfile)
        
        console_log(f"🔧💾✅ Configuration saved successfully as '{os.path.basename(new_file_path)}'. New file created!")
        debug_log(f"New configuration file created: {new_file_path}.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function_name)

    except Exception as e:
        error_message = f"🔧💾❌ Failed to save new configuration file: {e}. This is a problem!"
        console_log(error_message)
        debug_log(error_message,
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function_name)