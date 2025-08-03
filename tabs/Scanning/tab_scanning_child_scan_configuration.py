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
# Version 20250803.193000.1 (Restored missing text fields and converted band selection to buttons.)
# Version 20250803.192500.0 (FIXED: Implemented config saving on change and loading of settings into UI.)
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

current_version = "20250803.193000.1"

class ScanTab(ttk.Frame):
    """
    The Scan Configuration child tab. Contains all UI elements for setting
    up a scan session.
    """
    def __init__(self, master, app_instance, console_print_func, **kwargs):
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func

        self.bands_inner_frame_id = None
        self.setting_widgets = {}
        self._create_widgets()
        self.after(100, self._on_tab_selected)

    def _create_widgets(self):
        """Creates and arranges all widgets in the tab."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

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
        self._create_setting_row(settings_frame, row_idx, "graph_quality", "Graph Quality:", self.app_instance.rbw_step_size_hz_var, graph_quality_drop_down, "Hz"); row_idx += 1
        self._create_setting_row(settings_frame, row_idx, "dwell_time", "DWELL (s):", self.app_instance.maxhold_time_seconds_var, dwell_time_drop_down, "s"); row_idx += 1
        self._create_setting_row(settings_frame, row_idx, "max_hold_time", "Max Hold Time (s):", self.app_instance.cycle_wait_time_seconds_var, cycle_wait_time_presets, "s"); row_idx += 1
        self._create_setting_row(settings_frame, row_idx, "scan_rbw", "Scan RBW (Hz):", self.app_instance.scan_rbw_hz_var, rbw_presets, "Hz"); row_idx += 1
        self._create_setting_row(settings_frame, row_idx, "reference_level", "Reference Level (dBm):", self.app_instance.reference_level_dbm_var, reference_level_drop_down, "dBm"); row_idx += 1
        self._create_setting_row(settings_frame, row_idx, "frequency_shift", "Frequency Shift (Hz):", self.app_instance.freq_shift_var, frequency_shift_presets, "Hz"); row_idx += 1
        self._create_setting_row(settings_frame, row_idx, "num_scan_cycles", "Number of Scan Cycles:", self.app_instance.num_scan_cycles_var, number_of_scans_presets, "cycles"); row_idx += 1

        # Boolean settings
        ttk.Label(settings_frame, text="High Sensitivity:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w");
        hs_combo = ttk.Combobox(settings_frame, values=["Yes", "No"], state="readonly", width=35); hs_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        hs_combo.bind("<<ComboboxSelected>>", lambda e, v=self.app_instance.high_sensitivity_var: self._on_boolean_combobox_select(e, v)); self.setting_widgets['high_sensitivity'] = {'widget': hs_combo, 'var': self.app_instance.high_sensitivity_var}; row_idx += 1

        ttk.Label(settings_frame, text="Preamplifier ON:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w");
        pa_combo = ttk.Combobox(settings_frame, values=["Yes", "No"], state="readonly", width=35); pa_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        pa_combo.bind("<<ComboboxSelected>>", lambda e, v=self.app_instance.preamp_on_var: self._on_boolean_combobox_select(e, v)); self.setting_widgets['preamp_on'] = {'widget': pa_combo, 'var': self.app_instance.preamp_on_var}; row_idx += 1
        
        # --- ADDED BACK: Simple Entry fields ---
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

        self._populate_band_buttons()
        
    def _create_setting_row(self, parent, row, key, label_text, app_var, data_list, unit=""):
        """Generic function to create and store a labeled combobox row for a setting."""
        ttk.Label(parent, text=label_text).grid(row=row, column=0, padx=5, pady=2, sticky="w")
        display_values = [f"{item['value']} {unit}".strip() + f" - {item['label']}" for item in data_list]
        combo = ttk.Combobox(parent, values=display_values, state="readonly", width=35)
        combo.grid(row=row, column=1, padx=5, pady=2, sticky="w")
        description_var = tk.StringVar(self)
        ttk.Label(parent, textvariable=description_var, wraplength=400, justify="left").grid(row=row, column=2, padx=5, pady=2, sticky="w")
        combo.bind("<<ComboboxSelected>>", lambda e, v=app_var, d=data_list, dv=description_var, u=unit: self._on_combobox_select(e, v, d, dv, u))
        self.setting_widgets[key] = {'widget': combo, 'var': app_var, 'data': data_list, 'desc_var': description_var, 'unit': unit}

    def _on_combobox_select(self, event, app_var, data_list, description_var, unit):
        """Generic event handler for our settings comboboxes."""
        selected_display = event.widget.get()
        found_item = None
        for item in data_list:
            item_display = f"{item['value']} {unit}".strip() + f" - {item['label']}"
            if selected_display == item_display:
                found_item = item
                break
        if found_item:
            app_var.set(found_item['value'])
            description_var.set(found_item['description'])
            save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)

    def _on_boolean_combobox_select(self, event, app_var):
        """Handler specifically for 'Yes'/'No' comboboxes."""
        is_yes = event.widget.get() == "Yes"
        app_var.set(is_yes)
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)

    def _set_combobox_display_from_value(self, key):
        """Helper to find and set the display text and description for a given raw value."""
        widget_info = self.setting_widgets.get(key)
        if not widget_info: return
        combo, app_var, data_list, desc_var, unit = widget_info['widget'], widget_info['var'], widget_info['data'], widget_info['desc_var'], widget_info['unit']
        current_value = app_var.get()
        found_item = None
        for item in data_list:
            if isinstance(current_value, float) and abs(float(item['value']) - current_value) < 1e-9:
                found_item = item
                break
            elif str(item['value']) == str(current_value):
                found_item = item
                break
        if found_item:
            display_text = f"{found_item['value']} {unit}".strip() + f" - {found_item['label']}"
            combo.set(display_text)
            desc_var.set(found_item['description'])
        else:
            combo.set(f"{current_value} {unit}".strip() + " - Custom")
            desc_var.set("Custom value not in presets.")

    def _load_settings_into_ui(self):
        """Populates all UI elements with values from the app_instance variables."""
        for key in self.setting_widgets:
            if key in ['high_sensitivity', 'preamp_on']:
                widget_info = self.setting_widgets[key]
                widget_info['widget'].set("Yes" if widget_info['var'].get() else "No")
            else:
                self._set_combobox_display_from_value(key)

    def _populate_band_buttons(self):
        """Populates the scrollable frame with band selection buttons."""
        for widget in self.bands_inner_frame.winfo_children():
            widget.destroy()
        
        self.bands_inner_frame.grid_columnconfigure(0, weight=1)
        self.bands_inner_frame.grid_columnconfigure(1, weight=1)

        for i, band_item in enumerate(self.app_instance.band_vars):
            band = band_item["band"]
            var = band_item["var"]
            
            button_text = f"{band['Band Name']}\nStart: {band['Start MHz']:.3f} MHz\nStop: {band['Stop MHz']:.3f} MHz"
            
            btn = ttk.Button(self.bands_inner_frame, text=button_text)
            band_item['widget'] = btn # Store widget reference
            
            btn.configure(command=lambda v=var, b=btn: self._on_band_button_toggle(v, b))
            
            style = "Band.Selected.TButton" if var.get() else "Band.TButton"
            btn.configure(style=style)

            row, col = divmod(i, 2)
            btn.grid(row=row, column=col, sticky="ew", padx=2, pady=2)

    def _on_band_button_toggle(self, band_var, button_widget):
        """Toggles the state of a band and updates its button style."""
        new_state = not band_var.get()
        band_var.set(new_state)
        
        style = "Band.Selected.TButton" if new_state else "Band.TButton"
        button_widget.configure(style=style)
        
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)

    def _update_all_band_button_styles(self):
        """Updates the style of all band buttons to match their variable state."""
        for band_item in self.app_instance.band_vars:
            var = band_item["var"]
            widget = band_item.get("widget")
            if widget:
                style = "Band.Selected.TButton" if var.get() else "Band.TButton"
                widget.configure(style=style)

    def _select_all_bands(self):
        for band_item in self.app_instance.band_vars:
            band_item["var"].set(True)
        self._update_all_band_button_styles()
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)

    def _deselect_all_bands(self):
        for band_item in self.app_instance.band_vars:
            band_item["var"].set(False)
        self._update_all_band_button_styles()
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

    def _on_tab_selected(self, event=None):
        """Called when the tab is selected, ensures UI is synced with config."""
        self._load_settings_into_ui()
