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
#
# Version 20250803.2215.0 (REFACTORED: Removed all parent tab imports to finally kill the circular dependency.)
# Version 20250803.0147.1 (Added call to clear_console before each ASCII art display.)

current_version = "20250803.2215.0"

import tkinter as tk
import sys
import time
from tkinter import scrolledtext, TclError
import inspect

from src.debug_logic import debug_log
from src.console_logic import console_log, clear_console

#
# REMOVED ALL 'from tabs... import TAB_..._PARENT' LINES.
# This file is a low-level utility and must not import high-level UI components.
# This was the source of the circular import error.
#

class TextRedirector(object):
    """
    A class to redirect stdout/stderr to a Tkinter scrolled text widget.
    """
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag
        self._buffer = ""
        self._last_flush_time = 0

    def write(self, text):
        self._buffer += text
        current_time = time.time()
        if current_time - self._last_flush_time > 0.1 or len(self._buffer) > 1000:
            self.flush()

    def flush(self):
        if self._buffer:
            try:
                self.widget.insert(tk.END, self._buffer, (self.tag,))
                self.widget.see(tk.END)
                self._buffer = ""
                self._last_flush_time = time.time()
            except TclError:
                pass

def _print_open_air_ascii(console_print_func):
    """Prints the 'OPEN AIR' ASCII art to the console."""
    clear_console()
    lines = [
        " ░▒▓██████▓▒░ ░▒▓███████▓▒░ ░▒▓████████▓▒ ░▒▓███████▓▒░        ░▒▓██████▓▒░ ░▒▓█▓▒░ ▒▓███████▓▒░  ",
        "░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░       ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░ ▒▓█▓▒░░▒▓█▓▒░ ",
        "░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░       ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░ ▒▓█▓▒░░▒▓█▓▒░ ",
        "░▒▓█▓▒░░▒▓█▓▒ ░▒▓███████▓▒░ ░▒▓██████▓▒░  ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓████████▓▒ ░▒▓█▓▒░ ▒▓███████▓▒░  ",
        "░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░       ░▒▓█▓▒░       ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░ ▒▓█▓▒░░▒▓█▓▒░ ",
        "░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░       ░▒▓█▓▒░       ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░ ▒▓█▓▒░░▒▓█▓▒░ ",
        " ░▒▓██████▓▒░ ░▒▓█▓▒░       ░▒▓████████▓▒ ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒ ░▒▓█▓▒░ ▒▓█▓▒░░▒▓█▓▒░ "
    ]
    for line in lines:
        console_print_func(line)

def _print_collaboration_ascii(console_print_func):
    """Prints the collaboration ASCII art to the console."""
    clear_console()
    # ... (rest of ASCII functions are unchanged) ...
    lines = [
        "                                               #              #####                     ## ####",
        "                                               ###            ##   ######               ##  ## ",
        "                                               ####           ##         #####          ## ##  ",
        "                                  ##           ## ##          ##             #####      ####   ",
        "                       ############            ##  ###        #                  ###    ####   ",
        "             #########        ###              ##   ###      ##                    ##   ###    ",
        "   #########               ###                 ##     ##     ##                ####     ##     ",
        "                         ###                   ###########   ##          ######         ##     ",
        "                       ###                     ##       ###  #  ########                #      ",
        "                     ###                       ##         #####                                ",
        "                   ###                         ##           ##                        # ##     ",
        "                 ###                #######                 ##                        ###      ",
        "              ####            ######                        ##                  ##########     ",
        "            ###        #######                                   ##############                ",
        "          ###   #######                             ###########                                ",
        "        ########                  ########             ####                                    ",
        "      ###              ##########  ####              ########                                  ",
        "           ###########          ###         ########                                           ",
        " ##########                  ###    ########                                                   ",
        "                         ##########                                                            ",
        "                      #####                        "
    ]
    for line in lines:
        console_print_func(line)

def _print_inst_ascii(console_print_func):
    """Prints the 'INST' ASCII art to the console."""
    clear_console()
    lines = [
        "INST",
        "░▒▓█▓▒░▒▓███████▓▒░ ░▒▓███████▓▒░▒▓████████▓▒░ ",
        "░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░         ░▒▓█▓▒░     ",
        "░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░         ░▒▓█▓▒░     ",
        "░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░   ░▒▓█▓▒░     ",
        "░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░  ░▒▓█▓▒░     ",
        "░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░  ░▒▓█▓▒░     ",
        "░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░   ░▒▓█▓▒░     "
    ]
    for line in lines:
        console_print_func(line)

def _print_scan_ascii(console_print_func):
    """Prints the 'SCAN' ASCII art to the console."""
    clear_console()
    lines = [
        "SCAN",
        " ░▒▓███████▓▒░ ░▒▓██████▓▒░  ░▒▓██████▓▒░ ░▒▓███████▓▒░  ",
        "░▒▓█▓▒░       ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░ ",
        "░▒▓█▓▒░       ░▒▓█▓▒░       ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░ ",
        " ░▒▓██████▓▒░ ░▒▓█▓▒░       ░▒▓████████▓▒░░▒▓█▓▒░░▒▓█▓▒░ ",
        "       ░▒▓█▓▒░░▒▓█▓▒░       ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░ ",
        "       ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░ ",
        "░▒▓███████▓▒░  ░▒▓██████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░ "
    ]
    for line in lines:
        console_print_func(line)

def _print_plot_ascii(console_print_func):
    """Prints the 'PLOT' ASCII art to the console."""
    clear_console()
    lines = [
        "PLOT:                                                   ",
        "░▒▓███████▓▒░ ░▒▓█▓▒░       ░▒▓██████▓▒░░▒▓████████▓▒░ ",
        "░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░     ",
        "░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░     ",
        "░▒▓███████▓▒░ ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░     ",
        "░▒▓█▓▒░       ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░     ",
        "░▒▓█▓▒░       ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░     ",
        "░▒▓█▓▒░       ░▒▓████████▓▒░░▒▓██████▓▒░   ░▒▓█▓▒░     "
    ]
    for line in lines:
        console_print_func(line)

def _print_marks_ascii(console_print_func):
    """Prints the 'MARKS' ASCII art to the console."""
    clear_console()
    lines = [
        "MARKS:                                                                                                                ",
        "░▒▓██████████████▓▒░  ░▒▓██████▓▒░ ░▒▓███████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░ ",
        "░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░ ",
        "░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░ ",
        "░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓████████▓▒░░▒▓███████▓▒░ ░▒▓███████▓▒░  ",
        "░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░ ",
        "░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░ ",
        "░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░ "
    ]
    for line in lines:
        console_print_func(line)

def _print_presets_ascii(console_print_func):
    """Prints the 'PRESETS.CSV' ASCII art to the console."""
    clear_console()
    lines = [
        "PRESETS.CSV is a file that contains user-defined presets for the application.",
        "                                                                ",
        "░▒▓███████▓▒░ ░▒▓███████▓▒░ ░▒▓████████▓▒░ ░▒▓███████▓▒░░▒▓████████▓▒░░▒▓████████▓▒░ ",
        "░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░       ░▒▓█▓▒░       ░▒▓█▓▒░          ░▒▓█▓▒░     ",
        "░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░       ░▒▓█▓▒░       ░▒▓█▓▒░          ░▒▓█▓▒░     ",
        "░▒▓███████▓▒░ ░▒▓███████▓▒░ ░▒▓██████▓▒░   ░▒▓██████▓▒░ ░▒▓██████▓▒░     ░▒▓█▓▒░     ",
        "░▒▓█▓▒░       ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░              ░▒▓█▓▒░░▒▓█▓▒░          ░▒▓█▓▒░     ",
        "░▒▓█▓▒░       ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░              ░▒▓█▓▒░░▒▓█▓▒░          ░▒▓█▓▒░     ",
        "░▒▓█▓▒░       ░▒▓█▓▒░░▒▓█▓▒░░▒▓████████▓▒░░▒▓███████▓▒░ ░▒▓████████▓▒░   ░▒▓█▓▒░     "
    ]
    for line in lines:
        console_print_func(line)

def _print_xxx_ascii(console_print_func):
    """Prints the 'XXX' ASCII art to the console."""
    clear_console()
    lines = [
        "XXX",
        "░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ",
        "░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ",
        "░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ",
        " ░▒▓██████▓▒░        ░▒▓██████▓▒░        ░▒▓██████▓▒░       ",
        "░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ",
        "░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ",
        "░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      "
    ]
    for line in lines:
        console_print_func(line)

def display_splash_screen():
    """
    Prints a stylized ASCII art splash screen to the terminal.
    """
    console_log("")
    _print_open_air_ascii(console_log)
    console_log("")
    _print_collaboration_ascii(console_log)
    console_log("")
    console_log("A Colaboration betweeen Ike Zimbel and Anthony P. Kuzub")
    console_log("")
    console_log("https://zimbelaudio.com/ike-zimbel/    ")
    console_log("https://www.like.audio/")
    console_log("")