# Orchestrator/orchestrator_logic.py
#
# This file contains the core signaling logic for controlling a running process,
# including pausing and stopping. It manipulates threading events passed to it from the GUI.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250813.165000.1

import threading
import os
import inspect

from display.debug_logic import debug_log
from display.console_logic import console_log

# --- Version Information ---
current_version = "20250813.165000.1"
current_version_hash = (20250813 * 165000 * 1)


def toggle_pause_resume(app_instance, console_print_func, pause_event):
    """Toggles the pause/resume state of the running process by manipulating the pause_event."""
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Toggling pause state.",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)
              
    if pause_event.is_set():
        pause_event.clear()
        app_instance.is_paused_by_user = False
        console_print_func("▶️ Process resumed. ✅")
        debug_log(f"Process resumed successfully. 👍",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
    else:
        pause_event.set()
        app_instance.is_paused_by_user = True
        console_print_func("⏸️ Process paused.")
        debug_log(f"Process paused successfully. 👍",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)

def stop_logic(app_instance, console_print_func, stop_event, pause_event):
    """Stops the currently running process by setting the stop_event."""
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Stop signal requested.",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)
    
    # The main application thread is stored in 'scan_thread' on the app_instance
    # FIXED: Changed app_instance.run_thread to app_instance.scan_thread to match the actual attribute.
    if app_instance.scan_thread and app_instance.scan_thread.is_alive():
        stop_event.set()
        pause_event.clear() # Ensure it's not paused if we are stopping
        app_instance.is_paused_by_user = False
        console_print_func("⏹️ Signaling process to stop...")
        debug_log(f"Stop signal sent to the scan thread. ✅",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
    else:
        # This case handles if the stop button is somehow enabled when no thread is running.
        debug_log(f"Stop logic called, but no active thread found to stop. Fucking useless!",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)