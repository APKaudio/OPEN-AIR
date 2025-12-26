# workers/logger/logger.py
# Author: Anthony Peter Kuzub
# Description: Handles logging with a temporal buffer for pre-initialization messages.

import os
import inspect
from datetime import datetime
from workers.mqtt.setup.config_reader import Config # Import the Config class
app_constants = Config.get_instance() # Get the singleton instance

# --- GLOBALS ---
_log_directory = None
_log_buffer = []  # <--- The Temporal Buffer

def set_log_directory(directory):
    """
    Sets the log directory and flushes any buffered messages to the timeline.
    """
    global _log_directory, _log_buffer
    _log_directory = directory
    
    # Create directory if it doesn't exist
    if not os.path.exists(_log_directory):
        try:
            os.makedirs(_log_directory)
            if app_constants.global_settings["debug_to_terminal"]:
                print(f"📁 Created log directory: {_log_directory}")
        except OSError as e:
            if app_constants.global_settings["debug_to_terminal"]:
                print(f"❌ Error creating log directory: {e}")
            return

    # 🧪 FLUSH THE BUFFER
    if _log_buffer:
        # We use a direct print here to confirm the action in the console
        if app_constants.global_settings["debug_to_terminal"]:
            print(f"🧪 Great Scott! Flushing {len(_log_buffer)} buffered messages to the timeline!")
        for timestamp, level, message, args in _log_buffer:
            _write_to_file(timestamp, level, message, args)
        
        _log_buffer = [] # Clear the buffer

def debug_log(message: str, **kwargs):
    """
    Public function to log debug messages.
    """
    _write_to_log("DEBUG", message, kwargs)

def console_log(message: str):
    """
    Public function to log console/user messages.
    """
    # Print to actual console immediately
    print(message)
    _write_to_log("💬", message, {})

def _write_to_log(level: str, message: str, args: dict = None):
    """
    Writes a formatted message to the debug log file if enabled.
    This is the lowest-level logging function.
    """
    if not app_constants.global_settings['debug_to_file']:
        return


def _write_to_file(timestamp, level, message, args):
    """Helper to actually write to the disk."""
    try:
        # Format: 20251224.log
        log_filename = f"📍🐛{timestamp[:-6]}.log" 
        file_path = os.path.join(_log_directory, log_filename)
        
        with open(file_path, "a", encoding="utf-8") as f:
            # Format: Timestamp 💬 Message 🧩Args...
            # Note: We strip the emoji from level if it's already in message to avoid duplicates
            f.write(f"{timestamp}{level} {message}")
            if args:
                # Convert args to string representation for the log
                arg_str = str(args)
                f.write(f"🧩{arg_str}")
            f.write("\n")
    except Exception as e:
        print(f"❌ Critical Failure writing to log: {e}")