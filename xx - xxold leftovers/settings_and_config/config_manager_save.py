# settings_and_config/config_manager.py
#
# This file handles loading and saving application settings to 'config.ini'.
# It now uses primitive print statements for logging during initialization.
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
# Version 20250821.212000.1 (FIXED: Removed duplicate function)

import os
import inspect
import configparser
from datetime import datetime
import tkinter as tk

# Assuming these ref files exist and are correct
from ref.ref_file_paths import CONFIG_FILE_PATH, DATA_FOLDER_PATH
from ref.ref_program_default_values import DEFAULT_CONFIG

# --- Version Information ---
current_version = "20250821.212000.1"
current_file = os.path.basename(__file__)

def load_program_config():
    """
    Loads configuration from config.ini. If the file doesn't exist, or if it's
    missing sections/keys, it creates/updates it with default values from
    DEFAULT_CONFIG, preserving existing user settings.
    """
    current_function = inspect.currentframe().f_code.co_name
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - 🔧 🟢 Loading configuration.")
    
    config = configparser.ConfigParser()
    config.read_dict(DEFAULT_CONFIG)
    
    try:
        if not os.path.exists(DATA_FOLDER_PATH):
            os.makedirs(DATA_FOLDER_PATH)
            print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ✅ Created settings directory: {DATA_FOLDER_PATH}")

        if os.path.exists(CONFIG_FILE_PATH):
            config.read(CONFIG_FILE_PATH)
            print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ✅ Configuration loaded from {CONFIG_FILE_PATH}.")
        else:
            print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - 🟡 Config file not found. A new one will be created with default values.")

        with open(CONFIG_FILE_PATH, 'w') as configfile:
            config.write(configfile)
        print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ✅ Configuration file is up-to-date.")

    except Exception as e:
        print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ❌ Error loading/healing configuration: {e}. Falling back to in-memory defaults.")
        config.read_dict(DEFAULT_CONFIG)

    return config

def save_program_config(config):
    """Saves the provided configuration object to the config.ini file."""
    current_function = inspect.currentframe().f_code.co_name
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open(CONFIG_FILE_PATH, 'w') as configfile:
            config.write(configfile)
        print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ✅ Configuration saved to {CONFIG_FILE_PATH}.")
    except Exception as e:
        print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ❌ Error saving configuration: {e}.")

# --- REMOVED ---
# The restore_last_used_settings function has been removed from this file
# to prevent circular dependencies and duplicate definitions. Its sole location
# is now in 'restore_settings_logic.py'.
