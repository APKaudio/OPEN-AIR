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
# Version 20251009.214021.4
# FIXED: Added a check to reject commands containing placeholders (< or >) before sending.
# FIXED: Implemented a call to the new log_visa_command utility function for logging SCPI I/O.

import os
import inspect
import pyvisa
import time

# --- Utility and Worker Imports ---
# UPDATED: Import the centralized log_visa_command
from display.logger import debug_log, console_log, log_visa_command


# --- Global Scope Variables (as per Protocol 4.4) ---
current_version = "20251009.214021.4"
current_version_hash = (20251009 * 214021 * 4)
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
            # self.rm = pyvisa.ResourceManager() # No longer needed here
            self.inst = None
            self.model = ""
            self.manufacturer = ""

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

   

    def set_instrument_instance(self, inst):
        """
        Sets the PyVISA instrument instance for the dispatcher to use.
        This function is called by the VisaDeviceManager upon connection/disconnection.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🔵 Received new instrument instance. It's now my time to shine!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=self._print_to_gui_console
        )
        self.inst = inst
        if self.inst:
            console_log("✅ SCPI Dispatcher is now linked to an instrument.")
        else:
            console_log("✅ SCPI Dispatcher has been unlinked from the instrument.")


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
        if not self.inst:
            self._print_to_gui_console("❌ Error: Instrument not connected. Cannot write command.")
            debug_log(f"🐐 ❌ No instrument connected. Aborting command write.", file=current_file, version=current_version, function=current_function_name, console_print_func=self._print_to_gui_console)
            return False
        
        # --- Reject command if it contains placeholders. ---
        if "<" in command or ">" in command:
            error_message = f"❌ Error: Command rejected. Unresolved placeholders found: '{command}'."
            self._print_to_gui_console(error_message)
            debug_log(
                message=f"🐐 ❌ Command rejected! Unresolved placeholders found. The offending command be: {command}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )
            return False
        # --- END NEW FIX ---

        try:
            self.inst.write(command)
            # NEW: Log the command sent to the device
            log_visa_command(command=command, direction="SENT") 
            self._print_to_gui_console(f"✅ Sent command: {command}")
            return True
        except Exception as e:
            self._print_to_gui_console(f"❌ Error writing command '{command}': {e}")
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
        if not self.inst:
            self._print_to_gui_console("❌ Error: Instrument not connected. Cannot query command.")
            debug_log(f"🐐 ❌ No instrument connected. Aborting command query.", file=current_file, version=current_version, function=current_function_name, console_print_func=self._print_to_gui_console)
            return None
            
        # --- Reject command if it contains placeholders. ---
        if "<" in command or ">" in command:
            error_message = f"❌ Error: Query rejected. Unresolved placeholders found: '{command}'."
            self._print_to_gui_console(error_message)
            debug_log(
                message=f"🐐 ❌ Query rejected! Unresolved placeholders found. The offending command be: {command}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )
            return None
        # --- END NEW FIX ---
        
        try:
            # NEW: Log the query command sent
            log_visa_command(command=command, direction="SENT")
            response = self.inst.query(command).strip()
            # NEW: Log the response received
            log_visa_command(command=response, direction="RECEIVED")
            
            self._print_to_gui_console(f"✅ Sent query: {command}")
            self._print_to_gui_console(f"✅ Received response: {response}")
            return response
        except Exception as e:
            self._print_to_gui_console(f"❌ Error querying command '{command}': {e}")
            debug_log(
                message=f"🐐 🔴 Confound it! The query has returned naught but static! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=self._print_to_gui_console
            )
            self._reset_device(inst=self.inst)
            return None