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
# Version 20250802.1945.0 (Initialized debug_to_gui_console_var and applied it in _check_config_and_set_debug.)
# Version 20250802.1950.0 (Corrected `main_app.py` to ensure it's complete and not truncated.)
# Version 20250802.2040.0 (Updated Tkinter variable initializations to use 'value' key from ref_scanner_setting_lists.py.)
# Version 20250802.2045.0 (FIXED: Removed duplicate _setup_tkinter_vars and corrected KeyError: 'Value' by using 'value' key consistently.)
# Version 20250802.2100.0 (CRITICAL FIX: Restored full file content after previous truncation and verified all 'value' key usages.)
# Version 20250802.2105.0 (FIXED: TclError: Invalid slave specification in _on_parent_tab_change by correcting tab iteration logic.)
# Version 20250803.0144.1 (Added ASCII art display to _on_parent_tab_change for each parent tab selection.)
# Version 20250803.1410.0 (Deferred _refresh_devices call until after mainloop starts to fix RuntimeError.)
# Version 20250803.1415.0 (Restored full _setup_tkinter_vars and setting_var_map that were accidentally truncated.)
# Version 20250803.1420.0 (Added diagnostic prints to trace App initialization and type of self.)
# Version 20250803.1425.0 (Added more detailed diagnostic prints for self type and hasattr check before _ensure_data_directory_exists.)
# Version 20250803.1430.0 (Refactored _ensure_data_directory_exists, config loading, and debug setup into src/program_initialization.py.)
# Version 20250803.1435.0 (FIXED: AttributeError: '_tkinter.tkapp' object has no attribute 'current_version' by making current_version an App instance attribute.)
# Version 20250803.1445.0 (Removed _setup_tkinter_vars and called new setup_tkinter_variables from program_initial_values.py.)
# Version 20250803.1450.0 (Updated import for setup_tkinter_variables to program_shared_values.py and removed _setup_tkinter_vars method.)
# Version 20250803.1500.0 (Moved _apply_saved_geometry and _setup_styles to src/gui_utils.py)
# Version 20250803.1505.0 (Moved _create_widgets to src/gui_utils.py as create_widgets)
# Version 20250803.1510.0 (Fixed AttributeError: '_tkinter.tkapp' object has no attribute '_create_widgets' by calling create_widgets from gui_utils.)

current_version_string = "20250803.1510.0" # this variable should always be defined below the header to make the debugging better
current_version_hash_value = 20250803 * 1510 * 0 # Example hash, adjust as needed


# Project file structure
#└── OPEN-AIR/
#       ├── DATA/
#       ├── process_math/
#       ├── ref/
#       ├── scan_data/
#       ├── src/
#       ├── tabs/
#       │   ├── Console/ # NEW
#       │   ├── Experiments/
#       │   ├── Instrument/
#       │   ├── Markers/
#       │   ├── Plotting/
#       │   ├── Presets/
#       │   └── Scanning/
#       └── utils/

import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, TclError, ttk
import os
import sys
import threading
import time
import pyvisa
import configparser
import inspect
from datetime import datetime # For timestamp in debug_log


# Import local modules - Paths are relative to OPEN-AIR as main_app.py is in OPEN-AIR
# and src, tabs, utils, ref are direct subdirectories.
from src.settings_and_config.config_manager import load_config, save_config
from src.gui_elements import TextRedirector, display_splash_screen, _print_inst_ascii, _print_scan_ascii, _print_plot_ascii, _print_marks_ascii, _print_presets_ascii, _print_xxx_ascii # Import all ASCII art functions

# Import the new debug_logic and console_logic modules as modules to avoid circular import issues
import src.debug_logic as debug_logic_module
import src.console_logic as console_logic_module
from src.program_initialization import initialize_program_environment # NEW: Import the initialization function
from src.program_shared_values import setup_tkinter_variables # NEW: Import setup_tkinter_variables from program_shared_values.py
from src.program_gui_utils import apply_saved_geometry, setup_styles, create_widgets # NEW: Import GUI utility functions including create_widgets


from tabs.Instrument.instrument_logic import (
    populate_resources_logic,
    connect_instrument_logic,
    disconnect_instrument_logic, # Added disconnect_instrument_logic
    apply_settings_logic, # Corrected function name from apply_instrument_settings_logic
    query_current_settings_logic # Corrected function name from query_current_instrument_settings_logic
)
from src.connection_status_logic import update_connection_status_logic
from src.settings_and_config.restore_settings_logic import restore_default_settings_logic, restore_last_used_settings_logic
from tabs.Start_Pause_Stop.tab_scan_controler_button_logic import ScanControlTab
from src.check_Dependancies import check_and_install_dependencies


# Import the new parent tab classes
from tabs.Instrument.TAB_INSTRUMENT_PARENT import TAB_INSTRUMENT_PARENT
from tabs.Scanning.TAB_SCANNING_PARENT import TAB_SCANNING_PARENT
from tabs.Plotting.TAB_PLOTTING_PARENT import TAB_PLOTTING_PARENT
from tabs.Markers.TAB_MARKERS_PARENT import TAB_MARKERS_PARENT
from tabs.Presets.TAB_PRESETS_PARENT import TAB_PRESETS_PARENT
from tabs.Experiments.TAB_EXPERIMENTS_PARENT import TAB_EXPERIMENTS_PARENT
from tabs.Console.ConsoleTab import ConsoleTab # NEW: Import ConsoleTab directly


# Removed old preset logic imports as they are now handled by the new utility files
# from tabs.Presets.utils_preset import load_selected_preset_logic, query_device_presets_logic


# Import constants from frequency_bands.py
from ref.frequency_bands import SCAN_BAND_RANGES, MHZ_TO_HZ, VBW_RBW_RATIO
# NEW: Import scan_modes, attenuation_levels, and frequency_shift_presets for initializing Tkinter variables
from ref.ref_scanner_setting_lists import scan_modes, attenuation_levels, frequency_shift_presets, graph_quality_drop_down, number_of_scans_presets, rbw_presets, dwell_time_drop_down, cycle_wait_time_presets, reference_level_drop_down

print("App class defined.") # Diagnostic print

class App(tk.Tk):
    """
    Main application class for the RF Spectrum Analyzer Controller.
    This class inherits from Tkinter's Tk class to create the main window
    and manage the overall application flow, including GUI setup, instrument
    communication, and data processing.
    """
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    # FUCKING IMPORTANT: Update CONFIG_FILE_PATH to the new DATA directory location!
    # The DATA folder is now located directly within the application's root (where main_app.py resides)
    DATA_FOLDER_PATH = os.path.join(_script_dir, 'DATA') # Changed to place DATA folder inside OPEN-AIR
    CONFIG_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'config.ini') # Now points to DATA folder
    PRESETS_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'PRESETS.CSV') # Moved to DATA folder
    MARKERS_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'MARKERS.CSV') # Moved to DATA folder
    VISA_COMMANDS_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'VISA_COMMANDS.CSV') # Moved to DATA folder
    DEBUG_COMMANDS_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'Debug.log') # NEW: Debug Log File Path


    DEFAULT_WINDOW_GEOMETRY = "1400x780+100+100" # This is now a fallback, actual default comes from config

    def __init__(self):
        """
        Function Description:
        Initializes the main application window and sets up core components.
        It performs dependency checks, initializes instrument communication,
        sets up Tkinter variables, loads configuration, creates UI widgets,
        applies styling, and redirects console output. It now also checks
        for the presence of config.ini and enables general debugging if not found,
        displaying relevant status remarks on the GUI console.

        Inputs:
            None.

        Process:
            1. Calls the superclass constructor (tk.Tk).
            2. Sets the window title and protocol for closing.
            3. Initializes `configparser` object and `is_ready_to_save` flag.
            4. Calls `_check_and_install_dependencies` to ensure environment readiness.
            5. Initializes instrument-related attributes (`rm`, `inst`, `instrument_model`).
            6. Initializes data storage lists (`collected_scans_dataframes`, `last_scan_markers`).
            7. Initializes scan control flags and threading events.
            8. Sets up frequency band constants.
            9. Calls `setup_tkinter_variables` to create all Tkinter variables.
            10. Calls `initialize_program_environment` to handle data directory, config, and initial debug setup.
            11. Applies saved window geometry.
            12. Initializes `ttk.Style`.
            13. Calls `_setup_styles` to apply custom themes.
            14. Calls `_create_widgets` to build the GUI.
            15. Checks for config.ini and sets debug mode if not found, displaying status.
            16. Updates connection status.
            17. Prints application art.
            18. Loads band selections for ScanTab (now nested).
            19. Manually updates notes text widget on ScanMetaDataTab (now nested).
            20. Sets `is_ready_to_save` to True.

        Outputs:
            None. Initializes the main application object.
        """
        print(f"Before super().__init__ - Type of self: {type(self)}, ID: {id(self)}") # Diagnostic print
        super().__init__()
        print(f"After super().__init__ - Type of self: {type(self)}, ID: {id(self)}") # Diagnostic print

        print(f"Type of self in App.__init__: {type(self)}") # Diagnostic print
        self.title("OPEN AIR - 🌐🗺️ - Zone Awareness Processor")
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Initialize instance attributes for versioning
        self.current_version = current_version_string
        self.current_version_hash = current_version_hash_value

        # Store original stdout and stderr to restore on close
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

        # Initialize is_ready_to_save to False at the very beginning
        # This prevents AttributeError when Tkinter variable traces are triggered during setup.
        self.is_ready_to_save = False

        # console_text will be initialized in _create_widgets (by ConsoleTab) and a reference stored here
        self.console_text = None

        check_and_install_dependencies(console_logic_module.console_log) # Pass console_log

        self.rm = None
        self.inst = None
        # self.instrument_model is initialized in _setup_tkinter_vars now
        # self.instrument_serial is initialized in _setup_tkinter_vars now
        # self.instrument_firmware is initialized in _setup_tkinter_vars now
        # self.instrument_options is initialized in _setup_tkinter_vars now

        # Initialize is_connected here
        self.is_connected = tk.BooleanVar(value=False) #

        self.collected_scans_dataframes = []
        self.last_scan_markers = []
        # NEW: Add a flag to indicate if scan data is available for plotting/markers
        self.scan_data_available = False


        self.scanning = False
        self.scan_thread = None
        self.stop_scan_event = threading.Event()
        self.pause_scan_event = threading.Event()

        self.SCAN_BAND_RANGES = SCAN_BAND_RANGES
        self.MHZ_TO_HZ = MHZ_TO_HZ
        self.VBW_RBW_RATIO = VBW_RBW_RATIO

        # Parent Tab Colors - These are now defined in src/style.py's COLOR_PALETTE
        # and are no longer needed as a separate attribute here.
        # self.parent_tab_colors = { ... } # Removed as it's handled in style.py


        # Call the new function to set up Tkinter variables
        setup_tkinter_variables(self)

        # Call the new centralized initialization function
        initialize_program_environment(self)

        # Call the new GUI utility functions
        apply_saved_geometry(self)

        self.style = ttk.Style(self)

        # Call the new GUI utility functions
        setup_styles(self)
        self.update_idletasks()
        # Call the new create_widgets function from gui_utils
        create_widgets(self)
        
        # This call remains here as it specifically checks for config.ini existence
        # after load_config has run and potentially saved a new config.
        self._check_config_and_set_debug()
        self.bind("<Configure>", self._on_window_configure)

        display_splash_screen()

        # Schedule initial device refresh and connection status update after GUI is fully set up
        # This ensures mainloop is running when these calls are made
        self.after(100, lambda: self.instrument_parent_tab.instrument_settings_tab._refresh_devices())
        self.after(200, lambda: self.update_connection_status(self.inst is not None, self.scanning))
        self.after(300, lambda: self._on_parent_tab_change(None)) # Initial call to update connection status and ASCII art.


        if hasattr(self, 'scanning_parent_tab') and hasattr(self.scanning_parent_tab, 'scan_configuration_tab'):
            self.scanning_parent_tab.scan_configuration_tab._load_band_selections_from_config()
            debug_logic_module.debug_log(f"Called _load_band_selections_from_config on Scan Configuration Tab during startup.",
                                        file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                                        version=self.current_version,
                                        function=inspect.currentframe().f_code.co_name)
        if hasattr(self, 'scanning_parent_tab') and hasattr(self.scanning_parent_tab, 'scan_meta_data_tab'):
            if hasattr(self.scanning_parent_tab.scan_meta_data_tab, 'notes_text_widget'): # Corrected to notes_text_widget
                self.scanning_parent_tab.scan_meta_data_tab.notes_text_widget.delete("1.0", tk.END)
                self.scanning_parent_tab.scan_meta_data_tab.notes_text_widget.insert(tk.END, self.scan_notes_var.get())
                debug_logic_module.debug_log(f"Updated notes text widget on Scan Meta Data Tab during startup.",
                                            file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                                            version=self.current_version,
                                            function=inspect.currentframe().f_code.co_name)

        # Set is_ready_to_save to True only after all initial setup is complete
        self.is_ready_to_save = True
        debug_logic_module.debug_log(f"Application initialization complete. is_ready_to_save set to True.",
                                    file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                                    version=self.current_version,
                                    function=inspect.currentframe().f_code.co_name)

    def _on_window_configure(self, event):
        """
        Function Description:
        Handles the window's <Configure> event, which fires on size, position, and stacking changes.
        This method is used to save the window's geometry to config.ini.

        Inputs:
            event (tkinter.Event): The event object.

        Process:
            1. Checks if the event is a geometry change (width, height, x, or y changed).
            2. If a change is detected and `is_ready_to_save` is True, it saves the current geometry
                to the config and updates the `last_GLOBAL__window_geometry` setting.

        Outputs:
            None. Persists window geometry.
        """
        current_function = inspect.currentframe().f_code.co_name

        if self.is_ready_to_save and (event.widget == self):
            current_geometry = self.geometry()
            previous_geometry = self.config.get('LAST_USED_SETTINGS', 'last_GLOBAL__window_geometry', fallback="")

            if current_geometry != previous_geometry:
                self.config.set('LAST_USED_SETTINGS', 'last_GLOBAL__window_geometry', current_geometry)
                # Pass console_log from here to save_config
                save_config(self.config, self.CONFIG_FILE_PATH, console_logic_module.console_log, self)
                debug_logic_module.debug_log(f"Window geometry changed and saved: {current_geometry}.",
                            file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                            version=self.current_version,
                            function=current_function)


    def _on_closing(self):
        """
        Function Description:
        Handles the application closing event.
        It attempts to save the current configuration and gracefully
        disconnect from the instrument before destroying the main window.
        It also restores stdout/stderr to their original values.

        Inputs:
            None.

        Outputs:
            None. Performs cleanup and exits.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_logic_module.debug_log(f"Application is shutting down. Saving configuration...",
                    file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                    version=self.current_version,
                    function=current_function)

        if hasattr(self, 'main_panedwindow') and self.main_panedwindow.winfo_exists():
            sash_pos = self.main_panedwindow.sashpos(0)
            self.paned_window_sash_position_var.set(sash_pos)
            debug_logic_module.debug_log(f"Saved final sash position: {sash_pos}.",
                        file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                        version=self.current_version,
                        function=current_function)


        # Pass console_log from here to save_config
        save_config(self.config, self.CONFIG_FILE_PATH, console_logic_module.console_log, self)

        if self.inst:
            debug_logic_module.debug_log(f"Disconnecting instrument before exit.",
                        file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                        version=self.current_version,
                        function=current_function)
            disconnect_instrument_logic(self, console_logic_module.console_log)

        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        print(f"Debug output redirected back to terminal. Application closing. Version: {self.current_version}")

        self.destroy()

    def _on_parent_tab_change(self, event):
        """
        Function Description:
        Handles the event when the parent tab selection changes.
        It updates the styling of the parent tabs to reflect the active tab
        and propagates the `_on_tab_selected` event to the newly selected
        parent tab and its currently visible child tab. It also calls the
        appropriate ASCII art function for the selected parent tab.

        Inputs:
            event (tkinter.Event): The event object, or None if called manually.

        Process:
            1. Retrieves the currently selected parent tab's ID and text.
            2. Calls the appropriate ASCII art function based on the selected tab's text.
            3. Calls `_on_tab_selected` on the newly selected parent tab if the method exists.
            4. If the selected parent tab has a child notebook, it then
               propagates the `_on_tab_selected` event to the active child tab within it.
            5. Logs debug messages throughout the process.

        Outputs:
            None. Updates GUI appearance, triggers tab-specific logic, and displays ASCII art.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_logic_module.debug_log(f"Parent tab changed event triggered. Version: {self.current_version}. Time to update styles and ASCII art!",
                    file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                    version=self.current_version,
                    function=current_function,
                    special=True) # Adding special flag as per your style

        selected_tab_id = self.parent_notebook.select()
        selected_tab_text = self.parent_notebook.tab(selected_tab_id, "text")

        # Call the appropriate ASCII art function based on the selected tab
        if selected_tab_text == "INSTRUMENT":
            _print_inst_ascii(console_logic_module.console_log)
        elif selected_tab_text == "SCANNING":
            _print_scan_ascii(console_logic_module.console_log)
        elif selected_tab_text == "PLOTTING":
            _print_plot_ascii(console_logic_module.console_log)
        elif selected_tab_text == "MARKERS":
            _print_marks_ascii(console_logic_module.console_log)
        elif selected_tab_text == "PRESETS":
            _print_presets_ascii(console_logic_module.console_log)
        elif selected_tab_text == "EXPERIMENTS":
            _print_xxx_ascii(console_logic_module.console_log)
        else:
            debug_logic_module.debug_log(f"No specific ASCII art function found for tab: {selected_tab_text}. What the hell?!",
                        file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                        version=self.current_version,
                        function=current_function)


        # Propagate _on_tab_selected to the selected parent tab
        selected_parent_tab_widget = self.parent_tab_widgets.get(selected_tab_text) # Use self.parent_tab_widgets
        if selected_parent_tab_widget and hasattr(selected_parent_tab_widget, '_on_parent_tab_selected'): # Changed to _on_parent_tab_selected
            selected_parent_tab_widget._on_parent_tab_selected(event) # Call the new parent-specific method
            debug_logic_module.debug_log(f"Propagated _on_parent_tab_selected to active parent tab: {selected_parent_tab_widget.winfo_class()}. Version: {self.current_version}. Looking good!",
                        file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                        version=self.current_version,
                        function=current_function)
        else:
            debug_logic_module.debug_log(f"Active parent tab {selected_parent_tab_text} has no _on_parent_tab_selected method or widget not found. What the hell?! Version: {self.current_version}.",
                        file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                        version=self.current_version,
                        function=current_function)

        # Ensure the currently visible child tab also gets its _on_tab_selected called
        # This needs to be done after the parent tab's _on_tab_selected, as the parent might change its child selection.
        if selected_tab_text in self.child_notebooks:
            child_notebook = self.child_notebooks[selected_tab_text]
            selected_child_tab_id = child_notebook.select()
            if selected_child_tab_id:
                selected_child_tab_widget = child_notebook.nametowidget(selected_child_tab_id)
                if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                    selected_child_tab_widget._on_tab_selected(event)
                    debug_logic_module.debug_log(f"Propagated _on_tab_selected to active child tab {selected_child_tab_widget.winfo_class()} in parent '{selected_tab_text}'. Version: {self.current_version}. All good!",
                                file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                                version=self.current_version,
                                function=current_function)
                else:
                    debug_logic_module.debug_log(f"Active child tab {selected_child_tab_widget.winfo_class()} in parent '{selected_tab_text}' has no _on_tab_selected method.",
                                file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                                version=self.current_version,
                                function=current_function)
            else:
                debug_logic_module.debug_log(f"No child tab selected in parent '{selected_tab_text}'.",
                            file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                            version=self.current_version,
                            function=current_function)
        else:
            debug_logic_module.debug_log(f"No child notebook found for parent tab '{selected_tab_text}'.",
                        file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                        version=self.current_version,
                        function=current_function)

    def update_connection_status(self, is_connected, is_scanning):
        """
        Function Description:
        Updates the connection status displayed in the GUI, specifically
        on the Instrument tab's connection status label. It also updates
        the `is_connected` and `scanning` attributes based on the inputs.

        Inputs:
            is_connected (bool): True if the instrument is connected, False otherwise.
            is_scanning (bool): True if a scan is active, False otherwise.

        Process:
            1. Updates `self.is_connected` BooleanVar.
            2. Updates `self.scanning` boolean flag.
            3. Retrieves the `InstrumentConnectionTab` instance.
            4. Calls `update_status_label` on that tab to refresh the GUI.
            5. Logs the status update.

        Outputs:
            None. Refreshes the connection status display.
        """
        self.is_connected.set(is_connected) # Update the Tkinter BooleanVar
        self.scanning = is_scanning # Update the internal scanning flag

        # Get the InstrumentConnectionTab instance
        instrument_connection_tab = self.instrument_parent_tab.get_child_tab_instance("Connection")
        if instrument_connection_tab:
            instrument_connection_tab.update_status_label(is_connected, is_scanning)
            debug_logic_module.debug_log(f"Connection status updated: Connected={is_connected}, Scanning={is_scanning}",
                                        file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                                        version=self.current_version,
                                        function=inspect.currentframe().f_code.co_name)
        else:
            debug_logic_module.debug_log(f"Could not find InstrumentConnectionTab to update status.",
                                        file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                                        version=self.current_version,
                                        function=inspect.currentframe().f_code.co_name,
                                        Special=True)

    def _check_config_and_set_debug(self):
        """
        Function Description:
        Checks if the config file was found on startup. If not, it enables general
        debugging and displays a remark on the GUI console, guiding the user
        to the debug settings.

        Inputs:
            None.

        Process:
            1. Checks if `self.config_file_exists_on_startup` is False.
            2. If so, sets `self.general_debug_enabled_var` to True.
            3. Displays a message on the GUI console about debug mode being enabled.
            4. Logs the action.

        Outputs:
            None. Adjusts debug settings and informs the user if config was missing.
        """
        # This function is called after config is loaded and debug_logic is set up.
        # The `config_file_exists_on_startup` flag is set in __init__
        # NOTE: config_file_exists_on_startup is now handled within initialize_program_environment
        # This method now primarily serves to inform the user if the config was missing initially.
        if not os.path.exists(self.CONFIG_FILE_PATH):
            self.general_debug_enabled_var.set(True) # Ensure debug is on if config was missing
            console_logic_module.console_log("🚨 config.ini not found! General Debugging has been enabled by default. "
                                              "Please check the 'Debug' section in the 'Settings' tab to adjust debug preferences. 🚨")
            debug_logic_module.debug_log(f"config.ini was not found on startup, general debugging enabled.",
                                        file=f"{os.path.basename(__file__)} - {self.current_version}", # Updated debug file name
                                        version=self.current_version,
                                        function=inspect.currentframe().f_code.co_name)

    def get_tab_instance(self, tab_name):
        """
        Function Description:
        Retrieves an instance of a parent tab based on its name.

        Inputs:
            tab_name (str): The name of the tab (e.g., "Instrument", "Scanning").

        Process:
            1. Uses a dictionary mapping tab names to their instances.
            2. Returns the corresponding tab instance.

        Outputs:
            The instance of the requested tab, or None if not found.
        """
        # Mapping of tab names to their instances
        tab_map = {
            "Instrument": self.instrument_parent_tab,
            "Scanning": self.scanning_parent_tab,
            "Plotting": self.plotting_parent_tab,
            "Markers": self.markers_parent_tab,
            "Presets": self.presets_parent_tab,
            "Experiments": self.experiments_parent_tab,
            "Console": self.console_tab # NEW: Add ConsoleTab to map
        }
        return tab_map.get(tab_name)


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
    app = App()
    app.mainloop()
