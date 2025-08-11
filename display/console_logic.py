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
# Version 20250811.002800.1 (FIXED: Removed circular dependency with debug_logic by using a global function reference instead of a direct import.)

current_version = "20250811.002800.1"
current_version_hash = 20250811 * 2800 * 1

import sys
from datetime import datetime
import inspect
import tkinter as tk

# NEW: Global references to debug_logic components, to be set by debug_logic
# These are internal to console_logic and will be set by external calls.
_gui_console_stdout_redirector = None
_original_stdout = sys.stdout # Keep a reference to original stdout for fallback

_debug_file_include_flag_ref = None # Will hold the callable for INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE
_debug_file_write_func_ref = None    # Will hold the reference to _write_to_debug_file
_clear_console_func_ref = None       # Will hold the reference to the actual clear console function

def set_gui_console_redirector(stdout_redirector, stderr_redirector):
    """
    Function Description:
    Sets the TextRedirector instances for the GUI console for console messages.
    This function now directly sets the internal `_gui_console_stdout_redirector`.
    It does NOT call `debug_logic.set_debug_redirectors` to avoid circular import
    issues. The `debug_logic` module will call its own `set_debug_redirectors`.

    Inputs to this function:
    - stdout_redirector (gui_elements.TextRedirector): An instance of TextRedirector
                                                       that will redirect stdout to a Tkinter widget.
    - stderr_redirector (gui_elements.TextRedirector): An instance of TextRedirector
                                                       that will redirect stderr to a Tkinter widget.

    Process of this function:
    1. Sets the internal `_gui_console_stdout_redirector`.
    2. Logs the action (using `console_log` itself, which is safe after this setup).

    Outputs of this function:
    - None. Modifies global variables.
    """
    global _gui_console_stdout_redirector
    _gui_console_stdout_redirector = stdout_redirector
    current_function = inspect.currentframe().f_code.co_name
    # Now that _gui_console_stdout_redirector is set, console_log can write to GUI
    console_log(f"Console output redirected to GUI. Version: {current_version}", function=current_function)


def set_debug_file_hooks(include_flag_callable, write_func):
    """
    Registers the debug file logging flag callable and write function from debug_logic.
    This is called by main_app to break the circular import dependency.

    Args:
        include_flag_callable (callable): A callable (e.g., lambda) that returns the
                                          current boolean state of INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE
                                          from debug_logic.
        write_func (callable): The _write_to_debug_file function from debug_logic.
    """
    global _debug_file_include_flag_ref, _debug_file_write_func_ref
    _debug_file_include_flag_ref = include_flag_callable
    _debug_file_write_func_ref = write_func
    current_function = inspect.currentframe().f_code.co_name
    # Avoid logging here to prevent potential recursion if console_log is called during setup
    # console_log(f"Debug file hooks registered with console_logic. Breaking the circular import!",
    #             function=current_function)

def set_clear_console_func(clear_func):
    """
    Function Description:
    Registers the actual function that clears the GUI console.
    This is called by ConsoleTab to provide the console clearing capability.

    Inputs to this function:
    - clear_func (callable): A callable function (e.g., ConsoleTab's _clear_applications_console_action)
                             that will clear the content of the GUI console.

    Process of this function:
    1. Sets the global `_clear_console_func_ref` to the provided `clear_func`.

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
    This serves as the public interface for clearing the console from other modules.

    Inputs to this function:
    - None.

    Process of this function:
    1. Checks if `_clear_console_func_ref` is set.
    2. If set, calls the registered function to clear the console.
    3. If not set, logs a debug message indicating that the clear function is unavailable.

    Outputs of this function:
    - None. Triggers the console clear action.
    """
    current_function = inspect.currentframe().f_code.co_name
    if _clear_console_func_ref:
        _clear_console_func_ref()
    else:
        # Fallback to original stdout if GUI console is not set up yet
        _original_stdout.write(f"DEBUG: [{current_function}] Cannot clear console, function not registered yet. Fucking useless!\n")


def console_log(message, function=None):
    """
    Function Description:
    Prints a general application message to the console.
    This function always attempts to print to the GUI console if it's available.
    If the GUI console redirector is not yet set, it falls back to printing to the
    original standard output (terminal).
    Additionally, if INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE is enabled (via its callable),
    it writes the message to the debug log file.

    Inputs:
        message (str): The message to print.
        function (str, optional): The name of the function sending the message. Defaults to None.

    Process of this function:
        1. Generates a timestamp for the message.
        2. Constructs a prefix including the function name if provided.
        3. Formats the full message with an emoji and timestamp.
        4. If the shared `_gui_console_stdout_redirector` is set, writes the message to it,
           temporarily enabling the Text widget state.
        5. Otherwise, prints the message to the shared `_original_stdout`.
        6. If `_debug_file_include_flag_ref` is True and `_debug_file_write_func_ref` is available,
           writes the message to the debug file using the registered function.

    Outputs of this function:
        None. Prints a message to the console or terminal, and/or writes to a file.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    prefix_parts = []
    if function:
        prefix_parts.append(function)

    prefix = f"[{' | '.join(prefix_parts)}] " if prefix_parts else ""


    #full_message = f"💬 [{timestamp}] {prefix}{message}"

    full_message = f"{message}"
    
    # Use the shared _gui_console_stdout_redirector
    if _gui_console_stdout_redirector:
        # Enable the text widget state temporarily to write
        # This assumes _gui_console_stdout_redirector.text_widget is the ScrolledText
        text_widget = _gui_console_stdout_redirector.widget # Use .widget as per TextRedirector class
        original_state = text_widget.cget("state")
        text_widget.config(state=tk.NORMAL)
        _gui_console_stdout_redirector.write(full_message + "\n")
        text_widget.config(state=original_state)
    else:
        # Fallback to the shared _original_stdout
        _original_stdout.write(full_message + "\n")

    # Output to debug file if enabled
    # Use the registered callable for the flag and the registered write function
    if _debug_file_include_flag_ref and _debug_file_include_flag_ref() and _debug_file_write_func_ref:
        _debug_file_write_func_ref(full_message)
