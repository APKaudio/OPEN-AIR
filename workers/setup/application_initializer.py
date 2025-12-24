# workers/setup/application_initializer.py

import os
import sys
import pathlib


import workers.logger.logger

import workers.setup.app_constants as app_constants
import workers.setup.path_initializer as path_initializer
import workers.logger.logger_config as logger_config
import workers.setup.console_encoder as console_encoder
import workers.setup.debug_cleaner as debug_cleaner
from workers.utils.log_utils import _get_log_args


def initialize_app(console_print_func, debug_log_func):
    debug_log_func(
        message=f"🚀 Initialization sequence initiated for version {app_constants.current_version}.",
        **_get_log_args()
    )
    
    try:
        # Initialize paths
        debug_log_func(
            message="Initializing paths...",
            **_get_log_args()
        )
        global_project_root, data_dir = path_initializer.initialize_paths(console_print_func)
        debug_log_func(
            message=f"Paths initialized. Data directory: {data_dir}",
            **_get_log_args()
        )

        # Configure logger
        debug_log_func(
            message="Configuring logger...",
            **_get_log_args()
        )
        logger_config.configure_logger(data_dir, console_print_func)
        debug_log_func(
            message="Logger configured.",
            **_get_log_args()
        )

        # Clear debug directory
        debug_log_func(
            message="Clearing debug directory...",
            **_get_log_args()
        )
        debug_cleaner.clear_debug_directory(data_dir, console_print_func)
        debug_log_func(
            message="Debug directory cleared.",
            **_get_log_args()
        )

        # Configure console encoding
        debug_log_func(
            message="Configuring console encoding...",
            **_get_log_args()
        )
        console_encoder.configure_console_encoding(console_print_func, debug_log_func)
        debug_log_func(
            message="Console encoding configured.",
            **_get_log_args()
        )

        debug_log_func(
            message="✅ Application initialization completed successfully.",
            **_get_log_args()
        )
        return True
    except Exception as e:
        debug_log_func(
            message=f"❌ Error during application initialization: {e}",
            **_get_log_args()
        )
        return False