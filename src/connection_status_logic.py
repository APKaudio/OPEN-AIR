# src/connection_status_logic.py
#
# This file contains the core logic for updating the graphical user interface (GUI)
# elements based on the instrument's connection status and the current running state.
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
#
# Version 20250813.163700.1

import tkinter as tk
import inspect
import os

from display.debug_logic import debug_log
from display.console_logic import console_log

# --- Version Information ---
current_version = "20250813.163700.1"
current_version_hash = (20250813 * 163700 * 1)


def update_connection_status_logic(app_instance, is_connected, is_running, console_print_func):
    """
    Updates the state (enabled/disabled) of various GUI elements across different tabs
    based on the instrument's connection status and the current running state.
    This function acts as a central dispatcher for UI state changes.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Updating connection status. Connected: {is_connected}, Running: {is_running}. Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    # --- Instrument Tab ---
    if hasattr(app_instance, 'instrument_parent_tab') and hasattr(app_instance.instrument_parent_tab, 'instrument_settings_tab'):
        instrument_tab = app_instance.instrument_parent_tab.instrument_settings_tab
        if hasattr(instrument_tab, '_update_ui_state'):
            instrument_tab._update_ui_state()

    # --- Orchestrator GUI ---
    # CHANGED: Reference the new orchestrator_gui attribute
    if hasattr(app_instance, 'orchestrator_gui'):
        app_instance.orchestrator_gui._update_button_states()
        debug_log("Orchestrator GUI buttons updated.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Orchestrator GUI instance not found during status update.",
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