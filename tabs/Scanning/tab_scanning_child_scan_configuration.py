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
# Version 20250802.0014.4 (Fixed AttributeError: 'ScanTab' object has no attribute 'style_obj' by passing style_obj.)

current_version = "20250802.0014.4" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 14 * 4 # Example hash, adjust as needed

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

# Import constants from frequency_bands.py
from ref.frequency_bands import SCAN_BAND_RANGES, RBW_OPTIONS, VBW_RBW_RATIO_OPTIONS, DEFAULT_REF_LEVEL_OPTIONS, DEFAULT_FREQ_SHIFT_OPTIONS

# Define current_file for consistent logging
current_file = os.path.basename(__file__)

class ScanTab(ttk.Frame):
    """
    Function Description:
    Manages the Scan Configuration tab in the GUI. This includes:
    - Input fields for scan name, output folder, number of scan cycles.
    - Dropdowns for RBW step size, cycle wait time, maxhold time, scan RBW,
      reference level, and frequency shift.
    - Checkboxes for Maxhold Enable, High Sensitivity, and Preamp On.
    - Band selection checkboxes with dynamic descriptions.
    - Buttons to open the output folder and refresh bands.
    - Integration with application-wide settings and configuration saving.

    Inputs:
        parent (tk.Widget): The parent widget (e.g., ttk.Notebook).
        app_instance (object): The main application instance, providing access to shared data and methods.
        console_print_func (function): Function to print messages to the console.
        style_obj (ttk.Style): The ttk.Style object for applying styles.

    Process of this class:
        1. Initializes the Tkinter Frame and sets up instance variables.
        2. Defines dropdown options for various scan parameters.
        3. Creates and arranges widgets:
           - Scan Details section (scan name, output folder, cycles).
           - Instrument Settings section (RBW step, cycle wait, maxhold time, scan RBW, ref level, freq shift, maxhold enable, high sensitivity, preamp).
           - Band Selection section (checkboxes for each band, dynamically created).
        4. Sets up event bindings for dropdowns and checkboxes to trigger config saving.
        5. Implements methods for:
           - Opening the output folder (`_open_output_folder`).
           - Loading band selections from config (`_load_band_selections_from_config`).
           - Handling changes in dropdowns and checkboxes (`_on_setting_change`).
           - Handling canvas configuration for band scrolling (`_on_bands_canvas_configure`).
           - Handling tab selection (`_on_tab_selected`).
           - Loading current settings into dropdowns (`_load_current_settings_into_dropdowns`).

    Outputs of this class:
        A functional Tkinter Frame for configuring spectrum scans.
    """
    def __init__(self, parent, app_instance, console_print_func, style_obj):
        """
        Initializes the ScanTab.
        """
        super().__init__(parent, style='Dark.TFrame')
        self.app_instance = app_instance
        self.console_print_func = console_print_func
        self.style_obj = style_obj # Store the style object

        debug_log(f"Initializing ScanTab...",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

        self.rbw_options = RBW_OPTIONS
        self.vbw_rbw_ratio_options = VBW_RBW_RATIO_OPTIONS
        self.ref_level_options = DEFAULT_REF_LEVEL_OPTIONS
        self.freq_shift_options = DEFAULT_FREQ_SHIFT_OPTIONS

        self._create_widgets()
        self._setup_bindings()
        self._load_band_selections_from_config() # Load band selections on init
        self._load_current_settings_into_dropdowns() # Load other settings into dropdowns on init

        debug_log(f"ScanTab initialized.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

    def _create_widgets(self):
        """
        Function Description:
        Creates and arranges all the widgets for the Scan Configuration tab.

        Inputs:
            None.

        Process:
            1. Configures the grid layout for the main frame.
            2. Creates and places a LabelFrame for "Scan Details".
            3. Inside the scan details frame:
               - Creates Labels and Entry widgets for Scan Name, Output Folder, and Number of Scan Cycles.
               - Creates a "Browse" button for the output folder.
            4. Creates and places a LabelFrame for "Instrument Settings".
            5. Inside the instrument settings frame:
               - Creates Labels and Comboboxes for RBW Step Size, Cycle Wait Time, Maxhold Time, Scan RBW,
                 Reference Level, and Frequency Shift.
               - Creates Checkbuttons for Maxhold Enable, High Sensitivity, and Preamp On.
            6. Creates and places a LabelFrame for "Band Selection".
            7. Inside the band selection frame:
               - Creates a Canvas and a Frame within it to allow for scrollable band checkboxes.
               - Dynamically creates Checkbuttons for each band defined in `SCAN_BAND_RANGES`.
               - Creates a "Refresh Bands" button.

        Outputs:
            None. Populates the tab with GUI elements.
        """
        debug_log(f"Creating ScanTab widgets...",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Scan Details
        self.grid_rowconfigure(1, weight=0) # Instrument Settings
        self.grid_rowconfigure(2, weight=1) # Band Selection (takes remaining space)


        # --- Scan Details ---
        scan_details_frame = ttk.LabelFrame(self, text="Scan Details", style='Dark.TLabelframe')
        scan_details_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        scan_details_frame.grid_columnconfigure(1, weight=1) # Make entry widgets expand

        ttk.Label(scan_details_frame, text="Scan Name:", style='Dark.TLabel').grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.scan_name_entry = ttk.Entry(scan_details_frame, textvariable=self.app_instance.scan_name_var, style='Dark.TEntry')
        self.scan_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.scan_name_entry.bind("<FocusOut>", self._on_setting_change) # Save on focus out
        self.scan_name_entry.bind("<Return>", self._on_setting_change) # Save on Enter

        ttk.Label(scan_details_frame, text="Output Folder:", style='Dark.TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.output_folder_entry = ttk.Entry(scan_details_frame, textvariable=self.app_instance.output_folder_var, style='Dark.TEntry')
        self.output_folder_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.output_folder_entry.bind("<FocusOut>", self._on_setting_change) # Save on focus out
        self.output_folder_entry.bind("<Return>", self._on_setting_change) # Save on Enter

        self.output_folder_button = ttk.Button(scan_details_frame, text="Browse", command=self._browse_output_folder, style='Blue.TButton')
        self.output_folder_button.grid(row=1, column=2, padx=5, pady=2, sticky="e")

        ttk.Label(scan_details_frame, text="Number of Scan Cycles:", style='Dark.TLabel').grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.num_scan_cycles_entry = ttk.Entry(scan_details_frame, textvariable=self.app_instance.num_scan_cycles_var, style='Dark.TEntry')
        self.num_scan_cycles_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.num_scan_cycles_entry.bind("<FocusOut>", self._on_setting_change)
        self.num_scan_cycles_entry.bind("<Return>", self._on_setting_change)


        # --- Instrument Settings ---
        instrument_settings_frame = ttk.LabelFrame(self, text="Instrument Settings", style='Dark.TLabelframe')
        instrument_settings_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        instrument_settings_frame.grid_columnconfigure(1, weight=1) # Make dropdowns expand

        ttk.Label(instrument_settings_frame, text="RBW Step Size (Hz):", style='Dark.TLabel').grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.rbw_step_size_dropdown = ttk.Combobox(instrument_settings_frame, textvariable=self.app_instance.rbw_step_size_hz_var, values=self.rbw_options, state="readonly", style='TCombobox')
        self.rbw_step_size_dropdown.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.rbw_step_size_dropdown.bind("<<ComboboxSelected>>", self._on_setting_change)

        ttk.Label(instrument_settings_frame, text="Cycle Wait Time (s):", style='Dark.TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.cycle_wait_time_entry = ttk.Entry(instrument_settings_frame, textvariable=self.app_instance.cycle_wait_time_seconds_var, style='Dark.TEntry')
        self.cycle_wait_time_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.cycle_wait_time_entry.bind("<FocusOut>", self._on_setting_change)
        self.cycle_wait_time_entry.bind("<Return>", self._on_setting_change)

        ttk.Label(instrument_settings_frame, text="Maxhold Time (s):", style='Dark.TLabel').grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.maxhold_time_entry = ttk.Entry(instrument_settings_frame, textvariable=self.app_instance.maxhold_time_seconds_var, style='Dark.TEntry')
        self.maxhold_time_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.maxhold_time_entry.bind("<FocusOut>", self._on_setting_change)
        self.maxhold_time_entry.bind("<Return>", self._on_setting_change)

        ttk.Label(instrument_settings_frame, text="Scan RBW (Hz):", style='Dark.TLabel').grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.scan_rbw_dropdown = ttk.Combobox(instrument_settings_frame, textvariable=self.app_instance.scan_rbw_hz_var, values=self.rbw_options, state="readonly", style='TCombobox')
        self.scan_rbw_dropdown.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        self.scan_rbw_dropdown.bind("<<ComboboxSelected>>", self._on_setting_change)

        ttk.Label(instrument_settings_frame, text="Reference Level (dBm):", style='Dark.TLabel').grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.ref_level_dropdown = ttk.Combobox(instrument_settings_frame, textvariable=self.app_instance.reference_level_dbm_var, values=self.ref_level_options, state="readonly", style='TCombobox')
        self.ref_level_dropdown.grid(row=4, column=1, padx=5, pady=2, sticky="ew")
        self.ref_level_dropdown.bind("<<ComboboxSelected>>", self._on_setting_change)

        ttk.Label(instrument_settings_frame, text="Frequency Shift (Hz):", style='Dark.TLabel').grid(row=5, column=0, padx=5, pady=2, sticky="w")
        self.freq_shift_dropdown = ttk.Combobox(instrument_settings_frame, textvariable=self.app_instance.freq_shift_hz_var, values=self.freq_shift_options, state="readonly", style='TCombobox')
        self.freq_shift_dropdown.grid(row=5, column=1, padx=5, pady=2, sticky="ew")
        self.freq_shift_dropdown.bind("<<ComboboxSelected>>", self._on_setting_change)

        ttk.Label(instrument_settings_frame, text="RBW Segmentation (Hz):", style='Dark.TLabel').grid(row=6, column=0, padx=5, pady=2, sticky="w")
        self.scan_rbw_segmentation_entry = ttk.Entry(instrument_settings_frame, textvariable=self.app_instance.scan_rbw_segmentation_var, style='Dark.TEntry')
        self.scan_rbw_segmentation_entry.grid(row=6, column=1, padx=5, pady=2, sticky="ew")
        self.scan_rbw_segmentation_entry.bind("<FocusOut>", self._on_setting_change)
        self.scan_rbw_segmentation_entry.bind("<Return>", self._on_setting_change)

        ttk.Label(instrument_settings_frame, text="Default Focus Width (Hz):", style='Dark.TLabel').grid(row=7, column=0, padx=5, pady=2, sticky="w")
        self.desired_default_focus_width_entry = ttk.Entry(instrument_settings_frame, textvariable=self.app_instance.desired_default_focus_width_var, style='Dark.TEntry')
        self.desired_default_focus_width_entry.grid(row=7, column=1, padx=5, pady=2, sticky="ew")
        self.desired_default_focus_width_entry.bind("<FocusOut>", self._on_setting_change)
        self.desired_default_focus_width_entry.bind("<Return>", self._on_setting_change)


        self.maxhold_check = ttk.Checkbutton(instrument_settings_frame, text="Maxhold Enable", variable=self.app_instance.maxhold_enabled_var, style='Dark.TCheckbutton')
        self.maxhold_check.grid(row=8, column=0, columnspan=2, padx=5, pady=2, sticky="w")
        self.maxhold_check.bind("<ButtonRelease-1>", self._on_setting_change) # Bind to mouse release for immediate update

        self.high_sensitivity_check = ttk.Checkbutton(instrument_settings_frame, text="High Sensitivity", variable=self.app_instance.high_sensitivity_var, style='Dark.TCheckbutton')
        self.high_sensitivity_check.grid(row=9, column=0, columnspan=2, padx=5, pady=2, sticky="w")
        self.high_sensitivity_check.bind("<ButtonRelease-1>", self._on_setting_change)

        self.preamp_check = ttk.Checkbutton(instrument_settings_frame, text="Preamp On", variable=self.app_instance.preamp_on_var, style='Dark.TCheckbutton')
        self.preamp_check.grid(row=10, column=0, columnspan=2, padx=5, pady=2, sticky="w")
        self.preamp_check.bind("<ButtonRelease-1>", self._on_setting_change)


        # --- Band Selection ---
        bands_frame = ttk.LabelFrame(self, text="Band Selection", style='Dark.TLabelframe')
        bands_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        bands_frame.grid_columnconfigure(0, weight=1)
        bands_frame.grid_rowconfigure(0, weight=1) # Canvas takes all vertical space

        self.bands_canvas = tk.Canvas(bands_frame, bg=self.style_obj.lookup('Dark.TFrame', 'background'))
        self.bands_canvas.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.bands_scrollbar = ttk.Scrollbar(bands_frame, orient="vertical", command=self.bands_canvas.yview)
        self.bands_scrollbar.grid(row=0, column=1, sticky="ns")

        self.bands_canvas.configure(yscrollcommand=self.bands_scrollbar.set)
        self.bands_canvas.bind('<Configure>', self._on_bands_canvas_configure)

        self.bands_inner_frame = ttk.Frame(self.bands_canvas, style='Dark.TFrame')
        # Store the ID of the window created in the canvas
        self.bands_inner_frame_id = self.bands_canvas.create_window((0, 0), window=self.bands_inner_frame, anchor="nw")


        self.bands_inner_frame.grid_columnconfigure(0, weight=1) # Make band names expand
        self.bands_inner_frame.grid_columnconfigure(1, weight=1) # Make descriptions expand

        # Dynamically create checkboxes for each band
        for i, band_item in enumerate(self.app_instance.band_vars):
            band_name = band_item["band"]["Band Name"]
            # Dynamically create description from Start MHz and Stop MHz
            band_start_mhz = band_item["band"]["Start MHz"]
            band_stop_mhz = band_item["band"]["Stop MHz"]
            band_description = f"{band_start_mhz:.3f} - {band_stop_mhz:.3f} MHz"

            band_var = band_item["var"]

            cb = ttk.Checkbutton(self.bands_inner_frame, text=band_name, variable=band_var, style='Dark.TCheckbutton')
            cb.grid(row=i, column=0, padx=5, pady=2, sticky="w")
            cb.bind("<ButtonRelease-1>", self._on_setting_change) # Bind to mouse release for immediate update

            ttk.Label(self.bands_inner_frame, text=f"({band_description})", style='Dark.TLabel').grid(row=i, column=1, padx=5, pady=2, sticky="w")

        # Add a refresh bands button (useful if bands are dynamically loaded)
        self.refresh_bands_button = ttk.Button(bands_frame, text="Refresh Bands", command=self._load_band_selections_from_config, style='Blue.TButton')
        self.refresh_bands_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        debug_log(f"ScanTab widgets created. Ready to serve!",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

    def _setup_bindings(self):
        """
        Function Description:
        Sets up event bindings for the widgets in the ScanTab.

        Inputs:
            None.

        Process:
            1. Binds the `<<ComboboxSelected>>` event to various comboboxes.
            2. Binds the `<ButtonRelease-1>` event to checkboxes.
            3. Binds `<FocusOut>` and `<Return>` events to Entry widgets.

        Outputs:
            None. Establishes event handling.
        """
        debug_log(f"Setting up ScanTab bindings...",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        # All bindings are now directly in _create_widgets for simplicity.
        debug_log(f"ScanTab bindings setup complete.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

    def _browse_output_folder(self):
        """
        Function Description:
        Opens a directory dialog for the user to select an output folder.
        Updates the `output_folder_var` and saves the configuration.

        Inputs:
            None.

        Process:
            1. Opens a directory selection dialog.
            2. If a directory is selected, updates `self.app_instance.output_folder_var`.
            3. Calls `_on_setting_change` to save the updated path.

        Outputs:
            None. Updates output folder path.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Browsing for output folder...",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        initial_dir = self.app_instance.output_folder_var.get()
        if not os.path.isdir(initial_dir):
            initial_dir = os.path.expanduser("~") # Fallback to home directory

        folder_selected = filedialog.askdirectory(initialdir=initial_dir)
        if folder_selected:
            self.app_instance.output_folder_var.set(folder_selected)
            self.console_print_func(f"✅ Output folder set to: {folder_selected}")
            debug_log(f"Output folder selected: {folder_selected}.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            self._on_setting_change() # Trigger save after changing
        else:
            self.console_print_func("ℹ️ Output folder selection cancelled. Fine, be that way!")
            debug_log(f"Output folder selection cancelled.",
                        file=current_file,
                        version=current_version,
                        function=current_function)

    def _on_setting_change(self, event=None):
        """
        Function Description:
        Callback function triggered when a setting (dropdown, checkbox, entry) changes.
        This function saves the current configuration to `config.ini`.

        Inputs:
            event (tkinter.Event, optional): The event object that triggered the callback. Defaults to None.

        Process:
            1. Prints a debug message.
            2. Calls `save_config` to persist the application's current settings.

        Outputs:
            None. Persists configuration.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Setting changed. Saving config. Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Collect selected bands before saving
        selected_bands = [band_item["band"]["Band Name"] for band_item in self.app_instance.band_vars if band_item["var"].get()]
        self.app_instance.config.set('LAST_USED_SETTINGS', 'last_scan_configuration__selected_bands', ','.join(selected_bands))

        # Pass console_log from here to save_config
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
        debug_log(f"Config saved after setting change. Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

    def _on_bands_canvas_configure(self, event):
        """
        Function Description:
        Adjusts the scrolling region of the bands canvas when its size changes.
        This ensures that all band checkboxes are accessible via scrolling.

        Inputs:
            event (tkinter.Event): The event object.

        Process:
            1. Prints a debug message.
            2. Updates the canvas's scroll region to encompass the entire inner frame.

        Outputs:
            None. Adjusts canvas scrolling.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Configuring bands canvas. Adjusting width for inner frame. Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Update the scrollregion to encompass the inner frame
        self.bands_canvas.itemconfigure(self.bands_inner_frame_id, width=event.width)
        self.bands_canvas.config(scrollregion=self.bands_canvas.bbox("all"))

        debug_log(f"Bands canvas configured. Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)


    def _load_band_selections_from_config(self):
        """
        Loads the selected bands from config.ini into the checkboxes.
        This is called on tab selection to ensure the GUI reflects the config.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Loading band selections from config.ini... Syncing checkboxes with saved settings! Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Get the last used selected bands from config using the new prefixed key
        last_selected_bands_str = self.app_instance.config.get('LAST_USED_SETTINGS', 'last_scan_configuration__selected_bands', fallback='')
        last_selected_band_names = [name.strip() for name in last_selected_bands_str.split(',') if name.strip()]

        # Set the state of each checkbox based on the loaded bands
        for band_item in self.app_instance.band_vars:
            band_name = band_item["band"]["Band Name"]
            band_item["var"].set(band_name in last_selected_band_names)

        debug_log(f"Loaded selected bands from config: {last_selected_band_names}. Checkboxes updated! Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

    def _load_current_settings_into_dropdowns(self):
        """
        Loads the current instrument settings (from the app_instance's Tkinter variables)
        into the respective dropdowns on the Scan Configuration tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Loading current settings into dropdowns. Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # RBW Step Size
        rbw_step_size_str = self.app_instance.rbw_step_size_hz_var.get()
        if rbw_step_size_str in self.rbw_options:
            self.rbw_step_size_dropdown.set(rbw_step_size_str)
        else:
            self.rbw_step_size_dropdown.set(self.rbw_options[0]) # Default to first option

        # Cycle Wait Time
        self.cycle_wait_time_entry.delete(0, tk.END)
        self.cycle_wait_time_entry.insert(0, self.app_instance.cycle_wait_time_seconds_var.get())

        # Maxhold Time
        self.maxhold_time_entry.delete(0, tk.END)
        self.maxhold_time_entry.insert(0, self.app_instance.maxhold_time_seconds_var.get())

        # Scan RBW
        scan_rbw_str = self.app_instance.scan_rbw_hz_var.get()
        if scan_rbw_str in self.rbw_options:
            self.scan_rbw_dropdown.set(scan_rbw_str)
        else:
            self.scan_rbw_dropdown.set(self.rbw_options[0]) # Default to first option

        # Reference Level (dBm) - FIX: Handle 'N/A'
        ref_level_str = self.app_instance.reference_level_dbm_var.get()
        if ref_level_str == "N/A":
            current_value = -40 # A sensible default if not connected
            debug_log(f"Reference Level is 'N/A', defaulting to {current_value} dBm for dropdown.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        else:
            try:
                current_value = int(float(ref_level_str))
            except ValueError as e:
                debug_log(f"ERROR: Could not convert Reference Level '{ref_level_str}' to float. Defaulting to -40 dBm. Error: {e}",
                            file=current_file,
                            version=current_version,
                            function=current_function)
                current_value = -40 # Fallback if conversion fails for other reasons

        # Find the index of the current_value in the dropdown options
        try:
            # Ensure the value is a string for comparison with dropdown options
            index = self.ref_level_options.index(str(current_value))
            self.ref_level_dropdown.current(index)
        except ValueError:
            debug_log(f"Reference Level {current_value} not found in dropdown options. Setting to first option.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            self.ref_level_dropdown.current(0) # Set to first option if not found


        # Frequency Shift
        freq_shift_str = self.app_instance.freq_shift_hz_var.get()
        if freq_shift_str in self.freq_shift_options:
            self.freq_shift_dropdown.set(freq_shift_str)
        else:
            self.freq_shift_dropdown.set(self.freq_shift_options[0]) # Default to first option

        # RBW Segmentation
        self.scan_rbw_segmentation_entry.delete(0, tk.END)
        self.scan_rbw_segmentation_entry.insert(0, self.app_instance.scan_rbw_segmentation_var.get())

        # Default Focus Width
        self.desired_default_focus_width_entry.delete(0, tk.END)
        self.desired_default_focus_width_entry.insert(0, self.app_instance.desired_default_focus_width_var.get())

        debug_log(f"Current settings loaded into dropdowns. Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Can be used to refresh data or update UI elements specific to this tab.
        For the scan configuration, we ensure settings are loaded/reloaded.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"ScanTab selected. Refreshing settings... Let's get this updated! Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        self._load_current_settings_into_dropdowns()
        self._load_band_selections_from_config()
