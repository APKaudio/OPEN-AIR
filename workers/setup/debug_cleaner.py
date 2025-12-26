# workers/setup/debug_cleaner.py

import os
import sys
from workers.logger.logger import  debug_logger # import  debug_logger
from workers.utils.log_utils import _get_log_args # Import _get_log_args

def clear_debug_directory(data_dir): # Removed _func argument
    debug_logger(message="DEBUG: Entering clear_debug_directory.", **_get_log_args())
    # Clear debug directory
    debug_dir = os.path.join(data_dir, 'debug')
    if os.path.exists(debug_dir):
        debug_logger(message=f"DEBUG: Debug directory found: {debug_dir}. Proceeding to clear contents.", **_get_log_args())
        try:
            filenames = os.listdir(debug_dir) # Get list of files before deletion
            debug_logger(message=f"DEBUG: Found {len(filenames)} items in debug directory.", **_get_log_args())
            for filename in filenames:
                file_path = os.path.join(debug_dir, filename)
                try:
                    debug_logger(message=f"DEBUG: Attempting to delete: {file_path}", **_get_log_args())
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        debug_logger(message=f"DEBUG: Successfully deleted: {file_path}", **_get_log_args())
                except Exception as e:
                    debug_logger(message=f"Failed to delete {file_path}. Reason: {e}", **_get_log_args())
            debug_logger(message="DEBUG: Finished attempting to clear debug directory.", **_get_log_args())
        except Exception as e:
            debug_logger(message=f"🔴 ERROR listing or deleting files in {debug_dir}. Reason: {e}", **_get_log_args())

            
    else:
        debug_logger(message=f"DEBUG: Debug directory not found: {debug_dir}. Skipping clear.", **_get_log_args())
