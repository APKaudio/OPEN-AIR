# managers/manager_yak_tx.py
#
# This manager is responsible for transmitting the final SCPI command
# to the device via the ScpiDispatcher.

import os
import inspect
from workers.worker_logging import debug_log, console_log

# --- Global Scope Variables ---
current_version = "20250913.130500.10"
current_file = f"{os.path.basename(__file__)}"

class YakTxManager:
    """
    Transmits SCPI commands to the instrument using the ScpiDispatcher.
    """
    def __init__(self, dispatcher_instance):
        self.dispatcher = dispatcher_instance

    def execute_command(self, command_type, command_string):
        """
        Executes a command based on the presence of a '?' to determine if it is a query.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        # Check if the command string contains a '?' to identify it as a query
        if '?' in command_string:
            debug_log(
                message=f"🐐🐐🐐🚀 Engaging the '{command_type}' API! Dispatching query command now!",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )
            return self.dispatcher.query_safe(command_string)
        else:
            debug_log(
                message=f"🐐🐐🐐🚀 Engaging the '{command_type}' API! Dispatching write command now!",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )
            return self.dispatcher.write_safe(command_string)