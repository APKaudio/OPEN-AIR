# src/gui_elements.py
#
# This module defines common GUI elements and utilities, such as a TextRedirector
# for routing stdout/stderr to a Tkinter scrolled text widget, and the application's
# splash screen.
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
# Version 20250802.0025.1 (Refactored debug_print to debug_log; added flair.)

current_version = "20250802.0025.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 25 * 1 # Example hash, adjust as needed

import tkinter as tk
import sys
from tkinter import scrolledtext, TclError
import inspect # Added for debug_log

# Import the debug logic module to use debug_log
from src.debug_logic import debug_log # Changed from debug_print


class TextRedirector(object):
    """
    Function Description:
    A class to redirect standard output (stdout) and standard error (stderr)
    to a Tkinter scrolled text widget. This allows all print statements and
    error messages from the application's backend to be displayed directly
    within the GUI's console area, providing real-time feedback to the user.

    Inputs to this function:
    - widget (tk.scrolledtext.ScrolledText): The Tkinter scrolled text widget
                                              where output will be displayed.
    - tag (str, optional): A tag for text formatting within the widget. Defaults to "stdout".

    Process of this function:
    1. Stores the provided `widget` and `tag`.
    2. Initializes a `_buffer` to temporarily hold text before updating the widget.
    3. Sets a `_last_flush_time` to control the frequency of widget updates.

    Outputs of this function:
    - None. Initializes the TextRedirector object.
    """
    def __init__(self, widget, tag="stdout"):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing TextRedirector for tag '{tag}'. Setting up console redirection! Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        self.widget = widget
        self.tag = tag
        self._buffer = ""
        self._last_flush_time = 0

    def write(self, text):
        """
        Function Description:
        Writes text to the redirected widget. Text is buffered and flushed periodically
        to improve performance and prevent GUI freezing.

        Inputs:
        - text (str): The text string to write.

        Process of this function:
        1. Appends the input `text` to an internal buffer.
        2. Checks if enough time has passed since the last flush (0.1 seconds)
           or if the buffer size exceeds a threshold (1000 characters).
        3. If a flush is needed, inserts the buffered text into the widget,
           applies the specified tag, scrolls to the end, and clears the buffer.
        4. Handles `TclError` in case the widget is destroyed.

        Outputs of this function:
        - None. Modifies the Tkinter widget.
        """
        self._buffer += text
        # Flush every 0.1 seconds or if buffer is too large
        current_time = time.time() # Assuming time module is imported or available
        if current_time - self._last_flush_time > 0.1 or len(self._buffer) > 1000:
            self.flush()

    def flush(self):
        """
        Function Description:
        Flushes the buffered text to the Tkinter widget.

        Inputs:
        - None.

        Process of this function:
        1. If the buffer is not empty, attempts to insert its content into the widget.
        2. Applies the configured text tag.
        3. Scrolls the widget to the end to show the latest messages.
        4. Clears the buffer and updates the `_last_flush_time`.
        5. Handles `TclError` if the widget has been destroyed, preventing crashes.

        Outputs of this function:
        - None. Modifies the Tkinter widget.
        """
        if self._buffer:
            try:
                self.widget.insert(tk.END, self._buffer, (self.tag,))
                self.widget.see(tk.END)
                self._buffer = ""
                self._last_flush_time = time.time() # Assuming time module is imported or available
            except TclError:
                # Widget has been destroyed, stop writing
                pass

def display_splash_screen():
    """
    Function Description:
    Prints a stylized ASCII art splash screen to the terminal.
    This function is intended for initial application startup feedback
    before the full GUI is loaded.

    Inputs:
    - None.

    Process of this function:
    1. Prints several lines of ASCII art and application information.
    2. Includes author and blog details.

    Outputs of this function:
    - None. Prints directly to standard output.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Displaying splash screen. Welcome to the Spectrum Scanner! Version: {current_version}",
                file=__file__,
                version=current_version,
                function=current_function,
                special=True) # Adding special flag for splash screen

    ###https://patorjk.com/software/taag/#p=display&h=3&v=2&f=BlurVision%20ASCII&t=OPEN%20AIR%0A
    # Reverting to default print() behavior, letting it add newlines.
    # TextRedirector will now insert these newlines directly.
    print("") # First blank line
    print("") # Second blank line
    print("") # Third blank line
    print(" ░▒▓██████▓▒░ ░▒▓███████▓▒░ ░▒▓████████▓▒ ░▒▓███████▓▒░        ░▒▓██████▓▒░ ░▒▓█▓▒░ ▒▓███████▓▒░  ")
    print("░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░       ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░ ▒▓█▓▒░░▒▓█▓▒░ ")
    print("░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░       ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░ ▒▓█▓▒░░▒▓█▓▒░ ")
    print("░▒▓█▓▒░░▒▓█▓▒ ░▒▓███████▓▒░ ░▒▓██████▓▒░  ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓████████▓▒ ░▒▓█▓▒░ ▒▓███████▓▒░  ")
    print("░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░       ░▒▓█▓▒░       ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░ ▒▓█▓▒░░▒▓█▓▒░ ")
    print("░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░       ░▒▓█▓▒░       ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░ ▒▓█▓▒░░▒▓█▓▒░ ")
    print(" ░▒▓██████▓▒░ ░▒▓█▓▒░       ░▒▓████████▓▒ ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░ ▒▓█▓▒░░▒▓█▓▒░ ")
                                                                                             

    print("") # First blank line
    print("") # Second blank line
    print("") # Third blank line

    print("                                               #              #####                     ## ####")
    print("                                               ###            ##   ######               ##  ## ")
    print("                                               ####           ##         #####          ## ##  ")
    print("                                  ##           ## ##          ##             #####      ####   ")
    print("                       ############            ##  ###        #                  ###    ####   ")
    print("             #########        ###              ##   ###      ##                    ##   ###    ")
    print("   #########               ###                 ##     ##     ##                ####     ##     ")
    print("                         ###                   ###########   ##          ######         ##     ")
    print("                       ###                     ##       ###  #  ########                #      ")
    print("                     ###                       ##         #####                                ")
    print("                   ###                         ##           ##                        # ##     ")
    print("                 ###                #######                 ##                        ###      ")
    print("              ####            ######                        ##                  ##########     ")
    print("            ###        #######                                   ##############                ")
    print("          ###   #######                             ###########                                ")
    print("        ########                  ########             ####                                    ")
    print("      ###              ##########  ####              ########                                  ")
    print("           ###########          ###         ########                                           ")
    print(" ##########                  ###    ########                                                   ")
    print("                         ##########                                                            ")
    print("                      #####                        ")
    print("") # Blank line
    print("") # Blank line
    print("") # Blank line
    print("A Colaboration betweeen Ike Zimbel and Anthony P. Kuzub")
    print("") # Blank line
    print("https://zimbelaudio.com/ike-zimbel/    ")
    print("https://www.like.audio/")
    print("") # Blank line

    print("") # Blank line



