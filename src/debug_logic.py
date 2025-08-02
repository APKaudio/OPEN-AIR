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
# Version 20250802.0020.1 (Refactored debug_print to debug_log with expanded parameters; added flair.)

current_version = "20250802.0020.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 20 * 1 # Example hash, adjust as needed

import sys
import os
from datetime import datetime
import inspect # Import inspect for function name


# Global variables for debug control
DEBUG_MODE = False
LOG_VISA_COMMANDS = False
DEBUG_TO_TERMINAL = False # Controls where debug_log output goes (True: terminal, False: GUI console)

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


def debug_log(message, file=None, version=None, function=None, special=False):
    """
    Function Description:
    Prints a debug message if DEBUG_MODE is enabled.
    Output goes to the terminal or GUI console based on DEBUG_TO_TERMINAL.

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
        5. Directs the message to `_original_stdout` (terminal) if `DEBUG_TO_TERMINAL` is True,
           or to `_gui_console_stdout_redirector` (GUI console) if available.
        6. Falls back to `_original_stdout` if the GUI console is not ready and not debugging to terminal.

    Outputs of this function:
        None. Prints a message to the console or terminal.
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
    
    if DEBUG_TO_TERMINAL:
        # Print to original stdout (terminal)
        print(full_message, file=_original_stdout)
    elif _gui_console_stdout_redirector:
        # Print to GUI console via its redirector
        _gui_console_stdout_redirector.write(full_message + "\n")
    else:
        # Fallback to original stdout if GUI console not ready
        print(full_message, file=_original_stdout)


def log_visa_command(command, direction="SENT"):
    """
    Function Description:
    Logs VISA commands sent to or received from the instrument if LOG_VISA_COMMANDS is enabled.
    Output location (GUI console or terminal) is controlled by DEBUG_TO_TERMINAL.

    Inputs:
        command (str): The VISA command string.
        direction (str, optional): "SENT" or "RECEIVED". Defaults to "SENT".

    Process of this function:
        1. Checks if `LOG_VISA_COMMANDS` is enabled. If not, exits early.
        2. Generates a timestamp.
        3. Formats the log message.
        4. Directs the message to `_original_stdout` (terminal) if `DEBUG_TO_TERMINAL` is True,
           or to `_gui_console_stdout_redirector` (GUI console) if available.
        5. Falls back to `_original_stdout` if the GUI console is not ready and not debugging to terminal.

    Outputs of this function:
        None. Prints a message to the console or terminal.
    """
    if not LOG_VISA_COMMANDS:
        return

    timestamp = datetime.now().strftime("%M.%S")
    log_message = f"🌲 [{timestamp}] {direction}: {command.strip()}"
    
    if DEBUG_TO_TERMINAL:
        # Print to original stdout (terminal)
        print(log_message, file=_original_stdout)
    elif _gui_console_stdout_redirector:
        # Print to GUI console via its redirector
        _gui_console_stdout_redirector.write(log_message + "\n")
    else:
        # Fallback to original stdout if GUI console not ready
        print(log_message, file=_original_stdout)
