# Instrument/utils_visa_interpreter_commands.py

# This file contains the core logic for executing and testing VISA commands via the
# VisaInterpreterTab. It abstracts all the low-level command execution, error handling,
# and console logging, allowing the GUI to remain a simple view layer. This module
# ensures the principle of separation of concerns is upheld.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250821.175300.1
# UPDATED: File created to house all VISA command execution and testing logic.

import inspect
import os
from datetime import datetime
import tkinter as tk

from yak.utils_yak_visa import query_safe, write_safe
from display.debug_logic import debug_log
from display.console_logic import console_log

# --- Versioning ---
w = 20250821
x_str = '175300'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"{w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"


class VisaCommandExecutor:
    """
    This class handles all execution and testing of VISA commands. It is instantiated
    by the VisaInterpreterTab and is responsible for all communication with the
    connected instrument.
    """
    def __init__(self, app_instance, console_print_func):
        self.app_instance = app_instance
        self.console_print_func = console_print_func

        current_function = inspect.currentframe().f_code.co_name
        debug_log("Initializing VisaCommandExecutor. The command-slinger is ready! 🤠",
                    file=current_file,
                    version=current_version,
                    function=current_function)

    def _get_instrument_status(self):
        """Checks if an instrument is connected and returns the status."""
        is_connected = self.app_instance.inst is not None
        if not is_connected:
            self.console_print_func("❌ No instrument connected. The command is a whisper to the wind!")
            debug_log("Command failed: No instrument connection.",
                        file=current_file,
                        version=current_version,
                        function=inspect.currentframe().f_code.co_name)
        return is_connected

    def on_execute_command(self, command):
        """Executes a command (query or write) based on its format."""
        if not self._get_instrument_status():
            return
        
        self.console_print_func(f"Executing: {command}...")
        
        if command.endswith('?'):
            response = query_safe(self.app_instance.inst, command, self.console_print_func)
            self.console_print_func(f"Response: {response}")
        else:
            write_safe(self.app_instance.inst, command, self.console_print_func)
            self.console_print_func("✅ Command sent.")
    
    def on_query_command(self, command):
        """Executes a query command and displays the response."""
        if not self._get_instrument_status():
            return
        
        if not command.endswith('?'):
            self.console_print_func(f"⚠️ Command '{command}' does not end with '?' for a query. Executing as a simple write.")
            self.on_execute_command(command)
            return

        self.console_print_func(f"Querying: {command}...")
        response = query_safe(self.app_instance.inst, command, self.console_print_func)
        self.console_print_func(f"Response: {response}")

    def on_set_command(self, command):
        """Executes a set command, which requires a value."""
        if not self._get_instrument_status():
            return

        parts = command.split(' ', 1)
        if len(parts) < 2:
            self.console_print_func("❌ SET command requires a value. Format: 'command value'.")
            debug_log("Set failed: Invalid command format.",
                        file=current_file,
                        version=current_version,
                        function=inspect.currentframe().f_code.co_name)
            return
            
        full_command = f"{parts[0]} {parts[1]}"
        self.console_print_func(f"Setting: {full_command}...")
        write_safe(self.app_instance.inst, full_command, self.console_print_func)
        self.console_print_func("✅ Set command sent.")
    
    def on_do_command(self, command):
        """Executes a 'do' command, which performs an action."""
        if not self._get_instrument_status():
            return

        self.console_print_func(f"Executing: {command}...")
        write_safe(self.app_instance.inst, command, self.console_print_func)
        self.console_print_func("✅ Do command sent.")