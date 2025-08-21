# ref/ref_file_paths.py
#
# This file centralizes all file path definitions for the application, ensuring a
# single source of truth for file and folder locations. This is a core component
# for maintaining consistency and avoiding hard-coded paths.
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
# Version 20250821.144000.1
# NEW: Created a new file to centralize all application file and folder paths.

import os

# --- Version Information ---
current_version = "20250821.144000.1"
current_version_hash = (20250821 * 144000 * 1)
current_file = f"{os.path.basename(__file__)}"

# --- File Paths ---

# ref/ref_file_paths.py
#
# This file centralizes all file path definitions for the application, ensuring a
# single source of truth for file and folder locations. This is a core component
# for maintaining consistency and avoiding hard-coded paths.
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
# Version 20250821.144000.2
# NEW: Created a new file to centralize all application file and folder paths.

import os

# --- Version Information ---
current_version = "20250821.144000.2"
current_version_hash = (20250821 * 144000 * 2)
current_file = f"{os.path.basename(__file__)}"

# --- File Paths ---

# The base directory is assumed to be one level above this file's location.
# This ensures that the paths are relative to the project root.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The main data folder where all configuration and data files are stored.
DATA_FOLDER_PATH = os.path.join(BASE_DIR, 'DATA')

# Specific file paths within the data folder.
CONFIG_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'config.ini')
PRESETS_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'presets.json')
MARKERS_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'markers.json')
VISA_COMMANDS_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'visa_commands.log')
DEBUG_COMMANDS_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'debug.log')