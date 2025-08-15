# src/debug_logic.py
#
# This module centralizes all debug and console logging functionality for the application.
# It provides functions to print debug messages (which can be toggled to go to the terminal
# or the GUI console) and general application messages (which always go to the GUI console).
# It also manages global flags for debug mode and VISA command logging.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
# Version 20250814.214800.1 (FIXED: Removed DEBUG_TO_TERMINAL, updated logging to be more efficient, added a new setting for log truncation to limit long outputs.)

current_version = "20250814.214800.1"
current_version_hash = 20250814 * 214800 * 1

import sys
import os
from datetime import datetime
import inspect
import re

# Global variables for debug control - SET TO FALSE BY DEFAULT!
DEBUG_MODE = False
LOG_VISA_COMMANDS = False
DEBUG_TO_FILE = False
INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE = False
LOG_TRUNCATION_ENABLED = False
DEBUG_TO_GUI_CONSOLE = False
INCLUDE_VISA_MESSAGES_TO_DEBUG_FILE = False


# Define log file paths relative to the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG_FILE_PATH = os.path.join(PROJECT_ROOT, 'DATA', 'DEBUG_SOFTWARE.log')
VISA_FILE_PATH = os.path.join(PROJECT_ROOT, 'DATA', 'DEBUG_VISA_COMMANDS.log')

# Reference to the GUI console TextRedirector or original stdout/stderr
_gui_console_stdout_redirector = None
_gui_console_stderr_redirector = None
_original_stdout = sys.stdout
_original_stderr = sys.stderr

_console_log_func_ref = None


def _truncate_message(message: str, max_items=10) -> str:
    """Helper function to truncate long, comma-separated numeric strings."""
    if LOG_TRUNCATION_ENABLED:
        # Match scientific notation and standard float/int patterns
        numeric_pattern = re.compile(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?')
        matches = numeric_pattern.findall(message)
        if len(matches) > max_items:
            truncated_parts = matches[:max_items]
            return f"{', '.join(truncated_parts)}... (truncated)"
    return message


def set_debug_mode(mode: bool):
    global DEBUG_MODE
    DEBUG_MODE = mode
    current_function = inspect.currentframe().f_code.co_name
    if _console_log_func_ref:
        _console_log_func_ref(f"Debug Mode: {'Enabled' if DEBUG_MODE else 'Disabled'}", function=current_function)
    else:
        print(f"DEBUG_MODE set to: {DEBUG_MODE}. (console_log not yet registered)", file=_original_stdout)
    debug_log(f"Debug mode set to: {DEBUG_MODE}. Let the debugging begin!",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)

def set_log_visa_commands_mode(mode: bool):
    global LOG_VISA_COMMANDS
    LOG_VISA_COMMANDS = mode
    current_function = inspect.currentframe().f_code.co_name
    if _console_log_func_ref:
        _console_log_func_ref(f"VISA Command Logging: {'Enabled' if LOG_VISA_COMMANDS else 'Disabled'}", function=current_function)
    else:
        print(f"LOG_VISA_COMMANDS set to: {LOG_VISA_COMMANDS}. (console_log not yet registered)", file=_original_stdout)
    debug_log(f"VISA command logging set to: {LOG_VISA_COMMANDS}. Tracking those commands!",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)

def set_debug_to_file_mode(mode: bool):
    global DEBUG_TO_FILE
    DEBUG_TO_FILE = mode
    current_function = inspect.currentframe().f_code.co_name
    if _console_log_func_ref:
        _console_log_func_ref(f"Debug to File: {'Enabled' if DEBUG_TO_FILE else 'Disabled'}", function=current_function)
    else:
        print(f"Debug logging to file enabled. (console_log not yet registered)", file=_original_stdout)

def set_include_console_messages_to_debug_file_mode(mode: bool):
    global INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE
    INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE = mode
    current_function = inspect.currentframe().f_code.co_name
    if _console_log_func_ref:
        _console_log_func_ref(f"Include Console Messages to Debug File: {'Enabled' if INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE else 'Disabled'}", function=current_function)
    else:
        print(f"INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE set to: {INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE}. (console_log not yet registered)", file=_original_stdout)

def set_log_truncation_mode(mode: bool):
    global LOG_TRUNCATION_ENABLED
    LOG_TRUNCATION_ENABLED = mode
    current_function = inspect.currentframe().f_code.co_name
    if _console_log_func_ref:
        _console_log_func_ref(f"Log Truncation: {'Enabled' if LOG_TRUNCATION_ENABLED else 'Disabled'}", function=current_function)
    else:
        print(f"LOG_TRUNCATION_ENABLED set to: {LOG_TRUNCATION_ENABLED}. (console_log not yet registered)", file=_original_stdout)

def set_include_visa_messages_to_debug_file_mode(mode: bool):
    global INCLUDE_VISA_MESSAGES_TO_DEBUG_FILE
    INCLUDE_VISA_MESSAGES_TO_DEBUG_FILE = mode
    current_function = inspect.currentframe().f_code.co_name
    if _console_log_func_ref:
        _console_log_func_ref(f"Include VISA Messages to Debug File: {'Enabled' if INCLUDE_VISA_MESSAGES_TO_DEBUG_FILE else 'Disabled'}", function=current_function)
    else:
        print(f"INCLUDE_VISA_MESSAGES_TO_DEBUG_FILE set to: {INCLUDE_VISA_MESSAGES_TO_DEBUG_FILE}. (console_log not yet registered)", file=_original_stdout)


def set_debug_redirectors(stdout_redirector, stderr_redirector):
    global _gui_console_stdout_redirector, _gui_console_stderr_redirector
    _gui_console_stdout_redirector = stdout_redirector
    _gui_console_stderr_redirector = stderr_redirector
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"GUI debug redirectors set. All debug messages will now flow to the GUI! Version: {current_version}",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)

def set_console_log_func(func):
    global _console_log_func_ref
    _console_log_func_ref = func
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Console log function registered with debug_logic. Breaking the circular import!",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function,
                special=True)

def _write_to_debug_file(message: str):
    if DEBUG_TO_FILE and DEBUG_FILE_PATH:
        try:
            os.makedirs(os.path.dirname(DEBUG_FILE_PATH), exist_ok=True)
            with open(DEBUG_FILE_PATH, 'a', encoding='utf-8') as f:
                f.write(message + "\n")
        except Exception as e:
            print(f"ERROR: Failed to write to debug log file {DEBUG_FILE_PATH}: {e}", file=_original_stderr)

def _write_to_visa_file(message: str):
    if LOG_VISA_COMMANDS and VISA_FILE_PATH:
        try:
            os.makedirs(os.path.dirname(VISA_FILE_PATH), exist_ok=True)
            with open(VISA_FILE_PATH, 'a', encoding='utf-8') as f:
                f.write(message + "\n")
        except Exception as e:
            print(f"ERROR: Failed to write to VISA log file {VISA_FILE_PATH}: {e}", file=_original_stderr)

def clear_debug_log_file(file_path: str):
    current_function = inspect.currentframe().f_code.co_name
    if os.path.exists(file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"--- Debug Log Cleared: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            if _console_log_func_ref:
                _console_log_func_ref(f"✅ Debug log file cleared: {file_path}", function=current_function)
            else:
                print(f"✅ Debug log file cleared: {file_path}", file=_original_stdout)
            debug_log(f"Debug log file cleared.",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
        except Exception as e:
            if _console_log_func_ref:
                _console_log_func_ref(f"❌ Error clearing debug log file {file_path}: {e}", function=current_function)
            else:
                print(f"❌ Error clearing debug log file {file_path}: {e}", file=_original_stderr)
            debug_log(f"ERROR: Failed to clear debug log file: {e}",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
    else:
        if _console_log_func_ref:
            _console_log_func_ref(f"ℹ️ Debug log file does not exist: {file_path}. Nothing to clear.", function=current_function)
        else:
            print(f"ℹ️ Debug log file does not exist: {file_path}. Nothing to clear.", file=_original_stdout)
        debug_log(f"Debug log file does not exist. Cannot clear.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

def debug_log(message, file=None, version=None, function=None, special=False):
    if not DEBUG_MODE:
        return

    timestamp = datetime.now().strftime("%M.%S")
    
    prefix_parts = []
    if file:
        prefix_parts.append(os.path.basename(file))
    if version:
        prefix_parts.append(f"v{version}")
    if function:
        prefix_parts.append(function)
    if special:
        prefix_parts.append("SPECIAL")

    prefix = f"[{' | '.join(prefix_parts)}] " if prefix_parts else ""
    
    full_message = f"🚫🐛 [{timestamp}] {prefix}{_truncate_message(message)}"
    
    if DEBUG_TO_FILE:
        _write_to_debug_file(full_message)

    if _gui_console_stdout_redirector and DEBUG_TO_GUI_CONSOLE:
        _gui_console_stdout_redirector.write(full_message + "\n")
    else:
        print(full_message, file=_original_stdout)


def log_visa_command(command, direction="SENT"):
    if not LOG_VISA_COMMANDS:
        return

    timestamp = datetime.now().strftime("%M.%S")
    log_message = f"🌲 [{timestamp}] {direction}: {_truncate_message(command)}"
    
    _write_to_visa_file(log_message)
    
    if INCLUDE_VISA_MESSAGES_TO_DEBUG_FILE and DEBUG_TO_FILE:
        _write_to_debug_file(log_message)

    if _gui_console_stdout_redirector:
        _gui_console_stdout_redirector.write(log_message + "\n")
    else:
        print(log_message, file=_original_stdout)
