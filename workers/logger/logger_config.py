# workers/setup/logger_config.py

import pathlib
from workers.logger.logger import console_log, debug_log, set_log_directory 

def configure_logger(data_dir, console_log_func):
    # Configure the logger with the correct 
    set_log_directory(pathlib.Path(data_dir) / "debug")
    console_log_func("DEBUG: Logger configured via workers.logger.logger.set_log_directory.")
