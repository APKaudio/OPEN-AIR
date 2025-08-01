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
#
#
# Version 20250801.5 (Updated logic in update_connection_status_logic to remove references
#                     to 'resume_button' and 'skip_group_button', as these functionalities
#                     are now handled by the combined 'pause_resume_button' in ScanControlTab.
#                     Ensured correct state management for the combined pause/resume button.
#                     Updated debug_print calls with new current_version.)

current_version = "20250801.5" # this variable should always be defined below the header to make the debuggin better

import tkinter as tk
import inspect
import os # Added for os.path.exists check for preset folder

# Import debug_print from utils
from utils.utils_instrument_control import debug_print


def update_connection_status_logic(app_instance, is_connected, console_print_func):
    """
    Function Description:
    Updates the GUI elements based on the instrument connection status and scan status.
    This is the central function for managing button states across all relevant tabs.

    Inputs to this function:
        app_instance (App): The main application instance, used to access shared state
                            and tab instances.
        is_connected (bool): True if the instrument is connected, False otherwise.
        console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
        1. Logs the current connection status.
        2. Retrieves references to the parent tab instances from `app_instance`.
        3. From the parent tab instances, retrieves references to the specific child tabs
           (e.g., Instrument Connection tab, Scan Control tab).
        4. Determines the current scanning and pausing state from the Scan Control tab.
        5. Updates the state (enabled/disabled) of various buttons and
           other UI elements on the Instrument, Scan Control, Presets, Plotting, and Markers
           tabs based on `is_connected`, `is_scanning`, and `is_paused` flags.
        6. Logs debug messages if any expected tab instance is not found, indicating a potential
           initialization issue.

    Outputs of this function:
        None. Modifies the state of GUI elements.

    (2025-07-31) Change: Corrected tab access to go through parent tab instances (e.g., `app_instance.instrument_parent_tab.instrument_connection_tab`).
    (2025-07-31) Change: Added more robust debug logging for tab access.
    (2025-07-31) Change: Ensured button states are correctly set for `ScanControlTab` (start, pause, stop, resume, skip).
    (2025-07-31) Change: Ensured `PresetFilesTab` buttons (load from device, load selected, save preset, open folder) are correctly enabled/disabled.
    (2025-07-31) Change: Updated header.
    (2025-07-31) Change: Added `hasattr` checks for resume_button and skip_group_button in ScanControlTab
                          to prevent AttributeError if these buttons are not present in the class.
                          Also added hasattr checks for other buttons in PresetFilesTab and PlottingTab
                          for robustness.
    (2025-08-01) Change: Removed logic for 'resume_button' and 'skip_group_button' as they no longer exist as separate entities.
                          The 'pause_resume_button' in ScanControlTab now handles both pause and resume states.
                          Adjusted button state logic for the single 'pause_resume_button'.
    (2025-08-01) Change: Updated debug_print calls with current_version.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = f"src/scan_logic.py - {current_version}"
    debug_print(f"Updating connection status GUI elements. Connected: {is_connected}",
                file=current_file, function=current_function, console_print_func=console_print_func)

    # Get references to parent tabs (which are now attributes of app_instance)
    instrument_parent_tab = getattr(app_instance, 'instrument_parent_tab', None)
    scanning_parent_tab = getattr(app_instance, 'scanning_parent_tab', None)
    presets_parent_tab = getattr(app_instance, 'presets_parent_tab', None)
    plotting_parent_tab = getattr(app_instance, 'plotting_parent_tab', None)
    markers_parent_tab = getattr(app_instance, 'markers_parent_tab', None)

    # Get references to child tabs from their parent tabs
    instrument_tab = getattr(instrument_parent_tab, 'instrument_connection_tab', None) if instrument_parent_tab else None
    scan_control_tab = getattr(app_instance, 'scan_control_tab', None) # Directly under app_instance.
    preset_files_tab = getattr(presets_parent_tab, 'preset_files_tab', None) if presets_parent_tab else None
    plotting_tab = getattr(plotting_parent_tab, 'single_plotting_tab', None) if plotting_parent_tab else None
    markers_display_tab = getattr(markers_parent_tab, 'markers_display_tab', None) if markers_parent_tab else None


    # Determine scanning and paused states (default to False if tab not found)
    is_scanning = scan_control_tab.is_scanning if scan_control_tab and hasattr(scan_control_tab, 'is_scanning') else False
    is_paused = scan_control_tab.is_paused if scan_control_tab and hasattr(scan_control_tab, 'is_paused') else False

    debug_print(f"Scan status: Scanning={is_scanning}, Paused={is_paused}",
                file=current_file, function=current_function, console_print_func=console_print_func)


    # --- InstrumentTab buttons ---
    if instrument_tab:
        debug_print(f"Configuring InstrumentTab buttons. Connected: {is_connected}",
                    file=current_file, function=current_function, console_print_func=console_print_func)
        if is_connected:
            if hasattr(instrument_tab, 'connect_button'):
                instrument_tab.connect_button.grid_remove() # Hide connect button
            else:
                debug_print("InstrumentTab: connect_button not found. What the hell?!", file=current_file, function=current_function, console_print_func=console_print_func)

            if hasattr(instrument_tab, 'disconnect_button'):
                instrument_tab.disconnect_button.config(state=tk.NORMAL)
            else:
                debug_print("InstrumentTab: disconnect_button not found. Seriously?", file=current_file, function=current_function, console_print_func=console_print_func)

            if hasattr(instrument_tab, 'apply_settings_button'):
                instrument_tab.apply_settings_button.config(state=tk.NORMAL)
            else:
                debug_print("InstrumentTab: apply_settings_button not found. Unbelievable!", file=current_file, function=current_function, console_print_func=console_print_func)

            if hasattr(instrument_tab, 'query_settings_button'):
                instrument_tab.query_settings_button.config(state=tk.NORMAL)
            else:
                debug_print("InstrumentTab: query_settings_button not found. This is getting ridiculous!", file=current_file, function=current_function, console_print_func=console_print_func)

            debug_print("InstrumentTab: Connected state - Connect button hidden, Disconnect/Apply/Query enabled.",
                        file=current_file, function=current_function, console_print_func=console_print_func)
        else: # Instrument is disconnected
            if hasattr(instrument_tab, 'connect_button'):
                instrument_tab.connect_button.grid() # Show connect button
            else:
                debug_print("InstrumentTab: connect_button not found. Still missing!", file=current_file, function=current_function, console_print_func=console_print_func)

            if hasattr(instrument_tab, 'disconnect_button'):
                instrument_tab.disconnect_button.config(state=tk.DISABLED)
            else:
                debug_print("InstrumentTab: disconnect_button not found. Where is it?!", file=current_file, function=current_function, console_print_func=console_print_func)

            if hasattr(instrument_tab, 'apply_settings_button'):
                instrument_tab.apply_settings_button.config(state=tk.DISABLED)
            else:
                debug_print("InstrumentTab: apply_settings_button not found. Ugh!", file=current_file, function=current_function, console_print_func=console_print_func)

            if hasattr(instrument_tab, 'query_settings_button'):
                instrument_tab.query_settings_button.config(state=tk.DISABLED)
            else:
                debug_print("InstrumentTab: query_settings_button not found. Goddammit!", file=current_file, function=current_function, console_print_func=console_print_func)

            debug_print("InstrumentTab: Disconnected state - Connect button shown, Disconnect/Apply/Query disabled.",
                        file=current_file, function=current_function, console_print_func=console_print_func)
    else:
        debug_print("InstrumentTab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=current_file, function=current_function, console_print_func=console_print_func)

    # --- ScanControlTab buttons ---
    if scan_control_tab:
        debug_print(f"Configuring ScanControlTab buttons. Connected: {is_connected}, Scanning: {is_scanning}, Paused: {is_paused}",
                    file=current_file, function=current_function, console_print_func=console_print_func)
        if is_connected:
            if is_scanning and not is_paused:
                # Actively scanning
                if hasattr(scan_control_tab, 'start_button'):
                    scan_control_tab.start_button.config(state=tk.DISABLED)
                if hasattr(scan_control_tab, 'pause_resume_button'):
                    scan_control_tab.pause_resume_button.config(state=tk.NORMAL, text="Pause Scan", style='Orange.TButton')
                    scan_control_tab._stop_flashing() # Ensure no flashing if actively scanning
                if hasattr(scan_control_tab, 'stop_button'):
                    scan_control_tab.stop_button.config(state=tk.NORMAL)
                debug_print("ScanControlTab: Connected & Scanning - Start disabled, Pause/Resume enabled (as Pause), Stop enabled.",
                            file=current_file, function=current_function, console_print_func=console_print_func)
            elif is_scanning and is_paused:
                # Paused during a scan
                if hasattr(scan_control_tab, 'start_button'):
                    scan_control_tab.start_button.config(state=tk.DISABLED)
                if hasattr(scan_control_tab, 'pause_resume_button'):
                    scan_control_tab.pause_resume_button.config(state=tk.NORMAL, text="Resume Scan", style='Green.TButton')
                    scan_control_tab._start_flashing() # Start flashing when paused
                if hasattr(scan_control_tab, 'stop_button'):
                    scan_control_tab.stop_button.config(state=tk.NORMAL)
                debug_print("ScanControlTab: Connected & Paused - Start disabled, Pause/Resume enabled (as Resume and flashing), Stop enabled.",
                            file=current_file, function=current_function, console_print_func=console_print_func)
            else: # Connected but not scanning/paused (initial state or after stop)
                if hasattr(scan_control_tab, 'start_button'):
                    scan_control_tab.start_button.config(state=tk.NORMAL)
                if hasattr(scan_control_tab, 'pause_resume_button'):
                    scan_control_tab.pause_resume_button.config(state=tk.DISABLED, text="Pause Scan", style='Orange.TButton')
                    scan_control_tab._stop_flashing() # Ensure no flashing
                if hasattr(scan_control_tab, 'stop_button'):
                    scan_control_tab.stop_button.config(state=tk.DISABLED)
                debug_print("ScanControlTab: Connected & Not Scanning - Start enabled, Pause/Resume disabled, Stop disabled.",
                            file=current_file, function=current_function, console_print_func=console_print_func)
        else: # Not connected
            if hasattr(scan_control_tab, 'start_button'):
                scan_control_tab.start_button.config(state=tk.DISABLED)
            if hasattr(scan_control_tab, 'pause_resume_button'):
                scan_control_tab.pause_resume_button.config(state=tk.DISABLED, text="Pause Scan", style='Orange.TButton')
                scan_control_tab._stop_flashing() # Ensure no flashing
            if hasattr(scan_control_tab, 'stop_button'):
                scan_control_tab.stop_button.config(state=tk.DISABLED)
            debug_print("ScanControlTab: Disconnected - All scan control buttons disabled. Fucking useless without a connection!",
                        file=current_file, function=current_function, console_print_func=console_print_func)
    else:
        debug_print("ScanControlTab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=current_file, function=current_function, console_print_func=console_print_func)


    # --- PresetFilesTab buttons ---
    if preset_files_tab:
        debug_print(f"Configuring PresetFilesTab buttons. Connected: {is_connected}, Scanning: {is_scanning}",
                    file=current_file, function=current_function, console_print_func=console_print_func)
        # Load buttons: enabled if connected and not scanning
        load_state = tk.NORMAL if is_connected and not is_scanning else tk.DISABLED
        if hasattr(preset_files_tab, 'load_preset_from_device_button'):
            preset_files_tab.load_preset_from_device_button.config(state=load_state)
        else:
            debug_print("PresetFilesTab: load_preset_from_device_button not found.", file=current_file, function=current_function, console_print_func=console_print_func)

        if hasattr(preset_files_tab, 'load_selected_preset_button'):
            preset_files_tab.load_selected_preset_button.config(state=load_state)
        else:
            debug_print("PresetFilesTab: load_selected_preset_button not found.", file=current_file, function=current_function, console_print_func=console_print_func)

        if hasattr(preset_files_tab, 'save_preset_button'): # Assuming there's a save button
            preset_files_tab.save_preset_button.config(state=load_state)
        else:
            debug_print("PresetFilesTab: save_preset_button not found.", file=current_file, function=current_function, console_print_func=console_print_func)


        # Populate presets from device button
        populate_device_state = tk.NORMAL if is_connected and not is_scanning else tk.DISABLED
        if hasattr(preset_files_tab, 'populate_presets_from_device_button'):
            preset_files_tab.populate_presets_from_device_button.config(state=populate_device_state)
        else:
            debug_print("PresetFilesTab: populate_presets_from_device_button not found.", file=current_file, function=current_function, console_print_func=console_print_func)


        # Open preset folder button should always be enabled if the folder exists
        if hasattr(preset_files_tab, 'open_preset_folder_button'):
            # Check if the configured preset folder actually exists
            preset_folder = app_instance.config.get('LAST_USED_SETTINGS', 'last_scan_configuration__scan_directory', fallback='.')
            if os.path.exists(preset_folder):
                preset_files_tab.open_preset_folder_button.config(state=tk.NORMAL)
                debug_print("PresetFilesTab: Open Preset Folder button enabled (folder exists).",
                            file=current_file, function=current_function, console_print_func=console_print_func)
            else:
                preset_files_tab.open_preset_folder_button.config(state=tk.DISABLED)
                debug_print("PresetFilesTab: Open Preset Folder button disabled (folder does not exist). What the hell, where'd it go?!",
                            file=current_file, function=current_function, console_print_func=console_print_func)
        else:
            debug_print("PresetFilesTab: open_preset_folder_button not found.",
                        file=current_file, function=current_function, console_print_func=console_print_func)

        debug_print(f"PresetFilesTab buttons configured. Load state: {load_state}, Populate device state: {populate_device_state}",
                    file=current_file, function=current_function, console_print_func=console_print_func)
    else:
        debug_print("PresetFilesTab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=current_file, function=current_function, console_print_func=console_print_func)

    # --- Plotting tab buttons ---
    if plotting_tab:
        debug_print(f"Configuring PlottingTab buttons. Connected: {is_connected}, Scanning: {is_scanning}",
                    file=current_file, function=current_function, console_print_func=console_print_func)
        # Plot buttons should be enabled if there's data OR if connected (to allow plotting new data)
        # Here, we just ensure they are disabled if no instrument or scanning.
        if is_connected and not is_scanning:
            if hasattr(plotting_tab, 'plot_button'):
                plotting_tab.plot_button.config(state=tk.NORMAL)
            else:
                debug_print("PlottingTab: plot_button not found.", file=current_file, function=current_function, console_print_func=console_print_func)

            if hasattr(plotting_tab, 'plot_average_button'):
                plotting_tab.plot_average_button.config(state=tk.NORMAL)
            else:
                debug_print("PlottingTab: plot_average_button not found.", file=current_file, function=current_function, console_print_func=console_print_func)

            debug_print("PlottingTab: Connected & Not Scanning - Plot buttons enabled.",
                        file=current_file, function=current_function, console_print_func=console_print_func)
        else:
            if hasattr(plotting_tab, 'plot_button'):
                plotting_tab.plot_button.config(state=tk.DISABLED)
            if hasattr(plotting_tab, 'plot_average_button'):
                plotting_tab.plot_average_button.config(state=tk.DISABLED)
            debug_print("PlottingTab: Disconnected or Scanning - Plot buttons disabled.",
                        file=current_file, function=current_function, console_print_func=console_print_func)
    else:
        debug_print("PlottingTab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=current_file, function=current_function, console_print_func=console_print_func)

    # --- Markers Display Tab buttons (if any) ---
    if markers_display_tab:
        debug_print(f"Configuring MarkersDisplayTab. Connected: {is_connected}, Scanning: {is_scanning}",
                    file=current_file, function=current_function, console_print_func=console_print_func)
        # Assuming MarkersDisplayTab might have buttons that depend on connection/scan status
        # Example: if you have a button to "Query Markers from Instrument"
        # markers_display_tab.query_markers_button.config(state=tk.NORMAL if is_connected and not is_scanning else tk.DISABLED)
        # For now, no specific buttons to update in MarkersDisplayTab based on provided code
        pass
    else:
        debug_print("MarkersDisplayTab not found when updating connection status. This is a critical bug, fix this shit!",
                    file=current_file, function=current_function, console_print_func=console_print_func)