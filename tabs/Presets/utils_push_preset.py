# src/utils_push_preset.py
#
# This file contains the logic for pushing saved preset settings to the connected instrument.
# It retrieves settings from the application instance and sends the appropriate SCPI commands.
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
# Version 20250802.1702.1 (Added trace mode and marker calculation settings to push preset logic for N9340B.)
# Version 20250802.2300.0 (Modified push_preset_logic to accept preset_data dict and handle empty/BLANK values.)
# Version 20250803.0040.0 (FIXED: Corrected Center/Span frequency conversion from MHz to Hz for SCPI commands.)
# Version 20250803.0045.0 (FIXED: Removed unused 'read_safe' import to resolve ImportError.)
# Version 20250803.1730.0 (FIXED: ImportError for 'initialize_instrument' by correcting import to 'initialize_instrument_logic'.)

current_version = "20250803.0045.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 45 * 0 # Example hash, adjust as needed.

import os
import inspect # Import inspect module
import re # For regular expressions to match instrument model

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

from tabs.Instrument.utils_instrument_initialization import (
    initialize_instrument_logic # CORRECTED: Changed from initialize_instrument
)
from tabs.Instrument.utils_instrument_read_and_write import (
    write_safe,
    # read_safe # Removed as it's not used in this module and causing ImportError
)
from ref.frequency_bands import MHZ_TO_HZ # NEW: Import MHZ_TO_HZ for conversions

def push_preset_logic(app_instance, console_print_func, preset_data):
    """
    Function Description:
    Applies the current settings from the GUI (or a provided preset_data dictionary)
    to the connected instrument.

    Inputs:
    - app_instance: The main application instance, used to access Tkinter variables and retrieve settings.
    - console_print_func: A function to print messages to the GUI console.
    - preset_data (dict): A dictionary containing the preset settings to apply.
                          Keys should match the CSV headers (e.g., 'Center', 'Span', 'RBW').

    Process:
    1. Logs the start of applying settings.
    2. Checks if an instrument is connected.
    3. Retrieves settings from the provided preset_data dictionary.
    4. Converts frequency values (Center, Span) from MHz to Hz for SCPI commands.
    5. Sends SCPI commands to the instrument to apply settings.
    6. Handles model-specific commands (e.g., for N9340B/N9342CN).
    7. Logs success or failure.

    Outputs:
    - True if settings are applied successfully, False otherwise.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Applying settings to instrument. Let's dial this in! Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    if not app_instance.inst:
        console_print_func("❌ No instrument connected. Please connect to an instrument first. What are you doing?!")
        debug_log("No instrument connected. Cannot apply settings.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False

    try:
        # Retrieve values from preset_data, handling potential missing keys or empty strings
        # Use .strip() to handle whitespace, and convert to float/int where necessary.
        # If a value is missing or empty, it will be treated as None or default.

        # Center and Span are in MHz in the CSV, convert to Hz for instrument
        center_freq_mhz_str = preset_data.get('Center', '').strip()
        center_freq_hz = float(center_freq_mhz_str) * MHZ_TO_HZ if center_freq_mhz_str else None

        span_mhz_str = preset_data.get('Span', '').strip()
        span_hz = float(span_mhz_str) * MHZ_TO_HZ if span_mhz_str else None

        # RBW and VBW are in Hz in the CSV
        rbw_hz_str = preset_data.get('RBW', '').strip()
        rbw_hz = float(rbw_hz_str) if rbw_hz_str else None

        vbw_hz_str = preset_data.get('VBW', '').strip()
        vbw_hz = float(vbw_hz_str) if vbw_hz_str else None

        ref_level_str = preset_data.get('RefLevel', '').strip()
        reference_level_dbm = float(ref_level_str) if ref_level_str else None

        attenuation_str = preset_data.get('Attenuation', '').strip()
        attenuation_db = int(attenuation_str) if attenuation_str else None

        maxhold_str = preset_data.get('MaxHold', '').strip()
        maxhold_enabled = maxhold_str.upper() == 'ON' if maxhold_str else None

        high_sensitivity_str = preset_data.get('HighSens', '').strip()
        high_sensitivity_on = high_sensitivity_str.upper() == 'ON' if high_sensitivity_str else None

        preamp_str = preset_data.get('PreAmp', '').strip()
        preamp_on = preamp_str.upper() == 'ON' if preamp_str else None

        trace1_mode = preset_data.get('Trace1Mode', '').strip()
        trace2_mode = preset_data.get('Trace2Mode', '').strip()
        trace3_mode = preset_data.get('Trace3Mode', '').strip()
        trace4_mode = preset_data.get('Trace4Mode', '').strip()

        marker1_max = preset_data.get('Marker1Max', '').strip()
        marker2_max = preset_data.get('Marker2Max', '').strip()
        marker3_max = preset_data.get('Marker3Max', '').strip()
        marker4_max = preset_data.get('Marker4Max', '').strip()
        marker5_max = preset_data.get('Marker5Max', '').strip()
        marker6_max = preset_data.get('Marker6Max', '').strip()


        console_print_func("💬 Applying settings to instrument...")

        # Apply Center, Span, Attenuation if their values are present (not empty strings)
        if center_freq_hz is not None:
            write_safe(app_instance.inst, f":SENSe:FREQuency:CENTer {center_freq_hz}", console_print_func)
            debug_log(f"Applied Center Frequency: {center_freq_hz} Hz.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
        if span_hz is not None:
            write_safe(app_instance.inst, f":SENSe:FREQuency:SPAN {span_hz}", console_print_func)
            debug_log(f"Applied Span Frequency: {span_hz} Hz.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
        if attenuation_db is not None:
            write_safe(app_instance.inst, f":POWer:ATTenuation {attenuation_db}", console_print_func)
            debug_log(f"Applied Attenuation: {attenuation_db} dB.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)

        # Apply RBW and VBW
        if rbw_hz is not None:
            write_safe(app_instance.inst, f":SENSe:BANDwidth:RESolution {rbw_hz}", console_print_func)
            debug_log(f"Applied RBW: {rbw_hz} Hz.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
        if vbw_hz is not None:
            write_safe(app_instance.inst, f":SENSe:BANDwidth:VIDeo {vbw_hz}", console_print_func)
            debug_log(f"Applied VBW: {vbw_hz} Hz.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)

        # Apply Reference Level
        if reference_level_dbm is not None:
            write_safe(app_instance.inst, f":DISPlay:WINDow:TRACe:Y:RLEVel {reference_level_dbm}", console_print_func)
            debug_log(f"Applied Reference Level: {reference_level_dbm} dBm.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)

        # Apply MaxHold
        if maxhold_enabled is not None:
            write_safe(app_instance.inst, f":DISPlay:WINDow:TRACe:MAXHold {'ON' if maxhold_enabled else 'OFF'}", console_print_func)
            debug_log(f"Applied MaxHold: {'ON' if maxhold_enabled else 'OFF'}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)

        # Apply High Sensitivity (N9340B specific)
        model_match = app_instance.connected_instrument_model.get()
        if model_match and re.match(r"N9340B|N9342CN", model_match, re.IGNORECASE):
            if high_sensitivity_on is not None:
                write_safe(app_instance.inst, f":POWer:HSENse {'ON' if high_sensitivity_on else 'OFF'}", console_print_func)
                debug_log(f"Applied High Sensitivity: {'ON' if high_sensitivity_on else 'OFF'}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
            if preamp_on is not None:
                write_safe(app_instance.inst, f":POWer:GAIN:STATe {'ON' if preamp_on else 'OFF'}", console_print_func)
                debug_log(f"Applied Preamp: {'ON' if preamp_on else 'OFF'}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
            
            # Apply Trace Modes (N9340B specific)
            if trace1_mode:
                write_safe(app_instance.inst, f":TRACe1:MODE {trace1_mode}", console_print_func)
                debug_log(f"Applied Trace 1 Mode: {trace1_mode}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
            if trace2_mode:
                write_safe(app_instance.inst, f":TRACe2:MODE {trace2_mode}", console_print_func)
                debug_log(f"Applied Trace 2 Mode: {trace2_mode}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
            if trace3_mode:
                write_safe(app_instance.inst, f":TRACe3:MODE {trace3_mode}", console_print_func)
                debug_log(f"Applied Trace 3 Mode: {trace3_mode}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
            if trace4_mode:
                write_safe(app_instance.inst, f":TRACe4:MODE {trace4_mode}", console_print_func)
                debug_log(f"Applied Trace 4 Mode: {trace4_mode}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)

            # Apply Marker Max settings (N9340B specific)
            if marker1_max:
                write_safe(app_instance.inst, f":CALCulate:MARKer1:MAX:STATe {'ON' if marker1_max.upper() == 'WRITE' else 'OFF'}", console_print_func)
                debug_log(f"Applied Marker 1 Max: {marker1_max}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
            if marker2_max:
                write_safe(app_instance.inst, f":CALCulate:MARKer2:MAX:STATe {'ON' if marker2_max.upper() == 'WRITE' else 'OFF'}", console_print_func)
                debug_log(f"Applied Marker 2 Max: {marker2_max}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
            if marker3_max:
                write_safe(app_instance.inst, f":CALCulate:MARKer3:MAX:STATe {'ON' if marker3_max.upper() == 'WRITE' else 'OFF'}", console_print_func)
                debug_log(f"Applied Marker 3 Max: {marker3_max}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
            if marker4_max:
                write_safe(app_instance.inst, f":CALCulate:MARKer4:MAX:STATe {'ON' if marker4_max.upper() == 'WRITE' else 'OFF'}", console_print_func)
                debug_log(f"Applied Marker 4 Max: {marker4_max}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
            if marker5_max:
                write_safe(app_instance.inst, f":CALCulate:MARKer5:MAX:STATe {'ON' if marker5_max.upper() == 'WRITE' else 'OFF'}", console_print_func)
                debug_log(f"Applied Marker 5 Max: {marker5_max}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
            if marker6_max:
                write_safe(app_instance.inst, f":CALCulate:MARKer6:MAX:STATe {'ON' if marker6_max.upper() == 'WRITE' else 'OFF'}", console_print_func)
                debug_log(f"Applied Marker 6 Max: {marker6_max}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
        else:
            debug_log(f"Skipping N9340B specific settings for instrument model: {model_match}. This is not an N9340B or N9342CN.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

        console_print_func("✅ All settings applied successfully. Boom!")
        debug_log("All settings applied to instrument. Fucking awesome!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return True
    except ValueError as e:
        console_print_func(f"❌ Invalid setting value: {e}. Please check your inputs. You entered some garbage!")
        debug_log(f"ValueError applying settings: {e}. User entered some crap.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred while applying settings: {e}. This thing is a pain in the ass!")
        debug_log(f"An unexpected error occurred applying settings: {e}. Fucking hell!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False
