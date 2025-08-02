# tabs/Instrument/utils_instrument_control.py
#
# This module provides low-level functions for communicating with the spectrum analyzer
# via PyVISA. It includes functions for safely writing commands, querying data,
# connecting/disconnecting, initializing instrument settings, and managing device presets.
# This module is designed to abstract the direct VISA communication details from the
# higher-level application logic.
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
# Version 20250802.1052.1 (Added debug to list_visa_resources to show passed arguments.)

current_version = "20250802.1052.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 1052 * 1 # Example hash, adjust as needed

import pyvisa
import time
import inspect # Import inspect module
import os # Import os module to fix NameError
from datetime import datetime # Import datetime for timestamp

# Updated imports for new logging functions
from src.debug_logic import debug_log, log_visa_command # Ensure log_visa_command is imported
from src.console_logic import console_log

# Global variable for debug mode, controlled by GUI checkbox (These are now managed by src.debug_logic directly)
# DEBUG_MODE = False
# LOG_VISA_COMMANDS = False # New global variable for VISA command logging

def list_visa_resources(console_print_func=None, *args, **kwargs):
    """
    Function Description:
    Lists available VISA resources (instruments).

    Inputs to this function:
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.
    - *args: Catches any unexpected positional arguments.
    - **kwargs: Catches any unexpected keyword arguments.

    Process of this function:
    1. Initializes PyVISA ResourceManager.
    2. Logs any unexpected arguments received.
    3. Lists available resources.
    4. Logs the discovered resources or any errors.

    Outputs of this function:
    - list: A list of strings, where each string is a VISA resource name.
            Returns an empty list if no resources are found or an error occurs.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Listing VISA resources... Let's find some devices!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    # (2025-08-02 10:52) Change: Added debug to show unexpected arguments.
    if args or kwargs:
        debug_log(f"WARNING: list_visa_resources received unexpected arguments! Args: {args}, Kwargs: {kwargs}. What the hell are these?!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        console_print_func(f"⚠️ Warning: list_visa_resources received unexpected arguments! This might be the source of the problem. Check the call!")

    try:
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        debug_log(f"Found VISA resources: {resources}. Success!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return list(resources)
    except Exception as e:
        error_msg = f"❌ Error listing VISA resources: {e}. This is a disaster!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return []


def connect_to_instrument(resource_name, console_print_func=None):
    """
    Function Description:
    Establishes a connection to a VISA instrument.

    Inputs to this function:
    - resource_name (str): The VISA resource string (e.g., "GPIB0::1::INSTR").
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Initializes PyVISA ResourceManager.
    2. Opens the specified resource.
    3. Sets instrument timeout, read/write termination characters, and query delay.
    4. Logs connection status.

    Outputs of this function:
    - pyvisa.resources.Resource or None: The connected PyVISA instrument object if successful,
                                         None otherwise.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Connecting to instrument: {resource_name}. Fingers crossed!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    try:
        rm = pyvisa.ResourceManager()
        inst = rm.open_resource(resource_name)
        inst.timeout = 10000 # Set a timeout (milliseconds) - Increased for robustness
        inst.read_termination = '\n' # Set read termination character
        inst.write_termination = '\n' # Set write termination character
        inst.query_delay = 0.1 # Small delay between write and read for query
        console_print_func(f"✅ Successfully connected to {resource_name}. It's alive!")
        debug_log(f"Connection successful to {resource_name}. We're in!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return inst
    except pyvisa.errors.VisaIOError as e:
        error_msg = f"❌ VISA error connecting to {resource_name}: {e}. This is a nightmare!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return None
    except Exception as e:
        error_msg = f"❌ An unexpected error occurred while connecting to {resource_name}: {e}. What a mess!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return None


def disconnect_instrument(inst, console_print_func=None):
    """
    Function Description:
    Closes the connection to a VISA instrument.

    Inputs to this function:
    - inst (pyvisa.resources.Resource): The PyVISA instrument object to disconnect.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Checks if the instrument object is valid.
    2. Attempts to close the instrument connection.
    3. Logs disconnection status.

    Outputs of this function:
    - bool: True if disconnection is successful, False otherwise.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Disconnecting instrument... Saying goodbye!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    if inst:
        try:
            inst.close()
            console_print_func("✅ Instrument disconnected. See ya!")
            debug_log("Instrument connection closed. All done!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return True
        except pyvisa.errors.VisaIOError as e:
            error_msg = f"❌ VISA error disconnecting instrument: {e}. This thing is stuck!"
            console_print_func(error_msg)
            debug_log(error_msg,
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return False
        except Exception as e:
            error_msg = f"❌ An unexpected error occurred while disconnecting instrument: {e}. What a pain!"
            console_print_func(error_msg)
            debug_log(error_msg,
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return False
    debug_log("No instrument to disconnect. Already gone!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    return False


def write_safe(inst, command, console_print_func=None):
    """
    Function Description:
    Safely writes a command to the instrument.

    Inputs to this function:
    - inst (pyvisa.resources.Resource): The PyVISA instrument object.
    - command (str): The SCPI command string to write.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Checks if the instrument is connected.
    2. Logs the command using `log_visa_command`.
    3. Attempts to write the command to the instrument.
    4. Handles and logs any VISA or general exceptions.

    Outputs of this function:
    - bool: True if the command was written successfully, False otherwise.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    if not inst:
        debug_log(f"Not connected to instrument, cannot write command: {command}. Fucking useless!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        console_print_func(f"⚠️ Warning: Not connected. Failed to write: {command}. Connect the damn thing first!")
        return False
    try:
        log_visa_command(command, "SENT") # Use the imported log_visa_command
        inst.write(command)
        return True
    except pyvisa.errors.VisaIOError as e:
        error_msg = f"🛑 VISA error sending command '{command.strip()}': {e}. This is a nightmare!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False
    except Exception as e:
        error_msg = f"❌ An unexpected error occurred while sending command '{command.strip()}': {e}. What a mess!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False


def query_safe(inst, command, console_print_func=None):
    """
    Function Description:
    Safely queries the instrument and returns the response.
    Returns an empty string if an error occurs or no response, to prevent NoneType errors.

    Inputs to this function:
    - inst (pyvisa.resources.Resource): The PyVISA instrument object.
    - command (str): The SCPI query command string.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Checks if the instrument is connected.
    2. Logs the command using `log_visa_command`.
    3. Attempts to query the instrument and retrieve the response.
    4. Logs the response using `log_visa_command`.
    5. Handles and logs any VISA or general exceptions.

    Outputs of this function:
    - str: The instrument's response (stripped of whitespace) if successful,
           an empty string otherwise.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    if not inst:
        debug_log(f"Not connected to instrument, cannot query command: {command}. Fucking useless!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        console_print_func(f"⚠️ Warning: Not connected. Failed to query: {command}. Connect the damn thing first!")
        return "" # Return empty string on error if not connected
    try:
        log_visa_command(command, "SENT") # Use the imported log_visa_command
        response = inst.query(command).strip()
        log_visa_command(response, "RECEIVED") # Use the imported log_visa_command
        debug_log(f"Query '{command.strip()}' response: {response}. Got it!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return response
    except pyvisa.errors.VisaIOError as e:
        error_msg = f"🛑 VISA error querying '{command.strip()}': {e}. This goddamn thing is broken!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return "" # Return empty string on error
    except Exception as e:
        error_msg = f"❌ An unexpected error occurred while querying '{command.strip()}': {e}. What a pain!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return "" # Return empty string on error


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
            debug_log(f"Trace data format command skipped for model {model_match}. No specific command defined. Not applicable!",
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


def query_current_instrument_settings(inst, MHZ_TO_HZ_CONVERSION, console_print_func=None):
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
