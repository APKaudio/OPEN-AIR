# # tabs/Instrument/utils_yak_visa.py
#
# This file provides utility functions for safe and standardized execution of
# VISA commands (GET, SET, DO) on connected instruments. It wraps PyVISA operations
# with error handling and integrates with the application's debug logging.
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
# Version 20250801.2220.1 (Refactored debug_print, query_safe, write_safe to use new logging.)

current_version = "20250801.2220.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250801 * 2220 * 1 # Example hash, adjust as needed

import inspect
# Updated imports for new logging functions
from display.debug_logic import debug_log, log_visa_command
from display.console_logic import console_log

# Helper functions for instrument communication, using the new logging
def write_safe(inst, command, console_print_func):
    """
    Function Description:
    Safely writes a SCPI command to the instrument.
    Logs the command and handles potential errors.

    Inputs to this function:
    - inst (pyvisa.resources.Resource): The PyVISA instrument object.
    - command (str): The SCPI command string to write.
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Checks if the instrument is connected.
    2. Attempts to write the command.
    3. Logs success or failure to the console and debug log.

    Outputs of this function:
    - bool: True if the command was written successfully, False otherwise.

    (2025-08-01) Change: Refactored to use new logging.
    """
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
    """
    Function Description:
    Safely queries the instrument with a SCPI command and returns the response.
    Logs the command and response, and handles potential errors.

    Inputs to this function:
    - inst (pyvisa.resources.Resource): The PyVISA instrument object.
    - command (str): The SCPI query command string.
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Checks if the instrument is connected.
    2. Attempts to query the instrument.
    3. Logs the command, response, and handles errors.

    Outputs of this function:
    - str or None: The instrument's response if successful, None otherwise.

    (2025-08-01) Change: Refactored to use new logging.
    """
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
    Safely writes a SET command to the instrument with a specified value.

    Args:
        inst: The PyVISA instrument instance.
        command (str): The base VISA command string (e.g., ":SENSe:FREQuency:CENTer").
        value: The value to set (will be converted to string).
        console_print_func (function): Function to print messages to the GUI console.

    Returns:
        bool: True if the command was written successfully, False otherwise.
    """
    current_function = inspect.currentframe().f_code.co_name
    full_command = f"{command} {value}"
    debug_log(f"Attempting to SET: {full_command}",
                file=__file__,
                version=current_version,
                function=current_function)
    return write_safe(inst, full_command, console_print_func)

def execute_visa_command(inst, action_type, visa_command, variable_value, console_print_func):
    """
    Executes a given VISA command based on its action type and variable value.

    Args:
        inst: The PyVISA instrument instance.
        action_type (str): The type of action ("GET", "SET", "DO").
        visa_command (str): The base VISA command string.
        variable_value (str): The variable value to append for "SET" commands.
        console_print_func (function): Function to print messages to the GUI console.
    """
    current_function = inspect.currentframe().f_code.co_name

    if not inst:
        console_print_func("❌ No instrument connected. Cannot execute VISA command.")
        debug_log("No instrument connected for execute_visa_command. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return

    console_print_func(f"Attempting to perform {action_type} action for: {visa_command}")
    debug_log(f"Action: {action_type}, Command: {visa_command}, Variable: '{variable_value}'",
                file=__file__,
                version=current_version,
                function=current_function)

    try:
        if action_type == "GET":
            response = query_safe(inst, visa_command, console_print_func)
            if response is not None:
                console_print_func(f"✅ Response: {response}")
                debug_log(f"Query response: {response}. Fucking finally!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            else:
                console_print_func("❌ No response received or query failed.")
                debug_log("Query failed or no response. What the hell happened?!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        elif action_type == "SET":
            if set_safe(inst, visa_command, variable_value, console_print_func):
                console_print_func("✅ Command executed successfully.")
                debug_log("SET command executed successfully. Fucking brilliant!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            else:
                console_print_func("❌ Command execution failed.")
                debug_log("SET command execution failed. This bugger is being problematic!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        elif action_type == "DO":
            if write_safe(inst, visa_command, console_print_func):
                console_print_func("✅ Command executed successfully.")
                debug_log("DO command executed successfully. Fucking awesome!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            else:
                console_print_func("❌ Command execution failed.")
                debug_log("DO command execution failed. What the hell went wrong?!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        else:
            console_print_func(f"⚠️ Unknown action type '{action_type}'. Cannot execute command.")
            debug_log(f"Unknown action type '{action_type}' for command: {visa_command}. This is a goddamn mess!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
    except Exception as e:
        console_print_func(f"❌ Error during VISA command execution: {e}")
        debug_log(f"Error executing VISA command '{visa_command}': {e}. This thing is a pain in the ass!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
