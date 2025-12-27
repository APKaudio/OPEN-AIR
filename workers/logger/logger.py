# workers/logger/logger.py
# Author: Anthony Peter Kuzub
# Description: Handles logging with a temporal buffer for pre-initialization messages.
# Version: 20251226.004000.8

import os
import time
from datetime import datetime
from workers.mqtt.setup.config_reader import Config 

app_constants = Config.get_instance() 

# --- GLOBALS ---
_log_directory = None
_log_buffer = [] 

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
            if app_constants.global_settings.get("debug_to_terminal", True):
                print(f"📁 Created log directory: {_log_directory}")
        except OSError as e:
            if app_constants.global_settings.get("debug_to_terminal", True):
                print(f"❌ Error creating log directory: {e}")
            return

    # 🧪 FLUSH THE BUFFER
    if _log_buffer:
        if app_constants.global_settings.get("debug_to_terminal", True):
            print(f"🧪 Great Scott! Flushing {len(_log_buffer)} buffered messages to the timeline!")
        for timestamp, level, message, context_data in _log_buffer:
            _write_to_file(timestamp, level, message, context_data)
        
        _log_buffer = [] 

def debug_logger(message: str, **kwargs):
    """
    Public function to log debug messages.
    Receives 'message' and unpacked dictionary from _get_log_args() (file, function, version) in kwargs.
    """
    # Generate timestamp immediately so screen and file (if unbuffered) are close
    # Note: The buffer logic generates its own timestamp, but for screen printing we need one now.
    current_ts = f"{time.time():.6f}"
    
    # 1. TERMINAL OUTPUT (Immediate & Formatted)
    if app_constants.global_settings.get('debug_to_terminal', True):
        # Extract context
        c_file = kwargs.get('file', '?')
        c_func = kwargs.get('function', '?')
        
        # Clean the name (remove .py, remove _, remove brackets)
        clean_context = _clean_context_string(c_file, c_func)
        
        # Format: Timestamp Icon CleanContext Message
        # Matches: 1766723800.674347 💬 dynamicguicreatelabelfromconfig Message
        print(f"{current_ts}💬{message}{clean_context}")
    
    # 2. FILE/BUFFER OUTPUT
    _process_and_buffer_log_message("💬 ", message, kwargs)

def console_log(message: str):
    """
    Public function to log console/user messages.
    """
    current_ts = f"{time.time():.6f}"
    # Console logs usually don't have deep context
    print(f"{current_ts}\n🖥️{message}")
    _process_and_buffer_log_message("🖥️", message, {})

# --- Alias for compatibility ---
debug_log = debug_logger 

def _process_and_buffer_log_message(level: str, message: str, context_data: dict):
    """
    Handles buffering or direct writing of log messages based on _log_directory state.
    """
    # Generate High-Precision Unix Timestamp
    timestamp = f"{time.time():.6f}"
    
    if _log_directory is None:
        _log_buffer.append((timestamp, level, message, context_data))
    elif app_constants.global_settings.get('debug_to_file', False): 
        _write_to_file(timestamp, level, message, context_data)

def _clean_context_string(c_file, c_func):
    """
    Helper to strip .py, remove underscores, and remove whitespace.
    Input: "my_script.py", "my_func"
    Output: "myscriptmyfunc "
    """
    # 1. Handle defaults
    if c_file == '?' and c_func == '?':
        return ""

    # 2. Stringify and clean file: remove .py, replace _ with empty string
    clean_file = str(c_file).replace('.py', '').replace('_', ' ')
    
    # 3. Clean function: replace _ with empty string
    clean_func = str(c_func).replace('_', ' ') if c_func != '?' else ""

    # 4. Combine
    # If we have a function, append it. 
    combined = f"{clean_file}/{clean_func}"
    
    # Return with a trailing space so it separates from the message
    return f"{combined} "

def _write_to_file(timestamp, level, message, context_data):
    """Helper to actually write to the disk."""
    try:
        # 1. Filename: YYYYMMDDHHMM.log
        ts_float = float(timestamp)
        file_time_str = datetime.fromtimestamp(ts_float).strftime("%Y%m%d%H%M")
        log_filename = f"📍🐛{file_time_str}.log"
        file_path = os.path.join(_log_directory, log_filename)
        
        # 2. Extract Context (File, Function)
        c_file = context_data.get('file', '?')
        c_func = context_data.get('function', '?')

        with open(file_path, "a", encoding="utf-8") as f:
            # Format: Timestamp Level CleanContext Message
            # Note: Level usually contains the icon and space, e.g., "💬 "
            
            clean_context = _clean_context_string(c_file, c_func)
            
            # The 'level' var comes in with a space usually ("💬 "), so we strip it to control spacing manually
            # or just trust the input. The user wants: Timestamp 💬 CleanName
            
            clean_level = level.strip() 

            log_entry = f"{timestamp}{message}{clean_level}{clean_context}"
            
            # Append extras if they exist (excluding file/function since we used them)
            extras = {k: v for k, v in context_data.items() if k not in ['file', 'function']}
            if extras:
                log_entry += f" 🧩 {extras}"

            f.write(log_entry + "\n")
            
    except Exception as e:
        print(f"❌ Critical Failure writing to log: {e}")