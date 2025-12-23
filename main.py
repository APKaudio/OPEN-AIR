print("main.py started!")

# main.py
#
# This file (main.py) serves as the main entry point for the application, orchestrating startup checks and GUI launch.
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

import inspect
import importlib
import tkinter as tk
import os
import sys

# --- Module Imports ---
# Core utilities and components

from workers.splash.splash_screen import SplashScreen
#from managers.HOLD_connection.manager_visa_dispatch_scpi import ScpiDispatcher
from workers.Worker_Launcher import WorkerLauncher


# Application display module
import display.gui_display # Import the module, not just the class
from workers.logger.logger import debug_log

# Setup modules (ensure they are imported correctly)
import workers.setup.app_constants as app_constants

import workers.setup.path_initializer as path_initializer 
import workers.logger.logger_config as logger_config
import workers.setup.console_encoder as console_encoder
import workers.setup.debug_cleaner as debug_cleaner
# Assume before_main is also a module that needs to be imported
import before_main

# Import initialize_app directly
from workers.setup.application_initializer import initialize_app 

from workers.utils.log_utils import _get_log_args

current_file = f"{os.path.basename(__file__)}"

def action_open_display(root, splash): 
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(
        message="DEBUG: entering action_open_display",
        **_get_log_args()
        
    )
    # Initializes and opens the main graphical user interface and then publishes the dataset.
    debug_log(
        message=f"DEBUG: Entering action_open_display...",
        **_get_log_args()
        
    )
    
    if app_constants.LOCAL_DEBUG_ENABLE: 
        debug_log(
            message=f"🖥️🟢 The final step! Activating the main display in '{current_function_name}'!",
            **_get_log_args()
            
        )

    try:
        debug_log(message="--> [1/10] Setting splash status: Building GUI...", **_get_log_args() )
        splash.set_status("Building GUI...")

        debug_log(message="--> [2/10] Importing Application module...", **_get_log_args() )
        ApplicationModule = importlib.import_module("display.gui_display")
        Application = getattr(ApplicationModule, "Application")
        debug_log(message="<-- [2/10] Application module imported.", **_get_log_args() )

        debug_log(message="--> [3/10] Instantiating Application...", **_get_log_args() )
        app = Application(parent=root)
        app.pack(fill=tk.BOTH, expand=True)
        root.update_idletasks()
        splash.set_status("GUI constructed.")
        debug_log(message="<-- [3/10] Application instantiated.", **_get_log_args() )

        debug_log(message="--> [4/10] Instantiating ScpiDispatcher...", **_get_log_args() )
      # scpi_dispatcher = ScpiDispatcher(
      #     app_instance=app,
            
       #)
        splash.set_status("SCPI Dispatcher initialized.")
        debug_log(message="<-- [4/10] ScpiDispatcher instantiated.", **_get_log_args() )

        debug_log(message="--> [5/10] Launching managers...", **_get_log_args() )
      #  launch_managers(scpi_dispatcher, app, splash)
        debug_log(message="<-- [5/10] Managers launched.", **_get_log_args() )
        
        debug_log(message="--> [6/10] Launching workers...", **_get_log_args() )
        worker_launcher = WorkerLauncher(
            splash_screen=splash,
            console_print_func=app.print_to_console,
        )
        worker_launcher.launch_all_workers()
        debug_log(message="<-- [6/10] Workers launched.", **_get_log_args() )

        debug_log(message="--> [7/10] Publishing initial dataset...", **_get_log_args() )
        splash.set_status("Dataset published.")
        debug_log(message="<-- [7/10] Initial dataset published.", **_get_log_args() )

        debug_log(message="--> [9/10] Hiding splash screen...", **_get_log_args() )
        splash.hide() # Hide splash screen
        debug_log(message="<-- [9/10] Splash screen hidden.", **_get_log_args() )
        
        debug_log(message="--> [10/10] Deiconifying root window...", **_get_log_args() )
        root.deiconify()
        root.update_idletasks()
        debug_log(message="<-- [10/10] Root window deiconified.", **_get_log_args() )

        debug_log(message="✅ The grand spectacle begins! GUI is now open.", **_get_log_args() )
        debug_log(message="DEBUG: leaving action_open_display", **_get_log_args() )
        return True

    except Exception as e:
                debug_log(
                    message=f"❌ Error in {current_function_name}: {e}",
                    **_get_log_args()
                    
                )
    splash.hide() # Hide splash on error
    return False

def main():
    """The main execution function for the application."""
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(message="DEBUG: Entering main function.", **_get_log_args() )

    # Call path_initializer early to set up DATA_DIR needed for logger
    debug_log(message="DEBUG: Calling path_initializer.initialize_paths...", **_get_log_args() )
    global_project_root, data_dir = path_initializer.initialize_paths(print)
    debug_log(message=f"DEBUG: path_initializer.initialize_paths completed. data_dir is: {data_dir}", **_get_log_args() )

    # Configure logger
    debug_log(message="DEBUG: Calling logger_config.configure_logger...", **_get_log_args() )
    logger_config.configure_logger(data_dir, print)
    debug_log(message="DEBUG: logger_config.configure_logger completed.", **_get_log_args() )
    
    debug_log(message="DEBUG: Calling debug_cleaner.clear_debug_directory...", **_get_log_args() )
    debug_cleaner.clear_debug_directory(data_dir, print)
    debug_log(message="DEBUG: debug_cleaner.clear_debug_directory completed.", **_get_log_args() )

    debug_log(message="DEBUG: Calling console_encoder.configure_console_encoding...", **_get_log_args() )
    # Corrected call: Pass print and debug_log to configure_console_encoding
    console_encoder.configure_console_encoding(print, debug_log)
    debug_log(message="DEBUG: console_encoder.configure_console_encoding completed.", **_get_log_args() )

    debug_log(message="🚀 Running pre-flight dependency checks...", **_get_log_args() )
    if not before_main.action_check_dependancies(print, debug_log):
        debug_log(message="❌ Critical dependencies missing. Application will halt.", **_get_log_args() )
        sys.exit(1)
    debug_log(message="✅ Pre-flight dependency checks passed.", **_get_log_args() )

    # Initialize and start splash screen early
    debug_log(message="DEBUG: Initializing Tk root window...", **_get_log_args() )
    root = tk.Tk()
    root.title("OPEN-AIR 2")
    root.geometry("1600x1200")
    root.withdraw()
    debug_log(message="DEBUG: Tk root window initialized.", **_get_log_args() )
    

    debug_log(message="DEBUG: Initializing SplashScreen...", **_get_log_args() )
    splash = SplashScreen(root, app_constants.current_version, app_constants.LOCAL_DEBUG_ENABLE, print, debug_log)
    splash.set_status("Initializing application...") # Initial status update
    debug_log(message="DEBUG: SplashScreen initialized.", **_get_log_args() )
    

    debug_log(message="DEBUG: Calling initialize_app...", **_get_log_args() )
    # Corrected call: Use imported function directly
    if initialize_app(print, debug_log): # <-- initialize_app is called here directly
        debug_log(message="DEBUG: initialize_app returned True. Calling action_open_display...", **_get_log_args() )
       
        action_open_display(root, splash)
       
    else:
        splash.set_status("Halting startup due to initialization errors.")
        splash.hide() # Hide splash on error
        debug_log(message="❌ Halting startup due to initialization errors.", **_get_log_args() )

    debug_log(message="DEBUG: About to enter root.mainloop()...", **_get_log_args() )
    
    root.mainloop()
    
    debug_log(message="DEBUG: root.mainloop() has exited.", **_get_log_args() )  

if __name__ == "__main__":
    print("DEBUG: Calling main()...")
    main()