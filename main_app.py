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
# Version 20250801.1900.2 (Fixed config.ini not being created/populated on first run and TclError in tab styling.)

current_version = "20250801.1900.2" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250801 * 1900 * 2 + -638010053603417879 # Calculated hash for version 20250801.1900.2


# Project file structure
#└── OPEN-AIR/
#       ├── DATA/
#       ├── process_math/
#       ├── ref/
#       ├── scan_data/
#       ├── src/
#       ├── tabs/
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
from datetime import datetime # For timestamp in debug_print
import subprocess


# Import local modules - Paths are relative to OPEN-AIR as main_app.py is in OPEN-AIR
# and src, tabs, utils, ref are direct subdirectories.
from src.config_manager import load_config, save_config
from src.gui_elements import TextRedirector, print_art


from src.instrument_logic import (
    populate_resources_logic, connect_instrument_logic, disconnect_instrument_logic,
    apply_settings_logic,
    query_current_instrument_settings_logic
)
from src.scan_logic import update_connection_status_logic
from src.settings_logic import restore_default_settings_logic, restore_last_used_settings_logic
from src.scan_controler_button_logic import ScanControlTab
from src.style import apply_styles # NEW: Import the apply_styles function
from src.check_Dependancies import check_and_install_dependencies # NEW: Import the standalone dependency check

from utils.utils_instrument_control import set_debug_mode, set_log_visa_commands_mode, debug_print


# Import the new parent tab classes
from tabs.Instrument.TAB_INSTRUMENT_PARENT import TAB_INSTRUMENT_PARENT
from tabs.Scanning.TAB_SCANNING_PARENT import TAB_SCANNING_PARENT
from tabs.Plotting.TAB_PLOTTING_PARENT import TAB_PLOTTING_PARENT
from tabs.Markers.TAB_MARKERS_PARENT import TAB_MARKERS_PARENT
from tabs.Presets.TAB_PRESETS_PARENT import TAB_PRESETS_PARENT
from tabs.Experiments.TAB_EXPERIMENTS_PARENT import TAB_EXPERIMENTS_PARENT


# Import preset logic functions from utils.preset_utils
from tabs.Presets.utils_preset import load_selected_preset_logic, query_device_presets_logic


# Import constants from frequency_bands.py
from ref.frequency_bands import SCAN_BAND_RANGES, MHZ_TO_HZ, VBW_RBW_RATIO


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

  

    DEFAULT_WINDOW_GEOMETRY = "1400x780+100+100" # This is now a fallback, actual default comes from config

    def __init__(self):
        # Function Description:
        # Initializes the main application window and sets up core components.
        # It performs dependency checks, initializes instrument communication,
        # sets up Tkinter variables, loads configuration, creates UI widgets,
        # applies styling, and redirects console output. It now also checks
        # for the presence of config.ini and enables general debugging if not found,
        # displaying relevant status remarks on the GUI console.
        #
        # Inputs:
        #   None.
        #
        # Process:
        #   1. Calls the superclass constructor (tk.Tk).
        #   2. Sets the window title and protocol for closing.
        #   3. Initializes `configparser` object and `is_ready_to_save` flag.
        #   4. Calls `_check_and_install_dependencies` to ensure environment readiness.
        #   5. Initializes instrument-related attributes (`rm`, `inst`, `instrument_model`).
        #   6. Initializes data storage lists (`collected_scans_dataframes`, `last_scan_markers`).
        #   7. Initializes scan control flags and threading events.
        #   8. Sets up frequency band constants.
        #   9. Calls `_setup_tkinter_vars` to create all Tkinter variables.
        #   10. Calls `load_config` to populate variables from `config.ini`.
        #   11. Applies saved window geometry.
        #   12. Initializes `ttk.Style`.
        #   13. Sets debug modes based on loaded config.
        #   14. Calls `_ensure_data_directory_exists` to create the DATA folder.
        #   15. Calls `_create_widgets` to build the GUI.
        #   16. Calls `_setup_styles` to apply custom themes.
        #   17. Redirects stdout to the GUI console.
        #   18. **NEW: Checks for config.ini and sets debug mode if not found, displaying status.**
        #   19. Updates connection status.
        #   20. Prints application art.
        #   21. Loads band selections for ScanTab (now nested).
        #   22. Manually updates notes text widget on ScanMetaDataTab (now nested).
        #   23. Sets `is_ready_to_save` to True.
        #
        # Outputs:
        #   None. Initializes the main application object.
        #
        # (2025-08-01 18:07) Change: Fixed TypeError: update_connection_status_logic() got an unexpected keyword argument 'is_scanning'.
        # (2025-08-01 18:07) Change: Removed 'is_scanning' argument from the call to update_connection_status_logic.
        # (2025-08-01 18:07) Change: Corrected AttributeError: 'TAB_INSTRUMENT_PARENT' object has no attribute 'visa_interpreter_tab'.
        # (2025-08-01 18:07) Change: Fixed AttributeError: 'TAB_PLOTTING_PARENT' object has no attribute 'plotting_tab' by using correct child tab attributes.
        # (2025-08-01 18:07) Change: Fixed AttributeError: '_tkinter.tkapp' object has no attribute 'console_print_func' by conditionally passing console_print_func to debug_print during early initialization.
        # (2025-08-01 18:07) Change: Fixed TypeError: load_config() takes 3 positional arguments but 4 were given by removing the extra 'self' argument from the call.
        # (2025-08-01 1807.7) Change: Fixed AttributeError: 'function' object has no attribute 'SCAN_BAND_RANGES' by re-adding app_instance to load_config call and updating save_config signature.
        # (2025-08-01 1807.8) Change: Fixed TypeError: load_config() takes 3 positional arguments but 4 were given by correcting argument passing to load_config and updating save_config signature.
        # (2025-08-01 1807.9) Change: Fixed TypeError: update_connection_status_logic() got an unexpected keyword argument 'instrument_tab' by passing specific child tab instances.
        # (2025-08-01 1807.10) Change: Fixed TypeError: update_connection_status_logic() got an unexpected keyword argument 'instrument_connection_tab' by simplifying arguments passed to the function.
        # (2025-08-01 1807.11) Change: Fixed AttributeError: '_tkinter.tkapp' object has no attribute 'is_ready_to_save' by initializing the flag earlier.
        # (2025-08-01 1845.1) Change: Fixed DATA_FOLDER_PATH to be inside the main app directory.
        # (2025-08-01 1850.2) Change: Implemented logic to check for config.ini and enable general debugging if missing, displaying status on console.
        # (2025-08-01 1900.1) Change: Regenerated file to ensure latest version is presented. No functional changes from previous version.
        # (2025-08-01 1900.2) Change: Ensured config.ini is created and populated with defaults on first run if it doesn't exist.
        #                             Removed invalid 'background' and 'foreground' arguments from parent_notebook.tab() call to fix TclError.
        super().__init__()
        self.title("OPEN AIR - 🌐🗺️ - Zone Awareness Processor") # Changed window title
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Initialize is_ready_to_save to False at the very beginning
        # This prevents AttributeError when Tkinter variable traces are triggered during setup.
        self.is_ready_to_save = False

        # Initialize console_text to None or a dummy object before _create_widgets
        # This prevents AttributeError if _print_to_gui_console is called before the widget exists
        self.console_text = None

        check_and_install_dependencies(current_version) # Call the standalone function

        self.rm = None
        self.inst = None
        self.instrument_model = None

        self.collected_scans_dataframes = []
        self.last_scan_markers = [] # Ensure this is initialized

        self.scanning = False
        self.scan_thread = None
        self.stop_scan_event = threading.Event()
        self.pause_scan_event = threading.Event()

        self.SCAN_BAND_RANGES = SCAN_BAND_RANGES
        self.MHZ_TO_HZ = MHZ_TO_HZ
        self.VBW_RBW_RATIO = VBW_RBW_RATIO

        # Pass None for console_print_func initially, as console_text is not yet ready
        self._setup_tkinter_vars(console_print_func=None) # Initialize Tkinter variables BEFORE loading config

        # Ensure the DATA directory exists. Pass None for console_print_func initially.
        self._ensure_data_directory_exists(console_print_func=None)

        # Check if config.ini exists before attempting to load
        config_file_exists_on_startup = os.path.exists(self.CONFIG_FILE_PATH)

        # FUCKING IMPORTANT: Corrected load_config call to pass all required arguments
        # and assign the returned config object to self.config
        self.config = configparser.ConfigParser() # Initialize config parser before loading
        # Corrected load_config call to pass self.config, CONFIG_FILE_PATH, print func, and self (app_instance)
        load_config(self.config, self.CONFIG_FILE_PATH, self._print_to_gui_console, self)
        
        # If config.ini did not exist on startup, save it now to populate with defaults
        if not config_file_exists_on_startup:
            debug_print(f"config.ini was not found on startup. Saving defaults to new file.",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name,
                        console_print_func=self._print_to_gui_console)
            save_config(self.config, self.CONFIG_FILE_PATH, self._print_to_gui_console, self)


        # Pass None for console_print_func initially, as console_text is not yet ready
        self._apply_saved_geometry(console_print_func=None)

        # Initialize self.style BEFORE _create_widgets is called
        self.style = ttk.Style(self) # Make style an instance attribute

        # These calls now use the Tkinter variables directly, which are populated by load_config
        # The initial setting here uses values from config.ini, which might be defaults if config.ini was not found.
        set_debug_mode(self.general_debug_enabled_var.get())
        set_log_visa_commands_mode(self.log_visa_commands_enabled_var.get())

        self._create_widgets() # console_text is initialized here

        self._setup_styles() # This will now configure self.style
        self._redirect_stdout_to_console()

        # NEW: Check for config.ini and enable debug if not found, reporting status to GUI console
        self._check_config_and_set_debug()

        # Call _on_parent_tab_change to set initial tab colors after all widgets are created
        # Pass a dummy event as it's not triggered by a user action
        self._on_parent_tab_change(None)

        # Initial update of connection status. This will now correctly access the tab instances.
        self.update_connection_status(self.inst is not None)

        print_art()

        # Adjusted startup calls for band selections and notes to new nested tab structure
        if hasattr(self, 'scanning_parent_tab') and hasattr(self.scanning_parent_tab, 'scan_configuration_tab'):
            self.scanning_parent_tab.scan_configuration_tab._load_band_selections_from_config()
            debug_print(f"Called _load_band_selections_from_config on Scan Configuration Tab during startup.",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name,
                        console_print_func=self._print_to_gui_console) # Added console_print_func

        if hasattr(self, 'scanning_parent_tab') and hasattr(self.scanning_parent_tab, 'scan_meta_data_tab'):
            # Ensure the notes_text_widget exists before trying to access it
            if hasattr(self.scanning_parent_tab.scan_meta_data_tab, 'notes_text_widget'):
                self.scanning_parent_tab.scan_meta_data_tab.notes_text_widget.delete("1.0", tk.END)
                self.scanning_parent_tab.scan_meta_data_tab.notes_text_widget.insert("1.0", self.notes_var.get())
                debug_print(f"Updated notes_text_widget on Scan Meta Data Tab during startup.",
                            file=f"main_app.py - {current_version}",
                            function=inspect.currentframe().f_code.co_name,
                            console_print_func=self._print_to_gui_console) # Added console_print_func
            else:
                debug_print(f"ScanMetaDataTab notes_text_widget not found for initial notes update.",
                            file=f"main_app.py - {current_version}",
                            function=inspect.currentframe().f_code.co_name,
                            console_print_func=self._print_to_gui_console) # Added console_print_func
        else:
            debug_print(f"ScanMetaDataTab not found for initial notes update.",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name,
                        console_print_func=self._print_to_gui_console) # Added console_print_func


        # Set to True only after all initialization is complete
        self.is_ready_to_save = True
        debug_print(f"Application fully initialized and ready to save configuration.",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name,
                    console_print_func=self._print_to_gui_console) # Added console_print_func

    # Function Description:
    # Checks for the presence of the config.ini file in the DATA_FOLDER_PATH.
    # If config.ini is not found, it automatically enables general debugging
    # and updates the GUI console with status remarks.
    #
    # Inputs:
    #   None.
    #
    # Process:
    #   1. Logs the start of the configuration check to the debug console.
    #   2. Checks if self.CONFIG_FILE_PATH exists.
    #   3. If it does not exist:
    #      a. Prints a warning to the GUI console and debug log.
    #      b. Sets the general_debug_enabled_var to True.
    #      c. Calls set_debug_mode to activate debugging.
    #   4. If it exists:
    #      a. Prints a success message to the GUI console and debug log.
    #   5. Displays the current general debug mode status to the GUI console and debug log.
    #
    # Outputs:
    #   Returns True if config.ini was found, False otherwise.
    #   Modifies application state (debug mode) and updates GUI console.
    #
    # (2025-08-01 1850.2) Change: New function to check for config.ini and enable debug if missing.
    # (2025-08-01 1900.1) Change: No functional changes.
    # (2025-08-01 1900.2) Change: Modified to return a boolean indicating if config.ini was found.
    def _check_config_and_set_debug(self):
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)

        self._print_to_gui_console(f"--- Configuration & Debug Status ({current_version}) ---")
        debug_print(f"Checking for config.ini at: {self.CONFIG_FILE_PATH}",
                    file=f"{current_file} - {current_version}",
                    function=current_function, console_print_func=self._print_to_gui_console)

        config_file_found = os.path.exists(self.CONFIG_FILE_PATH)

        if not config_file_found:
            self._print_to_gui_console(f"❌ config.ini not found at '{self.CONFIG_FILE_PATH}'.")
            self._print_to_gui_console(f"⚠️ General debugging enabled automatically. Let's see what the fuck is going on!")
            self.general_debug_enabled_var.set(True)
            set_debug_mode(True) # Ensure the actual debug mode is set
            debug_print(f"config.ini not found. General debugging enabled.",
                        file=f"{current_file} - {current_version}",
                        function=current_function, console_print_func=self._print_to_gui_console)
        else:
            self._print_to_gui_console(f"✅ config.ini found at '{self.CONFIG_FILE_PATH}'.")
            debug_print(f"config.ini found.",
                        file=f"{current_file} - {current_version}",
                        function=current_function, console_print_func=self._print_to_gui_console)

        # Display current debug status (regardless of config.ini presence)
        if self.general_debug_enabled_var.get():
            self._print_to_gui_console(f"🐞 Current General Debug Mode: ENABLED")
            debug_print(f"Current General Debug Mode: ENABLED",
                        file=f"{current_file} - {current_version}",
                        function=current_function, console_print_func=self._print_to_gui_console)
        else:
            self._print_to_gui_console(f"🐞 Current General Debug Mode: DISABLED")
            debug_print(f"Current General Debug Mode: DISABLED",
                        file=f"{current_file} - {current_version}",
                        function=current_function, console_print_func=self._print_to_gui_console)
        self._print_to_gui_console(f"--------------------------------------------------")
        
        return config_file_found


    def _ensure_data_directory_exists(self, console_print_func=None):
        # Function Description:
        # Ensures that the DATA directory exists. If it doesn't, it creates it.
        # This function is called early in initialization, potentially before
        # the GUI console is fully set up, hence the conditional console_print_func.
        #
        # Inputs:
        #   console_print_func (function, optional): Function to use for console output.
        #
        # Process:
        #   1. Checks if `self.DATA_FOLDER_PATH` exists.
        #   2. If not, attempts to create it using `os.makedirs`.
        #   3. Logs success or failure to the console.
        #
        # Outputs:
        #   None. Creates a directory if necessary.
        #
        # (2025-07-31) Change: Initial implementation for DATA folder creation.
        # (2025-08-01) Change: Added console_print_func parameter to allow conditional printing.
        # (2025-08-01 1850.2) Change: No functional change, but now called early for directory creation.
        # (2025-08-01 1900.1) Change: No functional changes.
        # (2025-08-01 1900.2) Change: No functional changes.
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_print(f"Ensuring DATA directory exists at: {self.DATA_FOLDER_PATH}",
                    file=f"{current_file} - {current_version}",
                    function=current_function, console_print_func=console_print_func)
        try:
            if not os.path.exists(self.DATA_FOLDER_PATH):
                os.makedirs(self.DATA_FOLDER_PATH)
                if console_print_func: # Only print to GUI console if function is provided
                    console_print_func(f"✅ Created DATA directory: {self.DATA_FOLDER_PATH}")
                debug_print(f"DATA directory created.",
                            file=f"{current_file} - {current_version}",
                            function=current_function, console_print_func=console_print_func)
            else:
                if console_print_func: # Only print to GUI console if function is provided
                    console_print_func(f"ℹ️ DATA directory already exists: {self.DATA_FOLDER_PATH}")
                debug_print(f"DATA directory already exists.",
                            file=f"{current_file} - {current_version}",
                            function=current_function, console_print_func=console_print_func)
        except Exception as e:
            if console_print_func: # Only print to GUI console if function is provided
                console_print_func(f"❌ Error creating DATA directory {self.DATA_FOLDER_PATH}: {e}. This is a real clusterfuck!")
            debug_print(f"Error creating DATA directory: {e}",
                        file=f"{current_file} - {current_version}",
                        function=current_function, console_print_func=console_print_func)

    def _setup_tkinter_vars(self, console_print_func=None):
        # Function Description:
        # Initializes all Tkinter `StringVar`, `BooleanVar`, and `DoubleVar` instances
        # used throughout the application. These variables are linked to GUI widgets
        # and configuration settings.
        #
        # Inputs:
        #   console_print_func (function, optional): Function to use for console output.
        #
        # Process:
        #   1. Initializes StringVars for VISA resource names, selected resource,
        #      instrument model, and various scan settings (frequency, RBW, Ref Level, etc.).
        #   2. Initializes BooleanVars for debug modes, HTML output options, and marker inclusions.
        #   3. Initializes DoubleVars for VBW/RBW ratio and sweep time.
        #   4. Initializes IntegerVars for sweep points and average count.
        #
        # Outputs:
        #   None. Populates `self` with Tkinter variable objects.
        #
        # (2025-07-31) Change: Added `include_scan_intermod_markers_var` and `avg_include_intermod_markers_var`.
        # (2025-08-01) Change: Added console_print_func parameter to allow conditional printing during early init.
        # (2025-08-01 1850.2) Change: No functional change.
        # (2025-08-01 1900.1) Change: No functional changes.
        # (2025-08-01 1900.2) Change: No functional changes.
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_print("Setting up Tkinter variables...",
                    file=f"{current_file} - {current_version}",
                    function=current_function, console_print_func=console_print_func)

        # Define a helper function to add trace for saving config
        def create_trace_callback(var_name):
            def callback(*args):
                # Only save if the app is fully initialized to avoid saving partial states during startup
                if self.is_ready_to_save: # This check now works because is_ready_to_save is initialized early
                    debug_print(f"Tkinter variable '{var_name}' changed. Saving config.",
                                file=f"{current_file} - {current_version}", # Corrected file path
                                function=inspect.currentframe().f_code.co_name,
                                console_print_func=self._print_to_gui_console) # Added console_print_func
                    # FUCKING IMPORTANT: Call save_config here!
                    save_config(self.config, self.CONFIG_FILE_PATH, self._print_to_gui_console, self)
            return callback

        # GLOBAL variables
        self.general_debug_enabled_var = tk.BooleanVar(self, value=False)
        self.general_debug_enabled_var.trace_add("write", create_trace_callback("general_debug_enabled_var"))

        self.log_visa_commands_enabled_var = tk.BooleanVar(self, value=False)
        self.log_visa_commands_enabled_var.trace_add("write", create_trace_callback("log_visa_commands_enabled_var"))

        # NEW: PanedWindow sash position variable
        self.paned_window_sash_position_var = tk.IntVar(self, value=700) # Default to a reasonable split
        self.paned_window_sash_position_var.trace_add("write", create_trace_callback("paned_window_sash_position_var"))


        # Instrument Connection variables
        self.selected_resource = tk.StringVar(self) # Holds the currently selected VISA resource
        self.selected_resource.trace_add("write", create_trace_callback("selected_resource"))

        self.resource_names = tk.StringVar(self) # Holds the list of available VISA resources
        # resource_names does not need a trace as it's populated internally, not user-edited

        # Scan Configuration variables
        self.scan_name_var = tk.StringVar(self, value="ThisIsMyScan")
        self.scan_name_var.trace_add("write", create_trace_callback("scan_name_var"))

        # (2025-08-01) Change: Set output_folder_var to DATA_FOLDER_PATH
        self.output_folder_var = tk.StringVar(self, value=self.DATA_FOLDER_PATH)
        self.output_folder_var.trace_add("write", create_trace_callback("output_folder_var"))

        self.num_scan_cycles_var = tk.IntVar(self, value=1)
        self.num_scan_cycles_var.trace_add("write", create_trace_callback("num_scan_cycles_var"))

        self.rbw_step_size_hz_var = tk.StringVar(self, value="10000") # Now controlled by dropdown
        self.rbw_step_size_hz_var.trace_add("write", create_trace_callback("rbw_step_size_hz_var"))

        self.cycle_wait_time_seconds_var = tk.StringVar(self, value="0.5") # Now controlled by dropdown
        self.cycle_wait_time_seconds_var.trace_add("write", create_trace_callback("cycle_wait_time_seconds_var"))

        self.maxhold_time_seconds_var = tk.StringVar(self, value="3")
        self.maxhold_time_seconds_var.trace_add("write", create_trace_callback("maxhold_time_seconds_var"))

        self.scan_rbw_hz_var = tk.StringVar(self, value="10000") # Now controlled by dropdown
        self.scan_rbw_hz_var.trace_add("write", create_trace_callback("scan_rbw_hz_var"))

        self.reference_level_dbm_var = tk.StringVar(self, value="-40") # Now controlled by dropdown
        self.reference_level_dbm_var.trace_add("write", create_trace_callback("reference_level_dbm_var"))

        self.freq_shift_hz_var = tk.StringVar(self, value="0") # Now controlled by dropdown
        self.freq_shift_hz_var.trace_add("write", create_trace_callback("freq_shift_hz_var"))

        self.maxhold_enabled_var = tk.BooleanVar(self, value=True) # Removed from UI, but kept for config persistence
        self.maxhold_enabled_var.trace_add("write", create_trace_callback("maxhold_enabled_var"))

        self.high_sensitivity_var = tk.BooleanVar(self, value=True) # Corresponds to 'sensitivity' in config, now dropdown
        self.high_sensitivity_var.trace_add("write", create_trace_callback("high_sensitivity_var"))

        self.preamp_on_var = tk.BooleanVar(self, value=True) # Now controlled by dropdown
        self.preamp_on_var.trace_add("write", create_trace_callback("preamp_on_var"))

        self.scan_rbw_segmentation_var = tk.StringVar(self, value="1000000.0")
        self.scan_rbw_segmentation_var.trace_add("write", create_trace_callback("scan_rbw_segmentation_var"))

        self.desired_default_focus_width_var = tk.StringVar(self, value="10000.0")
        self.desired_default_focus_width_var.trace_add("write", create_trace_callback("desired_default_focus_width_var"))

        # Scan Meta Data variables
        self.operator_name_var = tk.StringVar(self, value="Anthony Peter Kuzub")
        self.operator_name_var.trace_add("write", create_trace_callback("operator_name_var"))

        self.operator_contact_var = tk.StringVar(self, value="I@Like.audio")
        self.operator_contact_var.trace_add("write", create_trace_callback("operator_contact_var"))

        self.venue_name_var = tk.StringVar(self, value="Garage") # Corresponds to 'name' in config
        self.venue_name_var.trace_add("write", create_trace_callback("venue_name_var"))

        # NEW: Location variables from ScanMetaDataTab
        self.venue_postal_code_var = tk.StringVar(self, value="")
        self.venue_postal_code_var.trace_add("write", create_trace_callback("venue_postal_code_var"))

        self.address_field_var = tk.StringVar(self, value="")
        self.address_field_var.trace_add("write", create_trace_callback("address_field_var"))

        self.city_var = tk.StringVar(self, value="Whitby") # Still used for City
        self.city_var.trace_add("write", create_trace_callback("city_var"))

        self.province_var = tk.StringVar(self, value="") # NEW: For Province
        self.province_var.trace_add("write", create_trace_callback("province_var"))

        self.scanner_type_var = tk.StringVar(self, value="Unknown")
        self.scanner_type_var.trace_add("write", create_trace_callback("scanner_type_var"))

        # NEW: Antenna and Amplifier variables
        self.selected_antenna_type_var = tk.StringVar(self, value="") # Holds selected type from dropdown
        self.selected_antenna_type_var.trace_add("write", create_trace_callback("selected_antenna_type_var"))

        self.antenna_description_var = tk.StringVar(self, value="") # Populated from selected antenna type
        self.antenna_description_var.trace_add("write", create_trace_callback("antenna_description_var"))

        self.antenna_use_var = tk.StringVar(self, value="") # Populated from selected antenna type
        self.antenna_use_var.trace_add("write", create_trace_callback("antenna_use_var"))

        self.antenna_mount_var = tk.StringVar(self, value="") # User input for mount
        self.antenna_mount_var.trace_add("write", create_trace_callback("antenna_mount_var"))

        self.selected_amplifier_type_var = tk.StringVar(self, value="") # Holds selected amplifier type from dropdown
        self.selected_amplifier_type_var.trace_add("write", create_trace_callback("selected_amplifier_type_var"))

        # Existing antenna_amplifier_var is still used by ScanMetaDataTab for the actual value
        self.antenna_amplifier_var = tk.StringVar(self, value="Ground Plane") # This variable is set by _on_amplifier_type_selected
        self.antenna_amplifier_var.trace_add("write", create_trace_callback("antenna_amplifier_var"))

        self.amplifier_description_var = tk.StringVar(self, value="") # NEW: Amplifier description
        self.amplifier_description_var.trace_add("write", create_trace_callback("amplifier_description_var"))

        self.amplifier_use_var = tk.StringVar(self, value="")         # NEW: Amplifier use
        self.amplifier_use_var.trace_add("write", create_trace_callback("amplifier_use_var"))

        self.notes_var = tk.StringVar(self, value="")
        # The notes_var is handled by a KeyRelease bind in ScanMetaDataTab, so no direct trace needed here.
        # It's explicitly saved in _on_notes_change in tab_scan_meta_data.py

        # NEW: Variables for persistent preset selection and its loaded details
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

        self.include_scan_intermod_markers_var = tk.BooleanVar(self, value=False) # NEW: For single scan intermod
        self.include_scan_intermod_markers_var.trace_add("write", create_trace_callback("include_scan_intermod_markers_var"))

        self.open_html_after_complete_var = tk.BooleanVar(self, value=True)
        self.open_html_after_complete_var.trace_add("write", create_trace_callback("open_html_after_complete_var"))

        self.create_html_var = tk.BooleanVar(self, value=True) # New variable for create_html
        self.create_html_var.trace_add("write", create_trace_callback("create_html_var"))

        # Plotting variables (Average Markers)
        self.avg_include_gov_markers_var = tk.BooleanVar(self, value=True) # New var
        self.avg_include_gov_markers_var.trace_add("write", create_trace_callback("avg_include_gov_markers_var"))

        self.avg_include_tv_markers_var = tk.BooleanVar(self, value=True) # New var
        self.avg_include_tv_markers_var.trace_add("write", create_trace_callback("avg_include_tv_markers_var"))

        self.avg_include_markers_var = tk.BooleanVar(self, value=True) # New var
        self.avg_include_markers_var.trace_add("write", create_trace_callback("avg_include_markers_var"))

        self.avg_include_intermod_markers_var = tk.BooleanVar(self, value=False) # NEW: For average plot intermod
        self.avg_include_intermod_markers_var.trace_add("write", create_trace_callback("avg_include_intermod_markers_var"))

        self.math_average_var = tk.BooleanVar(self, value=True) # New var
        self.math_average_var.trace_add("write", create_trace_callback("math_average_var"))

        self.math_median_var = tk.BooleanVar(self, value=True) # New var
        self.math_median_var.trace_add("write", create_trace_callback("math_median_var"))

        self.math_range_var = tk.BooleanVar(self, value=True) # New var
        self.math_range_var.trace_add("write", create_trace_callback("math_range_var"))

        self.math_standard_deviation_var = tk.BooleanVar(self, value=True) # New var
        self.math_standard_deviation_var.trace_add("write", create_trace_callback("math_standard_deviation_var"))

        self.math_variance_var = tk.BooleanVar(self, value=True) # New var
        self.math_variance_var.trace_add("write", create_trace_callback("math_variance_var"))

        self.math_psd_var = tk.BooleanVar(self, value=True) # New var
        self.math_psd_var.trace_add("write", create_trace_callback("math_psd_var"))


        # Map Tkinter variables to config.ini keys using the new prefixed style
        # Format: 'tk_var_name': ('last_key_in_config', 'default_key_in_config', tk_var_instance)
        # Note: 'last_key_in_config' and 'default_key_in_config' are the full key names including prefixes
        self.setting_var_map = {
            'general_debug_enabled_var': ('last_GLOBAL__debug_enabled', 'default_GLOBAL__debug_enabled', self.general_debug_enabled_var),
            'log_visa_commands_enabled_var': ('last_GLOBAL__log_visa_commands_enabled', 'default_GLOBAL__log_visa_commands_enabled', self.log_visa_commands_enabled_var),
            'paned_window_sash_position_var': ('last_GLOBAL__paned_window_sash_position', 'default_GLOBAL__paned_window_sash_position', self.paned_window_sash_position_var), # NEW
            'selected_resource': ('last_instrument_connection__visa_resource', 'default_instrument_connection__visa_resource', self.selected_resource),

            'scan_name_var': ('last_scan_configuration__scan_name', 'default_scan_configuration__scan_name', self.scan_name_var),
            'output_folder_var': ('last_scan_configuration__scan_directory', 'default_scan_configuration__scan_directory', self.output_folder_var),
            'num_scan_cycles_var': ('last_scan_configuration__num_scan_cycles', 'default_scan_configuration__num_scan_cycles', self.num_scan_cycles_var),
            'rbw_step_size_hz_var': ('last_scan_configuration__rbw_step_size_hz', 'default_scan_configuration__rbw_step_size_hz', self.rbw_step_size_hz_var),
            'cycle_wait_time_seconds_var': ('last_scan_configuration__cycle_wait_time_seconds', 'default_scan_configuration__cycle_wait_time_seconds', self.cycle_wait_time_seconds_var),
            'maxhold_time_seconds_var': ('last_scan_configuration__maxhold_time_seconds', 'default_scan_configuration__maxhold_time_seconds', self.maxhold_time_seconds_var),
            'scan_rbw_hz_var': ('last_scan_configuration__scan_rbw_hz', 'default_scan_configuration__scan_rbw_hz', self.scan_rbw_hz_var),
            'reference_level_dbm_var': ('last_scan_configuration__reference_level_dbm', 'default_scan_configuration__reference_level_dbm', self.reference_level_dbm_var),
            'freq_shift_hz_var': ('last_scan_configuration__freq_shift_hz', 'default_scan_configuration__freq_shift_hz', self.freq_shift_hz_var),
            'maxhold_enabled_var': ('last_scan_configuration__maxhold_enabled', 'default_scan_configuration__maxhold_enabled', self.maxhold_enabled_var),
            'high_sensitivity_var': ('last_scan_configuration__sensitivity', 'default_scan_configuration__sensitivity', self.high_sensitivity_var), # Mapped to 'sensitivity'
            'preamp_on_var': ('last_scan_configuration__preamp_on', 'default_scan_configuration__preamp_on', self.preamp_on_var),
            'scan_rbw_segmentation_var': ('last_scan_configuration__scan_rbw_segmentation', 'default_scan_configuration__scan_rbw_segmentation', self.scan_rbw_segmentation_var),
            'desired_default_focus_width_var': ('last_scan_configuration__default_focus_width', 'default_scan_configuration__default_focus_width', self.desired_default_focus_width_var),

            'operator_name_var': ('last_scan_meta_data__operator_name', 'default_scan_meta_data__operator_name', self.operator_name_var),
            'operator_contact_var': ('last_scan_meta_data__contact', 'default_scan_meta_data__contact', self.operator_contact_var),
            'venue_name_var': ('last_scan_meta_data__name', 'default_scan_meta_data__name', self.venue_name_var), # Mapped to 'name'

            # NEW: Location variables
            'venue_postal_code_var': ('last_scan_meta_data__venue_postal_code', 'default_scan_meta_data__venue_postal_code', self.venue_postal_code_var),
            'address_field_var': ('last_scan_meta_data__address_field', 'default_scan_meta_data__address_field', self.address_field_var),
            'city_var': ('last_scan_meta_data__city', 'default_scan_meta_data__city', self.city_var),
            'province_var': ('last_scan_meta_data__province', 'default_scan_meta_data__province', self.province_var),
            'scanner_type_var': ('last_scan_meta_data__scanner_type', 'default_scan_meta_data__scanner_type', self.scanner_type_var),

            # NEW: Antenna and Amplifier variables
            'selected_antenna_type_var': ('last_scan_meta_data__selected_antenna_type', 'default_scan_meta_data__selected_antenna_type', self.selected_antenna_type_var),
            'antenna_description_var': ('last_scan_meta_data__antenna_description', 'default_scan_meta_data__antenna_description', self.antenna_description_var),
            'antenna_use_var': ('last_scan_meta_data__antenna_use', 'default_scan_meta_data__antenna_use', self.antenna_use_var),
            'antenna_mount_var': ('last_scan_meta_data__antenna_mount', 'default_scan_meta_data__antenna_mount', self.antenna_mount_var),
            'selected_amplifier_type_var': ('last_scan_meta_data__selected_amplifier_type', 'default_scan_meta_data__selected_amplifier_type', self.selected_amplifier_type_var),
            'antenna_amplifier_var': ('last_scan_meta_data__antenna_amplifier', 'default_scan_meta_data__antenna_amplifier', self.antenna_amplifier_var), # Still used to store the final selected amplifier
            'amplifier_description_var': ('last_scan_meta_data__amplifier_description', 'default_scan_meta_data__amplifier_description', self.amplifier_description_var), # NEW
            'amplifier_use_var': ('last_scan_meta_data__amplifier_use', 'default_scan_meta_data__amplifier_use', self.amplifier_use_var), # NEW

            'notes_var': ('last_scan_meta_data__notes', 'default_scan_meta_data__notes', self.notes_var),

            # NEW: Variables for persistent preset selection and its loaded details
            'last_selected_preset_name_var': ('last_instrument_preset__selected_preset_name', 'default_instrument_preset__selected_preset_name', self.last_selected_preset_name_var),
            'last_loaded_preset_center_freq_mhz_var': ('last_instrument_preset__loaded_preset_center_freq_mhz', 'default_instrument_preset__loaded_preset_center_freq_mhz', self.last_loaded_preset_center_freq_mhz_var),
            'last_loaded_preset_span_mhz_var': ('last_instrument_preset__loaded_preset_span_mhz', 'default_instrument_preset__loaded_preset_span_mhz', self.last_loaded_preset_span_mhz_var),
            'last_loaded_preset_rbw_hz_var': ('last_instrument_preset__loaded_preset_rbw_hz', 'default_instrument_preset__loaded_preset_rbw_hz', self.last_loaded_preset_rbw_hz_var),

            # Plotting variables (Scan Markers)
            'include_gov_markers_var': ('last_plotting__scan_markers_to_plot__include_gov_markers', 'default_plotting__scan_markers_to_plot__include_gov_markers', self.include_gov_markers_var),
            'include_tv_markers_var': ('last_plotting__scan_markers_to_plot__include_tv_markers', 'default_plotting__scan_markers_to_plot__include_tv_markers', self.include_tv_markers_var),
            'include_markers_var': ('last_plotting__scan_markers_to_plot__include_markers', 'default_plotting__scan_markers_to_plot__include_markers', self.include_markers_var),
            'include_scan_intermod_markers_var': ('last_plotting__scan_markers_to_plot__include_intermod_markers', 'default_plotting__scan_markers_to_plot__include_intermod_markers', self.include_scan_intermod_markers_var), # NEW
            'open_html_after_complete_var': ('last_plotting__scan_markers_to_plot__open_html_after_complete', 'default_plotting__scan_markers_to_plot__open_html_after_complete', self.open_html_after_complete_var),
            'create_html_var': ('last_plotting__scan_markers_to_plot__create_html', 'default_plotting__scan_markers_to_plot__create_html', self.create_html_var),

            # Plotting variables (Average Markers)
            'avg_include_gov_markers_var': ('last_plotting__average_markers_to_plot__include_gov_markers', 'default_plotting__average_markers_to_plot__include_gov_markers', self.avg_include_gov_markers_var),
            'avg_include_tv_markers_var': ('last_plotting__average_markers_to_plot__include_tv_markers', 'default_plotting__average_markers_to_plot__include_tv_markers', self.avg_include_tv_markers_var),
            'avg_include_markers_var': ('last_plotting__average_markers_to_plot__include_markers', 'default_plotting__average_markers_to_plot__include_markers', self.avg_include_markers_var),
            'avg_include_intermod_markers_var': ('last_plotting__average_markers_to_plot__include_intermod_markers', 'default_plotting__average_markers_to_plot__include_intermod_markers', self.avg_include_intermod_markers_var), # NEW
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
            # Each item in band_vars will be a dict: {"band": {...}, "var": tk.BooleanVar}
            band_var = tk.BooleanVar(self, value=False)
            # Add trace to band selection variables to save config
            band_var.trace_add("write", create_trace_callback(f"band_var_{band['Band Name']}"))
            self.band_vars.append({"band": band, "var": band_var})


    def _apply_saved_geometry(self, console_print_func=None):
        # Function Description:
        # Applies the window geometry saved in config.ini, or uses a default
        # if no saved geometry is found or if it's invalid.
        #
        # Inputs:
        #   console_print_func (function, optional): Function to use for console output.
        #
        # Process:
        #   1. Retrieves the window geometry from the 'LAST_USED_SETTINGS'
        #      section of the application's config, using a default fallback.
        #   2. Attempts to apply the retrieved geometry to the main window.
        #   3. If a `TclError` occurs (due to invalid geometry string),
        #      it logs the error and applies the hardcoded default geometry.
        #
        # Outputs:
        #   None. Sets the main window's size and position.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        # (2025-08-01) Change: Updated header and version.
        # (2025-08-01) Change: Updated debug prints to new format, including console_print_func.
        # (2025-08-01 1850.2) Change: No functional change.
        # (2025-08-01 1900.1) Change: No functional changes.
        # (2025-08-01 1900.2) Change: No functional changes.
        """
        Applies the window geometry saved in config.ini, or uses a default.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)

        # Use the new prefixed key for window geometry
        saved_geometry = self.config.get('LAST_USED_SETTINGS', 'last_GLOBAL__window_geometry', fallback=self.DEFAULT_WINDOW_GEOMETRY)
        try:
            self.geometry(saved_geometry)
            debug_print(f"Applied saved geometry: {saved_geometry}.",
                        file=f"{current_file} - {current_version}",
                        function=current_function,
                        console_print_func=console_print_func) # Conditionally pass console_print_func
        except TclError as e:
            debug_print(f"ERROR: Invalid saved geometry '{saved_geometry}': {e}. Using default.",
                        file=f"{current_file} - {current_version}",
                        function=current_function,
                        console_print_func=console_print_func) # Conditionally pass console_print_func
            self.geometry(self.DEFAULT_WINDOW_GEOMETRY)


    def _create_widgets(self):
        # Function Description:
        # Creates and arranges all GUI widgets in the main application window.
        # It sets up a two-column layout using ttk.PanedWindow for a resizable divider,
        # with parent tabs on the left and scan control/console on the right.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Configures the main window's grid to host the PanedWindow.
        #   3. Creates `self.main_panedwindow` for the resizable layout.
        #   4. Creates `self.parent_notebook` for the top-level parent tabs and adds it to the left pane.
        #   5. Instantiates and adds all `TAB_X_PARENT` classes to `self.parent_notebook`,
        #      storing references to parent tab widgets and their child notebooks.
        #   6. Binds the `<<NotebookTabChanged>>` event for the parent notebook.
        #   7. Creates `right_column_container` for the right pane and adds it to the PanedWindow.
        #   8. Instantiates `ScanControlTab` and places it in the right column.
        #   9. Creates and configures the "Application Console" scrolled text widget
        #      within the right column.
        #   10. Applies the saved sash position to the PanedWindow.
        #
        # Outputs:
        #   None. Populates the main window with GUI elements.
        #
        # (2025-07-31) Change: Implemented two-layer tab structure with parent and child notebooks.
        #                      Instantiated new parent tab classes and added them to the main notebook.
        #                      Adjusted child notebook references to point to the nested notebooks within parent tabs.
        # (2025-07-31) Change: Corrected typo in console_print_func argument for Markers Parent Tab.
        # (2025-07-31) Change: Applied specific styles to parent tabs for correct color display.
        # (2025-07-31) Change: Removed immediate notebook.tab() calls after add; initial color handled by _on_parent_tab_change.
        # (2025-07-31) Change: Storing parent tab instances as attributes of App for global access.
        # (2025-07-31) Change: Replaced fixed grid columns with ttk.PanedWindow for resizable divider.
        #                      Adjusted ScanControlTab's sticky option to expand horizontally.
        # (2025-07-31) Change: Applied saved sash position to the PanedWindow.
        # (2025-08-01) Change: Updated header and version.
        # (2025-08-01) Change: Removed 'style' argument from add() calls to fix TclError.
        # (2025-08-01) Change: Updated debug prints to new format, including console_print_func.
        # (2025-08-01 1850.2) Change: No functional change.
        # (2025-08-01 1900.1) Change: No functional changes.
        # (2025-08-01 1900.2) Change: No functional changes.
        """
        Creates and arranges all GUI widgets in the main application window,
        implementing a two-layer tab structure using parent tabs.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_print(f"Creating main application widgets with nested tabs...",
                    file=f"{current_file} - {current_version}",
                    function=current_function,
                    console_print_func=self._print_to_gui_console) # Added console_print_func

        # Configure grid for the main window - single row, single column for the PanedWindow
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- PanedWindow for resizable columns ---
        self.main_panedwindow = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_panedwindow.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # --- Left Column: Parent Notebook ---
        self.parent_notebook = ttk.Notebook(self.main_panedwindow, style='Parent.TNotebook')
        self.main_panedwindow.add(self.parent_notebook, weight=1) # Add to paned window, give it weight to expand

        # Dictionary to hold child notebooks for easy access in _on_tab_change
        self.child_notebooks = {}
        # Dictionary to hold parent tab widget instances for robust color setting
        self.parent_tab_widgets = {}

        # Parent Tab Colors (as requested)
        # These constants are now primarily used for the *child* notebook backgrounds
        # and for the common active/inactive colors of the parent tabs.
        PARENT_INSTRUMENT_ACTIVE = "#FF0000"
        PARENT_INSTRUMENT_INACTIVE = "#660C0C"
        PARENT_SCANNING_ACTIVE = "#FF6600"
        PARENT_SCANNING_INACTIVE = "#926002"
        PARENT_PLOTTING_ACTIVE = "#D1D10E"
        PARENT_PLOTTING_INACTIVE = "#72720A"
        PARENT_MARKERS_ACTIVE = "#319131"
        PARENT_MARKERS_INACTIVE = "#1B4B1B"
        PARENT_PRESETS_ACTIVE = "#0303C9"
        PARENT_PRESETS_INACTIVE = "#00008B"
        ACCENT_PURPLE = "#6f42c1"
        PARENT_EXPERIMENTS_ACTIVE = ACCENT_PURPLE
        PARENT_EXPERIMENTS_INACTIVE = "#4d2482"

        # Store parent tab color mappings for dynamic updates
        # These colors are used for the *child notebook backgrounds*
        # and for the child notebook tabs.
        self.parent_tab_colors = {
            "INSTRUMENT": {"active": PARENT_INSTRUMENT_ACTIVE, "inactive": PARENT_INSTRUMENT_INACTIVE, "fg_active": "white", "fg_inactive": "#cccccc"},
            "SCANNING": {"active": PARENT_SCANNING_ACTIVE, "inactive": PARENT_SCANNING_INACTIVE, "fg_active": "white", "fg_inactive": "#cccccc"},
            "PLOTTING": {"active": PARENT_PLOTTING_ACTIVE, "inactive": PARENT_PLOTTING_INACTIVE, "fg_active": "black", "fg_inactive": "#cccccc"},
            "MARKERS": {"active": PARENT_MARKERS_ACTIVE, "inactive": PARENT_MARKERS_INACTIVE, "fg_active": "black", "fg_inactive": "#cccccc"},
            "PRESETS": {"active": PARENT_PRESETS_ACTIVE, "inactive": PARENT_PRESETS_INACTIVE, "fg_active": "white", "fg_inactive": "#cccccc"},
            "EXPERIMENTS": {"active": PARENT_EXPERIMENTS_ACTIVE, "inactive": PARENT_EXPERIMENTS_INACTIVE, "fg_active": "white", "fg_inactive": "#cccccc"},
        }


        # Instantiate and add parent tabs, storing widget references as App attributes
        # Removed 'style' argument from add() calls as it's not supported directly for tab labels.
        # Initial styling will be handled by _on_parent_tab_change.
        self.instrument_parent_tab = TAB_INSTRUMENT_PARENT(self.parent_notebook, app_instance=self, console_print_func=self._print_to_gui_console)
        self.parent_notebook.add(self.instrument_parent_tab, text="INSTRUMENT")
        self.child_notebooks["INSTRUMENT"] = self.instrument_parent_tab.child_notebook
        self.parent_tab_widgets["INSTRUMENT"] = self.instrument_parent_tab # Store widget reference

        self.scanning_parent_tab = TAB_SCANNING_PARENT(self.parent_notebook, app_instance=self, console_print_func=self._print_to_gui_console)
        self.parent_notebook.add(self.scanning_parent_tab, text="SCANNING")
        self.child_notebooks["SCANNING"] = self.scanning_parent_tab.child_notebook
        self.parent_tab_widgets["SCANNING"] = self.scanning_parent_tab # Store widget reference

        self.plotting_parent_tab = TAB_PLOTTING_PARENT(self.parent_notebook, app_instance=self, console_print_func=self._print_to_gui_console)
        self.parent_notebook.add(self.plotting_parent_tab, text="PLOTTING")
        self.child_notebooks["PLOTTING"] = self.plotting_parent_tab.child_notebook
        self.parent_tab_widgets["PLOTTING"] = self.plotting_parent_tab # Store widget reference

        self.markers_parent_tab = TAB_MARKERS_PARENT(self.parent_notebook, app_instance=self, console_print_func=self._print_to_gui_console)
        self.parent_notebook.add(self.markers_parent_tab, text="MARKERS")
        self.child_notebooks["MARKERS"] = self.markers_parent_tab.child_notebook
        self.parent_tab_widgets["MARKERS"] = self.markers_parent_tab # Store widget reference

        self.presets_parent_tab = TAB_PRESETS_PARENT(self.parent_notebook, app_instance=self, console_print_func=self._print_to_gui_console)
        self.parent_notebook.add(self.presets_parent_tab, text="PRESETS")
        self.child_notebooks["PRESETS"] = self.presets_parent_tab.child_notebook
        self.parent_tab_widgets["PRESETS"] = self.presets_parent_tab # Store widget reference

        self.experiments_parent_tab = TAB_EXPERIMENTS_PARENT(self.parent_notebook, app_instance=self, console_print_func=self._print_to_gui_console)
        self.parent_notebook.add(self.experiments_parent_tab, text="EXPERIMENTS")
        self.child_notebooks["EXPERIMENTS"] = self.experiments_parent_tab.child_notebook
        self.parent_tab_widgets["EXPERIMENTS"] = self.experiments_parent_tab # Store widget reference


        # Bind parent tab selection event
        self.parent_notebook.bind("<<NotebookTabChanged>>", self._on_parent_tab_change)


        # --- Right Column Container Frame ---
        # This frame is now added to the main_panedwindow
        right_column_container = ttk.Frame(self.main_panedwindow, style='Dark.TFrame')
        self.main_panedwindow.add(right_column_container, weight=1) # Add to paned window, give it weight to expand
        right_column_container.grid_columnconfigure(0, weight=1)
        right_column_container.grid_rowconfigure(0, weight=0) # Scan Control row
        right_column_container.grid_rowconfigure(1, weight=1) # Console row


        # --- Application Console Frame (Moved into right_column_container) ---
        # Initialize self.console_text here where it's actually created
        console_frame = ttk.LabelFrame(right_column_container, text="Application Console", style='Dark.TLabelframe')
        console_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        console_frame.grid_rowconfigure(0, weight=1)
        console_frame.grid_columnconfigure(0, weight=1)

        self.console_text = scrolledtext.ScrolledText(console_frame, wrap="word", bg="#2b2b2b", fg="#cccccc", insertbackground="white")
        self.console_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.console_text.config(state=tk.DISABLED)

        # --- Scan Control Buttons Frame (Moved into right_column_container) ---
        self.scan_control_tab = ScanControlTab(right_column_container, app_instance=self, console_print_func=self._print_to_gui_console)
        # Changed sticky to "nsew" to make it expand in all directions, especially horizontally
        self.scan_control_tab.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")


        # Apply the saved sash position after all widgets are added to the paned window
        # Ensure the value is within reasonable bounds (e.g., not zero, not exceeding window width)
        sash_pos = self.paned_window_sash_position_var.get()
        if sash_pos > 0: # Avoid setting to 0 which can hide a pane
            self.main_panedwindow.sashpos(0, sash_pos)
            debug_print(f"Applied saved PanedWindow sash position: {sash_pos}.",
                        file=f"{current_file} - {current_version}",
                        function=current_function,
                        console_print_func=self._print_to_gui_console) # Added console_print_func
        else:
            debug_print(f"WARNING: Invalid saved PanedWindow sash position: {sash_pos}. Using default.",
                        file=f"{current_file} - {current_version}",
                        function=current_function,
                        console_print_func=self._print_to_gui_console) # Added console_print_func


        debug_print(f"Main application widgets created.",
                    file=f"{current_file} - {current_version}",
                    function=current_function,
                    console_print_func=self._print_to_gui_console) # Added console_print_func


    def _setup_styles(self):
        # Function Description:
        # Configures and applies custom ttk styles for a modern dark theme
        # to various Tkinter widgets within the application. This includes
        # defining styles for parent and child notebooks to support the
        # two-layer tab structure with unique and dynamic colors for parent tabs.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Calls the external `apply_styles` function from `src.style`
        #      to apply all centralized style configurations.
        #
        # Outputs:
        #   None. Applies visual styling to the application's GUI.
        #
        # (2025-08-01) Change: Refactored all ttk.Style definitions from _setup_styles method
        #                      into a new external file: src/style.py.
        #                      This method now simply calls apply_styles from src.style.py.
        # (25-08-01) Change: Fixed AttributeError by passing the imported 'debug_print' function
        #                      directly instead of 'self.debug_print'.
        # (2025-08-01) Change: Updated debug prints to new format, including console_print_func.
        # (2025-08-01 1850.2) Change: No functional change.
        # (2025-08-01 1900.1) Change: No functional changes.
        # (2025-08-01 1900.2) Change: No functional changes.
        """
        Configures and applies custom ttk styles for a modern dark theme,
        including styles for nested tabs.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_print(f"Setting up ttk styles...",
                    file=f"{current_file} - {current_version}",
                    function=current_function,
                    console_print_func=self._print_to_gui_console) # Added console_print_func
        # self.style is now an instance attribute, initialized in __init__
        # Pass the parent_tab_colors dictionary to apply_styles
        apply_styles(self.style, debug_print, current_version, self.parent_tab_colors)


    def _redirect_stdout_to_console(self):
        # Function Description:
        # Redirects standard output and error streams to the GUI's scrolled text widget.
        # This allows all `print()` statements and error messages to appear in the
        # application's console area.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Reassigns `sys.stdout` and `sys.stderr` to instances of `TextRedirector`,
        #      which directs output to `self.console_text`.
        #   3. Prints an initial message to the console to confirm initialization.
        #
        # Outputs:
        #   None. Modifies global system streams.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        # (2025-08-01) Change: Updated header and version.
        # (2025-08-01) Change: Updated debug prints to new format, including console_print_func.
        # (2025-08-01 1850.2) Change: No functional change.
        # (2025-08-01 1900.1) Change: No functional changes.
        # (2025-08-01 1900.2) Change: No functional changes.
        """
        Redirects standard output and error streams to the GUI's scrolled text widget.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_print(f"Redirecting stdout/stderr to GUI console...",
                    file=f"{current_file} - {current_version}",
                    function=current_function,
                    console_print_func=self._print_to_gui_console) # Added console_print_func
        sys.stdout = TextRedirector(self.console_text, "stdout")
        sys.stderr = TextRedirector(self.console_text, "stderr") # Fix: Corrected to TextRedirector

        self._print_to_gui_console(f"Application console initialized. Version: {current_version}")
        debug_print(f"Console redirection complete.",
                    file=f"{current_file} - {current_version}",
                    function=current_function,
                    console_print_func=self._print_to_gui_console) # Added console_print_func


    def _on_closing(self):
        # Function Description:
        # Handles the application closing event.
        # It attempts to save the current configuration and gracefully
        # disconnect from the instrument before destroying the main window.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Prints a debug message indicating application shutdown.
        #   2. Attempts to save the current configuration to `config.ini`.
        #   3. Calls `disconnect_instrument_logic` to ensure the instrument is properly
        #      released, if connected.
        #   4. Destroys the main Tkinter window.
        #
        # Outputs:
        #   None. Closes the application.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        # (2025-08-01) Change: Updated header and version.
        # (2025-08-01) Change: Updated debug prints to new format, including console_print_func.
        # (2025-08-01 1850.2) Change: No functional change.
        # (2025-08-01 1900.1) Change: No functional changes.
        # (2025-08-01 1900.2) Change: No functional changes.
        """
        Handles the application closing event, saving configuration and disconnecting.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_print(f"Application is shutting down. Saving configuration...",
                    file=f"{current_file} - {current_version}",
                    function=current_function,
                    console_print_func=self._print_to_gui_console) # Added console_print_func

        # Save the current sash position before closing
        # Ensure self.main_panedwindow exists before trying to get its sash position
        if hasattr(self, 'main_panedwindow') and self.main_panedwindow.winfo_exists():
            sash_pos = self.main_panedwindow.sashpos(0)
            self.paned_window_sash_position_var.set(sash_pos)
            debug_print(f"Saved final sash position: {sash_pos}.",
                        file=f"{current_file} - {current_version}",
                        function=current_function,
                        console_print_func=self._print_to_gui_console) # Added console_print_func


        # FUCKING IMPORTANT: Pass the config object, file path, and console print func to save_config
        save_config(self.config, self.CONFIG_FILE_PATH, self._print_to_gui_console, self) # Corrected call to include app_instance

        if self.inst:
            debug_print(f"Disconnecting instrument before exit.",
                        file=f"{current_file} - {current_version}",
                        function=current_function,
                        console_print_func=self._print_to_gui_console) # Added console_print_func
            disconnect_instrument_logic(self, self._print_to_gui_console) # Pass app_instance and console_print_func

        self.destroy() # Destroy the main window


    def _print_to_gui_console(self, message):
        # Function Description:
        # Prints a message to the GUI's scrolled text console.
        # This function is used as the `console_print_func` argument
        # passed to various utility and logic functions, ensuring all
        # relevant output is displayed in the GUI.
        #
        # Inputs:
        #   message (str): The string message to print.
        #
        # Process:
        #   1. Checks if `self.console_text` (the scrolled text widget) exists.
        #   2. If it exists, enables the widget, inserts the message with a newline,
        #      scrolls to the end, and then disables the widget.
        #   3. If it doesn't exist (e.g., during early startup), it falls back to `print()`.
        #
        # Outputs:
        #   None. Displays text in the GUI console.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        # (2025-08-01) Change: Updated header and version.
        # (2025-08-01) Change: Fixed AttributeError by ensuring self.console_text exists
        #                      before attempting to write to it.
        # (2025-08-01) Change: Updated debug prints to new format, including console_print_func.
        # (2025-08-01 1850.2) Change: No functional change.
        # (2025-08-01 1900.1) Change: No functional changes.
        # (2025-08-01 1900.2) Change: No functional changes.
        """
        Prints a message to the GUI's scrolled text console.
        """
        if self.console_text:
            self.console_text.config(state=tk.NORMAL)
            self.console_text.insert(tk.END, message + "\n")
            self.console_text.see(tk.END)
            self.console_text.config(state=tk.DISABLED)
        else:
            # Fallback to standard print if console_text is not yet initialized
            print(f"[CONSOLE_FALLBACK] {message}")


    def _ensure_data_directory_exists(self, console_print_func=None):
        # Function Description:
        # Ensures that the 'DATA' directory exists at the specified `self.DATA_FOLDER_PATH`.
        # If the directory does not exist, it attempts to create it. This is crucial
        # for storing configuration files, scan data, and other application-related files.
        #
        # Inputs to this function:
        #   None (operates on self.DATA_FOLDER_PATH).
        #
        # Process of this function:
        #   1. Prints a debug message indicating the attempt to create the directory.
        #   2. Uses `os.makedirs` with `exist_ok=True` to create the directory.
        #      `exist_ok=True` prevents an error if the directory already exists (e.g., due to a race condition).
        #   3. Prints informative messages to the console about the directory status.
        #   4. Includes error handling for potential issues during directory creation.
        #
        # Outputs of this function:
        #   None. Ensures the 'DATA' directory is available for file operations.
        #
        # (2025-08-01) Change: New function to create the DATA folder.
        # (2025-08-01 1850.2) Change: No functional change.
        # (2025-08-01 1900.1) Change: No functional changes.
        # (2025-08-01 1900.2) Change: No functional changes.
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_print(f"Ensuring DATA directory exists at: {self.DATA_FOLDER_PATH}.",
                    file=f"{current_file} - {current_version}",
                    function=current_function,
                    console_print_func=console_print_func)

        try:
            os.makedirs(self.DATA_FOLDER_PATH, exist_ok=True)
            if console_print_func:
                self._print_to_gui_console(f"✅ DATA directory ensured at: {self.DATA_FOLDER_PATH}")
            debug_print(f"DATA directory created or already exists.",
                        file=f"{current_file} - {current_version}",
                        function=current_function,
                        console_print_func=console_print_func)
        except Exception as e:
            if console_print_func:
                self._print_to_gui_console(f"❌ Error creating DATA directory at {self.DATA_FOLDER_PATH}: {e}")
            debug_print(f"ERROR: Error creating DATA directory: {e}",
                        file=f"{current_file} - {current_version}",
                        function=current_function,
                        console_print_func=console_print_func)


    def update_connection_status(self, is_connected):
        # Function Description:
        # This function updates the state (enabled/disabled) of various GUI elements
        # across different tabs based on the instrument's connection status and
        # whether a scan is currently in progress. It ensures that only relevant
        # actions are available to the user at any given time.
        #
        # Inputs:
        #   is_connected (bool): True if the instrument is connected, False otherwise.
        #   is_scanning (bool): True if a scan is active, False otherwise.
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Calls `update_connection_status_logic` (from `src.scan_logic`) to
        #      handle the core logic of enabling/disabling widgets. This centralizes
        #      the UI state management.
        #   3. Passes references to all relevant tabs and their child tabs.
        #
        # Outputs:
        #   None. Modifies the state of GUI widgets.
        #
        # (2025-07-30) Change: Updated to pass all new tab instances (ScanConfig, ScanMetaData, Plotting, Markers, Presets).
        # (2025-07-31) Change: Updated to pass new nested tab structure to `update_connection_status_logic`.
        #                      Now passes parent tab instances, which then expose their child tabs.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        # (2025-08-01) Change: Updated header and version.
        # (2025-08-01) Change: Fixed AttributeError by ensuring correct tab attribute names are passed.
        #                      Specifically, changed `instrument_presets_tab` to `preset_files_tab`.
        # (2025-08-01) Change: Fixed AttributeError: 'TAB_PLOTTING_PARENT' object has no attribute 'plotting_tab'.
        #                      Corrected access to child tab within TAB_PLOTTING_PARENT.
        # (2025-08-01) Change: Fixed AttributeError: 'TAB_INSTRUMENT_PARENT' object has no attribute 'visa_interpreter_tab'.
        #                      Instantiated VisaInterpreterTab and assigned it as an attribute.
        # (2025-08-01) Change: Removed 'is_scanning' argument from the call to update_connection_status_logic.
        # (2025-08-01 1807.9) Change: Fixed TypeError: update_connection_status_logic() got an unexpected keyword argument 'instrument_tab' by passing specific child tab instances.
        # (2025-08-01 1807.10) Change: Fixed TypeError: update_connection_status_logic() got an unexpected keyword argument 'instrument_connection_tab' by simplifying arguments passed to the function.
        # (2025-08-01 1850.2) Change: No functional change.
        # (2025-08-01 1900.1) Change: No functional changes.
        # (2025-08-01 1900.2) Change: No functional changes.
        """
        Updates the state of various GUI elements based on connection and scan status.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_print(f"Updating connection status. Connected: {is_connected}.",
                    file=f"{current_file} - {current_version}",
                    function=current_function,
                    console_print_func=self._print_to_gui_console) # Added console_print_func

        # This central logic function now only takes the main app_instance
        # and the connection status. It should access all necessary tabs
        # and their widgets through the app_instance object.
        update_connection_status_logic(
            app_instance=self, # Pass the main app instance
            is_connected=is_connected,
            console_print_func=self._print_to_gui_console
        )


    def _on_parent_tab_change(self, event):
        # Function Description:
        # Handles the event when a parent tab is changed in the main notebook.
        # It updates the visual style of the newly selected tab (making it active)
        # and the previously selected tab (making it inactive). It also propagates
        # the tab selection event to the active child tab within the newly selected
        # parent tab, if that child tab has an `_on_tab_selected` method.
        #
        # Inputs:
        #   event (tkinter.Event): The event object that triggered the tab change.
        #                          Can be None during initial startup.
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Determines the currently selected parent tab's ID and widget.
        #   3. Iterates through all parent tabs:
        #      a. For each tab, it determines if it's the currently selected one.
        #      b. Applies the appropriate 'active' or 'inactive' style to the tab.
        #         Note: Direct 'background' and 'foreground' options are not supported
        #         by ttk.Notebook.tab(). Styling is handled via ttk.Style configurations
        #         for 'TNotebook.Tab' elements.
        #   4. If a child notebook exists for the newly selected parent tab,
        #      it identifies the currently active child tab within that notebook.
        #   5. If the active child tab has an `_on_tab_selected` method, it calls it,
        #      allowing the child tab to refresh its content or state.
        #
        # Outputs:
        #   None. Updates parent tab visual styles and triggers child tab updates.
        #
        # (2025-07-31) Change: Initial creation to handle parent tab style changes.
        #                      Implemented logic to set active/inactive colors.
        # (2025-07-31) Change: Propagated _on_tab_selected to active child tab.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        # (2025-08-01) Change: Updated header and version.
        # (2025-08-01) Change: Corrected ValueError by using tab_widget.winfo_name() to identify tab.
        #                      Fixed TclError by passing widget directly to notebook.tab().
        # (2025-08-01) Change: Fixed TclError: unknown option "-style" when applying style to parent tabs.
        #                      Now retrieves background and foreground from the style and applies them directly.
        # (2025-08-01 1850.2) Change: No functional change.
        # (2025-08-01 1900.1) Change: No functional changes.
        # (2025-08-01 1900.2) Change: Removed invalid 'background' and 'foreground' arguments from parent_notebook.tab() call to fix TclError.
        #                             Reliance on ttk.Style mapping for tab appearance.
        """
        Handles parent tab changes, updates styles, and propagates to active child tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_print(f"Parent tab changed.",
                    file=f"{current_file} - {current_version}",
                    function=current_function,
                    console_print_func=self._print_to_gui_console) # Added console_print_func

        # Get the currently selected parent tab widget
        selected_tab_id = self.parent_notebook.select()
        selected_tab_widget = self.parent_notebook.nametowidget(selected_tab_id)
        selected_tab_text = self.parent_notebook.tab(selected_tab_id, "text")


        # Update styles for all parent tabs
        for tab_name, tab_widget in self.parent_tab_widgets.items():
            # Determine the style name based on whether it's the selected tab
            if tab_name == selected_tab_text:
                style_name = f'Parent.Tab.{tab_name}.Active'
            else:
                style_name = f'Parent.Tab.{tab_name}.Inactive'
            
            # NOTE: ttk.Notebook.tab() does NOT support 'background' or 'foreground'
            # as direct options for the tab label. These are controlled by the ttk.Style
            # configuration for the 'TNotebook.Tab' element.
            # The style.lookup() calls here are correct for retrieving the colors,
            # but applying them directly via parent_notebook.tab() is incorrect
            # and causes the TclError.
            # The dynamic coloring should be handled by the style definitions in src/style.py
            # using style.map() for the 'selected' and '!selected' states of the TNotebook.Tab.
            
            # The following lines are removed to fix the TclError:
            # try:
            #     bg_color = self.style.lookup(style_name, "background")
            #     fg_color = self.style.lookup(style_name, "foreground")
            #     self.parent_notebook.tab(tab_widget, background=bg_color, foreground=fg_color)
            #     debug_print(f"Applied colors (BG: {bg_color}, FG: {fg_color}) to parent tab '{tab_name}' using style '{style_name}'.",
            #                 file=f"{current_file} - {current_version}",
            #                 function=current_function,
            #                 console_print_func=self._print_to_gui_console)
            # except TclError as e:
            #     debug_print(f"❌ TclError applying colors to parent tab '{tab_name}' with style '{style_name}': {e}. This is some bullshit!",
            #                 file=f"{current_file} - {current_version}",
            #                 function=current_function,
            #                 console_print_func=self._print_to_gui_console)
            # except Exception as e:
            #     debug_print(f"❌ An unexpected error occurred while applying colors to parent tab '{tab_name}': {e}. What the hell is going on?!",
            #                 file=f"{current_file} - {current_version}",
            #                 function=current_function,
            #                 console_print_func=self._print_to_gui_console)
            
            # Instead, we rely on the style system to apply the correct appearance based on selection.
            # Ensure the tab's style is set if the notebook.tab method supports it (it doesn't for the label itself).
            # The default ttk.Notebook should handle the 'selected' state visually if the styles are mapped correctly.
            pass # No direct tab styling here to avoid TclError


        # Propagate _on_tab_selected to the currently active child tab within the selected parent tab
        if selected_tab_text in self.child_notebooks:
            active_child_notebook = self.child_notebooks[selected_tab_text]
            selected_child_tab_id = active_child_notebook.select()
            if selected_child_tab_id:
                selected_child_tab_widget = active_child_notebook.nametowidget(selected_child_tab_id)
                if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                    selected_child_tab_widget._on_tab_selected(event)
                    debug_print(f"Propagated _on_tab_selected to active child tab: {selected_child_tab_widget.winfo_class()} in parent '{selected_tab_text}'.",
                                file=f"{current_file} - {current_version}",
                                function=current_function,
                                console_print_func=self._print_to_gui_console) # Added console_print_func
                else:
                    debug_print(f"Active child tab {selected_child_tab_widget.winfo_class()} in parent '{selected_tab_text}' has no _on_tab_selected method.",
                                file=f"{current_file} - {current_version}",
                                function=current_function,
                                console_print_func=self._print_to_gui_console) # Added console_print_func
            else:
                debug_print(f"No child tab selected in parent '{selected_tab_text}'.",
                            file=f"{current_file} - {current_version}",
                            function=current_function,
                            console_print_func=self._print_to_gui_console) # Added console_print_func
        else:
            debug_print(f"No child notebook found for parent tab '{selected_tab_text}'.",
                        file=f"{current_file} - {current_version}",
                        function=current_function,
                        console_print_func=self._print_to_gui_console) # Added console_print_func


if __name__ == "__main__":
    app = App()
    app.mainloop()
