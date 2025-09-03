# agents/agent_yak_dispatch_scpi.py
#
# This agent acts as the central dispatcher for all SCPI commands. It manages the
# PyVISA connection, loads the command repository, and routes high-level requests
# to the appropriate, low-level handler functions.
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
# Version 20250902.115000.1
# UPDATED: Merged all low-level VISA utility functions from utils_yak_visa.py into this class for a centralized communication core.

import os
import inspect
import csv
import pyvisa
import time
from collections import defaultdict

# Assume these are imported from a central logging utility
from workers.worker_logging import debug_log, console_log
from display.debug_logic import log_visa_command
from workers.worker_mqtt_controller_util import MqttControllerUtility


# --- Global Scope Variables ---
current_version = "20250902.115000.1"
current_version_hash = (20250902 * 115000 * 1)
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
VISA_COMMANDS_FILE_PATH = "DATA/Visa_Commands/visa commands.csv"
MAX_RETRY_ATTEMPTS = 3
VISA_COMMAND_DELAY_SECONDS = 0.05


class ScpiDispatcher:
    """
    Manages the PyVISA connection and dispatches SCPI commands.
    It loads the command repository and provides a safe interface for execution.
    """
    def __init__(self, mqtt_util_instance, app_instance):
        self.mqtt_util = mqtt_util_instance
        self.app_instance = app_instance
        self.visa_commands = self._load_commands_from_file()
        self.rm = pyvisa.ResourceManager()
        self.inst = None

    def _load_commands_from_file(self):
        """Loads the VISA commands from the specified CSV file."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐 🟢 Loading commands from file: {VISA_COMMANDS_FILE_PATH}",
            file=current_file, version=current_version, function=current_function,
            console_print_func=console_log
        )
        commands = {}
        try:
            with open(VISA_COMMANDS_FILE_PATH, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                for row in reader:
                    path = row[0].split('/')
                    # Build the nested dictionary based on the path
                    current_level = commands
                    for part in path[:-1]:
                        current_level = current_level.setdefault(part, {})
                    current_level[path[-1]] = {
                        "Active": row[1].lower() == 'true',
                        "Default_value": row[2],
                        "VISA_Command": row[3],
                        "validated": row[4]
                    }
            debug_log(
                message=f"🐐 ✅ Successfully loaded {len(commands)} commands from file.",
                file=current_file, version=current_version, function=current_function,
                console_print_func=console_log
            )
        except Exception as e:
            debug_log(
                message=f"🐐 ❌ Error loading commands from file: {e}. This is a disaster! 💥",
                file=current_file, version=current_version, function=current_function,
                console_print_func=console_log
            )
        return commands

    def get_command(self, command_path):
        """Traverses the nested dictionary to find the command details."""
        parts = command_path.split('/')
        command_details = self.visa_commands
        for part in parts:
            if part in command_details:
                command_details = command_details[part]
            else:
                return None
        return command_details

    def dispatch_command(self, command_type, action_type, *args):
        """High-level dispatcher that routes calls to the appropriate handler."""
        handler_map = {
            "BEG": handle_beg_command,
            "RIG": handle_rig_command,
            "DO": handle_do_command,
            "GET": handle_get_command,
            "SET": handle_set_command
        }
        handler = handler_map.get(action_type)
        if handler:
            return handler(self, command_type, *args)
        else:
            console_log(f"❌ Unknown action type '{action_type}'. Cannot execute command.")
            return "FAILED"

    def _reset_device(self, inst):
        """Sends a soft reset command to the instrument to restore a known state after an error."""
        current_function = inspect.currentframe().f_code.co_name
        console_log("⚠️ Command failed. Attempting to reset the instrument with '*RST'...")
        debug_log(f"🐐 🟡 Command failed. Attempting to send reset command '*RST' to the instrument.",
                    file=current_file, version=current_version, function=current_function)
        
        reset_success = self.write_safe("*RST")
        if reset_success:
            console_log("✅ Device reset command sent successfully.")
        else:
            console_log("❌ Failed to send reset command.")
        return reset_success

    def write_safe(self, command):
        """Safely writes a SCPI command to the instrument."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"🐐 📝 Attempting to write command: {command}",
                    file=current_file, version=current_version, function=current_function)
        if not self.inst:
            console_log("⚠️ Warning: Instrument not connected. Cannot write command.")
            return False
        try:
            self.inst.write(command)
            log_visa_command(command, "SENT")
            return True
        except Exception as e:
            console_log(f"❌ Error writing command '{command}': {e}")
            self._reset_device(self.inst)
            return False

    def query_safe(self, command):
        """Safely queries the instrument with a SCPI command and returns the response."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"🐐 📝 Attempting to query command: {command}",
                    file=current_file, version=current_version, function=current_function)
        if not self.inst:
            console_log("⚠️ Warning: Instrument not connected. Cannot query command.")
            return None
        try:
            response = self.inst.query(command).strip()
            log_visa_command(command, "SENT")
            log_visa_command(response, "RECEIVED")
            return response
        except Exception as e:
            console_log(f"❌ Error querying command '{command}': {e}")
            self._reset_device(self.inst)
            return None

    def set_safe(self, command, value):
        """Safely writes a SET command to the instrument with a specified value."""
        current_function = inspect.currentframe().f_code.co_name
        full_command = f"{command} {value}"
        debug_log(f"🐐 📝 Attempting to SET: {full_command}",
                    file=current_file, version=current_version, function=current_function)
        return self.write_safe(full_command)

    def _wait_for_opc(self, timeout=5):
        """Waits for the instrument's Operation Complete (OPC) flag."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"🐐 🟠 Waiting for Operation Complete (*OPC?) with a timeout of {timeout} seconds.",
                    file=current_file, version=current_version, function=current_function)
        original_timeout = self.inst.timeout
        self.inst.timeout = timeout * 1000
        try:
            response = self.inst.query("*OPC?").strip()
            self.inst.timeout = original_timeout
            if response == "1":
                console_log("✅ Operation Complete. Fucking brilliant!")
                return "PASSED"
            else:
                console_log("❌ Operation failed to complete or returned an unexpected value.")
                self._reset_device(self.inst)
                return "FAILED"
        except pyvisa.errors.VisaIOError as e:
            self.inst.timeout = original_timeout
            console_log(f"❌ Operation Complete query timed out after {timeout} seconds.")
            self._reset_device(self.inst)
            return "TIME FAILED"
        except Exception as e:
            self.inst.timeout = original_timeout
            console_log(f"❌ Error during Operation Complete query: {e}")
            self._reset_device(self.inst)
            return "FAILED"