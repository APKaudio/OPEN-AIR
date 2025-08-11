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
# Version 20250802.1701.10 (Refactored from utils_preset.py to handle query and load logic.)
# Version 20250802.1800.8 (Updated load_selected_preset_logic to handle local presets via dict.)
# Version 20250803.1740.0 (FIXED: ImportError for 'initialize_instrument' by correcting import to 'initialize_instrument_logic'.)

current_version = "20250802.1800.8" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 1800 * 8 # Example hash, adjust as needed

import pyvisa
import time
import inspect
import os
from datetime import datetime
import csv

# Updated imports for new logging functions
from display.debug_logic import debug_log, log_visa_command
from display.console_logic import console_log

# Import read/write safe functions from the new dedicated module
from tabs.Instrument.utils_instrument_read_and_write import query_safe, write_safe
from tabs.Instrument.utils_instrument_initialization import initialize_instrument_logic # CORRECTED: Changed import name
from tabs.Instrument.utils_instrument_query_settings import query_current_instrument_settings
from tabs.Instrument.utils_instrument_connection import connect_to_instrument, disconnect_instrument, list_visa_resources


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
                file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                version=current_version,
                function=current_function)

    if not app_instance.inst:
        console_print_func("❌ No instrument connected. Cannot query device presets.")
        debug_log("No instrument connected. Aborting device preset query.",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)
        return []

    # Check if the connected device is N9342CN
    if hasattr(app_instance, 'connected_instrument_model') and \
       app_instance.connected_instrument_model.get() != "N9342CN":
        console_print_func("⚠️ Device is not N9342CN. Cannot query device presets (feature limited to N9342CN).")
        debug_log("Device is not N9342CN. Aborting device preset query.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return []

    try:
        # Query the instrument for a catalog of its saved states/presets
        response = query_safe(app_instance.inst, ":MMEMory:CATalog:STATe?", console_print_func)
        if response:
            # The response is typically a comma-separated string of filenames/preset names
            preset_names = [name.strip().strip('"') for name in response.split(',') if name.strip()]
            console_print_func(f"✅ Found {len(preset_names)} device presets.")
            debug_log(f"Device presets found: {preset_names}.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
            return preset_names
        else:
            console_print_func("ℹ️ No device presets found or query failed.")
            debug_log("No device presets found or query returned empty response.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
            return []
    except Exception as e:
        console_print_func(f"❌ Error querying device presets: {e}. This is a disaster!")
        debug_log(f"Error querying device presets: {e}. Fucking hell!",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
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
        tuple: (success (bool), center_freq_hz (float), span_hz (float), rbw_hz (float))
               Returns (False, 0.0, 0.0, 0.0) on failure.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to load preset: '{selected_preset_name}'. Is Device Preset: {is_device_preset}.",
                file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                version=current_version,
                function=current_function)

    center_freq_hz = 0.0
    span_hz = 0.0
    rbw_hz = 0.0

    try:
        if is_device_preset:
            if not app_instance.inst:
                console_print_func("❌ No instrument connected. Cannot load device preset.")
                debug_log("No instrument connected. Aborting device preset load.",
                            file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                            version=current_version,
                            function=current_function)
                return False, 0.0, 0.0, 0.0

            # Check if the connected device is N9342CN for loading device presets
            if hasattr(app_instance, 'connected_instrument_model') and \
               app_instance.connected_instrument_model.get() != "N9342CN":
                console_print_func("⚠️ Device is not N9342CN. Cannot load device presets (feature limited to N9342CN).")
                debug_log("Device is not N9342CN. Aborting device preset load.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                return False, 0.0, 0.0, 0.0

            # Load the preset from the instrument's memory
            # The command might vary, typically it's MMEMory:LOAD:STATe "<preset_name>"
            load_command = f":MMEMory:LOAD:STATe \"{selected_preset_name}\""
            if write_safe(app_instance.inst, load_command, console_print_func):
                console_print_func(f"✅ Device preset '{selected_preset_name}' loaded to instrument.")
                debug_log(f"Device preset '{selected_preset_name}' loaded to instrument.",
                            file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                            version=current_version,
                            function=current_function)
                
                # After loading, query the instrument for its current settings to update GUI
                center_freq_mhz, span_mhz, rbw_hz_val, ref_level_dbm, preamp_on, high_sensitivity = \
                    query_current_instrument_settings(app_instance.inst, console_print_func)
                
                center_freq_hz = center_freq_mhz * app_instance.MHZ_TO_HZ if center_freq_mhz is not None else 0.0
                span_hz = span_mhz * app_instance.MHZ_TO_HZ if span_mhz is not None else 0.0
                rbw_hz = rbw_hz_val if rbw_hz_val is not None else 0.0

                # Update Tkinter variables in the app instance
                app_instance.center_freq_hz_var.set(center_freq_hz)
                app_instance.span_hz_var.set(span_hz)
                app_instance.rbw_hz_var.set(rbw_hz)
                app_instance.reference_level_dbm_var.set(ref_level_dbm)
                app_instance.preamp_on_var.set(preamp_on)
                app_instance.high_sensitivity_var.set(high_sensitivity)

                console_print_func(f"GUI settings updated from device preset: Center Freq={center_freq_mhz:.3f} MHz, Span={span_mhz:.3f} MHz, RBW={rbw_hz / 1000:.1f} kHz. Looking good!")
                debug_log(f"GUI settings updated from loaded device preset.",
                            file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                            version=current_version,
                            function=current_function)
                return True, center_freq_hz, span_hz, rbw_hz
            else:
                console_print_func(f"❌ Failed to load device preset '{selected_preset_name}'. This is frustrating!")
                debug_log(f"Failed to load device preset '{selected_preset_name}'. What a pain!",
                            file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                            version=current_version,
                            function=current_function)
                return False, 0.0, 0.0, 0.0
        else: # It's a local user preset
            if preset_data_dict:
                # Update Tkinter variables directly from the provided dictionary
                center_freq_hz = float(preset_data_dict.get('Center', 0.0))
                span_hz = float(preset_data_dict.get('Span', 0.0))
                rbw_hz = float(preset_data_dict.get('RBW', 0.0))
                # Markers data is in preset_data_dict['Markers'] but not directly mapped to a Tkinter var for instrument control

                app_instance.center_freq_hz_var.set(center_freq_hz)
                app_instance.span_hz_var.set(span_hz)
                app_instance.rbw_hz_var.set(rbw_hz)

                # For other settings like RefLevel, Preamp, High Sensitivity,
                # you would need to store them in the CSV and retrieve them here.
                # For now, they are not part of the basic CSV structure, so they won't be updated.
                # If the instrument is connected, you might want to apply these settings.
                # This is usually handled by the _update_gui_from_preset_data in LocalPresetsTab
                pass # Handled by the _update_gui_from_preset_data in LocalPresetsTab

                console_print_func(f"GUI settings updated from preset: Center Freq={center_freq_hz / app_instance.MHZ_TO_HZ:.3f} MHz, Span={span_hz / app_instance.MHZ_TO_HZ:.3f} MHz, RBW={rbw_hz:.0f} Hz. Looking good!")
                debug_log(f"GUI settings updated from loaded local preset.",
                            file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                            version=current_version,
                            function=current_function)
                return True, center_freq_hz, span_hz, rbw_hz
            else:
                console_print_func(f"❌ Failed to load local preset '{selected_preset_name}'. Preset data not provided.")
                debug_log(f"Failed to load local preset '{selected_preset_name}'. Preset data dictionary is missing.",
                            file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                            version=current_version,
                            function=current_function)
                return False, 0.0, 0.0, 0.0

    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred in load_selected_preset_logic: {e}. This is a disaster!")
        debug_log(f"An unexpected error occurred in load_selected_preset_logic: {e}. Fucking hell!",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)
        return False, 0.0, 0.0, 0.0




def query_current_instrument_settings_for_preset(inst, MHZ_TO_HZ_CONVERSION, console_print_func=None):
    """
    Function Description:
    Queries and returns the current Center Frequency, Span, and RBW from the instrument.

    Inputs:
        inst (pyvisa.resources.Resource): The connected VISA instrument object.
        MHZ_TO_HZ_CONVERSION (float): The conversion factor from MHz to Hz.
        console_print_func (function, optional): Function to print to the GUI console.
                                               Defaults to console_log if None.
    Outputs:
        tuple: (center_freq_mhz, span_mhz, rbw_hz) or (None, None, None) on failure.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Querying current instrument settings... Let's see what's happening!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    if not inst:
        debug_log("No instrument connected to query settings. Fucking useless!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        console_print_func("⚠️ Warning: No instrument connected. Cannot query settings. Connect the damn thing first!")
        return None, None, None

    center_freq_hz = None
    span_hz = None
    rbw_hz = None

    try:
        # Query Center Frequency
        center_freq_str = query_safe(inst, ":SENSe:FREQuency:CENTer?", console_print_func)
        if center_freq_str:
            center_freq_hz = float(center_freq_str)

        # Query Span
        span_str = query_safe(inst, ":SENSe:FREQuency:SPAN?", console_print_func)
        if span_str:
            span_hz = float(span_str)

        # Query RBW
        rbw_str = query_safe(inst, ":SENSe:BANDwidth:RESolution?", console_print_func)
        if rbw_str:
            rbw_hz = float(rbw_str)

        center_freq_mhz = center_freq_hz / MHZ_TO_HZ_CONVERSION if center_freq_hz is not None else None
        span_mhz = span_hz / MHZ_TO_HZ_CONVERSION if span_hz is not None else None

        debug_log(f"Queried settings: Center Freq: {center_freq_mhz:.3f} MHz, Span: {span_mhz:.3f} MHz, RBW: {rbw_hz} Hz. Got the info!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        console_print_func(f"✅ Queried settings: C: {center_freq_mhz:.3f} MHz, SP: {span_mhz:.3f} MHz, RBW: {rbw_hz / 1000:.1f} kHz. Details acquired!")

        return center_freq_mhz, span_mhz, rbw_hz

    except Exception as e:
        debug_log(f"❌ Error querying current instrument settings: {e}. What a mess!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        console_print_func(f"❌ Error querying current instrument settings: {e}. This is a disaster!")
        return None, None, None
