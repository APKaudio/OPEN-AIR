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

current_version = "20250802.1800.8" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 1800 * 8 # Example hash, adjust as needed

import pyvisa
import time
import inspect
import os
from datetime import datetime
import csv

# Updated imports for new logging functions
from src.debug_logic import debug_log, log_visa_command
from src.console_logic import console_log

# Import read/write safe functions from the new dedicated module
from tabs.Instrument.utils_instrument_read_and_write import query_safe, write_safe
from tabs.Instrument.utils_instrument_initialize import initialize_instrument
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
                if app_instance.inst:
                    # After updating GUI, apply these settings to the instrument
                    # This requires the apply_settings_logic to be called with the updated Tkinter vars
                    # This is usually handled by the InstrumentTab's _apply_settings_to_instrument
                    # or a direct call to apply_settings_logic.
                    # For simplicity, we'll assume the GUI update is enough for now,
                    # and the user can manually apply if needed, or a subsequent query will sync.
                    # Or, if you want to apply automatically:
                    # from tabs.Instrument.instrument_logic import apply_settings_logic
                    # apply_settings_logic(app_instance, console_print_func)
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

