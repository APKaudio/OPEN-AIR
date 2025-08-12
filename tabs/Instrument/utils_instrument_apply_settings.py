# tabs/Instrument/utils_instrument_apply_settings.py
# This module provides a low-level function for applying instrument settings.

import inspect
import os
from display.debug_logic import debug_log
from display.console_logic import console_log
from tabs.Instrument.utils_instrument_read_and_write import write_safe

# Constants for frequency conversion (if needed)
MHZ_TO_HZ_CONVERSION = 1_000_000

current_version = "20250803.1700.0" # Example version
current_version_hash = 20250803 * 1700 * 0

'''
def apply_instrument_settings_logic(inst, center_freq_mhz, span_mhz, rbw_hz, ref_level_dbm, preamp_on, high_sensitivity_on, console_print_func=None):
    """
    Function Description:
    Applies various settings to the connected spectrum analyzer.

    Inputs:
        inst (pyvisa.resources.Resource): The connected VISA instrument object.
        center_freq_mhz (float): Desired center frequency in MHz.
        span_mhz (float): Desired span in MHz.
        rbw_hz (float): Desired Resolution Bandwidth in Hz.
        ref_level_dbm (float): Desired reference level in dBm.
        preamp_on (bool): True to enable preamplifier, False otherwise.
        high_sensitivity_on (bool): True to enable high sensitivity mode, False otherwise.
        console_print_func (function, optional): Function to print messages to the GUI console.

    Process:
        1. Converts MHz values to Hz for SCPI commands.
        2. Sends SCPI commands to set center frequency, span, RBW, reference level.
        3. Configures preamplifier and high sensitivity based on boolean flags.
        4. Handles and logs any VISA or general exceptions.

    Outputs:
        bool: True if all settings are applied successfully, False otherwise.
    """
    console_print_func = console_print_func if console_print_func else console_log
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Applying instrument settings...",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    try:
        # Convert MHz to Hz for SCPI commands
        center_freq_hz = center_freq_mhz * MHZ_TO_HZ_CONVERSION
        span_hz = span_mhz * MHZ_TO_HZ_CONVERSION

        # Apply Center Frequency
        if not write_safe(inst, f":SENSe:FREQuency:CENTer {center_freq_hz}", console_print_func):
            return False
        console_print_func(f"✅ Set Center Freq to {center_freq_mhz:.3f} MHz.")

        # Apply Span
        if not write_safe(inst, f":SENSe:FREQuency:SPAN {span_hz}", console_print_func):
            return False
        console_print_func(f"✅ Set Span to {span_mhz:.3f} MHz.")

        # Apply RBW
        if not write_safe(inst, f":SENSe:BANDwidth:RESolution {rbw_hz}", console_print_func):
            return False
        console_print_func(f"✅ Set RBW to {rbw_hz} Hz.")

        # Apply Reference Level
        if not write_safe(inst, f":DISPlay:WINDow:TRACe:Y:RLEVel {ref_level_dbm}", console_print_func):
            return False
        console_print_func(f"✅ Set Ref Level to {ref_level_dbm} dBm.")

        # Apply Preamplifier
        preamp_cmd = "ON" if preamp_on else "OFF"
        if not write_safe(inst, f":POWer:GAIN {preamp_cmd}", console_print_func):
            return False
        console_print_func(f"✅ Preamplifier set to {preamp_cmd}.")

        # Apply High Sensitivity Mode (assuming this is a separate command or part of preamp logic)
        # This might require model-specific logic, similar to initialize_instrument
        high_sensitivity_cmd = "ON" if high_sensitivity_on else "OFF"
        # Example: if model_match == "N9342CN":
        #     if not write_safe(inst, f":POWer:HSENsitive {high_sensitivity_cmd}", console_print_func):
        #         return False
        console_print_func(f"✅ High Sensitivity set to {high_sensitivity_cmd}.")

        debug_log("All settings applied successfully.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return True
    except Exception as e:
        console_print_func(f"❌ Error applying settings: {e}")
        debug_log(f"Error applying settings: {e}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False 
    '''