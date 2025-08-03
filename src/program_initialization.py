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
# Version 20250803.1530.0 (Fixed AttributeError: '_tkinter.tkapp' object has no attribute 'DATA_FOLDER_PATH' by importing DATA_FOLDER_PATH.)
# Version 20250803.1550.0 (Fixed TypeError: 'str' object has no attribute 'read_dict' by passing a ConfigParser object to load_config.)
# Version 20250803.1555.0 (Fixed TypeError: set_debug_to_gui_console_mode() takes 1 positional argument but 2 were given.)

import os
import configparser
import inspect # For logging function names

# Import logging and config management functions
import src.debug_logic as debug_logic_module # Import as module to access internal functions
from src.debug_logic import debug_log, set_console_log_func, set_log_visa_commands_mode, set_debug_to_terminal_mode, set_debug_to_file_mode, set_include_console_messages_to_debug_file_mode, set_debug_to_gui_console_mode, set_log_visa_command_func, _write_to_debug_file # Explicit import for clarity
from src.console_logic import console_log, set_debug_file_hooks # Explicit import for clarity
from src.settings_and_config.config_manager import load_config, save_config
from src.program_default_values import DATA_FOLDER_PATH, CONFIG_FILE_PATH, DEBUG_COMMANDS_FILE_PATH # NEW: Import path constants


current_version = "20250803.1555.0" # this variable should always be defined below the header to make the debugging better

def ensure_data_directory_exists(data_folder_path, console_print_func, debug_print_func, app_version):
    """
    Function Description:
    Ensures that the application's DATA directory exists. If it doesn't,
    it creates the directory.

    Inputs:
        data_folder_path (str): The path to the DATA folder.
        console_print_func (function): Function to print messages to the console.
        debug_print_func (function): Function to print debug messages.
        app_version (str): The current version of the application for logging.

    Process:
        1. Checks if the `data_folder_path` exists.
        2. If not, creates the directory.
        3. Logs success or failure.

    Outputs:
        None. Ensures the DATA directory is present.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_print_func(f"Ensuring data directory exists at: {data_folder_path}. Version: {app_version}.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=app_version,
                        function=current_function)
    try:
        if not os.path.exists(data_folder_path):
            os.makedirs(data_folder_path)
            console_print_func(f"✅ Created DATA directory: {data_folder_path}")
            debug_print_func(f"DATA directory created successfully.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=app_version,
                                function=current_function)
        else:
            debug_print_func(f"DATA directory already exists.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=app_version,
                                function=current_function)
    except Exception as e:
        console_print_func(f"❌ Error creating DATA directory {data_folder_path}: {e}")
        debug_print_func(f"ERROR creating DATA directory: {e}",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=app_version,
                            function=current_function)

def initialize_program_environment(app_instance):
    """
    Function Description:
    Centralizes the initial setup of the application environment. This includes
    ensuring the data directory exists, loading the configuration, and setting
    up the initial debug logging parameters based on the loaded configuration.

    Inputs:
        app_instance (App): The main application instance, providing access to
                            config, Tkinter variables, and other app attributes.

    Process:
        1. Calls `ensure_data_directory_exists` to create the DATA folder if needed.
        2. Creates a `ConfigParser` object.
        3. Loads the application configuration from `config.ini` into the `ConfigParser` object.
        4. Registers console and debug logging functions with their respective modules.
        5. Sets debug modes based on the loaded configuration values (via Tkinter variables).
        6. Logs the completion of the initialization.

    Outputs:
        None. Configures the application's environment.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Initializing program environment. Version: {current_version}.",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    # Ensure the DATA directory exists FIRST
    ensure_data_directory_exists(DATA_FOLDER_PATH, console_log, debug_log, app_instance.current_version)

    # Create a ConfigParser object and then load configuration into it
    app_instance.config = configparser.ConfigParser()
    load_config(app_instance.config, CONFIG_FILE_PATH, console_log, app_instance)

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
    set_debug_to_file_mode(app_instance.debug_to_file_var.get(), DEBUG_COMMANDS_FILE_PATH) # Using imported DEBUG_COMMANDS_FILE_PATH
    set_include_console_messages_to_debug_file_mode(app_instance.include_console_messages_to_debug_file_var.get())
    set_debug_to_gui_console_mode(app_instance.debug_to_gui_console_var.get()) # Removed app_instance as it's not needed here

    # Register the log_visa_command function with debug_logic
    set_log_visa_command_func(debug_logic_module.log_visa_command)

    debug_log(f"Program environment initialized successfully. Version: {current_version}.",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
