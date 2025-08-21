# src/console_logic.py
#
# This module centralizes general application console logging functionality.
# It provides a function to print general application messages, which always
# attempt to go to the GUI console if available.
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
# Version 20250814.230000.1 (FIXED: The console_log function now correctly filters the message emoji from the on-screen console output but includes it in the debug file.)

current_version = "20250814.230000.1"
current_version_hash = 20250814 * 230000 * 1

import sys
from datetime import datetime
import inspect
import tkinter as tk
import re

# NEW: Global references to debug_logic components, to be set by debug_logic
_gui_console_stdout_redirector = None
_original_stdout = sys.stdout # Keep a reference to original stdout for fallback

_debug_file_include_flag_ref = None
_debug_file_write_func_ref = None
_clear_console_func_ref = None
_log_truncation_mode_ref = None


def set_gui_console_redirector(stdout_redirector, stderr_redirector):
    """
    Function Description:
    Sets the TextRedirector instances for the GUI console for console messages.

    Inputs to this function:
    - stdout_redirector (gui_elements.TextRedirector): An instance of TextRedirector
                                                       that will redirect stdout to a Tkinter widget.
    - stderr_redirector (gui_elements.TextRedirector): An instance of TextRedirector
                                                       that will redirect stderr to a Tkinter widget.

    Outputs of this function:
    - None. Modifies global variables.
    """
    global _gui_console_stdout_redirector
    _gui_console_stdout_redirector = stdout_redirector
    current_function = inspect.currentframe().f_code.co_name
    console_log(f"Console output redirected to GUI. Version: {current_version}", function=current_function)


def set_debug_file_hooks(include_flag_callable, write_func):
    """
    Registers the debug file logging flag callable and write function from debug_logic.

    Args:
        include_flag_callable (callable): A callable (e.g., lambda) that returns the
                                          current boolean state of INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE
                                          from debug_logic.
        write_func (callable): The _write_to_debug_file function from debug_logic.
    """
    global _debug_file_include_flag_ref, _debug_file_write_func_ref
    _debug_file_include_flag_ref = include_flag_callable
    _debug_file_write_func_ref = write_func

def set_log_truncation_mode_ref(mode_callable):
    """Registers the callable for the log truncation mode."""
    global _log_truncation_mode_ref
    _log_truncation_mode_ref = mode_callable


def set_clear_console_func(clear_func):
    """
    Function Description:
    Registers the actual function that clears the GUI console.

    Inputs to this function:
    - clear_func (callable): A callable function (e.g., ConsoleTab's _clear_applications_console_action)
                             that will clear the content of the GUI console.

    Outputs of this function:
    - None. Modifies a global variable.
    """
    global _clear_console_func_ref
    _clear_console_func_ref = clear_func
    current_function = inspect.currentframe().f_code.co_name
    console_log(f"Clear console function registered. Version: {current_version}", function=current_function)


def clear_console():
    """
    Function Description:
    Calls the registered function to clear the GUI console.

    Inputs to this function:
    - None.

    Outputs of this function:
    - None. Triggers the console clear action.
    """
    current_function = inspect.currentframe().f_code.co_name
    if _clear_console_func_ref:
        _clear_console_func_ref()
    else:
        _original_stdout.write(f"DEBUG: [{current_function}] Cannot clear console, function not registered yet. Fucking useless!\n")


def console_log(message, function=None):
    """
    Function Description:
    Prints a general application message to the console.

    Inputs:
        message (str): The message to print.
        function (str, optional): The name of the function sending the message. Defaults to None.

    Outputs of this function:
        None. Prints a message to the console or terminal, and/or writes to a file.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    prefix_parts = []
    if function:
        prefix_parts.append(function)

    prefix = f"[{' | '.join(prefix_parts)}] " if prefix_parts else ""

    # Generate message for debug file (with emoji)
    full_message_with_emoji = f"💬[{timestamp}] {prefix}{_truncate_message(message)}"
    
    # Generate message for console (without emoji)
    console_message = f"{prefix}{_truncate_message(message)}"

    if _gui_console_stdout_redirector:
        text_widget = _gui_console_stdout_redirector.widget
        original_state = text_widget.cget("state")
        text_widget.config(state=tk.NORMAL)
        _gui_console_stdout_redirector.write(console_message + "\n")
        text_widget.config(state=original_state)
    else:
        _original_stdout.write(console_message + "\n")

    if _debug_file_include_flag_ref and _debug_file_include_flag_ref() and _debug_file_write_func_ref:
        _debug_file_write_func_ref(full_message_with_emoji)

def _truncate_message(message: str, max_items=10) -> str:
    """Helper function to truncate long, comma-separated numeric strings."""
    numeric_pattern = re.compile(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?')
    matches = numeric_pattern.findall(message)
    if len(matches) > max_items:
        truncated_parts = matches[:max_items]
        return f"{', '.join(truncated_parts)}... (truncated)"
    return message
