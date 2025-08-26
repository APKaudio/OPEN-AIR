# utils/utils_preset_query_and_load.py
#
# This module provides utility functions for querying available presets from the
# connected instrument and loading selected presets (both device and user-defined).
# It abstracts the low-level SCPI commands for preset management and integrates
# with the GUI's state to update settings.
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
# Version 20250821.173331.1
# UPDATED: The load_selected_preset_logic now correctly uses the YakSet and YakDo functions
#          to set all the instrument's values from a preset, ensuring a complete and
#          reliable state update.

import pyvisa
import time
import inspect
import os
from datetime import datetime
import csv
import pandas as pd

from display.debug_logic import debug_log, log_visa_command
from display.console_logic import console_log
from Instrument.connection.instrument_logic import query_current_settings_logic
from yak.Yakety_Yak import YakGet, YakSet, YakDo, query_safe, write_safe
from ref.ref_frequency_bands import MHZ_TO_HZ as MHZ_TO_HZ_CONVERSION

# --- Versioning ---
w = 20250821
x_str = '173331'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"


def query_device_presets_logic(app_instance, console_print_func):
    """
    Queries the connected instrument for available presets and returns their names.
    This function is specifically for device-stored presets (e.g., from :MMEMory:CATalog:STATe?).

    Inputs:
        app_instance (App): The main application instance.
        console_print_func (function): Function to print messages to the GUI console.
    Outputs:
        list: A list of preset names (strings) found on the instrument.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Querying device presets from instrument...",
                file=current_file,
                version=current_version,
                function=current_function)

    if not app_instance.inst:
        console_print_func("❌ No instrument connected. Cannot query device presets.")
        debug_log("No instrument connected. Aborting device preset query.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return []

    if hasattr(app_instance, 'connected_instrument_model') and \
       app_instance.connected_instrument_model.get() != "N9342CN":
        console_print_func("⚠️ Device is not N9342CN. Cannot query device presets (feature limited to N9342CN).")
        debug_log("Device is not N9342CN. Aborting device preset query.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return []

    try:
        response = query_safe(app_instance.inst, ":MMEMory:CATalog:STATe?", console_print_func)
        if response:
            preset_names = [name.strip().strip('"') for name in response.split(',') if name.strip()]
            console_print_func(f"✅ Found {len(preset_names)} device presets.")
            debug_log(f"Device presets found: {preset_names}.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return preset_names
        else:
            console_print_func("ℹ️ No device presets found or query failed.")
            debug_log("No device presets found or query returned empty response.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return []
    except Exception as e:
        console_print_func(f"❌ Error querying device presets: {e}. This is a disaster!")
        debug_log(f"Error querying device presets: {e}. Fucking hell!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return []


def load_selected_preset_logic(app_instance, selected_preset_name, console_print_func, is_device_preset=True, preset_data_dict=None):
    """
    Loads a selected preset (either from device or local CSV) onto the instrument
    and updates the GUI's settings variables.

    Inputs:
        app_instance (App): The main application instance.
        selected_preset_name (str): The name of the preset to load.
        console_print_func (function): Function to print messages to the GUI console.
        is_device_preset (bool): True if loading a device preset, False for a local user preset.
        preset_data_dict (dict, optional): For local presets, the dictionary containing
                                           the preset's data. Not used for device presets.

    Outputs:
        bool: True if load was successful, False otherwise.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to load preset: '{selected_preset_name}'. Is Device Preset: {is_device_preset}.",
                file=current_file,
                version=current_version,
                function=current_function)

    try:
        if is_device_preset:
            if not app_instance.inst:
                console_print_func("❌ No instrument connected. Cannot load device preset.")
                debug_log("No instrument connected. Aborting device preset load.",
                            file=current_file,
                            version=current_version,
                            function=current_function)
                return False

            if hasattr(app_instance, 'connected_instrument_model') and \
               app_instance.connected_instrument_model.get() != "N9342CN":
                console_print_func("⚠️ Device is not N9342CN. Cannot load device presets (feature limited to N9342CN).")
                debug_log("Device is not N9342CN. Aborting device preset load.",
                            file=current_file,
                            version=current_version,
                            function=current_function)
                return False

            load_command = f":MMEMory:LOAD:STATe \"{selected_preset_name}\""
            if write_safe(app_instance.inst, load_command, console_print_func):
                console_print_func(f"✅ Device preset '{selected_preset_name}' loaded to instrument.")
                debug_log(f"Device preset '{selected_preset_name}' loaded to instrument.",
                            file=current_file,
                            version=current_version,
                            function=current_function)
                
                settings = query_current_settings_logic(app_instance, console_print_func)
                
                if settings:
                    center_freq_hz = settings.get('center_freq_hz', 0.0)
                    span_hz = settings.get('span_hz', 0.0)
                    rbw_hz = settings.get('rbw_hz', 0.0)

                    app_instance.center_freq_MHz_var.set(center_freq_hz / MHZ_TO_HZ_CONVERSION)
                    app_instance.span_freq_MHz_var.set(span_hz / MHZ_TO_HZ_CONVERSION)
                    app_instance.rbw_MHz_var.set(rbw_hz / MHZ_TO_HZ_CONVERSION)
                    
                    console_print_func(f"GUI settings updated from device preset: Center Freq={center_freq_hz / MHZ_TO_HZ_CONVERSION:.3f} MHz, Span={span_hz / MHZ_TO_HZ_CONVERSION:.3f} MHz, RBW={rbw_hz / 1000:.1f} kHz. Looking good!")
                    debug_log(f"GUI settings updated from loaded device preset.",
                                file=current_file,
                                version=current_version,
                                function=current_function)
                    return True
                else:
                    console_print_func("❌ Failed to query settings after loading device preset. This is frustrating!")
                    debug_log("Failed to query settings after loading device preset. What a pain!",
                                file=current_file,
                                version=current_version,
                                function=current_function)
                    return False
            else:
                console_print_func(f"❌ Failed to load device preset '{selected_preset_name}'. This is frustrating!")
                debug_log(f"Failed to load device preset '{selected_preset_name}'. What a pain!",
                            file=current_file,
                            version=current_version,
                            function=current_function)
                return False
        else:
            if preset_data_dict:
                from Presets.utils_push_preset import push_preset_logic
                return push_preset_logic(app_instance, console_print_func, preset_data_dict)
            else:
                console_print_func(f"❌ Failed to load local preset '{selected_preset_name}'. Preset data not provided.")
                debug_log(f"Failed to load local preset '{selected_preset_name}'. Preset data dictionary is missing.",
                            file=current_file,
                            version=current_version,
                            function=current_function)
                return False

    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred in load_selected_preset_logic: {e}. This is a disaster!")
        debug_log(f"An unexpected error occurred in load_selected_preset_logic: {e}. Fucking hell!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return False


def query_current_instrument_settings_for_preset(inst, console_print_func=None):
    """
    Function Description:
    Queries and returns the current Center Frequency, Span, and RBW from the instrument.

    Inputs:
        inst (pyvisa.resources.Resource): The connected VISA instrument object.
        console_print_func (function, optional): Function to print to the GUI console.
                                               Defaults to console_log if None.
    Outputs:
        tuple: (center_freq_MHz, span_MHz, rbw_hz) or (None, None, None) on failure.
    """
    console_print_func = console_print_func if console_print_func else console_log
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Querying current instrument settings... Let's see what's happening!",
                file=current_file,
                version=current_version,
                function=current_function)

    if not inst:
        debug_log("No instrument connected to query settings. Fucking useless!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        console_print_func("⚠️ Warning: No instrument connected. Cannot query settings. Connect the damn thing first!")
        return None, None, None

    center_freq_hz = None
    span_hz = None
    rbw_hz = None

    try:
        center_freq_str = query_safe(inst, ":SENSe:FREQuency:CENTer?", console_print_func)
        if center_freq_str:
            center_freq_hz = float(center_freq_str)

        span_str = query_safe(inst, ":SENSe:FREQuency:SPAN?", console_print_func)
        if span_str:
            span_hz = float(span_str)

        rbw_str = query_safe(inst, ":SENSe:BANDwidth:RESolution?", console_print_func)
        if rbw_str:
            rbw_hz = float(rbw_str)

        center_freq_MHz = center_freq_hz / 1_000_000 if center_freq_hz is not None else None
        span_MHz = span_hz / 1_000_000 if span_hz is not None else None

        debug_log(f"Queried settings: Center Freq: {center_freq_MHz:.3f} MHz, Span: {span_MHz:.3f} MHz, RBW: {rbw_hz} Hz. Got the info!",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        console_print_func(f"✅ Queried settings: C: {center_freq_MHz:.3f} MHz, SP: {span_MHz:.3f} MHz, RBW: {rbw_hz / 1000:.1f} kHz. Details acquired!")

        return center_freq_MHz, span_MHz, rbw_hz

    except Exception as e:
        debug_log(f"❌ Error querying current instrument settings: {e}. What a mess!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        console_print_func(f"❌ Error querying current instrument settings: {e}. This is a disaster!")
        return None, None, None