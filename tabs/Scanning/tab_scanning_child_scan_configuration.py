# tabs/Scanning/tab_scanning_child_scan_configuration.py
#
# This file defines the ScanTab, a Tkinter Frame that contains the Scan Configuration settings
# and the band selection checkboxes. It uses a clean, data-driven approach to populate
# dropdowns and handle user selections for all scan parameters.
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
# Version 20250803.183200.0 (Complete refactor from scratch. Standardized widget creation and event handling.)


import tkinter as tk
from tkinter import ttk, filedialog
import inspect
import os
import subprocess
import sys

# Local application imports
from src.debug_logic import debug_log
from src.settings_and_config.config_manager import save_config
from ref.frequency_bands import SCAN_BAND_RANGES
from ref.ref_scanner_setting_lists import (
    graph_quality_drop_down,
    dwell_time_drop_down,
    cycle_wait_time_presets,
    reference_level_drop_down,
    frequency_shift_presets,
    number_of_scans_presets,
    rbw_presets
)

current_version = "20250803.183200.0"
current_version_hash = (20250803 * 183200 * 0) # Placeholder


class ScanTab(ttk.Frame):
    """
    The Scan Configuration child tab. Contains all UI elements for setting
    up a scan session.
    """
    def __init__(self, master, app_instance, console_print_func, **kwargs):
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func

        # This ID is for managing the scrollable frame
        self.bands_inner_frame_id = None

        # A dictionary to hold the StringVars for all setting descriptions
        self.description_vars = {
            "graph_quality": tk.StringVar(self),
            "dwell_time": tk.StringVar(self),
            "max_hold_time": tk.StringVar(self),
            "scan_rbw": tk.StringVar(self),
            "reference_level": tk.StringVar(self),
            "frequency_shift": tk.StringVar(self),
            "num_scan_cycles": tk.StringVar(self)
        }

        self._create_widgets()
        self.after(100, self._on_tab_selected, None) # Populate UI after widgets are created

    def _create_widgets(self):
        """Creates and arranges all widgets in the tab."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Allow bands frame to expand

        # --- Output Settings ---
        output_frame = ttk.LabelFrame(self, text="Output Settings", style='Dark.TLabelframe')
        output_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        output_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(output_frame, text="Scan Name:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(output_frame, textvariable=self.app_instance.scan_name_var).grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(output_frame, text="Output Folder:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(output_frame, textvariable=self.app_instance.output_folder_var, state="readonly").grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        ttk.Button(output_frame, text="Browse", command=self._browse_output_folder, style='Blue.TButton').grid(row=1, column=2, padx=5, pady=2)
        ttk.Button(output_frame, text="Open Output Folder", command=self._open_output_folder, style='Blue.TButton').grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        # --- Scan Settings ---
        settings_frame = ttk.LabelFrame(self, text="Scan Settings", style='Dark.TLabelframe')
        settings_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        settings_frame.grid_columnconfigure(2, weight=1)

        row_idx = 0
        # This is where we use our generic row creator for most settings
        row_idx = self._create_setting_row(settings_frame, row_idx, "Graph Quality:", self.app_instance.rbw_step_size_hz_var, graph_quality_drop_down, self.description_vars["graph_quality"], "Hz")
        row_idx = self._create_setting_row(settings_frame, row_idx, "DWELL (s):", self.app_instance.maxhold_time_seconds_var, dwell_time_drop_down, self.description_vars["dwell_time"], "s")
        row_idx = self._create_setting_row(settings_frame, row_idx, "Max Hold Time (s):", self.app_instance.cycle_wait_time_seconds_var, cycle_wait_time_presets, self.description_vars["max_hold_time"], "s")
        row_idx = self._create_setting_row(settings_frame, row_idx, "Scan RBW (Hz):", self.app_instance.scan_rbw_hz_var, rbw_presets, self.description_vars["scan_rbw"], "Hz")
        row_idx = self._create_setting_row(settings_frame, row_idx, "Reference Level (dBm):", self.app_instance.reference_level_dbm_var, reference_level_drop_down, self.description_vars["reference_level"], "dBm")
        row_idx = self._create_setting_row(settings_frame, row_idx, "Frequency Shift (Hz):", self.app_instance.freq_shift_var, frequency_shift_presets, self.description_vars["frequency_shift"], "Hz")
        row_idx = self._create_setting_row(settings_frame, row_idx, "Number of Scan Cycles:", self.app_instance.num_scan_cycles_var, number_of_scans_presets, self.description_vars["num_scan_cycles"], "cycles")

        # Handle boolean settings separately for simplicity
        ttk.Label(settings_frame, text="High Sensitivity:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        hs_combo = ttk.Combobox(settings_frame, values=["Yes", "No"], state="readonly", width=35, style='Fixedwidth.TCombobox')
        hs_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        hs_combo.bind("<<ComboboxSelected>>", lambda e: self._on_boolean_combobox_select(e, self.app_instance.high_sensitivity_var))
        row_idx += 1

        ttk.Label(settings_frame, text="Preamplifier ON:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        pa_combo = ttk.Combobox(settings_frame, values=["Yes", "No"], state="readonly", width=35, style='Fixedwidth.TCombobox')
        pa_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        pa_combo.bind("<<ComboboxSelected>>", lambda e: self._on_boolean_combobox_select(e, self.app_instance.preamp_on_var))
        row_idx += 1
        
        # Simple Entry fields
        ttk.Label(settings_frame, text="Scan RBW Segmentation (Hz):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.app_instance.scan_rbw_segmentation_var).grid(row=row_idx, column=1, sticky="ew", columnspan=2, padx=5, pady=2)
        row_idx += 1
        ttk.Label(settings_frame, text="Default Focus Width (Hz):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.app_instance.desired_default_focus_width_var).grid(row=row_idx, column=1, sticky="ew", columnspan=2, padx=5, pady=2)
        row_idx += 1


        # --- Bands to Scan ---
        bands_frame = ttk.LabelFrame(self, text="Bands to Scan", style='Dark.TLabelframe')
        bands_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        bands_frame.grid_rowconfigure(1, weight=1)
        bands_frame.grid_columnconfigure(0, weight=1)

        band_button_frame = ttk.Frame(bands_frame, style='Dark.TFrame')
        band_button_frame.grid(row=0, column=0, pady=5, sticky="ew")
        band_button_frame.grid_columnconfigure(0, weight=1)
        band_button_frame.grid_columnconfigure(1, weight=1)
        ttk.Button(band_button_frame, text="Select All", command=self._select_all_bands, style='Blue.TButton').grid(row=0, column=0, padx=5, sticky="ew")
        ttk.Button(band_button_frame, text="Deselect All", command=self._deselect_all_bands, style='Blue.TButton').grid(row=0, column=1, padx=5, sticky="ew")

        self.bands_canvas = tk.Canvas(bands_frame, background="#2e2e2e", highlightthickness=0)
        bands_scrollbar = ttk.Scrollbar(bands_frame, orient="vertical", command=self.bands_canvas.yview)
        self.bands_canvas.configure(yscrollcommand=bands_scrollbar.set)
        self.bands_canvas.grid(row=1, column=0, sticky="nsew")
        bands_scrollbar.grid(row=1, column=1, sticky="ns")

        self.bands_inner_frame = ttk.Frame(self.bands_canvas, style='Dark.TFrame')
        self.bands_inner_frame_id = self.bands_canvas.create_window((0, 0), window=self.bands_inner_frame, anchor="nw")

        self.bands_inner_frame.bind('<Configure>', lambda e: self.bands_canvas.configure(scrollregion=self.bands_canvas.bbox("all")))
        self.bands_canvas.bind('<Configure>', lambda e: self.bands_canvas.itemconfigure(self.bands_inner_frame_id, width=e.width))

        self._populate_band_checkboxes()
        
    def _create_setting_row(self, parent, row, label_text, app_var, data_list, description_var, unit=""):
        """Generic function to create a labeled combobox row for a setting."""
        ttk.Label(parent, text=label_text).grid(row=row, column=0, padx=5, pady=2, sticky="w")
        
        display_values = [f"{item['value']} {unit}".strip() + f" - {item['label']}" for item in data_list]
        combo = ttk.Combobox(parent, values=display_values, state="readonly", width=35, style='Fixedwidth.TCombobox')
        combo.grid(row=row, column=1, padx=5, pady=2, sticky="w")
        
        # Use a lambda to pass arguments to the event handler
        combo.bind("<<ComboboxSelected>>", lambda event, v=app_var, d=data_list, dv=description_var: 
                   self._on_combobox_select(event, v, d, dv))
        
        ttk.Label(parent, textvariable=description_var, wraplength=400, justify="left").grid(row=row, column=2, padx=5, pady=2, sticky="w")
        
        return row + 1

    def _on_combobox_select(self, event, app_var, data_list, description_var):
        """Generic event handler for our settings comboboxes."""
        selected_display = event.widget.get()
        
        found_item = None
        for item in data_list:
            # Recreate the display string to find the matching item
            item_display = f"{item['value']} {getattr(self, 'unit', '')}".strip() + f" - {item['label']}"
            if selected_display == item_display:
                found_item = item
                break
        
        if found_item:
            app_var.set(found_item['value'])
            description_var.set(found_item['description'])
            save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
        else:
            debug_log(f"FUCK! Could not find a match for '{selected_display}' in the data list.", file=f"{os.path.basename(__file__)} - {current_version}", function="_on_combobox_select")

    def _on_boolean_combobox_select(self, event, app_var):
        """Handler specifically for 'Yes'/'No' comboboxes."""
        is_yes = event.widget.get() == "Yes"
        app_var.set(is_yes)
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)

    def _load_settings_into_ui(self):
        """Populates all UI elements with values from the app_instance variables."""
        # This function will need to be implemented to set the comboboxes correctly on load
        # For now, this is a placeholder. The logic will be similar to _on_combobox_select but in reverse.
        debug_log("UI settings population needs to be fully implemented in _load_settings_into_ui.", file=f"{os.path.basename(__file__)} - {current_version}", function="_load_settings_into_ui")
        
    def _populate_band_checkboxes(self):
        """Populates the scrollable frame with band selection checkboxes."""
        for widget in self.bands_inner_frame.winfo_children():
            widget.destroy() # Clear old widgets

        for i, band_item in enumerate(self.app_instance.band_vars):
            band = band_item["band"]
            var = band_item["var"]
            text = f"{band['Band Name']} ({band['Start MHz']:.3f} - {band['Stop MHz']:.3f} MHz)"
            cb = ttk.Checkbutton(self.bands_inner_frame, text=text, variable=var, style='TCheckbutton',
                                 command=lambda: save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance))
            cb.grid(row=i, column=0, sticky="w", padx=5, pady=2)

    def _select_all_bands(self):
        for band_item in self.app_instance.band_vars:
            band_item["var"].set(True)
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)

    def _deselect_all_bands(self):
        for band_item in self.app_instance.band_vars:
            band_item["var"].set(False)
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)

    def _browse_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.app_instance.output_folder_var.set(folder)
            save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)

    def _open_output_folder(self):
        path = self.app_instance.output_folder_var.get()
        if os.path.isdir(path):
            try:
                if sys.platform == "win32":
                    os.startfile(path)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", path])
                else:
                    subprocess.Popen(["xdg-open", path])
            except Exception as e:
                self.console_print_func(f"❌ Error opening folder: {e}")
        else:
            self.console_print_func(f"❌ Folder not found: {path}")

    def _on_tab_selected(self, event):
        """Called when the tab is selected, ensures UI is synced with config."""
        self._load_settings_into_ui()