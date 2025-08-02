# src/scan_logic.py
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
# Version 20250802.0040.1 (Refactored debug_print to debug_log; updated imports and flair.)

current_version = "20250802.0040.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 40 * 1 # Example hash, adjust as needed

import tkinter as tk
import inspect
import os # Added for os.path.exists check for preset folder

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log


def update_connection_status_logic(app_instance, is_connected, is_scanning, console_print_func=None):
    """
    Function Description:
    Updates the enabled/disabled state of various GUI elements across different tabs
    based on the instrument's connection status and whether a scan is in progress.
    This ensures that users can only interact with relevant controls at any given time.

    Inputs:
    - app_instance (object): The main application instance, providing access to
                             all Tkinter variables and child tab instances.
    - is_connected (bool): True if the instrument is currently connected, False otherwise.
    - is_scanning (bool): True if a scan is currently in progress, False otherwise.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Prints a debug message.
    2. Retrieves references to various child tabs (Instrument Connection, Scan Control,
       Scan Configuration, Scan Meta Data, Plotting, Markers Display, Presets, JSON API).
    3. Iterates through relevant buttons/widgets in each tab and sets their state
       (tk.NORMAL or tk.DISABLED) based on `is_connected` and `is_scanning`.
    4. Handles specific logic for the Scan Control tab's pause/resume button.
    5. Logs the state changes for debugging.

    Outputs of this function:
    - None. Modifies Tkinter widget states.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Updating connection status logic. Connected: {is_connected}, Scanning: {is_scanning}. Adjusting UI!",
                file=__file__,
                version=current_version,
                function=current_function)

    # Get references to relevant tabs
    instrument_connection_tab = None
    scan_control_tab = None
    scan_config_tab = None
    scan_meta_data_tab = None
    plotting_tab = None
    markers_display_tab = None
    presets_tab = None
    json_api_tab = None # New: Reference to JSON API tab

    # Safely get tab references
    if hasattr(app_instance, 'instrument_parent_tab') and \
       hasattr(app_instance.instrument_parent_tab, 'instrument_connection_tab'):
        instrument_connection_tab = app_instance.instrument_parent_tab.instrument_connection_tab
    if hasattr(app_instance, 'scanning_parent_tab') and \
       hasattr(app_instance.scanning_parent_tab, 'scan_control_tab'):
        scan_control_tab = app_instance.scanning_parent_tab.scan_control_tab
    if hasattr(app_instance, 'scanning_parent_tab') and \
       hasattr(app_instance.scanning_parent_tab, 'scan_tab'):
        scan_config_tab = app_instance.scanning_parent_tab.scan_tab
    if hasattr(app_instance, 'scanning_parent_tab') and \
       hasattr(app_instance.scanning_parent_tab, 'scan_meta_data_tab'):
        scan_meta_data_tab = app_instance.scanning_parent_tab.scan_meta_data_tab
    if hasattr(app_instance, 'plotting_parent_tab') and \
       hasattr(app_instance.plotting_parent_tab, 'plotting_tab'):
        plotting_tab = app_instance.plotting_parent_tab.plotting_tab
    if hasattr(app_instance, 'markers_parent_tab') and \
       hasattr(app_instance.markers_parent_tab, 'markers_display_tab'):
        markers_display_tab = app_instance.markers_parent_tab.markers_display_tab
    if hasattr(app_instance, 'presets_parent_tab') and \
       hasattr(app_instance.presets_parent_tab, 'preset_files_tab'):
        presets_tab = app_instance.presets_parent_tab.preset_files_tab
    if hasattr(app_instance, 'experiments_parent_tab') and \
       hasattr(app_instance.experiments_parent_tab, 'json_api_tab'): # New: Get JSON API tab
        json_api_tab = app_instance.experiments_parent_tab.json_api_tab


    # --- Instrument Connection Tab buttons ---
    if instrument_connection_tab:
        debug_log(f"Configuring Instrument Connection Tab. Connected: {is_connected}, Scanning: {is_scanning}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        instrument_connection_tab.connect_button.config(state=tk.DISABLED if is_connected else tk.NORMAL)
        instrument_connection_tab.disconnect_button.config(state=tk.NORMAL if is_connected else tk.DISABLED)
        instrument_connection_tab.apply_settings_button.config(state=tk.NORMAL if is_connected and not is_scanning else tk.DISABLED)
        instrument_connection_tab.query_settings_button.config(state=tk.NORMAL if is_connected and not is_scanning else tk.DISABLED)
        
        # Resource dropdown and refresh button should be disabled during scan
        instrument_connection_tab.resource_dropdown.config(state=tk.DISABLED if is_scanning else tk.NORMAL)
        instrument_connection_tab.refresh_button.config(state=tk.DISABLED if is_scanning else tk.NORMAL)

        debug_log("Instrument Connection Tab buttons updated.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Instrument Connection Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    # --- Scan Control Tab buttons ---
    if scan_control_tab:
        debug_log(f"Configuring Scan Control Tab. Connected: {is_connected}, Scanning: {is_scanning}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        scan_control_tab._update_button_states() # Let the tab manage its own buttons
        debug_log("Scan Control Tab buttons updated via its internal method.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Scan Control Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    # --- Scan Configuration Tab buttons/widgets ---
    if scan_config_tab:
        debug_log(f"Configuring Scan Configuration Tab. Connected: {is_connected}, Scanning: {is_scanning}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        # Enable/disable dropdowns and checkboxes based on scan status
        state = tk.DISABLED if is_scanning else tk.NORMAL
        scan_config_tab.scan_rbw_segmentation_dropdown.config(state=state)
        scan_config_tab.scan_rbw_hz_dropdown.config(state=state)
        scan_config_tab.reference_level_dbm_dropdown.config(state=state)
        scan_config_tab.freq_shift_hz_dropdown.config(state=state)
        scan_config_tab.high_sensitivity_checkbox.config(state=state)
        scan_config_tab.preamp_on_checkbox.config(state=state)
        scan_config_tab.open_scan_data_folder_button.config(state=state) # This button should always be available
        
        # Band checkboxes should be disabled during a scan
        for band_item in app_instance.band_vars:
            band_item["checkbox"].config(state=state)

        debug_log("Scan Configuration Tab widgets updated.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Scan Configuration Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    # --- Scan Meta Data Tab widgets ---
    if scan_meta_data_tab:
        debug_log(f"Configuring Scan Meta Data Tab. Connected: {is_connected}, Scanning: {is_scanning}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        # All meta data entry fields should be disabled during a scan
        state = tk.DISABLED if is_scanning else tk.NORMAL
        scan_meta_data_tab.operator_name_entry.config(state=state)
        scan_meta_data_tab.venue_name_entry.config(state=state)
        scan_meta_data_tab.equipment_used_entry.config(state=state)
        scan_meta_data_tab.notes_text.config(state=state)
        scan_meta_data_tab.postal_code_entry.config(state=state)
        scan_meta_data_tab.lookup_location_button.config(state=state)
        scan_meta_data_tab.antenna_type_dropdown.config(state=state)
        scan_meta_data_tab.antenna_amplifier_dropdown.config(state=state)
        scan_meta_data_tab.scan_name_entry.config(state=state)
        scan_meta_data_tab.output_folder_button.config(state=state)
        scan_meta_data_tab.open_output_folder_button.config(state=tk.NORMAL) # Always enabled

        debug_log("Scan Meta Data Tab widgets updated.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Scan Meta Data Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    # --- Plotting Tab buttons ---
    if plotting_tab:
        debug_log(f"Configuring Plotting Tab. Connected: {is_connected}, Scanning: {is_scanning}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        # Plotting buttons should be disabled during a scan
        if hasattr(plotting_tab, 'plot_button'):
            plotting_tab.plot_button.config(state=tk.DISABLED if is_scanning else tk.NORMAL)
        if hasattr(plotting_tab, 'plot_average_button'):
            # This button also depends on collected_scans_dataframes being not empty
            plot_average_state = tk.DISABLED
            if not is_scanning and app_instance.collected_scans_dataframes:
                plot_average_state = tk.NORMAL
            plotting_tab.plot_average_button.config(state=plot_average_state)
        debug_log("PlottingTab: Disconnected or Scanning - Plot buttons disabled.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    else:
        debug_log("PlottingTab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    # --- Markers Display Tab buttons (if any) ---
    if markers_display_tab:
        debug_log(f"Configuring MarkersDisplayTab. Connected: {is_connected}, Scanning: {is_scanning}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        # Assuming MarkersDisplayTab might have buttons that depend on connection/scan status
        # For example, if you have a button to "Query Markers from Instrument"
        if hasattr(markers_display_tab, 'set_marker_button'): # Example button
            markers_display_tab.set_marker_button.config(state=tk.NORMAL if is_connected and not is_scanning else tk.DISABLED)
        if hasattr(markers_display_tab, 'query_marker_y_button'): # Example button
            markers_display_tab.query_marker_y_button.config(state=tk.NORMAL if is_connected and not is_scanning else tk.DISABLED)
        # Add other marker-related buttons/widgets here as needed
        pass
        debug_log("MarkersDisplayTab buttons updated.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    else:
        debug_log("MarkersDisplayTab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    # --- Presets Tab buttons ---
    if presets_tab:
        debug_log(f"Configuring Presets Tab. Connected: {is_connected}, Scanning: {is_scanning}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        # Buttons that interact with the instrument should be disabled during a scan
        if hasattr(presets_tab, 'query_device_presets_button'):
            presets_tab.query_device_presets_button.config(state=tk.NORMAL if is_connected and not is_scanning else tk.DISABLED)
        if hasattr(presets_tab, 'load_selected_preset_button'):
            presets_tab.load_selected_preset_button.config(state=tk.NORMAL if is_connected and not is_scanning else tk.DISABLED)
        if hasattr(presets_tab, 'save_current_settings_button'):
            presets_tab.save_current_settings_button.config(state=tk.NORMAL if is_connected and not is_scanning else tk.DISABLED)
        
        # User preset buttons (load/delete) should be enabled unless scanning, as they don't touch instrument
        if hasattr(presets_tab, 'user_preset_buttons_frame'): # Assuming a frame holds these
            for child_widget in presets_tab.user_preset_buttons_frame.winfo_children():
                if isinstance(child_widget, ttk.Button):
                    child_widget.config(state=tk.NORMAL if not is_scanning else tk.DISABLED)

        debug_log("Presets Tab buttons updated.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Presets Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    # --- JSON API Tab buttons ---
    if json_api_tab:
        debug_log(f"Configuring JSON API Tab. Connected: {is_connected}, Scanning: {is_scanning}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        # API control buttons should be disabled during a scan if they affect instrument state
        # Or if the API itself is tied to active scanning
        state = tk.NORMAL if not is_scanning else tk.DISABLED
        if hasattr(json_api_tab, 'start_api_button'):
            json_api_tab.start_api_button.config(state=state)
        if hasattr(json_api_tab, 'stop_api_button'):
            json_api_tab.stop_api_button.config(state=state)
        if hasattr(json_api_tab, 'open_scan_in_progress_api_button'):
             # This button should be enabled only if a scan is active AND API is running
            json_api_tab.open_scan_in_progress_api_button.config(state=tk.NORMAL if is_scanning and json_api_tab.api_process and json_api_tab.api_process.poll() is None else tk.DISABLED)
        if hasattr(json_api_tab, 'open_marker_api_button'):
            json_api_tab.open_marker_api_button.config(state=state) # Markers API can be accessed anytime
        if hasattr(json_api_tab, 'open_all_scans_api_button'):
            json_api_tab.open_all_scans_api_button.config(state=state) # All scans API can be accessed anytime

        debug_log("JSON API Tab buttons updated.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    else:
        debug_log("JSON API Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    debug_log("Finished updating all UI elements based on connection status. UI is now responsive!",
                file=__file__,
                version=current_version,
                function=current_function,
                special=True)
