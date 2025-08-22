# configuration/logging/logging.py
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
# Version 20250823.234100.2

import os
import inspect
import datetime

# --- Global Scope Variables ---
CURRENT_DATE = datetime.datetime.now().strftime("%Y%m%d")
CURRENT_TIME = datetime.datetime.now().strftime("%H%M%S")
# Note: For hashing, any leading zero in the hour is dropped (e.g., 083015 becomes 83015).
CURRENT_TIME_HASH = int(datetime.datetime.now().strftime("%H%M%S"))
REVISION_NUMBER = 2
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME_HASH * REVISION_NUMBER)
current_file = f"{os.path.basename(__file__)}"

# --- Logging Toggles ---
LOG_TO_TERMINAL = True
LOG_TO_FILE = True
FILE_LOG_PATH = "debug.log"


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
        log_message = f"MAD SCIENTIST LOG: {message} (File: {file}, v{version}, Func: {function})"

        # --- Function logic goes here ---
        if LOG_TO_TERMINAL:
            console_print_func(log_message)

        if LOG_TO_FILE:
            with open(FILE_LOG_PATH, "a") as log_file:
                log_file.write(log_message + "\n")

    except Exception as e:
        if LOG_TO_TERMINAL:
            console_print_func(f"❌ Error in {current_function_name}: {e}")
            console_print_func(f"Arrr, the code be capsized! The error be: {e}")

