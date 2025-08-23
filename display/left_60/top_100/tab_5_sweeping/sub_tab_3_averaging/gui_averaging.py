# tabs/Plotting/tab_plotting_child_average.py
#
# Stripped-down GUI for plotting averaged scan data, with all interactions
# connected to MQTT publishing.
#
# Author: Anthony Peter Kuzub
#
# Version 20250824.180000.1

import tkinter as tk
from tkinter import ttk
import pathlib
import os

from datasets.logging import console_log
from display.styling.style import THEMES, DEFAULT_THEME
from workers.mqtt_controller_util import MqttControllerUtility

class AveragingTab(ttk.Frame):
    def __init__(self, master, mqtt_util, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)

        self.mqtt_util = mqtt_util
        self.current_topic_prefix = self._get_topic_prefix()

        self.last_opened_folder = None
        self.grouped_csv_files = {}
        self.selected_group_prefix = None

        self.math_average_var = tk.BooleanVar(self, value=False)
        self.math_median_var = tk.BooleanVar(self, value=False)
        self.math_range_var = tk.BooleanVar(self, value=False)
        self.math_standard_deviation_var = tk.BooleanVar(self, value=False)
        self.math_variance_var = tk.BooleanVar(self, value=False)
        self.math_psd_var = tk.BooleanVar(self, value=False)

        self.include_tv_markers_var = tk.BooleanVar(self, value=False)
        self.include_gov_markers_var = tk.BooleanVar(self, value=False)
        self.include_markers_var = tk.BooleanVar(self, value=False)
        self.include_scan_intermod_markers_var = tk.BooleanVar(self, value=False)

        self._apply_styles(theme_name=DEFAULT_THEME)
        self._create_widgets()
        
    def _get_topic_prefix(self):
        relative_path = pathlib.Path(__file__).resolve().relative_to(pathlib.Path(__file__).resolve().parent.parent.parent)
        topic = str(relative_path).replace(os.sep, '/')
        return os.path.splitext(topic)[0]

    def _apply_styles(self, theme_name: str):
        colors = THEMES.get(theme_name, THEMES["dark"])
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure('TFrame', background=colors["bg"])
        style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
        style.configure('TButton', background=colors["secondary"], foreground=colors["fg"])
        style.configure('TCombobox', fieldbackground=colors["entry_bg"], foreground=colors["entry_fg"])
        style.configure('TCheckbutton', background=colors["bg"], foreground=colors["fg"])
        style.configure('TLabelframe', background=colors["bg"], foreground=colors["fg"])
        style.configure('TLabelFrame.Label', background=colors["bg"], foreground=colors["fg"])
        
    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)

        self.averaging_folder_frame = ttk.LabelFrame(self, text="Plotting Averages from Folder", padding="10")
        self.averaging_folder_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.open_folder_button = ttk.Button(self.averaging_folder_frame, text="Open Folder to Average", command=lambda: self._publish_value("open_folder_to_average", "clicked"))
        self.open_folder_button.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.discovered_series_frame = ttk.LabelFrame(self.averaging_folder_frame, text="Discovered Series of Scans", padding="10")
        self.discovered_series_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.dynamic_avg_buttons_frame = ttk.Frame(self.discovered_series_frame)
        self.dynamic_avg_buttons_frame.pack(fill="both", expand=True)

        math_and_markers_frame = ttk.Frame(self.averaging_folder_frame)
        math_and_markers_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        math_and_markers_frame.grid_columnconfigure(0, weight=1)
        math_and_markers_frame.grid_columnconfigure(1, weight=1)

        apply_math_frame = ttk.LabelFrame(math_and_markers_frame, text="Apply Math", padding="10")
        apply_math_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        apply_math_frame.grid_columnconfigure(0, weight=1)

        math_types = ["Average", "Median", "Range", "Standard Deviation", "Variance", "Power Spectral Density (PSD)"]
        vars = [self.math_average_var, self.math_median_var, self.math_range_var, self.math_standard_deviation_var, self.math_variance_var, self.math_psd_var]
        for i, text in enumerate(math_types):
            chk = ttk.Checkbutton(apply_math_frame, text=text, variable=vars[i], command=lambda t=text, v=vars[i]: self._publish_value(f"math_{t.lower().replace(' ', '_')}", v.get()))
            chk.grid(row=i, column=0, padx=5, pady=2, sticky="w")

        markers_to_plot_frame = ttk.LabelFrame(math_and_markers_frame, text="Markers to Plot", padding="10")
        markers_to_plot_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        markers_to_plot_frame.grid_columnconfigure(0, weight=1)
        
        marker_types = ["Include TV Band Markers", "Include Government Band Markers", "Include Markers", "Include Intermodulations"]
        vars = [self.include_tv_markers_var, self.include_gov_markers_var, self.include_markers_var, self.include_scan_intermod_markers_var]
        for i, text in enumerate(marker_types):
            chk = ttk.Checkbutton(markers_to_plot_frame, text=text, variable=vars[i], command=lambda t=text, v=vars[i]: self._publish_value(f"marker_{t.lower().replace(' ', '_')}", v.get()))
            chk.grid(row=i, column=0, padx=5, pady=2, sticky="w")

        make_averages_frame = ttk.LabelFrame(self.averaging_folder_frame, text="Make Averages", padding="10")
        make_averages_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        make_averages_frame.grid_columnconfigure(0, weight=1)

        self.generate_csv_button = ttk.Button(make_averages_frame, text="Generate CSV of Selected Series of Scan", command=lambda: self._publish_value("generate_csv_button", "clicked"))
        self.generate_csv_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.generate_csv_button.config(state=tk.DISABLED)

        self.open_applied_math_folder_button = ttk.Button(make_averages_frame, text="Open Folder of Applied Math", command=lambda: self._publish_value("open_applied_math_folder", "clicked"))
        self.open_applied_math_folder_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.open_applied_math_folder_button.config(state=tk.DISABLED)

        self.generate_plot_averages_button = ttk.Button(make_averages_frame, text="Generate Plot of Averages", command=lambda: self._publish_value("generate_plot_averages", "clicked"))
        self.generate_plot_averages_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.generate_plot_averages_button.config(state=tk.DISABLED)

        self.generate_plot_averages_with_scan_button = ttk.Button(make_averages_frame, text="Generate Plot of Averages with Scan", command=lambda: self._publish_value("generate_plot_averages_with_scan", "clicked"))
        self.generate_plot_averages_with_scan_button.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        self.generate_plot_averages_with_scan_button.config(state=tk.DISABLED)
        
    def _publish_value(self, element_name, value):
        if self.mqtt_util:
            self.mqtt_util.publish_message(
                topic=self.current_topic_prefix,
                subtopic=element_name,
                value=value
            )