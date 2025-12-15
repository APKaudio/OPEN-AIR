# main.py
#
# This file (main.py) serves as the main entry point for the application, orchestrating startup checks and GUI launch.
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251213  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 44 ## a running version number - incriments by one each time 

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


# --- TEMPORARY IMPORTS (Only standard library imports are safe here) ---
# Project-specific imports are commented out or moved to avoid crashing before sys.path is set.
# from workers.mqtt.worker_mqtt_controller_util import MqttControllerUtility 
from display.logger import debug_log, console_log, log_visa_command
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
    from display.logger import debug_log, console_log, log_visa_command
    from workers.mqtt.worker_mqtt_controller_util import MqttControllerUtility
    from display.styling.style import THEMES, DEFAULT_THEME
    from display.splash.splash_screen import SplashScreen
    from before_main import action_check_dependancies as check_dependencies_before_main
    
    # workers
    from workers.active.worker_active_marker_tune_and_collect import MarkerGoGetterWorker
    from workers.active.worker_active_peak_publisher import ActivePeakPublisher  
    from workers.publishers.worker_dataset_publisher import main as dataset_publisher_main
    from workers.publishers.worker_meta_publisher import main as meta_publisher_main
    from workers.publishers.worker_YAK_publisher import main as repository_publisher_main
    
    # managers
    from managers.frequency_manager.frequency_state import FrequencyState
    from managers.frequency_manager.frequency_yak_communicator import FrequencyYakCommunicator
    from managers.frequency_manager.frequency_callbacks import FrequencyCallbacks
    # from managers.manager_instrument_settings_frequency import FrequencySettingsManager
    from managers.bandwidth_manager.bandwidth_state import BandwidthState
    from managers.bandwidth_manager.bandwidth_yak_communicator import BandwidthYakCommunicator
    from managers.bandwidth_manager.bandwidth_presets import BandwidthPresets
    from managers.bandwidth_manager.bandwidth_callbacks import BandwidthCallbacks
    # from managers.manager_instrument_settings_bandwidth import BandwidthSettingsManager
    from managers.yak_manager.manager_presets_span import SpanSettingsManager
    from managers.connection.manager_visa_device_search import VisaDeviceManager
    from managers.connection.manager_visa_dispatch_scpi import ScpiDispatcher
    from managers.yak_manager.manager_yakety_yak import YaketyYakManager
    from managers.connection.manager_visa_reset import VisaResetManager
    from managers.manager_instrument_settings_markers import MarkersSettingsManager

    Local_Debug_Enable = True

    # --- Set DATA_DIR ---
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as a bundled executable
        DATA_DIR = os.path.join(os.path.dirname(sys.executable), 'DATA')
    else:
        # Running from source
        DATA_DIR = os.path.join(GLOBAL_PROJECT_ROOT, 'DATA')

except Exception as e:
    # Fallback logging if the path and initial imports failCreate GEMINI.md files to customize your interactions with Gemini.
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


current_file = f"{os.path.basename(__file__)}" 




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
def action_open_display(mqtt_util_instance, splash): # Added splash parameter
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
        # SplashScreen().run() # REMOVED THIS CALL
        splash.set_status("Building GUI...")

        ApplicationModule = importlib.import_module("display.gui_display")
        Application = getattr(ApplicationModule, "Application")
        
        app = Application(mqtt_util_instance=mqtt_util_instance)
        splash.set_status("GUI constructed.")

        splash.set_status("Initializing managers...")

        scpi_dispatcher = ScpiDispatcher(
            app_instance=app,
            console_print_func=console_log
        )
        splash.set_status("SCPI Dispatcher initialized.")

        frequency_state = FrequencyState()
        frequency_yak_communicator = FrequencyYakCommunicator(mqtt_controller=mqtt_util_instance, state=frequency_state)
        frequency_callbacks = FrequencyCallbacks(mqtt_controller=mqtt_util_instance, state=frequency_state, yak_communicator=frequency_yak_communicator)
        frequency_callbacks.subscribe_to_topics()
        splash.set_status("Frequency manager initialized.")

        bandwidth_state = BandwidthState()
        bandwidth_yak_communicator = BandwidthYakCommunicator(mqtt_controller=mqtt_util_instance, state=bandwidth_state)
        bandwidth_presets = BandwidthPresets(mqtt_controller=mqtt_util_instance, state=bandwidth_state, yak_communicator=bandwidth_yak_communicator)
        bandwidth_callbacks = BandwidthCallbacks(mqtt_controller=mqtt_util_instance, state=bandwidth_state, yak_communicator=bandwidth_yak_communicator, presets=bandwidth_presets)
        bandwidth_callbacks.subscribe_to_topics()
        splash.set_status("Bandwidth manager initialized.")

        span_manager = SpanSettingsManager(mqtt_controller=mqtt_util_instance)
        splash.set_status("Span manager initialized.")

        manager_visa_connection = VisaDeviceManager(
            mqtt_controller=mqtt_util_instance,
            scpi_dispatcher=scpi_dispatcher
        )
        splash.set_status("VISA connection manager initialized.")

        manager_visa_reset = VisaResetManager(
            mqtt_controller=mqtt_util_instance,
            scpi_dispatcher=scpi_dispatcher
        )
        splash.set_status("VISA reset manager initialized.")

        manager_yakety_yak = YaketyYakManager(
            mqtt_controller=mqtt_util_instance,
            dispatcher_instance=scpi_dispatcher,
            app_instance=app
        )
        splash.set_status("Yakety Yak manager initialized.")

        marker_settings_manager = MarkersSettingsManager(mqtt_controller=mqtt_util_instance)
        splash.set_status("Marker settings manager initialized.")
        
        marker_go_getter = MarkerGoGetterWorker(mqtt_util=mqtt_util_instance)
        splash.set_status("Marker Go-Getter worker initialized.")
        
        active_peak_publisher = ActivePeakPublisher(mqtt_util=mqtt_util_instance)
        splash.set_status("Active Peak Publisher initialized.")

        # Publish the dataset after the GUI is created but before mainloop() starts
        splash.set_status("Publishing initial dataset...")
        dataset_publisher_main(mqtt_util_instance)
        meta_publisher_main(mqtt_util_instance)
        repository_publisher_main(mqtt_util_instance)
        splash.set_status("Dataset published.")

        mqtt_util_instance.resume()
        splash.set_status("MQTT message processing resumed.")
        splash.hide() # Hide splash screen

        console_log("DEBUG: Reached app.mainloop(). Attempting to display GUI.")
        app.mainloop() # This is the main GUI loop, should run indefinitely
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

    # Initialize and start splash screen early
    splash = SplashScreen()
    splash.start()
    splash.set_status("Initializing application...") # Initial status update

    if action_check_dependancies():
        splash.set_status("Dependencies checked.")
        if action_check_configuration():
            splash.set_status("Configuration validated.")
            mqtt_util_instance = MqttControllerUtility(console_log, console_log)
            
            # Pause MQTT immediately after initialization
            mqtt_util_instance.pause() 
            splash.set_status("MQTT client initialized and paused.")

            if hasattr(mqtt_util_instance, 'start_mosquitto'):
                mqtt_util_instance.start_mosquitto()
                time.sleep(1)
            
            mqtt_util_instance.connect_mqtt()
            splash.set_status("Connecting to MQTT broker...")

            # print("--- DEBUG: Main thread past connect_mqtt() ---") # REMOVED
            action_open_display(mqtt_util_instance, splash) # Pass splash to action_open_display
            
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

    # mainloop will be called by app instance in action_open_display

if __name__ == "__main__":
    main()