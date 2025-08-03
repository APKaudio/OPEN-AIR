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
# Version 20250802.2000.0 (Modified to keep Scan Configuration tab always enabled.)
# Version 20250802.2040.0 (Added hasattr check for connection_status_label in InstrumentTab.)
# Version 20250802.2050.0 (Added hasattr checks for scan control buttons.)

current_version = "20250802.2050.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 40 * 4 # Example hash, adjust as needed

import tkinter as tk
import inspect
import os # Added for os.path.exists check for preset folder

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log


def update_connection_status_logic(app_instance, is_connected, is_scanning, console_print_func):
    """
    Function Description:
    Updates the state (enabled/disabled) of various GUI elements across different tabs
    based on the instrument's connection status and the current scan state.
    This function acts as a central dispatcher for UI state changes.

    Inputs:
        app_instance (tk.Tk): The main application instance, providing access to its attributes.
        is_connected (bool): True if the instrument is connected, False otherwise.
        is_scanning (bool): True if a scan is active, False otherwise.
        console_print_func (callable): Function to print messages to the console.

    Process of this function:
        1. Logs the current connection and scanning status.
        2. Determines the appropriate state (tk.NORMAL or tk.DISABLED) for widgets.
        3. Updates the connection status label on the Instrument tab.
        4. Updates the state of various buttons and entry fields across different tabs:
            - Instrument Tab: Connect/Disconnect, Apply Settings, Query Settings, Send Command.
            - Scan Control Tab: Start/Stop/Pause/Resume Scan buttons.
            - JSON API Tab: Start/Stop API, Open Scan/Marker/All Scans API buttons.
        5. Ensures that the Scan Configuration tab remains enabled regardless of connection.

    Outputs of this function:
        None. Modifies the state of GUI widgets directly.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Updating connection status. Connected: {is_connected}, Scanning: {is_scanning}. Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    # Determine the general state for connection-dependent controls
    state = tk.NORMAL if is_connected else tk.DISABLED

    # --- Instrument Tab Controls ---
    instrument_tab = app_instance.get_tab_instance("Instrument", "Connection")
    if instrument_tab:
        if hasattr(instrument_tab, 'connection_status_label'): # Added hasattr check
            instrument_tab.connection_status_label.config(text=f"Status: {'Connected' if is_connected else 'Disconnected'}")

        # Connect/Disconnect Buttons
        instrument_tab.connect_button.config(state=tk.DISABLED if is_connected else tk.NORMAL)
        instrument_tab.disconnect_button.config(state=tk.NORMAL if is_connected else tk.DISABLED)

        # Resource Dropdown and Refresh
        if hasattr(instrument_tab, 'resource_dropdown'):
            instrument_tab.resource_dropdown.config(state=tk.DISABLED if is_connected else tk.NORMAL)
        if hasattr(instrument_tab, 'refresh_resources_button'):
            instrument_tab.refresh_resources_button.config(state=tk.DISABLED if is_connected else tk.NORMAL)

        # Apply Settings & Query Settings Buttons
        if hasattr(instrument_tab, 'apply_settings_button'):
            instrument_tab.apply_settings_button.config(state=state)
        if hasattr(instrument_tab, 'query_settings_button'):
            instrument_tab.query_settings_button.config(state=state)

        # Instrument Settings Entry Fields (Center Freq, Span, RBW, VBW, Sweep Time)
        # These should be enabled only if connected
        if hasattr(instrument_tab, 'center_freq_entry'):
            instrument_tab.center_freq_entry.config(state=state)
        if hasattr(instrument_tab, 'span_entry'):
            instrument_tab.span_entry.config(state=state)
        if hasattr(instrument_tab, 'rbw_entry'):
            instrument_tab.rbw_entry.config(state=state)
        if hasattr(instrument_tab, 'vbw_entry'):
            instrument_tab.vbw_entry.config(state=state)
        if hasattr(instrument_tab, 'sweep_time_entry'):
            instrument_tab.sweep_time_entry.config(state=state)

        debug_log("Instrument Tab buttons updated.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Instrument Tab instance not found.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    # --- VISA Interpreter Tab Controls ---
    visa_interpreter_tab = app_instance.get_tab_instance("Instrument", "VISA Interpreter")
    if visa_interpreter_tab:
        if hasattr(visa_interpreter_tab, 'send_command_button'):
            visa_interpreter_tab.send_command_button.config(state=state)
        if hasattr(visa_interpreter_tab, 'command_entry'):
            visa_interpreter_tab.command_entry.config(state=state)
        debug_log("VISA Interpreter Tab buttons updated.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_log("VISA Interpreter Tab instance not found.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    # --- Scan Control Tab Controls ---
    scan_control_tab = app_instance.get_tab_instance("Scanning", "Scan Control")
    if scan_control_tab:
        # Start button enabled only if connected and not scanning
        if hasattr(scan_control_tab, 'start_scan_button'): # Added hasattr check
            scan_control_tab.start_scan_button.config(state=tk.NORMAL if is_connected and not is_scanning else tk.DISABLED)
        # Stop button enabled only if scanning
        if hasattr(scan_control_tab, 'stop_scan_button'): # Added hasattr check
            scan_control_tab.stop_scan_button.config(state=tk.NORMAL if is_scanning else tk.DISABLED)
        # Pause/Resume buttons enabled only if scanning
        if hasattr(scan_control_tab, 'pause_scan_button'): # Added hasattr check
            scan_control_tab.pause_scan_button.config(state=tk.NORMAL if is_scanning and not app_instance.is_paused else tk.DISABLED)
        if hasattr(scan_control_tab, 'resume_scan_button'): # Added hasattr check
            scan_control_tab.resume_scan_button.config(state=tk.NORMAL if is_scanning and app_instance.is_paused else tk.DISABLED)
        debug_log("Scan Control Tab buttons updated.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Scan Control Tab instance not found.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    # --- Scan Configuration Tab Controls (Always Enabled) ---
    # This section ensures that all controls on the Scan Configuration tab
    # remain enabled, regardless of instrument connection status.
    scan_config_tab = app_instance.get_tab_instance("Scanning", "Scan Configuration")
    if scan_config_tab:
        # Enable all comboboxes and entry fields on this tab
        if hasattr(scan_config_tab, 'scan_name_entry'):
            scan_config_tab.scan_name_entry.config(state=tk.NORMAL)
        if hasattr(scan_config_tab, 'output_folder_entry'):
            scan_config_tab.output_folder_entry.config(state=tk.NORMAL)
        if hasattr(scan_config_tab, 'browse_output_folder_button'):
            scan_config_tab.browse_output_folder_button.config(state=tk.NORMAL)
        if hasattr(scan_config_tab, 'num_scan_cycles_combobox'):
            scan_config_tab.num_scan_cycles_combobox.config(state=tk.NORMAL)
        if hasattr(scan_config_tab, 'rbw_step_size_combobox'):
            scan_config_tab.rbw_step_size_combobox.config(state=tk.NORMAL)
        if hasattr(scan_config_tab, 'cycle_wait_time_combobox'):
            scan_config_tab.cycle_wait_time_combobox.config(state=tk.NORMAL)
        if hasattr(scan_config_tab, 'maxhold_time_combobox'):
            scan_config_tab.maxhold_time_combobox.config(state=tk.NORMAL)
        if hasattr(scan_config_tab, 'scan_rbw_combobox'):
            scan_config_tab.scan_rbw_combobox.config(state=tk.NORMAL)
        if hasattr(scan_config_tab, 'reference_level_combobox'):
            scan_config_tab.reference_level_combobox.config(state=tk.NORMAL)
        if hasattr(scan_config_tab, 'attenuation_combobox'):
            scan_config_tab.attenuation_combobox.config(state=tk.NORMAL)
        if hasattr(scan_config_tab, 'freq_shift_combobox'):
            scan_config_tab.freq_shift_combobox.config(state=tk.NORMAL)
        if hasattr(scan_config_tab, 'scan_mode_combobox'):
            scan_config_tab.scan_mode_combobox.config(state=tk.NORMAL)
        if hasattr(scan_config_tab, 'maxhold_checkbox'):
            scan_config_tab.maxhold_checkbox.config(state=tk.NORMAL)
        if hasattr(scan_config_tab, 'high_sensitivity_checkbox'):
            scan_config_tab.high_sensitivity_checkbox.config(state=tk.NORMAL)
        if hasattr(scan_config_tab, 'preamp_on_checkbox'):
            scan_config_tab.preamp_on_checkbox.config(state=tk.NORMAL)
        if hasattr(scan_config_tab, 'scan_rbw_segmentation_combobox'):
            scan_config_tab.scan_rbw_segmentation_combobox.config(state=tk.NORMAL)
        if hasattr(scan_config_tab, 'desired_default_focus_width_combobox'):
            scan_config_tab.desired_default_focus_width_combobox.config(state=tk.NORMAL)
        
        # Enable all band selection checkboxes
        for band_item in app_instance.band_vars:
            if "var_widget" in band_item and band_item["var_widget"] is not None: # Ensure widget exists
                band_item["var_widget"].config(state=tk.NORMAL)

        debug_log("Scan Configuration Tab controls are always enabled.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Scan Configuration Tab instance not found.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    # --- Scan Meta Data Tab Controls (Always Enabled) ---
    scan_meta_data_tab = app_instance.get_tab_instance("Scanning", "Scan Meta Data")
    if scan_meta_data_tab:
        # Enable all entry fields and comboboxes on this tab
        if hasattr(scan_meta_data_tab, 'operator_name_entry'):
            scan_meta_data_tab.operator_name_entry.config(state=tk.NORMAL)
        if hasattr(scan_meta_data_tab, 'operator_contact_entry'):
            scan_meta_data_tab.operator_contact_entry.config(state=tk.NORMAL)
        if hasattr(scan_meta_data_tab, 'venue_name_entry'):
            scan_meta_data_tab.venue_name_entry.config(state=tk.NORMAL)
        if hasattr(scan_meta_data_tab, 'postal_code_entry'):
            scan_meta_data_tab.postal_code_entry.config(state=tk.NORMAL)
        if hasattr(scan_meta_data_tab, 'lookup_postal_code_button'):
            scan_meta_data_tab.lookup_postal_code_button.config(state=tk.NORMAL)
        if hasattr(scan_meta_data_tab, 'address_field_entry'):
            scan_meta_data_tab.address_field_entry.config(state=tk.NORMAL)
        if hasattr(scan_meta_data_tab, 'city_entry'):
            scan_meta_data_tab.city_entry.config(state=tk.NORMAL)
        if hasattr(scan_meta_data_tab, 'province_entry'):
            scan_meta_data_tab.province_entry.config(state=tk.NORMAL)
        if hasattr(scan_meta_data_tab, 'scanner_type_combobox'):
            scan_meta_data_tab.scanner_type_combobox.config(state=tk.NORMAL)
        if hasattr(scan_meta_data_tab, 'antenna_type_combobox'):
            scan_meta_data_tab.antenna_type_combobox.config(state=tk.NORMAL)
        if hasattr(scan_meta_data_tab, 'antenna_mount_combobox'):
            scan_meta_data_tab.antenna_mount_combobox.config(state=tk.NORMAL)
        if hasattr(scan_meta_data_tab, 'antenna_amplifier_combobox'):
            scan_meta_data_tab.antenna_amplifier_combobox.config(state=tk.NORMAL)
        if hasattr(scan_meta_data_tab, 'notes_text_widget'):
            # ScrolledText widgets have a 'normal' state for editing
            scan_meta_data_tab.notes_text_widget.config(state=tk.NORMAL)
        
        debug_log("Scan Meta Data Tab controls are always enabled.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Scan Meta Data Tab instance not found.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    # --- Plotting Tab Controls ---
    plotting_tab = app_instance.get_tab_instance("Plotting", "Plotting")
    if plotting_tab:
        # Plotting buttons enabled only if scan data is available
        plot_state = tk.NORMAL if app_instance.scan_data_available else tk.DISABLED
        if hasattr(plotting_tab, 'plot_last_scan_button'):
            plotting_tab.plot_last_scan_button.config(state=plot_state)
        if hasattr(plotting_tab, 'plot_all_scans_button'):
            plotting_tab.plot_all_scans_button.config(state=tk.NORMAL) # Always enabled to load old scans
        if hasattr(plotting_tab, 'clear_all_scans_button'):
            plotting_tab.clear_all_scans_button.config(state=tk.NORMAL) # Always enabled to clear memory
        
        # Marker checkboxes
        if hasattr(plotting_tab, 'include_gov_markers_checkbox'):
            plotting_tab.include_gov_markers_checkbox.config(state=tk.NORMAL)
        if hasattr(plotting_tab, 'include_tv_markers_checkbox'):
            plotting_tab.include_tv_markers_checkbox.config(state=tk.NORMAL)
        if hasattr(plotting_tab, 'include_markers_checkbox'):
            plotting_tab.include_markers_checkbox.config(state=tk.NORMAL)
        if hasattr(plotting_tab, 'include_scan_intermod_markers_checkbox'):
            plotting_tab.include_scan_intermod_markers_checkbox.config(state=tk.NORMAL)
        if hasattr(plotting_tab, 'open_html_after_complete_checkbox'):
            plotting_tab.open_html_after_complete_checkbox.config(state=tk.NORMAL)
        if hasattr(plotting_tab, 'create_html_checkbox'):
            plotting_tab.create_html_checkbox.config(state=tk.NORMAL)

        debug_log("Plotting Tab buttons and checkboxes updated.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Plotting Tab instance not found.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    # --- Markers Tab Controls (Always Enabled) ---
    markers_tab = app_instance.get_tab_instance("Markers", "Markers Display")
    if markers_tab:
        # All marker display controls should be always enabled
        if hasattr(markers_tab, 'add_marker_button'):
            markers_tab.add_marker_button.config(state=tk.NORMAL)
        if hasattr(markers_tab, 'remove_marker_button'):
            markers_tab.remove_marker_button.config(state=tk.NORMAL)
        if hasattr(markers_tab, 'marker_frequency_entry'):
            markers_tab.marker_frequency_entry.config(state=tk.NORMAL)
        if hasattr(markers_tab, 'marker_label_entry'):
            markers_tab.marker_label_entry.config(state=tk.NORMAL)
        if hasattr(markers_tab, 'marker_listbox'):
            markers_tab.marker_listbox.config(state=tk.NORMAL)
        debug_log("Markers Tab controls are always enabled.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Markers Tab instance not found.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    # --- Presets Tab Controls (Always Enabled) ---
    presets_tab = app_instance.get_tab_instance("Presets", "Presets")
    if presets_tab:
        # All preset controls should be always enabled
        if hasattr(presets_tab, 'load_preset_button'):
            presets_tab.load_preset_button.config(state=tk.NORMAL)
        if hasattr(presets_tab, 'save_preset_button'):
            presets_tab.save_preset_button.config(state=tk.NORMAL)
        if hasattr(presets_tab, 'delete_preset_button'):
            presets_tab.delete_preset_button.config(state=tk.NORMAL)
        if hasattr(presets_tab, 'preset_name_entry'):
            presets_tab.preset_name_entry.config(state=tk.NORMAL)
        if hasattr(presets_tab, 'preset_listbox'):
            presets_tab.preset_listbox.config(state=tk.NORMAL)
        debug_log("Presets Tab controls are always enabled.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_log("Presets Tab instance not found.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    # --- JSON API Tab Controls ---
    json_api_tab = app_instance.get_tab_instance("Experiments", "JSON API") # Assuming JSON API is a child of Experiments
    if json_api_tab:
        if hasattr(json_api_tab, 'start_api_button'):
            json_api_tab.start_api_button.config(state=state)
        if hasattr(json_api_tab, 'stop_api_button'):
            json_api_tab.stop_api_button.config(state=state)
        if hasattr(json_api_tab, 'open_scan_in_progress_api_button'):
             # This button should be enabled only if a scan is active AND API is running
            json_api_tab.open_scan_in_progress_api_button.config(state=tk.NORMAL if is_scanning and hasattr(json_api_tab, 'api_process') and json_api_tab.api_process and json_api_tab.api_process.poll() is None else tk.DISABLED)
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
                function=current_function)
