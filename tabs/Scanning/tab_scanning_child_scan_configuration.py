# tabs/Scanning/tab_scanning_child_scan_configuration.py
#
# This file defines the ScanTab, a Tkinter Frame that contains the Scan Configuration settings
# and the band selection checkboxes. It includes dropdowns for various scan parameters
# with dynamic descriptions and handles saving/loading configuration.
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
# Version 20250802.0014.7 (Changed __init__ signature to use explicit positional arguments for master and app_instance.)
# Version 20250802.1805.0 (Fixed dropdown freezing by re-introducing description StringVars and linking comboboxes.)
# Version 20250802.1810.0 (Added debug log for ref_scanner_setting_lists.py version to diagnose ImportError.)
# Version 20250802.1915.0 (Fixed AttributeError: 'freq_shift_hz_var' by changing to 'freq_shift_var'.)
# Version 20250802.1920.0 (Added scan_mode_combobox and linked it to app_instance.scan_mode_var.)
# Version 20250802.1930.0 (Removed 'console_print_func' argument from debug_log calls as it's not supported.)

current_version = "20250802.1930.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 1930 * 0 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk, filedialog
import inspect
import os
import subprocess # Added for opening folders
import sys # Import the sys module to fix NameError

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

from src.settings_and_config.config_manager import save_config
from ref.frequency_bands import SCAN_BAND_RANGES, MHZ_TO_HZ, VBW_RBW_RATIO
# Updated import: scan_modes, reference_levels, attenuation_levels, frequency_shifts are now in ref_scanner_setting_lists
from ref.ref_scanner_setting_lists import (
    graph_quality_drop_down,
    dwell_time_drop_down,
    cycle_wait_time_presets,
    reference_level_drop_down,
    frequency_shift_presets,
    number_of_scans_presets,
    rbw_presets,
    scan_modes, # NEW: Import scan_modes
    current_version as ref_scanner_settings_version # Import the version from the ref file
)


class ScanTab(ttk.Frame):
    """
    A Tkinter Frame that contains the Scan Configuration settings
    and the band selection checkboxes.
    """
    # Changed __init__ signature to use explicit positional arguments for master and app_instance
    def __init__(self, master, app_instance, console_print_func, style_obj, **kwargs):
        # This function description tells me what this function does
        # Initializes the ScanTab, setting up the UI frame,
        # linking to the main application instance, and preparing
        # Tkinter variables for scan parameters and band selections.
        #
        # Inputs to this function
        #   master (tk.Widget): The parent widget, typically a ttk.Notebook.
        #   app_instance (object): Reference to the main application instance
        #                          to access shared variables and methods.
        #   console_print_func (function): A function to print messages to the
        #                                  application's console output.
        #   style_obj (ttk.Style): The ttk.Style object for applying styles.
        #   **kwargs: Arbitrary keyword arguments passed to the ttk.Frame constructor.
        #
        # Process of this function
        #   1. Calls the superclass constructor (ttk.Frame).
        #   2. Stores references to app_instance, console_print_func, and style_obj.
        #   3. Initializes Tkinter StringVars for scan name, output folder,
        #      scan mode, reference level, attenuation, frequency shift, RBW segmentation,
        #      and default focus width.
        #   4. Dynamically creates Tkinter BooleanVars for each scan band.
        #   5. Calls _create_widgets to build the UI.
        #
        # Outputs of this function
        #   None. Initializes the Tkinter frame and its internal state.
        #
        # (2025-07-30) Change: Initialized new StringVars for scan parameters and band selections.
        # (20250801.2335.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0014.1) Change: Assigned scan_name_entry and output_folder_entry as attributes for external access.
        # (20250802.0014.2) Change: Handled 'N/A' ValueError for reference_level_dbm_var.
        # (20250802.0014.3) Change: Explicitly filtered style_obj from kwargs passed to super().__init__.
        # (20250802.0014.4) Change: Fixed AttributeError: 'ScanTab' object has no attribute 'style_obj' by passing style_obj.
        # (20250802.0014.5) Change: Ensured scan configuration widgets are exposed as instance attributes.
        # (20250802.0014.6) Change: Updated import for scan_modes to ref_scanner_setting_lists.py.
        # (20250802.0014.7) Change: Changed __init__ signature to use explicit positional arguments for master and app_instance.
        # (20250802.1805.0) Change: Re-introduced description StringVars and linked comboboxes via textvariable.
        # (20250802.1810.0) Change: Added debug log for ref_scanner_setting_lists.py version.
        # (20250802.1915.0) Change: Fixed AttributeError: 'freq_shift_hz_var' by changing to 'freq_shift_var'.
        # (20250802.1920.0) Change: Added scan_mode_combobox and linked it to app_instance.scan_mode_var.
        # (20250802.1930.0) Change: Removed 'console_print_func' argument from debug_log calls.

        # Filter out 'style_obj' from kwargs before passing to super().__init__
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'style_obj'}
        super().__init__(master, style='Dark.TFrame', **filtered_kwargs) # Pass style string, and filtered kwargs
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
        self.style_obj = style_obj # Store the style object

        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing ScanTab. Version: {current_version}. Setting up scan configurations!",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Log the version of the imported ref_scanner_setting_lists.py
        debug_log(f"ref_scanner_setting_lists.py version: {ref_scanner_settings_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Initialize Tkinter variables for descriptions (NEWLY ADDED/UNCOMMENTED)
        self.graph_quality_description_var = tk.StringVar(self, value="")
        self.dwell_time_description_var = tk.StringVar(self, value="")
        self.max_hold_time_description_var = tk.StringVar(self, value="")
        self.scan_rbw_description_var = tk.StringVar(self, value="")
        self.reference_level_description_var = tk.StringVar(self, value="")
        self.frequency_shift_description_var = tk.StringVar(self, value="")
        self.high_sensitivity_description_var = tk.StringVar(self, value="")
        self.preamp_on_description_var = tk.StringVar(self, value="")
        self.num_scan_cycles_description_var = tk.StringVar(self, value="")
        self.scan_mode_description_var = tk.StringVar(self, value="") # NEW: Scan Mode description

        self._create_widgets()

        debug_log(f"ScanTab initialized. Version: {current_version}. Scan configuration interface ready!",
                    file=current_file,
                    version=current_version,
                    function=current_function)


    def _create_widgets(self):
        # This function description tells me what this function does
        # Creates and arranges the widgets for the Scan Configuration tab,
        # including input fields for scan parameters and checkboxes for band selection.
        # It sets up event bindings for dropdowns to update descriptions and saves
        # configuration changes automatically.
        #
        # Inputs to this function
        #   None (operates on self).
        #
        # Process of this function
        #   1. Prints a debug message.
        #   2. Configures the main grid layout for the tab.
        #   3. Creates a LabelFrame for "Scan Parameters" and populates it with
        #      Entry widgets, Comboboxes, and a Button for output folder selection.
        #   4. Creates a Canvas and a Frame for "Band Selection" to allow scrolling
        #      and dynamically adds Checkbuttons for each band from `SCAN_BAND_RANGES`.
        #   5. Binds events for dropdown selections to update descriptions and save config.
        #   6. Binds key release events to Entry widgets to save config.
        #
        # Outputs of this function
        #   None. Modifies the Tkinter frame by adding and arranging widgets.
        #
        # (2025-07-30) Change: Added scan_name_entry and output_folder_entry.
        # (2025-07-30) Change: Implemented dynamic band checkboxes with scrolling.
        # (20250801.2335.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0014.1) Change: Assigned scan_name_entry and output_folder_entry as attributes.
        # (20250802.0014.2) Change: Handled 'N/A' ValueError for reference_level_dbm_var.
        # (20250802.0014.5) Change: Ensured scan configuration widgets are exposed as instance attributes.
        # (20250802.0014.6) Change: No functional changes related to widget creation.
        # (20250802.0014.7) Change: No functional changes related to widget creation.
        # (20250802.1805.0) Change: Linked comboboxes to app_instance's StringVars and updated values format.
        # (20250802.1810.0) Change: No functional changes in _create_widgets.
        # (20250802.1915.0) Change: Fixed AttributeError: 'freq_shift_hz_var' by changing to 'freq_shift_var'.
        # (20250802.1920.0) Change: Added scan_mode_combobox and linked it to app_instance.scan_mode_var.
        # (20250802.1930.0) Change: Removed 'console_print_func' argument from debug_log calls.

        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating ScanTab widgets... Building the scan configuration form! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)

        # Main grid configuration for the tab
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Output settings frame
        self.grid_rowconfigure(1, weight=0) # Scan settings frame
        self.grid_rowconfigure(2, weight=1) # Bands frame should expand vertically

        # Output Folder and Scan Name (Moved to top)
        output_frame = ttk.LabelFrame(self, text="Output Settings", style='Dark.TLabelframe')
        output_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        output_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(output_frame, text="Scan Name:", style='TLabel').grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.scan_name_entry = ttk.Entry(output_frame, textvariable=self.app_instance.scan_name_var, style='TEntry')
        self.scan_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.scan_name_entry.bind("<KeyRelease>", lambda e: save_config(self.app_instance)) # Simplified save_config call

        ttk.Label(output_frame, text="Output Folder:", style='TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.output_folder_entry = ttk.Entry(output_frame, textvariable=self.app_instance.output_folder_var, style='TEntry')
        self.output_folder_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.output_folder_button = ttk.Button(output_frame, text="Browse", command=self._browse_output_folder, style='Blue.TButton')
        self.output_folder_button.grid(row=1, column=2, padx=5, pady=2, sticky="e")

        # NEW: Open Output Folder Button
        ttk.Button(output_frame, text="Open Output Folder", command=self._open_output_folder, style='Blue.TButton').grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")


        # Main frame for Scan Settings
        scan_settings_frame = ttk.LabelFrame(self, text="Scan Settings", style='Dark.TLabelframe')
        scan_settings_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew") # Placed after output_frame

        # Configure columns for Label, Combobox, and Description
        scan_settings_frame.grid_columnconfigure(0, weight=0) # Label column
        scan_settings_frame.grid_columnconfigure(1, weight=0) # Combobox column (fixed width via style)
        scan_settings_frame.grid_columnconfigure(2, weight=1) # Description column (expands)

        row_idx = 0

        # Graph Quality (formerly RBW Step Size)
        ttk.Label(scan_settings_frame, text="Graph Quality:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.graph_quality_combobox = ttk.Combobox(
            scan_settings_frame,
            textvariable=self.app_instance.rbw_step_size_hz_var, # Linked to app_instance's StringVar
            values=[f"{item['resolution_hz']} Hz - {item['label']}" for item in graph_quality_drop_down],
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.graph_quality_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.graph_quality_combobox.bind("<<ComboboxSelected>>", self._on_graph_quality_selected)
        ttk.Label(scan_settings_frame, textvariable=self.graph_quality_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # DWELL (now controls maxhold_time_seconds_var, uses dwell_time_drop_down)
        ttk.Label(scan_settings_frame, text="DWELL (s):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.dwell_time_combobox = ttk.Combobox(
            scan_settings_frame,
            textvariable=self.app_instance.maxhold_time_seconds_var, # Linked to app_instance's StringVar
            values=[f"{item['time_sec']} s - {item['label']}" for item in dwell_time_drop_down],
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.dwell_time_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.dwell_time_combobox.bind("<<ComboboxSelected>>", self._on_dwell_time_selected)
        ttk.Label(scan_settings_frame, textvariable=self.dwell_time_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # Max Hold Time (now controls cycle_wait_time_seconds_var, uses wait_time_presets)
        ttk.Label(scan_settings_frame, text="Max Hold Time (s):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.max_hold_time_combobox = ttk.Combobox(
            scan_settings_frame,
            textvariable=self.app_instance.cycle_wait_time_seconds_var, # Linked to app_instance's StringVar
            values=[f"{item['time_sec']} s - {item['label']}" for item in cycle_wait_time_presets],
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.max_hold_time_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.max_hold_time_combobox.bind("<<ComboboxSelected>>", self._on_max_hold_time_selected)
        ttk.Label(scan_settings_frame, textvariable=self.max_hold_time_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # Scan RBW
        ttk.Label(scan_settings_frame, text="Scan RBW (Hz):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.scan_rbw_combobox = ttk.Combobox(
            scan_settings_frame,
            textvariable=self.app_instance.scan_rbw_hz_var, # Linked to app_instance's StringVar
            values=[f"{item['rbw_hz']} Hz - {item['label']}" for item in rbw_presets],
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.scan_rbw_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.scan_rbw_combobox.bind("<<ComboboxSelected>>", self._on_scan_rbw_selected)
        ttk.Label(scan_settings_frame, textvariable=self.scan_rbw_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # Reference Level
        ttk.Label(scan_settings_frame, text="Reference Level (dBm):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.reference_level_combobox = ttk.Combobox(
            scan_settings_frame,
            textvariable=self.app_instance.reference_level_dbm_var, # Linked to app_instance's StringVar
            values=[f"{item['level_dbm']} dBm - {item['label']}" for item in reference_level_drop_down],
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.reference_level_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.reference_level_combobox.bind("<<ComboboxSelected>>", self._on_reference_level_selected)
        ttk.Label(scan_settings_frame, textvariable=self.reference_level_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # Frequency Shift
        ttk.Label(scan_settings_frame, text="Frequency Shift (Hz):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.frequency_shift_combobox = ttk.Combobox(
            scan_settings_frame,
            textvariable=self.app_instance.freq_shift_var, # Linked to app_instance's StringVar
            values=[f"{item['shift_hz']} Hz - {item['label']}" for item in frequency_shift_presets],
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.frequency_shift_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.frequency_shift_combobox.bind("<<ComboboxSelected>>", self._on_frequency_shift_selected)
        ttk.Label(scan_settings_frame, textvariable=self.frequency_shift_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # High Sensitivity (now Yes/No dropdown)
        ttk.Label(scan_settings_frame, text="High Sensitivity:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.high_sensitivity_combobox = ttk.Combobox(
            scan_settings_frame,
            textvariable=self.app_instance.high_sensitivity_var, # Linked to app_instance's StringVar (will convert bool to "Yes"/"No")
            values=["Yes", "No"],
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.high_sensitivity_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.high_sensitivity_combobox.bind("<<ComboboxSelected>>", self._on_high_sensitivity_selected)
        ttk.Label(scan_settings_frame, textvariable=self.high_sensitivity_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # Preamplifier ON (now Yes/No dropdown)
        ttk.Label(scan_settings_frame, text="Preamplifier ON:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.preamp_on_combobox = ttk.Combobox(
            scan_settings_frame,
            textvariable=self.app_instance.preamp_on_var, # Linked to app_instance's StringVar (will convert bool to "Yes"/"No")
            values=["Yes", "No"],
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.preamp_on_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.preamp_on_combobox.bind("<<ComboboxSelected>>", self._on_preamp_on_selected)
        ttk.Label(scan_settings_frame, textvariable=self.preamp_on_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # Scan RBW Segmentation (remains as entry as it's not in a dropdown list)
        ttk.Label(scan_settings_frame, text="Scan RBW Segmentation (Hz):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.scan_rbw_segmentation_entry = ttk.Entry(scan_settings_frame, textvariable=self.app_instance.scan_rbw_segmentation_var, style='TEntry')
        self.scan_rbw_segmentation_entry.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew", columnspan=2) # Span across combobox and description columns
        self.scan_rbw_segmentation_entry.bind("<KeyRelease>", lambda e: save_config(self.app_instance)) # Simplified save_config call
        row_idx += 1

        # Desired Default Focus Width (remains as entry)
        ttk.Label(scan_settings_frame, text="Default Focus Width (Hz):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.desired_default_focus_width_entry = ttk.Entry(scan_settings_frame, textvariable=self.app_instance.desired_default_focus_width_var, style='TEntry')
        self.desired_default_focus_width_entry.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew", columnspan=2) # Span across combobox and description columns
        self.desired_default_focus_width_entry.bind("<KeyRelease>", lambda e: save_config(self.app_instance)) # Simplified save_config call
        row_idx += 1

        # Number of Scan Cycles
        ttk.Label(scan_settings_frame, text="Number of Scan Cycles:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.num_scan_cycles_combobox = ttk.Combobox(
            scan_settings_frame,
            textvariable=self.app_instance.num_scan_cycles_var, # Linked to app_instance's StringVar
            values=[f"{item['scans']} cycles - {item['label']}" for item in number_of_scans_presets],
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.num_scan_cycles_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.num_scan_cycles_combobox.bind("<<ComboboxSelected>>", self._on_num_scan_cycles_selected)
        ttk.Label(scan_settings_frame, textvariable=self.num_scan_cycles_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1

        # Scan Mode (NEWLY ADDED)
        ttk.Label(scan_settings_frame, text="Scan Mode:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.scan_mode_combobox = ttk.Combobox( # Assign to an instance variable
            scan_settings_frame,
            textvariable=self.app_instance.scan_mode_var,
            values=[item['Value'] for item in scan_modes],
            state="readonly",
            width=35,
            style='Fixedwidth.TCombobox'
        )
        self.scan_mode_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.scan_mode_combobox.bind("<<ComboboxSelected>>", self._on_scan_mode_selected)
        ttk.Label(scan_settings_frame, textvariable=self.scan_mode_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # Frame for Bands to Scan
        bands_frame = ttk.LabelFrame(self, text="Bands to Scan", style='Dark.TLabelframe')
        bands_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew") # Placed after scan_settings_frame
        bands_frame.grid_columnconfigure(0, weight=1) # Single column for checkboxes
        bands_frame.grid_rowconfigure(1, weight=1) # Make the canvas/checkbox area expand vertically

        # Buttons for band selection (Moved above the canvas)
        band_button_frame = ttk.Frame(bands_frame, style='Dark.TFrame')
        band_button_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky="ew") # Span across canvas and scrollbar columns
        band_button_frame.grid_columnconfigure(0, weight=1)
        band_button_frame.grid_columnconfigure(1, weight=1)

        ttk.Button(band_button_frame, text="Select All", command=self._select_all_bands, style='Blue.TButton').grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(band_button_frame, text="Deselect All", command=self._deselect_all_bands, style='Blue.TButton').grid(row=0, column=1, padx=5, pady=5, sticky="ew")


        # Create a canvas and scrollbar for the bands
        self.bands_canvas = tk.Canvas(bands_frame, background="#2e2e2e", highlightthickness=0)
        self.bands_canvas.grid(row=1, column=0, sticky="nsew") # No columnspan needed for single column, placed at row 1

        bands_scrollbar = ttk.Scrollbar(bands_frame, orient="vertical", command=self.bands_canvas.yview)
        bands_scrollbar.grid(row=1, column=1, sticky="ns") # Scrollbar next to canvas, also at row 1

        self.bands_canvas.configure(yscrollcommand=bands_scrollbar.set)
        # Bind the canvas to resize its scrollregion when its size changes
        self.bands_canvas.bind('<Configure>', self._on_bands_canvas_configure)

        # Frame to hold the checkboxes inside the canvas
        self.bands_inner_frame = ttk.Frame(self.bands_canvas, style='Dark.TFrame')
        # Store the window ID returned by create_window
        self.bands_inner_frame_id = self.bands_canvas.create_window((0, 0), window=self.bands_inner_frame, anchor="nw")

        # Bind the inner frame to update the canvas scrollregion when its size changes
        self.bands_inner_frame.bind('<Configure>', lambda e: self.bands_canvas.configure(scrollregion=self.bands_canvas.bbox("all")))


        self.bands_inner_frame.grid_columnconfigure(0, weight=1) # Only one column for checkboxes

        # Populate band checkboxes
        self._populate_band_checkboxes()

        # Apply fixed width style for Comboboxes (adjust this value if needed)
        # Note: width is in characters, not pixels. A value of 35 should make it significantly wider.
        self.app_instance.style.configure('Fixedwidth.TCombobox', width=35)


        debug_log(f"ScanTab widgets created. Scan configuration form is complete! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)

    def _on_bands_canvas_configure(self, event):
        """
        Adjusts the width of the inner frame within the canvas when the canvas is resized.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Configuring bands canvas. Adjusting width for inner frame. Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        if self.bands_inner_frame_id: # Ensure the window item has been created
            self.bands_canvas.itemconfigure(self.bands_inner_frame_id, width=event.width)
        self.bands_canvas.configure(scrollregion=self.bands_canvas.bbox("all"))


    def _populate_band_checkboxes(self): # Renamed from _populate_bands for consistency
        """
        Populates the `bands_inner_frame` with checkboxes for each frequency band
        defined in `SCAN_BAND_RANGES`. Each checkbox is linked to a Tkinter BooleanVar
        and an event handler to save the configuration when its state changes.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Populating band selection checkboxes. Getting all the bands ready! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)

        # Clear existing checkboxes if any
        for widget in self.bands_inner_frame.winfo_children():
            widget.destroy()

        # Arrange checkboxes in a grid within the inner frame
        num_columns = 3 # Adjust as needed
        for i, band_item in enumerate(self.app_instance.band_vars):
            band_name = band_item["band"]["Band Name"]
            start_freq = band_item["band"]["Start MHz"]
            stop_freq = band_item["band"]["Stop MHz"]
            checkbox_text = f"{band_name} ({start_freq:.3f} - {stop_freq:.3f} MHz)"

            checkbox = ttk.Checkbutton(
                self.bands_inner_frame,
                text=checkbox_text,
                variable=band_item["var"],
                command=self._on_band_checkbox_change,
                style='TCheckbutton'
            )
            row = i // num_columns
            col = i % num_columns
            checkbox.grid(row=row, column=col, padx=5, pady=2, sticky="w")
            band_item["var_widget"] = checkbox # Store reference to the widget


        debug_log(f"Band selection checkboxes populated. Ready for selection! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)


    def _on_bands_frame_configure(self, event):
        """
        Configures the scroll region of the `bands_canvas` when the `bands_inner_frame`
        changes size. This ensures the scrollbar correctly reflects the content height.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Configuring bands frame. Adjusting scroll region. Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        self.bands_canvas.configure(scrollregion=self.bands_canvas.bbox("all"))


    def _browse_output_folder(self):
        """
        Opens a file dialog to allow the user to select an output folder for scan data.
        It updates the `output_folder_var` with the selected path and saves the configuration.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Opening folder browser for output directory. Let's pick a place to save scans! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)

        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.app_instance.output_folder_var.set(folder_selected)
            save_config(self.app_instance) # Simplified save_config call
            self.console_print_func(f"✅ Output folder set to: {folder_selected}. Ready for data!")
            debug_log(f"Output folder set to: {folder_selected}. Config saved! Version: {current_version}",
                        file=current_file,
                        version=current_function,
                        function=current_function)
        else:
            self.console_print_func("ℹ️ Output folder selection cancelled. No changes made!")
            debug_log(f"Output folder selection cancelled. Version: {current_version}",
                        file=current_file,
                        version=current_function,
                        function=current_function)

    def _open_output_folder(self):
        """
        Opens the directory specified in the output_folder_var using the default file explorer.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        output_path = self.app_instance.output_folder_var.get()
        debug_log(f"Attempting to open output folder: {output_path}. Version: {current_version}", file=current_file, function=current_function)

        if not output_path:
            self.console_print_func("❌ Output folder path is empty. Please set a folder first.")
            debug_log(f"Output folder path is empty. Version: {current_version}", file=current_file, function=current_function)
            return

        if not os.path.exists(output_path):
            self.console_print_func(f"⚠️ Output folder does not exist: {output_path}. Attempting to create it.")
            debug_log(f"Output folder does not exist: {output_path}. Attempting to create. Version: {current_version}", file=current_file, function=current_function)
            try:
                os.makedirs(output_path)
                self.console_print_func(f"✅ Created output folder: {output_path}")
                debug_log(f"Created output folder: {output_path}. Version: {current_version}", file=current_file, function=current_function)
            except Exception as e:
                self.console_print_func(f"❌ Failed to create output folder: {e}")
                debug_log(f"Failed to create output folder: {e}. Version: {current_version}", file=current_file, function=current_function)
                return

        try:
            if sys.platform == "win32":
                os.startfile(output_path) # For Windows
            elif sys.platform == "darwin":
                subprocess.Popen(["open", output_path]) # For macOS
            else:
                subprocess.Popen(["xdg-open", output_path]) # For Linux
            self.console_print_func(f"✅ Opened output folder: {output_path}")
            debug_log(f"Opened output folder: {output_path}. Version: {current_version}", file=current_file, function=current_function)
        except Exception as e:
            self.console_print_func(f"❌ Error opening output folder: {e}")
            debug_log(f"Error opening output folder '{output_path}': {e}. Version: {current_version}", file=current_file, function=current_function)


    def _on_graph_quality_selected(self, event):
        """
        Event handler for when a graph quality is selected from the dropdown.
        It updates the `app_instance.rbw_step_size_hz_var` and saves the configuration.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Graph Quality selected: {self.app_instance.rbw_step_size_hz_var.get()} Hz. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        # Update description
        selected_value_str = self.graph_quality_combobox.get().split(' ')[0] # Extract the numeric value
        try:
            selected_value = int(float(selected_value_str))
        except ValueError:
            selected_value = None # Handle cases where conversion fails

        for item in graph_quality_drop_down:
            if item["resolution_hz"] == selected_value:
                self.graph_quality_description_var.set(f"{item['label']}: {item['description']}")
                break
        save_config(self.app_instance)


    def _on_dwell_time_selected(self, event):
        """
        Event handler for when a dwell time is selected from the dropdown.
        It updates the `app_instance.maxhold_time_seconds_var` and saves the configuration.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"DWELL time selected: {self.app_instance.maxhold_time_seconds_var.get()} s. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        # Update description
        selected_value_str = self.dwell_time_combobox.get().split(' ')[0] # Extract the numeric value
        try:
            selected_value = float(selected_value_str)
        except ValueError:
            selected_value = None

        for item in dwell_time_drop_down:
            if item["time_sec"] == selected_value:
                self.dwell_time_description_var.set(f"{item['label']}: {item['description']}")
                break
        save_config(self.app_instance)


    def _on_max_hold_time_selected(self, event):
        """
        Event handler for when a max hold time is selected from the dropdown.
        It updates the `app_instance.cycle_wait_time_seconds_var` and saves the configuration.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Max Hold Time selected: {self.app_instance.cycle_wait_time_seconds_var.get()} s. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        # Update description
        selected_value_str = self.max_hold_time_combobox.get().split(' ')[0] # Extract the numeric value
        try:
            selected_value = float(selected_value_str)
        except ValueError:
            selected_value = None

        for item in cycle_wait_time_presets:
            if item["time_sec"] == selected_value:
                self.max_hold_time_description_var.set(f"{item['label']}: {item['description']}")
                break
        save_config(self.app_instance)


    def _on_scan_rbw_selected(self, event):
        """
        Event handler for when a scan RBW is selected from the dropdown.
        It updates the `app_instance.scan_rbw_hz_var` and saves the configuration.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Scan RBW selected: {self.app_instance.scan_rbw_hz_var.get()} Hz. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        # Update description
        selected_value_str = self.scan_rbw_combobox.get().split(' ')[0] # Extract the numeric value
        try:
            selected_value = float(selected_value_str)
        except ValueError:
            selected_value = None

        for item in rbw_presets:
            if item["rbw_hz"] == selected_value:
                self.scan_rbw_description_var.set(f"{item['label']}: {item['description']}")
                break
        save_config(self.app_instance)


    def _on_reference_level_selected(self, event):
        """
        Event handler for when a reference level is selected from the dropdown.
        It updates the `app_instance.reference_level_dbm_var` and saves the configuration.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Reference level selected: {self.app_instance.reference_level_dbm_var.get()} dBm. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        # Update description
        selected_value_str = self.reference_level_combobox.get().split(' ')[0] # Extract the numeric value
        try:
            selected_value = float(selected_value_str)
        except ValueError:
            selected_value = None

        for item in reference_level_drop_down:
            if item["level_dbm"] == selected_value:
                self.reference_level_description_var.set(f"{item['label']}: {item['description']}")
                break
        save_config(self.app_instance)


    def _on_frequency_shift_selected(self, event):
        """
        Event handler for when a frequency shift is selected from the dropdown.
        It updates the `app_instance.freq_shift_var` and saves the configuration.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Frequency shift selected: {self.app_instance.freq_shift_var.get()} Hz. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        # Update description
        selected_value_str = self.frequency_shift_combobox.get().split(' ')[0] # Extract the numeric value
        try:
            selected_value = float(selected_value_str)
        except ValueError:
            selected_value = None

        for item in frequency_shift_presets:
            if item["shift_hz"] == selected_value:
                self.frequency_shift_description_var.set(f"{item['label']}: {item['description']}")
                break
        save_config(self.app_instance)


    def _on_high_sensitivity_selected(self, event):
        """
        Event handler for when High Sensitivity is selected from the dropdown.
        It updates the `app_instance.high_sensitivity_var` and saves the configuration.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"High Sensitivity selected: {self.app_instance.high_sensitivity_var.get()}. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        # Update description
        selected_value = self.high_sensitivity_combobox.get()
        if selected_value == "Yes":
            self.high_sensitivity_description_var.set("Yes: High sensitivity mode enabled, optimizing for detection of weak signals.")
        else:
            self.high_sensitivity_description_var.set("No: High sensitivity mode disabled, potentially faster scans but less sensitive.")
        save_config(self.app_instance)


    def _on_preamp_on_selected(self, event):
        """
        Event handler for when Preamplifier ON is selected from the dropdown.
        It updates the `app_instance.preamp_on_var` and saves the configuration.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Preamplifier ON selected: {self.app_instance.preamp_on_var.get()}. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        # Update description
        selected_value = self.preamp_on_combobox.get()
        if selected_value == "Yes":
            self.preamp_on_description_var.set("Yes: Preamplifier is enabled, increasing sensitivity but potentially adding noise.")
        else:
            self.preamp_on_description_var.set("No: Preamplifier is disabled, reducing sensitivity but potentially cleaner signal.")
        save_config(self.app_instance)


    def _on_num_scan_cycles_selected(self, event):
        """
        Event handler for when Number of Scan Cycles is selected from the dropdown.
        It updates the `app_instance.num_scan_cycles_var` and saves the configuration.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Number of Scan Cycles selected: {self.app_instance.num_scan_cycles_var.get()}. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        # Update description
        selected_value_str = self.num_scan_cycles_combobox.get().split(' ')[0] # Extract the numeric value
        try:
            selected_value = int(float(selected_value_str))
        except ValueError:
            selected_value = None

        for item in number_of_scans_presets:
            if item["scans"] == selected_value:
                self.num_scan_cycles_description_var.set(f"{item['label']}: {item['description']}")
                break
        save_config(self.app_instance)


    def _on_scan_mode_selected(self, event):
        """
        Event handler for when Scan Mode is selected from the dropdown.
        It updates the `app_instance.scan_mode_var` and saves the configuration.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Scan Mode selected: {self.app_instance.scan_mode_var.get()}. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        # Update description
        selected_value = self.scan_mode_combobox.get()
        found_item = next((item for item in scan_modes if item['Value'] == selected_value), None)
        if found_item:
            self.scan_mode_description_var.set(found_item['Description'])
        else:
            self.scan_mode_description_var.set("No matching description.")
        save_config(self.app_instance)


    def _select_all_bands(self):
        """
        Selects all band checkboxes and updates the configuration.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Selecting all bands. Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        for band_item in self.app_instance.band_vars:
            band_item["var"].set(True)
        self._on_band_checkbox_change() # Trigger save


    def _deselect_all_bands(self):
        """
        Deselects all band checkboxes and updates the configuration.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Deselecting all bands. Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        for band_item in self.app_instance.band_vars:
            band_item["var"].set(False)
        self._on_band_checkbox_change() # Trigger save


    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Can be used to refresh data or update UI elements specific to this tab.
        For the scan configuration, we ensure settings are loaded/reloaded.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"ScanTab selected. Refreshing settings... Let's get this updated! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        self._load_current_settings_into_dropdowns()
        self._load_band_selections_from_config()
        debug_log(f"ScanTab refreshed. Settings are up-to-date! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)


    def _load_band_selections_from_config(self):
        """
        Loads the selected bands from config.ini into the checkboxes.
        This is called on tab selection to ensure the GUI reflects the config.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Loading band selections from config.ini... Syncing checkboxes with saved settings! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)

        # Get the last used selected bands from config using the new prefixed key
        last_selected_bands_str = self.app_instance.config.get('LAST_USED_SETTINGS', 'last_scan_configuration__selected_bands', fallback='')
        last_selected_band_names = [name.strip() for name in last_selected_bands_str.split(',') if name.strip()]

        # Set the state of each checkbox based on the loaded bands
        for band_item in self.app_instance.band_vars:
            band_name = band_item["band"]["Band Name"]
            band_item["var"].set(band_name in last_selected_band_names)

        debug_log(f"Loaded selected bands from config: {last_selected_band_names}. Checkboxes updated! Version: {current_version}", file=current_file, function=current_function)


    def _on_band_checkbox_change(self):
        """
        Event handler for when a band selection checkbox is toggled.
        It updates the 'last_scan_configuration__selected_bands' setting in the config.ini.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Band checkbox changed. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)

        selected_bands = [
            band_item["band"]["Band Name"]
            for band_item in self.app_instance.band_vars
            if band_item["var"].get()
        ]
        self.app_instance.config.set(
            'LAST_USED_SETTINGS',
            'last_scan_configuration__selected_bands',
            ",".join(selected_bands)
        )
        save_config(self.app_instance)
        debug_log(f"Selected bands saved: {selected_bands}. Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)


    def _load_current_settings_into_dropdowns(self):
        """
        Loads the current values from app_instance's Tkinter variables into the comboboxes
        and updates their corresponding description labels. This ensures the GUI reflects
        the loaded configuration when the tab is selected.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Loading current settings into dropdowns. Syncing UI with config! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)

        # Graph Quality
        current_value = self.app_instance.rbw_step_size_hz_var.get()
        found_item = next((item for item in graph_quality_drop_down if str(item['resolution_hz']) == current_value), None)
        if found_item:
            self.graph_quality_combobox.set(f"{found_item['resolution_hz']} Hz - {found_item['label']}")
            self.graph_quality_description_var.set(f"{found_item['label']}: {found_item['description']}")
        else:
            self.graph_quality_combobox.set("")
            self.graph_quality_description_var.set("No matching description.")

        # DWELL
        current_value = self.app_instance.maxhold_time_seconds_var.get()
        found_item = next((item for item in dwell_time_drop_down if str(item['time_sec']) == current_value), None)
        if found_item:
            self.dwell_time_combobox.set(f"{found_item['time_sec']} s - {found_item['label']}")
            self.dwell_time_description_var.set(f"{found_item['label']}: {found_item['description']}")
        else:
            self.dwell_time_combobox.set("")
            self.dwell_time_description_var.set("No matching description.")

        # Max Hold Time
        current_value = self.app_instance.cycle_wait_time_seconds_var.get()
        found_item = next((item for item in cycle_wait_time_presets if str(item['time_sec']) == current_value), None)
        if found_item:
            self.max_hold_time_combobox.set(f"{found_item['time_sec']} s - {found_item['label']}")
            self.max_hold_time_description_var.set(f"{found_item['label']}: {found_item['description']}")
        else:
            self.max_hold_time_combobox.set("")
            self.max_hold_time_description_var.set("No matching description.")

        # Scan RBW
        current_value = self.app_instance.scan_rbw_hz_var.get()
        found_item = next((item for item in rbw_presets if str(item['rbw_hz']) == current_value), None)
        if found_item:
            self.scan_rbw_combobox.set(f"{found_item['rbw_hz']} Hz - {found_item['label']}")
            self.scan_rbw_description_var.set(f"{found_item['label']}: {found_item['description']}")
        else:
            self.scan_rbw_combobox.set("")
            self.scan_rbw_description_var.set("No matching description.")

        # Reference Level
        current_value = self.app_instance.reference_level_dbm_var.get()
        found_item = next((item for item in reference_level_drop_down if str(item['level_dbm']) == current_value), None)
        if found_item:
            self.reference_level_combobox.set(f"{found_item['level_dbm']} dBm - {found_item['label']}")
            self.reference_level_description_var.set(f"{found_item['label']}: {found_item['description']}")
        else:
            self.reference_level_combobox.set("")
            self.reference_level_description_var.set("No matching description.")

        # Frequency Shift
        current_value = self.app_instance.freq_shift_var.get() # Corrected variable name
        found_item = next((item for item in frequency_shift_presets if str(item['shift_hz']) == current_value), None)
        if found_item:
            self.frequency_shift_combobox.set(f"{found_item['shift_hz']} Hz - {found_item['label']}")
            self.frequency_shift_description_var.set(f"{item['label']}: {item['description']}")
        else:
            self.frequency_shift_combobox.set("")
            self.frequency_shift_description_var.set("No matching description.")

        # High Sensitivity
        current_value_bool = self.app_instance.high_sensitivity_var.get()
        current_value_str = "Yes" if current_value_bool else "No"
        self.high_sensitivity_combobox.set(current_value_str)
        if current_value_str == "Yes":
            self.high_sensitivity_description_var.set("Yes: High sensitivity mode enabled, optimizing for detection of weak signals.")
        else:
            self.high_sensitivity_description_var.set("No: High sensitivity mode disabled, potentially faster scans but less sensitive.")

        # Preamplifier ON
        current_value_bool = self.app_instance.preamp_on_var.get()
        current_value_str = "Yes" if current_value_bool else "No"
        self.preamp_on_combobox.set(current_value_str)
        if current_value_str == "Yes":
            self.preamp_on_description_var.set("Yes: Preamplifier is enabled, increasing sensitivity but potentially adding noise.")
        else:
            self.preamp_on_description_var.set("No: Preamplifier is disabled, reducing sensitivity but potentially cleaner signal.")

        # Number of Scan Cycles
        current_value = self.app_instance.num_scan_cycles_var.get()
        found_item = next((item for item in number_of_scans_presets if str(item['scans']) == str(current_value)), None)
        if found_item:
            self.num_scan_cycles_combobox.set(f"{found_item['scans']} cycles - {found_item['label']}")
            self.num_scan_cycles_description_var.set(f"{found_item['label']}: {found_item['description']}")
        else:
            self.num_scan_cycles_combobox.set("")
            self.num_scan_cycles_description_var.set("No matching description.")

        # Scan Mode (NEWLY ADDED)
        current_value = self.app_instance.scan_mode_var.get()
        found_item = next((item for item in scan_modes if item['Value'] == current_value), None)
        if found_item:
            self.scan_mode_combobox.set(found_item['Value'])
            self.scan_mode_description_var.set(found_item['Description'])
        else:
            self.scan_mode_combobox.set("")
            self.scan_mode_description_var.set("No matching description.")

        debug_log(f"Current settings loaded into dropdowns and descriptions updated. Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
