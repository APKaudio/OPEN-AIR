# display/logger.py
#
# This module provides a centralized logging utility for the entire application,
# including console output, file writing, and conditional logging.
# It includes functionality for relative timestamps and error file logging.
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
# Version 20251213.000000.1 (Migrated from worker_active_logging.py)

import os
import inspect
import datetime
import pathlib
import json # Used for JSON logging if a payload is passed
import sys
import workers.setup.app_constants as app_constants
from datetime import datetime

# --- Configuration Placeholders (To be set by the main application's config manager) ---
# NOTE: These are temporary global placeholders that a Configuration Manager will eventually set.
global_settings = app_constants.global_settings
# Log file paths (relative to the project root for safety)
FILE_LOG_DIR: pathlib.Path = None # This will be set by the main application

VISA_LOG_FILENAME = "visa_commands.log"
DEBUG_FILE_PATH = None  # This will be dynamically set/updated
ERRORS_LOG_FILENAME = "🔴 ERRORS.log" # NEW CONSTANT FOR ERROR LOGGING

# Global variable to store the current log filename
current_debug_log_filename = None

# --- Constants (No Magic Numbers) ---
MAX_LOG_LENGTH = 150 
TRUNCATION_SUFFIX = " ... [Truncated]"
ERROR_MARKER_CRITICAL = "🔴"
ERROR_MARKER_USER = "❌"

# --- Global Redirectors (To be set by the GUI Application) ---
# These functions will be overwritten by the GUI's text redirectors.
GUI_CONSOLE_PRINT_FUNC = print 
GUI_LOG_TO_DEBUG_CONSOLE_FUNC = lambda x: print(f"GUI_DEBUG: {x}") 
GUI_CLEAR_CONSOLE_FUNC = lambda: None
# =========================================================================

def set_log_directory(path: pathlib.Path):
    """Sets the base directory for log files and ensures it exists."""
    global FILE_LOG_DIR
    FILE_LOG_DIR = path
    _safe_print(f"DEBUG: Attempting to set log directory to: {FILE_LOG_DIR}")
    try:
        if not FILE_LOG_DIR.exists():
            _safe_print(f"DEBUG: Log directory '{FILE_LOG_DIR}' does not exist. Attempting to create...")
            FILE_LOG_DIR.mkdir(parents=True, exist_ok=True)
            _safe_print(f"✅ Created missing log directory: {FILE_LOG_DIR}")
        else:
            _safe_print(f"DEBUG: Log directory '{FILE_LOG_DIR}' already exists.")
    except Exception as e:
        print(f"❌ Critical Error: Failed to create log directory '{FILE_LOG_DIR}': {e}")
        FILE_LOG_DIR = None # Invalidate if creation fails


def _log_to_error_file(message: str):
    # Logs the message to the dedicated ERRORS.log file if it contains a failure marker.
    if ERROR_MARKER_USER in message or ERROR_MARKER_CRITICAL in message:
        _log_to_file(message, ERRORS_LOG_FILENAME)


def get_log_filename():
    # Returns a unique filename based on the current date and minute.
    global current_debug_log_filename
    
    current_minute = datetime.now().strftime("%Y%m%d%H%M")
    if current_debug_log_filename is None or not current_debug_log_filename.startswith(f"📍🐛{current_minute}"):
        current_debug_log_filename = f"📍🐛{current_minute}.log"
        
    return current_debug_log_filename

def _safe_print(message: str):
    # Prints to the console/GUI target, avoiding recursion issues if print is hooked.
    timestamp_prefix = "" # No timestamp prefix as per user's request.

    if 'GUI_CONSOLE_PRINT_FUNC' in globals() and callable(GUI_CONSOLE_PRINT_FUNC):
        GUI_CONSOLE_PRINT_FUNC(f"{timestamp_prefix}{message}")
    else:
        # FALLBACK FIX: Use print() without arguments to avoid file=sys.stderr crash
        print(f"{timestamp_prefix}{message}")
        
def _log_to_file(message: str, log_filename: str):
    # Helper to safely write a message to a file.
    if FILE_LOG_DIR is None:
        print(f"❌ Error: Log directory not set. Cannot write to file '{log_filename}'.", file=sys.stderr)
        return

    log_path = FILE_LOG_DIR / log_filename
    
    try:
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(message + "\n")
            
    except Exception as e:
        print(f"❌ Error writing to log file '{log_path}': {e}")

def _truncate_message(message: str) -> str:
    # Truncates long messages as per spec, specifically targeting numeric-heavy payloads.
    if not global_settings["log_truncation_enabled"]:
        return message

    # Simplified check for a long string that looks like a data dump
    if len(message) > MAX_LOG_LENGTH and all(c.isdigit() or c in '.-+e' for c in message.replace(' ', '').replace(',', '').replace(';', '')):
        return message[:MAX_LOG_LENGTH] + TRUNCATION_SUFFIX
        
    return message


# =========================================================================
# PUBLIC LOGGING API (Called by other modules)
# =========================================================================



def debug_log(message: str, file: str = "N/A", version: str = "N/A", function: str = "N/A", console_print_func=None):
    # Logs a detailed debug message to the specified outputs.
    if not global_settings.get("general_debug_enabled", False):
        return
        
    # Truncate the message before prepending metadata
    truncated_message = _truncate_message(message)
    now = datetime.now()
    # The full log entry format: [EMOJI] [MESSAGE] | [FILE] | [VERSION] Function: [FUNCTION]
    timestamp_prefix = now.strftime("%Y%m%d%H%M%S")
    
    log_entry = f"{timestamp_prefix}💬{truncated_message}📄{file}🗄️{version}🧩{function}"

    # 1. Log to console output
    if global_settings["debug_to_terminal"]:
        if console_print_func and callable(console_print_func):
            console_print_func(log_entry)
        else:
            # Fallback to GUI_CONSOLE_PRINT_FUNC or standard print
            if 'GUI_CONSOLE_PRINT_FUNC' in globals() and callable(GUI_CONSOLE_PRINT_FUNC):
                GUI_CONSOLE_PRINT_FUNC(log_entry)
            else:
                print(log_entry)

    # Determine if this is an error log entry
    is_error_message = ERROR_MARKER_USER in truncated_message or ERROR_MARKER_CRITICAL in truncated_message

    # 2. Log to main debug file (always if debug_to_file is enabled)
    if global_settings["debug_to_file"] and not is_error_message: # Only log to main debug if not an error message
        _log_to_file(log_entry, get_log_filename())
    
    # 3. Log to errors file if it contains the marker
    if is_error_message:
        _log_to_file(log_entry, ERRORS_LOG_FILENAME) # Directly call _log_to_file with ERRORS_LOG_FILENAME


# PUBLIC API: Implemented as per the user's explicit request.

