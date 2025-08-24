# tabs/Presets/tab_presets_child_local.py
#
# Stripped-down GUI for displaying and loading local presets, with all
# interactions connected to MQTT publishing.
#
# Author: Anthony Peter Kuzub
#
# Version 20250824.160000.1

import tkinter as tk
from tkinter import ttk
import pathlib
import os

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from display.styling.style import THEMES, DEFAULT_THEME
from workers.mqtt_controller_util import MqttControllerUtility

class LocalPresetsTab(tk.Frame):
    """
    A Tkinter Frame for displaying and loading user-defined local presets.
    All controls publish to MQTT via the BaseGUIFrame's utility.
    """
    def __init__(self, master, mqtt_util, **kwargs):
        super().__init__(master, mqtt_util, console_log, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)
        self._create_widgets()

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        max_cols = 5
        for i in range(max_cols):
            scrollable_frame.grid_columnconfigure(i, weight=1)

        mock_presets = [
            {'NickName': 'Preset A', 'Start': '100.0', 'Stop': '200.0'},
            {'NickName': 'Preset B', 'Start': '300.0', 'Stop': '400.0'},
            {'NickName': 'Preset C', 'Start': '500.0', 'Stop': '600.0'}
        ]
        
        row_idx = 0
        col_idx = 0
        
        for preset in mock_presets:
            button_text = f"{preset['NickName']}\nStart: {preset['Start']} MHz\nStop: {preset['Stop']} MHz"
            preset_button = ttk.Button(scrollable_frame,
                                       text=button_text,
                                       command=lambda name=preset['NickName']: self._publish_value("load_preset", name))
            
            preset_button.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="nsew")

            col_idx += 1
            if col_idx >= max_cols:
                col_idx = 0
                row_idx += 1
        
        selected_preset_box = ttk.LabelFrame(self, text="Selected Preset Details")
        selected_preset_box.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        ttk.Label(selected_preset_box, text="Details will be displayed here.").pack(padx=5, pady=5)