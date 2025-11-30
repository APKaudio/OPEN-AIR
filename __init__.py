# __init__.py
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251129  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 1 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)

from workers.worker_active_logging import debug_log, console_log
ENABLE_DEBUG = False

def debug_log_switch(message, file, version, function, console_print_func):
    if ENABLE_DEBUG:
        debug_log_switch(message, file, version, function, console_print_func)

def console_log_switch(message):
    if ENABLE_DEBUG:
        console_log_switch(message)

