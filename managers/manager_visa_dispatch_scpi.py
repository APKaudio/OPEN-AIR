# managers/manager_visa_dispatch_scpi.py
#
# This manager provides a safe, low-level interface for executing SCPI write
# and query commands via PyVISA.
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
# Version 20250904.010100.1

import os
import inspect
import pyvisa
import time

# --- Utility and Worker Imports ---
from workers.worker_logging import debug_log, console_log
# NOTE: The log_visa_command function needs to be created or imported from its location.
# from display.debug_logic import log_visa_command


# --- Global Scope Variables (as per Protocol 4.4) ---
current_version = "20250904.010100.1"
current_version_hash = (20250904 * 10100 * 1)
current_file = f"{os.path.basename(__file__)}"


class ScpiDispatcher:
    """
    Manages the PyVISA connection and provides safe, low-level command execution.
    """
    def __init__(self, app_instance, console_print_func):
        # Initializes the SCPI dispatcher manager.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🟢 Entering {current_function_name}. The grand SCPI experiment begins!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_print_func
        )
        try:
            self.app_instance = app_instance
            self._print_to_gui_console = console_print_func
            self.rm = pyvisa.ResourceManager()
            self.inst = None
            console_log("✅ Success! The SCPI Dispatcher has initialized its core components.")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🛠️🔴 By Jove, the apparatus has failed to initialize! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )

    def _reset_device(self, inst):
        # Sends a soft reset command to the instrument to restore a known state after an error.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🟠 Entering {current_function_name}. Attempting a system-wide reset!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=self._print_to_gui_console
        )
        try:
            console_log("⚠️ Command failed. Attempting to reset the instrument with '*RST'...")
            reset_success = self.write_safe(command="*RST")

            if reset_success:
                console_log("✅ Success! The device reset command was sent successfully.")
            else:
                console_log("❌ Failure! The device did not respond to the reset command.")
            return reset_success

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🛠️🔴 The reset protocol has failed catastrophically! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )
            return False

    def write_safe(self, command):
        # Safely writes a SCPI command to the instrument.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐 📝 Entering {current_function_name} to transmit command: {command}",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=self._print_to_gui_console
        )
        try:
            if not self.inst:
                console_log("❌ Error in write_safe: Instrument not connected.")
                return False

            self.inst.write(command)
            # log_visa_command(command, "SENT") # Requires log_visa_command to be defined/imported
            console_log(f"✅ Success! The command '{command}' was written.")
            return True

        except Exception as e:
            console_log(f"❌ Error writing command '{command}': {e}")
            debug_log(
                message=f"🐐 🔴 Blast and barnacles! The write command has gone awry! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )
            # Prevent infinite loop if the reset command itself fails
            if command != "*RST":
                self._reset_device(inst=self.inst)
            return False

    def query_safe(self, command):
        # Safely queries the instrument with a SCPI command and returns the response.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐 📝 Entering {current_function_name} to query command: {command}",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=self._print_to_gui_console
        )
        try:
            if not self.inst:
                console_log("❌ Error in query_safe: Instrument not connected.")
                return None

            response = self.inst.query(command).strip()
            # log_visa_command(command, "SENT") # Requires log_visa_command
            # log_visa_command(response, "RECEIVED") # Requires log_visa_command
            console_log(f"✅ Success! The query '{command}' returned a response.")
            return response

        except Exception as e:
            console_log(f"❌ Error querying command '{command}': {e}")
            debug_log(
                message=f"🐐 🔴 Confound it! The query has returned naught but static! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )
            self._reset_device(inst=self.inst)
            return None

