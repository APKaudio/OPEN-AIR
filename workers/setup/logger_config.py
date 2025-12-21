# workers/setup/logger_config.py

import pathlib
import display.logger

def configure_logger(data_dir, console_log_func, watchdog_instance):
    # Configure the logger with the correct DATA_DIR
    display.logger.set_log_directory(pathlib.Path(data_dir) / "debug")
    console_log_func("DEBUG: Logger configured via display.logger.set_log_directory.")
    watchdog_instance.pet("initialize_app: logger configured")