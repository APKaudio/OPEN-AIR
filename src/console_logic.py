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
# Version 20250802.0015.1 (Refactored debug_print to use debug_log; added flair.)

current_version = "20250802.0015.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 15 * 1 # Example hash, adjust as needed

import sys
from datetime import datetime
import inspect # Import inspect for debug_log

# Import debug_log (assuming it's in src.debug_logic)
from src.debug_logic import debug_log


# Reference to the GUI console TextRedirector or original stdout/stderr
# These are specifically for console_log output
_gui_console_stdout_redirector = None
_original_stdout = sys.stdout # Keep a reference to original stdout for fallback


def set_console_redirector(stdout_redirector):
    """
    Function Description:
    Sets the TextRedirector instance for the GUI console for general application messages.
    This should be called by the main application once the GUI console is ready.

    Inputs to this function:
    - stdout_redirector (gui_elements.TextRedirector): An instance of TextRedirector
                                                       that will redirect stdout to a Tkinter widget.

    Process of this function:
    1. Assigns the provided `stdout_redirector` to the global `_gui_console_stdout_redirector`.
    2. Logs the action using `debug_log`.

    Outputs of this function:
    - None. Modifies a global variable.
    """
    global _gui_console_stdout_redirector
    _gui_console_stdout_redirector = stdout_redirector
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"GUI console redirector set. All messages will now flow to the GUI! Version: {current_version}",
                file=__file__,
                version=current_version,
                function=current_function)


def console_log(message, function=None):
    """
    Function Description:
    Prints a general application message to the GUI console.
    This function always attempts to print to the GUI console if it's available.
    If the GUI console redirector is not yet set, it falls back to printing to the
    original standard output (terminal).

    Inputs:
        message (str): The message to print.
        function (str, optional): The name of the function sending the message. Defaults to None.

    Process of this function:
        1. Generates a timestamp for the message.
        2. Constructs a prefix including the function name if provided.
        3. Formats the full message with an emoji and timestamp.
        4. If `_gui_console_stdout_redirector` is set, writes the message to it.
        5. Otherwise, prints the message to the original `sys.stdout` (terminal).

    Outputs of this function:
        None. Prints a message to the console or terminal.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    prefix_parts = []
    if function:
        prefix_parts.append(function)

    prefix = f"[{' | '.join(prefix_parts)}] " if prefix_parts else ""

    full_message = f"💬 [{timestamp}] {prefix}{message}"
    if _gui_console_stdout_redirector:
        _gui_console_stdout_redirector.write(full_message + "\n")
    else:
        # Fallback to original stdout if GUI console not ready
        _original_stdout.write(full_message + "\n")
