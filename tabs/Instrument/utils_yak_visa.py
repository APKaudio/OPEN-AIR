# utils/utils_yak_visa.py
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
#
#
# Version 20250801.1022.1 (Updated header and verified imports for new folder structure)

current_version = "20250801.1022.1" # this variable should always be defined below the header to make the debugging better

import inspect
from utils.utils_instrument_control import debug_print, query_safe, write_safe

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
    current_file = __file__
    full_command = f"{command} {value}"
    debug_print(f"Attempting to SET: {full_command}", file=current_file, function=current_function, console_print_func=console_print_func)
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
    current_file = __file__

    if not inst:
        console_print_func("❌ No instrument connected. Cannot execute VISA command.")
        debug_print("No instrument connected for execute_visa_command.", file=current_file, function=current_function, console_print_func=console_print_func)
        return

    console_print_func(f"Attempting to perform {action_type} action for: {visa_command}")
    debug_print(f"Action: {action_type}, Command: {visa_command}, Variable: '{variable_value}'", file=current_file, function=current_function, console_print_func=console_print_func)

    try:
        if action_type == "GET":
            response = query_safe(inst, visa_command, console_print_func)
            if response is not None:
                console_print_func(f"✅ Response: {response}")
                debug_print(f"Query response: {response}", file=current_file, function=current_function, console_print_func=console_print_func)
            else:
                console_print_func("❌ No response received or query failed.")
                debug_print("Query failed or no response.", file=current_file, function=current_function, console_print_func=console_print_func)
        elif action_type == "SET":
            if set_safe(inst, visa_command, variable_value, console_print_func):
                console_print_func("✅ Command executed successfully.")
                debug_print("SET command executed successfully.", file=current_file, function=current_function, console_print_func=console_print_func)
            else:
                console_print_func("❌ Command execution failed.")
                debug_print("SET command execution failed.", file=current_file, function=current_function, console_print_func=console_print_func)
        elif action_type == "DO":
            if write_safe(inst, visa_command, console_print_func):
                console_print_func("✅ Command executed successfully.")
                debug_print("DO command executed successfully.", file=current_file, function=current_function, console_print_func=console_print_func)
            else:
                console_print_func("❌ Command execution failed.")
                debug_print("DO command execution failed.", file=current_file, function=current_function, console_print_func=console_print_func)
        else:
            console_print_func(f"⚠️ Unknown action type '{action_type}'. Cannot execute command.")
            debug_print(f"Unknown action type '{action_type}' for command: {visa_command}", file=current_file, function=current_function, console_print_func=console_print_func)
    except Exception as e:
        console_print_func(f"❌ Error during VISA command execution: {e}")
        debug_print(f"Error executing VISA command '{visa_command}': {e}", file=current_file, function=current_function, console_print_func=console_print_func)

