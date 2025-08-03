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
# Version 20250802.0152.1 (Refined debug_log and console_log interaction, clarified DEBUG_MODE logic.)
# Version 20250802.1935.0 (Added DEBUG_TO_GUI_CONSOLE flag and logic to control debug output to GUI console.)
# Version 20250802.1940.0 (Ensured debug_log respects DEBUG_TO_GUI_CONSOLE flag for output to GUI.)
# Version 20250803.1535.0 (Added set_log_visa_command_func to resolve ImportError in program_initialization.py)

current_version = "20250803.1535.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 1535 * 0 # Example hash, adjust as needed

import sys
import os
from datetime import datetime
import inspect # Import inspect for function name

# REMOVED: from src.console_logic import console_log - This caused the circular import!

# Global variables for debug control
DEBUG_MODE = False # Master switch: Controls if debug_log messages are processed at all
LOG_VISA_COMMANDS = False # Controls if VISA commands are logged (only if DEBUG_MODE is True)
DEBUG_TO_TERMINAL = False # Controls where debug_log output goes (True: terminal, False: GUI console)
DEBUG_TO_FILE = False # Controls if debug_log output goes to a file
INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE = False # Controls if console_log messages also go to debug file
DEBUG_TO_GUI_CONSOLE = False # NEW: Controls if debug_log messages go to the GUI console
DEBUG_FILE_PATH = None # Path to the debug log file

# Reference to the GUI console TextRedirector or original stdout/stderr
_gui_console_stdout_redirector = None
_gui_console_stderr_redirector = None
_original_stdout = sys.stdout
_original_stderr = sys.stderr

# NEW: Global variable to hold reference to console_log function from console_logic
_console_log_func_ref = None

# NEW: Global variable to hold reference to the log_visa_command function for external registration
_log_visa_command_func_ref = None


def set_debug_mode(mode: bool):
    """
    Function Description:
    Sets the global DEBUG_MODE flag. This is the master switch for all debug_log messages.

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
    # Use _console_log_func_ref if available, otherwise fallback to print
    if _console_log_func_ref:
        _console_log_func_ref(f"Debug Mode: {'Enabled' if DEBUG_MODE else 'Disabled'}", function=current_function)
    else:
        print(f"DEBUG_MODE set to: {DEBUG_MODE}. (console_log not yet registered)", file=_original_stdout)
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
    if _console_log_func_ref:
        _console_log_func_ref(f"VISA Command Logging: {'Enabled' if LOG_VISA_COMMANDS else 'Disabled'}", function=current_function)
    else:
        print(f"LOG_VISA_COMMANDS set to: {LOG_VISA_COMMANDS}. (console_log not yet registered)", file=_original_stdout)
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
    if _console_log_func_ref:
        _console_log_func_ref(f"Debug to Terminal: {'Enabled' if DEBUG_TO_TERMINAL else 'Disabled'}", function=current_function)
    else:
        print(f"DEBUG_TO_TERMINAL set to: {DEBUG_TO_TERMINAL}. (console_log not yet registered)", file=_original_stdout)
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
            if _console_log_func_ref:
                _console_log_func_ref(f"Debug to File: Enabled. Output will be saved to: {DEBUG_FILE_PATH}", function=current_function)
            else:
                print(f"Debug logging to file enabled. Output will be saved to: {DEBUG_FILE_PATH}. (console_log not yet registered)", file=_original_stdout)
            debug_log(f"Debug logging to file enabled. Output will be saved to: {DEBUG_FILE_PATH}. Overwriting previous log!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except Exception as e:
            DEBUG_TO_FILE = False # Disable if file opening fails
            if _console_log_func_ref:
                _console_log_func_ref(f"ERROR: Could not open debug log file at {DEBUG_FILE_PATH}: {e}. Debug logging to file disabled.", function=current_function)
            else:
                print(f"ERROR: Could not open debug log file at {DEBUG_FILE_PATH}: {e}. Debug logging to file disabled. (console_log not yet registered)", file=_original_stderr)
            debug_log(f"ERROR: Could not open debug log file at {DEBUG_FILE_PATH}: {e}. Debug logging to file disabled. This is a disaster!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
    else:
        if _console_log_func_ref:
            _console_log_func_ref(f"Debug to File: Disabled.", function=current_function)
        else:
            print(f"Debug logging to file disabled. (console_log not yet registered)", file=_original_stdout)
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
    if _console_log_func_ref:
        _console_log_func_ref(f"Include Console Messages to Debug File: {'Enabled' if INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE else 'Disabled'}", function=current_function)
    else:
        print(f"INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE set to: {INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE}. (console_log not yet registered)", file=_original_stdout)
    debug_log(f"Including console messages in debug file set to: {INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE}.",
                file=__file__,
                version=current_version,
                function=current_function)


def set_debug_to_gui_console_mode(mode: bool):
    """
    Function Description:
    Sets the global DEBUG_TO_GUI_CONSOLE flag.

    Inputs:
    - mode (bool): True to enable debug_log messages to the GUI console, False to disable.

    Process of this function:
    1. Updates the global `DEBUG_TO_GUI_CONSOLE` variable.
    2. Prints a debug message indicating the new state.

    Outputs of this function:
    - None. Modifies a global variable.
    """
    global DEBUG_TO_GUI_CONSOLE
    DEBUG_TO_GUI_CONSOLE = mode
    current_function = inspect.currentframe().f_code.co_name
    if _console_log_func_ref:
        _console_log_func_ref(f"Debug to GUI Console: {'Enabled' if DEBUG_TO_GUI_CONSOLE else 'Disabled'}", function=current_function)
    else:
        print(f"DEBUG_TO_GUI_CONSOLE set to: {DEBUG_TO_GUI_CONSOLE}. (console_log not yet registered)", file=_original_stdout)
    debug_log(f"Debug logging to GUI console set to: {DEBUG_TO_GUI_CONSOLE}.",
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

# NEW: Function to register console_log with debug_logic
def set_console_log_func(func):
    """
    Registers the console_log function from console_logic with debug_logic.
    This breaks the circular import dependency.
    """
    global _console_log_func_ref
    _console_log_func_ref = func
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Console log function registered with debug_logic. Breaking the circular import!",
                file=__file__,
                version=current_version,
                function=current_function,
                special=True)

# NEW: Function to register log_visa_command with debug_logic (for external modules to reference)
def set_log_visa_command_func(func):
    """
    Registers the log_visa_command function from debug_logic.
    This allows other modules to get a reference to the log_visa_command function
    if needed, effectively making it available for external use without direct import
    if a circular dependency arises.
    """
    global _log_visa_command_func_ref
    _log_visa_command_func_ref = func
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Log VISA command function registered with debug_logic. Ready to track commands!",
                file=__file__,
                version=current_version,
                function=current_function,
                special=True)


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

def clear_debug_log_file(file_path: str):
    """
    Function Description:
    Clears the content of the debug log file.

    Inputs:
    - file_path (str): The full path to the debug log file.

    Process of this function:
    1. Checks if the file exists.
    2. If it exists, opens the file in 'w' mode (write, truncating to zero length)
       and writes a header indicating the log was cleared.
    3. Prints a message to the console and debug log.

    Outputs of this function:
    - None. Clears the content of the specified file.
    """
    current_function = inspect.currentframe().f_code.co_name
    if os.path.exists(file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"--- Debug Log Cleared: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            # Use the registered console_log function
            if _console_log_func_ref:
                _console_log_func_ref(f"✅ Debug log file cleared: {file_path}", function=current_function)
            else:
                print(f"✅ Debug log file cleared: {file_path}", file=_original_stdout) # Fallback if not registered
            debug_log(f"Debug log file cleared.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except Exception as e:
            # Use the registered console_log function
            if _console_log_func_ref:
                _console_log_func_ref(f"❌ Error clearing debug log file {file_path}: {e}", function=current_function)
            else:
                print(f"❌ Error clearing debug log file {file_path}: {e}", file=_original_stderr) # Fallback
            debug_log(f"ERROR: Failed to clear debug log file: {e}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
    else:
        # Use the registered console_log function
        if _console_log_func_ref:
            _console_log_func_ref(f"ℹ️ Debug log file does not exist: {file_path}. Nothing to clear.", function=current_function)
        else:
            print(f"ℹ️ Debug log file does not exist: {file_path}. Nothing to clear.", file=_original_stdout) # Fallback
        debug_log(f"Debug log file does not exist. Cannot clear.",
                    file=__file__,
                    version=current_version,
                    function=current_function)


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
    # Output to GUI console (only if not debugging to terminal AND DEBUG_TO_GUI_CONSOLE is True)
    elif _gui_console_stdout_redirector and DEBUG_TO_GUI_CONSOLE: # Added DEBUG_TO_GUI_CONSOLE check
        _gui_console_stdout_redirector.write(full_message + "\n")
    # Fallback to original stdout if GUI console not ready/enabled and not debugging to terminal
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
    # Output to GUI console (only if not debugging to terminal AND DEBUG_TO_GUI_CONSOLE is True)
    elif _gui_console_stdout_redirector and DEBUG_TO_GUI_CONSOLE: # Added DEBUG_TO_GUI_CONSOLE check
        _gui_console_stdout_redirector.write(log_message + "\n")
    # Fallback to original stdout if GUI console not ready/enabled and not debugging to terminal
    else:
        print(log_message, file=_original_stdout)

    # Output to debug file
    if DEBUG_TO_FILE:
        _write_to_debug_file(log_message)
