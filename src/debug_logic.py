# src/debug_logic.py
#
# This module centralizes all debug and console logging functionality for the application.
# It provides functions to print debug messages (which can be toggled to go to the terminal
# or the GUI console) and general application messages (which always go to the GUI console).
# It also manages global flags for debug mode and VISA command logging.
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
# Version 20250802.0070.2 (Added debug to file logic and new global flags.)

current_version = "20250802.0070.2" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 70 * 2 # Example hash, adjust as needed

import sys
import os
from datetime import datetime
import inspect # Import inspect for function name


# Global variables for debug control
DEBUG_MODE = False # Controls if debug_log messages are processed at all
LOG_VISA_COMMANDS = False # Controls if VISA commands are logged
DEBUG_TO_TERMINAL = False # Controls where debug_log output goes (True: terminal, False: GUI console)
DEBUG_TO_FILE = False # NEW: Controls if debug_log output goes to a file
INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE = False # NEW: Controls if console_log messages also go to debug file
DEBUG_FILE_PATH = None # NEW: Path to the debug log file

# Reference to the GUI console TextRedirector or original stdout/stderr
_gui_console_stdout_redirector = None
_gui_console_stderr_redirector = None
_original_stdout = sys.stdout
_original_stderr = sys.stderr


def set_debug_mode(mode: bool):
    """
    Function Description:
    Sets the global DEBUG_MODE flag.

    Inputs:
    - mode (bool): True to enable debug mode, False to disable.

    Process of this function:
    1. Updates the global `DEBUG_MODE` variable.
    2. Prints a debug message indicating the new state.

    Outputs of this function:
    - None. Modifies a global variable.
    """
    global DEBUG_MODE
    DEBUG_MODE = mode
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Debug mode set to: {DEBUG_MODE}. Let the debugging begin!",
                file=__file__,
                version=current_version,
                function=current_function)


def set_log_visa_commands_mode(mode: bool):
    """
    Function Description:
    Sets the global LOG_VISA_COMMANDS flag.

    Inputs:
    - mode (bool): True to enable VISA command logging, False to disable.

    Process of this function:
    1. Updates the global `LOG_VISA_COMMANDS` variable.
    2. Prints a debug message indicating the new state.

    Outputs of this function:
    - None. Modifies a global variable.
    """
    global LOG_VISA_COMMANDS
    LOG_VISA_COMMANDS = mode
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"VISA command logging set to: {LOG_VISA_COMMANDS}. Tracking those commands!",
                file=__file__,
                version=current_version,
                function=current_function)


def set_debug_to_terminal_mode(mode: bool):
    """
    Function Description:
    Sets the global DEBUG_TO_TERMINAL flag, controlling where debug_log output goes.

    Inputs:
    - mode (bool): True to redirect debug output to the terminal, False to GUI console.

    Process of this function:
    1. Updates the global `DEBUG_TO_TERMINAL` variable.
    2. Prints a debug message indicating the new output destination.

    Outputs of this function:
    - None. Modifies a global variable.
    """
    global DEBUG_TO_TERMINAL
    DEBUG_TO_TERMINAL = mode
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Debug output redirected to terminal: {DEBUG_TO_TERMINAL}. Adjusting the stream!",
                file=__file__,
                version=current_version,
                function=current_function)


def set_debug_to_file_mode(mode: bool, file_path: str = None):
    """
    Function Description:
    Sets the global DEBUG_TO_FILE flag and the path for the debug log file.
    If mode is True, opens/creates the debug file, overwriting existing content.

    Inputs:
    - mode (bool): True to enable logging to file, False to disable.
    - file_path (str, optional): The full path to the debug log file. Required if mode is True.

    Process of this function:
    1. Updates the global `DEBUG_TO_FILE` and `DEBUG_FILE_PATH` variables.
    2. If `mode` is True and `file_path` is provided, attempts to open the file in write mode ('w').
       This will overwrite any existing content.
    3. Prints a debug message indicating the new state.

    Outputs of this function:
    - None. Modifies global variables and may create/overwrite a file.
    """
    global DEBUG_TO_FILE, DEBUG_FILE_PATH
    DEBUG_TO_FILE = mode
    DEBUG_FILE_PATH = file_path
    
    current_function = inspect.currentframe().f_code.co_name
    if DEBUG_TO_FILE and DEBUG_FILE_PATH:
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(DEBUG_FILE_PATH), exist_ok=True)
            # Open in write mode ('w') to overwrite existing content
            with open(DEBUG_FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(f"--- Debug Log Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            debug_log(f"Debug logging to file enabled. Output will be saved to: {DEBUG_FILE_PATH}. Overwriting previous log!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except Exception as e:
            DEBUG_TO_FILE = False # Disable if file opening fails
            debug_log(f"ERROR: Could not open debug log file at {DEBUG_FILE_PATH}: {e}. Debug logging to file disabled. This is a disaster!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
    else:
        debug_log(f"Debug logging to file disabled.",
                    file=__file__,
                    version=current_version,
                    function=current_function)


def set_include_console_messages_to_debug_file_mode(mode: bool):
    """
    Function Description:
    Sets the global INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE flag.

    Inputs:
    - mode (bool): True to include console_log messages in the debug file, False otherwise.

    Process of this function:
    1. Updates the global `INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE` variable.
    2. Prints a debug message indicating the new state.

    Outputs of this function:
    - None. Modifies a global variable.
    """
    global INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE
    INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE = mode
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Including console messages in debug file set to: {INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE}.",
                file=__file__,
                version=current_version,
                function=current_function)


def set_debug_redirectors(stdout_redirector, stderr_redirector):
    """
    Function Description:
    Sets the TextRedirector instances for the GUI console for debug messages.
    This should be called by the main application once the GUI console is ready.

    Inputs:
    - stdout_redirector (gui_elements.TextRedirector): Instance for stdout redirection.
    - stderr_redirector (gui_elements.TextRedirector): Instance for stderr redirection.

    Process of this function:
    1. Assigns the provided redirectors to global variables.
    2. Prints a debug message confirming the setup.

    Outputs of this function:
    - None. Modifies global variables.
    """
    global _gui_console_stdout_redirector, _gui_console_stderr_redirector
    _gui_console_stdout_redirector = stdout_redirector
    _gui_console_stderr_redirector = stderr_redirector
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"GUI debug redirectors set. All debug messages will now flow to the GUI! Version: {current_version}",
                file=__file__,
                version=current_version,
                function=current_function)


def _write_to_debug_file(message: str):
    """
    Internal helper to write a message to the debug log file if DEBUG_TO_FILE is True.
    """
    if DEBUG_TO_FILE and DEBUG_FILE_PATH:
        try:
            with open(DEBUG_FILE_PATH, 'a', encoding='utf-8') as f: # 'a' for append mode
                f.write(message + "\n")
        except Exception as e:
            # If writing to file fails, print to original stdout as a last resort
            print(f"ERROR: Failed to write to debug log file {DEBUG_FILE_PATH}: {e}", file=_original_stderr)


def debug_log(message, file=None, version=None, function=None, special=False):
    """
    Function Description:
    Prints a debug message if DEBUG_MODE is enabled.
    Output goes to the terminal, GUI console, and/or a file based on flags.

    Inputs:
        message (str): The debug message.
        file (str, optional): The file from which the debug message originated. Defaults to None.
        version (str, optional): The version of the originating module. Defaults to None.
        function (str, optional): The name of the function sending the message. Defaults to None.
        special (bool, optional): If True, adds a "SPECIAL" tag to the prefix. Defaults to False.

    Process of this function:
        1. Checks if `DEBUG_MODE` is enabled. If not, exits early.
        2. Generates a timestamp.
        3. Constructs a prefix based on `file`, `version`, `function`, and `special` flags.
        4. Formats the full message.
        5. Directs the message to `_original_stdout` (terminal) if `DEBUG_TO_TERMINAL` is True.
        6. Directs the message to `_gui_console_stdout_redirector` (GUI console) if available and `DEBUG_TO_TERMINAL` is False.
        7. Writes the message to the debug file if `DEBUG_TO_FILE` is True.
        8. Falls back to `_original_stdout` if no other output destination is active.

    Outputs of this function:
        None. Prints a message to the console or terminal, and/or writes to a file.
    """
    if not DEBUG_MODE:
        return

    timestamp = datetime.now().strftime("%M.%S")
    
    prefix_parts = []
    if file:
        prefix_parts.append(os.path.basename(file))
    if version:
        prefix_parts.append(f"v{version}")
    if function:
        prefix_parts.append(function)
    if special:
        prefix_parts.append("SPECIAL")

    prefix = f"[{' | '.join(prefix_parts)}] " if prefix_parts else ""
    
    full_message = f"🚫🐛 [{timestamp}] {prefix}{message}"
    
    # Output to terminal
    if DEBUG_TO_TERMINAL:
        print(full_message, file=_original_stdout)
    # Output to GUI console (only if not debugging to terminal)
    elif _gui_console_stdout_redirector:
        _gui_console_stdout_redirector.write(full_message + "\n")
    # Fallback to original stdout if GUI console not ready and not debugging to terminal
    else:
        print(full_message, file=_original_stdout)

    # Output to debug file
    if DEBUG_TO_FILE:
        _write_to_debug_file(full_message)


def log_visa_command(command, direction="SENT"):
    """
    Function Description:
    Logs VISA commands sent to or received from the instrument if LOG_VISA_COMMANDS is enabled.
    Output location (GUI console or terminal, and/or file) is controlled by DEBUG_TO_TERMINAL and DEBUG_TO_FILE.

    Inputs:
        command (str): The VISA command string.
        direction (str, optional): "SENT" or "RECEIVED". Defaults to "SENT".

    Process of this function:
        1. Checks if `LOG_VISA_COMMANDS` is enabled. If not, exits early.
        2. Generates a timestamp.
        3. Formats the log message.
        4. Directs the message to `_original_stdout` (terminal) if `DEBUG_TO_TERMINAL` is True.
        5. Directs the message to `_gui_console_stdout_redirector` (GUI console) if available and `DEBUG_TO_TERMINAL` is False.
        6. Writes the message to the debug file if `DEBUG_TO_FILE` is True.
        7. Falls back to `_original_stdout` if no other output destination is active.

    Outputs of this function:
        None. Prints a message to the console or terminal, and/or writes to a file.
    """
    if not LOG_VISA_COMMANDS:
        return

    timestamp = datetime.now().strftime("%M.%S")
    log_message = f"🌲 [{timestamp}] {direction}: {command.strip()}"
    
    # Output to terminal
    if DEBUG_TO_TERMINAL:
        print(log_message, file=_original_stdout)
    # Output to GUI console (only if not debugging to terminal)
    elif _gui_console_stdout_redirector:
        _gui_console_stdout_redirector.write(log_message + "\n")
    # Fallback to original stdout if GUI console not ready and not debugging to terminal
    else:
        print(log_message, file=_original_stdout)

    # Output to debug file
    if DEBUG_TO_FILE:
        _write_to_debug_file(log_message)

