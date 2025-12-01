from workers.worker_active_logging import debug_log, console_log
Local_Debug_Enable = False

# The wrapper functions debug_log_switch and console_log_switch are removed
# as the core debug_log and console_log now directly handle Local_Debug_Enable.