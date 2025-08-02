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

current_version = "20250802.1701.7" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 1701 * 7 # Example hash, adjust as needed

import pyvisa
import time
import inspect # Import inspect module
import os # Import os module to fix NameError

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Import read/write safe functions from the new dedicated module
from tabs.Instrument.utils_instrument_read_and_write import write_safe, query_safe


def initialize_instrument(inst, ref_level_dbm, high_sensitivity_on, preamp_on, rbw_config_val, vbw_config_val, model_match, console_print_func=None):
    """
    Function Description:
    Initializes the spectrum analyzer with basic settings such as reference level,
    preamplifier state, high sensitivity mode, and trace configurations.
    This function sets up the instrument for a scan.

    Inputs:
        inst (pyvisa.resources.Resource): The connected VISA instrument object.
        ref_level_dbm (float): The desired reference level in dBm.
        high_sensitivity_on (bool): True to enable high sensitivity mode, False otherwise.
        preamp_on (bool): True to turn the preamplifier ON, False otherwise.
        rbw_config_val (float): The Resolution Bandwidth (RBW) value to configure on the instrument in Hz.
                                 (Note: This parameter is currently not directly used for setting RBW in this function
                                 but is passed for consistency with the GUI's intent. RBW for scanning is set in `scan_bands`.)
        vbw_config_val (float): The Video Bandwidth (VBW) value to configure on the instrument in Hz.
                                 (Note: This parameter is currently not directly used for setting VBW in this function
                                 but is passed for consistency with the GUI's intent. VBW for scanning is set in `scan_bands`.)
        model_match (str): The detected model of the instrument (e.g., "N9340B", "N9342CN").
                            Used for model-specific SCPI commands.
        console_print_func (function, optional): Function to use for console output.
                                               Defaults to console_log if None.
    Process:
        1. **Reset**: Sends `*RST` to reset the instrument to a known state, then waits for operation completion.
        2. **Reference Level**: Sets the display reference level.
        3. **Preamplifier/High Sensitivity**: Configures the preamplifier and high sensitivity mode based on `preamp_on`
           and `high_sensitivity_on` flags. This involves setting attenuation and gain.
        4. **Trace Modes**: Configures Trace 1 to 'WRITe', Trace 2 to 'MAXHold', and Trace 3 to 'MINHold'.
        5. **Display Scale**: Sets the Y-axis display scale to 'LOGarithmic'.
        6. **Sweep Time**: Sets sweep time to 'AUTO'.
        7. **Data Format**: Sets the trace data format to 'ASCII' for data transfer, with a model-specific command.
        8. Prints status messages for each configuration step.
        9. Handles `pyvisa.errors.VisaIOError` and general `Exception`.
    Outputs:
        bool: True if initialization is successful; False on failure.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    console_print_func("✨ Initializing instrument with desired settings. Getting ready for action!")
    debug_log("Initializing instrument with desired settings... Let's make this machine sing!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    try:
        # Reset the instrument to a known state using *RST first
        if not write_safe(inst, "*RST", console_print_func):
            debug_log("Failed to send *RST. This is a bad start!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return False
        time.sleep(0.5) # Small delay after reset to allow instrument to process
        if not query_safe(inst, "*OPC?", console_print_func):
            debug_log("Failed to query *OPC? after *RST (timeout likely). Instrument not responding!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return False # Wait for operation to complete
        time.sleep(1) # Give it a moment after reset and OPC


        # Set preamplifier
        if preamp_on:
            if not write_safe(inst, ":POWer:ATTenuation:AUTO ON", console_print_func):
                debug_log("Failed to set :POWer:ATTenuation:AUTO ON. Preamplifier issue!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                return False
            if not write_safe(inst, ":POWer:GAIN ON", console_print_func):
                debug_log("Failed to set :POWer:GAIN ON. Preamplifier gain problem!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                return False
            console_print_func("✅ Preamplifier ON. Boosting the signal!")
            debug_log("Preamplifier ON. Powering up!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            # Note: The original code re-set RLEVel here, preserving that behavior
            if not write_safe(inst, f":DISPlay:WINDow:TRACe:Y:RLEVel {ref_level_dbm}", console_print_func):
                debug_log(f"Failed to re-set reference level to {ref_level_dbm} dBm after preamp config. What a mess!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                return False
            console_print_func(f"✅ Set reference level to {ref_level_dbm} dBm. Perfect!")
            debug_log(f"Re-set reference level to {ref_level_dbm} dBm after preamp config. Level adjusted!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        else:
            if not write_safe(inst, ":POWer:GAIN OFF", console_print_func):
                debug_log("Failed to set :POWer:GAIN OFF. Preamplifier won't turn off!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                return False
            console_print_func("✅ Preamplifier OFF. Keeping it clean.")
            debug_log("Preamplifier OFF. Done!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

        # Set high sensitivity (preamplifier)
        if high_sensitivity_on:
            # Apply :POWer:HSENsitive ON only for N9342CN
            if model_match == "N9342CN":
                if not write_safe(inst, f":DISPlay:WINDow:TRACe:Y:RLEVel -50", console_print_func):
                    debug_log("Failed to set reference level to -50 dBm for high sensitivity (N9342CN). This is a disaster!",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                    return False
                if not write_safe(inst, ":POWer:ATTenuation 0", console_print_func):
                    debug_log("Failed to set :POWer:ATTenuation 0 (N9342CN). Attenuation problem!",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                    return False
                if not write_safe(inst, ":POWer:GAIN 1", console_print_func):
                    debug_log("Failed to set :POWer:GAIN 1 (N9342CN). Gain issue!",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                    return False
                if not write_safe(inst, ":POWer:HSENsitive ON", console_print_func):
                    debug_log("Failed to set :POWer:HSENsitive ON (N9342CN). High sensitivity won't activate!",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                    return False
                console_print_func("✅ High sensitivity turned ON for N9342CN. Detecting weak signals!")
                debug_log("High sensitivity turned ON for N9342CN. Activated!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            else:
                console_print_func(f"ℹ️ High Sensitivity (HSENsitive) command skipped for model {model_match}. It's specific to N9342CN. No worries!")
                debug_log(f"High Sensitivity (HSENsitive) command skipped for model {model_match}. It's specific to N9342CN. Not applicable!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
        else:
            # Apply :POWer:HSENsitive OFF only for N9342CN
            if model_match == "N9342CN":
                if not write_safe(inst, ":POWer:HSENsitive OFF", console_print_func):
                    debug_log("Failed to set :POWer:HSENsitive OFF (N9342CN). High sensitivity won't deactivate!",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                    return False
                if not write_safe(inst, ":POWer:ATTenuation 10", console_print_func):
                    debug_log("Failed to set :POWer:ATTenuation 10 (N9342CN). Attenuation problem!",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                    return False
                # Note: The original code re-set RLEVel here, preserving that behavior
                if not write_safe(inst, f":DISPlay:WINDow:TRACe:Y:RLEVel {ref_level_dbm}", console_print_func):
                    debug_log(f"Failed to re-set reference level to {ref_level_dbm} dBm after high sensitivity config (N9342CN). What a mess!",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                    return False
                console_print_func(f"✅ Set reference level to {ref_level_dbm} dBm.")
                console_print_func("✅ High sensitivity turned OFF for N9342CN. Back to normal!")
                debug_log("High sensitivity turned OFF for N9342CN. Deactivated!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            else:
                console_print_func(f"ℹ️ High Sensitivity (HSENsitive) command skipped for model {model_match}. It's specific to N9342CN. No worries!")
                debug_log(f"High Sensitivity (HSENsitive) command skipped for model {model_match}. It's specific to N9342CN. Not applicable!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)

        # Configure Trace Modes (These are now handled by set_span_logic when called from GUI)
        # The initial setup of trace modes here should reflect a default state,
        # which is usually Live (WRITe).
        if not write_safe(inst, ":TRAC1:MODE WRITe", console_print_func):
            debug_log("Failed to set :TRAC1:MODE WRITe. Trace 1 issue!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return False
        console_print_func(f"✅ Trace 1 set to write. Live data incoming!")
        debug_log("Trace 1 set to WRITE. Ready for live display!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Ensure other traces are blanked on initialization
        if not write_safe(inst, ":TRAC2:MODE BLANK", console_print_func):
            debug_log("Failed to set :TRAC2:MODE BLANK. Trace 2 issue!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return False
        console_print_func(f"✅ Trace 2 set to BLANK. Cleared!")
        debug_log("Trace 2 set to BLANK. Wiped clean!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        if not write_safe(inst, ":TRAC3:MODE BLANK", console_print_func):
            debug_log("Failed to set :TRAC3:MODE BLANK. Trace 3 issue!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return False
        console_print_func(f"✅ Trace 3 set to BLANK. Cleared!")
        debug_log("Trace 3 set to BLANK. Wiped clean!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Display scale is always LOGarithmic
        if not write_safe(inst, ":DISPlay:WINDow:TRACe:Y:SCALe:SPACing LOGarithmic", console_print_func):
            debug_log("Failed to set :DISPlay:WINDow:TRACe:Y:SCALe:SPACing LOGarithmic. Display scale problem!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return False
        console_print_func("✅ Display scale set to LOGarithmic (always). Visuals optimized!")
        debug_log("Display scale set to LOGarithmic. Perfect display!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Set VBW and Sweep Time to AUTO
        if not write_safe(inst, ":SENSe:BANDwidth:VIDeo:AUTO ON", console_print_func):
            debug_log("Failed to set :SENSe:BANDwidth:VIDeo:AUTO ON. VBW auto failed!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return False
        if not write_safe(inst, ":SENSe:SWEep:TIME:AUTO ON", console_print_func):
            debug_log("Failed to set :SENSe:SWEep:TIME:AUTO ON. Sweep time auto failed!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return False
        console_print_func("✅ VBW and Sweep time set to AUTO. Efficiency engaged!")
        debug_log("VBW and Sweep time set to AUTO. Automated!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Set trace data format based on model
        if model_match == "N9342CN":
            if not write_safe(inst, ":TRACe:FORMat:DATA ASCii", console_print_func):
                debug_log("Failed to set :TRACe:FORMat:DATA ASCii for N9342CN. Data format problem!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                return False
            console_print_func("✅ Set trace data format to ASCII for N9342CN. Data ready!")
            debug_log("Trace data format set to ASCII for N9342CN. Formatted!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        elif model_match == "N9340B":
            # Corrected command for N9340B
            if not write_safe(inst, ":TRACe:FORMat ASCii", console_print_func):
                debug_log("Failed to set :TRACe:FORMat ASCii for N9340B. Data format problem!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                return False
            console_print_func("✅ Set trace data format to ASCII for N9340B. Data ready!")
            debug_log("Trace data format set to ASCII for N9340B. Formatted!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        else:
            console_print_func(f"ℹ️ Trace data format command skipped for model {model_match}. No specific command defined. Moving on!")
            debug_log(f"Trace data format command skipped for model {model_match}. It's specific to N9342CN. Not applicable!",
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
