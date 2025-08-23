# tabs/Scanning/tab_scanning_child_scan_configuration.py
#
# Stripped-down GUI for scan configuration, with all interactions
# connected to MQTT publishing.
#
# Author: Anthony Peter Kuzub
#
# Version 20250824.160000.1

import tkinter as tk
from tkinter import ttk
import pathlib
import os

from display.base_gui_component_rebuilt import BaseGUIFrame
from utils.mqtt_controller_util import MqttControllerUtility
from configuration.logging import console_log

class ScanTab(BaseGUIFrame):
    """
    A Tkinter Frame with GUI elements for configuring a scan.
    All controls publish to MQTT via the BaseGUIFrame's utility.
    """
    def __init__(self, master, mqtt_util, **kwargs):
        super().__init__(master, mqtt_util, console_log, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)
        self._create_widgets()

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # --- Output Settings ---
        output_frame = ttk.LabelFrame(self, text="Output Settings")
        output_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        output_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(output_frame, text="Scan Name:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        scan_name_var = tk.StringVar(self)
        scan_name_entry = ttk.Entry(output_frame, textvariable=scan_name_var)
        scan_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        scan_name_entry.bind("<KeyRelease>", lambda e: self._publish_value("scan_name", scan_name_var.get()))

        ttk.Label(output_frame, text="Output Folder:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        output_folder_var = tk.StringVar(self)
        ttk.Entry(output_frame, textvariable=output_folder_var, state="readonly").grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        ttk.Button(output_frame, text="Browse", command=lambda: self._publish_value("browse_folder_button", "clicked")).grid(row=1, column=2, padx=5, pady=2)
        ttk.Button(output_frame, text="Open Output Folder", command=lambda: self._publish_value("open_folder_button", "clicked")).grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        # --- Scan Settings ---
        settings_frame = ttk.LabelFrame(self, text="Scan Settings")
        settings_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        settings_frame.grid_columnconfigure(2, weight=1)

        row_idx = 0
        self._create_setting_row(settings_frame, row_idx, "graph_quality", "Graph Quality:", ["High", "Medium", "Low"], "graph_quality_combobox"); row_idx += 1
        self._create_setting_row(settings_frame, row_idx, "dwell_time", "DWELL (s):", ["0.1", "0.5", "1.0", "Custom"], "dwell_time_combobox"); row_idx += 1
        self._create_setting_row(settings_frame, row_idx, "max_hold_time", "Max Hold Time (s):", ["1", "5", "10", "Infinite"], "max_hold_time_combobox"); row_idx += 1
        self._create_setting_row(settings_frame, row_idx, "scan_rbw", "Scan RBW (Hz):", ["100", "300", "1k", "10k"], "scan_rbw_combobox"); row_idx += 1
        self._create_setting_row(settings_frame, row_idx, "reference_level", "Reference Level (dBm):", ["-10", "0", "10", "20"], "reference_level_combobox"); row_idx += 1
        self._create_setting_row(settings_frame, row_idx, "frequency_shift", "Frequency Shift (Hz):", ["0", "10k", "100k"], "frequency_shift_combobox"); row_idx += 1
        self._create_setting_row(settings_frame, row_idx, "num_scan_cycles", "Number of Scan Cycles:", ["1", "5", "10", "Infinite"], "num_scan_cycles_combobox"); row_idx += 1
        
        # Boolean settings
        ttk.Label(settings_frame, text="High Sensitivity:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w");
        hs_combo_var = tk.StringVar(self)
        hs_combo = ttk.Combobox(settings_frame, values=["Yes", "No"], state="readonly", textvariable=hs_combo_var)
        hs_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        hs_combo.bind("<<ComboboxSelected>>", lambda e: self._publish_value("high_sensitivity", hs_combo_var.get() == "Yes")); row_idx += 1
        
        ttk.Label(settings_frame, text="Preamplifier ON:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w");
        pa_combo_var = tk.StringVar(self)
        pa_combo = ttk.Combobox(settings_frame, values=["Yes", "No"], state="readonly", textvariable=pa_combo_var)
        pa_combo.grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        pa_combo.bind("<<ComboboxSelected>>", lambda e: self._publish_value("preamplifier_on", pa_combo_var.get() == "Yes")); row_idx += 1
        
        ttk.Label(settings_frame, text="Scan RBW Segmentation (Hz):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        scan_rbw_segmentation_var = tk.StringVar(self)
        scan_rbw_segmentation_entry = ttk.Entry(settings_frame, textvariable=scan_rbw_segmentation_var)
        scan_rbw_segmentation_entry.grid(row=row_idx, column=1, sticky="ew", columnspan=2, padx=5, pady=2)
        scan_rbw_segmentation_entry.bind("<KeyRelease>", lambda e: self._publish_value("scan_rbw_segmentation", scan_rbw_segmentation_var.get()))
        row_idx += 1
        
        ttk.Label(settings_frame, text="Default Focus Width (Hz):").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        default_focus_width_var = tk.StringVar(self)
        default_focus_width_entry = ttk.Entry(settings_frame, textvariable=default_focus_width_var)
        default_focus_width_entry.grid(row=row_idx, column=1, sticky="ew", columnspan=2, padx=5, pady=2)
        default_focus_width_entry.bind("<KeyRelease>", lambda e: self._publish_value("default_focus_width", default_focus_width_var.get()))
        row_idx += 1

    def _create_setting_row(self, parent, row, key, label_text, data_list, mqtt_topic_suffix):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, padx=5, pady=2, sticky="w")
        combo_var = tk.StringVar(self)
        combo = ttk.Combobox(parent, values=data_list, state="readonly", textvariable=combo_var)
        combo.grid(row=row, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(parent, text="").grid(row=row, column=2, padx=5, pady=2, sticky="w")
        combo.bind("<<ComboboxSelected>>", lambda e: self._publish_value(mqtt_topic_suffix, combo_var.get()))