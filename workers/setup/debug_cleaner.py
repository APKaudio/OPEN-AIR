# workers/setup/debug_cleaner.py

import os

def clear_debug_directory(data_dir, console_log_func, watchdog_instance):
    # Clear debug directory
    debug_dir = os.path.join(data_dir, 'debug')
    if os.path.exists(debug_dir):
        for filename in os.listdir(debug_dir):
            file_path = os.path.join(debug_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                console_log_func(f"Failed to delete {file_path}. Reason: {e}")
    watchdog_instance.pet("initialize_app: cleared debug dir")
