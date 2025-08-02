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
# Version 20250802.0075.2 (Centralized stdout redirection via debug_logic.)

current_version = "20250802.0075.2" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 75 * 2 # Example hash, adjust as needed

import sys
from datetime import datetime
import inspect # Import inspect for debug_log

# Import debug_log, the shared redirectors, and new file logging functions/flags from src.debug_logic
from src.debug_logic import debug_log, INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE, _write_to_debug_file
# NEW: Import the global redirectors and their setter from debug_logic
from src.debug_logic import _gui_console_stdout_redirector, _original_stdout, set_debug_redirectors


# Removed: _gui_console_stdout_redirector = None
# Removed: _original_stdout = sys.stdout # Keep a reference to original stdout for fallback


def set_gui_console_redirector(stdout_redirector, stderr_redirector):
    """
    Function Description:
    Sets the TextRedirector instances for the GUI console for general application messages.
    This function now delegates the actual redirection to `debug_logic.set_debug_redirectors`,
    ensuring a single, centralized point for managing stdout/stderr redirection to the GUI.

    Inputs to this function:
    - stdout_redirector (gui_elements.TextRedirector): An instance of TextRedirector
                                                       that will redirect stdout to a Tkinter widget.
    - stderr_redirector (gui_elements.TextRedirector): An instance of TextRedirector
                                                       that will redirect stderr to a Tkinter widget.

    Process of this function:
    1. Calls `set_debug_redirectors` from `debug_logic` to set the global redirectors.
    2. Logs the action using `debug_log`.

    Outputs of this function:
    - None. Modifies global variables in `debug_logic`.
    """
    current_function = inspect.currentframe().f_code.co_name
    # Delegate the actual setting of global redirectors to debug_logic
    set_debug_redirectors(stdout_redirector, stderr_redirector)
    debug_log(f"GUI console redirector set via debug_logic. All messages will now flow to the GUI! Version: {current_version}",
                file=__file__,
                version=current_version,
                function=current_function)


def console_log(message, function=None):
    """
    Function Description:
    Prints a general application message to the GUI console.
    This function always attempts to print to the GUI console if the shared redirector is available.
    If the GUI console redirector is not yet set, it falls back to printing to the
    original standard output (terminal).
    Additionally, if INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE is enabled,
    it writes the message to the debug log file.

    Inputs:
        message (str): The message to print.
        function (str, optional): The name of the function sending the message. Defaults to None.

    Process of this function:
        1. Generates a timestamp for the message.
        2. Constructs a prefix including the function name if provided.
        3. Formats the full message with an emoji and timestamp.
        4. If the shared `_gui_console_stdout_redirector` (from `debug_logic`) is set, writes the message to it.
        5. Otherwise, prints the message to the shared `_original_stdout` (from `debug_logic`).
        6. If `INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE` is True, writes the message to the debug file.

    Outputs of this function:
        None. Prints a message to the console or terminal, and/or writes to a file.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    prefix_parts = []
    if function:
        prefix_parts.append(function)

    prefix = f"[{' | '.join(prefix_parts)}] " if prefix_parts else ""

    full_message = f"💬 [{timestamp}] {prefix}{message}"
    
    # Use the shared _gui_console_stdout_redirector from debug_logic
    if _gui_console_stdout_redirector:
        _gui_console_stdout_redirector.write(full_message + "\n")
    else:
        # Fallback to the shared _original_stdout from debug_logic
        _original_stdout.write(full_message + "\n")

    # Output to debug file if enabled
    if INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE:
        _write_to_debug_file(full_message)

