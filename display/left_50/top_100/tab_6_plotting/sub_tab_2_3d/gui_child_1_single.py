# tabs/Plotting/tab_plotting_child_3D.py
#
# Stripped-down GUI for generating 3D plots, with all interactions
# connected to MQTT publishing.
#
# Author: Anthony Peter Kuzub
#
# Version 20251127.000000.1

import tkinter as tk
from tkinter import ttk
import pathlib
import os

from workers.active.worker_active_logging import console_log
from display.styling.style import THEMES, DEFAULT_THEME
from workers.mqtt.worker_mqtt_controller_util import MqttControllerUtility

class Plotting3DTab(ttk.Frame):
    def __init__(self, master, mqtt_util, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)

        self.mqtt_util = mqtt_util
        self.current_topic_prefix = self._get_topic_prefix()

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

        self.plot_3d_frame = ttk.LabelFrame(self, text="3D Scans Over Time Plotting", padding="10")
        self.plot_3d_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.open_folder_3d_button = ttk.Button(self.plot_3d_frame, text="Open Folder for 3D Plotting", command=lambda: self._publish_value("open_folder_for_3d_plotting", "clicked"))
        self.open_folder_3d_button.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.discovered_series_3d_frame = ttk.LabelFrame(self.plot_3d_frame, text="Discovered Series of Scans (for 3D)", padding="10")
        self.discovered_series_3d_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.dynamic_3d_buttons_frame = ttk.Frame(self.discovered_series_3d_frame)
        self.dynamic_3d_buttons_frame.pack(fill="both", expand=True)

        ttk.Button(self.dynamic_3d_buttons_frame, text="Group 'Mock_Group_A' (5 files)", command=lambda: self._publish_value("group_select", "Mock_Group_A")).grid(row=0, column=0, padx=5, pady=2, sticky="ew")
        ttk.Button(self.dynamic_3d_buttons_frame, text="Group 'Mock_Group_B' (3 files)", command=lambda: self._publish_value("group_select", "Mock_Group_B")).grid(row=1, column=0, padx=5, pady=2, sticky="ew")

        amplitude_threshold_frame = ttk.Frame(self.plot_3d_frame)
        amplitude_threshold_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        amplitude_threshold_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(amplitude_threshold_frame, text="Amplitude Threshold (dBm):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        amplitude_threshold_var = tk.DoubleVar(self, value=-80.0)
        amplitude_threshold_entry = ttk.Entry(amplitude_threshold_frame, textvariable=amplitude_threshold_var)
        amplitude_threshold_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        amplitude_threshold_entry.bind("<KeyRelease>", lambda e: self._publish_value("amplitude_threshold", amplitude_threshold_var.get()))

        self.generate_plot_scans_over_time_button = ttk.Button(self.plot_3d_frame, text="Generate 3D Plot of Scans Over Time", command=lambda: self._publish_value("generate_3d_plot", "clicked"))
        self.generate_plot_scans_over_time_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.generate_plot_scans_over_time_button.config(state=tk.DISABLED)

    def _publish_value(self, element_name, value):
        if self.mqtt_util:
            self.mqtt_util.publish_message(
                topic=self.current_topic_prefix,
                subtopic=element_name,
                value=value
            )