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
# Version 20250803.2030.0 (CRITICAL FIX: Corrected import and usage of dwell_times instead of cycle_wait_times.)
# Version 20250803.2045.0 (CRITICAL FIX: Corrected import and usage of dwell_time_presets instead of dwell_times.)
# Version 20250803.2055.0 (CRITICAL FIX: Reverted to cycle_wait_times as per ref_scanner_setting_lists.py.)

current_version = "20250803.2055.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 2055 * 0 # Example hash, adjust as needed

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
  graph_quality_drop_down,dwell_time_drop_down,cycle_wait_time_presets,reference_level_drop_down,frequency_shift_presets,number_of_scans_presets,rbw_presets
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
    A Tkinter Frame that contains the Scan Configuration settings
    and the band selection checkboxes.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the ScanTab.

        Inputs:
            master (tk.Widget): The parent widget (the ttk.Notebook).
            app_instance (App): The main application instance, used for accessing
                                shared state like Tkinter variables and console print function.
            console_print_func (function): Function to print messages to the GUI console.
            **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        """
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else print

        self.bands_inner_frame_id = None # Initialize this attribute

        # NEW: StringVars for descriptions
        self.graph_quality_description_var = tk.StringVar(self, value="")
        self.dwell_time_description_var = tk.StringVar(self, value="")
        self.max_hold_time_description_var = tk.StringVar(self, value="") # NEW: For Max Hold Time description
        self.reference_level_description_var = tk.StringVar(self, value="")
        self.frequency_shift_description_var = tk.StringVar(self, value="")
        self.num_scan_cycles_description_var = tk.StringVar(self, value="")
        self.scan_rbw_description_var = tk.StringVar(self, value="")
        self.preamp_on_description_var = tk.StringVar(self, value="")
        self.high_sensitivity_description_var = tk.StringVar(self, value="")


        self._create_widgets()
        # Initial population of dropdowns and descriptions
        self._load_current_settings_into_dropdowns()


    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Scan Configuration tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_log(f"Creating ScanTab widgets... Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Configure grid for the main frame of this tab
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Output settings frame
        self.grid_rowconfigure(1, weight=0) # Scan settings frame
        self.grid_rowconfigure(2, weight=1) # Bands frame should expand vertically

        # Output Folder and Scan Name (Moved to top)
        output_frame = ttk.LabelFrame(self, text="Output Settings")
        output_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        output_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(output_frame, text="Scan Name:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(output_frame, textvariable=self.app_instance.scan_name_var).grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(output_frame, text="Output Folder:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        output_folder_entry = ttk.Entry(output_frame, textvariable=self.app_instance.output_folder_var)
        output_folder_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        ttk.Button(output_frame, text="Browse", command=self._browse_output_folder).grid(row=1, column=2, padx=2, pady=2)

        # NEW: Open Output Folder Button
        ttk.Button(output_frame, text="Open Output Folder", command=self._open_output_folder).grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")


        # Main frame for Scan Settings
        scan_settings_frame = ttk.LabelFrame(self, text="Scan Settings")
        scan_settings_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew") # Placed after output_frame
        
        # Configure columns for Label, Combobox, and Description
        scan_settings_frame.grid_columnconfigure(0, weight=0) # Label column
        scan_settings_frame.grid_columnconfigure(1, weight=0) # Combobox column (fixed width via style)
        scan_settings_frame.grid_columnconfigure(2, weight=1) # Description column (expands)

        row_idx = 0

        # Graph Quality (formerly RBW Step Size)
        ttk.Label(scan_settings_frame, text="Graph Quality:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.graph_quality_combobox = ttk.Combobox(
            scan_settings_frame,
            # textvariable=self.app_instance.rbw_step_size_hz_var, # Handled by _on_graph_quality_selected
            values=[f"{item['resolution_hz']} Hz - {item['label']}" for item in graph_quality_drop_down], # Numeric value first, then label for the dropdown list
            state="readonly",
            width=35, # Increased width for the combobox
            style='FixedWidth.TCombobox' # Apply custom style
        )
        self.graph_quality_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.graph_quality_combobox.bind("<<ComboboxSelected>>", self._on_graph_quality_selected)
        ttk.Label(scan_settings_frame, textvariable=self.graph_quality_description_var, wraplength=350, justify="left").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # DWELL (now controls maxhold_time_seconds_var, uses dwell_time_drop_down)
        ttk.Label(scan_settings_frame, text="DWELL (s):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.dwell_time_combobox = ttk.Combobox(
            scan_settings_frame,
            # textvariable=self.app_instance.maxhold_time_seconds_var, # NOW CONTROLS MAX HOLD TIME
            values=[f"{item['time_sec']} s - {item['label']}" for item in dwell_time_drop_down], # Numeric value first, then label for the dropdown list
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.dwell_time_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.dwell_time_combobox.bind("<<ComboboxSelected>>", self._on_dwell_time_selected)
        ttk.Label(scan_settings_frame, textvariable=self.dwell_time_description_var, wraplength=350, justify="left").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # Max Hold Time (now controls cycle_wait_time_seconds_var, uses wait_time_presets)
        ttk.Label(scan_settings_frame, text="Max Hold Time (s):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.max_hold_time_combobox = ttk.Combobox(
            scan_settings_frame,
            # textvariable=self.app_instance.cycle_wait_time_seconds_var, # NOW CONTROLS CYCLE WAIT TIME
            values=[f"{item['time_sec']} s - {item['label']}" for item in cycle_wait_time_presets], # Numeric value first, then label for the dropdown list
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.max_hold_time_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.max_hold_time_combobox.bind("<<ComboboxSelected>>", self._on_max_hold_time_selected)
        ttk.Label(scan_settings_frame, textvariable=self.max_hold_time_description_var, wraplength=350, justify="left").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # Scan RBW
        ttk.Label(scan_settings_frame, text="Scan RBW (Hz):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.scan_rbw_combobox = ttk.Combobox(
            scan_settings_frame,
            # textvariable=self.app_instance.scan_rbw_hz_var, # Handled by _on_scan_rbw_selected
            values=[f"{item['rbw_hz']} Hz - {item['label']}" for item in rbw_presets], # Numeric value first, then label for the dropdown list
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.scan_rbw_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.scan_rbw_combobox.bind("<<ComboboxSelected>>", self._on_scan_rbw_selected)
        ttk.Label(scan_settings_frame, textvariable=self.scan_rbw_description_var, wraplength=350, justify="left").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # Reference Level
        ttk.Label(scan_settings_frame, text="Reference Level (dBm):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.reference_level_combobox = ttk.Combobox(
            scan_settings_frame,
            # textvariable=self.app_instance.reference_level_dbm_var, # Handled by _on_reference_level_selected
            values=[f"{item['level_dbm']} dBm - {item['label']}" for item in reference_level_drop_down], # Numeric value first, then label for the dropdown list
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.reference_level_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.reference_level_combobox.bind("<<ComboboxSelected>>", self._on_reference_level_selected)
        ttk.Label(scan_settings_frame, textvariable=self.reference_level_description_var, wraplength=350, justify="left").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # Frequency Shift
        ttk.Label(scan_settings_frame, text="Frequency Shift (Hz):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.frequency_shift_combobox = ttk.Combobox(
            scan_settings_frame,
            # textvariable=self.app_instance.freq_shift_hz_var, # Handled by _on_frequency_shift_selected
            values=[f"{item['shift_hz']} Hz - {item['label']}" for item in frequency_shift_presets], # Numeric value first, then label for the dropdown list
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.frequency_shift_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.frequency_shift_combobox.bind("<<ComboboxSelected>>", self._on_frequency_shift_selected)
        ttk.Label(scan_settings_frame, textvariable=self.frequency_shift_description_var, wraplength=350, justify="left").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # High Sensitivity (now Yes/No dropdown)
        ttk.Label(scan_settings_frame, text="High Sensitivity:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.high_sensitivity_combobox = ttk.Combobox(
            scan_settings_frame,
            # textvariable=self.app_instance.high_sensitivity_var, # Handled by _on_high_sensitivity_selected
            values=["Yes", "No"], # Boolean values don't have a numeric part
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.high_sensitivity_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.high_sensitivity_combobox.bind("<<ComboboxSelected>>", self._on_high_sensitivity_selected)
        ttk.Label(scan_settings_frame, textvariable=self.high_sensitivity_description_var, wraplength=350, justify="left").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # Preamplifier ON (now Yes/No dropdown)
        ttk.Label(scan_settings_frame, text="Preamplifier ON:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.preamp_on_combobox = ttk.Combobox(
            scan_settings_frame,
            # textvariable=self.app_instance.preamp_on_var, # Handled by _on_preamp_on_selected
            values=["Yes", "No"], # Boolean values don't have a numeric part
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.preamp_on_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.preamp_on_combobox.bind("<<ComboboxSelected>>", self._on_preamp_on_selected)
        ttk.Label(scan_settings_frame, textvariable=self.preamp_on_description_var, wraplength=350, justify="left").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # Scan RBW Segmentation (remains as entry as it's not in a dropdown list)
        ttk.Label(scan_settings_frame, text="Scan RBW Segmentation (Hz):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(scan_settings_frame, textvariable=self.app_instance.scan_rbw_segmentation_var).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew", columnspan=2) # Span across combobox and description columns
        row_idx += 1

        # Desired Default Focus Width (remains as entry)
        ttk.Label(scan_settings_frame, text="Default Focus Width (Hz):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(scan_settings_frame, textvariable=self.app_instance.desired_default_focus_width_var).grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew", columnspan=2) # Span across combobox and description columns
        row_idx += 1

        # Number of Scan Cycles
        ttk.Label(scan_settings_frame, text="Number of Scan Cycles:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        self.num_scan_cycles_combobox = ttk.Combobox(
            scan_settings_frame,
            # textvariable=self.app_instance.num_scan_cycles_var, # Handled by _on_num_scan_cycles_selected
            values=[f"{item['scans']} cycles - {item['label']}" for item in number_of_scans_presets], # Numeric value first, then label for the dropdown list
            state="readonly",
            width=35, # Increased width for the combobox
            style='Fixedwidth.TCombobox'
        )
        self.num_scan_cycles_combobox.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        self.num_scan_cycles_combobox.bind("<<ComboboxSelected>>", self._on_num_scan_cycles_selected)
        ttk.Label(scan_settings_frame, textvariable=self.num_scan_cycles_description_var, wraplength=350, justify="left").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        row_idx += 1


        # Frame for Bands to Scan
        bands_frame = ttk.LabelFrame(self, text="Bands to Scan")
        bands_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew") # Placed after scan_settings_frame
        bands_frame.grid_columnconfigure(0, weight=1) # Single column for checkboxes
        bands_frame.grid_rowconfigure(1, weight=1) # Make the canvas/checkbox area expand vertically

        # Buttons for band selection (Moved above the canvas)
        band_button_frame = ttk.Frame(bands_frame)
        band_button_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky="ew") # Span across canvas and scrollbar columns
        band_button_frame.grid_columnconfigure(0, weight=1)
        band_button_frame.grid_columnconfigure(1, weight=1)

        ttk.Button(band_button_frame, text="Select All", command=self._select_all_bands).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(band_button_frame, text="Deselect All", command=self._deselect_all_bands).grid(row=0, column=1, padx=5, pady=5, sticky="ew")


        # Create a canvas and scrollbar for the bands
        self.bands_canvas = tk.Canvas(bands_frame, bg=self.app_instance.style.lookup('TFrame', 'background'))
        self.bands_canvas.grid(row=1, column=0, sticky="nsew") # No columnspan needed for single column, placed at row 1

        bands_scrollbar = ttk.Scrollbar(bands_frame, orient="vertical", command=self.bands_canvas.yview)
        bands_scrollbar.grid(row=1, column=1, sticky="ns") # Scrollbar next to canvas, also at row 1

        self.bands_canvas.configure(yscrollcommand=bands_scrollbar.set)
        # Bind the canvas to resize its scrollregion when its size changes
        self.bands_canvas.bind('<Configure>', self._on_bands_canvas_configure)

        # Frame to hold the checkboxes inside the canvas
        self.bands_inner_frame = ttk.Frame(self.bands_canvas)
        # Store the window ID returned by create_window
        self.bands_inner_frame_id = self.bands_canvas.create_window((0, 0), window=self.bands_inner_frame, anchor="nw")
        
        # Bind the inner frame to update the canvas scrollregion when its size changes
        self.bands_inner_frame.bind('<Configure>', lambda e: self.bands_canvas.configure(scrollregion=self.bands_canvas.bbox("all")))


        self.bands_inner_frame.grid_columnconfigure(0, weight=1) # Only one column for checkboxes

        # Populate band checkboxes
        self._populate_band_checkboxes()

        # Apply fixed width style for Comboboxes (adjust this value if needed)
        # Note: width is in characters, not pixels. A value of 35 should make it significantly wider.
        self.app_instance.style.configure('FixedWidth.TCombobox', width=35)


        debug_log(f"ScanTab widgets created. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)

    def _on_bands_canvas_configure(self, event):
        """
        Adjusts the width of the inner frame within the canvas when the canvas is resized.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_log(f"Configuring bands canvas. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        if self.bands_inner_frame_id: # Ensure the window item has been created
            self.bands_canvas.itemconfigure(self.bands_inner_frame_id, width=event.width)
        self.bands_canvas.configure(scrollregion=self.bands_canvas.bbox("all"))

    def _populate_band_checkboxes(self):
        """
        Creates checkboxes for each frequency band in the SCAN_BAND_RANGES.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_log(f"Populating band checkboxes... Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Clear existing checkboxes before repopulating
        for widget in self.bands_inner_frame.winfo_children():
            widget.destroy()

        # Changed to a single column layout
        for i, band_item in enumerate(self.app_instance.band_vars):
            band = band_item["band"]
            var = band_item["var"]
            band_name = band["Band Name"]
            start_freq = band["Start MHz"]
            stop_freq = band["Stop MHz"]

            # Display frequencies in MHz for readability
            checkbox_text = f"{band_name} ({start_freq:.3f} - {stop_freq:.3f} MHz)"
            ttk.Checkbutton(self.bands_inner_frame, text=checkbox_text, variable=var).grid(row=i, column=0, padx=5, pady=2, sticky="w")
            debug_log(f"Added checkbox for: {band_name}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Update the scrollregion of the canvas after populating checkboxes
        self.update_idletasks() # Ensure widgets are rendered before calculating bbox
        # The _on_bands_canvas_configure method will handle updating the scrollregion
        # when the canvas size is known. We just need to ensure the inner frame is sized correctly.
        # This line is no longer strictly necessary here if _on_bands_canvas_configure is called on resize.
        # However, it's good to call it once after initial population.
        if hasattr(self, 'bands_canvas'):
            self.bands_canvas.config(scrollregion=self.bands_canvas.bbox("all"))


    def _select_all_bands(self):
        """
        Sets all band selection checkboxes to True.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_log(f"Selecting all bands... Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        for band_item in self.app_instance.band_vars:
            band_item["var"].set(True)
        self.console_print_func("✅ All bands selected.")
        save_config(self.app_instance) # Save changes to config

    def _deselect_all_bands(self):
        """
        Sets all band selection checkboxes to False.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_log(f"Deselecting all bands... Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        for band_item in self.app_instance.band_vars:
            band_item["var"].set(False)
        self.console_print_func("✅ All bands deselected.")
        save_config(self.app_instance) # Save changes to config

    def _browse_output_folder(self):
        """
        Opens a file dialog to select the output folder for scan data.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_log(f"Browsing output folder from ScanTab... Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        # Use the app_instance.output_folder_var which is now correctly linked to config
        folder_selected = filedialog.askdirectory(initialdir=self.app_instance.output_folder_var.get())
        if folder_selected:
            self.app_instance.output_folder_var.set(folder_selected)
            self.console_print_func(f"Output folder set to: {folder_selected}")
            debug_log(f"Output folder set to: {folder_selected}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
            save_config(self.app_instance) # Save changes to config

    def _open_output_folder(self):
        """
        Opens the directory specified in the output_folder_var using the default file explorer.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
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


    def _on_graph_quality_selected(self, event):
        """
        Handles selection in the Graph Quality dropdown.
        Updates the app_instance's rbw_step_size_hz_var and the description.
        Sets the combobox display to the numeric value.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        # The selected_item will be in the format "VALUE Unit - LABEL"
        selected_item_text = self.graph_quality_combobox.get()
        debug_log(f"Graph Quality selected: {selected_item_text}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Extract the label from the selected_item_text
        # Assuming format "VALUE Unit - LABEL" or "LABEL" for boolean
        if ' - ' in selected_item_text:
            selected_label = selected_item_text.split(' - ')[1].strip()
        else:
            selected_label = selected_item_text # For boolean values like "Yes", "No"

        for item in graph_quality_drop_down:
            if item["label"] == selected_label:
                self.app_instance.rbw_step_size_hz_var.set(item["resolution_hz"])
                self.graph_quality_description_var.set(f"{item['label']}: {item['description']}") # Label first, then description
                self.graph_quality_combobox.set(f"{item['resolution_hz']} Hz") # Numeric value ONLY
                debug_log(f"Set rbw_step_size_hz_var to {item['resolution_hz']} Hz. Description: {self.graph_quality_description_var.get()}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                break
        save_config(self.app_instance)

    def _on_dwell_time_selected(self, event):
        """
        Handles selection in the DWELL dropdown.
        Updates the app_instance's maxhold_time_seconds_var and the description.
        Sets the combobox display to the numeric value.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        selected_item_text = self.dwell_time_combobox.get()
        debug_log(f"DWELL selected: {selected_item_text}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        if ' - ' in selected_item_text:
            selected_label = selected_item_text.split(' - ')[1].strip()
        else:
            selected_label = selected_item_text

        for item in dwell_time_drop_down: # Uses dwell_time_drop_down
            if item["label"] == selected_label:
                self.app_instance.maxhold_time_seconds_var.set(item["time_sec"]) # Updates maxhold_time_seconds_var
                self.dwell_time_description_var.set(f"{item['label']}: {item['description']}") # Label first, then description
                self.dwell_time_combobox.set(f"{item['time_sec']} s") # Numeric value ONLY
                debug_log(f"Set maxhold_time_seconds_var to {item['time_sec']} s. Description: {self.dwell_time_description_var.get()}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                break
        save_config(self.app_instance)

    def _on_max_hold_time_selected(self, event):
        """
        Handles selection in the Max Hold Time dropdown.
        Updates the app_instance's cycle_wait_time_seconds_var and the description.
        Sets the combobox display to the numeric value.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        selected_item_text = self.max_hold_time_combobox.get()
        debug_log(f"Max Hold Time selected: {selected_item_text}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        if ' - ' in selected_item_text:
            selected_label = selected_item_text.split(' - ')[1].strip()
        else:
            selected_label = selected_item_text

        for item in cycle_wait_time_presets: # Uses wait_time_presets
            if item["label"] == selected_label:
                self.app_instance.cycle_wait_time_seconds_var.set(item["time_sec"]) # Updates cycle_wait_time_seconds_var
                self.max_hold_time_description_var.set(f"{item['label']}: {item['description']}") # Label first, then description
                self.max_hold_time_combobox.set(f"{item['time_sec']} s") # Numeric value ONLY
                debug_log(f"Set cycle_wait_time_seconds_var to {item['time_sec']} s. Description: {self.max_hold_time_description_var.get()}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                break
        save_config(self.app_instance)


    def _on_scan_rbw_selected(self, event):
        """
        Handles selection in the Scan RBW dropdown.
        Updates the app_instance's scan_rbw_hz_var and the description.
        Sets the combobox display to the numeric value.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        selected_item_text = self.scan_rbw_combobox.get()
        debug_log(f"Scan RBW selected: {selected_item_text}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        if ' - ' in selected_item_text:
            selected_label = selected_item_text.split(' - ')[1].strip()
        else:
            selected_label = selected_item_text

        for item in rbw_presets:
            if item["label"] == selected_label:
                self.app_instance.scan_rbw_hz_var.set(item["rbw_hz"])
                self.scan_rbw_description_var.set(f"{item['label']}: {item['description']}") # Label first, then description
                self.scan_rbw_combobox.set(f"{item['rbw_hz']} Hz") # Numeric value ONLY
                debug_log(f"Set scan_rbw_hz_var to {item['rbw_hz']} Hz. Description: {self.scan_rbw_description_var.get()}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                break
        save_config(self.app_instance)

    def _on_reference_level_selected(self, event):
        """
        Handles selection in the Reference Level dropdown.
        Updates the app_instance's reference_level_dbm_var and the description.
        Sets the combobox display to the numeric value.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        selected_item_text = self.reference_level_combobox.get()
        debug_log(f"Reference Level selected: {selected_item_text}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        if ' - ' in selected_item_text:
            selected_label = selected_item_text.split(' - ')[1].strip()
        else:
            selected_label = selected_item_text

        for item in reference_level_drop_down:
            if item["label"] == selected_label:
                self.app_instance.reference_level_dbm_var.set(item["level_dbm"])
                self.reference_level_description_var.set(f"{item['label']}: {item['description']}") # Label first, then description
                self.reference_level_combobox.set(f"{item['level_dbm']} dBm") # Numeric value ONLY
                debug_log(f"Set reference_level_dbm_var to {item['level_dbm']} dBm. Description: {self.reference_level_description_var.get()}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                break
        save_config(self.app_instance)

    def _on_frequency_shift_selected(self, event):
        """
        Handles selection in the Frequency Shift dropdown.
        Updates the app_instance's freq_shift_hz_var and the description.
        Sets the combobox display to the numeric value.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        selected_item_text = self.frequency_shift_combobox.get()
        debug_log(f"Frequency Shift selected: {selected_item_text}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        if ' - ' in selected_item_text:
            selected_label = selected_item_text.split(' - ')[1].strip()
        else:
            selected_label = selected_item_text

        for item in frequency_shift_presets:
            if item["label"] == selected_label:
                self.app_instance.freq_shift_hz_var.set(item["shift_hz"])
                self.frequency_shift_description_var.set(f"{item['label']}: {item['description']}") # Label first, then description
                self.frequency_shift_combobox.set(f"{item['shift_hz']} Hz") # Numeric value ONLY
                debug_log(f"Set freq_shift_hz_var to {item['shift_hz']} Hz. Description: {self.frequency_shift_description_var.get()}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                break
        save_config(self.app_instance)

    def _on_num_scan_cycles_selected(self, event):
        """
        Handles selection in the Number of Scan Cycles dropdown.
        Updates the app_instance's num_scan_cycles_var and the description.
        Sets the combobox display to the numeric value.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        selected_item_text = self.num_scan_cycles_combobox.get()
        debug_log(f"Number of Scan Cycles selected: {selected_item_text}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        if ' - ' in selected_item_text:
            selected_label = selected_item_text.split(' - ')[1].strip()
        else:
            selected_label = selected_item_text

        for item in number_of_scans_presets:
            if item["label"] == selected_label:
                self.app_instance.num_scan_cycles_var.set(item["scans"])
                self.num_scan_cycles_description_var.set(f"{item['label']}: {item['description']}") # Label first, then description
                self.num_scan_cycles_combobox.set(f"{item['scans']} cycles") # Numeric value ONLY
                debug_log(f"Set num_scan_cycles_var to {item['scans']} cycles. Description: {self.num_scan_cycles_description_var.get()}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                break
        save_config(self.app_instance)

    def _on_preamp_on_selected(self, event):
        """
        Handles selection in the Preamplifier ON dropdown (Yes/No).
        Updates the app_instance's preamp_on_var and the description.
        Sets the combobox display to the selected label.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        selected_label = self.preamp_on_combobox.get()
        debug_log(f"Preamplifier ON selected: {selected_label}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        if selected_label == "Yes":
            self.app_instance.preamp_on_var.set(True)
            self.preamp_on_description_var.set(f"{selected_label}: Preamplifier is enabled, increasing sensitivity but potentially adding noise.") # Label first, then description
        else:
            self.app_instance.preamp_on_var.set(False)
            self.preamp_on_description_var.set(f"{selected_label}: Preamplifier is disabled, reducing sensitivity but potentially cleaner signal.") # Label first, then description
        self.preamp_on_combobox.set(selected_label) # Set combobox display to label (Yes/No)
        debug_log(f"Set preamp_on_var to {self.app_instance.preamp_on_var.get()}. Description: {self.preamp_on_description_var.get()}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        save_config(self.app_instance)

    def _on_high_sensitivity_selected(self, event):
        """
        Handles selection in the High Sensitivity dropdown (Yes/No).
        Updates the app_instance's high_sensitivity_var and the description.
        Sets the combobox display to the selected label.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        selected_label = self.high_sensitivity_combobox.get()
        debug_log(f"High Sensitivity selected: {selected_label}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        if selected_label == "Yes":
            self.app_instance.high_sensitivity_var.set(True)
            self.high_sensitivity_description_var.set(f"{selected_label}: High sensitivity mode enabled, optimizing for detection of weak signals.") # Label first, then description
        else:
            self.app_instance.high_sensitivity_var.set(False)
            self.high_sensitivity_description_var.set(f"{selected_label}: High sensitivity mode disabled, potentially faster scans but less sensitive.") # Label first, then description
        self.high_sensitivity_combobox.set(selected_label) # Set combobox display to label (Yes/No)
        debug_log(f"Set high_sensitivity_var to {self.app_instance.high_sensitivity_var.get()}. Description: {self.high_sensitivity_description_var.get()}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        save_config(self.app_instance)

    def _load_current_settings_into_dropdowns(self):
        """
        Loads the current values from app_instance's Tkinter variables into the dropdowns
        and updates their corresponding description labels. This is called on initialization
        and when the tab is selected.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_log(f"Loading current settings into dropdowns. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Helper to find label and description for a given value, and format display string
        def get_formatted_strings(value, dropdown_list, value_key, unit=""):
            for item in dropdown_list:
                if item[value_key] == value:
                    # Format for combobox display (ONLY value + unit)
                    combobox_display = f"{item[value_key]}{unit}" if unit else f"{item[value_key]}"
                    # Format for dropdown list values (value + unit + label)
                    dropdown_list_value = f"{item[value_key]}{unit} - {item['label']}" if unit else f"{item[value_key]} - {item['label']}"
                    # Format for description label (label + description)
                    description_display = f"{item['label']}: {item['description']}"
                    return combobox_display, description_display, dropdown_list_value
            # Fallback for custom values not in presets
            combobox_display_fallback = f"{value}{unit}" if unit else f"{value}"
            dropdown_list_value_fallback = f"{value}{unit} - Custom" if unit else f"{value} - Custom"
            description_display_fallback = f"Custom: Custom value detected. Select from dropdown to get description."
            return combobox_display_fallback, description_display_fallback, dropdown_list_value_fallback

        # Graph Quality (rbw_step_size_hz_var)
        current_value = int(float(self.app_instance.rbw_step_size_hz_var.get()))
        combobox_display, description_display, dropdown_list_value = get_formatted_strings(current_value, graph_quality_drop_down, "resolution_hz", " Hz")
        self.graph_quality_combobox.set(combobox_display)
        self.graph_quality_combobox['values'] = [f"{item['resolution_hz']} Hz - {item['label']}" for item in graph_quality_drop_down] # Ensure dropdown list is updated
        self.graph_quality_description_var.set(description_display)
        debug_log(f"Loaded Graph Quality: {combobox_display}. Description: {description_display}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)


        # DWELL (now uses maxhold_time_seconds_var, was cycle_wait_time_seconds_var)
        current_value = float(self.app_instance.maxhold_time_seconds_var.get()) # Changed to maxhold_time_seconds_var
        combobox_display, description_display, dropdown_list_value = get_formatted_strings(current_value, dwell_time_drop_down, "time_sec", " s")
        self.dwell_time_combobox.set(combobox_display)
        self.dwell_time_combobox['values'] = [f"{item['time_sec']} s - {item['label']}" for item in dwell_time_drop_down] # Ensure dropdown list is updated
        self.dwell_time_description_var.set(description_display)
        debug_log(f"Loaded DWELL: {combobox_display}. Description: {description_display}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Max Hold Time (now uses cycle_wait_time_seconds_var, was maxhold_time_seconds_var)
        current_value = int(float(self.app_instance.cycle_wait_time_seconds_var.get())) # Changed to cycle_wait_time_seconds_var
        combobox_display, description_display, dropdown_list_value = get_formatted_strings(current_value, cycle_wait_time_presets, "time_sec", " s")
        self.max_hold_time_combobox.set(combobox_display)
        self.max_hold_time_combobox['values'] = [f"{item['time_sec']} s - {item['label']}" for item in cycle_wait_time_presets] # Ensure dropdown list is updated
        self.max_hold_time_description_var.set(description_display)
        debug_log(f"Loaded Max Hold Time: {combobox_display}. Description: {description_display}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)


        # Scan RBW (scan_rbw_hz_var)
        current_value = int(float(self.app_instance.scan_rbw_hz_var.get()))
        combobox_display, description_display, dropdown_list_value = get_formatted_strings(current_value, rbw_presets, "rbw_hz", " Hz")
        self.scan_rbw_combobox.set(combobox_display)
        self.scan_rbw_combobox['values'] = [f"{item['rbw_hz']} Hz - {item['label']}" for item in rbw_presets] # Ensure dropdown list is updated
        self.scan_rbw_description_var.set(description_display)
        debug_log(f"Loaded Scan RBW: {combobox_display}. Description: {description_display}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)


        # Reference Level (reference_level_dbm_var)
        current_value = int(float(self.app_instance.reference_level_dbm_var.get()))
        combobox_display, description_display, dropdown_list_value = get_formatted_strings(current_value, reference_level_drop_down, "level_dbm", " dBm")
        self.reference_level_combobox.set(combobox_display)
        self.reference_level_combobox['values'] = [f"{item['level_dbm']} dBm - {item['label']}" for item in reference_level_drop_down] # Ensure dropdown list is updated
        self.reference_level_description_var.set(description_display)
        debug_log(f"Loaded Reference Level: {combobox_display}. Description: {description_display}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)


        # Frequency Shift (freq_shift_hz_var)
        current_value = int(float(self.app_instance.freq_shift_hz_var.get()))
        combobox_display, description_display, dropdown_list_value = get_formatted_strings(current_value, frequency_shift_presets, "shift_hz", " Hz")
        self.frequency_shift_combobox.set(combobox_display)
        self.frequency_shift_combobox['values'] = [f"{item['shift_hz']} Hz - {item['label']}" for item in frequency_shift_presets] # Ensure dropdown list is updated
        self.frequency_shift_description_var.set(description_display)
        debug_log(f"Loaded Frequency Shift: {combobox_display}. Description: {description_display}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)


        # Number of Scan Cycles (num_scan_cycles_var)
        current_value = int(self.app_instance.num_scan_cycles_var.get())
        combobox_display, description_display, dropdown_list_value = get_formatted_strings(current_value, number_of_scans_presets, "scans", " cycles")
        self.num_scan_cycles_combobox.set(combobox_display)
        self.num_scan_cycles_combobox['values'] = [f"{item['scans']} cycles - {item['label']}" for item in number_of_scans_presets] # Ensure dropdown list is updated
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


    def _on_tab_selected(self, event):
        """
        Callback for when this tab is selected.
        This can be used to refresh data or update UI elements specific to this tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_log(f"Scan Configuration Tab selected. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        # Load band selections from config when the tab is revisited.
        self._load_band_selections_from_config()
        # Also refresh dropdowns and descriptions
        self._load_current_settings_into_dropdowns()


    def _load_band_selections_from_config(self):
        """
        Loads the selected bands from config.ini into the checkboxes.
        This is called on tab selection to ensure the GUI reflects the config.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_log(f"Loading band selections from config.ini... Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Get the last used selected bands from config using the new prefixed key
        last_selected_bands_str = self.app_instance.config.get('LAST_USED_SETTINGS', 'last_scan_configuration__selected_bands', fallback='')
        last_selected_band_names = [name.strip() for name in last_selected_bands_str.split(',') if name.strip()]

        # Set the state of each checkbox based on the loaded bands
        for band_item in self.app_instance.band_vars:
            band_name = band_item["band"]["Band Name"]
            band_item["var"].set(band_name in last_selected_band_names)

        debug_log(f"Loaded selected bands from config: {last_selected_band_names}. Version: {current_version}", file=current_file, function=current_function, console_print_func=self.console_print_func)
