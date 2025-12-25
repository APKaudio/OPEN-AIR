import before_main # Moved to top
before_main.initialize_flags() # Call early to set flags

import inspect
import importlib
import tkinter as tk
import os
import sys

# --- Module Imports ---
from workers.splash.splash_screen import SplashScreen
from workers.Worker_Launcher import WorkerLauncher
import display.gui_display
from workers.logger.logger import debug_log
from workers.mqtt.setup.config_reader import app_constants
import workers.setup.path_initializer as path_initializer
import workers.logger.logger_config as logger_config
import workers.setup.console_encoder as console_encoder
import workers.setup.debug_cleaner as debug_cleaner
from workers.setup.application_initializer import initialize_app
from workers.utils.log_utils import _get_log_args

# Imports moved from inside main()'s try block
from workers.setup.path_initializer import initialize_paths
from workers.logger.logger import set_log_directory
from workers.setup.debug_cleaner import clear_debug_directory
from workers.setup.console_encoder import configure_console_encoding
import pathlib

def _reveal_main_window(root, splash):
    if app_constants.ENABLE_DEBUG_SCREEN:
        print("DEBUG: Revealing main window...")
    root.deiconify() # Ensure main window is visible
    splash.hide()    # Dismiss the splash screen

def action_open_display(root, splash):
    """
    Builds and displays the main application window, ensuring the splash
    screen remains responsive by updating the event loop between heavy steps.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(message=f"DEBUG: entering {current_function_name}", **_get_log_args())

    try:
        # Each step is followed by root.update() to process events and keep the splash screen alive.
        splash.set_status("Building main window...")
        root.update()

        ApplicationModule = importlib.import_module("display.gui_display")
        Application = getattr(ApplicationModule, "Application")
        
        # This is the primary long-running GUI task.
        # We pass the root window to the Application so it can call update() internally.
        app = Application(parent=root, root=root)
        app.pack(fill=tk.BOTH, expand=True)
        splash.set_status("Main window constructed.")
        root.update()

        splash.set_status("Launching background workers...")
        root.update()
        
        worker_launcher = WorkerLauncher(
            splash_screen=splash,
            console_print_func=app.print_to_console,
        )
        worker_launcher.launch_all_workers()
        splash.set_status("Workers launched.")
        root.update()

        

        # Schedule the final reveal to happen after the event loop has had a chance to start properly.

        root.after(2000, lambda: (

            (print("DEBUG: _reveal_main_window SCHEDULED AND EXECUTING") if app_constants.ENABLE_DEBUG_SCREEN else None), 

            _reveal_main_window(root, splash)

        ))

        

        return app



    except Exception as e:

        debug_log(message=f"❌ CRITICAL ERROR in {current_function_name}: {e}", **_get_log_args())

        import traceback

        traceback.print_exc()

        return None

def main():
    """The main execution function for the application."""
    temp_print = print # Keep temp_print for critical bootstrap failures that happen before debug_log is fully functional
    GLOBAL_PROJECT_ROOT = None
    data_dir = None

    import sys # Moved import sys here

    # --- Fix 2: Re-sequencing the Timeline ---
    # Phase 1 & 2: Define paths and engage logger IMMEDIATELY.
    from workers.setup.path_initializer import initialize_paths
    from workers.logger.logger import set_log_directory
    from workers.setup.debug_cleaner import clear_debug_directory
    from workers.setup.console_encoder import configure_console_encoding
    import pathlib

    GLOBAL_PROJECT_ROOT, data_dir = initialize_paths()
    log_dir = pathlib.Path(data_dir) / "debug"
    set_log_directory(log_dir)
    clear_debug_directory(data_dir)
    configure_console_encoding()

    # Now that the logger is safe, we can proceed with the rest of the setup.
    if not initialize_app():
        temp_print("❌ Critical initialization failed. Application will now exit.")
        sys.exit(1)

    # Perform dependency check after initial setup
    def conditional_console_print(message):
        if app_constants.global_settings["debug_to_terminal"]:
            print(message)
    before_main.run_interactive_pre_check(conditional_console_print, debug_log)

    # --- GUI setup starts here, after core initialization is complete ---
    root = tk.Tk()
    root.title("OPEN-AIR 2")
    root.geometry("1600x1200")
    # root.withdraw() # Removed for diagnostic
    
    print(f"DEBUG: app_constants.LOCAL_DEBUG_ENABLE before SplashScreen: {app_constants.LOCAL_DEBUG_ENABLE}")
    splash = SplashScreen(root, app_constants.CURRENT_VERSION, app_constants.LOCAL_DEBUG_ENABLE, temp_print, debug_log)
    root.splash_window = splash.splash_window # Strong reference
    splash.set_status("Initialization complete. Loading UI...")
    root.update() 
    
    # Now that the splash screen is visible, proceed with building the main display.
    app = action_open_display(root, splash)
    
    def on_closing():
        """Gracefully shuts down the application."""
        if app:
            app.shutdown()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Finally, enter the main event loop.
    root.mainloop()


if __name__ == "__main__":
    main()