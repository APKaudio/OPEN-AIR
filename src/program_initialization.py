# src/program_initialization.py
#
# This file contains the primary initialization sequence for the application.
# It handles the creation of necessary folders, loading of configuration files,
# and setting up the initial state of the application instance.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
#
#
# Version 20250814.214800.1 (FIXED: The call to 'set_debug_to_file_mode' was updated to correctly pass only one argument, resolving the TypeError. Corrected the initialization of a missing Tkinter variable to resolve an AttributeError.)

current_version = "20250814.214800.1"
current_version_hash = 20250814 * 214800 * 1

import os
import inspect
import tkinter as tk

# Local application imports
from display.debug_logic import debug_log, set_debug_mode, set_log_visa_commands_mode, set_debug_to_file_mode, set_include_console_messages_to_debug_file_mode, set_log_truncation_mode, set_include_visa_messages_to_debug_file_mode
from display.console_logic import console_log
from src.settings_and_config.program_default_values import (
    DATA_FOLDER_PATH, CONFIG_FILE_PATH
)
from src.settings_and_config.config_manager import load_config, save_config
from src.settings_and_config.restore_settings_logic import restore_last_used_settings_logic

def initialize_program_environment(app_instance):
    """
    Sets up the initial program environment, including creating necessary directories
    and loading the application configuration.
    
    This function has been refactored to remove GUI-related setup, which is
    now handled in program_gui_utils.py.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Initializing program environment...",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)

    # Ensure the main data folder exists
    try:
        if not os.path.exists(DATA_FOLDER_PATH):
            os.makedirs(DATA_FOLDER_PATH)
            console_log(f"✅ Created data folder at: {DATA_FOLDER_PATH}")
    except OSError as e:
        console_log(f"❌ Critical Error: Could not create data folder at '{DATA_FOLDER_PATH}'. Error: {e}")
        # In a real app, you might want to exit or handle this more gracefully
        return

    # Load configuration
    # The load_config function will create a default if one doesn't exist.
    app_instance.config = load_config(CONFIG_FILE_PATH, console_log)
    
    # After loading the config file, apply the last used settings to the Tkinter variables.
    restore_last_used_settings_logic(app_instance, console_log)
    
    # NEW LOGIC: Now that the config has been restored, we must set the global debug flags
    # in debug_logic.py to match the values loaded from the config. This is the fix.
    debug_log("Syncing debug settings with loaded configuration. Let's make this stick!",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function,
              special=True)
    
    set_debug_mode(app_instance.general_debug_enabled_var.get())
    set_log_visa_commands_mode(app_instance.log_visa_commands_enabled_var.get())
    
    set_debug_to_file_mode(app_instance.debug_to_file_var.get())
    set_include_console_messages_to_debug_file_mode(app_instance.include_console_messages_to_debug_file_var.get())
    set_log_truncation_mode(app_instance.log_truncation_enabled_var.get())
    set_include_visa_messages_to_debug_file_mode(app_instance.include_visa_messages_to_debug_file_var.get())
    
    debug_log("Debug settings synced. No more unwanted logging at startup!",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function,
              special=True)
