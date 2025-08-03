# OPEN-AIR/main_app.py
#
# This is the main entry point for the RF Spectrum Analyzer Controller application.
# It handles initial setup, checks for and installs necessary Python dependencies,
# and then launches the main graphical user interface (GUI).
# This file ensures that the application environment is ready before starting the UI.
# It also centralizes Tkinter `ttk.Style` configurations for consistent button
# styling across the application, including font sizes and flashing states for buttons.
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
# Version 20250802.1701.15 (Updated imports and tab instantiation for refactored modules.)
# Version 20250802.1815.0 (Fixed KeyError: 'Shift' by using 'shift_hz' for frequency_shifts initialization.)
# Version 20250802.1910.1 (Fixed KeyError: 'Mode' by using 'Value' for scan_modes initialization.)
# Version 20250802.1945.0 (Initialized debug_to_gui_console_var and applied it.)
# Version 20250803.1346.0 (Added self.is_connected as tk.BooleanVar to App class initialization.)
# Version 20250803.1610.0 (Added _post_gui_setup to handle initial device refresh after mainloop starts.)
# Version 20250803.1620.0 (Fixed ImportError: cannot import name 'set_console_redirectors' by correcting import to 'set_gui_console_redirector'.)
# Version 20250803.1630.0 (Fixed ImportError: cannot import name 'get_clear_console_func' by correcting registration to set_clear_console_func and updated Program Map.)
# Version 20250803.1635.0 (Fixed TypeError: check_and_install_dependencies() missing 1 required positional argument: 'current_app_version'.)


current_version_string = "20250803.1635.0" # this variable should always be defined below the header to make the debugging better
current_version_hash_value = 20250803 * 1635 * 0 # Example hash, adjust as needed


# Program Map:
# This section outlines the directory and file structure of the OPEN-AIR RF Spectrum Analyzer Controller application,
# providing a brief explanation for each component.
#
# └── OPEN-AIR/
#     ├── DATA/                       - Contains application data: logs, markers, presets, and configuration files.
#     │   ├── Debug.log               - Application debug log file.
#     │   ├── MARKERS.CSV             - Stores user-defined markers.
#     │   ├── PRESETS.CSV             - Stores instrument presets.
#     │   ├── VISA_COMMANDS.CSV       - Default VISA commands for the interpreter.
#     │   ├── config.ini              - Application configuration settings (persisted).
#     │   └── ... (exported_presets, scan_data subdirectories)
#     ├── process_math/               - Modules for mathematical processing and data manipulation.
#     │   ├── averaging_utils.py      - Functions for averaging scan data.
#     │   ├── calculate_intermod.py   - Logic for calculating intermodulation products.
#     │   ├── google_maps_lookup.py   - Integrates with Google Maps API for location data.
#     │   ├── json_host.py            - Handles JSON API interactions for scan data.
#     │   ├── ploting_intermod_zones.py - Functions for plotting intermodulation zones.
#     │   └── scan_stitch.py          - Utilities for stitching together scan segments.
#     ├── ref/                        - Reference data and default lists.
#     │   ├── Antenna_type.py         - Defines antenna types.
#     │   ├── antenna_amplifier_type.py - Defines antenna amplifier types.
#     │   ├── default_settings.py     - Contains default application settings.
#     │   ├── frequency_bands.py      - Defines standard frequency bands.
#     │   └── ref_scanner_setting_lists.py - Lists for scanner settings.
#     ├── scan_data/                  - Stores raw and processed scan data files (e.g., CSVs).
#     ├── src/                        - Core application source code and utilities.
#     │   ├── check_Dependancies.py   - Checks and installs necessary Python dependencies.
#     │   ├── console_logic.py        - Manages GUI console output.
#     │   ├── debug_logic.py          - Centralized debug logging functionality.
#     │   ├── gui_elements.py         - Custom Tkinter GUI elements and redirectors.
#     │   ├── program_default_values.py - Defines default values for application variables.
#     │   ├── program_gui_utils.py    - Utility functions for GUI setup and management.
#     │   ├── program_initialization.py - Handles initial program setup and environment.
#     │   ├── program_shared_values.py - Centralizes Tkinter variables and trace callbacks.
#     │   ├── program_style.py        - Defines custom Tkinter ttk styles for theming.
#     │   └── settings_and_config/    - Configuration management.
#     │       ├── config_manager.py   - Functions for loading and saving application configuration.
#     │       └── restore_settings_logic.py - Logic for restoring default or last-used settings.
#     ├── tabs/                       - Contains individual tab implementations for the GUI.
#     │   ├── Console/                - Console output and debug controls tab.
#     │   │   └── ConsoleTab.py       - GUI for the application console and debug options.
#     │   ├── Experiments/            - Tab for various experimental features (JSON API, Intermod, Config).
#     │   │   ├── TAB_EXPERIMENTS_PARENT.py - Parent tab for experiments.
#     │   │   ├── tab_experiments_child_JSON_api.py - JSON API interface for scan data.
#     │   │   ├── tab_experiments_child_initial_configuration.py - Initial configuration editor.
#     │   │   ├── tab_experiments_child_intermod.py - Intermodulation calculation and display.
#     │   │   └── tab_experiments_colouring.py - Color scheme preview and selection.
#     │   ├── Instrument/             - Tab for instrument connection and control.
#     │   │   ├── instrument_logic.py - Core logic for instrument interaction.
#     │   │   ├── TAB_INSTRUMENT_PARENT.py - Parent tab for instrument controls.
#     │   │   ├── tab_instrument_child_connection.py - Handles instrument connection and status.
#     │   │   ├── tab_instrument_child_visa_interpreter.py - VISA command interpreter.
#     │   │   ├── utils_instrument_connection.py - Low-level VISA connection utilities.
#     │   │   ├── utils_instrument_initialize.py - Instrument initialization routines.
#     │   │   ├── utils_instrument_query_settings.py - Queries current instrument settings.
#     │   │   ├── utils_instrument_read_and_write.py - Safe read/write operations for VISA.
#     │   │   └── utils_yak_visa.py   - Utility for executing VISA commands.
#     │   ├── Markers/                - Tab for managing frequency markers.
#     │   │   ├── TAB_MARKERS_PARENT.py - Parent tab for markers.
#     │   │   ├── tab_markers_child_display.py - Displays and interacts with markers.
#     │   │   ├── tab_markers_child_import_and_edit.py - Imports and edits marker data.
#     │   │   ├── utils_markers.py    - Marker-related utility functions.
#     │   │   └── utils_report_converter.py - Converts external reports to marker CSVs.
#     │   ├── Plotting/               - Tab for visualizing scan data.
#     │   │   ├── TAB_PLOTTING_PARENT.py - Parent tab for plotting.
#     │   │   ├── tab_plotting_child_3D.py - 3D plotting of scan data over time.
#     │   │   ├── tab_plotting_child_Single.py - Plots single scan data.
#     │   │   ├── tab_plotting_child_average.py - Averages and plots multiple scan files.
#     │   │   ├── utils_plotting.py   - General plotting utilities.
#     │   │   └── utils_plotting_scans_over_time.py - Utilities for plotting scans over time.
#     │   ├── Presets/                - Tab for managing instrument presets.
#     │   │   ├── TAB_PRESETS_PARENT.py - Parent tab for presets.
#     │   │   ├── tab_presets_child_device.py - Manages device-specific presets.
#     │   │   ├── tab_presets_child_local.py - Manages locally saved presets.
#     │   │   ├── tab_presets_child_preset_editor.py - Editor for user presets.
#     │   │   ├── utils_preset_process.py - Utilities for processing preset files.
#     │   │   └── utils_preset_query_and_load.py - Queries and loads presets.
#     │   │   └── utils_push_preset.py - Pushes presets to the instrument.
#     │   ├── Scanning/               - Tab for configuring and performing scans.
#     │   │   ├── TAB_SCANNING_PARENT.py - Parent tab for scanning.
#     │   │   ├── tab_scanning_child_scan_configuration.py - Configures scan parameters.
#     │   │   ├── tab_scanning_child_scan_meta_data.py - Manages scan metadata.
#     │   │   └── utils_scan_instrument.py - Instrument control during scanning.
#     │   └── Start_Pause_Stop/       - Tab with scan control buttons.
#     │       ├── scan_control_logic.py - Core logic for starting, pausing, stopping scans.
#     │       └── tab_scan_controler_button_logic.py - GUI for scan control buttons.
#     └── main_app.py                 - The main application entry point.


import tkinter as tk
from tkinter import ttk
import os
import sys
import inspect # Import inspect module for debug_log
import configparser # For ConfigParser object

# Import functions from refactored modules
from src.program_check_Dependancies import check_and_install_dependencies
from src.program_initialization import initialize_program_environment
from src.program_shared_values import setup_tkinter_variables, create_trace_callback
from src.program_gui_utils import apply_saved_geometry, setup_styles, create_widgets
from src.settings_and_config.config_manager import save_config
from src.debug_logic import debug_log, set_debug_redirectors # Import set_debug_redirectors
from src.console_logic import console_log, set_gui_console_redirector, clear_console, set_clear_console_func # Corrected: get_clear_console_func to set_clear_console_func
from src.program_default_values import CONFIG_FILE_PATH, DATA_FOLDER_PATH # Import path constants


class App(tk.Tk):
    """
    Function Description:
    The main application class for the RF Spectrum Analyzer Controller.
    It inherits from `tk.Tk` and manages the overall GUI structure,
    application state variables, and core functionalities like configuration
    management and tab navigation.

    Inputs:
        None.

    Process:
        1. Initializes the Tkinter root window.
        2. Sets the window title and binds the close protocol.
        3. Initializes `ttk.Style` for custom theming.
        4. Calls `_setup_tkinter_vars` to create all application-wide Tkinter variables.
        5. Calls `initialize_program_environment` for initial setup (data dir, config).
        6. Calls `apply_saved_geometry` to set window size/position.
        7. Calls `setup_styles` to apply custom visual styles.
        8. Calls `_create_widgets` to build the GUI layout with nested tabs.
        9. Sets up console and debug output redirection to the GUI.
        10. Schedules `_post_gui_setup` to run after the mainloop starts.

    Outputs:
        None. Initializes and runs the main application GUI.
    """
    def __init__(self):
        super().__init__()
        self.current_version = current_version_string # Set instance version
        self.current_version_hash = current_version_hash_value # Set instance version hash

        self.title(f"OPEN-AIR RF Spectrum Analyzer Controller (v{self.current_version})")
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.style = ttk.Style(self) # Pass self to ttk.Style

        # Initialize Tkinter variables (moved to program_shared_values.py)
        setup_tkinter_variables(self)

        # Initialize program environment (data directories, config loading, initial debug setup)
        initialize_program_environment(self)

        # Apply saved window geometry
        apply_saved_geometry(self)

        # Setup custom styles
        setup_styles(self)

        # Create main widgets (paned window, notebooks, tabs)
        create_widgets(self)

        # Set up console output redirection to the GUI console
        # This must happen AFTER the ConsoleTab and its ScrolledText widget are created
        if self.console_tab and hasattr(self.console_tab, 'console_text'):
            set_gui_console_redirector(self.console_tab.console_text, self.console_tab.console_text)
            set_debug_redirectors(self.console_tab.console_text, self.console_tab.console_text)
            debug_log(f"Console and debug output redirected to GUI. Version: {self.current_version}.",
                        file=f"{os.path.basename(__file__)} - {self.current_version}",
                        version=self.current_version,
                        function=inspect.currentframe().f_code.co_name,
                        special=True)
            # Register the clear console function
            set_clear_console_func(self.console_tab.clear_console_text)
        else:
            debug_log(f"WARNING: ConsoleTab or console_text not available for redirection. Output will go to terminal. Version: {self.current_version}.",
                        file=f"{os.path.basename(__file__)} - {self.current_version}",
                        version=self.current_version,
                        function=inspect.currentframe().f_code.co_name,
                        special=True)

        # Schedule post-GUI setup tasks to run after the mainloop starts
        self.after(100, self._post_gui_setup)


        debug_log(f"App initialized. Version: {self.current_version}. GUI is ready!",
                    file=f"{os.path.basename(__file__)} - {self.current_version}",
                    version=self.current_version,
                    function=inspect.currentframe().f_code.co_name,
                    special=True)

    def _post_gui_setup(self):
        """
        Function Description:
        Performs setup tasks that need to run after the Tkinter mainloop has started.
        This includes initial population of dynamic GUI elements like VISA resources.

        Inputs:
            None.

        Process:
            1. Retrieves the InstrumentTab instance.
            2. Calls its `_refresh_devices()` method to populate the VISA resource combobox.

        Outputs:
            None. Updates GUI elements.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Executing post-GUI setup tasks. Version: {self.current_version}.",
                    file=f"{os.path.basename(__file__)} - {self.current_version}",
                    version=self.current_version,
                    function=current_function,
                    special=True)

        # Get the InstrumentTab instance and trigger its device refresh
        instrument_tab = self.get_tab_instance("Instrument", "Connection")
        if instrument_tab and hasattr(instrument_tab, '_refresh_devices'):
            instrument_tab._refresh_devices()
            debug_log(f"Triggered initial device refresh on InstrumentTab. Version: {self.current_version}.",
                        file=f"{os.path.basename(__file__)} - {self.current_version}",
                        version=self.current_version,
                        function=current_function,
                        special=True)
        else:
            debug_log(f"WARNING: Could not find InstrumentTab or _refresh_devices method for post-GUI setup. Version: {self.current_version}.",
                        file=f"{os.path.basename(__file__)} - {self.current_version}",
                        version=self.current_version,
                        function=current_function,
                        special=True)


    def _on_closing(self):
        """
        Function Description:
        Handles the application closing event.
        Saves the current window geometry and paned window sash position
        to the configuration file before destroying the window.

        Inputs:
            None.

        Process:
            1. Prints a debug message.
            2. Saves the current window geometry.
            3. Saves the main paned window's sash position.
            4. Saves the entire application configuration to `config.ini`.
            5. Destroys the main application window.

        Outputs:
            None. Persists settings and exits the application.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Application closing. Version: {self.current_version}. Saving configuration...",
                    file=f"{os.path.basename(__file__)} - {self.current_version}",
                    version=self.current_version,
                    function=current_function,
                    special=True)

        # Save current window geometry
        self.config.set('LAST_USED_SETTINGS', 'last_GLOBAL__window_geometry', self.geometry())
        debug_log(f"Saved window geometry: {self.geometry()}.",
                    file=f"{os.path.basename(__file__)} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        # Save paned window sash position
        # Check if main_panedwindow exists and has sashes
        if hasattr(self, 'main_panedwindow') and self.main_panedwindow.sash_coords(0):
            sash_position = self.main_panedwindow.sash_coord(0)
            self.config.set('LAST_USED_SETTINGS', 'last_GLOBAL__paned_window_sash_position', str(sash_position))
            debug_log(f"Saved paned window sash position: {sash_position}.",
                        file=f"{os.path.basename(__file__)} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        else:
            debug_log(f"No main_panedwindow or sash found to save position. Skipping. Version: {self.current_version}.",
                        file=f"{os.path.basename(__file__)} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)


        # Save the entire configuration
        save_config(self.config, CONFIG_FILE_PATH, console_log, self)

        debug_log(f"Configuration saved. Destroying application. Version: {self.current_version}. Goodbye!",
                    file=f"{os.path.basename(__file__)} - {self.current_version}",
                    version=self.current_version,
                    function=current_function,
                    special=True)
        self.destroy()

    def _on_parent_tab_change(self, event):
        """
        Function Description:
        Event handler for when the main (parent) notebook tab is changed.
        This method is responsible for triggering actions specific to the newly
        selected parent tab, such as displaying ASCII art or refreshing child tab content.

        Inputs:
            event (tk.Event): The event object.

        Process:
            1. Identifies the newly selected parent tab.
            2. If the "Instrument" tab is selected, it calls its `_on_parent_tab_selected`
                method to display ASCII art and potentially refresh child tab content.
            3. Propagates the tab change event to the currently visible child tab
                within the selected parent tab, if that child tab has an `_on_tab_selected` method.

        Outputs:
            None. Updates GUI elements based on tab selection.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Parent tab changed event triggered. Version: {self.current_version}. New tab, new adventure!",
                    file=f"{os.path.basename(__file__)} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        selected_tab_id = self.parent_notebook.select()
        selected_tab_widget = self.parent_notebook.nametowidget(selected_tab_id)

        # Check if the selected tab is the Instrument tab and call its specific handler
        if selected_tab_widget == self.instrument_parent_tab:
            debug_log(f"Instrument Parent Tab selected. Version: {self.current_version}. Time to show some instrument love! 🎶",
                        file=f"{os.path.basename(__file__)} - {self.current_version}",
                        version=self.current_version,
                        function=current_function,
                        special=True)
            # Call the _on_parent_tab_selected method of the InstrumentTab
            if hasattr(self.instrument_parent_tab, '_on_parent_tab_selected'):
                self.instrument_parent_tab._on_parent_tab_selected(event)


        # Also ensure the currently visible child tab gets its _on_tab_selected called
        # This handles cases where a child tab might need to refresh its content
        # when its parent tab becomes active.
        selected_child_tab_id = None
        if selected_tab_widget in self.child_notebooks.values():
            # If the selected_tab_widget is itself a child_notebook (e.g., if a parent tab has no sub-tabs directly,
            # but is acting as a placeholder for a single child tab), then we need to get its selected tab.
            # This logic might need refinement based on how exactly child_notebooks are structured.
            # For now, let's assume selected_tab_widget is the parent tab frame, and we get its child notebook.
            pass # This path is generally not taken if parent_notebook adds TAB_X_PARENT instances directly

        # More robust way to get the active child tab:
        # Iterate through parent_tab_widgets to find the currently selected parent,
        # then get its active child tab.
        active_parent_tab_name = self.parent_notebook.tab(selected_tab_id, "text")
        active_parent_tab_instance = self.parent_tab_widgets.get(active_parent_tab_name)

        if active_parent_tab_instance and hasattr(active_parent_tab_instance, 'child_notebook'):
            child_notebook = active_parent_tab_instance.child_notebook
            if child_notebook:
                selected_child_tab_id = child_notebook.select()
                if selected_child_tab_id:
                    selected_child_tab_widget = child_notebook.nametowidget(selected_child_tab_id)
                    if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                        selected_child_tab_widget._on_tab_selected(event)
                        debug_log(f"Propagated _on_tab_selected to active child tab: {selected_child_tab_widget.winfo_name()}. Version: {self.current_version}.",
                                    file=f"{os.path.basename(__file__)} - {self.current_version}",
                                    version=self.current_version,
                                    function=current_function)
                    else:
                        debug_log(f"Active child tab {selected_child_tab_widget.winfo_name()} has no _on_tab_selected method. Version: {self.current_version}. What the hell?!",
                                    file=f"{os.path.basename(__file__)} - {self.current_version}",
                                    version=self.current_version,
                                    function=current_function)
                else:
                    debug_log(f"No child tab selected in {active_parent_tab_name}'s child notebook. Version: {self.current_version}. Skipping child tab event.",
                                file=f"{os.path.basename(__file__)} - {self.current_version}",
                                version=self.current_version,
                                function=current_function)
            else:
                debug_log(f"Parent tab {active_parent_tab_name} has no child notebook. Version: {self.current_version}. Skipping child tab event.",
                            file=f"{os.path.basename(__file__)} - {self.current_version}",
                            version=self.current_version,
                            function=current_function)
        else:
            debug_log(f"Selected parent tab {active_parent_tab_name} has no instance or child notebook. Version: {self.current_version}. Skipping child tab event.",
                        file=f"{os.path.basename(__file__)} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)


    def get_tab_instance(self, parent_tab_name, child_tab_name=None):
        """
        Function Description:
        Retrieves an instance of a specified tab (either parent or child).

        Inputs:
            parent_tab_name (str): The name of the parent tab (e.g., "Instrument").
            child_tab_name (str, optional): The name of the child tab (e.g., "Connection").
                                            If None, returns the parent tab instance.

        Process:
            1. Checks if the parent tab exists in `self.tab_instances`.
            2. If `child_tab_name` is provided, checks for the child tab within the parent.
            3. Returns the requested tab instance or None if not found.

        Outputs:
            The instance of the requested tab, or None if not found.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Attempting to get tab instance: Parent='{parent_tab_name}', Child='{child_tab_name}'. Version: {self.current_version}.",
                    file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                    version=self.current_version,
                    function=current_function)

        if parent_tab_name not in self.tab_instances:
            debug_log(f"ERROR: Parent tab '{parent_tab_name}' not found in tab_instances. Version: {self.current_version}.",
                        file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                        version=self.current_version,
                        function=current_function)
            return None

        if child_tab_name:
            if child_tab_name not in self.tab_instances[parent_tab_name]:
                debug_log(f"ERROR: Child tab '{child_tab_name}' not found in parent '{parent_tab_name}'. Version: {self.current_version}.",
                            file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                            version=self.current_version,
                            function=current_function)
                return None
            return self.tab_instances[parent_tab_name][child_tab_name]
        else:
            return self.parent_tab_widgets.get(parent_tab_name)

def current_version():
    # This function is a placeholder and should ideally reflect the version from the header.
    # For now, it returns the string directly.
    # This global function is kept for backward compatibility if other modules
    # are still importing it directly, but the App class now uses its own instance attribute.
    return current_version_string

def current_version_hash():
    # This function is a placeholder for the hash calculation.
    # In a real scenario, you'd calculate a hash of the file content.
    # For now, it returns the example hash.
    # This global function is kept for backward compatibility.
    return current_version_hash_value

if __name__ == "__main__":
    print("Instantiating App.") # Diagnostic print
    # Check and install dependencies first
    check_and_install_dependencies(current_version_string) # Pass current_version_string
    
    app = App()
    app.mainloop()
