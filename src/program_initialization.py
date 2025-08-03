# src/program_initialization.py
#
# This module centralizes the "pre-flight setup" and initialization logic
# for the RF Spectrum Analyzer Controller application. It handles tasks
# such as ensuring necessary data directories exist, loading application
# configuration, and setting up initial debugging parameters.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
# Version 20250803.1430.0 (Initial creation: Centralized data directory creation, config loading, and debug setup.)
# Version 20250803.1440.0 (FIXED: AttributeError: 'function' object has no attribute '_write_to_debug_file' by correcting reference to debug_logic_module._write_to_debug_file.)
# Version 20250803.1445.0 (Moved _setup_tkinter_vars content from main_app.py to a new function: setup_tkinter_variables.)
# Version 20250803.1450.0 (Removed setup_tkinter_variables from this file and imported it from program_shared_values.py.)

import os
import configparser
import inspect # For logging function names

# Import logging and config management functions
import src.debug_logic as debug_logic_module # Import as module to access internal functions
from src.debug_logic import debug_log, set_console_log_func, set_log_visa_commands_mode, set_debug_to_terminal_mode, set_debug_to_file_mode, set_include_console_messages_to_debug_file_mode, set_debug_to_gui_console_mode
from src.console_logic import console_log, set_debug_file_hooks
from src.settings_and_config.config_manager import load_config, save_config
from src.program_shared_values import setup_tkinter_variables # NEW: Import setup_tkinter_variables

current_version = "20250803.1450.0" # this variable should always be defined below the header to make the debugging better

def ensure_data_directory_exists(data_folder_path, console_log_func, debug_log_func, app_version):
    """
    Function Description:
    Ensures that the application's DATA directory exists. If it does not,
    it creates the directory.

    Inputs:
        data_folder_path (str): The absolute path to the DATA directory.
        console_log_func (function): Function to log messages to the GUI console.
        debug_log_func (function): Function to log debug messages.
        app_version (str): The current version of the application for logging.

    Process:
        1. Checks if the `data_folder_path` exists.
        2. If not, attempts to create it.
        3. Logs success or failure.

    Outputs:
        None. Creates the directory as a side effect.
    """
    current_function = inspect.currentframe().f_code.co_name
    if not os.path.exists(data_folder_path):
        try:
            os.makedirs(data_folder_path)
            console_log_func(f"✅ Created DATA directory: {data_folder_path}. All good!")
            debug_log_func(f"DATA directory created: {data_folder_path}. Nice!",
                           file=f"{os.path.basename(__file__)} - {app_version}",
                           version=app_version,
                           function=current_function)
        except OSError as e:
            console_log_func(f"❌ Error creating DATA directory {data_folder_path}: {e}. This is a critical error!")
            debug_log_func(f"ERROR creating DATA directory {data_folder_path}: {e}. What a mess!",
                           file=f"{os.path.basename(__file__)} - {app_version}",
                           version=app_version,
                           function=current_function)
    else:
        debug_log_func(f"DATA directory already exists: {data_folder_path}. No need to create!",
                       file=f"{os.path.basename(__file__)} - {app_version}",
                       version=app_version,
                       function=current_function)


def initialize_program_environment(app_instance):
    """
    Function Description:
    Performs all necessary pre-flight setup for the application environment.
    This includes ensuring data directories, loading configuration, and
    setting up initial debugging parameters.

    Inputs:
        app_instance (App): The main application instance, providing access to
                            paths and Tkinter variables.

    Process:
        1. Ensures the DATA directory exists.
        2. Initializes the ConfigParser.
        3. Loads the application configuration.
        4. If config.ini was not found, it saves default settings.
        5. Sets up the console and debug logging functions based on config.

    Outputs:
        None. Modifies the app_instance and sets up logging.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Starting program environment initialization. Version: {current_version}.",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)

    # Ensure DATA directory exists first
    ensure_data_directory_exists(app_instance.DATA_FOLDER_PATH, console_log, debug_log, app_instance.current_version)

    # Initialize configparser
    app_instance.config = configparser.ConfigParser()

    # Check if config file exists before loading to determine if defaults need saving
    config_file_exists_on_startup = os.path.exists(app_instance.CONFIG_FILE_PATH)

    # Load configuration
    load_config(app_instance.config, app_instance.CONFIG_FILE_PATH, console_log, app_instance)

    # If config.ini was not found on startup, save defaults
    if not config_file_exists_on_startup:
        debug_log(f"config.ini was not found on startup. Saving defaults to new file.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        save_config(app_instance.config, app_instance.CONFIG_FILE_PATH, console_log, app_instance)

    # Register console_log function with debug_logic
    set_console_log_func(console_log)

    # Register debug file hooks from debug_logic with console_logic
    set_debug_file_hooks(
        lambda: app_instance.include_console_messages_to_debug_file_var.get(),
        debug_logic_module._write_to_debug_file # Corrected: Access via the module alias
    )

    # Set debug modes based on loaded config (via Tkinter variables)
    debug_logic_module.set_debug_mode(app_instance.general_debug_enabled_var.get()) # Use module alias
    set_log_visa_commands_mode(app_instance.log_visa_commands_enabled_var.get())
    set_debug_to_terminal_mode(app_instance.debug_to_terminal_var.get())
    set_debug_to_file_mode(app_instance.debug_to_file_var.get(), app_instance.DEBUG_COMMANDS_FILE_PATH)
    set_include_console_messages_to_debug_file_mode(app_instance.include_console_messages_to_debug_file_var.get())
    set_debug_to_gui_console_mode(app_instance.debug_to_gui_console_var.get())

    debug_log(f"Program environment initialization complete. Version: {current_version}.",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)
