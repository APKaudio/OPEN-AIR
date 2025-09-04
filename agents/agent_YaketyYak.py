# agents/agent_YaketyYak.py
#
# This agent provides a high-level API for executing different types of SCPI commands
# (GET, SET, DO, RIG, BEG). It acts as a bridge between the application's business logic
# and the low-level SCPI dispatcher.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250904.004900.1

import os
import inspect

# --- Utility and Manager Imports ---
from workers.worker_logging import debug_log, console_log
from managers.manager_visa_dispatch_scpi import ScpiDispatcher

# --- Global Scope Variables (as per Protocol 4.4) ---
current_version = "20250904.004900.1"
current_version_hash = (20250904 * 4900 * 1)
current_file = f"{os.path.basename(__file__)}"


def YakBeg(dispatcher: ScpiDispatcher, command_string: str):
    # Executes a 'BEG' (Begin) VISA command, which is a combined set-and-query operation.
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(
        message=f"🐐 🟢 Entering {current_function_name} with command: {command_string}",
        file=current_file, version=current_version, function=current_function_name,
        console_print_func=dispatcher._print_to_gui_console
    )
    try:
        response = dispatcher.query_safe(command=command_string)
        if response is not None:
            console_log(f"✅ Beg Response: {response}")
            return response
        else:
            console_log("❌ No response received or BEG query failed.")
            return "FAILED"
    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        return "FAILED"

def YakRig(dispatcher: ScpiDispatcher, command_string: str):
    # Executes a 'RIG' VISA command for multi-parameter settings.
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(
        message=f"🐐 🟢 Entering {current_function_name} with command: {command_string}",
        file=current_file, version=current_version, function=current_function_name,
        console_print_func=dispatcher._print_to_gui_console
    )
    try:
        if dispatcher.write_safe(command=command_string):
            console_log("✅ Rig command executed successfully.")
            return "PASSED"
        else:
            console_log("❌ Rig command execution failed.")
            return "FAILED"
    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        return "FAILED"

def YakDo(dispatcher: ScpiDispatcher, command_string: str):
    # Executes a 'DO' VISA command (a simple write without a response).
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(
        message=f"🐐 🟢 Entering {current_function_name} with command: {command_string}",
        file=current_file, version=current_version, function=current_function_name,
        console_print_func=dispatcher._print_to_gui_console
    )
    try:
        if dispatcher.write_safe(command=command_string):
            console_log("✅ Command executed successfully.")
            return "PASSED"
        else:
            console_log("❌ Command execution failed.")
            return "FAILED"
    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        return "FAILED"

def YakGet(dispatcher: ScpiDispatcher, command_string: str):
    # Executes a 'GET' VISA command and returns the response.
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(
        message=f"🐐 🟢 Entering {current_function_name} with command: {command_string}",
        file=current_file, version=current_version, function=current_function_name,
        console_print_func=dispatcher._print_to_gui_console
    )
    try:
        response = dispatcher.query_safe(command=command_string)
        if response is not None:
            console_log(f"✅ Response: {response}")
            return response
        else:
            console_log("❌ No response received or query failed.")
            return "FAILED"
    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        return "FAILED"

def YakSet(dispatcher: ScpiDispatcher, command_string: str):
    # Executes a 'SET' VISA command with a specific value.
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(
        message=f"🐐 🟢 Entering {current_function_name} with command: {command_string}",
        file=current_file, version=current_version, function=current_function_name,
        console_print_func=dispatcher._print_to_gui_console
    )
    try:
        if dispatcher.write_safe(command=command_string):
            console_log("✅ Command executed successfully.")
            return "PASSED"
        else:
            console_log("❌ Command execution failed.")
            return "FAILED"
    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        return "FAILED"

