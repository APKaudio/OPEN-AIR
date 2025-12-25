# utils/device_interface_util.py
#
# A utility module to handle the logic for interfacing with an external device.
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
Version = "20250821.200641.1"

import os
import inspect # For dynamic introspection required by _get_log_args
from workers.mqtt.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args



class DeviceUtility:
    """
    Manages communication logic with external devices.

    This utility acts as a translator in the application's data flow model:
    GUI <-> Utilities (this module) <-> Handlers <-> Translators <-> Device.
    It abstracts away the complexities of device interaction from the GUI,
    providing a clean interface for data processing and command dispatch.
    """
    def __init__(self, print_to_gui_func):
        # Maximum number of attempts to retry a data processing operation before giving up.
        # This prevents infinite loops on persistent issues.
        self.MAX_RETRIES = 3
        # Default timeout in seconds for device communication operations.
        # Ensures operations don't hang indefinitely.
        self.DEFAULT_TIMEOUT_S = 10
        self._print_to_gui_console = print_to_gui_func
        self.current_class_name = self.__class__.__name__

        def process_data_from_device(self, raw_data: str, retry_count: int):
            """
            Processes raw data received from an external device for GUI consumption.
    
            This function attempts to transform the raw data into a usable format.
            It includes retry logic and robust error handling to ensure data integrity
            and application stability.
    
            Args:
                raw_data (str): The unprocessed data string received from the device.
                retry_count (int): The current attempt number for processing this data.
    
            Returns:
                str | None: The processed data string if successful, otherwise None.
            """
            current_function_name = inspect.currentframe().f_code.co_name
    
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"🛠️🟢 Ahoy! Entering '{current_function_name}' to wrangle this beastly data payload. Preparing for processing...",
                    **_get_log_args())
    
            try:
                if app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                        message=f"🛠️🔵 Inspecting data. The payload appears to be {len(raw_data)} bytes long. A magnificent specimen, indeed!",
                        **_get_log_args())
    
                if retry_count > self.MAX_RETRIES:
                     self._print_to_gui_console("❌ Maximum retries exceeded. The device remains stubborn!")
                     raise ValueError("Too many failed attempts to process data.")
    
                # Perform the actual data processing (e.g., converting to uppercase for this example)
                processed_data = f"Processed: {raw_data.upper()}"
                self._print_to_gui_console("✅ Victory! The data has been tamed and processed successfully!")
                if app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                        message=f"🛠️✅ Data transformation complete! The beast is now a beauty: '{processed_data}'.",
                        **_get_log_args())
                return processed_data
            except Exception as e:
                if app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                    message=f"🛠️🔴 Blast and barnacles! The gears have jammed! A dreadful error (type: {type(e).__name__}) occurred: {e}. My calculations were... imperfect!",
                    **_get_log_args())
            return None