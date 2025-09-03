# agents/agent_yak_handler_rig.py
#
# This handler is responsible for processing 'RIG' type SCPI commands.
# It handles the substitution of placeholder values in a command template
# and sends a single, multi-parameter command to the instrument.
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
# Version 20250902.115600.1

import inspect
import os

from workers.worker_logging import debug_log, console_log
from agents.agent_YaketyYak import YakRig

# --- Global Scope Variables ---
current_version = "20250902.115600.1"
current_version_hash = (20250902 * 115600 * 1)
current_file = f"{os.path.basename(__file__)}"

def YakRig_handle_command(dispatcher, command_type, *variable_values):
    """
    Handles a 'RIG' command by substituting placeholders.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering {current_function}. command_type: {command_type}, variable_values: {variable_values}",
                file=current_file,
                version=current_version,
                function=current_function)

    response = YakRig(dispatcher, command_type, variable_values)

    if response == "PASSED":
        return "PASSED"
    else:
        return "FAILED"
