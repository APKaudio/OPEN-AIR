# tabs/Presets/tab_presets_child_preset_editor.py
#
# Stripped-down GUI for managing presets, with all interactions
# connected to MQTT publishing.
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

class PresetEditorTab(tk.Frame):
    """
    A Tkinter Frame that provides comprehensive functionality for managing
    user-defined presets. All controls publish to MQTT via the BaseGUIFrame's utility.
    """
    def __init__(self, master, mqtt_util, **kwargs):
        super().__init__(master, mqtt_util, console_log, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)
        self.columns = ['Filename', 'NickName'] # Simplified columns for this example
        self._create_widgets()

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0)

        top_button_frame = ttk.Frame(self)
        top_button_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        top_button_frame.grid_columnconfigure(0, weight=1)
        top_button_frame.grid_columnconfigure(1, weight=1)
        top_button_frame.grid_columnconfigure(2, weight=1)

        add_current_button = ttk.Button(top_button_frame, text="Add Current Settings", command=lambda: self._publish_value("add_current_settings", "clicked"))
        add_current_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        add_empty_row_button = ttk.Button(top_button_frame, text="Add New Empty Row", command=lambda: self._publish_value("add_empty_row", "clicked"))
        add_empty_row_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        delete_button = ttk.Button(top_button_frame, text="Delete Selected", command=lambda: self._publish_value("delete_selected", "clicked"))
        delete_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        move_button_frame = ttk.Frame(self)
        move_button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        move_button_frame.grid_columnconfigure(0, weight=1)
        move_button_frame.grid_columnconfigure(1, weight=1)

        move_up_button = ttk.Button(move_button_frame, text="Move Preset UP", command=lambda: self._publish_value("move_up", "clicked"))
        move_up_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        move_down_button = ttk.Button(move_button_frame, text="Move Preset DOWN", command=lambda: self._publish_value("move_down", "clicked"))
        move_down_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        presets_tree = ttk.Treeview(self, columns=self.columns, show='headings')
        presets_tree.heading("Filename", text="Filename")
        presets_tree.heading("NickName", text="NickName")
        presets_tree.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        vsb = ttk.Scrollbar(self, orient="vertical", command=presets_tree.yview)
        vsb.grid(row=2, column=1, sticky='ns')
        presets_tree.configure(yscrollcommand=vsb.set)
        
        # Mock double-click event to publish the selected item's filename
        def on_double_click(event):
            item_id = presets_tree.identify_row(event.y)
            if item_id:
                filename = presets_tree.item(item_id, 'values')[0]
                self._publish_value("double_click", filename)
        presets_tree.bind("<Double-1>", on_double_click)

        file_ops_button_frame = ttk.Frame(self)
        file_ops_button_frame.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        file_ops_button_frame.grid_columnconfigure(0, weight=1)
        file_ops_button_frame.grid_columnconfigure(1, weight=1)

        import_button = ttk.Button(file_ops_button_frame, text="Import Presets", command=lambda: self._publish_value("import_presets", "clicked"))
        import_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        export_button = ttk.Button(file_ops_button_frame, text="Export Presets", command=lambda: self._publish_value("export_presets", "clicked"))
        export_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")