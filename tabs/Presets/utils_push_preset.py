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

current_version = "20250802.1702.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 1702 * 1 # Example hash, adjust as needed

import os
import inspect # Import inspect module

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

from tabs.Instrument.utils_instrument_initialize import (
    initialize_instrument
)
from tabs.Instrument.utils_instrument_read_and_write import (
    write_safe,
    query_safe
)


def push_preset_logic(app_instance, console_print_func, Filena):
    # Function Description:
    # Applies the current settings from the GUI or a loaded preset to the connected instrument.
    #
    # Inputs:
    # - app_instance: The main application instance, used to access Tkinter variables and retrieve settings.
    # - console_print_func: A function to print messages to the GUI console.
    # - Filena: The filename from which the preset was loaded (currently unused but kept for potential future use).
    #
    # Process:
    # 1. Logs the start of applying settings.
    # 2. Checks if an instrument is connected.
    # 3. Retrieves various settings (frequency, power, trace modes, marker settings etc.) from Tkinter variables.
    # 4. Calls `initialize_instrument` for core settings.
    # 5. Implements conditional logic to send SCPI commands for trace modes and marker calculations
    #    based on the `instrument_model`, specifically for the N9340B.
    # 6. Logs success or failure for each setting application.
    #
    # Outputs:
    # - True if settings are applied successfully, False otherwise.
    #
    # (2025-08-02) Change: Initial implementation.
    # (2025-08-02) Change: Updated debug file name to use `os.path.basename(__file__)`.
    # (2025-08-02) Change: Corrected call to `initialize_instrument` with correct arguments.
    # (2025-08-02) Change: Updated import for `initialize_instrument` from `utils_instrument_initialize`.
    # (2025-08-02) Change: Added logic to apply trace mode and marker calculation settings based on instrument model.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Applying settings to instrument. Let's dial this in! Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    if not app_instance.inst:
        console_print_func("❌ No instrument connected. Cannot apply settings. You gotta connect first, you know!")
        debug_log("No instrument connected to apply settings. This is a goddamn mess!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False

    console_print_func("💬 Applying settings to instrument...")
    try:
        center_freq_hz = float(app_instance.center_freq_hz_var.get())
        span_hz = float(app_instance.span_hz_var.get())
        rbw_hz = float(app_instance.rbw_hz_var.get())
        vbw_hz = float(app_instance.vbw_hz_var.get())
        sweep_time_s = float(app_instance.sweep_time_s_var.get())
        ref_level_dbm = float(app_instance.reference_level_dbm_var.get())
        attenuation_db = int(app_instance.attenuation_var.get())
        freq_shift_hz = float(app_instance.freq_shift_var.get())
        maxhold_enabled = app_instance.maxhold_enabled_var.get()
        high_sensitivity_enabled = app_instance.high_sensitivity_var.get()
        preamp_on = app_instance.preamp_on_var.get()

        # New variables for trace and marker settings
        trace1_mode = app_instance.trace1_mode_var.get() if hasattr(app_instance, 'trace1_mode_var') else None
        trace2_mode = app_instance.trace2_mode_var.get() if hasattr(app_instance, 'trace2_mode_var') else None
        trace3_mode = app_instance.trace3_mode_var.get() if hasattr(app_instance, 'trace3_mode_var') else None
        trace4_mode = app_instance.trace4_mode_var.get() if hasattr(app_instance, 'trace4_mode_var') else None

        marker1_calculate_max = app_instance.marker1_calculate_max_var.get() if hasattr(app_instance, 'marker1_calculate_max_var') else False
        marker2_calculate_max = app_instance.marker2_calculate_max_var.get() if hasattr(app_instance, 'marker2_calculate_max_var') else False
        marker3_calculate_max = app_instance.marker3_calculate_max_var.get() if hasattr(app_instance, 'marker3_calculate_max_var') else False
        marker4_calculate_max = app_instance.marker4_calculate_max_var.get() if hasattr(app_instance, 'marker4_calculate_max_var') else False
        marker5_calculate_max = app_instance.marker5_calculate_max_var.get() if hasattr(app_instance, 'marker5_calculate_max_var') else False
        marker6_calculate_max = app_instance.marker6_calculate_max_var.get() if hasattr(app_instance, 'marker6_calculate_max_var') else False


        # Get the model match from app_instance.instrument_model
        model_match = app_instance.instrument_model.get()

        if initialize_instrument(
            app_instance.inst,
            ref_level_dbm,
            high_sensitivity_enabled,
            preamp_on,
            rbw_hz, # Passing rbw_hz as rbw_config_val
            vbw_hz, # Passing vbw_hz as vbw_config_val
            model_match,
            console_print_func
        ):
            console_print_func("✅ Core settings applied successfully. Boom!")
            debug_log("Core settings applied to instrument. Fucking awesome!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        else:
            console_print_func("❌ Failed to apply core settings. What the hell went wrong?!")
            debug_log("Failed to apply core settings to instrument. This is a disaster!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return False

        # Apply model-specific settings
        if model_match == "N9340B":
            # Apply Trace Modes
            if trace1_mode:
                write_safe(app_instance.inst, f":TRAC1:MODE {trace1_mode}", console_print_func)
                debug_log(f"Applied Trace 1 Mode: {trace1_mode}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
            if trace2_mode:
                write_safe(app_instance.inst, f":TRAC2:MODE {trace2_mode}", console_print_func)
                debug_log(f"Applied Trace 2 Mode: {trace2_mode}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
            if trace3_mode:
                write_safe(app_instance.inst, f":TRAC3:MODE {trace3_mode}", console_print_func)
                debug_log(f"Applied Trace 3 Mode: {trace3_mode}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
            if trace4_mode:
                write_safe(app_instance.inst, f":TRAC4:MODE {trace4_mode}", console_print_func)
                debug_log(f"Applied Trace 4 Mode: {trace4_mode}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)

            # Apply Marker Calculate Max
            if marker1_calculate_max:
                write_safe(app_instance.inst, ":CALCulate:MARKer1:MAX", console_print_func)
                debug_log("Applied Marker 1 Calculate Max.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
            if marker2_calculate_max:
                write_safe(app_instance.inst, ":CALCulate:MARKer2:MAX", console_print_func)
                debug_log("Applied Marker 2 Calculate Max.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
            if marker3_calculate_max:
                write_safe(app_instance.inst, ":CALCulate:MARKer3:MAX", console_print_func)
                debug_log("Applied Marker 3 Calculate Max.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
            if marker4_calculate_max:
                write_safe(app_instance.inst, ":CALCulate:MARKer4:MAX", console_print_func)
                debug_log("Applied Marker 4 Calculate Max.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
            if marker5_calculate_max:
                write_safe(app_instance.inst, ":CALCulate:MARKer5:MAX", console_print_func)
                debug_log("Applied Marker 5 Calculate Max.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
            if marker6_calculate_max:
                write_safe(app_instance.inst, ":CALCulate:MARKer6:MAX", console_print_func)
                debug_log("Applied Marker 6 Calculate Max.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)

            debug_log(f"N9340B specific settings applied for model: {model_match}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)
        else:
            debug_log(f"Skipping N9340B specific settings for instrument model: {model_match}.", file=f"{os.path.basename(__file__)} - {current_version}", version=current_version, function=current_function)

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