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
# Feature Request can be emailed to i @ like . audio
#
#
# Version 20250801.2100.1 (Refactored debug_print to debug_log with expanded parameters.)

import sys
import os
from datetime import datetime

# Global variables for debug control
DEBUG_MODE = False
LOG_VISA_COMMANDS = False
DEBUG_TO_TERMINAL = False # Controls where debug_log output goes (True: terminal, False: GUI console)

# Reference to the GUI console TextRedirector or original stdout/stderr
_gui_console_stdout_redirector = None
_gui_console_stderr_redirector = None
_original_stdout = sys.stdout
_original_stderr = sys.stderr

def set_debug_mode(mode):
    """
    Sets the global debug mode flag. When DEBUG_MODE is True,
    debug messages are processed.
    """
    global DEBUG_MODE
    DEBUG_MODE = mode

def set_log_visa_commands_mode(mode):
    """
    Sets the global VISA command logging flag. When True,
    all VISA commands sent and received are processed.
    """
    global LOG_VISA_COMMANDS
    LOG_VISA_COMMANDS = mode

def set_debug_to_terminal_mode(mode):
    """
    Sets the global flag for directing debug output.
    If True, debug_log sends to terminal. If False, debug_log sends to GUI console.
    """
    global DEBUG_TO_TERMINAL
    DEBUG_TO_TERMINAL = mode
    # When this mode changes, re-apply the stdout/stderr redirection
    _apply_stdout_redirection()


def set_gui_console_redirector(stdout_redirector, stderr_redirector):
    """
    Sets the TextRedirector instances for the GUI console.
    This should be called by the main application once the GUI console is ready.
    """
    global _gui_console_stdout_redirector, _gui_console_stderr_redirector
    _gui_console_stdout_redirector = stdout_redirector
    _gui_console_stderr_redirector = stderr_redirector
    _apply_stdout_redirection() # Apply redirection immediately after setting


def _apply_stdout_redirection():
    """
    Applies or removes stdout/stderr redirection based on DEBUG_TO_TERMINAL.
    This function is internal to debug_logic.
    """
    if DEBUG_TO_TERMINAL:
        # If debug is to terminal, ensure original stdout/stderr are used for Python's print()
        sys.stdout = _original_stdout
        sys.stderr = _original_stderr
        # console_log will still go to GUI if _gui_console_stdout_redirector is set
    else:
        # If debug is to GUI, redirect Python's print() to GUI console
        if _gui_console_stdout_redirector:
            sys.stdout = _gui_console_stdout_redirector
        if _gui_console_stderr_redirector:
            sys.stderr = _gui_console_stderr_redirector


def debug_log(message, file=None, version=None, function=None, special=False):
    """
    Prints a debug message if DEBUG_MODE is enabled.
    Output location (GUI console or terminal) is controlled by DEBUG_TO_TERMINAL.
    Includes file name, version, function context, and a 'special' flag for better traceability.

    Args:
        message (str): The debug message to print.
        file (str, optional): The name of the file sending the debug message (e.g., __file__).
        version (str, optional): The version of the file sending the debug message.
        function (str, optional): The name of the function sending the debug message.
        special (bool, optional): A flag to mark special debug messages. Defaults to False.
    """
    if DEBUG_MODE:
        timestamp = datetime.now().strftime("%M.%S")
        prefix_parts = []

        if file:
            prefix_parts.append(os.path.basename(file))
        if version:
            prefix_parts.append(f"Ver:{version}")
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
    Logs VISA commands sent to or received from the instrument if LOG_VISA_COMMANDS is enabled.
    Output location (GUI console or terminal) is controlled by DEBUG_TO_TERMINAL.
    """
    if LOG_VISA_COMMANDS:
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

