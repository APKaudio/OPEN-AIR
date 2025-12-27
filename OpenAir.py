import sys
import os
import pathlib

# Get the directory of the current script (OpenAir.py)
current_script_dir = pathlib.Path(__file__).resolve().parent

# Add the project root (which is current_script_dir in this case) to sys.path
if str(current_script_dir) not in sys.path:
    sys.path.insert(0, str(current_script_dir))

import inspect
import tkinter as tk
import importlib   

# --- Custom Module Imports (Config MUST be read first) ---
from workers.setup.config_reader import Config # Import the Config class
app_constants = Config.get_instance() # Get the singleton instance and ensure config is read

# --- Core Application Imports ---
import before_main # Moved to top - app_constants is already global
before_main.initialize_flags() # Call early to set flags

# Other essential modules
from workers.splash.splash_screen import SplashScreen
from workers.Worker_Launcher import WorkerLauncher
import display.gui_display
from workers.logger.logger import  debug_logger

import workers.setup.path_initializer as path_initializer
import workers.logger.logger_config as logger_config
import workers.setup.console_encoder as console_encoder
import workers.setup.debug_cleaner as debug_cleaner
from workers.setup.application_initializer import initialize_app
from workers.utils.log_utils import _get_log_args
from managers.manager_launcher import launch_managers

current_version = "20251226.000000.1"

def _reveal_main_window(root, splash):
    if app_constants.ENABLE_DEBUG_SCREEN:
        print("DEBUG: Revealing main window...")
    root.deiconify() # Ensure main window is visible
    splash.hide()    # Dismiss the splash screen

def action_open_display(root, splash, mqtt_connection_manager, subscriber_router, state_mirror_engine):
    """
    Builds and displays the main application window, ensuring the splash
    screen remains responsive by updating the event loop between heavy steps.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    debug_logger(message=f"▶️ Entering {current_function_name}", **_get_log_args())

    try:
        # Each step is followed by root.update() to process events and keep the splash screen alive.
        splash.set_status("Building main window...")
        root.update()

        ApplicationModule = importlib.import_module("display.gui_display")
        Application = getattr(ApplicationModule, "Application")
        
        debug_logger(message=f"⚙️ Preparing to instantiate Application with: mqtt_connection_manager={mqtt_connection_manager}, subscriber_router={subscriber_router}, state_mirror_engine={state_mirror_engine}", **_get_log_args())
        # This is the primary long-running GUI task.
        # We pass the root window to the Application so it can call update() internally.
        app = Application(parent=root, root=root,
                          mqtt_connection_manager=mqtt_connection_manager,
                          subscriber_router=subscriber_router,
                          state_mirror_engine=state_mirror_engine)
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

        debug_logger(message=f"❌ CRITICAL ERROR in {current_function_name}: {e}", **_get_log_args())

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
        if app_constants.global_settings["debug_enabled"]:
            print(message)
    before_main.run_interactive_pre_check(conditional_console_print, debug_logger)

    # --- GUI setup starts here, after core initialization is complete ---
    root = tk.Tk()
    root.title("OPEN-AIR 2")
    root.geometry("1600x1200")
    # root.withdraw() # Removed for diagnostic
    
   
    splash = SplashScreen(root, app_constants.CURRENT_VERSION, app_constants.global_settings['debug_enabled'], temp_print, debug_logger)
    root.splash_window = splash.splash_window # Strong reference
    splash.set_status("Initialization complete. Loading UI...")
    root.update() 
    
    # Launch managers
    managers = launch_managers(app=None, splash=splash) # Pass app=None for now, will be updated.
    
    if managers is None:
        debug_logger(message="❌ Manager launch failed. Exiting application.", **_get_log_args())
        sys.exit(1)

    # Debug: Inspect managers dictionary
    debug_logger(message=f"✅ Managers launched: {managers}", **_get_log_args())

    # Now that the splash screen is visible, proceed with building the main display.
    app = action_open_display(root, splash,
                              mqtt_connection_manager=managers["mqtt_connection_manager"],
                              subscriber_router=managers["subscriber_router"],
                              state_mirror_engine=managers["state_mirror_engine"])
    
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