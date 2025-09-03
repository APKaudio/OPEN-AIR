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
# Version 20250902.115200.1
# UPDATED: Implemented the logic for YakBeg, YakRig, YakDo, YakGet, and YakSet functions.

import csv
import os
import inspect
import pyvisa
import time
from tkinter import messagebox
from collections import defaultdict
from typing import Optional, List, Dict

# Assume ScpiDispatcher is imported
from agents.agent_yak_dispatch_scpi import ScpiDispatcher
from display.debug_logic import debug_log, log_visa_command
from display.console_logic import console_log

# --- Global Scope Variables ---
current_version = "20250902.115200.1"
current_version_hash = (20250902 * 115200 * 1)
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
VISA_COMMAND_DELAY_SECONDS = 0.05
MAX_RETRY_ATTEMPTS = 3
MHZ_TO_HZ = 1000000

def YakBeg(dispatcher: ScpiDispatcher, command_type, console_print_func, *variable_values):
    """
    Executes a 'BEG' (Beg) VISA command and returns the response.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering YakBeg. command_type: {command_type}, variable_values: {variable_values}",
                file=current_file,
                version=current_version,
                function=current_function)
    
    response = dispatcher.dispatch_command(command_type, "BEG", *variable_values)
    
    if response and response != "FAILED":
        console_print_func(f"✅ Beg Response: {response}")
        debug_log(f"🐐 ✅ Beg query response: {response}. Fucking finally!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return response
    else:
        console_print_func("❌ No response received or query failed.")
        debug_log("🐐 ❌ Beg query failed or no response. What the hell happened?!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return "FAILED"

def YakRig(dispatcher: ScpiDispatcher, command_type, console_print_func, *variable_values):
    """
    Executes a 'RIG' VISA command for multi-parameter settings.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering YakRig. command_type: {command_type}, variable_values: {variable_values}",
                file=current_file,
                version=current_version,
                function=current_function)
    
    response = dispatcher.dispatch_command(command_type, "RIG", *variable_values)
    
    if response == "PASSED":
        console_print_func("✅ Rig command executed successfully.")
        debug_log("🐐 ✅ Rig command executed successfully.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return "PASSED"
    else:
        console_print_func("❌ Rig command execution failed.")
        debug_log("🐐 ❌ Rig command execution failed. What the hell went wrong?!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return "FAILED"


def YakDo(dispatcher: ScpiDispatcher, command_type, console_print_func):
    """
    Executes a 'DO' VISA command (a simple write without a response).
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering YakDo. command_type: {command_type}",
              file=current_file,
              version=current_version,
              function=current_function)
    
    response = dispatcher.dispatch_command(command_type, "DO")
    
    if response == "PASSED":
        console_print_func("✅ Command executed successfully.")
        debug_log("🐐 ✅ Command executed successfully.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return "PASSED"
    else:
        console_print_func("❌ Command execution failed.")
        debug_log("🐐 ❌ DO command execution failed. What the hell went wrong?!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return "FAILED"


def YakGet(dispatcher: ScpiDispatcher, command_type, console_print_func):
    """
    Executes a 'GET' VISA command and returns the response.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering YakGet. command_type: {command_type}",
                file=current_file,
                version=current_version,
                function=current_function)
    
    response = dispatcher.dispatch_command(command_type, "GET")

    if response and response != "FAILED":
        console_print_func(f"✅ Response: {response}")
        debug_log(f"🐐 ✅ Query response: {response}. Finally!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return response
    else:
        console_print_func("❌ No response received or query failed.")
        debug_log("🐐 ❌ Query failed or no response. What the hell happened?!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return "FAILED"

def YakSet(dispatcher: ScpiDispatcher, command_type, variable_value, console_print_func):
    """
    Executes a 'SET' VISA command with a specific value.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering YakSet. command_type: {command_type}, variable_value: {variable_value}",
                file=current_file,
                version=current_version,
                function=current_function)
    
    response = dispatcher.dispatch_command(command_type, "SET", variable_value)
    
    if response == "PASSED":
        console_print_func("✅ Command executed successfully.")
        debug_log("🐐 ✅ Command executed successfully.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return "PASSED"
    else:
        console_print_func("❌ Command execution failed.")
        debug_log("🐐 ❌ SET command execution failed. What the hell went wrong?!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return "FAILED"