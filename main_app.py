# OPEN-AIR/main_app.py
#
# This is the main entry point for the RF Spectrum Analyzer Controller application.
# It handles initial setup, checks for and installs necessary Python dependencies,
# and then launches the main graphical user interface (GUI).
# This file ensures that the application environment is ready before starting the UI.
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
# Version 20250801.1005.1 (Corrected import paths for numbered subfolders in 'tabs')

current_version = "20250801.1005.1" # this variable should always be defined below the header to make the debugging better

import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, TclError, ttk
import os
import sys
import threading
import time
import pyvisa
import configparser
import inspect
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

from utils.utils_instrument_control import set_debug_mode, set_log_visa_commands_mode, debug_print

# Import the new parent tab classes - CORRECTED PATHS
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
    CONFIG_FILE = os.path.join(_script_dir, 'config.ini')

    DEFAULT_WINDOW_GEOMETRY = "1400x780+100+100" # This is now a fallback, actual default comes from config

    def __init__(self):
        # Initializes the main application window and sets up core components.
        # It performs dependency checks, initializes instrument communication,
        # sets up Tkinter variables, loads configuration, creates UI widgets,
        # applies styling, and redirects console output.
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
        #   14. Calls `_create_widgets` to build the GUI.
        #   15. Calls `_setup_styles` to apply custom themes.
        #   16. Redirects stdout to the GUI console.
        #   17. Updates connection status.
        #   18. Prints application art.
        #   19. Loads band selections for ScanTab (now nested).
        #   20. Manually updates notes text widget on ScanMetaDataTab (now nested).
        #   21. Sets `is_ready_to_save` to True.
        #
        # Outputs:
        #   None. Initializes the main application object.
        #
        # (2025-07-30) Change: Updated to initialize new Tkinter variables for Scan Meta Data tab.
        # (2025-07-30) Change: Initialized new Tkinter StringVars for persistent preset selection and loaded details.
        # (2025-07-31) Change: No functional change, just updated header.
        # (2025-07-31) Change: Updated window title to "OPEN AIR - RF Spectrum Analyzer".
        # (2025-07-31) Change: Adjusted startup calls for band selections and notes to new nested tab structure.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Added initialization for paned_window_sash_position_var.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        super().__init__()
        self.title("OPEN AIR - 🌐📡🗺️ - Zone Awareness Processor") # Changed window title
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.config = configparser.ConfigParser()

        self.is_ready_to_save = False

        self._check_and_install_dependencies()

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

        self._setup_tkinter_vars() # Initialize Tkinter variables BEFORE loading config

        load_config(self) # Now load_config will find the variables and populate them
        self._apply_saved_geometry()

        # Initialize self.style BEFORE _create_widgets is called
        self.style = ttk.Style(self) # Make style an instance attribute

        # These calls now use the Tkinter variables directly, which are populated by load_config
        set_debug_mode(self.general_debug_enabled_var.get())
        set_log_visa_commands_mode(self.log_visa_commands_enabled_var.get())

        self._create_widgets()
        self._setup_styles() # This will now configure self.style
        self._redirect_stdout_to_console()

        # Call _on_parent_tab_change to set initial tab colors after all widgets are created
        # Pass a dummy event as it's not triggered by a user action
        self._on_parent_tab_change(None)

        # Initial update of connection status. This will now correctly access the tab instances.
        self.update_connection_status(self.inst is not None)

        print_art()

        # Adjusted startup calls for band selections and notes to new nested tab structure
        if hasattr(self, 'scanning_parent_tab') and hasattr(self.scanning_parent_tab, 'scan_configuration_tab'):
            self.scanning_parent_tab.scan_configuration_tab._load_band_selections_from_config()
            debug_print(f"🚫🐛 [DEBUG] Called _load_band_selections_from_config on Scan Configuration Tab during startup. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)

        if hasattr(self, 'scanning_parent_tab') and hasattr(self.scanning_parent_tab, 'scan_meta_data_tab'):
            self.scanning_parent_tab.scan_meta_data_tab.notes_text_widget.delete("1.0", tk.END)
            self.scanning_parent_tab.scan_meta_data_tab.notes_text_widget.insert("1.0", self.notes_var.get())
            debug_print(f"🚫🐛 [DEBUG] Updated notes_text_widget on Scan Meta Data Tab during startup. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)


        self.is_ready_to_save = True
        debug_print(f"🚫🐛 [DEBUG] Application fully initialized and ready to save configuration. Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)


    def _check_and_install_dependencies(self):
        # Checks for necessary Python packages (pyvisa, pandas, beautifulsoup4, pdfplumber, requests)
        # and attempts to install them if missing. If packages are missing and the user agrees,
        # it installs them and then exits the application, prompting for a restart.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Defines a dictionary of required dependencies (import name: package name).
        #   2. Iterates through the dependencies, attempting to import each.
        #   3. If an ImportError occurs, adds the package name to a `missing_dependencies` list.
        #   4. If `missing_dependencies` is not empty, prompts the user to install them.
        #   5. If the user agrees, attempts to install using `pip`.
        #   6. Shows success/failure messages and exits the application if installation occurs
        #      or if the user declines installation.
        #
        # Outputs:
        #   None. May exit the application if dependencies are missing or installed.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        Checks for necessary Python packages (pyvisa, pandas, beautifulsoup4, pdfplumber, requests)
        and attempts to install them if missing.
        """
        dependencies = {
            "pyvisa": "pyvisa",
            "pandas": "pandas",
            "bs4": "beautifulsoup4", # For BeautifulSoup
            "pdfplumber": "pdfplumber",
            "requests": "requests" # Added requests to the dependency check
        }
        missing_dependencies = []

        for import_name, package_name in dependencies.items():
            try:
                __import__(import_name)
            except ImportError:
                missing_dependencies.append(package_name)

        if missing_dependencies:
            missing_str = ", ".join(missing_dependencies)
            response = messagebox.askyesno(
                "Missing Dependencies",
                f"The following Python packages are missing: {missing_str}.\n"
                "Do you want to install them now? This may take a few moments."
            )
            if response:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_dependencies])
                    messagebox.showinfo("Installation Complete", "Required packages installed successfully. Please restart the application.")
                    sys.exit(0) # Exit to restart application
                except Exception as e:
                    messagebox.showerror("Installation Failed", f"Failed to install packages: {e}\nPlease install them manually using 'pip install {missing_str}'")
                    sys.exit(1) # Exit if user chooses not to install
            else:
                messagebox.showwarning("Dependencies Missing", "Application may not function correctly without required packages.")
                sys.exit(1) # Exit if user chooses not to install


    def _setup_tkinter_vars(self):
        # Initializes all Tkinter variables used throughout the application.
        # It creates StringVars, IntVars, and BooleanVars, and adds trace listeners
        # to them. These trace listeners automatically trigger the `save_config`
        # function whenever a variable's value changes, ensuring settings are persisted.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Defines a helper function `create_trace_callback` that returns a
        #      closure to save configuration when a variable changes, but only
        #      if the application is fully initialized.
        #   2. Initializes global application variables (e.g., debug settings).
        #   3. Initializes instrument connection variables.
        #   4. Initializes scan configuration variables.
        #   5. Initializes scan meta data variables, including new ones for
        #      location lookup results and detailed antenna/amplifier properties.
        #   6. Initializes plotting variables for both single scan and average plots.
        #   7. Initializes new variables for persistent preset selection and its details.
        #   8. Creates a `setting_var_map` dictionary that maps each Tkinter variable
        #      to its corresponding keys in the `config.ini` file (last used and default).
        #   9. Initializes `band_vars` for frequency band selections, adding traces.
        #
        # Outputs:
        #   None. Populates `self` with Tkinter variables and `setting_var_map`.
        #
        # (2025-07-30) Change: Added new Tkinter variables for Venue Postal Code, Address Field, Province,
        #                      Selected Antenna Type, Antenna Description, Antenna Use, Antenna Mount,
        #                      and Selected Amplifier Type. Updated `setting_var_map` accordingly.
        # (2025-07-30) Change: Verified and ensured all relevant Tkinter StringVars have trace listeners for auto-saving.
        # (2025-07-30) Change: Added new Tkinter StringVars for persistent preset selection and loaded details.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Added paned_window_sash_position_var and added it to setting_var_map.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        Initializes Tkinter variables for all application settings,
        mapping them to their corresponding keys in config.ini using the new prefixed style.
        Also adds trace listeners to trigger config saving on changes.
        """
        # Define a helper function to add trace for saving config
        def create_trace_callback(var_name):
            def callback(*args):
                # Only save if the app is fully initialized to avoid saving partial states during startup
                if self.is_ready_to_save:
                    debug_print(f"🚫🐛 [DEBUG] Tkinter variable '{var_name}' changed. Saving config. Version: {current_version}",
                                file=f"main_app.py - {current_version}",
                                function=inspect.currentframe().f_code.co_name)
                    save_config(self)
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

        self.output_folder_var = tk.StringVar(self, value="scan_data")
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


            'include_gov_markers_var': ('last_plotting__scan_markers_to_plot__include_gov_markers', 'default_plotting__scan_markers_to_plot__include_gov_markers', self.include_gov_markers_var),
            'include_tv_markers_var': ('last_plotting__scan_markers_to_plot__include_tv_markers', 'default_plotting__scan_markers_to_plot__include_tv_markers', self.include_tv_markers_var),
            'include_markers_var': ('last_plotting__scan_markers_to_plot__include_markers', 'default_plotting__scan_markers_to_plot__include_markers', self.include_markers_var),
            'include_scan_intermod_markers_var': ('last_plotting__scan_markers_to_plot__include_intermod_markers', 'default_plotting__scan_markers_to_plot__include_intermod_markers', self.include_scan_intermod_markers_var), # NEW
            'open_html_after_complete_var': ('last_plotting__scan_markers_to_plot__open_html_after_complete', 'default_plotting__scan_markers_to_plot__open_html_after_complete', self.open_html_after_complete_var),
            'create_html_var': ('last_plotting__scan_markers_to_plot__create_html', 'default_plotting__scan_markers_to_plot__create_html', self.create_html_var),

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


    def _apply_saved_geometry(self):
        # Applies the window geometry saved in config.ini, or uses a default
        # if no saved geometry is found or if it's invalid.
        #
        # Inputs:
        #   None (operates on self).
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
        """
        Applies the window geometry saved in config.ini, or uses a default.
        """
        # Use the new prefixed key for window geometry
        saved_geometry = self.config.get('LAST_USED_SETTINGS', 'last_GLOBAL__window_geometry', fallback=self.DEFAULT_WINDOW_GEOMETRY)
        try:
            self.geometry(saved_geometry)
            debug_print(f"🚫🐛 [DEBUG] Applied saved geometry: {saved_geometry}. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)
        except TclError as e:
            debug_print(f"🚫🐛 [ERROR] Invalid saved geometry '{saved_geometry}': {e}. Using default. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)
            self.geometry(self.DEFAULT_WINDOW_GEOMETRY)


    def _create_widgets(self):
        # Creates and arranges all GUI widgets in the main application window.
        # It sets up a two-column layout using ttk.Notebook for parent tabs on the left
        # which then contain nested ttk.Notebooks for child tabs, and a container
        # for scan control and console on the right.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Configures the main window's grid to have two columns.
        #   3. Creates `self.parent_notebook` for the top-level parent tabs.
        #   4. For each parent category (INSTRUMENT, SCANNING, MARKERS, PRESETS, EXPERIMENTS):
        #      a. Instantiates the corresponding `TAB_X_PARENT` class.
        #      b. Adds this parent tab instance to `self.parent_notebook`.
        #      c. Stores a reference to the child notebook within the parent tab for easy access.
        #   5. Binds the `<<NotebookTabChanged>>` event to `_on_parent_tab_change` for the parent notebook.
        #   6. Creates `right_column_container` for the right column.
        #   7. Instantiates `ScanControlTab` and places it in the right column.
        #   8. Creates and configures the "Application Console" scrolled text widget
        #      within the right column.
        #
        # Outputs:
        #   None. Populates the main window with GUI elements.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Implemented two-layer tab structure with parent and child notebooks.
        #                      Instantiated new parent tab classes and added them to the main notebook.
        #                      Adjusted child notebook references to point to the nested notebooks within parent tabs.
        # (2025-07-31) Change: Corrected typo in console_print_func argument for Markers Parent Tab.
        # (2025-07-31) Change: Applied specific styles to parent tabs for correct color display.
        # (2025-07-31) Change: Removed 'style' argument from parent_notebook.add() calls to fix TclError.
        # (2025-07-31) Change: Dynamically setting parent tab colors via notebook.tab() calls.
        # (2025-07-31) Change: Storing parent tab widget instances for more robust color setting.
        # (2025-07-31) Change: Removed immediate notebook.tab() calls after add; initial color handled by _on_parent_tab_change.
        # (2025-07-31) Change: Storing parent tab instances as attributes of App for global access.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Replaced fixed grid columns with ttk.PanedWindow for resizable divider.
        #                      Adjusted ScanControlTab's sticky option to expand horizontally.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Applied saved sash position to the PanedWindow.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        Creates and arranges all GUI widgets in the main application window,
        implementing a two-layer tab structure using parent tabs.
        """
        debug_print(f"🚫🐛 [DEBUG] Creating main application widgets with nested tabs... Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)

        # Configure grid for the main window - single row, single column for the PanedWindow
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- PanedWindow for resizable columns ---
        # This allows the user to resize the left and right columns
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


        # --- Scan Control Buttons Frame (Moved into right_column_container) ---
        self.scan_control_tab = ScanControlTab(right_column_container, app_instance=self, console_print_func=self._print_to_gui_console)
        # Changed sticky to "nsew" to make it expand in all directions, especially horizontally
        self.scan_control_tab.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")


        # --- Application Console Frame (Moved into right_column_container) ---
        console_frame = ttk.LabelFrame(right_column_container, text="Application Console", style='Dark.TLabelframe')
        console_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        console_frame.grid_rowconfigure(0, weight=1)
        console_frame.grid_columnconfigure(0, weight=1)

        self.console_text = scrolledtext.ScrolledText(console_frame, wrap="word", bg="#2b2b2b", fg="#cccccc", insertbackground="white")
        self.console_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.console_text.config(state=tk.DISABLED)

        # Apply the saved sash position after all widgets are added to the paned window
        # Ensure the value is within reasonable bounds (e.g., not zero, not exceeding window width)
        sash_pos = self.paned_window_sash_position_var.get()
        if sash_pos > 0: # Avoid setting to 0 which can hide a pane
            self.main_panedwindow.sashpos(0, sash_pos)
            debug_print(f"🚫🐛 [DEBUG] Applied saved PanedWindow sash position: {sash_pos}. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)
        else:
            debug_print(f"🚫🐛 [WARNING] Invalid saved PanedWindow sash position: {sash_pos}. Using default. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)


        debug_print(f"🚫🐛 [DEBUG] Main application widgets created. Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)


    def _setup_styles(self):
        # Configures and applies custom ttk styles for a modern dark theme
        # to various Tkinter widgets within the application. This includes
        # defining styles for parent and child notebooks to support the
        # two-layer tab structure with unique and dynamic colors for parent tabs.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Sets the ttk theme to 'clam'.
        #   3. Defines a set of consistent color variables for the theme,
        #      including specific colors for parent tabs.
        #   4. Configures styles for general widgets like `TFrame`, `TLabel`, `TEntry`, `TCombobox`.
        #   5. Defines and maps styles for various `TButton` types (default, Blue, Green, Red, Orange, Purple, LargeYAK).
        #   6. Configures styles for `TCheckbutton`, `TLabelFrame`, and `TNotebook` (tabs).
        #   7. Defines specific styles for parent notebooks, including unique
        #      backgrounds for selected and unselected parent tabs.
        #   8. Configures styles for `Treeview` widgets (headings and rows).
        #   9. Defines specific styles for the "Markers Tab".
        #
        # Outputs:
        #   None. Applies visual styling to the application's GUI.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Adjusted preset button font size to 10pt and selected button color to orange.
        # (2025-07-31) Change: Added custom styles for parent tabs to allow unique bright/muted colors.
        # (2025-07-31) Change: Defined and applied specific styles for child notebooks to match parent colors.
        # (2025-07-31) Change: Refactored parent tab styling to use individual styles per tab for correct color display.
        # (2025-07-31) Change: Simplified parent tab styling to ensure consistent display and avoid TclError.
        # (2025-07-31) Change: Implemented user-requested color scheme for parent and child tabs.
        # (2025-07-31) Change: Removed problematic style.map for Parent.TNotebook.Tab as colors are now set dynamically.
        # (2025-07-31) Change: Defined explicit active and inactive styles for each parent tab to fix "-background" error.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Added new Markers tab specific styles.
        """
        Configures and applies custom ttk styles for a modern dark theme,
        including styles for nested tabs.
        """
        debug_print(f"🚫🐛 [DEBUG] Setting up ttk styles... Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)
        # self.style is now an instance attribute, initialized in __init__
        self.style.theme_use('clam')

        # General background and foreground colors
        BG_DARK = "#1e1e1e"
        FG_LIGHT = "#cccccc"
        ACCENT_BLUE = "#007bff"
        ACCENT_GREEN = "#28a745"
        ACCENT_RED = "#dc3545"
        ACCENT_ORANGE = "#ffc107"
        ACCENT_PURPLE = "#6f42c1"

        # Parent Tab Colors (defined in _create_widgets now and used via self.parent_tab_colors)
        # These constants are kept here for clarity but the actual values are pulled from self.parent_tab_colors
        # in _create_widgets and _on_parent_tab_change.
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
        # ACCENT_PURPLE is already defined above, reusing for consistency
        PARENT_EXPERIMENTS_ACTIVE = ACCENT_PURPLE
        PARENT_EXPERIMENTS_INACTIVE = "#4d2482"


        self.style.configure('.', background=BG_DARK, foreground=FG_LIGHT, font=('Helvetica', 10))
        self.style.configure('TFrame', background=BG_DARK)
        self.style.configure('TLabel', background=BG_DARK, foreground=FG_LIGHT)
        self.style.configure('TEntry', fieldbackground="#3b3b3b", foreground="#ffffff", borderwidth=1, relief="flat")
        self.style.map('TEntry', fieldbackground=[('focus', '#4a4a4a')])
        self.style.configure('TCombobox', fieldbackground="#3b3b3b", foreground="#ffffff", selectbackground=ACCENT_BLUE, selectforeground="white")
        self.style.map('TCombobox', fieldbackground=[('readonly', '#3b3b3b')], arrowcolor=[('!disabled', FG_LIGHT)])

        # Buttons
        self.style.configure('TButton',
                        background="#4a4a4a",
                        foreground="white",
                        font=('Helvetica', 10, 'bold'),
                        borderwidth=0,
                        focusthickness=3,
                        focuscolor=ACCENT_BLUE,
                        padding=5)
        self.style.map('TButton',
                background=[('active', '#606060'), ('disabled', '#303030')],
                foreground=[('disabled', '#808060')])

        # Specific button styles
        self.style.configure('Blue.TButton', background=ACCENT_BLUE, foreground="white")
        self.style.map('Blue.TButton', background=[('active', '#0056b3'), ('disabled', '#004085')])

        self.style.configure('Green.TButton', background=ACCENT_GREEN, foreground="white")
        self.style.map('Green.TButton', background=[('active', '#218838'), ('disabled', '#1e7e34')])

        self.style.configure('Red.TButton', background=ACCENT_RED, foreground="white")
        self.style.map('Red.TButton', background=[('active', '#c82333'), ('disabled', '#bd2130')])

        self.style.configure('Orange.TButton', background=ACCENT_ORANGE, foreground="#333333")
        self.style.map('Orange.TButton', background=[('active', '#e0a800'), ('disabled', '#d39e00')])

        self.style.configure('Purple.TButton', background=ACCENT_PURPLE, foreground="white")
        self.style.map('Purple.TButton', background=[('active', '#5a2d9e'), ('disabled', '#4d2482')])


        # Checkbuttons
        self.style.configure('TCheckbutton', background=BG_DARK, foreground=FG_LIGHT, indicatorcolor="#4a4a4a")
        self.style.map('TCheckbutton',
                background=[('active', BG_DARK)],
                foreground=[('disabled', '#808080')],
                indicatorcolor=[('selected', ACCENT_BLUE)])

        # LabelFrame
        self.style.configure('TLabelFrame', background=BG_DARK, foreground=FG_LIGHT, borderwidth=1, relief="solid")
        self.style.configure('TLabelFrame.Label', background=BG_DARK, foreground=FG_LIGHT, font=('Helvetica', 10, 'bold'))
        self.style.configure('Dark.TLabelframe', background="#1e1e1e", foreground="#cccccc")
        self.style.configure('Dark.TLabelframe.Label', background="#1e1e1e", foreground="#cccccc")
        self.style.configure('Dark.TFrame', background="#1e1e1e")

        # --- Parent Notebook Styles ---
        # Generic Parent Notebook style (for the notebook frame itself)
        self.style.configure('Parent.TNotebook', background=BG_DARK, borderwidth=0)
        # Configure the tab elements directly for Parent.TNotebook.Tab
        # This will apply to ALL parent tabs. We use style.map for state-based changes.
        self.style.configure('Parent.TNotebook.Tab',
                             background="#3b3b3b", # Default inactive background
                             foreground=FG_LIGHT,
                             padding=[15, 8],
                             font=('Helvetica', 11, 'bold'))

        # Map colors for Parent.TNotebook.Tab based on state
        self.style.map('Parent.TNotebook.Tab',
                       background=[('selected', ACCENT_BLUE), ('active', ACCENT_BLUE)], # Common active color
                       foreground=[('selected', 'white'), ('active', 'white')],
                       expand=[('selected', [1, 1, 1, 0])]) # Expand selected tab

        # --- Child Notebook Styles (Matching Parent Colors) ---
        # These styles are applied to the *child notebooks themselves* and their tabs.
        # Instrument Child Notebook Tabs (Red)
        self.style.configure('InstrumentChild.TNotebook', background=self.parent_tab_colors["INSTRUMENT"]["active"], borderwidth=0)
        self.style.configure('InstrumentChild.TNotebook.Tab', background=self.parent_tab_colors["INSTRUMENT"]["inactive"], foreground=FG_LIGHT, padding=[10, 5])
        self.style.map('InstrumentChild.TNotebook.Tab',
                background=[('selected', self.parent_tab_colors["INSTRUMENT"]["active"]), ('active', self.parent_tab_colors["INSTRUMENT"]["active"])],
                foreground=[('selected', 'white')],
                expand=[('selected', [1, 1, 1, 0])])

        # Scanning Child Notebook Tabs (Orange)
        self.style.configure('ScanningChild.TNotebook', background=self.parent_tab_colors["SCANNING"]["active"], borderwidth=0)
        self.style.configure('ScanningChild.TNotebook.Tab', background=self.parent_tab_colors["SCANNING"]["inactive"], foreground=BG_DARK, padding=[10, 5])
        self.style.map('ScanningChild.TNotebook.Tab',
                background=[('selected', self.parent_tab_colors["SCANNING"]["active"]), ('active', self.parent_tab_colors["SCANNING"]["active"])],
                foreground=[('selected', BG_DARK)],
                expand=[('selected', [1, 1, 1, 0])])

        # Plotting Child Notebook Tabs (Yellow)
        self.style.configure('PlottingChild.TNotebook', background=self.parent_tab_colors["PLOTTING"]["active"], borderwidth=0)
        self.style.configure('PlottingChild.TNotebook.Tab', background=self.parent_tab_colors["PLOTTING"]["inactive"], foreground=BG_DARK, padding=[10, 5])
        self.style.map('PlottingChild.TNotebook.Tab',
                background=[('selected', self.parent_tab_colors["PLOTTING"]["active"]), ('active', self.parent_tab_colors["PLOTTING"]["active"])],
                foreground=[('selected', 'black')], # Black foreground for yellow for better contrast
                expand=[('selected', [1, 1, 1, 0])])


        # Markers Child Notebook Tabs (Green)
        self.style.configure('MarkersChild.TNotebook', background=self.parent_tab_colors["MARKERS"]["active"], borderwidth=0)
        self.style.configure('MarkersChild.TNotebook.Tab', background=self.parent_tab_colors["MARKERS"]["inactive"], foreground=BG_DARK, padding=[10, 5])
        self.style.map('MarkersChild.TNotebook.Tab',
                background=[('selected', self.parent_tab_colors["MARKERS"]["active"]), ('active', self.parent_tab_colors["MARKERS"]["active"])],
                foreground=[('selected', BG_DARK)], # White foreground for green
                expand=[('selected', [1, 1, 1, 0])])

        # Presets Child Notebook Tabs (Blue)
        self.style.configure('PresetsChild.TNotebook', background=self.parent_tab_colors["PRESETS"]["active"], borderwidth=0)
        self.style.configure('PresetsChild.TNotebook.Tab', background=self.parent_tab_colors["PRESETS"]["inactive"], foreground=FG_LIGHT, padding=[10, 5])
        self.style.map('PresetsChild.TNotebook.Tab',
                background=[('selected', self.parent_tab_colors["PRESETS"]["active"]), ('active', self.parent_tab_colors["PRESETS"]["active"])],
                foreground=[('selected', 'white')],
                expand=[('selected', [1, 1, 1, 0])])

        # Experiments Child Notebook Tabs (Purple)
        self.style.configure('ExperimentsChild.TNotebook', background=self.parent_tab_colors["EXPERIMENTS"]["active"], borderwidth=0)
        self.style.configure('ExperimentsChild.TNotebook.Tab', background=self.parent_tab_colors["EXPERIMENTS"]["inactive"], foreground=FG_LIGHT, padding=[10, 5])
        self.style.map('ExperimentsChild.TNotebook.Tab',
                background=[('selected', self.parent_tab_colors["EXPERIMENTS"]["active"]), ('active', self.parent_tab_colors["EXPERIMENTS"]["active"])],
                foreground=[('selected', 'white')],
                expand=[('selected', [1, 1, 1, 0])])


        # Treeview (for MarkersDisplayTab and VisaInterpreterTab)
        self.style.configure('Treeview',
                        background="#3b3b3b",
                        foreground="#ffffff",
                        fieldbackground="#3b3b3b",
                        rowheight=25)
        self.style.map('Treeview',
                background=[('selected', ACCENT_BLUE)],
                foreground=[('selected', 'white')])

        self.style.configure('Treeview.Heading',
                        background="#4a4a4a",
                        foreground="white",
                        font=('Helvetica', 10, "bold"))
        self.style.map('Treeview.Heading',
                background=[('active', '#606060')])

        # Markers Tab Specific Styles (from the immersive artifact)
        self.style.configure("Markers.TFrame",
                            background="#1e1e1e", # Dark background for the main markers tab frame
                            foreground="#cccccc") # Light grey text for general labels

        self.style.configure("Dark.TLabelframe",
                            background="#2b2b2b", # Slightly lighter dark for labelled frames
                            foreground="#ffffff", # White text for the labelframe title
                            bordercolor="#444444",
                            lightcolor="#444444",
                            darkcolor="#1a1a1a")
        self.style.map("Dark.TLabelframe",
                  background=[('active', '#3a3a3a')]) # Subtle change on active

        self.style.configure("Dark.TLabelframe.Label",
                            background="#2b2b2b",
                            foreground="#ffffff",
                            font=("Arial", 10, "bold"))

        self.style.configure("Dark.TFrame",
                            background="#1e1e1e") # For inner frames without a label

        self.style.configure("Markers.Inner.Treeview",
                            background="#2b2b2b", # Dark background for treeview
                            foreground="#cccccc", # Light grey text
                            fieldbackground="#2b2b2b",
                            bordercolor="#444444",
                            lightcolor="#444444",
                            darkcolor="#1a1a1a",
                            font=("Arial", 9))
        self.style.map("Markers.Inner.Treeview",
                  background=[('selected', '#555555')], # Darker grey when selected
                  foreground=[('selected', '#ffffff')]) # White text when selected

        self.style.configure("Markers.TLabel",
                            background="#1e1e1e", # Dark background for labels
                            foreground="#cccccc", # Light grey text
                            font=("Arial", 9))

        self.style.configure("Markers.TEntry",
                            fieldbackground="#3a3a3a", # Darker input field
                            foreground="#ffffff", # White text
                            insertcolor="#ffffff", # White cursor
                            bordercolor="#555555",
                            lightcolor="#555555",
                            darkcolor="#222222",
                            font=("Arial", 9))
        self.style.map("Markers.TEntry",
                  fieldbackground=[('focus', '#4a4a4a')]) # Slightly lighter on focus

        self.style.configure("Markers.TButton",
                            background="#4a4a4a", # Default dark grey button
                            foreground="white",
                            font=("Arial", 9, "bold"),
                            borderwidth=1,
                            relief="raised",
                            focusthickness=2,
                            focuscolor="#007bff") # Blue focus highlight
        self.style.map("Markers.TButton",
                  background=[('active', '#5a5a5a'), # Lighter grey on hover
                              ('pressed', '#3a3a3a')], # Darker grey on press
                  foreground=[('active', '#ffffff'),
                              ('pressed', '#ffffff')])

        self.style.configure("ActiveScan.TButton",
                            background="#28a745", # Green
                            foreground="#000000", # Black text
                            font=("Arial", 9, "bold"))
        self.style.map("ActiveScan.TButton",
                  background=[('active', '#218838'),
                              ('pressed', '#1e7e34')],
                  foreground=[('active', '#ffffff'),
                              ('pressed', '#ffffff')])


        self.style.configure("Markers.SelectedButton.TButton",
                            background="#ff8c00", # Orange
                            foreground="#000000", # Black text for contrast
                            font=("Arial", 9, "bold"),
                            borderwidth=2, # Thicker border for selected
                            relief="solid", # Solid border
                            bordercolor="#ffaa00") # Slightly lighter orange border
        self.style.map("Markers.SelectedButton.TButton",
                  background=[('active', '#e67e00'), # Darker orange on hover
                              ('pressed', '#cc7000')], # Even darker on press
                  foreground=[('active', '#ffffff'),
                              ('pressed', '#ffffff')])

        self.style.configure("DeviceButton.TButton",
                            background="#007bff", # Blue
                            foreground="#ffffff", # White text
                            font=("Arial", 9, "bold"))
        self.style.map("DeviceButton.TButton",
                  background=[('active', '#0056b3'),
                              ('pressed', '#004085')],
                  foreground=[('active', '#ffffff'),
                              ('pressed', '#ffffff')])


        # Updated LargePreset.TButton font size to 10
        self.style.configure("LargePreset.TButton",
                        background="#4a4a4a",
                        foreground="white",
                        font=("Helvetica", 10, "bold"), # Changed font size from 14 to 10
                        padding=[30, 15, 30, 15])
        self.style.map("LargePreset.TButton",
                background=[('active', '#606060')])

        # Updated SelectedPreset.TButton to be orange and font size to 10
        self.style.configure("SelectedPreset.Orange.TButton", # Renamed style to be explicit
                        background="#ff8c00", # Orange color
                        foreground="white",
                        font=("Helvetica", 10, "bold"), # Changed font size from 14 to 10
                        padding=[30, 15, 30, 15])
        self.style.map("SelectedPreset.Orange.TButton",
                background=[('active', '#e07b00')]) # Darker orange on active/hover

        YAK_ORANGE = "#ff8c00"
        self.style.configure('LargeYAK.TButton',
                        font=('Helvetica', 100, 'bold'),
                        background=YAK_ORANGE,
                        foreground="white",
                        padding=[20, 10])
        self.style.map('LargeYAK.TButton',
                  background=[('active', '#e07b00'), ('disabled', '#cc7000')])


        debug_print(f"🚫🐛 [DEBUG] ttk styles set up. Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)


    def _redirect_stdout_to_console(self):
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
        """
        Redirects standard output and error streams to the GUI's scrolled text widget.
        """
        debug_print(f"🚫🐛 [DEBUG] Redirecting stdout/stderr to GUI console... Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)
        sys.stdout = TextRedirector(self.console_text, "stdout")
        sys.stderr = TextRedirector(self.console_text, "stderr")
        print("Application console initialized.")

    def _print_to_gui_console(self, message, overwrite=False):
        # A helper function to print messages to the GUI console from any thread.
        # It uses `self.after(0, ...)` to ensure thread safety by scheduling
        # the console update on the main Tkinter thread.
        #
        # Inputs:
        #   message (str): The string message to print to the console.
        #   overwrite (bool, optional): If True, the last line in the console
        #                               will be overwritten. Defaults to False.
        #
        # Process:
        #   1. Schedules `_update_console_text` to run on the main Tkinter thread.
        #
        # Outputs:
        #   None. Updates the GUI console asynchronously.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        A wrapper method in the App class to call the external logic function.
        This method will be called by other parts of the application.
        """
        self.after(0, lambda: self._update_console_text(message, overwrite))

    def _update_console_text(self, message, overwrite):
        # Appends a message to the scrolled text widget that serves as the GUI console.
        # It ensures the text widget is enabled for writing, inserts the message,
        # scrolls to the end, and then disables the widget.
        #
        # Inputs:
        #   message (str): The string message to append.
        #   overwrite (bool): If True, the last line of text is deleted before
        #                     the new message is inserted.
        #
        # Process:
        #   1. Sets the console text widget state to `tk.NORMAL` to allow editing.
        #   2. If `overwrite` is True, calculates the start of the last line and deletes it.
        #   3. Inserts the new message at the end of the text widget, followed by a newline.
        #   4. Scrolls the view to the end to show the latest message.
        #   5. Sets the console text widget state back to `tk.DISABLED` to prevent user editing.
        #
        # Outputs:
        #   None. Modifies the content of the GUI console.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        Appends a message to the scrolled text widget.
        If overwrite is True, it deletes the last line before inserting.
        """
        self.console_text.config(state=tk.NORMAL)
        if overwrite:
            last_line_start = self.console_text.index("end-1c linestart")
            self.console_text.delete(last_line_start, tk.END)

        self.console_text.insert(tk.END, message + "\n")
        self.console_text.see(tk.END)
        self.console_text.config(state=tk.DISABLED)


    def _populate_resources(self):
        # Delegates the task of populating VISA resources to the `InstrumentTab`.
        # It acts as a centralized point for other parts of the application
        # to request resource population.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Checks if `instrument_parent_tab` and its nested `instrument_connection_tab` exist.
        #      If so, calls its `_populate_resources` method.
        #   3. If not initialized, prints a warning to the console and debug log.
        #
        # Outputs:
        #   None. Triggers resource population in a delegated tab.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Adjusted delegation to target the nested Instrument Connection tab.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        Delegates the call to populate VISA resources to the Instrument Connection tab.
        """
        debug_print(f"🚫🐛 [DEBUG] Delegating populate VISA resources to Instrument Connection tab... Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)
        if hasattr(self, 'instrument_parent_tab') and hasattr(self.instrument_parent_tab, 'instrument_connection_tab'):
            self.instrument_parent_tab.instrument_connection_tab._populate_resources()
        else:
            self._print_to_gui_console("⚠️ Warning: Instrument Connection tab not initialized. Cannot populate resources.")
            debug_print(f"🚫🐛 [WARNING] Instrument Connection tab not initialized for _populate_resources. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)


    def _on_resource_selected(self, event):
        # Delegates the resource selection callback event to the `InstrumentTab`.
        # This allows the `InstrumentTab` to handle the logic associated with
        # a user selecting a different VISA resource from the dropdown.
        #
        # Inputs:
        #   event (tkinter.Event): The event object that triggered the call.
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Checks if `instrument_parent_tab` and its nested `instrument_connection_tab` exist.
        #      If so, calls its `_on_resource_selected` method.
        #   3. If not initialized, prints a warning to the console and debug log.
        #
        # Outputs:
        #   None. Triggers resource selection handling in a delegated tab.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Adjusted delegation to target the nested Instrument Connection tab.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        Delegates the resource selection callback to the Instrument Connection tab.
        """
        debug_print(f"🚫🐛 [DEBUG] Delegating resource selection to Instrument Connection tab... Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)
        if hasattr(self, 'instrument_parent_tab') and hasattr(self.instrument_parent_tab, 'instrument_connection_tab'):
            self.instrument_parent_tab.instrument_connection_tab._on_resource_selected(event)
        else:
            self._print_to_gui_console("⚠️ Warning: Instrument Connection tab not initialized. Cannot handle resource selection.")
            debug_print(f"🐛 [WARNING] Instrument Connection tab not initialized for _on_resource_selected. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)


    def _connect_instrument(self):
        # Delegates the instrument connection request to the `InstrumentTab`.
        # This provides a centralized method for other parts of the application
        # to initiate an instrument connection.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Checks if `instrument_parent_tab` and its nested `instrument_connection_tab` exist.
        #      If so, calls its `_connect_instrument` method.
        #   3. If not initialized, prints a warning to the console and debug log.
        #
        # Outputs:
        #   None. Triggers instrument connection in a delegated tab.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Adjusted delegation to target the nested Instrument Connection tab.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        Delegates the connect instrument call to the Instrument Connection tab.
        """
        debug_print(f"🚫🐛 [DEBUG] Delegating connect instrument to Instrument Connection tab... Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)
        if hasattr(self, 'instrument_parent_tab') and hasattr(self.instrument_parent_tab, 'instrument_connection_tab'):
            self.instrument_parent_tab.instrument_connection_tab._connect_instrument()
        else:
            self._print_to_gui_console("⚠️ Warning: Instrument Connection tab not initialized. Cannot connect instrument.")
            debug_print(f"🚫🐛 [WARNING] Instrument Connection tab not initialized for _connect_instrument. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)


    def _disconnect_instrument(self):
        # Delegates the instrument disconnection request to the `InstrumentTab`.
        # This provides a centralized method for other parts of the application
        # to initiate an instrument disconnection.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Checks if `instrument_parent_tab` and its nested `instrument_connection_tab` exist.
        #      If so, calls its `_disconnect_instrument` method.
        #   3. If not initialized, prints a warning to the console and debug log.
        #
        # Outputs:
        #   None. Triggers instrument disconnection in a delegated tab.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Adjusted delegation to target the nested Instrument Connection tab.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        Delegates the disconnect instrument call to the Instrument Connection tab.
        """
        debug_print(f"�🐛 [DEBUG] Delegating disconnect instrument to Instrument Connection tab... Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)
        if hasattr(self, 'instrument_parent_tab') and hasattr(self.instrument_parent_tab, 'instrument_connection_tab'):
            self.instrument_parent_tab.instrument_connection_tab._disconnect_instrument()
        else:
            self._print_to_gui_console("⚠️ Warning: Instrument Connection tab not initialized. Cannot disconnect instrument.")
            debug_print(f"🚫🐛 [WARNING] Instrument Connection tab not initialized for _disconnect_instrument. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)


    def _apply_instrument_settings(self):
        # Delegates the request to apply instrument settings to the `InstrumentTab`.
        # This provides a centralized method for other parts of the application
        # to initiate the application of current settings to the connected instrument.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Checks if `instrument_parent_tab` and its nested `instrument_connection_tab` exist.
        #      If so, calls its `_apply_settings` method.
        #   3. If not initialized, prints a warning to the console and debug log.
        #
        # Outputs:
        #   None. Triggers settings application in a delegated tab.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Adjusted delegation to target the nested Instrument Connection tab.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        Delegates the apply instrument settings call to the Instrument Connection tab.
        """
        debug_print(f"🚫🐛 [DEBUG] Delegating apply instrument settings to Instrument Connection tab... Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)
        if hasattr(self, 'instrument_parent_tab') and hasattr(self.instrument_parent_tab, 'instrument_connection_tab'):
            self.instrument_parent_tab.instrument_connection_tab._apply_settings()
        else:
            self._print_to_gui_console("⚠️ Warning: Instrument Connection tab not initialized. Cannot apply settings.")
            debug_print(f"🚫🐛 [WARNING] Instrument Connection tab not initialized for _apply_instrument_settings. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)


    def _load_selected_preset(self):
        # Loads the currently selected preset file onto the instrument.
        # This function is called when the "Load Selected Preset" button is clicked.
        # It delegates the actual loading logic to the nested `preset_files_tab`.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Checks if `presets_parent_tab` and its nested `preset_files_tab` exist.
        #      If so, calls its `_load_selected_preset` method.
        #   3. If not initialized, prints a warning to the console and debug log.
        #
        # Outputs:
        #   None. Triggers preset loading in a delegated tab.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Adjusted delegation to target the nested Instrument Presets tab.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        Loads the currently selected preset file onto the instrument.
        This function is called when the "Load Selected Preset" button is clicked.
        It delegates the actual loading logic to the nested Instrument Presets tab.
        """
        debug_print(f"🚫🐛 [DEBUG] Loading selected preset... Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)
        if hasattr(self, 'presets_parent_tab') and hasattr(self.presets_parent_tab, 'preset_files_tab'):
            self.presets_parent_tab.preset_files_tab._load_selected_preset()
        else:
            self._print_to_gui_console("⚠️ Warning: Instrument Presets tab not initialized.")
            debug_print(f"🚫🐛 [WARNING] Instrument Presets tab not initialized. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)


    def _start_scan(self):
        # Initiates the scan process by delegating the call to the `ScanControlTab`.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Checks if `scan_control_tab` exists. If so, calls its `_start_scan` method.
        #   3. If `scan_control_tab` is not initialized, prints a warning to the console and debug log.
        #
        # Outputs:
        #   None. Triggers scan initiation in a delegated tab.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        Initiates the scan process in a separate thread.
        """
        debug_print(f"🚫🐛 [DEBUG] Starting scan... Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)
        if hasattr(self, 'scan_control_tab'):
            self.scan_control_tab._start_scan_thread() # Changed to _start_scan_thread as per scan_controler_button_logic
        else:
            self._print_to_gui_console("⚠️ Warning: Scan Control tab not initialized.")
            debug_print(f"🚫🐛 [WARNING] ScanControlTab not initialized for _start_scan. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)


    def _pause_scan(self):
        # Pauses the active scan by delegating the call to the `ScanControlTab`.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Checks if `scan_control_tab` exists. If so, calls its `_pause_scan` method.
        #   3. If `scan_control_tab` is not initialized, prints a warning to the console and debug log.
        #
        # Outputs:
        #   None. Triggers scan pausing in a delegated tab.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        Pauses the active scan.
        """
        debug_print(f"🚫🐛 [DEBUG] Pausing scan... Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)
        if hasattr(self, 'scan_control_tab'):
            self.scan_control_tab._pause_scan()
        else:
            self._print_to_gui_console("⚠️ Warning: Scan Control tab not initialized.")
            debug_print(f"🚫🐛 [WARNING] ScanControlTab not initialized for _pause_scan. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)


    def _stop_scan(self):
        # Stops the active scan by delegating the call to the `ScanControlTab`.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Checks if `scan_control_tab` exists. If so, calls its `_stop_scan` method.
        #   3. If `scan_control_tab` is not initialized, prints a warning to the console and debug log.
        #
        # Outputs:
        #   None. Triggers scan stopping in a delegated tab.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        Stops the active scan.
        """
        debug_print(f"🚫🐛 [DEBUG] Stopping scan... Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)
        if hasattr(self, 'scan_control_tab'):
            self.scan_control_tab._stop_scan()
        else:
            self._print_to_gui_console("⚠️ Warning: Scan Control tab not initialized.")
            debug_print(f"🚫🐛 [WARNING] ScanControlTab not initialized for _stop_scan. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)


    def _browse_output_folder(self):
        # Opens a file dialog to allow the user to select an output folder
        # for saving scan data. It updates the `output_folder_var` with the
        # selected path.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Opens a directory selection dialog, defaulting to the current
        #      value of `output_folder_var`.
        #   3. If a folder is selected, updates `output_folder_var` and
        #      prints a confirmation message to the GUI console and debug log.
        #
        # Outputs:
        #   None. Updates a Tkinter variable and interacts with the file system.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        Opens a file dialog to select the output folder for scan data.
        """
        debug_print(f"🚫🐛 [DEBUG] Browsing output folder... Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)
        folder_selected = filedialog.askdirectory(initialdir=self.output_folder_var.get())
        if folder_selected:
            self.output_folder_var.set(folder_selected)
            self._print_to_gui_console(f"Output folder set to: {folder_selected}")
            debug_print(f"🚫🐛 [DEBUG] Output folder set to: {folder_selected}. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)


    def reset_setting_colors_logic(self):
        # Resets the background color of all setting entry and checkbutton widgets
        # to their default appearance. This is typically called after settings
        # are applied or restored to remove any visual indication of unsaved changes.
        # It iterates through all Tkinter variables in `setting_var_map` and
        # attempts to find and reset the style of associated widgets across all tabs.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Iterates through each `tk_var_instance` in `self.setting_var_map`.
        #   3. For each variable, it traverses the widget hierarchy (main window, parent notebooks, child notebooks, tabs, frames)
        #      to find and reset the style of associated `ttk.Entry`, `ttk.Checkbutton`, and `ttk.Combobox` widgets.
        #   4. Includes special handling for `notes_var` as it's linked to a `ScrolledText` widget,
        #      which does not use `ttk.Style` for background.
        #
        # Outputs:
        #   None. Modifies the visual style of Tkinter widgets.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Adjusted widget traversal to account for nested notebooks.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        Resets the background color of all setting entry widgets to default.
        This function is called after settings are applied or restored to remove
        any visual indication of unsaved changes.
        """
        debug_print(f"🐛 [DEBUG] Resetting setting colors... Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)

        # Helper to recursively find widgets
        def find_and_reset_widgets(parent_widget, tk_var_instance):
            for child in parent_widget.winfo_children():
                # Check if child is a notebook
                if isinstance(child, ttk.Notebook):
                    for tab_id in child.tabs():
                        tab_widget = child.nametowidget(tab_id)
                        find_and_reset_widgets(tab_widget, tk_var_instance) # Recurse into tabs
                # Check if child is a panedwindow
                elif isinstance(child, ttk.PanedWindow):
                    for pane_child in child.winfo_children():
                        find_and_reset_widgets(pane_child, tk_var_instance) # Recurse into panes
                # Check if child is a frame or labelframe
                elif isinstance(child, (ttk.Frame, ttk.LabelFrame)):
                    find_and_reset_widgets(child, tk_var_instance) # Recurse into frames
                # Check for Entry, Checkbutton, Combobox
                elif isinstance(child, ttk.Entry) and child.cget('textvariable') == str(tk_var_instance):
                    child.config(style='TEntry')
                    debug_print(f"🚫🐛 [DEBUG] Reset color for {tk_var_instance.get()} (Entry) in {child.winfo_class()}. Version: {current_version}",
                                file=f"main_app.py - {current_version}",
                                function=inspect.currentframe().f_code.co_name)
                elif isinstance(child, ttk.Checkbutton) and child.cget('variable') == str(tk_var_instance):
                    child.config(style='TCheckbutton')
                    debug_print(f"🚫🐛 [DEBUG] Reset color for {tk_var_instance.get()} (Checkbutton) in {child.winfo_class()}. Version: {current_version}",
                                file=f"main_app.py - {current_version}",
                                function=inspect.currentframe().f_code.co_name)
                elif isinstance(child, ttk.Combobox) and child.cget('textvariable') == str(tk_var_instance):
                    child.config(style='TCombobox')
                    debug_print(f"🚫🐛 [DEBUG] Reset color for {tk_var_instance.get()} (Combobox) in {child.winfo_class()}. Version: {current_version}",
                                file=f"main_app.py - {current_version}",
                                function=inspect.currentframe().f_code.co_name)

        # Start recursive search from the main panedwindow, as it's the top-level container now
        find_and_reset_widgets(self.main_panedwindow, tk_var_instance)


    def _on_closing(self):
        # Handles the window closing event. It ensures that the current
        # configuration settings are saved to `config.ini` before the
        # application exits, but only if the application is fully initialized.
        # It also updates the `notes_var` from the `ScrolledText` widget
        # before saving.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Prints a debug message indicating application closing.
        #   2. If the `scanning_parent_tab`, its `scan_meta_data_tab`, and its `notes_text_widget` exist,
        #      it updates `notes_var` with the current content of the widget.
        #   3. Checks `is_ready_to_save` flag. If True, it saves the current
        #      configuration using `save_config`.
        #   4. If `is_ready_to_save` is False, it skips saving and logs a message.
        #   5. Destroys the main Tkinter window.
        #
        # Outputs:
        #   None. Saves configuration and closes the application.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Adjusted notes_var update to target the nested Scan Meta Data tab.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Captured and saved the current PanedWindow sash position.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        Handles the window closing event. Saves configuration before exiting,
        but only if the application is fully initialized.
        """
        debug_print(f"🚫🐛 [DEBUG] Application closing. Performing cleanup... Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)

        # Before saving, ensure the notes_var reflects the current content of the ScrolledText
        if hasattr(self, 'scanning_parent_tab') and hasattr(self.scanning_parent_tab, 'scan_meta_data_tab') and hasattr(self.scanning_parent_tab.scan_meta_data_tab, 'notes_text_widget'):
            self.notes_var.set(self.scanning_parent_tab.scan_meta_data_tab.notes_text_widget.get("1.0", tk.END).strip())
            debug_print(f"🚫🐛 [DEBUG] Updated notes_var from ScrolledText before saving: {self.notes_var.get()}. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)

        # Capture current PanedWindow sash position before saving
        if hasattr(self, 'main_panedwindow') and self.main_panedwindow.winfo_ismapped():
            # Check if the panedwindow is mapped (visible) before trying to get sashpos
            current_sash_pos = self.main_panedwindow.sashpos(0)
            self.paned_window_sash_position_var.set(current_sash_pos)
            debug_print(f"🚫🐛 [DEBUG] Captured current PanedWindow sash position: {current_sash_pos}. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)
        else:
            debug_print(f"🚫🐛 [WARNING] main_panedwindow not mapped or does not exist. Cannot save sash position. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)


        if self.is_ready_to_save:
            debug_print(f"🚫🐛 [DEBUG] --- State of band_vars before saving --- Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)
            for i, band_item in enumerate(self.band_vars):
                debug_print(f"🚫🐛 [DEBUG]   Band {band_item['band']['Band Name']}: {band_item['var'].get()}. Version: {current_version}",
                            file=f"main_app.py - {current_version}",
                            function=inspect.currentframe().f_code.co_name)
            debug_print(f"🚫🐛 [DEBUG] --- End state of band_vars --- Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)
            save_config(self)
        else:
            debug_print(f"🚫🐛 [WARNING] Application closing prematurely or not fully initialized. Skipping config save. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)

        self.destroy()


    def _on_parent_tab_change(self, event):
        # Handles tab change events in the parent Notebook.
        # When a parent tab is selected, it ensures the corresponding parent tab's
        # `_on_tab_selected` method is called, which then propagates the call
        # to its currently active child tab. It also updates the visual style
        # of the parent tabs.
        #
        # Inputs:
        #   event (tkinter.Event): The event object that triggered the tab change.
        #
        # Process:
        #   1. Determines the currently selected parent tab and its widget.
        #   2. Gets the text of the selected parent tab.
        #   3. Logs a debug message.
        #   4. (Removed direct style application to individual tabs to fix TclError).
        #      The `style.map` on `Parent.TNotebook.Tab` now handles the common
        #      active/inactive appearance for all parent tab labels.
        #   5. Calls the `_on_tab_selected` method of the selected parent tab itself,
        #      which is responsible for activating and refreshing its default child tab.
        #
        # Outputs:
        #   None. Triggers UI updates in the selected parent and its active child tabs.
        #
        # (2025-07-31) Change: New function to handle parent tab changes and default child tab selection.
        # (2025-07-31) Change: Modified to call _on_tab_selected on the parent tab instance itself.
        # (2025-07-31) Change: Removed redundant style re-application loop, as map handles it.
        # (2025-07-31) Change: Dynamically updates parent tab colors based on selection.
        # (2025-07-31) Change: Uses the stored widget instance for notebook.tab() calls.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        selected_parent_tab_id = self.parent_notebook.select()
        selected_parent_tab_widget = self.parent_notebook.nametowidget(selected_parent_tab_id)
        parent_tab_text = self.parent_notebook.tab(selected_parent_tab_id, "text")

        debug_print(f"🚫🐛 [DEBUG] Parent tab changed to: {parent_tab_text}. Version: {current_version}",
                    file=f"main_app.py - {current_version}",
                    function=inspect.currentframe().f_code.co_name)

        # Removed the problematic style setting for individual parent tabs.
        # The style.map on 'Parent.TNotebook.Tab' now handles the selected/unselected
        # appearance automatically for all parent tab labels.

        # Call the _on_tab_selected method on the selected parent tab instance itself
        if hasattr(selected_parent_tab_widget, '_on_tab_selected'):
            selected_parent_tab_widget._on_tab_selected(event)
            debug_print(f"🚫🐛 [DEBUG] Called _on_tab_selected on parent tab: {selected_parent_tab_widget.winfo_class()}. Version: {current_version}",
                            file=f"main_app.py - {current_version}",
                            function=inspect.currentframe().f_code.co_name)
        else:
            debug_print(f"🚫🐛 [WARNING] Parent tab {selected_parent_tab_widget.winfo_class()} has no _on_tab_selected method. Version: {current_version}",
                            file=f"main_app.py - {current_version}",
                            function=inspect.currentframe().f_code.co_name)


    def _on_tab_change(self, event):
        # Handles tab change events in any Notebook (parent or child).
        # It calls the `_on_tab_selected` method on the newly selected tab's
        # widget if that method exists, allowing individual tabs to refresh
        # their content or state when they become active. This method is
        # generic and can be bound to any ttk.Notebook.
        #
        # Inputs:
        #   event (tkinter.Event): The event object that triggered the tab change.
        #
        # Process:
        #   1. Determines the notebook that triggered the event.
        #   2. Gets the ID of the newly selected tab within that notebook.
        #   3. Converts the tab ID to its corresponding widget instance.
        #   4. Checks if the selected tab widget has an `_on_tab_selected` method.
        #   5. If the method exists, calls it, logging the action.
        #   6. If the method does not exist, logs that it was not found.
        #
        # Outputs:
        #   None. Triggers UI updates in the selected tab.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Modified to handle tab changes for both parent and child notebooks,
        #                      calling _on_tab_selected on the actual tab widget.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        Handles tab change events in any Notebook (parent or child).
        Calls _on_tab_selected for the newly selected tab if available.
        """
        # Determine which notebook triggered the event
        notebook_widget = event.widget

        selected_tab_id = notebook_widget.select()
        selected_tab_widget = notebook_widget.nametowidget(selected_tab_id)

        if hasattr(selected_tab_widget, '_on_tab_selected'):
            selected_tab_widget._on_tab_selected(event)
            debug_print(f"🚫🐛 [DEBUG] Tab changed to {selected_tab_widget.winfo_class()}. Calling _on_tab_selected. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)
        else:
            debug_print(f"🚫🐛 [DEBUG] Tab changed to {selected_tab_widget.winfo_class()}. No _on_tab_selected method found. Version: {current_version}",
                        file=f"main_app.py - {current_version}",
                        function=inspect.currentframe().f_code.co_name)


    def update_connection_status(self, is_connected):
        # A wrapper method in the App class to call the external logic function.
        # This method will be called by other parts of the application.
        #
        # Inputs:
        #   is_connected (bool): True if the instrument is connected, False otherwise.
        #
        # Process:
        #   1. Calls the `update_connection_status_logic` function, passing
        #      `self` (the App instance), `is_connected`, and the GUI console
        #      print function.
        #
        # Outputs:
        #   None. Updates the connection status display via external logic.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        """
        A wrapper method in the App class to call the external logic function.
        This method will be called by other parts of the application.
        """
        update_connection_status_logic(self, is_connected, self._print_to_gui_console)


if __name__ == "__main__":
    app = App()
    app.mainloop()