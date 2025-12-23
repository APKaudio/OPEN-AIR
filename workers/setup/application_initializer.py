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


def initialize_app(console_print_func, debug_log_func):
    debug_log_func(
        message=f"🚀 Initialization sequence initiated for version {app_constants.current_version}.",
        file=os.path.basename(__file__),
        version=app_constants.current_version,
        function=initialize_app.__name__,
      
    )
    

    # Initialize paths
    debug_log_func(
        message="Initializing paths...",
        file=os.path.basename(__file__),
        version=app_constants.current_version,
        function=initialize_app.__name__,
      
    )
    global_project_root, data_dir = path_initializer.initialize_paths(console_print_func)
    debug_log_func(
        message=f"Paths initialized. Data directory: {data_dir}",
        file=os.path.basename(__file__),
        version=app_constants.current_version,
        function=initialize_app.__name__,
      
    )

    # Configure logger
    debug_log_func(
        message="Configuring logger...",
        file=os.path.basename(__file__),
        version=app_constants.current_version,
        function=initialize_app.__name__,
      
    )
    logger_config.configure_logger(data_dir, console_print_func)
    debug_log_func(
        message="Logger configured.",
        file=os.path.basename(__file__),
        version=app_constants.current_version,
        function=initialize_app.__name__,
      
    )

    # Clear debug directory
    debug_log_func(
        message="Clearing debug directory...",
        file=os.path.basename(__file__),
        version=app_constants.current_version,
        function=initialize_app.__name__,
      
    )
    debug_cleaner.clear_debug_directory(data_dir, console_print_func)
    debug_log_func(
        message="Debug directory cleared.",
        file=os.path.basename(__file__),
        version=app_constants.current_version,
        function=initialize_app.__name__,
      
    )

    # Configure console encoding
    debug_log_func(
        message="Configuring console encoding...",
        file=os.path.basename(__file__),
        version=app_constants.current_version,
        function=initialize_app.__name__,
      
    )
    console_encoder.configure_console_encoding(console_print_func, debug_log_func)
    debug_log_func(
        message="Console encoding configured.",
        file=os.path.basename(__file__),
        version=app_constants.current_version,
        function=initialize_app.__name__,
      
    )

    return True