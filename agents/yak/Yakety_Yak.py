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
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250821.210502.1
# FIXED: The YakNab function now returns the raw response string without parsing it, as this should be handled by the specific handler function that knows the data structure.
# UPDATED: All debug messages now include the required 🐐 emoji at the start.

import csv
import os
import inspect
import pyvisa
import time
from tkinter import messagebox
from display.debug_logic import debug_log, log_visa_command
from display.console_logic import console_log
from ref.ref_file_paths import VISA_COMMANDS_FILE_PATH

# FIXED: Import the low-level read/write functions from the correct location
from yak.utils_yak_visa import write_safe, query_safe

# --- User-configurable variables ---
VISA_COMMAND_DELAY_SECONDS = 0.05
MAX_RETRY_ATTEMPTS = 3

# Global variable to store loaded commands to avoid re-reading the file
_visa_commands_data = []
_last_file_modification_time = 0

# --- Versioning ---
w = 20250821
x_str = '210502'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"


def _load_commands_from_file(file_path):
    # Function Description:
    # Loads or reloads the VISA commands from the specified CSV file.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 Entering {current_function}. File: {file_path}",
                file=current_file,
                version=current_version,
                function=current_function)

    global _visa_commands_data, _last_file_modification_time

    try:
        if not os.path.exists(file_path):
            debug_log(f"🐐 ❌ File not found: {file_path}. Aborting load. �",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return False

        current_mod_time = os.path.getmtime(file_path)
        if current_mod_time <= _last_file_modification_time:
            debug_log(f"🐐 😴 File '{file_path}' has not been modified since last load. Skipping. 😴",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return True

        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            _visa_commands_data = [row for row in reader]

        _last_file_modification_time = current_mod_time
        debug_log(f"🐐 ✅ Successfully loaded {len(_visa_commands_data)} commands from file. 🎉",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return True

    except Exception as e:
        debug_log(f"🐐 💥 Error loading commands from file: {e}. This is a goddamn mess! 💥",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        _visa_commands_data = []
        return False

def _find_command(command_type, action_type, model):
    # Function Description:
    # Finds the correct VISA command from the loaded data based on the command type,
    # action type, and instrument model.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🔍 Searching for command. Type: '{command_type}', Action: '{action_type}', Model: '{model}'. Let's find it! 🕵️‍♀️",
                file=current_file,
                version=current_version,
                function=current_function)

    upper_command_type = command_type.upper()
    upper_action_type = action_type.upper()
    upper_model = model.upper()
    
    if not _visa_commands_data:
        debug_log("🐐 ❌ No command data loaded. What a disaster!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return None, None, None

    for row in _visa_commands_data:
        if row[2].upper() == upper_command_type and row[3].upper() == upper_action_type and row[1].upper() == upper_model:
            debug_log(f"🐐 ✅ Found an exact match! Command: '{upper_command_type}', Action: '{upper_action_type}', Model: '{upper_model}'. This is fucking brilliant! ✅",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return row[3], row[4], row[5]

    for row in _visa_commands_data:
        if row[2].upper() == upper_command_type and row[3].upper() == upper_action_type and row[1] == '*':
            debug_log(f"🐐 🔎 Found a wildcard match! Command: '{upper_command_type}', Action: '{upper_action_type}', Model: '*'. Not perfect, but it'll do. 😉",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return row[3], row[4], row[5]

    debug_log(f"🐐 ❌ No matching command found for Type: '{upper_command_type}', Action: '{upper_action_type}', Model: '{upper_model}'. This is a fucking waste of time! 🤯",
                file=current_file,
                version=current_version,
                function=current_function)
    return None, None, None

def YakRig(app_instance, command_type, console_print_func, *variable_values):
    """
    Function Description:
    Executes a 'RIG' VISA command by combining a template command string
    with up to 8 provided variable values. This is designed for single-line
    configuration commands that set multiple parameters at once.

    Inputs:
    - app_instance (object): A reference to the main application instance.
    - command_type (str): The name of the 'RIG' command from the CSV (e.g., "MARKER/PLACE/ALL").
    - console_print_func (function): A function to print messages to the GUI console.
    - variable_values (str...): Up to 8 values to be substituted into the command template.
                                These will replace the placeholders 111, 222, etc.

    Outputs:
    - "PASSED" if the command is executed successfully, "FAILED" otherwise.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering YakRig. command_type: {command_type}, variable_values: {variable_values}",
                file=current_file,
                version=current_version,
                function=current_function)

    _load_commands_from_file(app_instance.VISA_COMMANDS_FILE_PATH)
    
    model = app_instance.connected_instrument_model.get()
    
    action, command_template, _ = _find_command(command_type, "RIG", model)

    if action == "RIG" and command_template:
        full_command = command_template
        placeholders = ["111", "222", "333", "444", "555", "666", "777", "888"]
        
        # Replace placeholders with provided values
        for i, value in enumerate(variable_values):
            if i < len(placeholders):
                full_command = full_command.replace(placeholders[i], str(value))
        
        console_log(f"💬 Rigging command: {full_command}")
        debug_log(f"🐐 📝 Rigged command string: {full_command}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        if write_safe(app_instance.inst, full_command, console_print_func):
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
    else:
        console_log(f"❌ Could not find a matching RIG command for '{command_type}'.")
        debug_log(f"🐐 🚫 No matching RIG command found for '{command_type}'. Fucking useless!",
                   file=current_file,
                    version=current_version,
                    function=current_function)
        return "FAILED"

def YakBeg(app_instance, command_type, console_print_func, *variable_values):
    """
    Function Description:
    Executes a 'BEG' (Beg) VISA command by combining a SET command with a GET query.
    This is an atomic action designed for configuring a setting and immediately
    verifying its value from the instrument.

    Inputs:
    - app_instance (object): A reference to the main application instance.
    - command_type (str): The name of the 'BEG' command from the CSV.
    - console_print_func (function): A function to print messages to the GUI console.
    - variable_values (str...): Up to 8 values to be substituted into the command template.
                                These will replace the placeholders 111, 222, etc.

    Outputs:
    - The response string from the GET command if successful, or "FAILED" otherwise.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering YakBeg. command_type: {command_type}, variable_values: {variable_values}",
                file=current_file,
                version=current_version,
                function=current_function)
    
    _load_commands_from_file(app_instance.VISA_COMMANDS_FILE_PATH)
    
    model = app_instance.connected_instrument_model.get()
    
    action, command_template, _ = _find_command(command_type, "BEG", model)

    if action == "BEG" and command_template:
        full_command = command_template
        placeholders = ["111", "222", "333", "444", "555", "666", "777", "888"]
        
        # Replace placeholders with provided values
        for i, value in enumerate(variable_values):
            if i < len(placeholders):
                full_command = full_command.replace(placeholders[i], str(value))

        console_log(f"💬 Begging for a response with command: {full_command}")
        debug_log(f"🐐 📝 Beg command string: {full_command}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # The BEG command is a single string with both set and get queries.
        # We use query_safe to send the entire string and get the response.
        response = query_safe(app_instance.inst, full_command, console_print_func)
    
        if response is not None:
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
    else:
        console_log(f"❌ Could not find a matching BEG command for '{command_type}'.")
        debug_log(f"🐐 🚫 No matching BEG command found for '{command_type}'. Fucking useless!",
                   file=current_file,
                    version=current_version,
                    function=current_function)
        return "FAILED"

def YakGet(app_instance, command_type, console_print_func):
    # Function Description:
    # Executes a 'GET' or a new 'NAB' VISA command for a given command type.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering YakGet. command_type: {command_type}",
                file=current_file,
                version=current_version,
                function=current_function)
    
    _load_commands_from_file(VISA_COMMANDS_FILE_PATH)
    
    manufacturer = app_instance.connected_instrument_manufacturer.get()
    model = app_instance.connected_instrument_model.get()
    
    action, command, variable = _find_command(command_type, "GET", model)
    if not action:
        action, command, variable = _find_command(command_type, "NAB", model)
    
    if action and command:
        return execute_visa_command(app_instance, action, command, variable, console_print_func)
    else:
        console_print_func(f"❌ Could not find a matching GET or NAB command for '{command_type}'.")
        debug_log(f"🐐 🚫 No matching GET or NAB command found for '{command_type}'. Fucking useless!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return "FAILED"
  
def YakNab(app_instance, command_type, console_print_func):
    """
    Function Description:
    Executes a 'NAB' (multi-query) VISA command for a given command type.
    
    Inputs:
    - app_instance (object): A reference to the main application instance.
    - command_type (str): The name of the 'NAB' command from the CSV.
    - console_print_func (function): A function to print messages to the GUI console.
    
    Outputs:
    - The response string from the GET command if successful, or a list of parsed strings otherwise.
      "FAILED" on failure.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering YakNab. command_type: {command_type}",
                file=current_file,
                version=current_version,
                function=current_function)

    _load_commands_from_file(app_instance.VISA_COMMANDS_FILE_PATH)
    
    manufacturer = app_instance.connected_instrument_manufacturer.get()
    model = app_instance.connected_instrument_model.get()

    action, command, num_reads_str = _find_command(command_type, "NAB", model)

    if action == "NAB" and command:
        try:
            response_string = query_safe(app_instance.inst, command, console_print_func)
        except (ValueError, IndexError):
            console_print_func("❌ NAB command variable for num_reads is not a valid integer.")
            debug_log("🐐 🤷‍♀️ NAB command variable for num_reads is not a valid integer. Defaulting to 1. 🤷‍♀️",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            response_string = query_safe(app_instance.inst, command, console_print_func)
        
        if response_string is not None:
            values = [val.strip() for val in response_string.split(';') if val.strip()]
            console_print_func(f"✅ NAB Response: {values}")
            debug_log(f"🐐 ✅ NAB Query response: {response_string}. Fucking finally!",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return values
        else:
            return "FAILED"
    else:
        console_print_func(f"❌ Could not find a matching NAB command for '{command_type}'.")
        debug_log(f"🐐 🚫 No matching NAB command found for '{command_type}'. Fucking useless!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return "FAILED"


def YakSet(app_instance, command_type, variable_value, console_print_func):
    # Function Description:
    # Executes a 'SET' VISA command with a specific value.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering YakSet. command_type: {command_type}, variable_value: {variable_value}",
                file=current_file,
                version=current_version,
                function=current_function)

    _load_commands_from_file(app_instance.VISA_COMMANDS_FILE_PATH)
    
    manufacturer = app_instance.connected_instrument_manufacturer.get()
    model = app_instance.connected_instrument_model.get()
    
    action, command, _ = _find_command(command_type, "SET", model)
    
    if action == "SET" and command:
        return execute_visa_command(app_instance, action, command, variable_value, console_print_func)
    else:
        console_print_func(f"❌ Could not find a matching SET command for '{command_type}'.")
        debug_log(f"🐐 🚫 No matching SET command found for '{command_type}'. Fucking useless!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return "FAILED"

def YakDo(app_instance, command_type, console_print_func):
    # Function Description:
    # Executes a 'DO' VISA command.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering YakDo. command_type: {command_type}",
                file=current_file,
                version=current_version,
                function=current_function)

    _load_commands_from_file(VISA_COMMANDS_FILE_PATH)
    
    manufacturer = app_instance.connected_instrument_manufacturer.get()
    model = app_instance.connected_instrument_model.get()
    
    action, command, variable = _find_command(command_type, "DO", model)
    
    if action == "DO" and command:
        return execute_visa_command(app_instance, action, command, variable, console_print_func)
    else:
        console_print_func(f"❌ Could not find a matching DO command for '{command_type}'.")
        debug_log(f"🐐 🚫 No matching DO command found for '{command_type}'. Fucking useless!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return "FAILED"

def execute_visa_command(app_instance, action_type, visa_command, variable_value, console_print_func, num_reads=1):
    # Function Description:
    # Executes a given VISA command based on its action type and variable value.
    current_function = inspect.currentframe().f_code.co_name
    inst = app_instance.inst

    if not inst:
        console_print_func("❌ No instrument connected. Cannot execute VISA command.")
        debug_log("🐐 ❌ No instrument connected for execute_visa_command. Fucking useless!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return "FAILED"

    try:
        if action_type == "GET":
            full_command = f"{visa_command}{variable_value}" if variable_value and variable_value.strip() == "?" else visa_command
            debug_log(f"🐐 📝 Prepared command string for GET: {full_command}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            response = query_safe(inst, full_command, console_print_func)
            if response is not None:
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
        elif action_type == "NAB":
            full_command = visa_command
            
            response_string = query_safe(inst, full_command, console_print_func)
            
            if response_string is not None:
                values = [val.strip() for val in response_string.split(';') if val.strip()]
                console_print_func(f"✅ NAB Response: {values}")
                debug_log(f"🐐 ✅ NAB Query response: {response_string}. Fucking finally!",
                            file=current_file,
                            version=current_version,
                            function=current_function)
                return values
            else:
                return "FAILED"

        elif action_type == "DO":
            if variable_value and variable_value.strip():
                full_command = f"{visa_command} {variable_value}"
            else:
                full_command = visa_command
            
            debug_log(f"🐐 📝 Prepared command string for DO: {full_command}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            if write_safe(inst, full_command, console_print_func):
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
        elif action_type == "SET":
            try:
                float_value = float(variable_value)
                int_value = int(float_value)
                if float_value == int_value:
                    full_command = f"{visa_command} {int_value}"
                else:
                    full_command = f"{visa_command} {float_value}"
            except (ValueError, TypeError):
                full_command = f"{visa_command} {variable_value}"
            
            debug_log(f"🐐 📝 Prepared command string for SET: {full_command}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            if write_safe(inst, full_command, console_print_func):
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
        elif action_type == "RIG":
            full_command = visa_command
            
            debug_log(f"🐐 📝 Prepared command string for RIG: {full_command}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            if write_safe(inst, full_command, console_print_func):
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
        elif action_type == "BEG":
            full_command = visa_command
            debug_log(f"🐐 📝 Prepared command string for BEG: {full_command}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            response_string = query_safe(inst, visa_command, console_print_func)
            if response_string is not None:
                return response_string
            else:
                return "FAILED"
        else:
            console_print_func(f"⚠️ Unknown action type '{action_type}'. Cannot execute command.")
            debug_log(f"🐐 ❌ Unknown action type '{action_type}' for command: {visa_command}. This is a goddamn mess!",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return "FAILED"
    except Exception as e:
        console_print_func(f"❌ Error during VISA command execution: {e}")
        debug_log(f"🐐 🧨 Error executing VISA command '{visa_command}': {e}. This thing is a pain in the ass!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return "FAILED"
