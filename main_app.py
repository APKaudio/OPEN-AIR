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
#
#
# Version 20250801.1135.1 (Corrected previous error where file was truncated by using the full original file.
#                          Moved ttk.Style configurations for button fonts and flashing
#                          states from scan_controler_button_logic.py to main_app.py.
#                          Adjusted button font size to 30pt globally. Updated debug_print
#                          calls with new current_version.)

current_version = "20250801.1135.1" # this variable should always be defined below the header to make the debugging better

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
from src.scan_controler_button_logic import ScanControlTab # Keep this import, as we still need the class

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
    CONFIG_FILE = os.path.join(_script_dir, 'config.ini')

    # Define the path to the DATA folder, one level up from the application's root
    DATA_FOLDER_PATH = os.path.join(os.path.dirname(_script_dir), 'DATA')


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
        #   14. Calls `_ensure_data_directory_exists` to create the DATA folder.
        #   15. Calls `_create_widgets` to build the GUI.
        #   16. Calls `_setup_styles` to apply custom themes.
        #   17. Redirects stdout to the GUI console.
        #   18. Updates connection status.
        #   19. Prints application art.
        #   20. Loads band selections for ScanTab (now nested).
        #   21. Manually updates notes text widget on ScanMetaDataTab (now nested).
        #   22. Sets `is_ready_to_save` to True.
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
        # (2025-08-01) Change: Updated header and version. Verified import paths based on new directory structure.
        # (2025-08-01) Change: Corrected import paths for numbered subfolders (e.g., '1_Instrument' instead of '1Instrument').
        # (2025-08-01) Change: Corrected import paths to remove leading digits from folder names (e.g., 'tabs.Instrument' instead of 'tabs.1_Instrument').
        # (2025-08-01) Change: Added logic to create the 'DATA' folder one level above the application directory on startup.
        # (2025-08-01) Change: Moved ttk.Style configurations for button fonts and flashing
        #                      states from scan_controler_button_logic.py to main_app.py.
        #                      Adjusted button font size to 30pt globally. Updated debug_print
        #                      calls with new current_version.
        # (2025-08-01) Change: Corrected previous error where file was truncated by using the full original file.
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

        # Ensure the DATA directory exists
        self._ensure_data_directory_exists()

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
        debug_print(f"�🐛 [DEBUG] Application fully initialized and ready to save configuration. Version: {current_version}",
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
        # (2025-08-01) Change: Updated header and version.
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
        # (2025-08-01) Change: Updated header and version.
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
        # (2025-07-31) Change: Added saving of paned window sash position.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        # (2025-08-01) Change: Updated header and version.
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
        # (2025-08-01) Change: Updated header and version.
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
        # (2025-08-01) Change: Updated header and version.
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

        # Buttons - General TButton style (font size 30pt, as requested by Anthony)
        self.style.configure('TButton',
                        background="#4a4a4a",
                        foreground="white",
                        font=('Helvetica', 30, 'bold'), # Set font size to 30pt here
                        borderwidth=0,
                        focusthickness=3,
                        focuscolor=ACCENT_BLUE,
                        padding=(10, 20)) # Set padding for ~50px height
        self.style.map('TButton',
                background=[('active', '#606060'), ('disabled', '#303030')],
                foreground=[('disabled', '#808060')])

        # Specific button styles (inherit from TButton, but override colors)
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

        # Flashing styles for the Pause/Resume button
        # These styles will be toggled by the _start_flashing and _stop_flashing methods
        self.style.configure('FlashingGreen.TButton', background='green', foreground='white',
                             font=('Helvetica', 30, 'bold'), padding=(10, 20))
        self.style.map('FlashingGreen.TButton',
                       background=[('active', 'lightgreen'), ('!active', 'green')],
                       foreground=[('active', 'black'), ('!active', 'white')])

        self.style.configure('FlashingDark.TButton', background='darkgray', foreground='white',
                             font=('Helvetica', 30, 'bold'), padding=(10, 20))
        self.style.map('FlashingDark.TButton',
                       background=[('active', 'gray'), ('!active', 'darkgray')],
                       foreground=[('active', 'black'), ('!active', 'white')])


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
        # (2025-08-01) Change: Updated header and version.
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
        # (2025-08-01) Change: Updated header and version.
        """
        A helper function to print messages to the GUI console from any thread.
        """
        self.after(0, self._update_console_text, message, overwrite)

    def _update_console_text(self, message, overwrite):
        # This function descriotion tells me what this function does
        # Appends a message to the GUI console's scrolled text widget.
        # If `overwrite` is True, it deletes the last line before inserting the new message.
        # It also ensures the console automatically scrolls to the end.
        #
        # Inputs to this function
        #   message (str): The string message to append or overwrite.
        #   overwrite (bool): If True, the last line is removed before inserting.
        #
        # Process of this function
        #   1. Enables the console text widget for editing.
        #   2. If `overwrite` is True, it deletes the last line.
        #   3. Inserts the new message, followed by a newline.
        #   4. Disables the console text widget to prevent user editing.
        #   5. Scrolls to the end of the text widget.
        #
        # Outputs of this function
        #   None. Modifies the GUI console display.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        # (2025-08-01) Change: Updated header and version.
        """
        Appends a message to the GUI console's scrolled text widget.
        """
        self.console_text.config(state=tk.NORMAL)
        if overwrite:
            # Delete last line if it's not empty
            if self.console_text.get("end-2c", "end-1c") != "\n": # Check if last char is not newline
                self.console_text.delete("end-2c", "end-1c") # Delete last character if not newline
            self.console_text.delete("end-1c linestart", "end-1c") # Delete the last line
        self.console_text.insert(tk.END, message + "\n")
        self.console_text.config(state=tk.DISABLED)
        self.console_text.see(tk.END)

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
        # (2025-08-01) Change: Updated header and version.
        """
        A wrapper method in the App class to call the external logic function.
        This method will be called by other parts of the application.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_print(f"Updating connection status to: {is_connected}. Version: {current_version}",
                    file=current_file, function=current_function, console_print_func=self._print_to_gui_console)

        # Call the external logic function
        update_connection_status_logic(self, is_connected, self._print_to_gui_console)

    def _on_closing(self):
        # Handles the application closing event.
        # It saves the current window geometry and paned window sash position to config.ini,
        # then destroys the main application window.
        #
        # Inputs:
        #   None (operates on self).
        #
        # Process:
        #   1. Prints a debug message.
        #   2. Retrieves the current window geometry and stores it in `self.config`.
        #   3. Retrieves the current paned window sash position and stores it in `self.config`.
        #   4. Calls `save_config` to persist the settings.
        #   5. Destroys the main Tkinter window.
        #
        # Outputs:
        #   None. Closes the application.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        # (2025-07-31) Change: Updated header.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Added saving of paned window sash position.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        # (2025-08-01) Change: Updated header and version.
        """
        Handles the application closing event, saving window geometry and paned window sash position.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_print(f"Application closing. Saving configuration... Version: {current_version}",
                    file=current_file, function=current_function, console_print_func=self._print_to_gui_console)

        # Save window geometry
        self.config.set('LAST_USED_SETTINGS', 'last_GLOBAL__window_geometry', self.geometry())

        # Save paned window sash position
        # Get the position of the first (and only) sash
        sash_position = self.main_panedwindow.sashpos(0)
        self.config.set('LAST_USED_SETTINGS', 'last_GLOBAL__paned_window_sash_position', str(sash_position))

        save_config(self) # Save the configuration to config.ini
        self.destroy()

    def _on_parent_tab_change(self, event):
        # Function Description:
        # Handles tab change events in the main parent Notebook.
        # It updates the background and foreground colors of the selected parent tab
        # and its corresponding child notebook to provide visual feedback.
        # It also calls the `_on_tab_selected` method on the newly selected parent tab's
        # widget if that method exists, allowing individual parent tabs to refresh
        # their content or state when they become active.
        #
        # Inputs to this function:
        #   event (tkinter.Event): The event object that triggered the tab change.
        #
        # Process of this function:
        #   1. Prints a debug message.
        #   2. Iterates through all parent tabs to reset their colors to inactive.
        #   3. Determines the currently selected tab in the parent notebook.
        #   4. Retrieves the text (name) and widget instance of the selected tab.
        #   5. Updates the selected parent tab's background and foreground colors to active.
        #   6. If the selected parent tab widget has an `_on_tab_selected` method, calls it.
        #      This propagates the selection event down to the parent tab's own logic,
        #      which in turn can propagate it to its active child tab.
        #
        # Outputs of this function:
        #   None. Triggers UI updates and content refreshes.
        #
        # (2025-07-31) Change: Added to handle parent tab changes and update colors dynamically.
        # (2025-07-31) Change: Refactored to use explicit style configurations for active/inactive tabs.
        # (2025-07-31) Change: Implemented user-requested color scheme for parent tabs.
        # (2025-07-31) Change: Storing parent tab widget instances for more robust color setting.
        # (2025-07-31) Change: Version incremented for resizable divider and scan control expansion.
        # (2025-07-31) Change: Version incremented for paned window sash position saving.
        # (2025-07-31) Change: Version incremented for dropdown UI in Scan Configuration tab.
        # (2025-07-31) Change: Version incremented for new Markers tab styles.
        # (2025-08-01) Change: Updated header and version.
        """
        Handles tab change events in the main parent Notebook, updating colors
        and propagating the selection event to the active parent tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_print(f"🚫🐛 [DEBUG] Parent tab changed. Version: {current_version}",
                    file=current_file, function=current_function, console_print_func=self._print_to_gui_console)

        # Reset all parent tabs to inactive style first
        for tab_name, tab_widget in self.parent_tab_widgets.items():
            self.style.configure(f'Parent.TNotebook.Tab',
                                 background=self.parent_tab_colors[tab_name]["inactive"],
                                 foreground=self.parent_tab_colors[tab_name]["fg_inactive"])

        # Get the currently selected tab
        selected_tab_id = self.parent_notebook.select()
        selected_tab_text = self.parent_notebook.tab(selected_tab_id, "text")
        selected_tab_widget = self.parent_notebook.nametowidget(selected_tab_id)

        # Apply active style to the selected parent tab
        if selected_tab_text in self.parent_tab_colors:
            active_color = self.parent_tab_colors[selected_tab_text]["active"]
            active_fg = self.parent_tab_colors[selected_tab_text]["fg_active"]
            self.style.configure(f'Parent.TNotebook.Tab',
                                 background=active_color,
                                 foreground=active_fg)
            # Also update the background of the child notebook within this parent tab
            if selected_tab_text in self.child_notebooks:
                child_notebook = self.child_notebooks[selected_tab_text]
                # This sets the background of the notebook frame itself
                self.style.configure(f'{selected_tab_text}Child.TNotebook', background=active_color)
                # This sets the background of the *tabs* within the child notebook
                self.style.configure(f'{selected_tab_text}Child.TNotebook.Tab',
                                     background=self.parent_tab_colors[selected_tab_text]["inactive"],
                                     foreground=self.parent_tab_colors[selected_tab_text]["fg_inactive"])
                self.style.map(f'{selected_tab_text}Child.TNotebook.Tab',
                               background=[('selected', active_color), ('active', active_color)],
                               foreground=[('selected', active_fg)],
                               expand=[('selected', [1, 1, 1, 0])])


        # Propagate _on_tab_selected to the active parent tab
        if hasattr(selected_tab_widget, '_on_tab_selected'):
            selected_tab_widget._on_tab_selected(event)
            debug_print(f"🚫🐛 [DEBUG] Propagated _on_tab_selected to active parent tab: {selected_tab_text}. Version: {current_version}",
                        file=current_file, function=current_function, console_print_func=self._print_to_gui_console)
        else:
            debug_print(f"🚫🐛 [DEBUG] Active parent tab {selected_tab_text} has no _on_tab_selected method. Version: {current_version}",
                        file=current_file, function=current_function, console_print_func=self._print_to_gui_console)

    def _ensure_data_directory_exists(self):
        # Function Description:
        # Ensures that the dedicated 'DATA' directory exists one level above the application's root.
        # If the directory does not exist, it creates it.
        #
        # Inputs to this function:
        #   None (operates on self).
        #
        # Process of this function:
        #   1. Uses `self.DATA_FOLDER_PATH` to determine the target directory.
        #   2. Checks if the directory exists using `os.path.exists`.
        #   3. If it doesn't exist, attempts to create it using `os.makedirs(exist_ok=True)`.
        #      `exist_ok=True` prevents an error if the directory already exists (e.g., due to a race condition).
        #   4. Prints informative messages to the console about the directory status.
        #   5. Includes error handling for potential issues during directory creation.
        #
        # Outputs of this function:
        #   None. Ensures the 'DATA' directory is available for file operations.
        #
        # (2025-08-01) Change: New function to create the DATA folder.
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_print(f"Ensuring DATA directory exists at: {self.DATA_FOLDER_PATH}. Version: {current_version}",
                    file=current_file, function=current_function, console_print_func=self._print_to_gui_console)

        try:
            os.makedirs(self.DATA_FOLDER_PATH, exist_ok=True)
            self._print_to_gui_console(f"✅ DATA directory ensured at: {self.DATA_FOLDER_PATH}")
            debug_print(f"DATA directory created or already exists.", file=current_file, function=current_function, console_print_func=self._print_to_gui_console)
        except Exception as e:
            self._print_to_gui_console(f"❌ Error creating DATA directory at {self.DATA_FOLDER_PATH}: {e}")
            debug_print(f"Error creating DATA directory: {e}", file=current_file, function=current_function, console_print_func=self._print_to_gui_console)


if __name__ == "__main__":
    app = App()
    app.mainloop()