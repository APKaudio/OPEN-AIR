# workers/setup/debug_cleaner.py

import os
import sys

def clear_debug_directory(data_dir, console_log_func):
    console_log_func("DEBUG: Entering clear_debug_directory.")
    # Clear debug directory
    debug_dir = os.path.join(data_dir, 'debug')
    if os.path.exists(debug_dir):
        console_log_func(f"DEBUG: Debug directory found: {debug_dir}. Proceeding to clear contents.")
        try:
            filenames = os.listdir(debug_dir) # Get list of files before deletion
            console_log_func(f"DEBUG: Found {len(filenames)} items in debug directory.")
            for filename in filenames:
                file_path = os.path.join(debug_dir, filename)
                try:
                    console_log_func(f"DEBUG: Attempting to delete: {file_path}")
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        console_log_func(f"DEBUG: Successfully deleted: {file_path}")
                except Exception as e:
                    console_log_func(f"Failed to delete {file_path}. Reason: {e}")
            console_log_func("DEBUG: Finished attempting to clear debug directory.")
        except Exception as e:
            console_log_func(f"Error listing or deleting files in {debug_dir}. Reason: {e}")

            
    else:
        console_log_func(f"DEBUG: Debug directory not found: {debug_dir}. Skipping clear.")
            
