# workers/setup/app_constants.py

# Version and Debugging Constants
Current_Date = 20251215  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 58 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)
LOCAL_DEBUG_ENABLE = True  # Set to True to enable local debug logging
 

# --- Global Settings ---
global_settings = {
    "general_debug_enabled": True, # The main toggle for debug messages
    "debug_to_terminal": False,     # Output debug to the terminal/IDE console
    "debug_to_file": True,         # Output debug to the debug log file
    "log_truncation_enabled": True, # Truncate large numeric payloads
    "include_console_messages_to_debug_file": True, # Include  output in debug file
    "#log_visa_commands_enabled": True, # Log all SCPI commands sent/received
    "include_visa_messages_to_debug_file": True, # Include VISA logs in the main debug file
    "debug_to_gui_console": True,  # Output debug to the in-app console
    "include_timestamp_in_debug": True, # NEW: Include MM.SS timestamp in debug output
}


