# workers/worker_active_logging.py
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251129  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 1 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


# A central utility file to provide standardized logging functions for the entire application,
# including console output, file writing, and conditional logging for specialized data like VISA commands.
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
# Version 20251026.225659.1
# DEFINITIVE FIX: Removed all direct references to sys.stdout and sys.stderr in utility functions 
#                 to prevent fatal crashes during module loading in specific thread contexts.
# NEW FEATURE: Logs messages containing '❌' or '🔴' to a dedicated "ERRORS.log" file.

import os
import inspect
import datetime
import pathlib
import json # Used for JSON logging if a payload is passed
import sys

from workers.utils.worker_project_paths import GLOBAL_PROJECT_ROOT


# --- Global Scope Variables (as per Section 4.4) ---
current_version = "20251026.225659.1"
current_version_hash = (20251026 * 225659 * 1)
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
}
# Log file paths (relative to the project root for safety)
FILE_LOG_DIR = GLOBAL_PROJECT_ROOT / "DATA" / "debug"

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
    if 'GUI_CONSOLE_PRINT_FUNC' in globals() and callable(GUI_CONSOLE_PRINT_FUNC):
        GUI_CONSOLE_PRINT_FUNC(message)
    else:
        # FALLBACK FIX: Use print() without arguments to avoid file=sys.stderr crash
        print(message)
        
def _log_to_file(message: str, log_filename: str):
    # Helper to safely write a message to a file.
    log_path = FILE_LOG_DIR / log_filename
    
    # --- NEW FIX: Ensure the log directory exists before trying to open the file. ---
    try:
        if not FILE_LOG_DIR.exists():
            FILE_LOG_DIR.mkdir(parents=True, exist_ok=True)
            _safe_print(f"✅ Created missing log directory: {FILE_LOG_DIR}")
    except Exception as e:
        # FALLBACK FIX: Use simple print.
        print(f"❌ Critical Error: Failed to create log directory '{FILE_LOG_DIR}': {e}")
        return # Abort logging if directory creation fails
    # --- END NEW FIX ---
    
    try:
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(message + "\n")
            
    except Exception as e:
        # FALLBACK FIX: Use simple print.
        print(f"❌ Error writing to log file '{log_path}': {e}")

def _truncate_message(message: str) -> str:
    # Truncates long messages as per spec, specifically targeting numeric-heavy payloads.
    if not global_settings["log_truncation_enabled"]:
        return message

    # Simplified check for a long string that looks like a data dump
    if len(message) > MAX_LOG_LENGTH and all(c.isdigit() or c in '.-+e' for c in message.replace(' ', '').replace(',', '').replace(';', '')):
        return message[:MAX_LOG_LENGTH] + TRUNCATION_SUFFIX
    elif len(message) > MAX_LOG_LENGTH and message.count('/') > 5:
        # Also truncate long MQTT topic paths
        return message[:MAX_LOG_LENGTH] + TRUNCATION_SUFFIX
        
    return message


# =========================================================================
# PUBLIC LOGGING API (Called by other modules)
# =========================================================================

def console_log(message: str):
    # Logs a user-facing message to the console and conditionally to the debug file.

    frame = inspect.currentframe().f_back
    if 'Local_Debug_Enable' in frame.f_globals and frame.f_globals['Local_Debug_Enable']:
        # 1. Log to console output
        if global_settings["debug_to_terminal"]:
            _safe_print(message)
            
        # 2. Log to main debug file
        if global_settings["debug_to_file"] and global_settings["include_console_messages_to_debug_file"]:
            # We don't prepend file/version/function for console logs
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
    if 'Local_Debug_Enable' in frame.f_globals and frame.f_globals['Local_Debug_Enable']:
        # Truncate the message before prepending metadata
        truncated_message = _truncate_message(message)
        
        # The full log entry format: [EMOJI] [MESSAGE] | [FILE] | [VERSION] Function: [FUNCTION]
        log_entry = f"{truncated_message} | {file} | {version} Function: {function}"

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
