# tabs/Plotting/tab_plotting_child_Single.py
#
# Stripped-down GUI for plotting single scans, with all interactions
# connected to MQTT publishing.
#
# Author: Anthony Peter Kuzub
#
# Version 20250824.180000.1

import tkinter as tk
from tkinter import ttk
import pathlib
import os

from configuration.logging import console_log
from display.styling.style import THEMES, DEFAULT_THEME
from utils.mqtt_controller_util import MqttControllerUtility

class PlottingTab(ttk.Frame):
    def __init__(self, master, mqtt_util, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)

        self.mqtt_util = mqtt_util
        self.current_topic_prefix = self._get_topic_prefix()

        self.open_html_after_complete_var = tk.BooleanVar(self, value=False)
        self.create_html_report_var = tk.BooleanVar(self, value=True)
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

        plotting_options_frame = ttk.LabelFrame(self, text="SCAN Plotting Options", padding="10")
        plotting_options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        scan_options_inner_frame = ttk.Frame(plotting_options_frame)
        scan_options_inner_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew", columnspan=2)
        scan_options_inner_frame.grid_columnconfigure(0, weight=1)
        scan_options_inner_frame.grid_columnconfigure(1, weight=1)

        html_output_options_frame = ttk.LabelFrame(scan_options_inner_frame, text="HTML Output Options", padding="10")
        html_output_options_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        html_output_options_frame.grid_columnconfigure(0, weight=1)

        ttk.Checkbutton(html_output_options_frame, text="Plot the HTML after every scan", variable=self.open_html_after_complete_var, command=lambda: self._publish_value("open_html_after_complete", self.open_html_after_complete_var.get())).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(html_output_options_frame, text="Create HTML", variable=self.create_html_report_var, command=lambda: self._publish_value("create_html_report", self.create_html_report_var.get())).grid(row=1, column=0, padx=5, pady=2, sticky="w")

        scan_markers_to_plot_frame = ttk.LabelFrame(scan_options_inner_frame, text="Scan Markers to Plot", padding="10")
        scan_markers_to_plot_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        scan_markers_to_plot_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Checkbutton(scan_markers_to_plot_frame, text="Include TV Band Markers", variable=self.include_tv_markers_var, command=lambda: self._publish_value("include_tv_markers", self.include_tv_markers_var.get())).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(scan_markers_to_plot_frame, text="Include Government Band Markers", variable=self.include_gov_markers_var, command=lambda: self._publish_value("include_gov_markers", self.include_gov_markers_var.get())).grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(scan_markers_to_plot_frame, text="Include Markers", variable=self.include_markers_var, command=lambda: self._publish_value("include_markers", self.include_markers_var.get())).grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(scan_markers_to_plot_frame, text="Include Intermodulations", variable=self.include_scan_intermod_markers_var, command=lambda: self._publish_value("include_scan_intermod_markers", self.include_scan_intermod_markers_var.get())).grid(row=3, column=0, padx=5, pady=2, sticky="w")

        self.plot_button = ttk.Button(plotting_options_frame, text="Plot Single Scan", command=lambda: self._publish_value("plot_single_scan", "clicked"))
        self.plot_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.plot_average_button = ttk.Button(plotting_options_frame, text="Plot Current Cycle Average (All Traces)", command=lambda: self._publish_value("plot_current_cycle_average", "clicked"))
        self.plot_average_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.plot_average_button.config(state=tk.DISABLED)

        self.open_last_plot_button = ttk.Button(plotting_options_frame, text="Open Last Plot", command=lambda: self._publish_value("open_last_plot", "clicked"))
        self.open_last_plot_button.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        
    def _publish_value(self, element_name, value):
        if self.mqtt_util:
            self.mqtt_util.publish_message(
                topic=self.current_topic_prefix,
                subtopic=element_name,
                value=value
            )