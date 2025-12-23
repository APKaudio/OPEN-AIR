# workers/setup/console_encoder.py

import os
import sys

def configure_console_encoding(_func, debug_log_func): # Added _func and debug_log_func
    # This block ensures the console can handle UTF-8 characters, preventing encoding errors.
    if os.name == 'nt':
        try:
            _func("DEBUG: Entering configure_console_encoding.")
            
            # --- FIX START ---
            # Providing all required arguments to debug_log_func
            debug_log_func(
                message="DEBUG: Attempting to reconfigure stdout encoding to UTF-8.",
                file=os.path.basename(__file__),
                version=app_constants.current_version, # Assuming app_constants is accessible
                function="configure_console_encoding", # String indicating function name
                
                )

            # --- FIX END ---
            sys.stdout.reconfigure(encoding='utf-8')
            _func("DEBUG: Successfully reconfigured stdout encoding.")
            
            # --- FIX START ---
            # Providing all required arguments to debug_log_func
            debug_log_func(
                message="DEBUG: Attempting to reconfigure stderr encoding to UTF-8.",
                file=os.path.basename(__file__),
                version=app_constants.current_version,
                function="configure_console_encoding",
                
                )
            # --- FIX END ---
            sys.stderr.reconfigure(encoding='utf-8')
            _func("DEBUG: Successfully reconfigured stderr encoding.")
        except AttributeError:
            _func("DEBUG: sys.stdout/stderr.reconfigure not available (likely older Python version). Skipping.")
            # Fallback for older Python versions that don't have reconfigure
            pass
        except Exception as e:
            _func(f"WARNING: Exception during console encoding reconfiguration: {e}")
            # Log the exception but continue if possible
            
    else:
        _func("DEBUG: Not on Windows ('nt'), skipping console encoding reconfiguration.")
            
    _func("DEBUG: Exiting configure_console_encoding.")
