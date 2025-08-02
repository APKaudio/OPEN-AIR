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

current_version = "20250802.1805.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 1805 * 0 # Example hash, adjust as needed

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
    rbw_presets
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
            textvariable=self.app_instance.freq_shift_hz_var, # Linked to app_instance's StringVar
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


    def _populate_bands(self):
        # This function description tells me what this function does
        # Populates the `bands_inner_frame` with checkboxes for each frequency band
        # defined in `SCAN_BAND_RANGES`. Each checkbox is linked to a Tkinter BooleanVar
        # and an event handler to save the configuration when its state changes.
        #
        # Inputs to this function
        #   None (operates on self).
        #
        # Process of this function
        #   1. Prints a debug message.
        #   2. Clears any existing widgets in `bands_inner_frame`.
        #   3. Iterates through `app_instance.band_vars` (which holds band data and BooleanVars).
        #   4. For each band, creates a `ttk.Checkbutton` and packs it into the frame.
        #   5. Binds the checkbutton's command to `_on_band_checkbox_change` to save config.
        #   6. Stores a reference to the checkbutton widget in the `band_item` dictionary.
        #
        # Outputs of this function
        #   None. Adds Checkbutton widgets to the UI.
        #
        # (2025-07-30) Change: Implemented dynamic creation of checkboxes for bands.
        # (20250801.2335.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0014.1) Change: Stored reference to the Checkbutton widget.
        # (20250802.1805.0) Change: Renamed from _populate_band_checkboxes for consistency.
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
        # This function description tells me what this function does
        # Configures the scroll region of the `bands_canvas` when the `bands_inner_frame`
        # changes size. This ensures the scrollbar correctly reflects the content height.
        #
        # Inputs to this function
        #   event (tkinter.Event): The event object that triggered the configuration.
        #
        # Process of this function
        #   1. Prints a debug message.
        #   2. Updates the `scrollregion` of `bands_canvas` to encompass the entire
        #      bounding box of `bands_inner_frame`.
        #
        # Outputs of this function
        #   None. Adjusts the canvas scroll region.
        #
        # (2025-07-30) Change: Implemented for scrollable band selection.
        # (20250801.2335.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0014.1) Change: No functional changes.
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Configuring bands frame. Adjusting scroll region. Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        self.bands_canvas.configure(scrollregion=self.bands_canvas.bbox("all"))


    def _browse_output_folder(self):
        # This function description tells me what this function does
        # Opens a file dialog to allow the user to select an output folder for scan data.
        # It updates the `output_folder_var` with the selected path and saves the configuration.
        #
        # Inputs to this function
        #   None (operates on self).
        #
        # Process of this function
        #   1. Prints a debug message.
        #   2. Opens a directory selection dialog.
        #   3. If a directory is selected, updates `app_instance.output_folder_var`.
        #   4. Calls `save_config` to persist the new output folder.
        #
        # Outputs of this function
        #   None. Updates a Tkinter variable and saves application configuration.
        #
        # (2025-07-30) Change: Implemented folder browsing.
        # (20250801.2335.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0014.1) Change: No functional changes.
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
        debug_log(f"Attempting to open output folder: {output_path}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        if not output_path:
            self.console_print_func("❌ Output folder path is empty. Please set a folder first.")
            debug_log(f"Output folder path is empty. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
            return

        if not os.path.exists(output_path):
            self.console_print_func(f"⚠️ Output folder does not exist: {output_path}. Attempting to create it.")
            debug_log(f"Output folder does not exist: {output_path}. Attempting to create. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
            try:
                os.makedirs(output_path)
                self.console_print_func(f"✅ Created output folder: {output_path}")
                debug_log(f"Created output folder: {output_path}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
            except Exception as e:
                self.console_print_func(f"❌ Failed to create output folder: {e}")
                debug_log(f"Failed to create output folder: {e}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                return

        try:
            if sys.platform == "win32":
                os.startfile(output_path) # For Windows
            elif sys.platform == "darwin":
                subprocess.Popen(["open", output_path]) # For macOS
            else:
                subprocess.Popen(["xdg-open", output_path]) # For Linux
            self.console_print_func(f"✅ Opened output folder: {output_path}")
            debug_log(f"Opened output folder: {output_path}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        except Exception as e:
            self.console_print_func(f"❌ Error opening output folder: {e}")
            debug_log(f"Error opening output folder '{output_path}': {e}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def _on_scan_mode_selected(self, event):
        # This function description tells me what this function does
        # Event handler for when a scan mode is selected from the dropdown.
        # It updates the `app_instance.scan_mode_var` and saves the configuration.
        #
        # Inputs to this function
        #   event (tkinter.Event): The event object that triggered the call.
        #
        # Process of this function
        #   1. Prints a debug message.
        #   2. Retrieves the selected scan mode.
        #   3. Calls `save_config` to persist the new scan mode.
        #
        # Outputs of this function
        #   None. Updates a Tkinter variable and saves application configuration.
        #
        # (2025-07-30) Change: Implemented scan mode selection and config saving.
        # (20250801.2335.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0014.1) Change: No functional changes.
        # (20250802.1805.0) Change: Updated description var and simplified save_config.
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Scan mode selected: {self.app_instance.scan_mode_var.get()}. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        # Update description for Scan Mode (if applicable, currently not in ref_scanner_setting_lists)
        # For now, just save config.
        save_config(self.app_instance)


    def _on_reference_level_selected(self, event):
        # This function description tells me what this function does
        # Event handler for when a reference level is selected from the dropdown.
        # It updates the `app_instance.reference_level_dbm_var` and saves the configuration.
        #
        # Inputs to this function
        #   event (tkinter.Event): The event object that triggered the call.
        #
        # Process of this function
        #   1. Prints a debug message.
        #   2. Retrieves the selected reference level.
        #   3. Calls `save_config` to persist the new reference level.
        #
        # Outputs of this function
        #   None. Updates a Tkinter variable and saves application configuration.
        #
        # (2025-07-30) Change: Implemented reference level selection and config saving.
        # (20250801.2335.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0014.1) Change: No functional changes.
        # (20250802.1805.0) Change: Updated description var and simplified save_config.
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Reference level selected: {self.app_instance.reference_level_dbm_var.get()} dBm. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        # Update description
        selected_value = float(self.app_instance.reference_level_dbm_var.get())
        for item in reference_level_drop_down:
            if item["level_dbm"] == selected_value:
                self.reference_level_description_var.set(f"{item['label']}: {item['description']}")
                break
        save_config(self.app_instance)


    def _on_attenuation_selected(self, event):
        # This function description tells me what this function does
        # Event handler for when an attenuation level is selected from the dropdown.
        # It updates the `app_instance.attenuation_var` and saves the configuration.
        #
        # Inputs to this function
        #   event (tkinter.Event): The event object that triggered the call.
        #
        # Process of this function
        #   1. Prints a debug message.
        #   2. Retrieves the selected attenuation level.
        #   3. Calls `save_config` to persist the new attenuation level.
        #
        # Outputs of this function
        #   None. Updates a Tkinter variable and saves application configuration.
        #
        # (2025-07-30) Change: Implemented attenuation selection and config saving.
        # (250802.0014.1) Change: No functional changes.
        # (20250802.1805.0) Change: Updated description var and simplified save_config.
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Attenuation selected: {self.app_instance.attenuation_var.get()} dB. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        # Update description for Attenuation (if applicable, currently not in ref_scanner_setting_lists)
        # For now, just save config.
        save_config(self.app_instance)


    def _on_freq_shift_selected(self, event):
        # This function description tells me what this function does
        # Event handler for when a frequency shift is selected from the dropdown.
        # It updates the `app_instance.freq_shift_var` and saves the configuration.
        #
        # Inputs to this function
        #   event (tkinter.Event): The event object that triggered the call.
        #
        # Process of this function
        #   1. Prints a debug message.
        #   2. Retrieves the selected frequency shift.
        #   3. Calls `save_config` to persist the new frequency shift.
        #
        # Outputs of this function
        #   None. Updates a Tkinter variable and saves application configuration.
        #
        # (2025-07-30) Change: Implemented frequency shift selection and config saving.
        # (20250801.2335.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0014.1) Change: No functional changes.
        # (20250802.1805.0) Change: Updated description var and simplified save_config.
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Frequency shift selected: {self.app_instance.freq_shift_var.get()} MHz. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)
        # Update description for Frequency Shift (if applicable, currently not in ref_scanner_setting_lists)
        # For now, just save config.
        save_config(self.app_instance)


    def _on_band_checkbox_change(self):
        # This function description tells me what this function does
        # Event handler for when a band selection checkbox is toggled.
        # It updates the `app_instance.selected_bands` list and saves the configuration.
        #
        # Inputs to this function
        #   None (operates on self).
        #
        # Process of this function
        #   1. Prints a debug message.
        #   2. Clears the `app_instance.selected_bands` list.
        #   3. Iterates through `app_instance.band_vars`.
        #   4. If a band's checkbox is checked, adds its name to `app_instance.selected_bands`.
        #   5. Calls `save_config` to persist the updated selected bands.
        #
        # Outputs of this function
        #   None. Updates a list and saves application configuration.
        #
        # (2025-07-30) Change: Implemented band selection and config saving.
        # (20250801.2335.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0014.1) Change: No functional changes.
        # (20250802.1805.0) Change: Simplified save_config.
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Band checkbox changed. Updating selected bands and saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)

        self.app_instance.selected_bands.clear()
        for band_item in self.app_instance.band_vars:
            if band_item["var"].get():
                self.app_instance.selected_bands.append(band_item["band"]["Band Name"])
        save_config(self.app_instance)


    def _load_current_settings_into_dropdowns(self):
        """
        Loads the current instrument settings (from the app_instance's Tkinter variables)
        into the respective dropdowns on the Scan Configuration tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Loading current settings into dropdowns. Syncing UI with config! Version: {current_version}",
                    file=current_file,
                    version=current_function,
                    function=current_function)

        # Helper to find label and description for a given value, and format display string
        def get_formatted_strings(value, dropdown_list, value_key, unit=""):
            for item in dropdown_list:
                # Ensure comparison is type-safe (e.g., convert value to int/float if necessary)
                if isinstance(item[value_key], (int, float)) and isinstance(value, (int, float)):
                    if item[value_key] == value:
                        combobox_display = f"{item[value_key]}{unit}" if unit else f"{item[value_key]}"
                        description_display = f"{item['label']}: {item['description']}"
                        return combobox_display, description_display
                elif str(item[value_key]) == str(value): # For string comparisons
                    combobox_display = f"{item[value_key]}{unit}" if unit else f"{item[value_key]}"
                    description_display = f"{item['label']}: {item['description']}"
                    return combobox_display, description_display
            # Fallback for custom values not in presets
            combobox_display_fallback = f"{value}{unit}" if unit else f"{value}"
            description_display_fallback = f"Custom: Custom value detected. Select from dropdown to get description."
            return combobox_display_fallback, description_display_fallback

        # Scan Name
        self.scan_name_entry.delete(0, tk.END)
        self.scan_name_entry.insert(0, self.app_instance.scan_name_var.get())

        # Output Folder
        self.output_folder_entry.delete(0, tk.END)
        self.output_folder_entry.insert(0, self.app_instance.output_folder_var.get())

        # Graph Quality (rbw_step_size_hz_var)
        current_value = int(float(self.app_instance.rbw_step_size_hz_var.get()))
        combobox_display, description_display = get_formatted_strings(current_value, graph_quality_drop_down, "resolution_hz", " Hz")
        self.graph_quality_combobox.set(combobox_display)
        self.graph_quality_description_var.set(description_display)
        debug_log(f"Loaded Graph Quality: {combobox_display}. Description: {description_display}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)


        # DWELL (maxhold_time_seconds_var)
        current_value = float(self.app_instance.maxhold_time_seconds_var.get())
        combobox_display, description_display = get_formatted_strings(current_value, dwell_time_drop_down, "time_sec", " s")
        self.dwell_time_combobox.set(combobox_display)
        self.dwell_time_description_var.set(description_display)
        debug_log(f"Loaded DWELL: {combobox_display}. Description: {description_display}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Max Hold Time (cycle_wait_time_seconds_var)
        current_value = float(self.app_instance.cycle_wait_time_seconds_var.get())
        combobox_display, description_display = get_formatted_strings(current_value, cycle_wait_time_presets, "time_sec", " s")
        self.max_hold_time_combobox.set(combobox_display)
        self.max_hold_time_description_var.set(description_display)
        debug_log(f"Loaded Max Hold Time: {combobox_display}. Description: {description_display}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)


        # Scan RBW (scan_rbw_hz_var)
        current_value = float(self.app_instance.scan_rbw_hz_var.get())
        combobox_display, description_display = get_formatted_strings(current_value, rbw_presets, "rbw_hz", " Hz")
        self.scan_rbw_combobox.set(combobox_display)
        self.scan_rbw_description_var.set(description_display)
        debug_log(f"Loaded Scan RBW: {combobox_display}. Description: {description_display}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)


        # Reference Level (reference_level_dbm_var)
        current_value = float(self.app_instance.reference_level_dbm_var.get())
        combobox_display, description_display = get_formatted_strings(current_value, reference_level_drop_down, "level_dbm", " dBm")
        self.reference_level_combobox.set(combobox_display)
        self.reference_level_description_var.set(description_display)
        debug_log(f"Loaded Reference Level: {combobox_display}. Description: {description_display}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)


        # Frequency Shift (freq_shift_hz_var)
        current_value = float(self.app_instance.freq_shift_hz_var.get())
        combobox_display, description_display = get_formatted_strings(current_value, frequency_shift_presets, "shift_hz", " Hz")
        self.frequency_shift_combobox.set(combobox_display)
        self.frequency_shift_description_var.set(description_display)
        debug_log(f"Loaded Frequency Shift: {combobox_display}. Description: {description_display}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)


        # Number of Scan Cycles (num_scan_cycles_var)
        current_value = int(float(self.app_instance.num_scan_cycles_var.get()))
        combobox_display, description_display = get_formatted_strings(current_value, number_of_scans_presets, "scans", " cycles")
        self.num_scan_cycles_combobox.set(combobox_display)
        self.num_scan_cycles_description_var.set(description_display)
        debug_log(f"Loaded Number of Scan Cycles: {combobox_display}. Description: {description_display}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)


        # Preamplifier ON (preamp_on_var)
        current_value = self.app_instance.preamp_on_var.get()
        label = "Yes" if current_value else "No"
        description_text = "Preamplifier is enabled, increasing sensitivity but potentially adding noise." if current_value else "Preamplifier is disabled, reducing sensitivity but potentially cleaner signal."
        combobox_display = label # For Yes/No, label is the display
        description_display = f"{label}: {description_text}" # Label first, then description
        self.preamp_on_combobox.set(combobox_display)
        self.preamp_on_description_var.set(description_display)
        debug_log(f"Loaded Preamplifier ON: {combobox_display}. Description: {description_display}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)


        # High Sensitivity (high_sensitivity_var)
        current_value = self.app_instance.high_sensitivity_var.get()
        label = "Yes" if current_value else "No"
        description_text = "High sensitivity mode enabled, optimizing for detection of weak signals." if current_value else "High sensitivity mode disabled, potentially faster scans but less sensitive."
        combobox_display = label # For Yes/No, label is the display
        description_display = f"{label}: {description_text}" # Label first, then description
        self.high_sensitivity_combobox.set(combobox_display)
        self.high_sensitivity_description_var.set(description_display)
        debug_log(f"Loaded High Sensitivity: {combobox_display}. Description: {description_display}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # RBW Segmentation and Default Focus Width are Entry widgets, not comboboxes,
        # so their values are directly set by their textvariable.
        # No explicit set() needed here as textvariable handles it.


    def _on_tab_selected(self, event):
        # This function description tells me what this function does
        # Called when this tab is selected in the notebook.
        # Can be used to refresh data or update UI elements specific to this tab.
        # For the scan configuration, we ensure settings are loaded/reloaded.
        #
        # Inputs to this function
        #   event (tkinter.Event): The event object that triggered the call.
        #
        # Process of this function
        #   1. Prints a debug message indicating the tab selection.
        #   2. Calls `_load_current_settings_into_dropdowns` to refresh all input fields.
        #   3. Calls `_load_band_selections_from_config` to update checkbox states.
        #
        # Outputs of this function
        #   None. Refreshes the UI elements on tab selection.
        #
        # (2025-07-30) Change: Added to load settings and band selections on tab selection.
        # (20250801.2335.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0014.1) Change: No functional changes.
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
        # This function description tells me what this function does
        # Loads the selected bands from config.ini into the checkboxes.
        # This is called on tab selection to ensure the GUI reflects the config.
        #
        # Inputs to this function
        #   None (operates on self).
        #
        # Process of this function
        #   1. Prints a debug message.
        #   2. Retrieves the last selected bands string from the application's configuration.
        #   3. Parses the string into a list of band names.
        #   4. Iterates through the `app_instance.band_vars` (which contains band data and BooleanVars).
        #   5. Sets the state of each checkbox (BooleanVar) based on whether its band name
        #      is present in the loaded `last_selected_band_names`.
        #
        # Outputs of this function
        #   None. Updates the state of Tkinter checkboxes.
        #
        # (2025-07-30) Change: Implemented loading selected bands from config.
        # (20250801.2335.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0014.1) Change: No functional changes.
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

        debug_log(f"Loaded selected bands from config: {last_selected_band_names}. Checkboxes updated! Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)

