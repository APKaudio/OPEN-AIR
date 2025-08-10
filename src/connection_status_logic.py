# src/connection_status_logic.py
#
# This file contains the core logic for updating the graphical user interface (GUI)
# elements based on the instrument's connection status and the current scan state.
# It acts as a centralized function to enable or disable buttons and other widgets
# across various tabs, ensuring the UI accurately reflects the application's status.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
# Version 20250803.200000.0 (FIXED: Circular dependency by using hasattr instead of get_tab_instance.)
# Version 20250803.195000.0 (FIXED: Added checks to ensure tab instances exist before access.)
# Version 20250802.2050.0 (Added hasattr checks for scan control buttons.)
# Version 20250802.2040.0 (Added hasattr check for connection_status_label in InstrumentTab.)
# Version 20250802.2000.0 (Modified to keep Scan Configuration tab always enabled.)

current_version = "20250803.200000.0"

import tkinter as tk
import inspect
import os

from display.debug_logic import debug_log
from display.console_logic import console_log


def update_connection_status_logic(app_instance, is_connected, is_scanning, console_print_func):
    """
    Updates the state (enabled/disabled) of various GUI elements across different tabs
    based on the instrument's connection status and the current scan state.
    This function acts as a central dispatcher for UI state changes.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Updating connection status. Connected: {is_connected}, Scanning: {is_scanning}. Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    # --- Instrument Tab ---
    # This check is safe because it doesn't call back into main_app. It just checks for attributes.
    if hasattr(app_instance, 'instrument_parent_tab') and hasattr(app_instance.instrument_parent_tab, 'instrument_settings_tab'):
        instrument_tab = app_instance.instrument_parent_tab.instrument_settings_tab
        if hasattr(instrument_tab, '_update_ui_state'):
            instrument_tab._update_ui_state() # Delegate state management to the tab itself

    # --- Scan Control Tab ---
    if hasattr(app_instance, 'scan_control_tab'):
        app_instance.scan_control_tab._update_button_states()
        debug_log("Scan Control Tab buttons updated.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Scan Control Tab instance not found during status update.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    # --- Presets Tab ---
    if hasattr(app_instance, 'presets_parent_tab') and hasattr(app_instance.presets_parent_tab, 'device_presets_tab'):
        device_presets_tab = app_instance.presets_parent_tab.device_presets_tab
        if hasattr(device_presets_tab, 'handle_connection_status_change_event'):
            device_presets_tab.handle_connection_status_change_event()
            debug_log("Device Presets Tab notified of connection change.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

    debug_log("Finished updating all UI elements based on connection status. UI is now responsive!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
