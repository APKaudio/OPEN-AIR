from workers.worker_active_logging import debug_log, console_log
ENABLE_DEBUG = False

def debug_log_switch(message, file, version, function, console_print_func):
    if ENABLE_DEBUG:
        debug_log_switch(message, file, version, function, console_print_func)

def console_log_switch(message):
    if ENABLE_DEBUG:
        console_log_switch(message)

