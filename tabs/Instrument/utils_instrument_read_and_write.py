# tabs/Instrument/utils_instrument_read_and_write
# .py
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

