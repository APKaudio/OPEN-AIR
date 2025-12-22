# managers/yak_manager/manager_yak_tx.py
#
# This file (manager_yak_tx.py) is responsible for transmitting the final SCPI command to the device via the ScpiDispatcher.
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251213  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 44 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


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


import os
import inspect
from workers.logger.logger import debug_log, console_log, log_visa_command

Local_Debug_Enable = True

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
        
        # --- FIX: Clean the command string before sending ---
        cleaned_command = command_string.strip()
        # --- END FIX ---
        
        # Check if the command string contains a '?' to identify it as a query
        if '?' in cleaned_command:
            if Local_Debug_Enable:
                debug_log(
                    message=f"🐐🐐🐐🚀 Engaging the '{command_type}' API! Dispatching query command now!",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
            return self.dispatcher.query_safe(cleaned_command)
        else:
            if Local_Debug_Enable:
                debug_log(
                    message=f"🐐🐐🐐🚀 Engaging the '{command_type}' API! Dispatching write command now!",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
            return self.dispatcher.write_safe(cleaned_command)