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
# Version 20250813.103500.1 (FIXED: The write_safe and query_safe functions were restored to this file to resolve the circular import error.)

current_version = "20250813.103500.1" 
current_version_hash = 20250813 * 103500 * 1

import pyvisa
import time
import inspect # Import inspect module
import os # Import os module to fix NameError
from datetime import datetime # Import datetime for timestamp

# Updated imports for new logging functions
from display.debug_logic import debug_log, log_visa_command 
from display.console_logic import console_log

# The low-level read and write functions are defined here.
# These functions should not be in Yakety_Yak.py to prevent circular imports.
def write_safe(inst, command, app_instance_ref, console_print_func=None):
    # Function Description:
    # Safely writes a command to the instrument.
    current_function = inspect.currentframe().f_code.co_name
    console_print_func = console_print_func if console_print_func else console_log
    debug_log(f"Attempting to write command: {command}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    if not inst:
        app_instance_ref.after(0, lambda: console_print_func(f"⚠️ Warning: Not connected. Failed to write: {command}. Connect the damn thing first!"))
        return False
    try:
        log_visa_command(command, "SENT")
        inst.write(command)
        return True
    except pyvisa.errors.VisaIOError as e:
        error_msg = f"🛑 VISA error sending command '{command.strip()}': {e}. This is a nightmare!"
        app_instance_ref.after(0, lambda: console_print_func(error_msg))
        debug_log(error_msg,
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False
    except Exception as e:
        error_msg = f"❌ An unexpected error occurred while sending command '{command.strip()}': {e}. What a mess!"
        app_instance_ref.after(0, lambda: console_print_func(error_msg))
        debug_log(error_msg,
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False


def query_safe(inst, command, app_instance_ref, console_print_func=None):
    # Function Description:
    # Safely queries the instrument and returns the response.
    current_function = inspect.currentframe().f_code.co_name
    console_print_func = console_print_func if console_print_func else console_log
    debug_log(f"Attempting to query command: {command}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    if not inst:
        app_instance_ref.after(0, lambda: console_print_func(f"⚠️ Warning: Not connected. Failed to query: {command}. Connect the damn thing first!"))
        return ""
    try:
        log_visa_command(command, "SENT")
        response = inst.query(command).strip()
        log_visa_command(response, "RECEIVED")
        debug_log(f"Query '{command.strip()}' response: {response}. Got it!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return response
    except pyvisa.errors.VisaIOError as e:
        error_msg = f"🛑 VISA error querying '{command.strip()}': {e}. This goddamn thing is broken!"
        app_instance_ref.after(0, lambda: console_print_func(error_msg))
        debug_log(error_msg,
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return ""
    except Exception as e:
        error_msg = f"❌ An unexpected error occurred while querying '{command.strip()}': {e}. What a pain!"
        app_instance_ref.after(0, lambda: console_print_func(error_msg))
        debug_log(error_msg,
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return ""

