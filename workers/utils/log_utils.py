# workers/utils/log_utils.py
import inspect
import os
from workers.mqtt.setup.config_reader import app_constants

def _get_log_args():
    """Helper to get common debug_log arguments.
    
    Returns:
        dict: A dictionary containing 'file', 'version', and 'function' 
              to be used with debug_log.
    """
    if app_constants.PERFORMANCE_MODE: # This was the line where PERFORMANCE_MODE was undefined
        return {} # Return empty dict in performance mode
        
    # This frame navigation is crucial.
    # inspect.currentframe() is _get_log_args
    # f_back is the caller of _get_log_args (e.g., debug_log(...))
    # f_back.f_back is the actual function that called debug_log.
    frame = inspect.currentframe().f_back.f_back
    
    # Ensure app_constants has current_version defined.
    # If not, a default or error handling might be needed.
    # Assuming app_constants.current_version is always available.
    
    return {
        "file": os.path.basename(frame.f_code.co_filename),
        "version": app_constants.CURRENT_VERSION,
        "function": frame.f_code.co_name
    }