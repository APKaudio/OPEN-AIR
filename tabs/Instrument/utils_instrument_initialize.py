# tabs/Instrument/utils_instrument_initialize.py
#
# This module provides a low-level function for initializing a spectrum analyzer
# with basic settings. It handles resetting the instrument, configuring reference
# level, preamplifier, high sensitivity mode, trace modes, display scale,
# sweep time, and data format.
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
# Version 20250802.1701.7 (Refactored from utils_instrument_control.py to handle instrument initialization logic.)
# Version 20250803.1705.1 (Ensured initialize_instrument_logic is correctly defined and exposed.)

current_version = "20250803.1705.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 1705 * 1 # Example hash, adjust as needed

import pyvisa
import time
import inspect # Import inspect module
import os # Import os module to fix NameError

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Import read/write safe functions from the new dedicated module
from tabs.Instrument.utils_instrument_read_and_write import write_safe, query_safe

def initialize_instrument_logic(inst, ref_level_dbm, high_sensitivity_on, preamp_on, rbw_hz, vbw_hz, instrument_model, console_print_func):
    """
    Function Description:
    Initializes the connected spectrum analyzer with a set of basic, common settings.
    This function performs a reset, configures reference level, preamplifier,
    high sensitivity mode (for N9342CN), trace modes, display scale, sweep time,
    and data format.

    Inputs:
        inst (pyvisa.resources.Resource): The connected VISA instrument object.
        ref_level_dbm (float): The desired reference level in dBm.
        high_sensitivity_on (bool): True to enable high sensitivity mode, False otherwise.
        preamp_on (bool): True to enable the preamplifier, False otherwise.
        rbw_hz (float): The desired Resolution Bandwidth in Hz.
        vbw_hz (float): The desired Video Bandwidth in Hz.
        instrument_model (str): The model string of the connected instrument (e.g., "N9342CN").
        console_print_func (function): Function to print messages to the GUI console.

    Process:
        1. Checks for instrument connection.
        2. Resets the instrument to its default state.
        3. Configures various instrument settings using SCPI commands.
        4. Handles model-specific commands (e.g., high sensitivity for N9342CN).
        5. Logs actions and errors to the console and debug file.

    Outputs:
        bool: True if initialization is successful, False otherwise.
    """
    console_print_func = console_print_func if console_print_func else console_log
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to initialize instrument. Version: {current_version}. Let's get this instrument ready!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    if not inst:
        console_print_func("🛑 Instrument not connected. Cannot initialize. Connect the damn thing first!")
        debug_log("Instrument not connected. Initialization aborted!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False

    try:
        # Reset instrument
        if not write_safe(inst, "*RST", console_print_func):
            return False
        console_print_func("✅ Instrument reset to default settings.")
        time.sleep(1) # Give instrument time to reset

        # Set Reference Level
        if not write_safe(inst, f":DISPlay:WINDow:TRACe:Y:RLEVel {ref_level_dbm}", console_print_func):
            return False
        console_print_func(f"✅ Reference Level set to {ref_level_dbm} dBm.")

        # Set Preamplifier
        preamp_cmd = "ON" if preamp_on else "OFF"
        if not write_safe(inst, f":POWer:GAIN {preamp_cmd}", console_print_func):
            return False
        console_print_func(f"✅ Preamplifier set to {preamp_cmd}.")

        # Set High Sensitivity Mode (for N9342CN only)
        if instrument_model == "N9342CN":
            high_sensitivity_cmd = "ON" if high_sensitivity_on else "OFF"
            if not write_safe(inst, f":POWer:HSENsitive {high_sensitivity_cmd}", console_print_func):
                return False
            console_print_func(f"✅ High Sensitivity Mode set to {high_sensitivity_cmd} for N9342CN.")
        else:
            debug_log(f"High Sensitivity Mode not applicable to {instrument_model}. Not applicable!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)

        console_print_func("🎉 Instrument initialized successfully with desired settings. All systems go!")
        debug_log("Instrument initialized successfully. Ready for operation!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return True
    except pyvisa.errors.VisaIOError as e:
        console_print_func(f"🛑 Failed to initialize instrument with desired settings: {e}. This is a critical error!")
        debug_log(f"VISA Error during instrument initialization: {e}. What a nightmare!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred during instrument initialization: {e}. This is a disaster!")
        debug_log(f"Unexpected error during instrument initialization: {e}. Fucking hell!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False
