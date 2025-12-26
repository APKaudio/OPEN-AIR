# managers/yak_manager/manager_yak_tx.py
#
# This file (manager_yak_tx.py) is responsible for transmitting the final SCPI command to the device via the ScpiDispatcher.
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

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
from workers.logger.logger import  debug_logger
from workers.utils.log_utils import _get_log_args 
from workers.utils.log_utils import _get_log_args

LOCAL_DEBUG_ENABLE = False


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
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"🐐🐐🐐🚀 Engaging the '{command_type}' API! Dispatching query command now!",
                    **_get_log_args()


                )
            return self.dispatcher.query_safe(cleaned_command)
        else:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"🐐🐐🐐🚀 Engaging the '{command_type}' API! Dispatching write command now!",
                    **_get_log_args()


                )
            return self.dispatcher.write_safe(cleaned_command)