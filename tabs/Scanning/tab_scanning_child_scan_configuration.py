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

current_version = "20250802.0014.7" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 14 * 7 # Example hash, adjust as needed

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
from ref.ref_scanner_setting_lists import scan_modes, reference_levels, attenuation_levels, frequency_shifts


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

        # Initialize Tkinter variables for scan parameters
        # These are now managed by app_instance for centralized access
        # self.scan_name_var = tk.StringVar(value="New Scan") # Managed by app_instance.scan_name_var
        # self.output_folder_var = tk.StringVar(value=os.path.join(os.getcwd(), "DATA", "Scans")) # Managed by app_instance.output_folder_var
        # self.scan_mode_var = tk.StringVar(value=scan_modes[0]["Mode"]) # Managed by app_instance.scan_mode_var
        # self.reference_level_dbm_var = tk.StringVar(value=str(reference_levels[0]["Level"])) # Managed by app_instance.reference_level_dbm_var
        # self.attenuation_var = tk.StringVar(value=str(attenuation_levels[0]["Value"])) # Managed by app_instance.attenuation_var
        # self.freq_shift_var = tk.StringVar(value=str(frequency_shifts[0]["Shift"])) # Managed by app_instance.freq_shift_var
        # self.scan_rbw_segmentation_var = tk.StringVar(value="50000000") # Managed by app_instance.scan_rbw_segmentation_var
        # self.desired_default_focus_width_var = tk.StringVar(value="10000000") # Managed by app_instance.desired_default_focus_width_var

        # Create BooleanVars for each scan band, managed by app_instance
        # self.app_instance.band_vars is already initialized in main_app.py
        # No need to re-initialize here, just ensure they are referenced correctly in _create_widgets

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
        
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating ScanTab widgets... Building the scan configuration form! Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Main grid configuration for the tab
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Scan Parameters (fixed height)
        self.grid_rowconfigure(1, weight=1) # Band Selection (expands)

        # --- Scan Parameters Box ---
        scan_params_frame = ttk.LabelFrame(self, text="Scan Parameters", style='Dark.TLabelframe')
        scan_params_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        scan_params_frame.grid_columnconfigure(1, weight=1) # Allow entry widgets to expand

        # Scan Name
        ttk.Label(scan_params_frame, text="Scan Name:", style='TLabel').grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.scan_name_entry = ttk.Entry(scan_params_frame, textvariable=self.app_instance.scan_name_var, style='TEntry')
        self.scan_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.scan_name_entry.bind("<KeyRelease>", lambda e: save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance))

        # Output Folder
        ttk.Label(scan_params_frame, text="Output Folder:", style='TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.output_folder_entry = ttk.Entry(scan_params_frame, textvariable=self.app_instance.output_folder_var, style='TEntry')
        self.output_folder_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.output_folder_button = ttk.Button(scan_params_frame, text="Browse", command=self._browse_output_folder, style='Blue.TButton')
        self.output_folder_button.grid(row=1, column=2, padx=5, pady=2, sticky="e")
        # No KeyRelease bind for output_folder_entry as it's primarily set by browse

        # Scan Mode
        ttk.Label(scan_params_frame, text="Scan Mode:", style='TLabel').grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.scan_mode_dropdown = ttk.Combobox(
            scan_params_frame,
            textvariable=self.app_instance.scan_mode_var,
            values=[mode["Mode"] for mode in scan_modes],
            state="readonly",
            style='TCombobox'
        )
        self.scan_mode_dropdown.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.scan_mode_dropdown.bind("<<ComboboxSelected>>", self._on_scan_mode_selected)

        # Reference Level (dBm)
        ttk.Label(scan_params_frame, text="Reference Level (dBm):", style='TLabel').grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.reference_level_dbm_dropdown = ttk.Combobox(
            scan_params_frame,
            textvariable=self.app_instance.reference_level_dbm_var,
            values=[str(level["Level"]) for level in reference_levels],
            state="readonly",
            style='TCombobox'
        )
        self.reference_level_dbm_dropdown.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        self.reference_level_dbm_dropdown.bind("<<ComboboxSelected>>", self._on_reference_level_selected)

        # Attenuation (dB)
        ttk.Label(scan_params_frame, text="Attenuation (dB):", style='TLabel').grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.attenuation_dropdown = ttk.Combobox(
            scan_params_frame,
            textvariable=self.app_instance.attenuation_var,
            values=[str(att["Value"]) for att in attenuation_levels],
            state="readonly",
            style='TCombobox'
        )
        self.attenuation_dropdown.grid(row=4, column=1, padx=5, pady=2, sticky="ew")
        self.attenuation_dropdown.bind("<<ComboboxSelected>>", self._on_attenuation_selected)

        # Frequency Shift (MHz)
        ttk.Label(scan_params_frame, text="Frequency Shift (MHz):", style='TLabel').grid(row=5, column=0, padx=5, pady=2, sticky="w")
        self.freq_shift_dropdown = ttk.Combobox(
            scan_params_frame,
            textvariable=self.app_instance.freq_shift_var,
            values=[str(shift["Shift"]) for shift in frequency_shifts],
            state="readonly",
            style='TCombobox'
        )
        self.freq_shift_dropdown.grid(row=5, column=1, padx=5, pady=2, sticky="ew")
        self.freq_shift_dropdown.bind("<<ComboboxSelected>>", self._on_freq_shift_selected)

        # RBW Segmentation (Hz)
        ttk.Label(scan_params_frame, text="RBW Segmentation (Hz):", style='TLabel').grid(row=6, column=0, padx=5, pady=2, sticky="w")
        self.scan_rbw_segmentation_entry = ttk.Entry(scan_params_frame, textvariable=self.app_instance.scan_rbw_segmentation_var, style='TEntry')
        self.scan_rbw_segmentation_entry.grid(row=6, column=1, padx=5, pady=2, sticky="ew")
        self.scan_rbw_segmentation_entry.bind("<KeyRelease>", lambda e: save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance))

        # Desired Default Focus Width (Hz)
        ttk.Label(scan_params_frame, text="Default Focus Width (Hz):", style='TLabel').grid(row=7, column=0, padx=5, pady=2, sticky="w")
        self.desired_default_focus_width_entry = ttk.Entry(scan_params_frame, textvariable=self.app_instance.desired_default_focus_width_var, style='TEntry')
        self.desired_default_focus_width_entry.grid(row=7, column=1, padx=5, pady=2, sticky="ew")
        self.desired_default_focus_width_entry.bind("<KeyRelease>", lambda e: save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance))


        # --- Band Selection Box (with Scrollbar) ---
        bands_frame = ttk.LabelFrame(self, text="Band Selection", style='Dark.TLabelframe')
        bands_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        bands_frame.grid_rowconfigure(0, weight=1) # Allow canvas to expand
        bands_frame.grid_columnconfigure(0, weight=1) # Allow canvas to expand

        self.bands_canvas = tk.Canvas(bands_frame, background="#2e2e2e", highlightthickness=0) # Use canvas for scrollability
        self.bands_canvas.grid(row=0, column=0, sticky="nsew")

        self.bands_scrollbar = ttk.Scrollbar(bands_frame, orient="vertical", command=self.bands_canvas.yview)
        self.bands_scrollbar.grid(row=0, column=1, sticky="ns")
        self.bands_canvas.configure(yscrollcommand=self.bands_scrollbar.set)

        self.bands_inner_frame = ttk.Frame(self.bands_canvas, style='Dark.TFrame') # Frame to hold checkboxes
        self.bands_canvas.create_window((0, 0), window=self.bands_inner_frame, anchor="nw")

        self.bands_inner_frame.bind("<Configure>", self._on_bands_frame_configure)
        self.bands_canvas.bind("<Configure>", self._on_bands_canvas_configure)

        # Populate bands
        self._populate_bands()

        debug_log(f"ScanTab widgets created. Scan configuration form is complete! Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)


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
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Populating band selection checkboxes. Getting all the bands ready! Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Clear existing checkboxes if any
        for widget in self.bands_inner_frame.winfo_children():
            widget.destroy()

        # Arrange checkboxes in a grid within the inner frame
        num_columns = 3 # Adjust as needed
        for i, band_item in enumerate(self.app_instance.band_vars):
            band_name = band_item["band"]["Band Name"]
            checkbox = ttk.Checkbutton(
                self.bands_inner_frame,
                text=band_name,
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
                    version=current_version,
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
                    version=current_version,
                    function=current_function)
        self.bands_canvas.configure(scrollregion=self.bands_canvas.bbox("all"))


    def _on_bands_canvas_configure(self, event):
        # This function description tells me what this function does
        # Configures the width of the `bands_inner_frame` to match the width of the `bands_canvas`.
        # This ensures the inner frame expands horizontally to fill the canvas, preventing
        # horizontal scrolling and maintaining proper layout.
        #
        # Inputs to this function
        #   event (tkinter.Event): The event object that triggered the configuration.
        #
        # Process of this function
        #   1. Prints a debug message.
        #   2. Updates the width of the `bands_inner_frame` to the new width of `bands_canvas`.
        #
        # Outputs of this function
        #   None. Adjusts the inner frame's width.
        #
        # (2025-07-30) Change: Implemented for scrollable band selection.
        # (20250801.2335.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0014.1) Change: No functional changes.
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Configuring bands canvas. Adjusting width for inner frame. Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        self.bands_canvas.itemconfig(self.bands_canvas.find_withtag("all")[0], width=event.width)


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
                    version=current_version,
                    function=current_function)

        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.app_instance.output_folder_var.set(folder_selected)
            save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
            self.console_print_func(f"✅ Output folder set to: {folder_selected}. Ready for data!")
            debug_log(f"Output folder set to: {folder_selected}. Config saved! Version: {current_version}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        else:
            self.console_print_func("ℹ️ Output folder selection cancelled. No changes made!")
            debug_log(f"Output folder selection cancelled. Version: {current_version}",
                        file=current_file,
                        version=current_version,
                        function=current_function)


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
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Scan mode selected: {self.app_instance.scan_mode_var.get()}. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)


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
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Reference level selected: {self.app_instance.reference_level_dbm_var.get()} dBm. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)


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
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Attenuation selected: {self.app_instance.attenuation_var.get()} dB. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)


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
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Frequency shift selected: {self.app_instance.freq_shift_var.get()} MHz. Saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)


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
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Band checkbox changed. Updating selected bands and saving configuration! Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        self.app_instance.selected_bands.clear()
        for band_item in self.app_instance.band_vars:
            if band_item["var"].get():
                self.app_instance.selected_bands.append(band_item["band"]["Band Name"])
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)


    def _load_current_settings_into_dropdowns(self):
        """
        Loads the current instrument settings (from the app_instance's Tkinter variables)
        into the respective dropdowns on the Scan Configuration tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Loading current settings into dropdowns. Syncing UI with config! Version: {current_version}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Scan Name
        self.scan_name_entry.delete(0, tk.END)
        self.scan_name_entry.insert(0, self.app_instance.scan_name_var.get())

        # Output Folder
        self.output_folder_entry.delete(0, tk.END)
        self.output_folder_entry.insert(0, self.app_instance.output_folder_var.get())

        # Scan Mode
        scan_mode_str = self.app_instance.scan_mode_var.get()
        if scan_mode_str in [mode["Mode"] for mode in scan_modes]:
            self.scan_mode_dropdown.set(scan_mode_str)
        else:
            self.scan_mode_dropdown.set(scan_modes[0]["Mode"]) # Default to first option

        # Reference Level
        ref_level_str = self.app_instance.reference_level_dbm_var.get()
        # Ensure the value is valid before setting, handle potential 'N/A' or empty string
        if ref_level_str and ref_level_str in [str(level["Level"]) for level in reference_levels]:
            self.reference_level_dbm_dropdown.set(ref_level_str)
        else:
            self.reference_level_dbm_dropdown.set(str(reference_levels[0]["Level"])) # Default to first option

        # Attenuation
        attenuation_str = self.app_instance.attenuation_var.get()
        if attenuation_str in [str(att["Value"]) for att in attenuation_levels]:
            self.attenuation_dropdown.set(attenuation_str)
        else:
            self.attenuation_dropdown.set(str(attenuation_levels[0]["Value"])) # Default to first option

        # Frequency Shift
        freq_shift_str = self.app_instance.freq_shift_var.get()
        if freq_shift_str in [str(shift["Shift"]) for shift in frequency_shifts]:
            self.freq_shift_dropdown.set(freq_shift_str)
        else:
            self.freq_shift_dropdown.set(frequency_shifts[0]["Shift"]) # Default to first option

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
                    version=current_version,
                    function=current_function)
        self._load_current_settings_into_dropdowns()
        self._load_band_selections_from_config()
        debug_log(f"ScanTab refreshed. Settings are up-to-date! Version: {current_version}",
                    file=current_file,
                    version=current_version,
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
