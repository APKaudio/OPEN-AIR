# tabs/Presets/utils_push_preset.py
#
# This file contains the logic for pushing saved preset settings to the connected instrument.
# It retrieves settings from the application instance and sends the appropriate SCPI commands.
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
# Version 20250821.173331.1
# UPDATED: The push_preset_logic now correctly uses YakSet and YakDo with proper command types
#          and includes all missing preset variables and trace configurations.

import os
import inspect
import re

from display.debug_logic import debug_log
from display.console_logic import console_log

from yak.Yakety_Yak import YakSet, YakDo
from ref.ref_frequency_bands import MHZ_TO_HZ

# --- Versioning ---
w = 20250821
x_str = '173331'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"


def push_preset_logic(app_instance, console_print_func, preset_data):
    """
    Function Description:
    Applies the current settings from the GUI (or a provided preset_data dictionary)
    to the connected instrument using the Yak command protocol.

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
    5. Sends SCPI commands to the instrument using YakSet and YakDo.
    6. Handles model-specific commands (e.g., for N9340B/N9342CN).
    7. Logs success or failure.

    Outputs:
    - True if settings are applied successfully, False otherwise.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Applying settings to instrument with the Yak Attack! Version: {current_version}",
                file=current_file,
                version=current_version,
                function=current_function)

    if not app_instance.inst:
        console_print_func("❌ No instrument connected. Please connect to an instrument first. What are you doing?!")
        debug_log("No instrument connected. Cannot apply settings.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return False

    success = True
    try:
        center_freq_mhz_str = preset_data.get('Center', '').strip()
        center_freq_hz = float(center_freq_mhz_str) * MHZ_TO_HZ if center_freq_mhz_str else None

        span_mhz_str = preset_data.get('Span', '').strip()
        span_hz = float(span_mhz_str) * MHZ_TO_HZ if span_mhz_str else None

        rbw_hz_str = preset_data.get('RBW', '').strip()
        rbw_hz = float(rbw_hz_str) if rbw_hz_str else None

        vbw_hz_str = preset_data.get('VBW', '').strip()
        vbw_hz = float(vbw_hz_str) if vbw_hz_str else None

        ref_level_str = preset_data.get('RefLevel', '').strip()
        reference_level_dbm = ref_level_str if ref_level_str else None

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

        console_print_func("💬 Applying settings to instrument using Yak commands...")

        if center_freq_hz is not None:
            if YakSet(app_instance, "FREQUENCY/CENTER", str(int(center_freq_hz)), console_print_func) == "FAILED": success = False
            debug_log(f"Applied Center Frequency: {int(center_freq_hz)} Hz.", file=current_file, version=current_version, function=current_function)
        if span_hz is not None:
            if YakSet(app_instance, "FREQUENCY/SPAN", str(int(span_hz)), console_print_func) == "FAILED": success = False
            debug_log(f"Applied Span Frequency: {int(span_hz)} Hz.", file=current_file, version=current_version, function=current_function)
        if attenuation_db is not None:
            if YakSet(app_instance, "AMPLITUDE/POWER/ATTENUATION", str(attenuation_db), console_print_func) == "FAILED": success = False
            debug_log(f"Applied Attenuation: {attenuation_db} dB.", file=current_file, version=current_version, function=current_function)

        if rbw_hz is not None:
            if YakSet(app_instance, "BANDWIDTH/RESOLUTION", str(int(rbw_hz)), console_print_func) == "FAILED": success = False
            debug_log(f"Applied RBW: {int(rbw_hz)} Hz.", file=current_file, version=current_version, function=current_function)
        if vbw_hz is not None:
            if YakSet(app_instance, "BANDWIDTH/VIDEO", str(int(vbw_hz)), console_print_func) == "FAILED": success = False
            debug_log(f"Applied VBW: {int(vbw_hz)} Hz.", file=current_file, version=current_version, function=current_function)

        if reference_level_dbm is not None:
            if YakDo(app_instance, f"AMPLITUDE/REFERENCE LEVEL/{reference_level_dbm}", console_print_func) == "FAILED": success = False
            debug_log(f"Applied Reference Level: {reference_level_dbm} dBm.", file=current_file, version=current_version, function=current_function)

        if high_sensitivity_on is not None:
            if YakSet(app_instance, "AMPLITUDE/POWER/HIGH SENSITIVE", 'ON' if high_sensitivity_on else 'OFF', console_print_func) == "FAILED": success = False
            debug_log(f"Applied High Sensitivity: {'ON' if high_sensitivity_on else 'OFF'}.", file=current_file, version=current_version, function=current_function)
        if preamp_on is not None:
            if YakSet(app_instance, "AMPLITUDE/POWER/GAIN", 'ON' if preamp_on else 'OFF', console_print_func) == "FAILED": success = False
            debug_log(f"Applied Preamp: {'ON' if preamp_on else 'OFF'}.", file=current_file, version=current_version, function=current_function)
        
        if trace1_mode:
            if YakDo(app_instance, f"TRACE/1/MODE/{trace1_mode}", console_print_func) == "FAILED": success = False
            debug_log(f"Applied Trace 1 Mode: {trace1_mode}.", file=current_file, version=current_version, function=current_function)
        if trace2_mode:
            if YakDo(app_instance, f"TRACE/2/MODE/{trace2_mode}", console_print_func) == "FAILED": success = False
            debug_log(f"Applied Trace 2 Mode: {trace2_mode}.", file=current_file, version=current_version, function=current_function)
        if trace3_mode:
            if YakDo(app_instance, f"TRACE/3/MODE/{trace3_mode}", console_print_func) == "FAILED": success = False
            debug_log(f"Applied Trace 3 Mode: {trace3_mode}.", file=current_file, version=current_version, function=current_function)
        if trace4_mode:
            if YakDo(app_instance, f"TRACE/4/MODE/{trace4_mode}", console_print_func) == "FAILED": success = False
            debug_log(f"Applied Trace 4 Mode: {trace4_mode}.", file=current_file, version=current_version, function=current_function)

        if marker1_max:
            if YakSet(app_instance, "MARKER/1/CALCULATE/MAX", 'ON' if marker1_max.upper() == 'WRITE' else 'OFF', console_print_func) == "FAILED": success = False
            debug_log(f"Applied Marker 1 Max: {marker1_max}.", file=current_file, version=current_version, function=current_function)
        if marker2_max:
            if YakSet(app_instance, "MARKER/2/CALCULATE/MAX", 'ON' if marker2_max.upper() == 'WRITE' else 'OFF', console_print_func) == "FAILED": success = False
            debug_log(f"Applied Marker 2 Max: {marker2_max}.", file=current_file, version=current_version, function=current_function)
        if marker3_max:
            if YakSet(app_instance, "MARKER/3/CALCULATE/MAX", 'ON' if marker3_max.upper() == 'WRITE' else 'OFF', console_print_func) == "FAILED": success = False
            debug_log(f"Applied Marker 3 Max: {marker3_max}.", file=current_file, version=current_version, function=current_function)
        if marker4_max:
            if YakSet(app_instance, "MARKER/4/CALCULATE/MAX", 'ON' if marker4_max.upper() == 'WRITE' else 'OFF', console_print_func) == "FAILED": success = False
            debug_log(f"Applied Marker 4 Max: {marker4_max}.", file=current_file, version=current_version, function=current_function)
        if marker5_max:
            if YakSet(app_instance, "MARKER/5/CALCULATE/MAX", 'ON' if marker5_max.upper() == 'WRITE' else 'OFF', console_print_func) == "FAILED": success = False
            debug_log(f"Applied Marker 5 Max: {marker5_max}.", file=current_file, version=current_version, function=current_function)
        if marker6_max:
            if YakSet(app_instance, "MARKER/6/CALCULATE/MAX", 'ON' if marker6_max.upper() == 'WRITE' else 'OFF', console_print_func) == "FAILED": success = False
            debug_log(f"Applied Marker 6 Max: {marker6_max}.", file=current_file, version=current_version, function=current_function)


        if success:
            console_print_func("✅ All settings applied successfully. Boom!")
            debug_log("All settings applied to instrument. Fucking awesome!",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        else:
            console_print_func("❌ Failed to apply all settings. This thing is a pain in the ass!")
            debug_log("Failed to apply all settings.",
                        file=current_file,
                        version=current_version,
                        function=current_function)

        return success
    except ValueError as e:
        console_print_func(f"❌ Invalid setting value: {e}. Please check your inputs. You entered some garbage!")
        debug_log(f"ValueError applying settings: {e}. User entered some crap.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return False
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred while applying settings: {e}. This thing is a pain in the ass!")
        debug_log(f"An unexpected error occurred applying settings: {e}. Fucking hell!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return False