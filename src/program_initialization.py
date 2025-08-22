# src/program_initialization.py
#
# This file contains the primary initialization sequence for the application, handling
# folder creation, configuration loading, and initial state setup.
#
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
#
# Version 20250821.213700.1

import os
import inspect
import tkinter as tk
from datetime import datetime

# Local application imports
from settings_and_config.config_manager_save import load_program_config
from src.program_shared_values import setup_shared_values
from ref.ref_file_paths import DATA_FOLDER_PATH

# --- Version Information ---
current_version = "20250821.213700.1"
current_version_hash = 20250821 * 213700 * 1
current_file = os.path.basename(__file__)

def initialize_application(app_instance):
    """
    Main function to orchestrate the application's initialization sequence.
    """
    current_function = inspect.currentframe().f_code.co_name
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - 🚀 🟢 Starting application initialization sequence.")
    
    try:
        _create_required_folders()
        
        app_instance.program_config = load_program_config()
        print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ✅ Configuration loaded.")
        
        # Setup shared Tkinter variables
        _setup_initial_settings(app_instance)
        print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ✅ Shared values initialized.")
        
        # --- REMOVED ---
        # The call to restore_last_used_settings was removed from here.
        # It must be called AFTER the GUI console is created.

        print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - 🚀 ✅ Application initialization complete! All systems go!")
    
    except Exception as e:
        print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ❌ A critical error occurred during initialization: {e}")
        raise

def _create_required_folders():
    """
    Ensures that all necessary data and configuration folders exist.
    """
    current_function = inspect.currentframe().f_code.co_name
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - 📂 🟢 Checking for required folders.")
    
    folders_to_create = [DATA_FOLDER_PATH]
    
    try:
        for folder_path in folders_to_create:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ✅ Created folder: {folder_path}")
            else:
                print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - 👍 Folder already exists: {folder_path}")
    except Exception as e:
        print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ❌ Error creating folders: {e}")
                
def _setup_initial_settings(app_instance):
    """
    Sets up the initial Tkinter variables and default values for the application.
    """
    current_function = inspect.currentframe().f_code.co_name
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ⚙️ 🟢 Setting up initial application settings.")
                    
    setup_shared_values(app_instance=app_instance)
    
    app_instance.showtime_parent_tab = None
    
    print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ⚙️ ✅ Initial settings configured.")