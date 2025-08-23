# tabs/Scanning/tab_scanning_child_bands.py
#
# Stripped-down GUI for selecting frequency bands, with all interactions
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

class BandsTab(BaseGUIFrame):
    """
    A Tkinter Frame with GUI elements for selecting frequency bands.
    All controls publish to MQTT via the BaseGUIFrame's utility.
    """
    def __init__(self, master, mqtt_util, **kwargs):
        super().__init__(master, mqtt_util, console_log, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)
        self._create_widgets()

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        band_button_frame = ttk.Frame(self)
        band_button_frame.grid(row=0, column=0, pady=5, padx=10, sticky="ew")
        band_button_frame.grid_columnconfigure(0, weight=1)
        band_button_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Button(band_button_frame, text="Select All", command=lambda: self._publish_value("select_all_bands", "clicked")).grid(row=0, column=0, padx=5, sticky="ew")
        ttk.Button(band_button_frame, text="Deselect All", command=lambda: self._publish_value("deselect_all_bands", "clicked")).grid(row=0, column=1, padx=5, sticky="ew")

        bands_inner_frame = ttk.Frame(self)
        bands_inner_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        bands_inner_frame.grid_columnconfigure(0, weight=1)
        bands_inner_frame.grid_columnconfigure(1, weight=1)

        mock_bands = [
            {"name": "VHF Band", "start": 137.0, "stop": 144.0, "level": 1},
            {"name": "UHF Band", "start": 400.0, "stop": 420.0, "level": 2},
            {"name": "ISM Band", "start": 902.0, "stop": 928.0, "level": 3},
            {"name": "LTE Band", "start": 700.0, "stop": 800.0, "level": 0}
        ]
        
        for i, band in enumerate(mock_bands):
            button_text = f"{band['name']}\nStart: {band['start']:.3f} MHz\nStop: {band['stop']:.3f} MHz"
            
            # This is where the MQTT connection happens
            btn = ttk.Button(bands_inner_frame, text=button_text,
                             command=lambda b=band: self._publish_value("band_toggle", b["name"]))
            
            row, col = divmod(i, 2)
            btn.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
            
        table_frame = ttk.Frame(self)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        ttk.Label(table_frame, text="This is where the table would go.").grid(row=0, column=0, sticky="nsew")
        
        chart_frame = ttk.Frame(self)
        chart_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
        chart_frame.grid_columnconfigure(0, weight=1)
        chart_frame.grid_rowconfigure(0, weight=1)
        ttk.Label(chart_frame, text="This is where the chart would go.").grid(row=0, column=0, sticky="nsew")