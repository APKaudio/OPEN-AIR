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
# Version 20250802.0040.4 (Added hasattr checks for resource_dropdown in InstrumentTab.)

current_version = "20250802.0040.4" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 40 * 4 # Example hash, adjust as needed

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
                file=f"{os.path.basename(__file__)} - {current_version}", # Corrected file parameter
                version=current_version,
                function=current_function)

    # Get references to relevant tabs
    # (2025-08-02 11:42) Change: Corrected tab attribute names to match main_app.py and parent tab instantiations.
    instrument_connection_tab = None
    scan_control_tab = None
    scan_config_tab = None
    scan_meta_data_tab = None
    plotting_tab = None
    markers_display_tab = None
    presets_tab = None
    json_api_tab = None

    # Safely get tab references
    if hasattr(app_instance, 'instrument_parent_tab') and \
       hasattr(app_instance.instrument_parent_tab, 'instrument_connection_tab'):
        instrument_connection_tab = app_instance.instrument_parent_tab.instrument_connection_tab
    else:
        debug_log("Instrument Connection Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    if hasattr(app_instance, 'start_pause_stop_tab'):
        scan_control_tab = app_instance.start_pause_stop_tab
    else:
        debug_log("Scan Control Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    if hasattr(app_instance, 'scanning_parent_tab') and \
       hasattr(app_instance.scanning_parent_tab, 'scan_configuration_tab'):
        scan_config_tab = app_instance.scanning_parent_tab.scan_configuration_tab
    else:
        debug_log("Scan Configuration Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    if hasattr(app_instance, 'scanning_parent_tab') and \
       hasattr(app_instance.scanning_parent_tab, 'scan_meta_data_tab'):
        scan_meta_data_tab = app_instance.scanning_parent_tab.scan_meta_data_tab
    else:
        debug_log("Scan Meta Data Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    if hasattr(app_instance, 'plotting_tab'):
        plotting_tab = app_instance.plotting_tab
    else:
        debug_log("Plotting Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    if hasattr(app_instance, 'markers_display_tab'):
        markers_display_tab = app_instance.markers_display_tab
    else:
        debug_log("Markers Display Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    if hasattr(app_instance, 'presets_parent_tab') and \
       hasattr(app_instance.presets_parent_tab, 'preset_files_tab'):
        presets_tab = app_instance.presets_parent_tab.preset_files_tab
    else:
        debug_log("Presets Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    if hasattr(app_instance, 'json_api_tab'):
        json_api_tab = app_instance.json_api_tab
    else:
        debug_log("JSON API Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    # Determine the state for buttons
    state = tk.NORMAL if is_connected and not is_scanning else tk.DISABLED
    scan_active_state = tk.NORMAL if is_scanning else tk.DISABLED # For buttons active during scan

    # --- Instrument Connection Tab ---
    if instrument_connection_tab:
        # Check if resource_dropdown exists before trying to configure it
        if hasattr(instrument_connection_tab, 'resource_dropdown'):
            instrument_connection_tab.resource_dropdown.config(state=tk.DISABLED if is_scanning else tk.NORMAL)
            debug_log(f"Instrument Connection Tab: resource_dropdown state set to {instrument_connection_tab.resource_dropdown.cget('state')}.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        else:
            debug_log("Instrument Connection Tab: 'resource_dropdown' attribute not found. Skipping configuration.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

        if hasattr(instrument_connection_tab, 'connect_button'):
            instrument_connection_tab.connect_button.config(state=tk.DISABLED if is_connected or is_scanning else tk.NORMAL)
            debug_log(f"Instrument Connection Tab: connect_button state set to {instrument_connection_tab.connect_button.cget('state')}.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        if hasattr(instrument_connection_tab, 'disconnect_button'):
            instrument_connection_tab.disconnect_button.config(state=tk.NORMAL if is_connected and not is_scanning else tk.DISABLED)
            debug_log(f"Instrument Connection Tab: disconnect_button state set to {instrument_connection_tab.disconnect_button.cget('state')}.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        if hasattr(instrument_connection_tab, 'refresh_button'):
            instrument_connection_tab.refresh_button.config(state=tk.DISABLED if is_connected or is_scanning else tk.NORMAL)
            debug_log(f"Instrument Connection Tab: refresh_button state set to {instrument_connection_tab.refresh_button.cget('state')}.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        if hasattr(instrument_connection_tab, 'query_settings_button'):
            instrument_connection_tab.query_settings_button.config(state=tk.NORMAL if is_connected and not is_scanning else tk.DISABLED)
            debug_log(f"Instrument Connection Tab: query_settings_button state set to {instrument_connection_tab.query_settings_button.cget('state')}.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        if hasattr(instrument_connection_tab, 'apply_settings_button'):
            instrument_connection_tab.apply_settings_button.config(state=tk.NORMAL if is_connected and not is_scanning else tk.DISABLED)
            debug_log(f"Instrument Connection Tab: apply_settings_button state set to {instrument_connection_tab.apply_settings_button.cget('state')}.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        debug_log("Instrument Connection Tab buttons updated.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Instrument Connection Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    # --- Scan Control Tab ---
    if scan_control_tab:
        if hasattr(scan_control_tab, 'start_button'):
            scan_control_tab.start_button.config(state=tk.NORMAL if is_connected and not is_scanning else tk.DISABLED)
            debug_log(f"Scan Control Tab: start_button state set to {scan_control_tab.start_button.cget('state')}.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        if hasattr(scan_control_tab, 'pause_button'):
            scan_control_tab.pause_button.config(state=tk.NORMAL if is_scanning else tk.DISABLED)
            debug_log(f"Scan Control Tab: pause_button state set to {scan_control_tab.pause_button.cget('state')}.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        if hasattr(scan_control_tab, 'resume_button'):
            scan_control_tab.resume_button.config(state=tk.NORMAL if is_connected and scan_control_tab.is_paused else tk.DISABLED)
            debug_log(f"Scan Control Tab: resume_button state set to {scan_control_tab.resume_button.cget('state')}.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        if hasattr(scan_control_tab, 'stop_button'):
            scan_control_tab.stop_button.config(state=tk.NORMAL if is_scanning else tk.DISABLED)
            debug_log(f"Scan Control Tab: stop_button state set to {scan_control_tab.stop_button.cget('state')}.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        debug_log("Scan Control Tab buttons updated.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Scan Control Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    # --- Scan Configuration Tab ---
    if scan_config_tab:
        # Enable/disable all input widgets in scan_config_tab
        # Assuming scan_config_tab has a method or a list of widgets to control
        # For now, let's assume direct access to some key widgets
        for widget in [scan_config_tab.scan_name_entry,
                       scan_config_tab.output_folder_entry,
                       scan_config_tab.output_folder_button,
                       scan_config_tab.scan_mode_dropdown,
                       scan_config_tab.reference_level_dbm_dropdown,
                       scan_config_tab.attenuation_dropdown,
                       scan_config_tab.freq_shift_dropdown,
                       scan_config_tab.scan_rbw_segmentation_entry,
                       scan_config_tab.desired_default_focus_width_entry]:
            if hasattr(widget, 'config'): # Check if it's a configurable Tkinter widget
                widget.config(state=state)
        
        # Handle checkboxes separately as their state is managed differently
        for band_item in scan_config_tab.app_instance.band_vars:
            band_item["var_widget"].config(state=state) # Assuming var_widget is the Checkbutton widget

        debug_log("Scan Configuration Tab buttons and inputs updated.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Scan Configuration Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    # --- Scan Meta Data Tab ---
    if scan_meta_data_tab:
        for widget in [scan_meta_data_tab.operator_name_entry,
                       scan_meta_data_tab.operator_contact_entry,
                       scan_meta_data_tab.venue_name_entry,
                       scan_meta_data_tab.postal_code_entry,
                       scan_meta_data_tab.lookup_location_button,
                       scan_meta_data_tab.address_field_entry,
                       scan_meta_data_tab.city_entry,
                       scan_meta_data_tab.province_entry,
                       scan_meta_data_tab.equipment_used_entry,
                       scan_meta_data_tab.antenna_type_dropdown,
                       scan_meta_data_tab.antenna_description_entry,
                       scan_meta_data_tab.antenna_use_entry,
                       scan_meta_data_tab.antenna_mount_entry,
                       scan_meta_data_tab.antenna_amplifier_dropdown,
                       scan_meta_data_tab.amplifier_description_entry,
                       scan_meta_data_tab.amplifier_use_entry]:
            if hasattr(widget, 'config'):
                widget.config(state=state)
        
        if hasattr(scan_meta_data_tab, 'notes_text'):
            # ScrolledText widget's state is set differently
            notes_state = tk.NORMAL if is_connected and not is_scanning else tk.DISABLED
            scan_meta_data_tab.notes_text.config(state=notes_state)

        debug_log("Scan Meta Data Tab buttons and inputs updated.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Scan Meta Data Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    # --- Plotting Tab ---
    if plotting_tab:
        # Plotting buttons should be enabled if connected AND not scanning
        # or if disconnected but there's data to plot (e.g., from a previous scan)
        plot_button_state = tk.NORMAL if (is_connected and not is_scanning) or (not is_connected and not is_scanning and app_instance.raw_scan_data_for_current_sweep) else tk.DISABLED
        
        if hasattr(plotting_tab, 'plot_current_scan_button'):
            plotting_tab.plot_current_scan_button.config(state=plot_button_state)
        if hasattr(plotting_tab, 'plot_stitched_scan_button'):
            plotting_tab.plot_stitched_scan_button.config(state=plot_button_state)
        if hasattr(plotting_tab, 'plot_historical_scan_button'):
            plotting_tab.plot_historical_scan_button.config(state=tk.NORMAL if not is_scanning else tk.DISABLED) # Always allow historical plotting if not scanning
        if hasattr(plotting_tab, 'open_scan_folder_button'):
            plotting_tab.open_scan_folder_button.config(state=tk.NORMAL if not is_scanning else tk.DISABLED) # Always allow opening folder if not scanning

        debug_log("Plotting Tab buttons updated.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Plotting Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    # --- Markers Display Tab ---
    if markers_display_tab:
        # All marker display buttons should be enabled if connected and not scanning
        # or if not connected but there is data to process (e.g. from a loaded report)
        marker_display_state = tk.NORMAL if (is_connected and not is_scanning) or (not is_connected and not is_scanning and app_instance.markers_data_from_scan) else tk.DISABLED

        if hasattr(markers_display_tab, 'load_report_button'):
            markers_display_tab.load_report_button.config(state=tk.NORMAL if not is_scanning else tk.DISABLED) # Always allow loading reports if not scanning
        if hasattr(markers_display_tab, 'calculate_intermod_button'):
            markers_display_tab.calculate_intermod_button.config(state=marker_display_state)
        if hasattr(markers_display_tab, 'plot_intermod_button'):
            markers_display_tab.plot_intermod_button.config(state=marker_display_state)
        if hasattr(markers_display_tab, 'export_intermod_csv_button'):
            markers_display_tab.export_intermod_csv_button.config(state=marker_display_state)
        if hasattr(markers_display_tab, 'clear_markers_button'):
            markers_display_tab.clear_markers_button.config(state=marker_display_state)
        if hasattr(markers_display_tab, 'open_reports_folder_button'):
            markers_display_tab.open_reports_folder_button.config(state=tk.NORMAL if not is_scanning else tk.DISABLED) # Always allow opening reports folder if not scanning

        debug_log("Markers Display Tab buttons updated.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Markers Display Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    # --- Presets Tab ---
    if presets_tab:
        # Presets tab buttons should be enabled if connected and not scanning
        # or if not connected but there are user presets to load/save
        preset_state = tk.NORMAL if (is_connected and not is_scanning) or (not is_connected and not is_scanning and os.path.exists(os.path.join(os.path.dirname(app_instance.CONFIG_FILE_PATH), 'user_presets.csv'))) else tk.DISABLED

        if hasattr(presets_tab, 'query_device_presets_button'):
            presets_tab.query_device_presets_button.config(state=tk.NORMAL if is_connected and not is_scanning else tk.DISABLED)
        if hasattr(presets_tab, 'load_device_preset_button'):
            presets_tab.load_device_preset_button.config(state=tk.NORMAL if is_connected and not is_scanning else tk.DISABLED)
        if hasattr(presets_tab, 'save_user_preset_button'):
            presets_tab.save_user_preset_button.config(state=tk.NORMAL if is_connected and not is_scanning else tk.DISABLED)
        if hasattr(presets_tab, 'load_user_preset_button'):
            presets_tab.load_user_preset_button.config(state=preset_state)
        if hasattr(presets_tab, 'delete_user_preset_button'):
            presets_tab.delete_user_preset_button.config(state=preset_state)
        if hasattr(presets_tab, 'open_preset_folder_button'):
            presets_tab.open_preset_folder_button.config(state=tk.NORMAL if not is_scanning else tk.DISABLED) # Always allow opening folder if not scanning

        debug_log("Presets Tab buttons updated.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Presets Tab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    # --- JSON API Tab ---
    if json_api_tab:
        # JSON API buttons should be enabled if not scanning
        # The 'Open Scan In Progress API' button has special logic
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
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    # The else branch is now handled by the specific debug_log calls above for clarity


    debug_log("Finished updating all UI elements based on connection status. UI is now responsive!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function,
                special=True)
