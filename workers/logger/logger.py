# workers/logger/logger.py
# Author: Anthony Peter Kuzub
# Description: Handles logging with a temporal buffer for pre-initialization messages.
# Version: 20251226.004000.8

import os
import time
from datetime import datetime
from workers.utils.log_utils import _get_log_args # Import _get_log_args

# Global cache for Config instance
_config_instance_cache = None

# --- GLOBALS ---
_log_directory = None
_log_buffer = [] 

def _get_config_instance():
    global _config_instance_cache
    if _config_instance_cache is None:
        from workers.setup.config_reader import Config
        # If Config._instance is still None, it means Config is not yet fully initialized.
        # In this very early stage, we might have to use some sensible defaults.
        if Config._instance is None:
            class DummyConfig:
                PERFORMANCE_MODE = False
                @property
                def global_settings(self):
                    return {"debug_to_terminal": True, "debug_to_file": False, "debug_enabled": False} # Sensible defaults
            _config_instance_cache = DummyConfig()
        else:
            _config_instance_cache = Config._instance
    # Ensure that if the real config has been initialized, we always return that.
    # This covers the case where DummyConfig was used initially.
    from workers.setup.config_reader import Config # Re-import just in case
    if Config._instance is not None:
        return Config._instance
    return _config_instance_cache

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
            debug_logger(message=f"📁 Created log directory: {_log_directory}", **_get_log_args())
        except OSError as e:
            debug_logger(message=f"❌ Error creating log directory: {e}", **_get_log_args())
            return

    # 🧪 FLUSH THE BUFFER
    if _log_buffer:
        debug_logger(message=f"🧪 Great Scott! Flushing {len(_log_buffer)} buffered messages to the timeline!", **_get_log_args())
        for timestamp, level, message, context_data in _log_buffer:
            _write_to_file(timestamp, level, message, context_data)
        
        _log_buffer = []

def debug_logger(message: str, **kwargs):
    """
    Public function to log debug messages.
    Receives 'message' and unpacked dictionary from _get_log_args() (file, function, version) in kwargs.
    """
    config_instance = _get_config_instance() # Get the Config instance

    # If PERFORMANCE_MODE is enabled, completely silence debug_logger
    if config_instance.PERFORMANCE_MODE: # Use config_instance here
        return
    
    # Generate timestamp immediately so screen and file (if unbuffered) are close
    # Note: The buffer logic generates its own timestamp, but for screen printing we need one now.
    current_ts = f"{time.time():.6f}"
    
    is_error = "ERROR" in message or "❌" in message
    level = "❌" if is_error else "🦆"

    # 1. TERMINAL OUTPUT (Immediate & Formatted)
    if config_instance.global_settings['debug_to_terminal']: # Use config_instance
        # Extract context
        c_file = kwargs.get('file', '?')
        c_func = kwargs.get('function', '?')
        
        # Clean the name (remove .py, remove _, remove brackets)
        clean_context = _clean_context_string(c_file, c_func)
        
        # Format: Timestamp Icon CleanContext Message
        print(f"{current_ts} {message} {level} {clean_context}")
    
    # 2. FILE/BUFFER OUTPUT
    _process_and_buffer_log_message(f"{level} ", message, kwargs)
    
    # 3. WRITE TO ERROR LOG
    if is_error:
        _write_to_error_log(current_ts, level, message, kwargs)

def console_log(message: str):
    """
    Public function to log console/user messages.
    """
    current_ts = f"{time.time():.6f}"
    # Console logs usually don't have deep context
    # Need to check config_instance here too if we want to silence console_log based on DEBUG_TO_TERMINAL
    config_instance = _get_config_instance()
    if config_instance.global_settings['debug_to_terminal']: # Use config_instance
        print(f"{current_ts}🖥️{message}")
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
    else:
        config_instance = _get_config_instance()
        if config_instance.global_settings.get('debug_to_file', False): # Use config_instance
            # Write current message
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
    combined = f"{clean_file}🪿 {clean_func}"
    
    # Return with a trailing space so it separates from the message
    return f"{combined} "

def _write_to_file(timestamp, level, message, context_data):
    """Helper to actually write to the disk."""
    try:
        config_instance = _get_config_instance()
        if not config_instance.global_settings.get('debug_to_file', False):
            return # Don't write to file if debug_to_file is False

        # 1. Filename: YYYYMMDDHHMM.log
        ts_float = float(timestamp)
        file_time_str = datetime.fromtimestamp(ts_float).strftime("%Y%m%d%H%M")
        log_filename = f"📍🐛{file_time_str}.log"
        file_path = os.path.join(_log_directory, log_filename)
        
        # 2. Extract Context (File, Function)
        c_file = context_data.get('file', '?')
        c_func = context_data.get('function', '?')
        clean_context = _clean_context_string(c_file, c_func)
        
        clean_level = level.strip() 

        log_entry = f"{timestamp} {message} {clean_level} {clean_context}"
        
        # Append extras if they exist (excluding file/function since we used them)
        extras = {k: v for k, v in context_data.items() if k not in ['file', 'function']}
        if extras:
            log_entry += f" 🧩 {extras}"

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
            
    except Exception as e:
        print(f"❌ Critical Failure writing to log: {e}")

def _write_to_error_log(timestamp, level, message, context_data):
    """Helper to write error messages to a separate ERRORS.log file."""
    try:
        config_instance = _get_config_instance()
        if not config_instance.global_settings.get('debug_to_file', False):
            return # Don't write to error log if debug_to_file is False

        if not _log_directory:
            return

        error_log_filename = "ERRORS.log"
        file_path = os.path.join(_log_directory, error_log_filename)
        
        c_file = context_data.get('file', '?')
        c_func = context_data.get('function', '?')
        clean_context = _clean_context_string(c_file, c_func)
        
        clean_level = level.strip()

        log_entry = f"{timestamp}{message} {clean_level} {clean_context}"
        
        extras = {k: v for k, v in context_data.items() if k not in ['file', 'function']}
        if extras:
            log_entry += f" 🧩 {extras}"

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
            
    except Exception as e:
        print(f"❌ Critical Failure writing to error log: {e}")
