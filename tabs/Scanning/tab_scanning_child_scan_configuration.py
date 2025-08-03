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
# Version 20250802.2015.1 (Standardized data structures to use 'label', 'value', and 'description' for comboboxes.)
# Version 20250802.2030.0 (Fixed AttributeError: 'desired_default_focus_width_combobox' by changing it from Entry to Combobox.)
# Version 20250802.2035.0 (Updated combobox value and label keys to 'value' and 'label' as per new ref_scanner_setting_lists.py structure.)
# Version 20250803.1910.0 (FIXED: ImportError for instrument logic functions by correcting import path.)
# Version 20250803.1920.0 (Re-checked all imports to ensure no circular dependencies or incorrect paths.)
# Version 20250803.1940.0 (FIXED: Incorrect import path for restore_default_settings_logic.)
# Version 20250803.1945.0 (FIXED: Added missing import for str_to_bool function from incorrect location.)
# Version 20250803.2000.0 (CRITICAL FIX: Corrected import path for str_to_bool to src.program_shared_values.)
# Version 20250803.2015.0 (CRITICAL FIX: Corrected import of rbw_drop_down and ref_level_drop_down from ref_scanner_setting_lists.py)

current_version = "20250803.2015.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 2015 * 0 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk, filedialog
import os
import inspect # Import inspect module

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Import configuration and settings management functions
from src.settings_and_config.config_manager import save_config, load_config
from src.settings_and_config.restore_settings_logic import restore_default_settings_logic
from src.program_shared_values import str_to_bool # CRITICAL FIX: Corrected import for str_to_bool

# Import data structures for dropdowns
from ref.ref_scanner_setting_lists import (
    graph_quality_drop_down, cycle_wait_times, maxhold_times,
    frequency_shifts, maxhold_enabled_options,
    sensitivity_options, preamp_options, rbw_segmentation_options, number_of_scans_presets,
    scan_modes, rbw_drop_down, ref_level_drop_down # CRITICAL FIX: Changed rbw_step_sizes, scan_rbw_options, reference_levels to rbw_drop_down, ref_level_drop_down
)
from ref.frequency_bands import SCAN_BAND_RANGES, MHZ_TO_HZ # Import SCAN_BAND_RANGES and MHZ_TO_HZ

# Import instrument logic functions
# connect_instrument_logic and disconnect_instrument_logic are defined in instrument_logic.py
from tabs.Instrument.instrument_logic import connect_instrument_logic, disconnect_instrument_logic
# list_visa_resources is defined in utils_instrument_connection.py
from tabs.Instrument.utils_instrument_connection import list_visa_resources
from tabs.Instrument.utils_instrument_initialize import initialize_instrument_logic
from tabs.Instrument.utils_instrument_query_settings import query_current_instrument_settings
from tabs.Instrument.utils_instrument_apply_settings import apply_instrument_settings_logic


class ScanTab(ttk.Frame):
    """
    Function Description:
    A Tkinter Frame that serves as a child tab for Scan Configuration.
    It provides UI elements for setting scan parameters, selecting frequency bands,
    and managing scan-related settings. It handles dynamic updates to descriptions
    based on dropdown selections and saves configuration changes.

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
        3. Initializes Tkinter StringVars for displaying dynamic descriptions.
        4. Calls `_create_widgets` to build the UI.
        5. Calls `_setup_initial_combobox_values` to set initial selections and descriptions.
        6. Binds the tab selection event to `_on_tab_selected` to refresh UI on tab switch.

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
        super().__init__(master, style='Dark.TLabelframe', **filtered_kwargs) # Pass style string, and filtered kwargs

        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
        self.style_obj = style_obj # Store the style object

        self.current_file = os.path.basename(__file__)

        # Tkinter StringVars for dynamic descriptions
        self.rbw_step_size_description_var = tk.StringVar(self)
        self.cycle_wait_time_description_var = tk.StringVar(self)
        self.maxhold_time_description_var = tk.StringVar(self)
        self.scan_rbw_description_var = tk.StringVar(self)
        self.reference_level_description_var = tk.StringVar(self)
        self.freq_shift_description_var = tk.StringVar(self)
        self.maxhold_enabled_description_var = tk.StringVar(self)
        self.high_sensitivity_description_var = tk.StringVar(self)
        self.preamp_on_description_var = tk.StringVar(self)
        self.rbw_segmentation_description_var = tk.StringVar(self)
        self.num_scan_cycles_description_var = tk.StringVar(self)
        self.scan_mode_description_var = tk.StringVar(self)
        self.desired_default_focus_width_description_var = tk.StringVar(self)


        self._create_widgets()
        self._setup_initial_combobox_values() # Set initial values and descriptions

        # Bind the tab selection event
        # The parent notebook for this tab is self.master
        self.master.bind("<<NotebookTabChanged>>", self._on_tab_selected)

        debug_log(f"ScanTab initialized. Configuration interface ready! Version: {current_version}",
                    file=self.current_file,
                    version=current_version,
                    function=current_function)


    def _create_widgets(self):
        """
        Function Description:
        Creates and arranges all the GUI widgets within the Scan Configuration tab.
        This includes input fields and comboboxes for various scan parameters,
        as well as checkboxes for frequency band selection.

        Inputs:
            None (operates on self).

        Process of this function:
            1. Configures the grid layout for the main frame.
            2. Creates and places a LabelFrame for scan parameters.
            3. Populates the scan parameters frame with:
                - Entry fields for Scan Name and Output Folder.
                - Comboboxes for RBW Step Size, Cycle Wait Time, Maxhold Time,
                  Scan RBW, Reference Level, Frequency Shift, Number of Scan Cycles,
                  Scan Mode, and Desired Default Focus Width.
                - Checkbuttons for Maxhold Enabled, High Sensitivity, Preamplifier ON.
                - Labels for dynamic descriptions.
            4. Creates and places a LabelFrame for frequency band selection.
            5. Populates the band selection frame with checkboxes for each band
               defined in `SCAN_BAND_RANGES`.
            6. Configures initial states of buttons based on connection status.

        Outputs of this function:
            None. Populates the ScanTab frame with GUI elements.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating ScanTab widgets... Building the scan configuration panel! Version: {current_version}",
                    file=self.current_file,
                    version=current_version,
                    function=current_function)

        # Configure grid for the main frame
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Scan Parameters frame
        self.grid_rowconfigure(1, weight=1) # Band Selection frame

        # --- Scan Parameters Frame ---
        scan_params_frame = ttk.LabelFrame(self, text="Scan Parameters", style='Dark.TLabelframe')
        scan_params_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        scan_params_frame.grid_columnconfigure(1, weight=1) # Make entry/combobox columns expandable

        row_idx = 0

        # Scan Name
        ttk.Label(scan_params_frame, text="Scan Name:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.scan_name_entry = ttk.Entry(scan_params_frame, textvariable=self.app_instance.scan_name_var, style='TEntry')
        self.scan_name_entry.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        row_idx += 1

        # Output Folder
        ttk.Label(scan_params_frame, text="Output Folder:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        output_folder_frame = ttk.Frame(scan_params_frame, style='Dark.TFrame')
        output_folder_frame.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        output_folder_frame.grid_columnconfigure(0, weight=1)
        self.output_folder_entry = ttk.Entry(output_folder_frame, textvariable=self.app_instance.output_folder_var, style='TEntry')
        self.output_folder_entry.grid(row=0, column=0, sticky="ew")
        self.browse_folder_button = ttk.Button(output_folder_frame, text="Browse", command=self._browse_output_folder, style='Blue.TButton')
        self.browse_folder_button.grid(row=0, column=1, padx=(5,0), sticky="e")
        row_idx += 1

        # RBW Step Size (Using rbw_drop_down as per your correction)
        ttk.Label(scan_params_frame, text="RBW Step Size (Hz):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.rbw_step_size_combobox = ttk.Combobox(scan_params_frame, textvariable=self.app_instance.rbw_step_size_hz_var, values=[item['value'] for item in rbw_drop_down], state="readonly", style='TCombobox')
        self.rbw_step_size_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        self.rbw_step_size_combobox.bind("<<ComboboxSelected>>", lambda event: self._update_description(event, self.rbw_step_size_combobox, rbw_drop_down, self.rbw_step_size_description_var, 'label', 'description'))
        ttk.Label(scan_params_frame, textvariable=self.rbw_step_size_description_var, style='Dark.TLabel.Value').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1

        # Cycle Wait Time
        ttk.Label(scan_params_frame, text="Cycle Wait Time (s):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.cycle_wait_time_combobox = ttk.Combobox(scan_params_frame, textvariable=self.app_instance.cycle_wait_time_seconds_var, values=[item['value'] for item in cycle_wait_times], state="readonly", style='TCombobox')
        self.cycle_wait_time_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        self.cycle_wait_time_combobox.bind("<<ComboboxSelected>>", lambda event: self._update_description(event, self.cycle_wait_time_combobox, cycle_wait_times, self.cycle_wait_time_description_var, 'label', 'description'))
        ttk.Label(scan_params_frame, textvariable=self.cycle_wait_time_description_var, style='Dark.TLabel.Value').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1

        # Maxhold Time
        ttk.Label(scan_params_frame, text="Maxhold Time (s):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.maxhold_time_combobox = ttk.Combobox(scan_params_frame, textvariable=self.app_instance.maxhold_time_seconds_var, values=[item['value'] for item in maxhold_times], state="readonly", style='TCombobox')
        self.maxhold_time_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        self.maxhold_time_combobox.bind("<<ComboboxSelected>>", lambda event: self._update_description(event, self.maxhold_time_combobox, maxhold_times, self.maxhold_time_description_var, 'label', 'description'))
        ttk.Label(scan_params_frame, textvariable=self.maxhold_time_description_var, style='Dark.TLabel.Value').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1

        # Scan RBW (Using rbw_drop_down as per your correction)
        ttk.Label(scan_params_frame, text="Scan RBW (Hz):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.scan_rbw_combobox = ttk.Combobox(scan_params_frame, textvariable=self.app_instance.scan_rbw_hz_var, values=[item['value'] for item in rbw_drop_down], state="readonly", style='TCombobox')
        self.scan_rbw_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        self.scan_rbw_combobox.bind("<<ComboboxSelected>>", lambda event: self._update_description(event, self.scan_rbw_combobox, rbw_drop_down, self.scan_rbw_description_var, 'label', 'description'))
        ttk.Label(scan_params_frame, textvariable=self.scan_rbw_description_var, style='Dark.TLabel.Value').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1

        # Reference Level (Using ref_level_drop_down as per your correction)
        ttk.Label(scan_params_frame, text="Reference Level (dBm):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.reference_level_combobox = ttk.Combobox(scan_params_frame, textvariable=self.app_instance.reference_level_dbm_var, values=[item['value'] for item in ref_level_drop_down], state="readonly", style='TCombobox')
        self.reference_level_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        self.reference_level_combobox.bind("<<ComboboxSelected>>", lambda event: self._update_description(event, self.reference_level_combobox, ref_level_drop_down, self.reference_level_description_var, 'label', 'description'))
        ttk.Label(scan_params_frame, textvariable=self.reference_level_description_var, style='Dark.TLabel.Value').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1

        # Frequency Shift
        ttk.Label(scan_params_frame, text="Frequency Shift (Hz):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.freq_shift_combobox = ttk.Combobox(scan_params_frame, textvariable=self.app_instance.freq_shift_var, values=[item['value'] for item in frequency_shifts], state="readonly", style='TCombobox')
        self.freq_shift_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        self.freq_shift_combobox.bind("<<ComboboxSelected>>", lambda event: self._update_description(event, self.freq_shift_combobox, frequency_shifts, self.freq_shift_description_var, 'label', 'description'))
        ttk.Label(scan_params_frame, textvariable=self.freq_shift_description_var, style='Dark.TLabel.Value').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1

        # Maxhold Enabled
        ttk.Label(scan_params_frame, text="Maxhold Enabled:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.maxhold_enabled_combobox = ttk.Combobox(scan_params_frame, textvariable=self.app_instance.maxhold_enabled_var, values=[item['value'] for item in maxhold_enabled_options], state="readonly", style='TCombobox')
        self.maxhold_enabled_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        self.maxhold_enabled_combobox.bind("<<ComboboxSelected>>", lambda event: self._update_description(event, self.maxhold_enabled_combobox, maxhold_enabled_options, self.maxhold_enabled_description_var, 'label', 'description'))
        ttk.Label(scan_params_frame, textvariable=self.maxhold_enabled_description_var, style='Dark.TLabel.Value').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1

        # High Sensitivity
        ttk.Label(scan_params_frame, text="High Sensitivity:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.high_sensitivity_combobox = ttk.Combobox(scan_params_frame, textvariable=self.app_instance.high_sensitivity_var, values=[item['value'] for item in sensitivity_options], state="readonly", style='TCombobox')
        self.high_sensitivity_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        self.high_sensitivity_combobox.bind("<<ComboboxSelected>>", lambda event: self._update_description(event, self.high_sensitivity_combobox, sensitivity_options, self.high_sensitivity_description_var, 'label', 'description'))
        ttk.Label(scan_params_frame, textvariable=self.high_sensitivity_description_var, style='Dark.TLabel.Value').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1

        # Preamplifier ON
        ttk.Label(scan_params_frame, text="Preamplifier ON:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.preamp_on_combobox = ttk.Combobox(scan_params_frame, textvariable=self.app_instance.preamp_on_var, values=[item['value'] for item in preamp_options], state="readonly", style='TCombobox')
        self.preamp_on_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        self.preamp_on_combobox.bind("<<ComboboxSelected>>", lambda event: self._update_description(event, self.preamp_on_combobox, preamp_options, self.preamp_on_description_var, 'label', 'description'))
        ttk.Label(scan_params_frame, textvariable=self.preamp_on_description_var, style='Dark.TLabel.Value').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1

        # RBW Segmentation
        ttk.Label(scan_params_frame, text="RBW Segmentation (Hz):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.rbw_segmentation_combobox = ttk.Combobox(scan_params_frame, textvariable=self.app_instance.scan_rbw_segmentation_var, values=[item['value'] for item in rbw_segmentation_options], state="readonly", style='TCombobox')
        self.rbw_segmentation_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        self.rbw_segmentation_combobox.bind("<<ComboboxSelected>>", lambda event: self._update_description(event, self.rbw_segmentation_combobox, rbw_segmentation_options, self.rbw_segmentation_description_var, 'label', 'description'))
        ttk.Label(scan_params_frame, textvariable=self.rbw_segmentation_description_var, style='Dark.TLabel.Value').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1

        # Number of Scan Cycles
        ttk.Label(scan_params_frame, text="Number of Scan Cycles:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.num_scan_cycles_combobox = ttk.Combobox(scan_params_frame, textvariable=self.app_instance.num_scan_cycles_var, values=[item['value'] for item in number_of_scans_presets], state="readonly", style='TCombobox')
        self.num_scan_cycles_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        self.num_scan_cycles_combobox.bind("<<ComboboxSelected>>", lambda event: self._update_description(event, self.num_scan_cycles_combobox, number_of_scans_presets, self.num_scan_cycles_description_var, 'label', 'description'))
        ttk.Label(scan_params_frame, textvariable=self.num_scan_cycles_description_var, style='Dark.TLabel.Value').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1

        # Scan Mode
        ttk.Label(scan_params_frame, text="Scan Mode:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.scan_mode_combobox = ttk.Combobox(scan_params_frame, textvariable=self.app_instance.scan_mode_var, values=[item['value'] for item in scan_modes], state="readonly", style='TCombobox')
        self.scan_mode_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        self.scan_mode_combobox.bind("<<ComboboxSelected>>", lambda event: self._update_description(event, self.scan_mode_combobox, scan_modes, self.scan_mode_description_var, 'label', 'description'))
        ttk.Label(scan_params_frame, textvariable=self.scan_mode_description_var, style='Dark.TLabel.Value').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1

        # Desired Default Focus Width (This was an entry, now making it a combobox)
        ttk.Label(scan_params_frame, text="Default Focus Width (Hz):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.desired_default_focus_width_combobox = ttk.Combobox(scan_params_frame, textvariable=self.app_instance.desired_default_focus_width_var, values=[item['value'] for item in graph_quality_drop_down], state="readonly", style='TCombobox')
        self.desired_default_focus_width_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        self.desired_default_focus_width_combobox.bind("<<ComboboxSelected>>", lambda event: self._update_description(event, self.desired_default_focus_width_combobox, graph_quality_drop_down, self.desired_default_focus_width_description_var, 'label', 'description'))
        ttk.Label(scan_params_frame, textvariable=self.desired_default_focus_width_description_var, style='Dark.TLabel.Value').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # --- Band Selection Frame ---
        band_selection_frame = ttk.LabelFrame(self, text="Frequency Band Selection", style='Dark.TLabelframe')
        band_selection_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        band_selection_frame.grid_columnconfigure(0, weight=1) # Allow columns to expand for checkboxes

        self.band_checkboxes_frame = ttk.Frame(band_selection_frame, style='Dark.TFrame')
        self.band_checkboxes_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.band_checkboxes_frame.grid_columnconfigure(0, weight=1) # First column for checkboxes
        self.band_checkboxes_frame.grid_columnconfigure(1, weight=1) # Second column for checkboxes
        self.band_checkboxes_frame.grid_columnconfigure(2, weight=1) # Third column for checkboxes
        self.band_checkboxes_frame.grid_columnconfigure(3, weight=1) # Fourth column for checkboxes

        self._populate_band_checkboxes()

        debug_log(f"ScanTab widgets created. UI elements are in place! Version: {current_version}",
                    file=self.current_file,
                    version=current_version,
                    function=current_function)


    def _populate_band_checkboxes(self):
        """
        Function Description:
        Populates the frequency band selection frame with checkboxes for each
        band defined in `SCAN_BAND_RANGES`. Each checkbox is linked to a
        BooleanVar stored in `self.app_instance.band_vars`.

        Inputs:
            None (operates on self.band_checkboxes_frame and self.app_instance.band_vars).

        Process of this function:
            1. Clears any existing widgets in `band_checkboxes_frame`.
            2. Iterates through `self.app_instance.band_vars`.
            3. For each band, creates a `ttk.Checkbutton` with the band name
               and associates it with the corresponding `BooleanVar`.
            4. Places the checkboxes in a grid layout.
            5. Logs the operation.

        Outputs of this function:
            None. Populates `band_checkboxes_frame` with checkboxes.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Populating band checkboxes. Getting ready to select frequencies! Version: {current_version}",
                    file=self.current_file,
                    version=current_version,
                    function=current_function)

        # Clear existing checkboxes
        for widget in self.band_checkboxes_frame.winfo_children():
            widget.destroy()

        num_columns = 4 # Number of columns for checkboxes
        for i, band_item in enumerate(self.app_instance.band_vars):
            band_name = band_item['band']['Band Name']
            band_var = band_item['var']
            row = i // num_columns
            col = i % num_columns
            checkbox = ttk.Checkbutton(self.band_checkboxes_frame,
                                       text=band_name,
                                       variable=band_var,
                                       style='TCheckbutton')
            checkbox.grid(row=row, column=col, sticky="w", padx=5, pady=2)
            debug_log(f"Added checkbox for band: {band_name}. Initial state: {band_var.get()}. Version: {current_version}",
                        file=self.current_file,
                        version=current_version,
                        function=current_function)

        debug_log(f"Band checkboxes populated. {len(self.app_instance.band_vars)} bands available. Version: {current_version}",
                    file=self.current_file,
                    version=current_version,
                    function=current_function)


    def _update_description(self, event, combobox_widget, data_list, description_var, value_key, description_key, format_string="{item[value]} - {description}"):
        """
        Function Description:
        Updates a description label based on the selected item in a combobox.

        Inputs:
            event: The Tkinter event object (unused, but required for bind).
            combobox_widget (ttk.Combobox): The combobox that triggered the event.
            data_list (list): The list of dictionaries containing the combobox data.
            description_var (tk.StringVar): The StringVar linked to the description label.
            value_key (str): The key in `data_list` dictionaries that holds the combobox's value.
            description_key (str): The key in `data_list` dictionaries that holds the description.
            format_string (str): A format string to display the description.
                                 Can use {item[key]} for any key in the data_list item,
                                 and {label} for the 'label' if it exists, or {description}.

        Process of this function:
            1. Retrieves the currently selected value from the combobox.
            2. Finds the corresponding item in `data_list`.
            3. Extracts the description and updates `description_var`.
            4. Saves the updated configuration.
            5. Logs the operation.

        Outputs of this function:
            None. Updates `description_var` and saves config.
        """
        current_function = inspect.currentframe().f_code.co_name
        selected_value = combobox_widget.get()
        debug_log(f"Combobox selection changed to: {selected_value}. Updating description. Version: {current_version}",
                    file=self.current_file,
                    version=current_version,
                    function=current_function)

        for item in data_list:
            # Handle boolean values correctly for comparison
            if isinstance(item[value_key], bool) and isinstance(selected_value, str):
                compare_value = str_to_bool(selected_value)
            elif isinstance(item[value_key], (int, float)) and isinstance(selected_value, str):
                try:
                    compare_value = type(item[value_key])(selected_value)
                except ValueError:
                    continue # Skip if conversion fails
            else:
                compare_value = selected_value

            if item[value_key] == compare_value:
                description = item.get(description_key, "No description available.")
                label = item.get('label', str(item[value_key])) # Get label if exists, else use value
                try:
                    # Use .format() to allow flexible string formatting
                    formatted_description = format_string.format(item=item, description=description, label=label)
                    description_var.set(formatted_description)
                except KeyError as e:
                    debug_log(f"Error formatting description string for {value_key}: {e}. Format string: '{format_string}'. Item: {item}",
                                file=self.current_file,
                                version=current_version,
                                function=current_function,
                                level="ERROR")
                    description_var.set(f"Error: {description}") # Fallback
                break
        else:
            description_var.set("No description available.")
            debug_log(f"No matching item found for selected value: {selected_value}. Version: {current_version}",
                        file=self.current_file,
                        version=current_version,
                        function=current_function)

        # Save config after every selection change
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
        debug_log(f"Configuration saved after combobox selection. Version: {current_version}",
                    file=self.current_file,
                    version=current_version,
                    function=current_function)


    def _setup_initial_combobox_values(self):
        """
        Function Description:
        Sets the initial selected values for all comboboxes based on the
        application's Tkinter variables and updates their corresponding descriptions.
        This ensures the UI reflects the loaded configuration on startup.

        Inputs:
            None (operates on self).

        Process of this function:
            1. Defines a helper function `_set_combobox_display_and_description`
               to reduce redundancy in setting combobox values and descriptions.
            2. Calls this helper function for each combobox, passing the combobox widget,
               its associated Tkinter variable, the data list, keys for value/label/description,
               and a format string.
            3. Logs the operation.

        Outputs of this function:
            None. Updates combobox displays and description labels.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Setting up initial combobox values. Syncing UI with config! Version: {current_version}",
                    file=self.current_file,
                    version=current_version,
                    function=current_function)

        def _set_combobox_display_and_description(combobox_widget, tk_var, data_list, value_key, description_var, label_key, description_key, format_string):
            """Helper to set combobox display and update description."""
            current_value = tk_var.get()
            found_item = None
            for item in data_list:
                # Handle boolean values from tk_var (which will be True/False) vs string 'True'/'False' in data_list
                if isinstance(item[value_key], bool) and isinstance(current_value, bool):
                    if item[value_key] == current_value:
                        found_item = item
                        break
                elif str(item[value_key]) == str(current_value):
                    found_item = item
                    break

            if found_item:
                # Set the combobox display value using the label_key
                display_label = found_item.get(label_key, str(found_item[value_key]))
                combobox_widget.set(display_label) # Set the displayed text in the combobox

                description = found_item.get(description_key, "No description available.")
                try:
                    formatted_description = format_string.format(item=found_item, description=description, label=display_label)
                    description_var.set(formatted_description)
                except KeyError as e:
                    debug_log(f"Error formatting initial description string for {value_key}: {e}. Format string: '{format_string}'. Item: {found_item}",
                                file=self.current_file,
                                version=current_version,
                                function=current_function,
                                level="ERROR")
                    description_var.set(f"Error: {description}") # Fallback
            else:
                combobox_widget.set(str(current_value)) # Fallback to raw value if no matching item
                description_var.set("No description available.")
            debug_log(f"Initialized combobox {combobox_widget.winfo_name()} with value {current_value}. Version: {current_version}",
                        file=self.current_file,
                        version=current_version,
                        function=current_function)


        # RBW Step Size (Using rbw_drop_down as per your correction)
        _set_combobox_display_and_description(self.rbw_step_size_combobox, self.app_instance.rbw_step_size_hz_var, rbw_drop_down, 'value', self.rbw_step_size_description_var, 'label', 'description', "{item[value]} Hz - {label}")

        # Cycle Wait Time
        _set_combobox_display_and_description(self.cycle_wait_time_combobox, self.app_instance.cycle_wait_time_seconds_var, cycle_wait_times, 'value', self.cycle_wait_time_description_var, 'label', 'description', "{item[value]} s - {label}")

        # Maxhold Time
        _set_combobox_display_and_description(self.maxhold_time_combobox, self.app_instance.maxhold_time_seconds_var, maxhold_times, 'value', self.maxhold_time_description_var, 'label', 'description', "{item[value]} s - {label}")

        # Scan RBW (Using rbw_drop_down as per your correction)
        _set_combobox_display_and_description(self.scan_rbw_combobox, self.app_instance.scan_rbw_hz_var, rbw_drop_down, 'value', self.scan_rbw_description_var, 'label', 'description', "{item[value]} Hz - {label}")

        # Reference Level (Using ref_level_drop_down as per your correction)
        _set_combobox_display_and_description(self.reference_level_combobox, self.app_instance.reference_level_dbm_var, ref_level_drop_down, 'value', self.reference_level_description_var, 'label', 'description', "{item[value]} dBm - {label}")

        # Frequency Shift
        _set_combobox_display_and_description(self.freq_shift_combobox, self.app_instance.freq_shift_var, frequency_shifts, 'value', self.freq_shift_description_var, 'label', 'description', "{item[label]}")

        # Maxhold Enabled
        _set_combobox_display_and_description(self.maxhold_enabled_combobox, self.app_instance.maxhold_enabled_var, maxhold_enabled_options, 'value', self.maxhold_enabled_description_var, 'label', 'description', "{item[label]}")

        # High Sensitivity
        _set_combobox_display_and_description(self.high_sensitivity_combobox, self.app_instance.high_sensitivity_var, sensitivity_options, 'value', self.high_sensitivity_description_var, 'label', 'description', "{item[label]}")

        # Preamplifier ON
        _set_combobox_display_and_description(self.preamp_on_combobox, self.app_instance.preamp_on_var, preamp_options, 'value', self.preamp_on_description_var, 'label', 'description', "{item[label]}")

        # RBW Segmentation
        _set_combobox_display_and_description(self.rbw_segmentation_combobox, self.app_instance.scan_rbw_segmentation_var, rbw_segmentation_options, 'value', self.rbw_segmentation_description_var, 'label', 'description', "{item[value]} Hz - {label}")

        # Number of Scan Cycles
        _set_combobox_display_and_description(self.num_scan_cycles_combobox, self.app_instance.num_scan_cycles_var, number_of_scans_presets, 'value', self.num_scan_cycles_description_var, 'label', 'description', "{item[value]} cycles - {label}")

        # Scan Mode
        _set_combobox_display_and_description(self.scan_mode_combobox, self.app_instance.scan_mode_var, scan_modes, 'value', self.scan_mode_description_var, 'label', 'description', "{item[value]} - {label}")

        # Desired Default Focus Width (This was an entry, now making it a combobox)
        _set_combobox_display_and_description(self.desired_default_focus_width_combobox, self.app_instance.desired_default_focus_width_var, graph_quality_drop_down, 'value', self.desired_default_focus_width_description_var, 'label', 'description', "{item[value]} Hz - {label}")


        debug_log(f"Finished setting up initial combobox values. UI is synced! Version: {current_version}",
                    file=self.current_file,
                    version=current_version,
                    function=current_function)


    def _browse_output_folder(self):
        """
        Function Description:
        Opens a directory selection dialog and updates the output folder path.

        Inputs:
            None (operates on self.app_instance.output_folder_var).

        Process of this function:
            1. Opens a `filedialog.askdirectory` dialog.
            2. If a directory is selected, updates `self.app_instance.output_folder_var`.
            3. Saves the updated configuration.
            4. Logs the operation.

        Outputs of this function:
            None. Updates `output_folder_var` and saves config.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Browsing for output folder. Opening directory dialog! Version: {current_version}",
                    file=self.current_file,
                    version=current_version,
                    function=current_function)
        initial_dir = self.app_instance.output_folder_var.get()
        if not os.path.isdir(initial_dir):
            initial_dir = os.getcwd() # Fallback to current working directory if path is invalid

        folder_selected = filedialog.askdirectory(initialdir=initial_dir)
        if folder_selected:
            self.app_instance.output_folder_var.set(folder_selected)
            self.console_print_func(f"✅ Output folder set to: {folder_selected}")
            save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
            debug_log(f"Output folder updated to: {folder_selected}. Config saved! Version: {current_version}",
                        file=self.current_file,
                        version=current_version,
                        function=current_function)
        else:
            self.console_print_func("ℹ️ Output folder selection cancelled.")
            debug_log(f"Output folder selection cancelled. Version: {current_version}",
                        file=self.current_file,
                        version=current_version,
                        function=current_function)


    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Can be used to refresh data or update UI elements specific to this tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Scan Configuration Tab selected. Version: {self.current_version}. Time to configure scans!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        # Check if the currently selected tab in the PARENT notebook is the Scanning tab itself
        selected_parent_tab = self.app_instance.notebook.nametowidget(self.app_instance.notebook.select())
        if selected_parent_tab == self.master.master: # self.master is the child_notebook, self.master.master is the main_app.notebook
            # No specific UI updates needed for this tab on selection, as most are bound to vars.
            # However, we can ensure the combobox descriptions are up-to-date.
            self._setup_initial_combobox_values()

        # Propagate the tab selected event to the main app's parent tab handler
        # This will trigger ASCII art creation to display ASCII art when the parent tab is selected.
        if hasattr(self.app_instance, '_on_parent_tab_selected'):
            self.app_instance._on_parent_tab_selected(event) # Pass the event object
