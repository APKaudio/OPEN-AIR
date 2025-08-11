# tabs/Instrument/utils_yak_visa.py
#
# This file provides utility functions for safe and standardized execution of
# VISA commands (GET, SET, DO) on connected instruments. It wraps PyVISA operations
# with error handling and integrates with the application's debug logging.
# This version has been updated to handle 'GET' commands where the '?' terminator
# is provided as a variable, and now returns a response value to the caller.
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
# Version 20250811.154005.0 (REFACTORED: Implemented *OPC? check for SET commands to verify completion and handle timeouts, aligning with the DO command logic.)

current_version = "20250811.154005.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250811 * 154005 * 0 # Example hash, adjust as needed

import inspect
import pyvisa
import time

# Updated imports for new logging functions
from display.debug_logic import debug_log, log_visa_command
from display.console_logic import console_log

# Helper functions for instrument communication, using the new logging
def write_safe(inst, command, console_print_func):
    # Function Description:
    # Safely writes a SCPI command to the instrument.
    # Logs the command and handles potential errors.
    #
    # Inputs to this function:
    # - inst (pyvisa.resources.Resource): The PyVISA instrument object.
    # - command (str): The SCPI command string to write.
    # - console_print_func (function): Function to print messages to the GUI console.
    #
    # Process of this function:
    # 1. Checks if the instrument is connected.
    # 2. Attempts to write the command.
    # 3. Logs success or failure to the console and debug log.
    #
    # Outputs of this function:
    # - bool: True if the command was written successfully, False otherwise.
    #
    # (2025-08-01) Change: Refactored to use new logging.
    # (2025-08-11) Change: No changes.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to write command: {command}",
                file=__file__,
                version=current_version,
                function=current_function)
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot write command.")
        debug_log("Instrument not connected. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False
    try:
        inst.write(command)
        log_visa_command(command, "SENT") # Log the VISA command
        return True
    except Exception as e:
        console_print_func(f"❌ Error writing command '{command}': {e}")
        debug_log(f"Error writing command '{command}': {e}. This thing is a pain in the ass!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False

def query_safe(inst, command, console_print_func):
    # Function Description:
    # Safely queries the instrument with a SCPI command and returns the response.
    # Logs the command and response, and handles potential errors.
    #
    # Inputs to this function:
    # - inst (pyvisa.resources.Resource): The PyVISA instrument object.
    # - command (str): The full SCPI command string to query.
    # - console_print_func (function): Function to print messages to the GUI console.
    #
    # Process of this function:
    # 1. Checks if the instrument is connected.
    # 2. Attempts to query the instrument.
    # 3. Logs the command, response, and handles errors.
    #
    # Outputs of this function:
    # - str or None: The instrument's response if successful, None otherwise.
    #
    # (2025-08-01) Change: Refactored to use new logging.
    # (2025-08-11) Change: No changes.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to query command: {command}",
                file=__file__,
                version=current_version,
                function=current_function)
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot query command.")
        debug_log("Instrument not connected. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return None
    try:
        response = inst.query(command).strip()
        log_visa_command(command, "SENT") # Log the VISA command
        log_visa_command(response, "RECEIVED") # Log the VISA response
        return response
    except Exception as e:
        console_print_func(f"❌ Error querying command '{command}': {e}")
        debug_log(f"Error querying command '{command}': {e}. This goddamn thing is broken!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return None

def set_safe(inst, command, value, console_print_func):
    """
    Function Description:
    Safely writes a SET command to the instrument with a specified value.

    Inputs to this function:
    - inst: The PyVISA instrument instance.
    - command (str): The base VISA command string (e.g., ":SENSe:FREQuency:CENTer").
    - value: The value to set (will be converted to string).
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Constructs the full command string.
    2. Calls write_safe to send the command.

    Outputs of this function:
    - bool: True if the command was written successfully, False otherwise.
    """
    current_function = inspect.currentframe().f_code.co_name
    full_command = f"{command} {value}"
    debug_log(f"Attempting to SET: {full_command}",
                file=__file__,
                version=current_version,
                function=current_function)
    return write_safe(inst, full_command, console_print_func)

def _wait_for_opc(inst, console_print_func, timeout=5):
    """
    Function Description:
    Waits for the instrument's Operation Complete (OPC) flag by querying *OPC?.
    This is a blocking function that handles timeouts.

    Inputs to this function:
    - inst: The PyVISA instrument instance.
    - console_print_func: The function to print messages to the GUI console.
    - timeout (int): The maximum time to wait for a response in seconds.

    Outputs of this function:
    - str: "PASSED" if the operation completes, "TIME FAILED" on timeout,
      or "FAILED" for other errors.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Waiting for Operation Complete (*OPC?) with a timeout of {timeout} seconds. Let's see if this thing is done!",
                file=__file__,
                version=current_version,
                function=current_function)

    original_timeout = inst.timeout
    inst.timeout = timeout * 1000 # PyVISA timeout is in milliseconds

    try:
        response = inst.query("*OPC?").strip()
        inst.timeout = original_timeout # Restore original timeout
        log_visa_command("*OPC?", "SENT")
        log_visa_command(response, "RECEIVED")

        if response == "1":
            console_print_func("✅ Operation Complete. Fucking brilliant!")
            return "PASSED"
        else:
            console_print_func("❌ Operation failed to complete or returned an unexpected value.")
            debug_log(f"OPC query returned '{response}', not '1'. What the hell?!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return "FAILED"

    except pyvisa.errors.VisaIOError as e:
        inst.timeout = original_timeout # Restore original timeout
        console_print_func(f"❌ Operation Complete query timed out after {timeout} seconds.")
        debug_log(f"OPC query failed with a timeout: {e}. This thing is a stubborn bastard!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return "TIME FAILED"
    except Exception as e:
        inst.timeout = original_timeout # Restore original timeout
        console_print_func(f"❌ Error during Operation Complete query: {e}")
        debug_log(f"Error during OPC query: {e}. This bugger is being problematic!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return "FAILED"


def execute_visa_command(inst, action_type, visa_command, variable_value, console_print_func):
    """
    Function Description:
    Executes a given VISA command based on its action type and variable value.
    This function has been updated to handle a 'GET' action where the '?' is
    passed in the `variable_value` parameter. It also returns the command's
    response or a boolean indicating success/failure.

    Inputs to this function:
    - inst: The PyVISA instrument instance.
    - action_type (str): The type of action ("GET", "SET", "DO").
    - visa_command (str): The base VISA command string.
    - variable_value (str): The variable value to append for "SET" commands,
      or the "?" terminator for "GET" commands.
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Checks for a connected instrument.
    2. Constructs the full command based on `action_type`.
    3. Calls the appropriate helper function (`query_safe`, `set_safe`, `write_safe`).
    4. Logs the result and returns the response or a boolean.

    Outputs of this function:
    - str or None: The instrument's response if the action was a successful "GET".
    - str: "PASSED", "TIME FAILED", or "FAILED" for a "DO" command.
    - str: "PASSED", "TIME FAILED", or "FAILED" for a "SET" command.
    """
    current_function = inspect.currentframe().f_code.co_name

    if not inst:
        console_print_func("❌ No instrument connected. Cannot execute VISA command.")
        debug_log("No instrument connected for execute_visa_command. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False

    try:
        if action_type == "GET":
            full_command = f"{visa_command}{variable_value}" if variable_value.startswith("?") else visa_command
            response = query_safe(inst, full_command, console_print_func)
            if response is not None:
                console_print_func(f"✅ Response: {response}")
                debug_log(f"Query response: {response}. Fucking finally!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                return response
            else:
                console_print_func("❌ No response received or query failed.")
                debug_log("Query failed or no response. What the hell happened?!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                return None
        elif action_type == "SET":
            if set_safe(inst, visa_command, variable_value, console_print_func):
                return _wait_for_opc(inst, console_print_func)
            else:
                console_print_func("❌ Command execution failed.")
                debug_log("SET command execution failed. This bugger is being problematic!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                return "FAILED"
        elif action_type == "DO":
            if write_safe(inst, visa_command, console_print_func):
                return _wait_for_opc(inst, console_print_func)
            else:
                console_print_func("❌ Command execution failed.")
                debug_log("DO command execution failed. What the hell went wrong?!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                return "FAILED"
        else:
            console_print_func(f"⚠️ Unknown action type '{action_type}'. Cannot execute command.")
            debug_log(f"Unknown action type '{action_type}' for command: {visa_command}. This is a goddamn mess!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return False
    except Exception as e:
        console_print_func(f"❌ Error during VISA command execution: {e}")
        debug_log(f"Error executing VISA command '{visa_command}': {e}. This thing is a pain in the ass!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False