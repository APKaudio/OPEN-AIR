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


# Record the application start time for relative timestamps
APP_START_TIME = datetime.datetime.now()


# --- Global Scope Variables (as per Section 4.4) ---
current_version = "20251213.000000.1" # Version for this specific logging module
current_version_hash = (20251213 * 0 * 1)
current_file = f"{os.path.basename(__file__)}"
Local_Debug_Enable = True


# --- Configuration Placeholders (To be set by the main application's config manager) ---
# NOTE: These are temporary global placeholders that a Configuration Manager will eventually set.
global_settings = {
    "general_debug_enabled": True, # The main toggle for debug messages
    "debug_to_terminal": True,     # Output debug to the terminal/IDE console
    "debug_to_file": True,         # Output debug to the debug log file
    "log_truncation_enabled": True, # Truncate large numeric payloads
    "include_console_messages_to_debug_file": True, # Include console_log output in debug file
    "log_visa_commands_enabled": True, # Log all SCPI commands sent/received
    "include_visa_messages_to_debug_file": True, # Include VISA logs in the main debug file
    "debug_to_gui_console": True,  # Output debug to the in-app console
    "include_timestamp_in_debug": True, # NEW: Include MM.SS timestamp in debug output
}
# Log file paths (relative to the project root for safety)
FILE_LOG_DIR: pathlib.Path = None # This will be set by the main application

VISA_LOG_FILENAME = "visa_commands.log"
DEBUG_FILE_PATH = None  # This will be dynamically set/updated
ERRORS_LOG_FILENAME = "ERRORS.log" # NEW CONSTANT FOR ERROR LOGGING

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
    
    current_minute = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    if current_debug_log_filename is None or not current_debug_log_filename.startswith(f"debug_log_{current_minute}"):
        current_debug_log_filename = f"debug_log_{current_minute}.log"
        
    return current_debug_log_filename

def _safe_print(message: str):
    # Prints to the console/GUI target, avoiding recursion issues if print is hooked.
    timestamp_prefix = ""
    if global_settings.get("include_timestamp_in_debug"):
        elapsed_seconds = (datetime.datetime.now() - APP_START_TIME).total_seconds()
        minutes = int(elapsed_seconds // 60)
        seconds = int(elapsed_seconds % 60)
        milliseconds = int((elapsed_seconds - int(elapsed_seconds)) * 1000)
        timestamp_prefix = f"{minutes:02d}.{seconds:02d}.{milliseconds:03d} "

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

def console_log(message: str, local_debug_enabled: bool = None):
    # Logs a user-facing message to the console and conditionally to the debug file.
    if local_debug_enabled is None:
        frame = inspect.currentframe().f_back
        if frame:
            frame = frame.f_back # Go up one more frame to get the caller of console_log
        local_debug_enabled = frame.f_globals.get('Local_Debug_Enable', False) if frame else False

    if local_debug_enabled:
        # 1. Log to console output
        if global_settings["debug_to_terminal"]:
            _safe_print(message)
            
        # 2. Log to main debug file
        if global_settings["debug_to_file"] and global_settings["include_console_messages_to_debug_file"]:
            _log_to_file(f"🖥️ {message}", get_log_filename())

    # 3. Log to errors file if it contains the marker (always, regardless of debug flag)
    _log_to_error_file(message)

def debug_log(message: str, file: str, version: str, function: str, console_print_func):
    # Logs a detailed debug message to the specified outputs.
    if not global_settings["general_debug_enabled"]:
        return
        
    # Get the calling frame
    frame = inspect.currentframe().f_back
    
    # Check if Local_Debug_Enable is defined and True in the calling frame
    local_debug_enabled = frame.f_globals.get('Local_Debug_Enable', False)

    if local_debug_enabled:        # Truncate the message before prepending metadata
        truncated_message = _truncate_message(message)
        
        # The full log entry format: [EMOJI] [MESSAGE] | [FILE] | [VERSION] Function: [FUNCTION]
        timestamp_prefix = ""
        if global_settings.get("include_timestamp_in_debug"):
            elapsed_seconds = (datetime.datetime.now() - APP_START_TIME).total_seconds()
            minutes = int(elapsed_seconds // 60)
            seconds = int(elapsed_seconds % 60)
            milliseconds = int((elapsed_seconds - int(elapsed_seconds)) * 1000)
            timestamp_prefix = f"{minutes:02d}.{seconds:02d}.{milliseconds:03d} "
        
        log_entry = f"{timestamp_prefix}{truncated_message} | {file} | {version} Function: {function}"

        # 1. Log to console output
        if global_settings["debug_to_terminal"]:
            console_print_func(log_entry)

        # 2. Log to main debug file
        if global_settings["debug_to_file"]:
            _log_to_file(log_entry, get_log_filename())
            
        # 3. Log to errors file if it contains the marker
        _log_to_error_file(message)


# PUBLIC API: Implemented as per the user's explicit request.
def log_visa_command(command: str, direction: str):
    # Logs SCPI commands sent to and responses received from the instrument.
    if not global_settings["log_visa_commands_enabled"]:
        return
        
    direction_emoji = "➡️" if direction == "SENT" else "⬅️"
    
    # Truncate command, primarily for large query responses
    truncated_command = _truncate_message(command)
    
    # The log entry format for the visa file is simple
    log_entry = f"🐐 {direction_emoji} {direction}: {truncated_command}"

    # 1. Log to VISA-specific file
    _log_to_file(log_entry, VISA_LOG_FILENAME)

    # 2. Conditionally log to main debug file
    if global_settings["include_visa_messages_to_debug_file"]:
        _log_to_file(f"🐐 {log_entry}", get_log_filename())
        
    # 3. Log to errors file if it contains the marker
    _log_to_error_file(log_entry)
