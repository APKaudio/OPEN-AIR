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
# Version 20250803.233621.0 (FIXED: Corrected function call to load_config with the right number of arguments.)
# Version 20250803.204901.0 (REFACTORED: Moved console redirection logic to main_app.py to resolve circular import.)

current_version = "20250803.233621.0"

import os
import inspect

# Local application imports
from src.debug_logic import debug_log
from src.console_logic import console_log
from src.program_default_values import (
    DATA_FOLDER_PATH, CONFIG_FILE_PATH
)
from src.settings_and_config.config_manager import load_config, save_config

def initialize_program_environment(app_instance):
    """
    Sets up the initial program environment, including creating necessary directories
    and loading the application configuration.
    
    This function has been refactored to remove GUI-related setup, which is
    now handled in program_gui_utils.py.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Initializing program environment...",
              file=f"{os.path.basename(__file__)} - {current_version}",
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
    # CORRECTED: The function call now uses the correct arguments and assigns the returned value.
    app_instance.config = load_config(CONFIG_FILE_PATH, console_log)