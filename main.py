print("main.py started!")

# main.py
#
# This file (main.py) serves as the main entry point for the application, orchestrating startup checks and GUI launch.
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251215  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 58 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#


import os
import inspect
import datetime
import sys
import pathlib
import importlib
import time
import tkinter as tk
from managers.connection.manager_visa_dispatch_scpi import ScpiDispatcher
from workers.Worker_Launcher import WorkerLauncher
from workers.watchdog.worker_watchdog import Watchdog
from workers.splash.splash_screen import SplashScreen

# from display.splash.splash_screen import SplashScreen # MOVED TO TOP-LEVEL

# --- TEMPORARY IMPORTS (Only standard library imports are safe here) ---

# ... (rest of initial imports) ...


# --- GLOBAL PATH ANCHOR (CRITICAL FIX: Ensure this runs first!) ---
# This defines the absolute, true root path of the project, irrespective of the CWD.
# try:
GLOBAL_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
print(f"DEBUG: GLOBAL_PROJECT_ROOT set to {GLOBAL_PROJECT_ROOT}")
# Add the project's root directory to the system path to allow for imports from
# all sub-folders (e.g., 'configuration' and 'display'). This is a robust way to handle imports.
if str(GLOBAL_PROJECT_ROOT) not in sys.path:
    sys.path.append(str(GLOBAL_PROJECT_ROOT))
print(f"DEBUG: sys.path updated. Current sys.path: {sys.path}")

# --- Project-specific Imports (SAFE TO RUN NOW) ---
# Import core application modules
# from display.logger import debug_log, console_log, log_visa_command # Commented for debugging
# from managers.connection.manager_visa_dispatch_scpi import ScpiDispatcher # Commented for debugging
# from managers.manager_launcher import launch_managers # Commented for debugging
# from workers.Worker_Launcher import WorkerLauncher # Commented for debugging
# from workers.utils.worker_watchdog import Watchdog # Commented for debugging
    
Local_Debug_Enable = True

# --- Set DATA_DIR ---
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running as a bundled executable
    DATA_DIR = os.path.join(os.path.dirname(sys.executable), 'DATA')
else:
    DATA_DIR = os.path.join(GLOBAL_PROJECT_ROOT, 'DATA')

# Configure the logger with the correct DATA_DIR
import display.logger
display.logger.set_log_directory(pathlib.Path(DATA_DIR) / "debug")
print("DEBUG: Logger configured via display.logger.set_log_directory.")

# except Exception as e:
#    # Fallback logging if the path and initial imports failCreate GEMINI.md files to customize your interactions with Gemini.
#    print(f"❌ CRITICAL INITIALIZATION ERROR: {e}", file=sys.stderr)
#    print("Application halted at startup due to module import failure.")
#    sys.exit(1)


# This block ensures the console can handle UTF-8 characters, preventing encoding errors.
if os.name == 'nt':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for older Python versions that don't have reconfigure
        pass


current_file = f"{os.path.basename(__file__)}" 


from display.logger import debug_log, console_log, log_visa_command


def action_check_dependancies():
    # Checks for required system and library dependencies.
    current_function_name = inspect.currentframe().f_code.co_name
    if Local_Debug_Enable:
        debug_log(
            message=f"🖥️🟢 Ah, good, we're entering '{current_function_name}'! Let's examine the raw materials, shall we?",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )

    try:
        # --- Function logic goes here ---
        # Placeholder for dependency checking logic
        console_log("✅ A most glorious success! Dependencies are in order.")
        return True

    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        if Local_Debug_Enable:
            debug_log(
                message=f"🖥️🔴 Heavens to Betsy! We've hit a snag in the dependencies! The error be: {e}",
                file=current_file,
                version=current_version,
                function=current_function_name,
                console_print_func=console_log
            )
        return False
def action_check_configuration():
    # Validates the application's configuration files.
    current_function_name = inspect.currentframe().f_code.co_name


    if Local_Debug_Enable:
        debug_log(
            message=f"🖥️🟢 Ahem, commencing the configuration validation experiment in '{current_function_name}'.",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )

   
    try:

        # Placeholder for configuration validation
        console_log("✅ Excellent! The configuration is quite, quite brilliant.")
        return True

    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        if Local_Debug_Enable:
            debug_log(
                message=f"🖥️🔴 By Jove! The configuration is in shambles! The error be: {e}",
                file=current_file,
                version=current_version,
                function=current_function_name,
                console_print_func=console_log
            )
        return False
def action_open_display(root, splash, watchdog): # Added watchdog
    # Initializes and opens the main graphical user interface and then publishes the dataset.
    current_function_name = inspect.currentframe().f_code.co_name
    if Local_Debug_Enable:
        debug_log(
            message=f"🖥️🟢 The final step! Activating the main display in '{current_function_name}'!",
            file=current_file,
            version=current_version,
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
        if Local_Debug_Enable:
            debug_log(
                message=f"🖥️🔴 Blast and barnacles! The display has failed to materialize! The error be: {e}",
                file=current_file,
                version=current_version,
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
    
    console_log(f"🚀 Launch sequence initiated for version {current_version}.")

    debug_dir = os.path.join(DATA_DIR, 'debug')
    if os.path.exists(debug_dir):
        for filename in os.listdir(debug_dir):
            file_path = os.path.join(debug_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                console_log(f"Failed to delete {file_path}. Reason: {e}")
    
    watchdog.pet("main: cleared debug dir")

    root = tk.Tk()
    root.title("OPEN-AIR 2")
    root.geometry("1600x1200")
    root.withdraw()
    
    watchdog.pet("main: tk root created")

    # Initialize and start splash screen early
    splash = SplashScreen(root)
    splash.set_status("Initializing application...") # Initial status update
    watchdog.pet("main: splash screen created")

    if action_check_dependancies():
        splash.set_status("Dependencies checked.")
        watchdog.pet("main: dependencies checked")
        if action_check_configuration():
            splash.set_status("Configuration validated.")
            watchdog.pet("main: configuration validated")
            


            
            action_open_display(root, splash, watchdog) # Pass watchdog
            watchdog.pet("main: action_open_display returned")
            
            # AFTER GUI is built and data published, resume MQTT and hide splash
            # These actions are now handled within action_open_display()


        else:
            splash.set_status("Halting startup due to configuration errors.")
            splash.hide() # Hide splash on error
            console_log("❌ Halting startup due to configuration errors.")
    else:
        splash.set_status("Halting startup due to missing dependencies.")
        splash.hide() # Hide splash on error
        console_log("❌ Halting startup due to missing dependencies.")

    watchdog.pet("main: before mainloop")
    root.mainloop()
    watchdog.stop()

if __name__ == "__main__":
    print("DEBUG: Calling main()...")
    main()