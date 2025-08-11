# tabs/Instrument/utils_yak_visa.py
#
# This file provides utility functions for safe and standardized execution of
# VISA commands (GET, SET, DO) on connected instruments. It wraps PyVISA operations
# with error handling and integrates with the application's debug logging.
# NOTE: The high-level command execution logic (e.g., `execute_visa_command`) has been
# moved to the new `Yakety_Yak.py` file to separate concerns and improve modularity.
# This file now focuses exclusively on low-level, safe read/write operations.
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
# Version 20250811.183037.0

current_version = "20250811.183037.0"
current_version_hash = 20250811 * 183037 * 0

import inspect
import pyvisa
import time
import os

# Updated imports for new logging functions
from display.debug_logic import debug_log, log_visa_command
from display.console_logic import console_log

# Helper function for instrument communication, using the new logging

def _reset_device(inst, console_print_func):
    """
    Function Description:
    Sends a soft reset command to the instrument to restore a known state after an error.
    This is a last resort to recover from a bad state. It's a fucking miracle worker!

    Inputs to this function:
    - inst: The PyVISA instrument instance.
    - console_print_func: The function to print messages to the GUI console.

    Process of this function:
    1. Sends the '*RST' command using write_safe.
    2. Logs the attempt and the result to the debug and console.
    
    Outputs of this function:
    - bool: True if the reset command was sent, False otherwise.
    """
    current_function = inspect.currentframe().f_code.co_name
    console_print_func("⚠️ Command failed. Attempting to reset the instrument with '*RST'...")
    debug_log(f"Command failed. Attempting to send reset command '*RST' to the instrument.",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)
    # Use the write_safe function to send the reset command
    reset_success = write_safe(inst, "*RST", console_print_func)
    if reset_success:
        console_print_func("✅ Device reset command sent successfully.")
        debug_log("Reset command sent. Goddamn, that felt good!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
    else:
        console_print_func("❌ Failed to send reset command.")
        debug_log("Failed to send reset command. This is a goddamn mess!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
    return reset_success


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
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot write command.")
        debug_log("Instrument not connected. Fucking useless!",
                    file=os.path.basename(__file__),
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
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        _reset_device(inst, console_print_func)
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
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot query command.")
        debug_log("Instrument not connected. Fucking useless!",
                    file=os.path.basename(__file__),
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
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        _reset_device(inst, console_print_func)
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
                file=os.path.basename(__file__),
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
                file=os.path.basename(__file__),
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
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            _reset_device(inst, console_print_func)
            return "FAILED"

    except pyvisa.errors.VisaIOError as e:
        inst.timeout = original_timeout # Restore original timeout
        console_print_func(f"❌ Operation Complete query timed out after {timeout} seconds.")
        debug_log(f"OPC query failed with a timeout: {e}. This thing is a stubborn bastard!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        _reset_device(inst, console_print_func)
        return "TIME FAILED"
    except Exception as e:
        inst.timeout = original_timeout # Restore original timeout
        console_print_func(f"❌ Error during Operation Complete query: {e}")
        debug_log(f"Error during OPC query: {e}. This bugger is being problematic!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        _reset_device(inst, console_print_func)
        return "FAILED"