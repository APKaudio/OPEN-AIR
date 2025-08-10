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
# Version 20250810.220100.8 (FIXED: Added call to restore_last_used_settings_logic after loading config to ensure saved settings are applied correctly at startup.)

current_version = "20250810.220100.8"
current_version_hash = 20250810 * 220100 * 8 # Example hash, adjust as needed

import os
import inspect

# Local application imports
from display.debug_logic import debug_log
from display.console_logic import console_log
from src.program_default_values import (
    DATA_FOLDER_PATH, CONFIG_FILE_PATH
)
from src.settings_and_config.config_manager import load_config, save_config
from src.settings_and_config.restore_settings_logic import restore_last_used_settings_logic # NEW: Import the restore logic

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
    
    # NEW LOGIC: After loading the config file, apply the last used settings to the Tkinter variables.
    # This is the key piece that was missing. It ensures the UI reflects the saved state.
    restore_last_used_settings_logic(app_instance, console_log)
    debug_log("Called restore_last_used_settings_logic to apply loaded settings.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function,
              special=True)
