# tabs/Instrument/Yakety_Yak.py
#
# This file provides a high-level interface for executing VISA commands
# by a user-defined type, model, and manufacturer. It acts as a wrapper
# for the low-level `execute_visa_command` function, ensuring the correct
# command is sent based on the provided parameters. It also manages the
# loading of the `visa_commands.csv` file.
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
# Version 20250811.200000.0

current_version = "20250811.200000.0"
current_version_hash = 20250811 * 200000 * 0

import csv
import os
import inspect
import pyvisa
import time
from tkinter import messagebox
from display.debug_logic import debug_log, log_visa_command
from display.console_logic import console_log

# Global variable to store loaded commands to avoid re-reading the file
_visa_commands_data = []
_last_file_modification_time = 0

# --- Helper functions for low-level VISA operations ---
def _reset_device(inst, console_print_func):
    """
    Function Description:
    Sends a soft reset command to the instrument to restore a known state after an error.
    """
    current_function = inspect.currentframe().f_code.co_name
    console_print_func("⚠️ Command failed. Attempting to reset the instrument with '*RST'...")
    debug_log(f"Command failed. Attempting to send reset command '*RST' to the instrument.",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)
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
    """
    Function Description:
    Safely writes a SCPI command to the instrument.
    """
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
        log_visa_command(command, "SENT")
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
    """
    Function Description:
    Safely queries the instrument with a SCPI command and returns the response.
    """
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
        log_visa_command(command, "SENT")
        log_visa_command(response, "RECEIVED")
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

def execute_visa_command(inst, action_type, visa_command, variable_value, console_print_func):
    """
    Function Description:
    Executes a given VISA command based on its action type and variable value.
    This function has been updated to handle a 'GET' action where the '?' is
    passed in the `variable_value` parameter. It also returns the command's
    response or a boolean indicating success/failure. If the command fails for
    any reason, it will now attempt to soft reset the device with '*RST'.

    Inputs to this function:
    - inst: The PyVISA instrument instance.
    - action_type (str): The type of action ("GET", "SET", "DO").
    - visa_command (str): The base VISA command string.
    - variable_value (str): The variable value to append for "SET" commands,
      or the "?" terminator for "GET" commands.
    - console_print_func (function): Function to print messages to the GUI console.

    Outputs of this function:
    - str or None: The instrument's response if the action was a successful "GET".
    - str: "PASSED", "TIME FAILED", or "FAILED" for a "DO" command.
    - str: "PASSED", "TIME FAILED", or "FAILED" for a "SET" command.
    """
    current_function = inspect.currentframe().f_code.co_name

    if not inst:
        console_print_func("❌ No instrument connected. Cannot execute VISA command.")
        debug_log("No instrument connected for execute_visa_command. Fucking useless!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        return "FAILED"

    try:
        if action_type == "GET":
            full_command = f"{visa_command}{variable_value}" if variable_value.startswith("?") else visa_command
            response = query_safe(inst, full_command, console_print_func)
            if response is not None:
                console_print_func(f"✅ Response: {response}")
                debug_log(f"Query response: {response}. Fucking finally!",
                            file=os.path.basename(__file__),
                            version=current_version,
                            function=current_function)
                return response
            else:
                console_print_func("❌ No response received or query failed.")
                debug_log("Query failed or no response. What the hell happened?!",
                            file=os.path.basename(__file__),
                            version=current_version,
                            function=current_function)
                _reset_device(inst, console_print_func)
                return "FAILED"
        elif action_type == "SET":
            if set_safe(inst, visa_command, variable_value, console_print_func):
                return _wait_for_opc(inst, console_print_func)
            else:
                console_print_func("❌ Command execution failed.")
                debug_log("SET command execution failed. This bugger is being problematic!",
                            file=os.path.basename(__file__),
                            version=current_version,
                            function=current_function)
                _reset_device(inst, console_print_func)
                return "FAILED"
        elif action_type == "DO":
            if write_safe(inst, visa_command, console_print_func):
                return _wait_for_opc(inst, console_print_func)
            else:
                console_print_func("❌ Command execution failed.")
                debug_log("DO command execution failed. What the hell went wrong?!",
                            file=os.path.basename(__file__),
                            version=current_version,
                            function=current_function)
                _reset_device(inst, console_print_func)
                return "FAILED"
        else:
            console_print_func(f"⚠️ Unknown action type '{action_type}'. Cannot execute command.")
            debug_log(f"Unknown action type '{action_type}' for command: {visa_command}. This is a goddamn mess!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            _reset_device(inst, console_print_func)
            return "FAILED"
    except Exception as e:
        console_print_func(f"❌ Error during VISA command execution: {e}")
        debug_log(f"Error executing VISA command '{visa_command}': {e}. This thing is a pain in the ass!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        _reset_device(inst, console_print_func)
        return "FAILED"

def _load_commands_from_file(file_path):
    """
    Loads or reloads the VISA commands from the specified CSV file.
    It checks the file's modification time to avoid unnecessary re-reads.
    """
    global _visa_commands_data
    global _last_file_modification_time
    
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering _load_commands_from_file. File: {file_path}",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)

    try:
        if not os.path.exists(file_path):
            debug_log(f"File not found: {file_path}. Aborting load. 💀",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return False

        current_mod_time = os.path.getmtime(file_path)
        if current_mod_time <= _last_file_modification_time:
            debug_log(f"File '{file_path}' has not been modified since last load. Skipping. 😴",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return True

        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader) # Skip header row
            _visa_commands_data = [row for row in reader]

        _last_file_modification_time = current_mod_time
        debug_log(f"Successfully loaded {len(_visa_commands_data)} commands from file. 🚀",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        return True

    except Exception as e:
        debug_log(f"Error loading commands from file: {e}. This is a goddamn mess! 💥",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        _visa_commands_data = [] # Clear data on error
        return False

def _find_command(command_type, manufacturer, model):
    """
    Finds the correct VISA command and action type from the loaded data
    based on command type, manufacturer, and model. It prioritizes specific
    matches over generic ones.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Searching for command. Type: '{command_type}', Manufacturer: '{manufacturer}', Model: '{model}'. Let's find it! 🕵️‍♀️",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)

    if not _visa_commands_data:
        debug_log("No command data loaded. What a disaster!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        return None, None, None

    # Prioritize exact matches (Manufacturer and Model)
    for row in _visa_commands_data:
        # Columns: Manufacturer (0), Model (1), Command Type (2), Action (3), VISA Command (4), Variable (5), Validated (6)
        if row[2] == command_type and row[0] == manufacturer and row[1] == model:
            debug_log("Found an exact match! This is fucking brilliant! ✅",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return row[3], row[4], row[5]

    # Fallback to wildcard matches
    for row in _visa_commands_data:
        # Match any manufacturer/model if a wildcard is used
        if row[2] == command_type and (row[0] == '*' or row[1] == '*'):
            debug_log("Found a wildcard match. Not perfect, but it'll do. 😉",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return row[3], row[4], row[5]

    debug_log("No matching command found. This is a fucking waste of time! 💥",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)
    return None, None, None

def YakGet(app_instance, command_type, console_print_func):
    """
    Function Description:
    Executes a 'GET' VISA command for a given command type.
    It automatically finds the correct command from the loaded data based on
    the connected instrument's manufacturer and model.

    Inputs:
        app_instance (object): Reference to the main application instance to get the instrument and its details.
        command_type (str): The logical name of the command to execute (e.g., "GET_FREQUENCY").
        console_print_func (function): Function to print messages to the GUI console.

    Outputs:
        str or None: The response from the instrument, or None on failure.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering YakGet. command_type: {command_type}",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)
    
    _load_commands_from_file(app_instance.VISA_COMMANDS_FILE_PATH)
    
    manufacturer = app_instance.connected_instrument_manufacturer.get()
    model = app_instance.connected_instrument_model.get()
    
    action, command, variable = _find_command(command_type, manufacturer, model)
    
    if action == "GET" and command:
        return execute_visa_command(app_instance.inst, action, command, variable, console_print_func)
    else:
        console_print_func(f"❌ Could not find a matching GET command for '{command_type}'.")
        debug_log(f"No matching GET command found for '{command_type}'. Fucking useless!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        return None

def YakSet(app_instance, command_type, variable_value, console_print_func):
    """
    Function Description:
    Executes a 'SET' VISA command with a specific value.
    It finds the correct command and sends it to the instrument.

    Inputs:
        app_instance (object): Reference to the main application instance.
        command_type (str): The logical name of the command to execute.
        variable_value (str): The value to be set.
        console_print_func (function): Function to print messages to the GUI console.

    Outputs:
        str or None: The result from `execute_visa_command` ("PASSED", "FAILED", etc.).
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering YakSet. command_type: {command_type}, variable_value: {variable_value}",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)

    _load_commands_from_file(app_instance.VISA_COMMANDS_FILE_PATH)
    
    manufacturer = app_instance.connected_instrument_manufacturer.get()
    model = app_instance.connected_instrument_model.get()
    
    action, command, _ = _find_command(command_type, manufacturer, model)
    
    if action == "SET" and command:
        return execute_visa_command(app_instance.inst, action, command, variable_value, console_print_func)
    else:
        console_print_func(f"❌ Could not find a matching SET command for '{command_type}'.")
        debug_log(f"No matching SET command found for '{command_type}'. Fucking useless!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        return "FAILED"

def YakDo(app_instance, command_type, console_print_func):
    """
    Function Description:
    Executes a 'DO' VISA command.
    It finds the command and sends it without any variable.

    Inputs:
        app_instance (object): Reference to the main application instance.
        command_type (str): The logical name of the command to execute.
        console_print_func (function): Function to print messages to the GUI console.

    Outputs:
        str or None: The result from `execute_visa_command` ("PASSED", "FAILED", etc.).
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering YakDo. command_type: {command_type}",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)

    _load_commands_from_file(app_instance.VISA_COMMANDS_FILE_PATH)
    
    manufacturer = app_instance.connected_instrument_manufacturer.get()
    model = app_instance.connected_instrument_model.get()
    
    action, command, _ = _find_command(command_type, manufacturer, model)
    
    if action == "DO" and command:
        return execute_visa_command(app_instance.inst, action, command, "", console_print_func)
    else:
        console_print_func(f"❌ Could not find a matching DO command for '{command_type}'.")
        debug_log(f"No matching DO command found for '{command_type}'. Fucking useless!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        return "FAILED"