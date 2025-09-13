# managers/manager_yak_on_trigger.py
#
# This manager listens for MQTT messages and orchestrates the command
# execution by delegating tasks to specialized sub-managers.

import os
import inspect
import json
import pathlib

# --- Utility and Manager Imports ---
from workers.worker_logging import debug_log, console_log
current_version = "20250912.223200.3"
current_version_hash = (20250912 * 223200 * 3)
current_file = f"{os.path.basename(__file__)}"


def YAK_TRIGGER_COMMAND(self, topic, payload):
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message="TRIGGER TRIGGER TRIGGER",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )