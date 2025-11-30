# OPEN-AIR/main.py
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251129  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 1 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


# This file serves as the main entry point for the application, orchestrating startup checks and GUI launch.
#
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
#
# Version 20251006.220900.1

import os
import inspect
import datetime
import sys
import pathlib
import importlib
import time


# --- TEMPORARY IMPORTS (Only standard library imports are safe here) ---
# Project-specific imports are commented out or moved to avoid crashing before sys.path is set.
# from workers.worker_mqtt_controller_util import MqttControllerUtility 
# from workers.worker_active_logging import debug_log, console_log
# ... (rest of initial imports) ...


# --- GLOBAL PATH ANCHOR (CRITICAL FIX: Ensure this runs first!) ---
# This defines the absolute, true root path of the project, irrespective of the CWD.
try:
    GLOBAL_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
    # Add the project's root directory to the system path to allow for imports from
    # all sub-folders (e.g., 'configuration' and 'display'). This is a robust way to handle imports.
    if str(GLOBAL_PROJECT_ROOT) not in sys.path:
        sys.path.append(str(GLOBAL_PROJECT_ROOT))
    
    # --- Project-specific Imports (SAFE TO RUN NOW) ---
    # Import core application modules
    from workers.worker_active_logging import debug_log, console_log
    from workers.worker_mqtt_controller_util import MqttControllerUtility
    from display.styling.style import THEMES, DEFAULT_THEME
    
    # workers
    from workers.worker_active_marker_tune_and_collect import MarkerGoGetterWorker
    from workers.worker_active_peak_publisher import ActivePeakPublisher  
    from datasets.worker_dataset_publisher import main as dataset_publisher_main
    from datasets.worker_repository_publisher import main as repository_publisher_main
    
    # managers
    from managers.manager_instrument_settings_frequency import FrequencySettingsManager
    from managers.manager_instrument_settings_bandwidth import BandwidthSettingsManager
    from managers.manager_presets_span import SpanSettingsManager
    from managers.manager_visa_device_search import VisaDeviceManager
    from managers.manager_visa_dispatch_scpi import ScpiDispatcher
    from managers.manager_yakety_yak import YaketyYakManager
    from managers.manager_visa_reset import VisaResetManager
    from managers.manager_instrument_settings_markers import MarkersSettingsManager

    # --- Set DATA_DIR ---
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as a bundled executable
        DATA_DIR = os.path.join(os.path.dirname(sys.executable), 'DATA')
    else:
        # Running from source
        DATA_DIR = os.path.join(GLOBAL_PROJECT_ROOT, 'DATA')

except Exception as e:
    # Fallback logging if the path and initial imports fail
    print(f"❌ CRITICAL INITIALIZATION ERROR: {e}", file=sys.stderr)
    print("Application halted at startup due to module import failure.")
    sys.exit(1)


# This block ensures the console can handle UTF-8 characters, preventing encoding errors.
if os.name == 'nt':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for older Python versions that don't have reconfigure
        pass


# --- Global Scope Variables ---
current_version = "20251124.140000.3"
# Note: For hashing, any leading zero in the hour is dropped (e.g., 083015 becomes 83015).
current_version_hash = (20251124 * 140000 * 3)
current_file = f"{os.path.basename(__file__)}"


def action_check_dependancies():
    # Checks for required system and library dependencies.
    current_function_name = inspect.currentframe().f_code.co_name
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
        debug_log(
            message=f"🖥️🔴 By Jove! The configuration is in shambles! The error be: {e}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )
        return False

def action_open_display(mqtt_util_instance):
    # Initializes and opens the main graphical user interface and then publishes the dataset.
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(
        message=f"🖥️🟢 The final step! Activating the main display in '{current_function_name}'!",
        file=current_file,
        version=current_version,
        function=current_function_name,
        console_print_func=console_log
    )

    try:
        # --- Function logic goes here ---
        # CRITICAL FIX: Import the Application class *here* using importlib
        ApplicationModule = importlib.import_module("display.gui_display")
        Application = getattr(ApplicationModule, "Application")
        
        app = Application()


################ INITIALIZE MANAGERS ################

        ################ INITIALIZE MANAGERS ################
        # Instantiate the low-level SCPI dispatcher first, as other managers depend on it.
        scpi_dispatcher = ScpiDispatcher(
            app_instance=app,
            console_print_func=console_log
        )


        frequency_manager = FrequencySettingsManager(mqtt_controller=mqtt_util_instance)
        bandwidth_manager = BandwidthSettingsManager(mqtt_controller=mqtt_util_instance)

        span_manager = SpanSettingsManager(mqtt_controller=mqtt_util_instance)


        # PASS THE SCPI DISPATCHER TO THE DEVICE MANAGER FOR SYNCHRONIZATION
        manager_visa_connection = VisaDeviceManager(
            mqtt_controller=mqtt_util_instance,
            scpi_dispatcher=scpi_dispatcher
        )

        # ADDED: Instantiate the new VisaResetManager
        manager_visa_reset = VisaResetManager(
            mqtt_controller=mqtt_util_instance,
            scpi_dispatcher=scpi_dispatcher
        )

        # Correctly instantiate the YaketyYakManager with all required arguments.
        manager_yakety_yak = YaketyYakManager(
            mqtt_controller=mqtt_util_instance,
            dispatcher_instance=scpi_dispatcher,
            app_instance=app
        )

        # ADDED: Instantiate the MarkerSettingsManager
        marker_settings_manager = MarkersSettingsManager(mqtt_controller=mqtt_util_instance)
        
        # ADDED: Instantiate the worker responsible for sweeping and collecting marker data
        marker_go_getter = MarkerGoGetterWorker(mqtt_util=mqtt_util_instance)
        
        # ADDED: Instantiate the worker responsible for pivoting marker output to hierarchical topics
        active_peak_publisher = ActivePeakPublisher(mqtt_util=mqtt_util_instance)


        # Publish the dataset after the GUI is created but before mainloop() starts
        dataset_publisher_main(mqtt_util_instance)
        repository_publisher_main(mqtt_util_instance)


        app.mainloop()
        console_log("✅ The grand spectacle begins! GUI is now open.")
        return True

    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        debug_log(
            message=f"🖥️🔴 Blast and barnacles! The display has failed to materialize! The error be: {e}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )
        return False

def main():
    """The main execution function for the application."""
    console_log(f"🚀 Launch sequence initiated for version {current_version}.")

    if action_check_dependancies():

        if action_check_configuration():
            mqtt_util_instance = MqttControllerUtility(console_log, console_log)
            # FIX: Start the broker before attempting to connect.
            if hasattr(mqtt_util_instance, 'start_mosquitto'):
                mqtt_util_instance.start_mosquitto()
                time.sleep(1) # Give the broker a second to start
            
            mqtt_util_instance.connect_mqtt()
            action_open_display(mqtt_util_instance)
        else:
        
            console_log("❌ Halting startup due to configuration errors.")
    else:
        console_log("❌ Halting startup due to missing dependencies.")


if __name__ == "__main__":
    main()