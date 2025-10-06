# configuration/logging.py
#
# A simple utility file to provide standardized debugging functions for the application.
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
# Version 20250822.215200.1

import os
import inspect
import datetime
import pathlib

# --- Global Scope Variables ---
# ⏰ As requested, the version is now hardcoded to the time this file was generated.
# The version strings and numbers below are static and will not change at runtime.
current_version = "20250822.215200.1"
# The hash calculation drops the leading zero from the hour, but 21 has no leading zero.
current_version_hash = (20250822 * 215200 * 1)
current_file = f"{os.path.basename(__file__)}"

# --- Logging Toggles ---
LOG_TO_TERMINAL = True
LOG_TO_FILE = True
# The log file path is now relative to the parent directory.
FILE_LOG_DIR = pathlib.Path("DATA/debug")

# Global variable to store the current log filename
current_log_filename = None

def get_log_filename():
    """
    Returns a unique filename based on the current date and minute.
    """
    global current_log_filename
    
    # Check if the filename needs to be updated (new minute)
    current_minute = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    if current_log_filename is None or not current_log_filename.startswith(f"debug_log_{current_minute}"):
        current_log_filename = f"debug_log_{current_minute}.log"
        
    return current_log_filename

def console_log(message: str):
    """
    Prints a message to the console if the toggle is enabled.
    """
    current_function_name = inspect.currentframe().f_code.co_name

    try:
        if LOG_TO_TERMINAL:
            print(message)

    except Exception as e:
        if LOG_TO_TERMINAL:
            print(f"❌ Error in {current_function_name}: {e}")

def debug_log(message: str, file: str, version: str, function: str, console_print_func):
    """
    Prints a detailed debug message with a 'mad scientist' personality,
    directing output based on the global toggles.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    
    try:
        # Re-formatting the message to better match the 'mad scientist' persona
        log_message = f"💡📝{message} | {file} | {version} Function: {function}"

        # --- Function logic goes here ---
        if LOG_TO_TERMINAL:
            console_print_func(log_message)

        if LOG_TO_FILE:
            # We explicitly open the log file with UTF-8 encoding to support emojis
            log_filename = get_log_filename()
            log_path = FILE_LOG_DIR / log_filename
            
            # Create the DATA directory if it does not exist
            FILE_LOG_DIR.mkdir(exist_ok=True)
            
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write(log_message + "\n")

    except Exception as e:
        if LOG_TO_TERMINAL:
            console_print_func(f"❌ Error in {current_function_name}: {e}")