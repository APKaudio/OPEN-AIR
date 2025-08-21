# tabs/Scanning/tab_scanning_child_scan_configuration.py
#
# This file defines the ScanTab, a Tkinter Frame that provides a user interface
# for configuring scanner settings such as frequency span, RBW, sweep time, etc.
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
# Version 20250815.151740.3
# FIX: Corrected import names and paths after refactoring of preset lists.

current_version = "20250815.151740.3"
current_version_hash = (20250815 * 151740 * 3)

import tkinter as tk
from tkinter import ttk
import inspect
import os
import subprocess
import sys
from tkinter import filedialog


from display.debug_logic import debug_log
from display.console_logic import console_log
from settings_and_config.config_manager import save_config

# Import presets that have associated handlers
from ref.ref_scanner_setting_lists import (
    
    PRESET_AMPLITUDE_REFERENCE_LEVEL,
    PRESET_AMPLITUDE_PREAMP_STATE,
    PRESET_AMPLITUDE_HIGH_SENSITIVITY_STATE,
    PRESET_AMPLITUDE_POWER_ATTENUATION,
    PRESET_BANDWIDTH_RBW,
    PRESET_FREQUENCY_SPAN,
    PRESET_TRACE_MODES,
    PRESET_CONTINUOUS_MODE
)

# Import presets for UI only
from ref.ref_scanning_setting import (
    PRESET_SWEEP_TIME,
    PRESET_DISPLAY_GRAPH_QUALITY,
    PRESET_CYCLE_WAIT_TIME,
    PRESET_FREQUENCY_SHIFT,
    PRESET_NUMBER_OF_SCANS,
)


class ScanTab(ttk.Frame):
    """
    The Scan Configuration child tab. Contains all UI elements for setting
    up a scan session.
    """
    def __init__(self, master, app_instance, console_print_func, **kwargs):
        # This function description tells me what this function does
        # Initializes the ScanTab, creating a frame to hold the main scan
        # configuration settings, such as output folder, scan name, and
        # instrument parameters.
        #
        # Inputs to this function
        #   master (tk.Widget): The parent widget, typically a ttk.Notebook.
        #   app_instance (object): A reference to the main application instance.
        #   console_print_func (function): A function to use for console output.
        #   **kwargs: Arbitrary keyword arguments.
        #
        # Outputs of this function
        #   None. Initializes the Tkinter frame and its internal state.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing ScanTab...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func

        self.setting_widgets = {}
        self._create_widgets()
        self.after(100, self._on_tab_selected)
        
        debug_log(f"ScanTab initialized. Scan configuration widgets are ready.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    def _create_widgets(self):
        # This function description tells me what this function does
        # Creates and arranges all widgets in the tab, including the output
        # settings frame and the instrument scan settings frame.
        #
        # Inputs to this function
        #   None.
        #
        # Outputs of this function
        #   None. Populates the tab with GUI elements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating ScanTab widgets.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
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
        # self._create_setting_row(settings_frame, row_idx, "graph_quality", "Graph Quality:", self.app_instance.rbw_step_size_hz_var, graph_quality_drop_down, "Hz"); row_idx += 1
        # self._create_setting_row(settings_frame, row_idx, "dwell_time", "DWELL (s):", self.app_instance.maxhold_time_seconds_var, dwell_time_drop_down, "s"); row_idx += 1
        # self._create_setting_row(settings_frame, row_idx, "max_hold_time", "Max Hold Time (s):", self.app_instance.cycle_wait_time_seconds_var, cycle_wait_time_presets, "s"); row_idx += 1
        # self._create_setting_row(settings_frame, row_idx, "scan_rbw", "Scan RBW (Hz):", self.app_instance.scan_rbw_hz_var, rbw_presets, "Hz"); row_idx += 1
        # self._create_setting_row(settings_frame, row_idx, "reference_level", "Reference Level (dBm):", self.app_instance.reference_level_dbm_var, reference_level_drop_down, "dBm"); row_idx += 1
        # self._create_setting_row(settings_frame, row_idx, "frequency_shift", "Frequency Shift (Hz):", self.app_instance.freq_shift_var, frequency_shift_presets, "Hz"); row_idx += 1
        # self._create_setting_row(settings_frame, row_idx, "num_scan_cycles", "Number of Scan Cycles:", self.app_instance.num_scan_cycles_var, number_of_scans_presets, "cycles"); row_idx += 1

        # # Boolean settings
        # ttk.Label(settings_frame, text="High Sensitivity:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w");
        # hs_combo = ttk.Combobox(settings_frame, values=["Yes", "No"], state="readonly", width=35); hs_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        # hs_combo.bind("<<ComboboxSelected>>", lambda e, v=self.app_instance.high_sensitivity_var: self._on_boolean_combobox_select(e, v)); self.setting_widgets['high_sensitivity'] = {'widget': hs_combo, 'var': self.app_instance.high_sensitivity_var}; row_idx += 1
        #
        # ttk.Label(settings_frame, text="Preamplifier ON:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w");
        # pa_combo = ttk.Combobox(settings_frame, values=["Yes", "No"], state="readonly", width=35); pa_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        # pa_combo.bind("<<ComboboxSelected>>", lambda e, v=self.app_instance.preamp_on_var: self._on_boolean_combobox_select(e, v)); self.setting_widgets['preamp_on'] = {'widget': pa_combo, 'var': self.app_instance.preamp_on_var}; row_idx += 1
        #
        # # --- ADDED BACK: Simple Entry fields ---
        # ttk.Label(settings_frame, text="Scan RBW Segmentation (Hz):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        # ttk.Entry(settings_frame, textvariable=self.app_instance.scan_rbw_segmentation_var).grid(row=row_idx, column=1, sticky="ew", columnspan=2, padx=5, pady=2)
        # row_idx += 1
        # ttk.Label(settings_frame, text="Default Focus Width (Hz):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        # ttk.Entry(settings_frame, textvariable=self.app_instance.desired_default_focus_width_var).grid(row=row_idx, column=1, sticky="ew", columnspan=2, padx=5, pady=2)
        # row_idx += 1

        debug_log(f"ScanTab widgets created.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
    def _create_setting_row(self, parent, row, key, label_text, app_var, data_list, unit=""):
        """Generic function to create and store a labeled combobox row for a setting."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating setting row for {key}.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
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
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Combobox selected. Updating value and description.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
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
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Boolean combobox selected. Updating value.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        is_yes = event.widget.get() == "Yes"
        app_var.set(is_yes)
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)

    def _set_combobox_display_from_value(self, key):
        """Helper to find and set the display text and description for a given raw value."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Setting combobox display from value for {key}.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
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
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Loading settings into UI.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        for key in self.setting_widgets:
            if key in ['high_sensitivity', 'preamp_on']:
                widget_info = self.setting_widgets[key]
                widget_info['widget'].set("Yes" if widget_info['var'].get() else "No")
            else:
                self._set_combobox_display_from_value(key)

    def _browse_output_folder(self):
        # This function description tells me what this function does
        # Opens a file dialog for the user to select an output folder and saves
        # the selected path to the `output_folder_var` in the main application instance.
        #
        # Inputs to this function
        #   None.
        #
        # Outputs of this function
        #   None. Updates a Tkinter variable and saves the config.
        current_function = inspect.currentframe().f_code.co_name
        console_log("Browse for output folder...", self.console_print_func, function=current_function)
        debug_log(f"Opening file dialog to select output folder.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        folder = filedialog.askdirectory()
        if folder:
            self.app_instance.output_folder_var.set(folder)
            save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)

    def _open_output_folder(self):
        # This function description tells me what this function does
        # Opens the currently selected output folder using the default file explorer
        # for the operating system. It handles different OS commands and logs errors.
        #
        # Inputs to this function
        #   None.
        #
        # Outputs of this function
        #   None. Opens a file explorer window.
        current_function = inspect.currentframe().f_code.co_name
        path = self.app_instance.output_folder_var.get()
        debug_log(f"Attempting to open output folder: {path}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        if os.path.isdir(path):
            try:
                if sys.platform == "win32":
                    os.startfile(path)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", path])
                else:
                    subprocess.Popen(["xdg-open", path])
                console_log(f"✅ Opened output folder: {path}", self.console_print_func, function=current_function)
            except Exception as e:
                console_log(f"❌ Error opening folder: {e}", self.console_print_func, function=current_function)
        else:
            console_log(f"❌ Folder not found: {path}", self.console_print_func, function=current_function)

    def _on_tab_selected(self, event=None):
        """Called when the tab is selected, ensures UI is synced with config."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"ScanTab selected. Refreshing UI from config.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        self._load_settings_into_ui()
