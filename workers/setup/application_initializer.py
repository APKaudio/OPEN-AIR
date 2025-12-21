# workers/setup/application_initializer.py

import os
import sys
import pathlib

from workers.watchdog.worker_watchdog import Watchdog
import display.logger

import workers.setup.app_constants as app_constants
import workers.setup.path_initializer as path_initializer
import workers.setup.logger_config as logger_config
import workers.setup.console_encoder as console_encoder
import workers.setup.debug_cleaner as debug_cleaner


def initialize_app(console_log_func, debug_log_func, watchdog_instance):
    console_log_func(f"🚀 Initialization sequence initiated for version {app_constants.current_version}.")
    watchdog_instance.pet("initialize_app: start")

    # Initialize paths
    global_project_root, data_dir = path_initializer.initialize_paths(console_log_func, watchdog_instance)

    # Configure logger
    logger_config.configure_logger(data_dir, console_log_func, watchdog_instance)

    # Clear debug directory
    debug_cleaner.clear_debug_directory(data_dir, console_log_func, watchdog_instance)

    # Configure console encoding
    console_encoder.configure_console_encoding(watchdog_instance)

    return True