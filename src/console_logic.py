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
# Feature Request can be emailed to i @ like . audio
#
#
# Version 20250801.2135.1 (Added optional 'function' parameter to console_log.)

import sys
from datetime import datetime


# Reference to the GUI console TextRedirector or original stdout/stderr
# These are specifically for console_log output
_gui_console_stdout_redirector = None
_original_stdout = sys.stdout # Keep a reference to original stdout for fallback


def set_console_redirector(stdout_redirector):
    """
    Sets the TextRedirector instance for the GUI console for general application messages.
    This should be called by the main application once the GUI console is ready.
    """
    global _gui_console_stdout_redirector
    _gui_console_stdout_redirector = stdout_redirector


def console_log(message, function=None):
    """
    Prints a general application message to the GUI console.
    This function always attempts to print to the GUI console if it's available.

    Args:
        message (str): The message to print.
        function (str, optional): The name of the function sending the message. Defaults to None.
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
        # Fallback to original stdout (terminal) if GUI console not ready
        print(full_message, file=_original_stdout)
