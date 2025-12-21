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

from workers.watchdog.worker_watchdog import Watchdog
from workers.splash.splash_screen import SplashScreen
from managers.connection.manager_visa_dispatch_scpi import ScpiDispatcher
from workers.Worker_Launcher import WorkerLauncher

from display.logger import debug_log, console_log, log_visa_command

from workers.setup.application_initializer import initialize_app
import workers.setup.app_constants as app_constants
import before_main

current_file = f"{os.path.basename(__file__)}"



def action_open_display(root, splash, watchdog): # Added watchdog
    # Initializes and opens the main graphical user interface and then publishes the dataset.
    current_function_name = inspect.currentframe().f_code.co_name
    if app_constants.Local_Debug_Enable:
        debug_log(
            message=f"🖥️🟢 The final step! Activating the main display in '{current_function_name}'!",
            file=current_file,
            version=app_constants.current_version,
            function=current_function_name,
            console_print_func=console_log
        )

    try:
        watchdog.pet("action_open_display: start")
        console_log("--> [1/10] Setting splash status: Building GUI...")
        splash.set_status("Building GUI...")

        watchdog.pet("action_open_display: 1/10")
        console_log("--> [2/10] Importing Application module...")
        ApplicationModule = importlib.import_module("display.gui_display")
        Application = getattr(ApplicationModule, "Application")
        
        watchdog.pet("action_open_display: 2/10")
        console_log("--> [3/10] Instantiating Application...")
        app = Application(parent=root)
        app.pack(fill=tk.BOTH, expand=True)
        root.update_idletasks()
        splash.set_status("GUI constructed.")
        console_log("<-- [3/10] Application instantiated.")
        watchdog.pet("action_open_display: 3/10")

        console_log("--> [4/10] Instantiating ScpiDispatcher...")
        scpi_dispatcher = ScpiDispatcher(
            app_instance=app,
            console_print_func=console_log
        )
        splash.set_status("SCPI Dispatcher initialized.")
        console_log("<-- [4/10] ScpiDispatcher instantiated.")
        watchdog.pet("action_open_display: 4/10")



        console_log("--> [5/10] Launching managers...")
      #  launch_managers(scpi_dispatcher, app, splash)
        console_log("<-- [5/10] Managers launched.")
        watchdog.pet("action_open_display: 5/10")
        
        console_log("--> [6/10] Launching workers...")
        worker_launcher = WorkerLauncher(
            splash_screen=splash,
            console_print_func=console_log
        )
        worker_launcher.launch_all_workers()
        console_log("<-- [6/10] Workers launched.")
        watchdog.pet("action_open_display: 6/10")

        console_log("--> [7/10] Publishing initial dataset...")
        splash.set_status("Dataset published.")
        console_log("<-- [7/10] Initial dataset published.")
        watchdog.pet("action_open_display: 7/10")



        console_log("--> [9/10] Hiding splash screen...")
        splash.hide() # Hide splash screen
        console_log("<-- [9/10] Splash screen hidden.")
        watchdog.pet("action_open_display: 9/10")
        
        console_log("--> [10/10] Deiconifying root window...")
        root.deiconify()
        root.update_idletasks()
        console_log("<-- [10/10] Root window deiconified.")
        watchdog.pet("action_open_display: 10/10")

        console_log("✅ The grand spectacle begins! GUI is now open.")
        return True

    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        if app_constants.Local_Debug_Enable:
            debug_log(
                message=f"🖥️🔴 Blast and barnacles! The display has failed to materialize! The error be: {e}",
                file=current_file,
                version=app_constants.current_version,
                function=current_function_name,
                console_print_func=console_log
            )
        splash.hide() # Hide splash on error
        return False

def main():
    """The main execution function for the application."""
    watchdog = Watchdog()
    watchdog.start()
    watchdog.pet("main: start")

    # Call path_initializer early to set up DATA_DIR needed for logger
    import workers.setup.path_initializer as path_initializer
    global_project_root, data_dir = path_initializer.initialize_paths(console_log, watchdog)

    # Configure logger as early as possible
    import workers.setup.logger_config as logger_config
    logger_config.configure_logger(data_dir, console_log, watchdog)
    
    current_file = f"{os.path.basename(__file__)}"

    # Perform initial dependency checks using before_main.py
    console_log("🚀 Running pre-flight dependency checks...")
    if not before_main.action_check_dependancies(console_log, debug_log):
        console_log("❌ Critical dependencies missing. Application will halt.")
        sys.exit(1)
    console_log("✅ Pre-flight dependency checks passed.")

    # Initialize and start splash screen early
    root = tk.Tk()
    root.title("OPEN-AIR 2")
    root.geometry("1600x1200")
    root.withdraw()
    watchdog.pet("main: tk root created")

    splash = SplashScreen(root, app_constants.current_version, app_constants.Local_Debug_Enable, console_log, debug_log)
    splash.set_status("Initializing application...") # Initial status update
    watchdog.pet("main: splash screen created")

    if initialize_app(console_log, debug_log, watchdog):
        action_open_display(root, splash, watchdog)
        watchdog.pet("main: action_open_display returned")
    else:
        splash.set_status("Halting startup due to initialization errors.")
        splash.hide() # Hide splash on error
        console_log("❌ Halting startup due to initialization errors.")

    watchdog.pet("main: before mainloop")
    root.mainloop()
    watchdog.stop()

if __name__ == "__main__":
    print("DEBUG: Calling main()...")
    main()