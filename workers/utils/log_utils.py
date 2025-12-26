# workers/utils/log_utils.py
#
# Utility to capture the context (File, Function, Version) of a log call.
#
# Author: Anthony Peter Kuzub
# Version: 20251226.002000.1
#

import inspect
import os
from workers.mqtt.setup.config_reader import Config

app_constants = Config.get_instance()

def _get_log_args():
    """
    Inspects the call stack to retrieve the filename, function name,
    and 'current_version' of the caller.
    """
    try:
        # 1. Step back one frame to find who called this function
        frame = inspect.currentframe().f_back
        
        if frame:
            # 2. Extract Filename
            filename = os.path.basename(frame.f_code.co_filename)
            
            # 3. Extract Function Name
            function_name = frame.f_code.co_name
            
            # 4. Extract 'current_version' from the caller's globals
            # (As per the Flux Capacitor Protocol: Every file defines current_version)
            version = frame.f_globals.get('current_version', 'Unknown_Ver')
            
            return {
                "file": filename,
                "version": version,
                "function": function_name
            }
            
    except Exception as e:
        # If the stack is unstable, return defaults to prevent a crash
        return {
            "file": "unknown_file",
            "version": "unknown_ver",
            "function": "unknown_func",
            "error": str(e)
        }
    
    # Fallback
    return {
        "file": "unknown",
        "version": "unknown",
        "function": "unknown"
    }