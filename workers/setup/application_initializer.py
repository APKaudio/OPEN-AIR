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


def initialize_app(console_log_func, debug_log_func):
    console_log_func(f"🚀 Initialization sequence initiated for version {app_constants.current_version}.")
    

    # Initialize paths
    global_project_root, data_dir = path_initializer.initialize_paths(console_log_func)

    # Configure logger
    logger_config.configure_logger(data_dir, console_log_func)

    # Clear debug directory
    debug_cleaner.clear_debug_directory(data_dir, console_log_func)

    # Configure console encoding
    # Pass logger functions to configure_console_encoding
    console_encoder.configure_console_encoding( console_log_func, debug_log_func) # Corrected call

    return True