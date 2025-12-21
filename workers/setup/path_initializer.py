# workers/setup/path_initializer.py

import os
import sys
import pathlib

GLOBAL_PROJECT_ROOT = None
DATA_DIR = None

def initialize_paths(console_log_func, watchdog_instance):
    global GLOBAL_PROJECT_ROOT, DATA_DIR

    # --- GLOBAL PATH ANCHOR (CRITICAL FIX: Ensure this runs first!) ---
    # This defines the absolute, true root path of the project, irrespective of the CWD.
    GLOBAL_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent # Adjust path for setup directory
    console_log_func(f"DEBUG: GLOBAL_PROJECT_ROOT set to {GLOBAL_PROJECT_ROOT}")
    # Add the project's root directory to the system path to allow for imports from
    # all sub-folders (e.g., 'configuration' and 'display'). This is a robust way to handle imports.
    if str(GLOBAL_PROJECT_ROOT) not in sys.path:
        sys.path.append(str(GLOBAL_PROJECT_ROOT))
    console_log_func(f"DEBUG: sys.path updated. Current sys.path: {sys.path}")

    watchdog_instance.pet("initialize_app: global path set")

    # --- Set DATA_DIR ---
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as a bundled executable
        DATA_DIR = os.path.join(os.path.dirname(sys.executable), 'DATA')
    else:
        DATA_DIR = os.path.join(GLOBAL_PROJECT_ROOT, 'DATA')
    
    return GLOBAL_PROJECT_ROOT, DATA_DIR
