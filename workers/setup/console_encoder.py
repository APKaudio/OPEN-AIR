# workers/setup/console_encoder.py

import os
import sys

def configure_console_encoding(console_log_func, debug_log_func): # Added console_log_func and debug_log_func
    # This block ensures the console can handle UTF-8 characters, preventing encoding errors.
    if os.name == 'nt':
        try:
            console_log_func("DEBUG: Entering configure_console_encoding.")
            
            # --- FIX START ---
            # Providing all required arguments to debug_log_func
            debug_log_func(
                message="DEBUG: Attempting to reconfigure stdout encoding to UTF-8.",
                file=os.path.basename(__file__),
                version=app_constants.current_version, # Assuming app_constants is accessible
                function="configure_console_encoding", # String indicating function name
                console_print_func=console_log_func # Pass the console logger
            )
            # --- FIX END ---
            sys.stdout.reconfigure(encoding='utf-8')
            console_log_func("DEBUG: Successfully reconfigured stdout encoding.")
            
            # --- FIX START ---
            # Providing all required arguments to debug_log_func
            debug_log_func(
                message="DEBUG: Attempting to reconfigure stderr encoding to UTF-8.",
                file=os.path.basename(__file__),
                version=app_constants.current_version,
                function="configure_console_encoding",
                console_print_func=console_log_func
            )
            # --- FIX END ---
            sys.stderr.reconfigure(encoding='utf-8')
            console_log_func("DEBUG: Successfully reconfigured stderr encoding.")
        except AttributeError:
            console_log_func("DEBUG: sys.stdout/stderr.reconfigure not available (likely older Python version). Skipping.")
            # Fallback for older Python versions that don't have reconfigure
            pass
        except Exception as e:
            console_log_func(f"WARNING: Exception during console encoding reconfiguration: {e}")
            # Log the exception but continue if possible
            
    else:
        console_log_func("DEBUG: Not on Windows ('nt'), skipping console encoding reconfiguration.")
            
    console_log_func("DEBUG: Exiting configure_console_encoding.")
