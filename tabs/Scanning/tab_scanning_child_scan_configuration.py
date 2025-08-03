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
# Version 20250802.2010.0 (Ensured dropdowns store raw values in config.ini, not display strings.)
# Version 20250802.2020.0 (Fixed KeyError: 'time_s' by adding checks for missing keys in combobox value generation and parsing.)
# Version 20250802.2030.0 (Fixed AttributeError: 'desired_default_focus_width_combobox' by changing it from Entry to Combobox.)

current_version = "20250802.2030.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 2030 * 0 # Example hash, adjust as needed

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
    attenuation_levels, # Ensure this is imported
    current_version as ref_scanner_settings_version # Import the version from the ref file
)


class ScanTab(ttk.Frame):
    """
    Function Description:
    A Tkinter Frame that serves as a child tab for Scan Configuration settings.
    It includes input fields and dropdowns for various scan parameters,
    such as scan name, output folder, number of cycles, RBW step size,
    and band selection checkboxes. It handles the display and saving
    of these settings.

    Inputs to the constructor:
        master (tk.Widget): The parent widget (e.g., ttk.Notebook).
        app_instance (object): A reference to the main application instance.
                               This allows access to shared variables and methods.
        console_print_func (callable): A function to print messages to the console.
        style_obj (ttk.Style): The ttk.Style object for applying styles.
        **kwargs: Arbitrary keyword arguments passed to the ttk.Frame constructor.

    Process of the constructor:
        1. Calls the superclass constructor (ttk.Frame).
        2. Stores references to `app_instance` and `console_print_func`.
        3. Initializes Tkinter StringVars for combobox descriptions.
        4. Creates and arranges GUI widgets for:
            - Scan Name and Output Folder.
            - Scan Parameters (Number of Cycles, RBW Step Size, Cycle Wait Time, Maxhold Time).
            - Instrument Settings for Scan (Scan RBW, Reference Level, Attenuation, Frequency Shift, Scan Mode).
            - Checkboxes for Maxhold, High Sensitivity, Preamplifier.
            - Band selection checkboxes.
        5. Calls `_create_widgets` to build the UI.
        6. Calls `_load_current_settings_into_dropdowns` to populate comboboxes.
        7. Calls `_load_band_selections_from_config` to set band checkbox states.

    Outputs of the constructor:
        An initialized ScanTab instance.
    """
    def __init__(self, master, app_instance, console_print_func, style_obj, **kwargs):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing ScanTab. Setting up scan configuration UI. Version: {current_version}",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

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
                    version=current_version, # Corrected to current_version
                    function=current_function)

        # Initialize Tkinter variables for descriptions
        self.graph_quality_description_var = tk.StringVar(self, value="")
        self.dwell_time_description_var = tk.StringVar(self, value="")
        self.max_hold_time_description_var = tk.StringVar(self, value="")
        self.scan_rbw_description_var = tk.StringVar(self, value="")
        self.reference_level_description_var = tk.StringVar(self, value="")
        self.attenuation_description_var = tk.StringVar(self, value="") # NEW: Attenuation description
        self.frequency_shift_description_var = tk.StringVar(self, value="")
        self.high_sensitivity_description_var = tk.StringVar(self, value="")
        self.preamp_on_description_var = tk.StringVar(self, value="")
        self.num_scan_cycles_description_var = tk.StringVar(self, value="")
        self.scan_mode_description_var = tk.StringVar(self, value="") # NEW: Scan Mode description
        self.desired_default_focus_width_description_var = tk.StringVar(self, value="") # NEW: Default Focus Width description

        # Local StringVars for combobox display values (these will hold the formatted strings)
        self._graph_quality_display_var = tk.StringVar(self)
        self._dwell_time_display_var = tk.StringVar(self)
        self._max_hold_time_display_var = tk.StringVar(self)
        self._scan_rbw_display_var = tk.StringVar(self)
        self._reference_level_display_var = tk.StringVar(self)
        self._attenuation_display_var = tk.StringVar(self)
        self._frequency_shift_display_var = tk.StringVar(self)
        self._high_sensitivity_display_var = tk.StringVar(self)
        self._preamp_on_display_var = tk.StringVar(self)
        self._num_scan_cycles_display_var = tk.StringVar(self)
        self._scan_mode_display_var = tk.StringVar(self)
        self._desired_default_focus_width_display_var = tk.StringVar(self)


        self._create_widgets()
        # No need for _setup_trace_callbacks here, traces are on app_instance vars
        self._load_current_settings_into_dropdowns() # Load values into comboboxes after creation
        self._load_band_selections_from_config()

        debug_log(f"ScanTab initialized. Version: {current_version}. Scan configuration interface ready!",
                    file=current_file,
                    version=current_version,
                    function=current_function)


    def _create_widgets(self):
        """
        Function Description:
        Creates and arranges all the GUI widgets within the Scan Configuration tab.
        This includes labels, entry fields, comboboxes for various settings,
        and checkboxes for band selection.

        Inputs:
            None (operates on self).

        Process of this function:
            1. Sets up the grid layout for the frame.
            2. Creates and places widgets for:
                - Scan Name and Output Folder with a browse button.
                - Dropdowns for Number of Scan Cycles, RBW Step Size, Cycle Wait Time, Maxhold Time.
                - Dropdowns for Scan RBW, Reference Level, Attenuation, Frequency Shift, Scan Mode.
                - Checkboxes for Maxhold, High Sensitivity, Preamplifier On.
                - Band selection checkboxes dynamically generated from `SCAN_BAND_RANGES`.
            3. Configures comboboxes with values and binds them to description variables.

        Outputs of this function:
            None. Populates the ScanTab frame with GUI elements.
        """
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
        self.scan_name_entry.bind("<KeyRelease>", lambda e: save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)) # Use full save_config call

        ttk.Label(output_frame, text="Output Folder:", style='TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.output_folder_entry = ttk.Entry(output_frame, textvariable=self.app_instance.output_folder_var, style='TEntry')
        self.output_folder_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.browse_output_folder_button = ttk.Button(output_frame, text="Browse", command=self._browse_output_folder, style='Blue.TButton')
        self.browse_output_folder_button.grid(row=1, column=2, padx=5, pady=2, sticky="e")

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
            textvariable=self._graph_quality_display_var, # Linked to local display StringVar
            values=[f"{item['resolution_hz']} Hz - {item['label']}" for item in graph_quality_drop_down if 'resolution_hz' in item and 'label' in item],
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.graph_quality_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.graph_quality_combobox.bind("<<ComboboxSelected>>", lambda e: self._on_combobox_select(e, self.app_instance.rbw_step_size_hz_var, graph_quality_drop_down, 'resolution_hz', self.graph_quality_description_var, 'label', 'description', "{item[resolution_hz]} Hz - {label}"))
        ttk.Label(scan_settings_frame, textvariable=self.graph_quality_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # DWELL (now controls maxhold_time_seconds_var, uses dwell_time_drop_down)
        ttk.Label(scan_settings_frame, text="DWELL (s):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.dwell_time_combobox = ttk.Combobox(
            scan_settings_frame,
            textvariable=self._dwell_time_display_var, # Linked to local display StringVar
            values=[f"{item['time_s']} s - {item['label']}" for item in dwell_time_drop_down if 'time_s' in item and 'label' in item], # Added check for 'time_s' and 'label'
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.dwell_time_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.dwell_time_combobox.bind("<<ComboboxSelected>>", lambda e: self._on_combobox_select(e, self.app_instance.maxhold_time_seconds_var, dwell_time_drop_down, 'time_s', self.dwell_time_description_var, 'label', 'description', "{item[time_s]} s - {label}"))
        ttk.Label(scan_settings_frame, textvariable=self.dwell_time_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # Max Hold Time (now controls cycle_wait_time_seconds_var, uses wait_time_presets)
        ttk.Label(scan_settings_frame, text="Max Hold Time (s):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.max_hold_time_combobox = ttk.Combobox(
            scan_settings_frame,
            textvariable=self._max_hold_time_display_var, # Linked to local display StringVar
            values=[f"{item['time_s']} s - {item['label']}" for item in cycle_wait_time_presets if 'time_s' in item and 'label' in item], # Added check for 'time_s' and 'label'
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.max_hold_time_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.max_hold_time_combobox.bind("<<ComboboxSelected>>", lambda e: self._on_combobox_select(e, self.app_instance.cycle_wait_time_seconds_var, cycle_wait_time_presets, 'time_s', self.max_hold_time_description_var, 'label', 'description', "{item[time_s]} s - {label}"))
        ttk.Label(scan_settings_frame, textvariable=self.max_hold_time_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # Scan RBW
        ttk.Label(scan_settings_frame, text="Scan RBW (Hz):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.scan_rbw_combobox = ttk.Combobox(
            scan_settings_frame,
            textvariable=self._scan_rbw_display_var, # Linked to local display StringVar
            values=[f"{item['rbw_hz']} Hz - {item['label']}" for item in rbw_presets if 'rbw_hz' in item and 'label' in item],
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.scan_rbw_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.scan_rbw_combobox.bind("<<ComboboxSelected>>", lambda e: self._on_combobox_select(e, self.app_instance.scan_rbw_hz_var, rbw_presets, 'rbw_hz', self.scan_rbw_description_var, 'label', 'description', "{item[rbw_hz]} Hz - {label}"))
        ttk.Label(scan_settings_frame, textvariable=self.scan_rbw_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # Reference Level
        ttk.Label(scan_settings_frame, text="Reference Level (dBm):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.reference_level_combobox = ttk.Combobox(
            scan_settings_frame,
            textvariable=self._reference_level_display_var, # Linked to local display StringVar
            values=[f"{item['Value']} dBm - {item['Description']}" for item in reference_level_drop_down if 'Value' in item and 'Description' in item],
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.reference_level_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.reference_level_combobox.bind("<<ComboboxSelected>>", lambda e: self._on_combobox_select(e, self.app_instance.reference_level_dbm_var, reference_level_drop_down, 'Value', self.reference_level_description_var, 'Description', 'Description', "{item[Value]} dBm - {label}"))
        ttk.Label(scan_settings_frame, textvariable=self.reference_level_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1

        # Attenuation
        ttk.Label(scan_settings_frame, text="Attenuation (dB):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.attenuation_combobox = ttk.Combobox(
            scan_settings_frame,
            textvariable=self._attenuation_display_var, # Linked to local display StringVar
            values=[f"{item['Value']} dB - {item['Description']}" for item in attenuation_levels if 'Value' in item and 'Description' in item],
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.attenuation_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.attenuation_combobox.bind("<<ComboboxSelected>>", lambda e: self._on_combobox_select(e, self.app_instance.attenuation_var, attenuation_levels, 'Value', self.attenuation_description_var, 'Description', 'Description', "{item[Value]} dB - {label}"))
        ttk.Label(scan_settings_frame, textvariable=self.attenuation_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1

        # Frequency Shift
        ttk.Label(scan_settings_frame, text="Frequency Shift (Hz):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.frequency_shift_combobox = ttk.Combobox(
            scan_settings_frame,
            textvariable=self._frequency_shift_display_var, # Linked to local display StringVar
            values=[f"{item['shift_hz']} Hz - {item['Description']}" for item in frequency_shift_presets if 'shift_hz' in item and 'Description' in item],
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.frequency_shift_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.frequency_shift_combobox.bind("<<ComboboxSelected>>", lambda e: self._on_combobox_select(e, self.app_instance.freq_shift_var, frequency_shift_presets, 'shift_hz', self.frequency_shift_description_var, 'Description', 'Description', "{item[shift_hz]} Hz - {label}"))
        ttk.Label(scan_settings_frame, textvariable=self.frequency_shift_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # High Sensitivity (now Yes/No dropdown)
        ttk.Label(scan_settings_frame, text="High Sensitivity:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.high_sensitivity_combobox = ttk.Combobox(
            scan_settings_frame,
            textvariable=self._high_sensitivity_display_var, # Linked to local display StringVar
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
            textvariable=self._preamp_on_display_var, # Linked to local display StringVar
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
        self.scan_rbw_segmentation_entry.bind("<KeyRelease>", lambda e: save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)) # Use full save_config call
        row_idx += 1

        # Desired Default Focus Width (CHANGED FROM ENTRY TO COMBOBOX)
        ttk.Label(scan_settings_frame, text="Default Focus Width (Hz):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.desired_default_focus_width_combobox = ttk.Combobox( # Changed to combobox
            scan_settings_frame,
            textvariable=self._desired_default_focus_width_display_var, # Linked to local display StringVar
            values=[f"{item['resolution_hz']} Hz - {item['label']}" for item in graph_quality_drop_down if 'resolution_hz' in item and 'label' in item],
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.desired_default_focus_width_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.desired_default_focus_width_combobox.bind("<<ComboboxSelected>>", lambda e: self._on_combobox_select(e, self.app_instance.desired_default_focus_width_var, graph_quality_drop_down, 'resolution_hz', self.desired_default_focus_width_description_var, 'label', 'description', "{item[resolution_hz]} Hz - {label}"))
        ttk.Label(scan_settings_frame, textvariable=self.desired_default_focus_width_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1

        # Number of Scan Cycles
        ttk.Label(scan_settings_frame, text="Number of Scan Cycles:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.num_scan_cycles_combobox = ttk.Combobox(
            scan_settings_frame,
            textvariable=self._num_scan_cycles_display_var, # Linked to local display StringVar
            values=[f"{item['scans']} cycles - {item['label']}" for item in number_of_scans_presets if 'scans' in item and 'label' in item],
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.num_scan_cycles_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.num_scan_cycles_combobox.bind("<<ComboboxSelected>>", lambda e: self._on_combobox_select(e, self.app_instance.num_scan_cycles_var, number_of_scans_presets, 'scans', self.num_scan_cycles_description_var, 'label', 'description', "{item[scans]} cycles - {label}"))
        ttk.Label(scan_settings_frame, textvariable=self.num_scan_cycles_description_var, wraplength=350, justify="left", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1

        # Scan Mode (NEWLY ADDED)
        ttk.Label(scan_settings_frame, text="Scan Mode:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.scan_mode_combobox = ttk.Combobox( # Assign to an instance variable
            scan_settings_frame,
            textvariable=self._scan_mode_display_var, # Linked to local display StringVar
            values=[item['Value'] for item in scan_modes if 'Value' in item],
            state="readonly",
            width=35,
            style='Fixedwidth.TCombobox'
        )
        self.scan_mode_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.scan_mode_combobox.bind("<<ComboboxSelected>>", lambda e: self._on_combobox_select(e, self.app_instance.scan_mode_var, scan_modes, 'Value', self.scan_mode_description_var, 'Description', 'Description', "{item[Value]}"))
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
            save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance) # Use full save_config call
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


    def _on_combobox_select(self, event, tk_var, data_list, value_key, description_tk_var, label_key, description_key, display_format_string):
        """
        Generic callback for combobox selections.
        When an item is selected, it extracts the raw value from the corresponding
        data item in the provided list and updates the associated Tkinter variable.
        It also updates the description label.

        Inputs:
            event: The Tkinter event object.
            tk_var (tk.StringVar/DoubleVar/IntVar): The Tkinter variable to update with the raw value.
            data_list (list): The list of dictionaries (e.g., rbw_presets) from ref_scanner_setting_lists.
            value_key (str): The key in the dictionary that holds the raw value (e.g., 'rbw_hz', 'scans', 'Value', 'shift_hz').
            description_tk_var (tk.StringVar): The Tkinter variable for the description label.
            label_key (str): The key in the dictionary that holds the display label (e.g., 'label', 'Description', 'Value').
            description_key (str): The key in the dictionary that holds the full description.
            display_format_string (str): A format string to reconstruct the display value (e.g., "{item[resolution_hz]} Hz - {label}").

        Process of this function:
            1. Gets the currently selected display value from the combobox.
            2. Iterates through `data_list` to find the matching item based on the display value.
            3. Extracts the raw value using `value_key` and sets it to `tk_var`.
            4. Extracts the description using `description_key` and sets it to `description_tk_var`.
            5. Logs the update.

        Outputs of this function:
            None. Updates Tkinter variables and UI labels.
        """
        current_function = inspect.currentframe().f_code.co_name
        selected_display_value = event.widget.get()
        debug_log(f"Combobox selected: '{selected_display_value}'. Parsing and updating Tkinter var. Version: {current_version}",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        found_item = None
        for item in data_list:
            # Reconstruct the expected display value for comparison
            # Ensure keys exist before accessing
            if value_key not in item or label_key not in item or description_key not in item:
                debug_log(f"Skipping malformed item in data_list: {item}. Missing required keys.",
                            file=os.path.basename(__file__),
                            version=current_version,
                            function=current_function)
                continue

            if isinstance(tk_var, tk.BooleanVar):
                expected_display = "Yes" if item[value_key] else "No"
            else:
                try:
                    expected_display = display_format_string.format(item=item, label=item[label_key], value=item[value_key])
                except KeyError:
                    # Fallback if a key is missing in the item for the format string
                    expected_display = str(item[value_key]) # Fallback to just the raw value

            if str(selected_display_value) == str(expected_display):
                found_item = item
                break

        if found_item:
            # Set the raw value to the Tkinter variable
            if isinstance(tk_var, tk.BooleanVar):
                tk_var.set(found_item[value_key]) # Set boolean directly
            else:
                tk_var.set(str(found_item[value_key])) # Set string representation of raw value
            debug_log(f"Set {tk_var._name} to raw value: {tk_var.get()}. Version: {current_version}",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)

            # Update the description label
            description_tk_var.set(found_item[description_key])
            debug_log(f"Updated description for {tk_var._name}: {found_item[description_key]}. Version: {current_version}",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
        else:
            debug_log(f"WARNING: Could not find matching item for selected display value: '{selected_display_value}' in data list for {tk_var._name}. Version: {current_version}",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            # Optionally clear the Tkinter variable or set a default
            # tk_var.set("")
            # description_tk_var.set("No matching description.")


    def _on_high_sensitivity_selected(self, event):
        """
        Event handler for when High Sensitivity is selected from the dropdown.
        It updates the `app_instance.high_sensitivity_var` (BooleanVar) and saves the configuration.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        selected_value = self._high_sensitivity_display_var.get() # Get from local display var
        
        # Update app_instance's BooleanVar based on selection
        self.app_instance.high_sensitivity_var.set(selected_value == "Yes")

        debug_log(f"High Sensitivity selected: {self.app_instance.high_sensitivity_var.get()}. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        
        # Update description
        if selected_value == "Yes":
            self.high_sensitivity_description_var.set("Yes: High sensitivity mode enabled, optimizing for detection of weak signals.")
        else:
            self.high_sensitivity_description_var.set("No: High sensitivity mode disabled, potentially faster scans but less sensitive.")
        
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)


    def _on_preamp_on_selected(self, event):
        """
        Event handler for when Preamplifier ON is selected from the dropdown.
        It updates the `app_instance.preamp_on_var` (BooleanVar) and saves the configuration.
        """
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        selected_value = self._preamp_on_display_var.get() # Get from local display var

        # Update app_instance's BooleanVar based on selection
        self.app_instance.preamp_on_var.set(selected_value == "Yes")

        debug_log(f"Preamplifier ON selected: {self.app_instance.preamp_on_var.get()}. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        
        # Update description
        if selected_value == "Yes":
            self.preamp_on_description_var.set("Yes: Preamplifier is enabled, increasing sensitivity but potentially adding noise.")
        else:
            self.preamp_on_description_var.set("No: Preamplifier is disabled, reducing sensitivity but potentially cleaner signal.")
        
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)


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
                    function=current_function,
                    special=True) # Adding special flag as per your style

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
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
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

        # Helper to set combobox display and description based on raw value
        def _set_combobox_display_and_description(combobox_widget, app_tk_var, data_list, value_key, description_tk_var, label_key, description_key, display_format_string):
            current_raw_value = app_tk_var.get()
            found_item = None

            # Special handling for boolean vars (High Sensitivity, Preamplifier ON)
            if isinstance(app_tk_var, tk.BooleanVar):
                # Find item where value_key matches the boolean state
                found_item = next((item for item in data_list if item.get(value_key) == current_raw_value), None) # Use .get() for safety
                if found_item:
                    display_value = "Yes" if current_raw_value else "No"
                    combobox_widget.set(display_value)
                    description_tk_var.set(found_item.get(description_key, "No matching description.")) # Use .get() for safety
                else:
                    combobox_widget.set("No") # Default to "No" if not found
                    description_tk_var.set("No matching description.")
                return

            # For other types (numerical, string)
            for item in data_list:
                # Use .get() for safe access and ensure all required keys exist
                if (value_key in item and label_key in item and description_key in item and
                    str(item.get(value_key)) == str(current_raw_value)):
                    found_item = item
                    break
            
            if found_item:
                try:
                    combobox_widget.set(display_format_string.format(item=found_item, label=found_item.get(label_key, ''), value=found_item.get(value_key, ''))) # Use .get() for safety
                except KeyError:
                    combobox_widget.set(str(found_item.get(value_key, ''))) # Fallback
                description_tk_var.set(found_item.get(description_key, "No matching description.")) # Use .get() for safety
            else:
                combobox_widget.set("")
                description_tk_var.set("No matching description.")
                debug_log(f"No matching item found for {app_tk_var._name} with raw value '{current_raw_value}'. Setting to blank. Version: {current_version}",
                            file=current_file,
                            version=current_function,
                            function=current_function)


        # Graph Quality
        _set_combobox_display_and_description(self.graph_quality_combobox, self.app_instance.rbw_step_size_hz_var, graph_quality_drop_down, 'resolution_hz', self.graph_quality_description_var, 'label', 'description', "{item[resolution_hz]} Hz - {label}")

        # DWELL
        _set_combobox_display_and_description(self.dwell_time_combobox, self.app_instance.maxhold_time_seconds_var, dwell_time_drop_down, 'time_s', self.dwell_time_description_var, 'label', 'description', "{item[time_s]} s - {label}")

        # Max Hold Time
        _set_combobox_display_and_description(self.max_hold_time_combobox, self.app_instance.cycle_wait_time_seconds_var, cycle_wait_time_presets, 'time_s', self.max_hold_time_description_var, 'label', 'description', "{item[time_s]} s - {label}")

        # Scan RBW
        _set_combobox_display_and_description(self.scan_rbw_combobox, self.app_instance.scan_rbw_hz_var, rbw_presets, 'rbw_hz', self.scan_rbw_description_var, 'label', 'description', "{item[rbw_hz]} Hz - {label}")

        # Reference Level
        _set_combobox_display_and_description(self.reference_level_combobox, self.app_instance.reference_level_dbm_var, reference_level_drop_down, 'Value', self.reference_level_description_var, 'Description', 'Description', "{item[Value]} dBm - {label}")

        # Attenuation
        _set_combobox_display_and_description(self.attenuation_combobox, self.app_instance.attenuation_var, attenuation_levels, 'Value', self.attenuation_description_var, 'Description', 'Description', "{item[Value]} dB - {label}")

        # Frequency Shift
        _set_combobox_display_and_description(self.frequency_shift_combobox, self.app_instance.freq_shift_var, frequency_shift_presets, 'shift_hz', self.frequency_shift_description_var, 'Description', 'Description', "{item[shift_hz]} Hz - {label}")

        # High Sensitivity
        _set_combobox_display_and_description(self.high_sensitivity_combobox, self.app_instance.high_sensitivity_var, [{"Value": True, "Description": "Yes: High sensitivity mode enabled, optimizing for detection of weak signals."}, {"Value": False, "Description": "No: High sensitivity mode disabled, potentially faster scans but less sensitive."}], 'Value', self.high_sensitivity_description_var, 'Description', 'Description', "{item[Description]}")

        # Preamplifier ON
        _set_combobox_display_and_description(self.preamp_on_combobox, self.app_instance.preamp_on_var, [{"Value": True, "Description": "Yes: Preamplifier is enabled, increasing sensitivity but potentially adding noise."}, {"Value": False, "Description": "No: Preamplifier is disabled, reducing sensitivity but potentially cleaner signal."}], 'Value', self.preamp_on_description_var, 'Description', 'Description', "{item[Description]}")

        # Number of Scan Cycles
        _set_combobox_display_and_description(self.num_scan_cycles_combobox, self.app_instance.num_scan_cycles_var, number_of_scans_presets, 'scans', self.num_scan_cycles_description_var, 'label', 'description', "{item[scans]} cycles - {label}")

        # Scan Mode
        _set_combobox_display_and_description(self.scan_mode_combobox, self.app_instance.scan_mode_var, scan_modes, 'Value', self.scan_mode_description_var, 'Description', 'Description', "{item[Value]}")

        # Desired Default Focus Width (This was an entry, now making it a combobox)
        _set_combobox_display_and_description(self.desired_default_focus_width_combobox, self.app_instance.desired_default_focus_width_var, graph_quality_drop_down, 'resolution_hz', self.desired_default_focus_width_description_var, 'label', 'description', "{item[resolution_hz]} Hz - {label}")


        debug_log(f"Current settings loaded into dropdowns and descriptions updated. Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
