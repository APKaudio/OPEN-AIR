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
# Version 20250802.2110.0 (FIXED: TclError: unknown option "-style" by removing incorrect style application in _on_parent_tab_change.)
# Version 20250802.2246.0 (Fixed TypeError: apply_styles() takes 3 positional arguments but 4 were given by removing parent_tab_colors argument.)
# Version 20250803.0144.1 (Added ASCII art display to _on_parent_tab_change for each parent tab selection.)

current_version = "20250803.0144.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 144 * 1 # Example hash, adjust as needed


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
from src.style import apply_styles
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
            9. Calls `_setup_tkinter_vars` to create all Tkinter variables.
            10. Calls `load_config` to populate variables from `config.ini`.
            11. Applies saved window geometry.
            12. Initializes `ttk.Style`.
            13. Calls `_ensure_data_directory_exists` to create the DATA folder.
            14. Calls `_setup_styles` to apply custom themes.
            15. Calls `_create_widgets` to build the GUI.
            16. **NEW: Checks for config.ini and sets debug mode if not found, displaying status.**
            17. Updates connection status.
            18. Prints application art.
            19. Loads band selections for ScanTab (now nested).
            20. Manually updates notes text widget on ScanMetaDataTab (now nested).
            21. Sets `is_ready_to_save` to True.

        Outputs:
            None. Initializes the main application object.
        """
        super().__init__()
        self.title("OPEN AIR - 🌐🗺️ - Zone Awareness Processor")
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

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
        # PARENT_INSTRUMENT_ACTIVE = "#FF0000"
        # PARENT_INSTRUMENT_INACTIVE = "#660C0C"
        # PARENT_SCANNING_ACTIVE = "#FF6600"
        # PARENT_SCANNING_INACTIVE = "#926002"
        # PARENT_PLOTTING_ACTIVE = "#D1D10E"
        # PARENT_PLOTTING_INACTIVE = "#72720A"
        # PARENT_MARKERS_ACTIVE = "#319131"
        # PARENT_MARKERS_INACTIVE = "#1B4B1B"
        # PARENT_PRESETS_ACTIVE = "#0303C9"
        # PARENT_PRESETS_INACTIVE = "#00008B"
        # ACCENT_PURPLE = "#6f42c1"
        # PARENT_EXPERIMENTS_ACTIVE = ACCENT_PURPLE
        # PARENT_EXPERIMENTS_INACTIVE = "#4d2482"

        # Store parent tab color mappings for dynamic updates - This will now be accessed via COLOR_PALETTE['parent_tabs']
        # self.parent_tab_colors = {
        #     "INSTRUMENT": {"active": PARENT_INSTRUMENT_ACTIVE, "inactive": PARENT_INSTRUMENT_INACTIVE, "fg_active": "white", "fg_inactive": "#cccccc"},
        #     "SCANNING": {"active": PARENT_SCANNING_ACTIVE, "inactive": PARENT_SCANNING_INACTIVE, "fg_active": "white", "fg_inactive": "#cccccc"},
        #     "PLOTTING": {"active": PARENT_PLOTTING_ACTIVE, "inactive": PARENT_PLOTTING_INACTIVE, "fg_active": "black", "fg_inactive": "#cccccc"},
        #     "MARKERS": {"active": PARENT_MARKERS_ACTIVE, "inactive": PARENT_MARKERS_INACTIVE, "fg_active": "black", "fg_inactive": "#cccccc"},
        #     "PRESETS": {"active": PARENT_PRESETS_ACTIVE, "inactive": PARENT_PRESETS_INACTIVE, "fg_active": "white", "fg_inactive": "#cccccc"},
        #     "EXPERIMENTS": {"active": PARENT_EXPERIMENTS_ACTIVE, "inactive": PARENT_EXPERIMENTS_INACTIVE, "fg_active": "white", "fg_inactive": "#cccccc"},
        # }


        self._setup_tkinter_vars()

        self._ensure_data_directory_exists()

        config_file_exists_on_startup = os.path.exists(self.CONFIG_FILE_PATH)

        self.config = configparser.ConfigParser()
        # Pass console_log from here to load_config
        load_config(self.config, self.CONFIG_FILE_PATH, console_logic_module.console_log, self)

        if not config_file_exists_on_startup:
            debug_logic_module.debug_log(f"config.ini was not found on startup. Saving defaults to new file.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=inspect.currentframe().f_code.co_name)
            # Pass console_log from here to save_config
            save_config(self.config, self.CONFIG_FILE_PATH, console_logic_module.console_log, self)


        self._apply_saved_geometry()

        self.style = ttk.Style(self)

        # Initialize logging setup early, AFTER config is loaded but BEFORE _create_widgets()
        # This is CRUCIAL for breaking the circular dependency and ensuring logging works from the start.

        # Register console_log function with debug_logic
        debug_logic_module.set_console_log_func(console_logic_module.console_log)

        # Register debug file hooks from debug_logic with console_logic
        # Pass callables (lambdas) to get the current state of the flag and the write function
        console_logic_module.set_debug_file_hooks(
            lambda: debug_logic_module.INCLUDE_CONSOLE_MESSAGES_TO_DEBUG_FILE,
            debug_logic_module._write_to_debug_file
        )

        # Set debug modes based on loaded config. These are called here to ensure logging is configured early.
        debug_logic_module.set_debug_mode(self.general_debug_enabled_var.get())
        debug_logic_module.set_log_visa_commands_mode(self.log_visa_commands_enabled_var.get())
        debug_logic_module.set_debug_to_terminal_mode(self.debug_to_terminal_var.get())
        debug_logic_module.set_debug_to_file_mode(self.debug_to_file_var.get(), self.DEBUG_COMMANDS_FILE_PATH)
        debug_logic_module.set_include_console_messages_to_debug_file_mode(self.include_console_messages_to_debug_file_var.get())
        debug_logic_module.set_debug_to_gui_console_mode(self.debug_to_gui_console_var.get()) # NEW: Set new debug mode


        self._setup_styles()
        self.update_idletasks()

        self._create_widgets() # console_text is initialized here (within ConsoleTab)

        # The console redirector is now set within ConsoleTab's __init__
        # via set_gui_console_redirector. No need to call it here explicitly.
        # The _redirect_stdout_to_console function is also removed as it's no longer needed.


        self._check_config_and_set_debug()

        self.bind("<Configure>", self._on_window_configure)

        self._on_parent_tab_change(None)

        # Initial call to update connection status.
        # This will now correctly use the new get_tab_instance method.
        self.update_connection_status(self.inst is not None, self.scanning)

        display_splash_screen()

        if hasattr(self, 'scanning_parent_tab') and hasattr(self.scanning_parent_tab, 'scan_configuration_tab'):
            self.scanning_parent_tab.scan_configuration_tab._load_band_selections_from_config()
            debug_logic_module.debug_log(f"Called _load_band_selections_from_config on Scan Configuration Tab during startup.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=inspect.currentframe().f_code.co_name)

        if hasattr(self, 'scanning_parent_tab') and hasattr(self.scanning_parent_tab, 'scan_meta_data_tab'):
            if hasattr(self.scanning_parent_tab.scan_meta_data_tab, 'notes_text_widget'): # Corrected to notes_text_widget
                self.scanning_parent_tab.scan_meta_data_tab.notes_text_widget.delete("1.0", tk.END) # Corrected to notes_text_widget
                self.scanning_parent_tab.scan_meta_data_tab.notes_text_widget.insert("1.0", self.notes_var.get()) # Corrected to notes_text_widget
                debug_logic_module.debug_log(f"Updated notes_text_widget on Scan Meta Data Tab during startup.", # Corrected to notes_text_widget
                            file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                            version=current_version,
                            function=inspect.currentframe().f_code.co_name)
            else:
                debug_logic_module.debug_log(f"ScanMetaDataTab notes_text_widget not found for initial notes update.", # Corrected to notes_text_widget
                            file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                            version=current_version,
                            function=inspect.currentframe().f_code.co_name)
        else:
            debug_logic_module.debug_log(f"ScanMetaDataTab not found for initial notes update.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=inspect.currentframe().f_code.co_name)


        self.is_ready_to_save = True
        debug_logic_module.debug_log(f"Application fully initialized and ready to save configuration.",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

    def _check_config_and_set_debug(self):
        """
        Function Description:
        Checks for the presence of the config.ini file in the DATA_FOLDER_PATH.
        If config.ini is not found, it automatically enables general debugging
        and updates the GUI console with status remarks.

        Inputs:
            None.

        Process:
            1. Logs the start of the configuration check to the debug console.
            2. Checks if self.CONFIG_FILE_PATH exists.
            3. If it does not exist:
                a. Prints a warning to the GUI console and debug log.
                b. Sets the general_debug_enabled_var to True.
                c. Calls set_debug_mode to activate debugging.
            4. If it exists:
                a. Prints a success message to the GUI console and debug log.
            5. Displays the current general debug mode status to the GUI console and debug log.

        Outputs:
            Returns True if config.ini was found, False otherwise.
            Modifies application state (debug mode) and updates GUI console.
        """
        current_function = inspect.currentframe().f_code.co_name

        console_logic_module.console_log(f"--- Configuration & Debug Status ({current_version}) ---", function=current_function)
        debug_logic_module.debug_log(f"Checking for config.ini at: {self.CONFIG_FILE_PATH}.",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)

        config_file_found = os.path.exists(self.CONFIG_FILE_PATH)

        if not config_file_found:
            console_logic_module.console_log(f"❌ config.ini not found at '{self.CONFIG_FILE_PATH}'.", function=current_function)
            console_logic_module.console_log(f"⚠️ General debugging enabled automatically. Let's see what the fuck is going on!", function=current_function)
            self.general_debug_enabled_var.set(True)
            debug_logic_module.set_debug_mode(True) # Ensure the actual debug mode is set
            debug_logic_module.debug_log(f"config.ini not found. General debugging enabled.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
        else:
            console_logic_module.console_log(f"✅ config.ini found at '{self.CONFIG_FILE_PATH}'.", function=current_function)
            debug_logic_module.debug_log(f"config.ini found.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)

        # Display current debug status (regardless of config.ini presence)
        if self.general_debug_enabled_var.get():
            console_logic_module.console_log(f"🐞 Current General Debug Mode: ENABLED", function=current_function)
            debug_logic_module.debug_log(f"Current General Debug Mode: ENABLED",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
        else:
            console_logic_module.console_log(f"🐞 Current General Debug Mode: DISABLED", function=current_function)
            debug_logic_module.debug_log(f"Current General Debug Mode: DISABLED",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
        
        # NEW: Display Debug to GUI Console Mode status
        if self.debug_to_gui_console_var.get():
            console_logic_module.console_log(f"🐞 Current Debug to GUI Console Mode: ENABLED", function=current_function)
            debug_logic_module.debug_log(f"Current Debug to GUI Console Mode: ENABLED",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
        else:
            console_logic_module.console_log(f"🐞 Current Debug to GUI Console Mode: DISABLED", function=current_function)
            debug_logic_module.debug_log(f"Current Debug to GUI Console Mode: DISABLED",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
        
        console_logic_module.console_log(f"--------------------------------------------------", function=current_function)

        return config_file_found


    def _ensure_data_directory_exists(self):
        """
        Function Description:
        Ensures that the 'DATA' directory exists at the specified `self.DATA_FOLDER_PATH`.
        If the directory does not exist, it attempts to create it. This is crucial
        for storing configuration files, scan data, and other application-related files.

        Inputs to this function:
            None (operates on self.DATA_FOLDER_PATH).

        Process of this function:
            1. Prints a debug message indicating the attempt to create the directory.
            2. Uses `os.makedirs` with `exist_ok=True` to create the directory.
                `exist_ok=True` prevents an error if the directory already exists (e.g., due to a race condition).
            3. Prints informative messages to the console about the directory status.
            4. Includes error handling for potential issues during directory creation.

        Outputs of this function:
            None. Ensures the 'DATA' directory is available for file operations.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_logic_module.debug_log(f"Ensuring DATA directory exists at: {self.DATA_FOLDER_PATH}.",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)
        try:
            os.makedirs(self.DATA_FOLDER_PATH, exist_ok=True)
            console_logic_module.console_log(f"✅ DATA directory ensured at: {self.DATA_FOLDER_PATH}", function=current_function)
            debug_logic_module.debug_log(f"DATA directory created or already exists.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
        except Exception as e:
            console_logic_module.console_log(f"❌ Error creating DATA directory at {self.DATA_FOLDER_PATH}: {e}. This is a real clusterfuck!", function=current_function)
            debug_logic_module.debug_log(f"ERROR: Error creating DATA directory: {e}",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
            raise

    def _setup_tkinter_vars(self):
        """
        Function Description:
        Initializes all Tkinter `StringVar`, `BooleanVar`, and `DoubleVar` instances
        used throughout the application. These variables are linked to GUI widgets
        and configuration settings.

        Inputs:
            None.

        Process:
            1. Initializes StringVars for VISA resource names, selected resource,
                instrument model, and various scan settings (frequency, RBW, Ref Level, etc.).
            2. Initializes BooleanVars for debug modes, HTML output options, and marker inclusions.
            3. Initializes DoubleVars for VBW/RBW ratio and sweep time.
            4. Initializes IntegerVars for sweep points and average count.

        Outputs:
            None. Populates `self` with Tkinter variable objects.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_logic_module.debug_log("Setting up Tkinter variables...",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)

        # Define a helper function to add trace for saving config
        def create_trace_callback(var_name):
            def callback(*args):
                if self.is_ready_to_save:
                    debug_logic_module.debug_log(f"Tkinter variable '{var_name}' changed. Saving config.",
                                file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                                version=current_version,
                                function=inspect.currentframe().f_code.co_name)
                    # Pass console_log from here to save_config
                    save_config(self.config, self.CONFIG_FILE_PATH, console_logic_module.console_log, self)
            return callback

        # GLOBAL variables
        self.general_debug_enabled_var = tk.BooleanVar(self, value=False)
        self.general_debug_enabled_var.trace_add("write", create_trace_callback("general_debug_enabled_var"))

        self.log_visa_commands_enabled_var = tk.BooleanVar(self, value=False)
        self.log_visa_commands_enabled_var.trace_add("write", create_trace_callback("log_visa_commands_enabled_var"))

        self.debug_to_terminal_var = tk.BooleanVar(self, value=False)
        self.debug_to_terminal_var.trace_add("write", create_trace_callback("debug_to_terminal_var"))

        self.debug_to_file_var = tk.BooleanVar(self, value=False)
        self.debug_to_file_var.trace_add("write", create_trace_callback("debug_to_file_var"))

        self.include_console_messages_to_debug_file_var = tk.BooleanVar(self, value=False)
        self.include_console_messages_to_debug_file_var.trace_add("write", create_trace_callback("include_console_messages_to_debug_file_var"))

        self.debug_to_gui_console_var = tk.BooleanVar(self, value=False) # NEW: Initialized here
        self.debug_to_gui_console_var.trace_add("write", create_trace_callback("debug_to_gui_console_var"))

        self.paned_window_sash_position_var = tk.IntVar(self, value=700)
        self.paned_window_sash_position_var.trace_add("write", create_trace_callback("paned_window_sash_position_var"))

        # NEW: Variable to hold the last config save time
        self.last_config_save_time_var = tk.StringVar(self, value="Last Saved: Never")
        # No trace needed for this variable as it's updated programmatically


        # Instrument Connection variables
        self.selected_resource = tk.StringVar(self)
        self.selected_resource.trace_add("write", create_trace_callback("selected_resource"))

        self.available_resources = tk.StringVar(self) # Added initialization for available_resources
        self.available_resources.trace_add("write", create_trace_callback("available_resources")) # Add trace if needed

        self.resource_names = tk.StringVar(self) # This was already here, keep it.

        # (2025-08-02 13:59) Change: Initialize instrument info variables
        self.instrument_model = tk.StringVar(self, value="N/A")
        self.instrument_model.trace_add("write", create_trace_callback("instrument_model"))

        self.instrument_serial = tk.StringVar(self, value="N/A")
        self.instrument_serial.trace_add("write", create_trace_callback("instrument_serial"))

        self.instrument_firmware = tk.StringVar(self, value="N/A")
        self.instrument_firmware.trace_add("write", create_trace_callback("instrument_firmware"))

        self.instrument_options = tk.StringVar(self, value="N/A")
        self.instrument_options.trace_add("write", create_trace_callback("instrument_options"))


        # Instrument settings variables (used by instrument_logic.py)
        # (2025-08-02 14:38) Change: Moved initialization of instrument settings variables BEFORE setting_var_map
        self.center_freq_hz_var = tk.DoubleVar(self, value=2400000000.0)
        self.center_freq_hz_var.trace_add("write", create_trace_callback("center_freq_hz_var"))

        self.span_hz_var = tk.DoubleVar(self, value=100000000.0)
        self.span_hz_var.trace_add("write", create_trace_callback("span_hz_var"))

        self.rbw_hz_var = tk.DoubleVar(self, value=10000.0)
        self.rbw_hz_var.trace_add("write", create_trace_callback("rbw_hz_var"))

        self.vbw_hz_var = tk.DoubleVar(self, value=3000.0)
        self.vbw_hz_var.trace_add("write", create_trace_callback("vbw_hz_var"))

        self.sweep_time_s_var = tk.DoubleVar(self, value=0.01) # Added missing sweep_time_s_var
        self.sweep_time_s_var.trace_add("write", create_trace_callback("sweep_time_s_var"))


        # Scan Configuration variables
        self.scan_name_var = tk.StringVar(self, value="ThisIsMyScan")
        self.scan_name_var.trace_add("write", create_trace_callback("scan_name_var"))

        self.output_folder_var = tk.StringVar(self, value=self.DATA_FOLDER_PATH)
        self.output_folder_var.trace_add("write", create_trace_callback("output_folder_var"))

        # Initialize with 'value' key from the standardized lists
        self.num_scan_cycles_var = tk.IntVar(self, value=number_of_scans_presets[0]["value"])
        self.num_scan_cycles_var.trace_add("write", create_trace_callback("num_scan_cycles_var"))

        self.rbw_step_size_hz_var = tk.StringVar(self, value=str(graph_quality_drop_down[0]["value"]))
        self.rbw_step_size_hz_var.trace_add("write", create_trace_callback("rbw_step_size_hz_var"))

        self.cycle_wait_time_seconds_var = tk.StringVar(self, value=str(cycle_wait_time_presets[0]["value"]))
        self.cycle_wait_time_seconds_var.trace_add("write", create_trace_callback("cycle_wait_time_seconds_var"))

        self.maxhold_time_seconds_var = tk.StringVar(self, value=str(dwell_time_drop_down[0]["value"]))
        self.maxhold_time_seconds_var.trace_add("write", create_trace_callback("maxhold_time_seconds_var"))

        self.scan_rbw_hz_var = tk.StringVar(self, value=str(rbw_presets[0]["value"]))
        self.scan_rbw_hz_var.trace_add("write", create_trace_callback("scan_rbw_hz_var"))

        self.reference_level_dbm_var = tk.StringVar(self, value=str(reference_level_drop_down[0]["value"]))
        self.reference_level_dbm_var.trace_add("write", create_trace_callback("reference_level_dbm_var"))

        self.attenuation_var = tk.StringVar(self, value=str(attenuation_levels[0]["value"])) # Corrected to 'value'
        self.attenuation_var.trace_add("write", create_trace_callback("attenuation_var"))

        self.freq_shift_var = tk.StringVar(self, value=str(frequency_shift_presets[0]["value"])) # Corrected to 'value'
        self.freq_shift_var.trace_add("write", create_trace_callback("freq_shift_var"))

        self.scan_mode_var = tk.StringVar(self, value=scan_modes[0]["value"]) # Corrected to 'value'
        self.scan_mode_var.trace_add("write", create_trace_callback("scan_mode_var"))

        self.maxhold_enabled_var = tk.BooleanVar(self, value=True)
        self.maxhold_enabled_var.trace_add("write", create_trace_callback("maxhold_enabled_var"))

        self.high_sensitivity_var = tk.BooleanVar(self, value=True)
        self.high_sensitivity_var.trace_add("write", create_trace_callback("high_sensitivity_var"))

        self.preamp_on_var = tk.BooleanVar(self, value=True)
        self.preamp_on_var.trace_add("write", create_trace_callback("preamp_on_var"))

        self.scan_rbw_segmentation_var = tk.StringVar(self, value="1000000.0")
        self.scan_rbw_segmentation_var.trace_add("write", create_trace_callback("scan_rbw_segmentation_var"))

        self.desired_default_focus_width_var = tk.StringVar(self, value=str(graph_quality_drop_down[0]["value"]))
        self.desired_default_focus_width_var.trace_add("write", create_trace_callback("desired_default_focus_width_var"))


        # Scan Meta Data variables
        self.operator_name_var = tk.StringVar(self, value="Anthony Peter Kuzub")
        self.operator_name_var.trace_add("write", create_trace_callback("operator_name_var"))

        self.operator_contact_var = tk.StringVar(self, value="I@Like.audio")
        self.operator_contact_var.trace_add("write", create_trace_callback("operator_contact_var"))

        self.venue_name_var = tk.StringVar(self, value="Garage")
        self.venue_name_var.trace_add("write", create_trace_callback("venue_name_var"))

        self.venue_postal_code_var = tk.StringVar(self, value="")
        self.venue_postal_code_var.trace_add("write", create_trace_callback("venue_postal_code_var"))

        self.address_field_var = tk.StringVar(self, value="")
        self.address_field_var.trace_add("write", create_trace_callback("address_field_var"))

        self.city_var = tk.StringVar(self, value="Whitby")
        self.city_var.trace_add("write", create_trace_callback("city_var"))

        self.province_var = tk.StringVar(self, value="")
        self.province_var.trace_add("write", create_trace_callback("province_var"))

        self.scanner_type_var = tk.StringVar(self, value="Unknown")
        self.scanner_type_var.trace_add("write", create_trace_callback("scanner_type_var"))

        self.selected_antenna_type_var = tk.StringVar(self, value="")
        self.selected_antenna_type_var.trace_add("write", create_trace_callback("selected_antenna_type_var"))

        self.antenna_description_var = tk.StringVar(self, value="")
        self.antenna_description_var.trace_add("write", create_trace_callback("antenna_description_var"))

        self.antenna_use_var = tk.StringVar(self, value="")
        self.antenna_use_var.trace_add("write", create_trace_callback("antenna_use_var"))

        self.antenna_mount_var = tk.StringVar(self, value="")
        self.antenna_mount_var.trace_add("write", create_trace_callback("antenna_mount_var"))

        self.selected_amplifier_type_var = tk.StringVar(self, value="")
        self.selected_amplifier_type_var.trace_add("write", create_trace_callback("selected_amplifier_type_var"))

        self.antenna_amplifier_var = tk.StringVar(self, value="Ground Plane")
        self.antenna_amplifier_var.trace_add("write", create_trace_callback("antenna_amplifier_var"))

        self.amplifier_description_var = tk.StringVar(self, value="")
        self.amplifier_description_var.trace_add("write", create_trace_callback("amplifier_description_var"))

        self.amplifier_use_var = tk.StringVar(self, value="")
        self.amplifier_use_var.trace_add("write", create_trace_callback("amplifier_use_var"))

        self.notes_var = tk.StringVar(self, value="")

        self.last_selected_preset_name_var = tk.StringVar(self, value="")
        self.last_selected_preset_name_var.trace_add("write", create_trace_callback("last_selected_preset_name_var"))

        self.last_loaded_preset_center_freq_mhz_var = tk.StringVar(self, value="")
        self.last_loaded_preset_center_freq_mhz_var.trace_add("write", create_trace_callback("last_loaded_preset_center_freq_mhz_var"))

        self.last_loaded_preset_span_mhz_var = tk.StringVar(self, value="")
        self.last_loaded_preset_span_mhz_var.trace_add("write", create_trace_callback("last_loaded_preset_span_mhz_var"))

        self.last_loaded_preset_rbw_hz_var = tk.StringVar(self, value="")
        self.last_loaded_preset_rbw_hz_var.trace_add("write", create_trace_callback("last_loaded_preset_rbw_hz_var"))


        # Plotting variables (Scan Markers)
        self.include_gov_markers_var = tk.BooleanVar(self, value=True)
        self.include_gov_markers_var.trace_add("write", create_trace_callback("include_gov_markers_var"))

        self.include_tv_markers_var = tk.BooleanVar(self, value=True)
        self.include_tv_markers_var.trace_add("write", create_trace_callback("include_tv_markers_var"))

        self.include_markers_var = tk.BooleanVar(self, value=True)
        self.include_markers_var.trace_add("write", create_trace_callback("include_markers_var"))

        self.include_scan_intermod_markers_var = tk.BooleanVar(self, value=False)
        self.include_scan_intermod_markers_var.trace_add("write", create_trace_callback("include_scan_intermod_markers_var"))

        self.open_html_after_complete_var = tk.BooleanVar(self, value=True)
        self.open_html_after_complete_var.trace_add("write", create_trace_callback("open_html_after_complete_var"))

        self.create_html_var = tk.BooleanVar(self, value=True)
        self.create_html_var.trace_add("write", create_trace_callback("create_html_var"))

        # Plotting variables (Average Markers)
        self.avg_include_gov_markers_var = tk.BooleanVar(self, value=True)
        self.avg_include_gov_markers_var.trace_add("write", create_trace_callback("avg_include_gov_markers_var"))

        self.avg_include_tv_markers_var = tk.BooleanVar(self, value=True)
        self.avg_include_tv_markers_var.trace_add("write", create_trace_callback("avg_include_tv_markers_var"))

        self.avg_include_markers_var = tk.BooleanVar(self, value=True)
        self.avg_include_markers_var.trace_add("write", create_trace_callback("avg_include_markers_var"))

        self.avg_include_intermod_markers_var = tk.BooleanVar(self, value=False)
        self.avg_include_intermod_markers_var.trace_add("write", create_trace_callback("avg_include_intermod_markers_var"))

        self.math_average_var = tk.BooleanVar(self, value=True)
        self.math_average_var.trace_add("write", create_trace_callback("math_average_var"))

        self.math_median_var = tk.BooleanVar(self, value=True)
        self.math_median_var.trace_add("write", create_trace_callback("math_median_var"))

        self.math_range_var = tk.BooleanVar(self, value=True)
        self.math_range_var.trace_add("write", create_trace_callback("math_range_var"))

        self.math_standard_deviation_var = tk.BooleanVar(self, value=True)
        self.math_standard_deviation_var.trace_add("write", create_trace_callback("math_standard_deviation_var"))

        self.math_variance_var = tk.BooleanVar(self, value=True)
        self.math_variance_var.trace_add("write", create_trace_callback("math_variance_var"))

        self.math_psd_var = tk.BooleanVar(self, value=True)
        self.math_psd_var.trace_add("write", create_trace_callback("math_psd_var"))


        # Map Tkinter variables to config.ini keys using the new prefixed style
        self.setting_var_map = {
            'general_debug_enabled_var': ('last_GLOBAL__debug_enabled', 'default_GLOBAL__debug_enabled', self.general_debug_enabled_var),
            'log_visa_commands_enabled_var': ('last_GLOBAL__log_visa_commands_enabled', 'default_GLOBAL__log_visa_commands_enabled', self.log_visa_commands_enabled_var),
            'debug_to_terminal_var': ('last_GLOBAL__debug_to_Terminal', 'default_GLOBAL__debug_to_Terminal', self.debug_to_terminal_var),
            'debug_to_file_var': ('last_GLOBAL__debug_to_File', 'default_GLOBAL__debug_to_File', self.debug_to_file_var),
            'include_console_messages_to_debug_file_var': ('last_GLOBAL__include_console_messages_to_debug_file', 'default_GLOBAL__include_console_messages_to_debug_file', self.include_console_messages_to_debug_file_var),
            'debug_to_gui_console_var': ('last_GLOBAL__debug_to_GUI_Console', 'default_GLOBAL__debug_to_GUI_Console', self.debug_to_gui_console_var), # NEW MAPPING
            'paned_window_sash_position_var': ('last_GLOBAL__paned_window_sash_position', 'default_GLOBAL__paned_window_sash_position', self.paned_window_sash_position_var),
            'last_config_save_time_var': ('last_GLOBAL__last_config_save_time', 'default_GLOBAL__last_config_save_time', self.last_config_save_time_var), # NEW MAPPING
            'selected_resource': ('last_instrument_connection__visa_resource', 'default_instrument_connection__visa_resource', self.selected_resource),
            'available_resources': ('last_instrument_connection__available_resources', 'default_instrument_connection__available_resources', self.available_resources), # NEW MAPPING

            'instrument_model': ('last_instrument_info__model', 'default_instrument_info__model', self.instrument_model), # NEW MAPPING
            'instrument_serial': ('last_instrument_info__serial', 'default_instrument_info__serial', self.instrument_serial), # NEW MAPPING
            'instrument_firmware': ('last_instrument_info__firmware', 'default_instrument_info__firmware', self.instrument_firmware), # NEW MAPPING
            'instrument_options': ('last_instrument_info__options', 'default_instrument_info__options', self.instrument_options), # NEW MAPPING


            'center_freq_hz_var': ('last_instrument_settings__center_freq_hz', 'default_instrument_settings__center_freq_hz', self.center_freq_hz_var),
            'span_hz_var': ('last_instrument_settings__span_hz', 'default_instrument_settings__span_hz', self.span_hz_var),
            'rbw_hz_var': ('last_instrument_settings__rbw_hz', 'default_instrument_settings__rbw_hz', self.rbw_hz_var),
            'vbw_hz_var': ('last_instrument_settings__vbw_hz', 'default_instrument_settings__vbw_hz', self.vbw_hz_var),
            'sweep_time_s_var': ('last_instrument_settings__sweep_time_s', 'default_instrument_settings__sweep_time_s', self.sweep_time_s_var), # Added missing sweep_time_s_var

            'scan_name_var': ('last_scan_configuration__scan_name', 'default_scan_configuration__scan_name', self.scan_name_var),
            'output_folder_var': ('last_scan_configuration__scan_directory', 'default_scan_configuration__scan_directory', self.output_folder_var),
            'num_scan_cycles_var': ('last_scan_configuration__num_scan_cycles', 'default_scan_configuration__num_scan_cycles', self.num_scan_cycles_var),
            'rbw_step_size_hz_var': ('last_scan_configuration__rbw_step_size_hz', 'default_scan_configuration__rbw_step_size_hz', self.rbw_step_size_hz_var),
            'cycle_wait_time_seconds_var': ('last_scan_configuration__cycle_wait_time_seconds', 'default_scan_configuration__cycle_wait_time_seconds', self.cycle_wait_time_seconds_var),
            'maxhold_time_seconds_var': ('last_scan_configuration__maxhold_time_seconds', 'default_scan_configuration__maxhold_time_seconds', self.maxhold_time_seconds_var),
            'scan_rbw_hz_var': ('last_scan_configuration__scan_rbw_hz', 'default_scan_configuration__scan_rbw_hz', self.scan_rbw_hz_var),
            'reference_level_dbm_var': ('last_scan_configuration__reference_level_dbm', 'default_scan_configuration__reference_level_dbm', self.reference_level_dbm_var),
            'attenuation_var': ('last_scan_configuration__attenuation', 'default_scan_configuration__attenuation', self.attenuation_var), # NEW MAPPING
            'freq_shift_var': ('last_scan_configuration__freq_shift_hz', 'default_scan_configuration__freq_shift_hz', self.freq_shift_var), # NEW MAPPING
            'scan_mode_var': ('last_scan_configuration__scan_mode', 'default_scan_configuration__scan_mode', self.scan_mode_var), # NEW MAPPING
            'maxhold_enabled_var': ('last_scan_configuration__maxhold_enabled', 'default_scan_configuration__maxhold_enabled', self.maxhold_enabled_var),
            'high_sensitivity_var': ('last_scan_configuration__sensitivity', 'default_scan_configuration__sensitivity', self.high_sensitivity_var),
            'preamp_on_var': ('last_scan_configuration__preamp_on', 'default_scan_configuration__preamp_on', self.preamp_on_var),
            'scan_rbw_segmentation_var': ('last_scan_configuration__scan_rbw_segmentation', 'default_scan_configuration__scan_rbw_segmentation', self.scan_rbw_segmentation_var),
            'desired_default_focus_width_var': ('last_scan_configuration__default_focus_width', 'default_scan_configuration__default_focus_width', self.desired_default_focus_width_var),


            'operator_name_var': ('last_scan_meta_data__operator_name', 'default_scan_meta_data__operator_name', self.operator_name_var),
            'operator_contact_var': ('last_scan_meta_data__contact', 'default_scan_meta_data__contact', self.operator_contact_var),
            'venue_name_var': ('last_scan_meta_data__name', 'default_scan_meta_data__name', self.venue_name_var),

            'venue_postal_code_var': ('last_scan_meta_data__venue_postal_code', 'default_scan_meta_data__venue_postal_code', self.venue_postal_code_var),
            'address_field_var': ('last_scan_meta_data__address_field', 'default_scan_meta_data__address_field', self.address_field_var),
            'city_var': ('last_scan_meta_data__city', 'default_scan_meta_data__city', self.city_var),
            'province_var': ('last_scan_meta_data__province', 'default_scan_meta_data__province', self.province_var),
            'scanner_type_var': ('last_scan_meta_data__scanner_type', 'default_scan_meta_data__scanner_type', self.scanner_type_var),

            'selected_antenna_type_var': ('last_scan_meta_data__selected_antenna_type', 'default_scan_meta_data__selected_antenna_type', self.selected_antenna_type_var),
            'antenna_description_var': ('last_scan_meta_data__antenna_description', 'default_scan_meta_data__antenna_description', self.antenna_description_var),
            'antenna_use_var': ('last_scan_meta_data__antenna_use', 'default_scan_meta_data__antenna_use', self.antenna_use_var),
            'antenna_mount_var': ('last_scan_meta_data__antenna_mount', 'default_scan_meta_data__antenna_mount', self.antenna_mount_var),
            'selected_amplifier_type_var': ('last_scan_meta_data__selected_amplifier_type', 'default_scan_meta_data__selected_amplifier_type', self.selected_amplifier_type_var),
            'antenna_amplifier_var': ('last_scan_meta_data__antenna_amplifier', 'default_scan_meta_data__antenna_amplifier', self.antenna_amplifier_var),
            'amplifier_description_var': ('last_scan_meta_data__amplifier_description', 'default_scan_meta_data__amplifier_description', self.amplifier_description_var),
            'amplifier_use_var': ('last_scan_meta_data__amplifier_use', 'default_scan_meta_data__amplifier_use', self.amplifier_use_var),

            'notes_var': ('last_scan_meta_data__notes', 'default_scan_meta_data__notes', self.notes_var),

            'last_selected_preset_name_var': ('last_instrument_preset__selected_preset_name', 'default_instrument_preset__selected_preset_name', self.last_selected_preset_name_var),
            'last_loaded_preset_center_freq_mhz_var': ('last_instrument_preset__loaded_preset_center_freq_mhz', 'default_instrument_preset__loaded_preset_center_freq_mhz', self.last_loaded_preset_center_freq_mhz_var),
            'last_loaded_preset_span_mhz_var': ('last_instrument_preset__loaded_preset_span_mhz', 'default_instrument_preset__loaded_preset_span_mhz', self.last_loaded_preset_span_mhz_var),
            'last_loaded_preset_rbw_hz_var': ('last_instrument_preset__loaded_preset_rbw_hz', 'default_instrument_preset__loaded_preset_rbw_hz', self.last_loaded_preset_rbw_hz_var),


            'include_gov_markers_var': ('last_plotting__scan_markers_to_plot__include_gov_markers', 'default_plotting__scan_markers_to_plot__include_gov_markers', self.include_gov_markers_var),
            'include_tv_markers_var': ('last_plotting__scan_markers_to_plot__include_tv_markers', 'default_plotting__scan_markers_to_plot__include_tv_markers', self.include_tv_markers_var),
            'include_markers_var': ('last_plotting__scan_markers_to_plot__include_markers', 'default_plotting__scan_markers_to_plot__include_markers', self.include_markers_var),
            'include_scan_intermod_markers_var': ('last_plotting__scan_markers_to_plot__include_intermod_markers', 'default_plotting__scan_markers_to_plot__include_intermod_markers', self.include_scan_intermod_markers_var),
            'open_html_after_complete_var': ('last_plotting__scan_markers_to_plot__open_html_after_complete', 'default_plotting__scan_markers_to_plot__open_html_after_complete', self.open_html_after_complete_var),
            'create_html_var': ('last_plotting__scan_markers_to_plot__create_html', 'default_plotting__scan_markers_to_plot__create_html', self.create_html_var),

            'avg_include_gov_markers_var': ('last_plotting__average_markers_to_plot__include_gov_markers', 'default_plotting__average_markers_to_plot__include_gov_markers', self.avg_include_gov_markers_var),
            'avg_include_tv_markers_var': ('last_plotting__average_markers_to_plot__include_tv_markers', 'default_plotting__average_markers_to_plot__include_tv_markers', self.avg_include_tv_markers_var),
            'avg_include_markers_var': ('last_plotting__average_markers_to_plot__include_markers', 'default_plotting__average_markers_to_plot__include_markers', self.avg_include_markers_var),
            'avg_include_intermod_markers_var': ('last_plotting__average_markers_to_plot__include_intermod_markers', 'default_plotting__average_markers_to_plot__include_intermod_markers', self.avg_include_intermod_markers_var),
            'math_average_var': ('last_plotting__average_markers_to_plot__math_average', 'default_plotting__average_markers_to_plot__math_average', self.math_average_var),
            'math_median_var': ('last_plotting__average_markers_to_plot__math_median', 'default_plotting__average_markers_to_plot__math_median', self.math_median_var),
            'math_range_var': ('last_plotting__average_markers_to_plot__math_range', 'default_plotting__average_markers_to_plot__math_range', self.math_range_var),
            'math_standard_deviation_var': ('last_plotting__average_markers_to_plot__math_standard_deviation', 'default_plotting__average_markers_to_plot__math_standard_deviation', self.math_standard_deviation_var),
            'math_variance_var': ('last_plotting__average_markers_to_plot__math_variance', 'default_plotting__average_markers_to_plot__math_variance', self.math_variance_var),
            'math_psd_var': ('last_plotting__average_markers_to_plot__math_psd', 'default_plotting__average_markers_to_plot__math_psd', self.math_psd_var),
        }

        # Tkinter variables for band selection checkboxes
        self.band_vars = []
        for band in self.SCAN_BAND_RANGES:
            band_var = tk.BooleanVar(self, value=False)
            band_var.trace_add("write", create_trace_callback(f"band_var_{band['Band Name']}"))
            self.band_vars.append({"band": band, "var": band_var})

    def _apply_saved_geometry(self):
        """
        Function Description:
        Applies the window geometry saved in config.ini, or uses a default
        if no saved geometry is found or if it's invalid.

        Inputs:
            None.

        Process:
            1. Retrieves the window geometry from the 'LAST_USED_SETTINGS'
                section of the application's config, using a default fallback.
            2. Attempts to apply the retrieved geometry to the main window.
            3. If a `TclError` occurs (due to invalid geometry string),
                it logs the error and applies the hardcoded default geometry.

        Outputs:
            None. Sets the main window's size and position.
        """
        current_function = inspect.currentframe().f_code.co_name

        saved_geometry = self.config.get('LAST_USED_SETTINGS', 'last_GLOBAL__window_geometry', fallback=self.DEFAULT_WINDOW_GEOMETRY)
        try:
            self.geometry(saved_geometry)
            debug_logic_module.debug_log(f"Applied saved geometry: {saved_geometry}.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
        except TclError as e:
            debug_logic_module.debug_log(f"ERROR: Invalid saved geometry '{saved_geometry}': {e}. Using default.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
            self.geometry(self.DEFAULT_WINDOW_GEOMETRY)


    def _create_widgets(self):
        """
        Function Description:
        Creates and arranges all GUI widgets in the main application window.
        It sets up a two-column layout using ttk.PanedWindow for a resizable divider,
        with parent tabs on the left and scan control/console on the right.

        Inputs:
            None (operates on self).

        Process:
            1. Prints a debug message.
            2. Configures the main window's grid to host the PanedWindow.
            3. Creates `self.main_panedwindow` for the resizable layout.
            4. Creates `self.parent_notebook` for the top-level parent tabs and adds it to the left pane.
            5. Instantiates and adds all `TAB_X_PARENT` classes to `self.parent_notebook`,
                storing references to parent tab widgets and their child notebooks.
            6. Binds the `<<NotebookTabChanged>>` event for the parent notebook.
            7. Creates `right_column_container` for the right pane and adds it to the PanedWindow.
            8. Instantiates `ScanControlTab` and places it in the right column.
            9. Instantiates `ConsoleTab` and places it below the `ScanControlTab`.
            10. Applies the saved sash position to the PanedWindow.

        Outputs:
            None. Populates the main window with GUI elements.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_logic_module.debug_log(f"Creating main application widgets with nested tabs...",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_panedwindow = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_panedwindow.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.parent_notebook = ttk.Notebook(self.main_panedwindow, style='Parent.TNotebook')
        self.main_panedwindow.add(self.parent_notebook, weight=1)

        # Dictionary to hold references to child tab instances for easy lookup
        # Structure: { "ParentTabName": { "ChildTabName": instance } }
        self.tab_instances = {
            "Instrument": {},
            "Scanning": {},
            "Plotting": {},
            "Markers": {},
            "Presets": {},
            "Experiments": {},
            "JSON API": {} # Assuming a JSON API tab will exist
        }

        self.child_notebooks = {}
        self.parent_tab_widgets = {}

        # Instrument Parent Tab and its children
        self.instrument_parent_tab = TAB_INSTRUMENT_PARENT(self.parent_notebook, app_instance=self, console_print_func=console_logic_module.console_log, style_obj=self.style)
        self.parent_notebook.add(self.instrument_parent_tab, text="INSTRUMENT")
        self.child_notebooks["INSTRUMENT"] = self.instrument_parent_tab.child_notebook
        self.parent_tab_widgets["INSTRUMENT"] = self.instrument_parent_tab
        # Correctly map child tabs for Instrument
        if hasattr(self.instrument_parent_tab, 'instrument_settings_tab'):
            self.tab_instances["Instrument"]["Connection"] = self.instrument_parent_tab.instrument_settings_tab
        if hasattr(self.instrument_parent_tab, 'visa_interpreter_tab'):
            self.tab_instances["Instrument"]["VISA Interpreter"] = self.instrument_parent_tab.visa_interpreter_tab


        # Scanning Parent Tab and its children
        self.scanning_parent_tab = TAB_SCANNING_PARENT(self.parent_notebook, app_instance=self, console_print_func=console_logic_module.console_log)
        self.parent_notebook.add(self.scanning_parent_tab, text="SCANNING")
        self.child_notebooks["SCANNING"] = self.scanning_parent_tab.child_notebook
        self.parent_tab_widgets["SCANNING"] = self.scanning_parent_tab
        # Correctly map child tabs for Scanning
        if hasattr(self.scanning_parent_tab, 'scan_configuration_tab'):
            self.tab_instances["Scanning"]["Scan Configuration"] = self.scanning_parent_tab.scan_configuration_tab
        if hasattr(self.scanning_parent_tab, 'scan_meta_data_tab'):
            self.tab_instances["Scanning"]["Scan Meta Data"] = self.scanning_parent_tab.scan_meta_data_tab
        # Note: Scan Control Tab is handled separately below as it's in the right column


        # Plotting Parent Tab and its children
        self.plotting_parent_tab = TAB_PLOTTING_PARENT(self.parent_notebook, app_instance=self, console_print_func=console_logic_module.console_log)
        self.parent_notebook.add(self.plotting_parent_tab, text="PLOTTING")
        self.child_notebooks["PLOTTING"] = self.plotting_parent_tab.child_notebook
        self.parent_tab_widgets["PLOTTING"] = self.plotting_parent_tab
        # Correctly map child tabs for Plotting
        if hasattr(self.plotting_parent_tab, 'plotting_tab'):
            self.tab_instances["Plotting"]["Plotting"] = self.plotting_parent_tab.plotting_tab


        # Markers Parent Tab and its children
        self.markers_parent_tab = TAB_MARKERS_PARENT(self.parent_notebook, app_instance=self, console_print_func=console_logic_module.console_log)
        self.parent_notebook.add(self.markers_parent_tab, text="MARKERS")
        self.child_notebooks["MARKERS"] = self.markers_parent_tab.child_notebook
        self.parent_tab_widgets["MARKERS"] = self.markers_parent_tab
        # Correctly map child tabs for Markers
        if hasattr(self.markers_parent_tab, 'markers_display_tab'):
            self.tab_instances["Markers"]["Markers Display"] = self.markers_parent_tab.markers_display_tab


        # Presets Parent Tab and its children
        self.presets_parent_tab = TAB_PRESETS_PARENT(self.parent_notebook, app_instance=self, console_print_func=console_logic_module.console_log, style_obj=self.style)
        self.parent_notebook.add(self.presets_parent_tab, text="PRESETS")
        self.child_notebooks["PRESETS"] = self.presets_parent_tab.child_notebook
        self.parent_tab_widgets["PRESETS"] = self.presets_parent_tab
        # Correctly map child tabs for Presets
        if hasattr(self.presets_parent_tab, 'presets_tab'):
            self.tab_instances["Presets"]["Presets"] = self.presets_parent_tab.presets_tab
        if hasattr(self.presets_parent_tab, 'initial_config_tab'): # Added initial_config_tab
            self.tab_instances["Presets"]["Initial Configuration"] = self.presets_parent_tab.initial_config_tab


        # Experiments Parent Tab and its children
        self.experiments_parent_tab = TAB_EXPERIMENTS_PARENT(self.parent_notebook, app_instance=self, console_print_func=console_logic_module.console_log)
        self.parent_notebook.add(self.experiments_parent_tab, text="EXPERIMENTS")
        self.child_notebooks["EXPERIMENTS"] = self.experiments_parent_tab.child_notebook
        self.parent_tab_widgets["EXPERIMENTS"] = self.experiments_parent_tab
        self.tab_instances["Experiments"]["Experiments"] = self.experiments_parent_tab.child_notebook


        self.parent_notebook.bind("<<NotebookTabChanged>>", self._on_parent_tab_change)


        # --- Right Column Container Frame ---
        right_column_container = ttk.Frame(self.main_panedwindow, style='Dark.TFrame')
        self.main_panedwindow.add(right_column_container, weight=1)
        right_column_container.grid_columnconfigure(0, weight=1)
        right_column_container.grid_rowconfigure(0, weight=0) # Scan Control row
        right_column_container.grid_rowconfigure(1, weight=1) # Console row


        # --- Scan Control Buttons Frame ---
        scan_control_frame = ttk.Frame(right_column_container, style='Dark.TFrame')
        scan_control_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        scan_control_frame.grid_columnconfigure(0, weight=1)

        self.scan_control_tab = ScanControlTab(scan_control_frame, app_instance=self)
        self.scan_control_tab.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        # Store the ScanControlTab instance directly as it's not part of a nested notebook
        self.tab_instances["Scanning"]["Scan Control"] = self.scan_control_tab


        # --- Console and Debug Options Frame (Directly in right_column_container) ---
        self.console_tab = ConsoleTab(right_column_container, app_instance=self)
        self.console_tab.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        # Store the ConsoleTab instance directly
        #self.tab_instances["Console"]["Console"] = self


        # Apply the saved sash position after all widgets are added to the paned window
        sash_pos = self.paned_window_sash_position_var.get()
        if sash_pos > 0:
            self.main_panedwindow.sashpos(0, sash_pos)
            debug_logic_module.debug_log(f"Applied saved PanedWindow sash position: {sash_pos}.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
        else:
            debug_logic_module.debug_log(f"WARNING: Invalid saved PanedWindow sash position: {sash_pos}. Using default.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)


        debug_logic_module.debug_log(f"Main application widgets created.",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_function)


    def _setup_styles(self):
        """
        Function Description:
        Configures and applies custom ttk styles for a modern dark theme
        to various Tkinter widgets within the application. This includes
        defining styles for parent and child notebooks to support the
        two-layer tab structure with unique and dynamic colors for parent tabs.

        Inputs:
            None (operates on self).

        Process:
            1. Calls the external `apply_styles` function from `src.style`
                to apply all centralized style configurations.

        Outputs:
            None. Applies visual styling to the application's GUI.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_logic_module.debug_log(f"Setting up ttk styles...",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)
        # Removed self.parent_tab_colors as it's now handled internally by apply_styles via COLOR_PALETTE
        apply_styles(self.style, debug_logic_module.debug_log, current_version)


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
                            file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                            version=current_version,
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
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)

        if hasattr(self, 'main_panedwindow') and self.main_panedwindow.winfo_exists():
            sash_pos = self.main_panedwindow.sashpos(0)
            self.paned_window_sash_position_var.set(sash_pos)
            debug_logic_module.debug_log(f"Saved final sash position: {sash_pos}.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)


        # Pass console_log from here to save_config
        save_config(self.config, self.CONFIG_FILE_PATH, console_logic_module.console_log, self)

        if self.inst:
            debug_logic_module.debug_log(f"Disconnecting instrument before exit.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
            disconnect_instrument_logic(self, console_logic_module.console_log)

        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        print(f"Debug output redirected back to terminal. Application closing. Version: {current_version}")

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
        debug_logic_module.debug_log(f"Parent tab changed event triggered. Version: {current_version}. Time to update styles and ASCII art!",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
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
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)


        # Propagate _on_tab_selected to the selected parent tab
        selected_parent_tab_widget = self.parent_notebook.nametowidget(selected_tab_id)
        if hasattr(selected_parent_tab_widget, '_on_parent_tab_selected'): # Changed to _on_parent_tab_selected
            selected_parent_tab_widget._on_parent_tab_selected(event) # Call the new parent-specific method
            debug_logic_module.debug_log(f"Propagated _on_parent_tab_selected to active parent tab: {selected_parent_tab_widget.winfo_class()}. Version: {current_version}. Looking good!",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
        else:
            debug_logic_module.debug_log(f"Active parent tab {selected_parent_tab_widget.winfo_class()} has no _on_parent_tab_selected method. What the hell?! Version: {current_version}.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
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
                    debug_logic_module.debug_log(f"Propagated _on_tab_selected to active child tab {selected_child_tab_widget.winfo_class()} in parent '{selected_tab_text}'. Version: {current_version}. All good!",
                                file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                                version=current_version,
                                function=current_function)
                else:
                    debug_logic_module.debug_log(f"Active child tab {selected_child_tab_widget.winfo_class()} in parent '{selected_tab_text}' has no _on_tab_selected method.",
                                file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                                version=current_version,
                                function=current_function)
            else:
                debug_logic_module.debug_log(f"No child tab selected in parent '{selected_tab_text}'.",
                            file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                            version=current_version,
                            function=current_function)
        else:
            debug_logic_module.debug_log(f"No child notebook found for parent tab '{selected_tab_text}'.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)

    def update_connection_status(self, is_connected, is_scanning):
        """
        Function Description:
        Updates the connection status label and the flashing state of the Connect/Disconnect button
        on the Instrument Connection tab. It dynamically changes the button's style
        based on the connection and scanning status.

        Inputs:
            is_connected (bool): True if the instrument is connected, False otherwise.
            is_scanning (bool): True if a scan is currently in progress, False otherwise.

        Process:
            1. Logs the status update.
            2. Retrieves the Instrument Connection tab instance.
            3. If the tab exists:
                a. Updates the connection status label text.
                b. Manages the flashing state of the Connect/Disconnect button:
                    - If scanning, sets it to 'flashing_red'.
                    - If connected and not scanning, sets it to 'flashing_green'.
                    - If disconnected, sets it to 'flashing_gray'.
                c. Updates the button's style.
            4. If the tab does not exist, logs a warning.

        Outputs:
            None. Updates GUI elements.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_logic_module.debug_log(f"Updating connection status: Connected={is_connected}, Scanning={is_scanning}. Version: {current_version}.",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)

        instrument_connection_tab = self.tab_instances.get("Instrument", {}).get("Connection")

        if instrument_connection_tab:
            if is_connected:
                instrument_connection_tab.connection_status_label.config(text="Status: Connected 🎉", foreground="green")
            else:
                instrument_connection_tab.connection_status_label.config(text="Status: Disconnected 💀", foreground="red")

            # Manage flashing state of the Connect/Disconnect button
            if is_scanning:
                instrument_connection_tab.connect_button.config(style="FlashingRed.TButton")
                debug_logic_module.debug_log(f"Connect button style set to FlashingRed.",
                            file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                            version=current_version,
                            function=current_function)
            elif is_connected:
                instrument_connection_tab.connect_button.config(style="FlashingGreen.TButton")
                debug_logic_module.debug_log(f"Connect button style set to FlashingGreen.",
                            file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                            version=current_version,
                            function=current_function)
            else:
                instrument_connection_tab.connect_button.config(style="FlashingGray.TButton")
                debug_logic_module.debug_log(f"Connect button style set to FlashingGray.",
                            file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                            version=current_version,
                            function=current_function)
        else:
            debug_logic_module.debug_log(f"WARNING: Instrument Connection tab not found for status update.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)

    def get_tab_instance(self, parent_tab_name, child_tab_name=None):
        """
        Function Description:
        Retrieves a specific tab instance from the `tab_instances` dictionary.
        This provides a centralized way to access tab objects for updating their
        GUI elements or calling their methods.

        Inputs:
            parent_tab_name (str): The name of the parent tab (e.g., "Instrument", "Scanning").
            child_tab_name (str, optional): The name of the child tab within the parent.
                                            If None, returns the parent tab widget itself.

        Process:
            1. If `child_tab_name` is provided, it attempts to retrieve the specific
                child tab instance from the nested dictionary.
            2. If `child_tab_name` is None, it returns the parent tab widget.
            3. Includes error handling for cases where the tab is not found.

        Outputs:
            The requested tab instance, or None if not found.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_logic_module.debug_log(f"Attempting to get tab instance: Parent='{parent_tab_name}', Child='{child_tab_name}'. Version: {current_version}.",
                    file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                    version=current_version,
                    function=current_function)

        if parent_tab_name not in self.tab_instances:
            debug_logic_module.debug_log(f"ERROR: Parent tab '{parent_tab_name}' not found in tab_instances.",
                        file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                        version=current_version,
                        function=current_function)
            return None

        if child_tab_name:
            if child_tab_name not in self.tab_instances[parent_tab_name]:
                debug_logic_module.debug_log(f"ERROR: Child tab '{child_tab_name}' not found in parent '{parent_tab_name}'.",
                            file=f"{os.path.basename(__file__)} - {current_version}", # Updated debug file name
                            version=current_version,
                            function=current_function)
                return None
            return self.tab_instances[parent_tab_name][child_tab_name]
        else:
            return self.parent_tab_widgets.get(parent_tab_name)

if __name__ == "__main__":
    app = App()
    app.mainloop()
