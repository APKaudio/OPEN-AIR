# prototype_device_interaction.py
#
# Prototype file to demonstrate the usage of DeviceUtility and its integration with the logging system.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Version 20251223.120000.proto
import os
import sys
import pathlib

# Add the project root to the sys.path to allow imports from workers and utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Mock app_constants (should already be created by the agent)
import workers.setup.app_constants as app_constants
from workers.logger.logger import debug_log, set_log_directory
from workers.utils.log_utils import _get_log_args
from utils.device_interface_util import DeviceUtility

# Override app_constants.LOCAL_DEBUG_ENABLE for this prototype if needed,
# though it's already set to True in the mock app_constants.py
app_constants.LOCAL_DEBUG_ENABLE = True

# --- Global Scope Variables for this prototype ---
Current_Date = 20251223
Current_Time = 120000
Current_iteration = 1

app_constants.current_version = "20251223.120000.proto" # Ensure consistent version for _get_log_args
current_file = os.path.basename(__file__)

def mock_gui_print(message: str):
    """
    A mock function to simulate printing to a GUI console.
    """
    print(f"🖥️ GUI Console Output: {message}")

def run_prototype():
    """
    Runs various scenarios to test the DeviceUtility class.
    """
    # Configure log directory for debug_log to write files
    log_dir_path = pathlib.Path("./DATA/debug_logs_prototype")
    log_dir_path.mkdir(parents=True, exist_ok=True)
    set_log_directory(log_dir_path)

    # Force enable debug for the prototype run
    app_constants.global_settings["general_debug_enabled"] = True
    app_constants.global_settings["debug_to_terminal"] = True
    app_constants.LOCAL_DEBUG_ENABLE = True


    print("\n--- Initializing DeviceUtility Prototype ---")
    device_manager = DeviceUtility(mock_gui_print)

    # Scenario 1: Successful data processing
    print("\n--- Scenario 1: Successful Data Processing ---")
    raw_data_success = "hello world"
    processed_output_success = device_manager.process_data_from_device(raw_data_success, 0)
    print(f"Prototype received (success): {processed_output_success}")

    # Scenario 2: Exceeding max retries
    print("\n--- Scenario 2: Exceeding Max Retries ---")
    raw_data_fail_retry = "problematic data"
    try:
        processed_output_fail_retry = device_manager.process_data_from_device(raw_data_fail_retry, device_manager.MAX_RETRIES + 1)
        print(f"Prototype received (retry failure): {processed_output_fail_retry}")
    except ValueError as e:
        print(f"Prototype caught expected error: {e}")

    # Scenario 3: General exception during processing (e.g., raw_data is not a string)
    print("\n--- Scenario 3: General Exception ---")
    raw_data_exception = 12345 # This will cause .upper() to fail
    processed_output_exception = device_manager.process_data_from_device(raw_data_exception, 0)
    print(f"Prototype received (general exception): {processed_output_exception}")

    # Scenario 4: Successful data processing with debug disabled
    print("\n--- Scenario 4: Successful Data Processing (Debug Disabled) ---")
    app_constants.LOCAL_DEBUG_ENABLE = False
    app_constants.global_settings["general_debug_enabled"] = False
    raw_data_debug_off = "silent mode"
    processed_output_debug_off = device_manager.process_data_from_device(raw_data_debug_off, 0)
    print(f"Prototype received (debug off): {processed_output_debug_off}")
    app_constants.LOCAL_DEBUG_ENABLE = True # Re-enable for subsequent runs if any
    app_constants.global_settings["general_debug_enabled"] = True


    print("\n--- Prototype Run Complete ---")

if __name__ == "__main__":
    run_prototype()
