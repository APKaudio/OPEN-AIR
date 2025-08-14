# tabs/Markers/tab_markers_child_zone_groups_devices.py
#
# This file defines the ZoneGroupsDevicesFrame, a reusable ttk.Frame that
# contains the UI for displaying Zones, Groups, and Devices.
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
# Version 20250814.161200.1

current_version = "20250814.161200.1"
current_version_hash = (20250814 * 161200 * 1)

import tkinter as tk
from tkinter import ttk

class ZoneGroupsDevicesFrame(ttk.Frame):
    def __init__(self, parent, app_instance):
        # [A brief, one-sentence description of the function's purpose.]
        # Initializes the frame containing Zones, Groups, and Devices UI.
        super().__init__(parent, style='TFrame')
        self.app_instance = app_instance
        self.grid(row=0, column=0, sticky="nsew")

        self._create_widgets()

    def _create_widgets(self):
        # [A brief, one-sentence description of the function's purpose.]
        # Creates and arranges the main layout frames.
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1) # Device frame should expand vertically

        # --- Create the main frames for each section ---
        self._create_zone_frame(self)
        self._create_group_frame(self)
        self._create_device_frame(self)

    def _create_zone_frame(self, parent):
        # [A brief, one-sentence description of the function's purpose.]
        # Creates the 'Zones' labelframe and populates it with placeholder buttons.
        zones_frame = ttk.LabelFrame(parent, text="Zones", style='TLabelframe')
        zones_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        zones_frame.columnconfigure(list(range(5)), weight=1) # 5 columns, equal weight

        # Placeholder buttons
        max_columns = 5
        for i in range(12):
            row = i // max_columns
            col = i % max_columns
            btn_text = f"Zone {i+1}\n(## Devices)"
            btn = ttk.Button(zones_frame, text=btn_text, style='ControlButton.Inactive.TButton')
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")

    def _create_group_frame(self, parent):
        # [A brief, one-sentence description of the function's purpose.]
        # Creates the 'Groups' labelframe and populates it with placeholder buttons.
        groups_frame = ttk.LabelFrame(parent, text="Groups", style='TLabelframe')
        groups_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        groups_frame.columnconfigure(list(range(5)), weight=1) # 5 columns, equal weight

        # Placeholder buttons
        max_columns = 5
        for i in range(7):
            row = i // max_columns
            col = i % max_columns
            btn_text = f"Group {i+1}\n(## Devices)"
            btn = ttk.Button(groups_frame, text=btn_text, style='ControlButton.Inactive.TButton')
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")

    def _create_device_frame(self, parent):
        # [A brief, one-sentence description of the function's purpose.]
        # Creates the 'Devices' labelframe with a scrollable area for device buttons.
        devices_frame = ttk.LabelFrame(parent, text="Devices", style='TLabelframe')
        devices_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        devices_frame.grid_rowconfigure(0, weight=1)
        devices_frame.grid_columnconfigure(0, weight=1)

        # Create a scrollable canvas
        canvas = tk.Canvas(devices_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(devices_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Dark.TFrame')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Placeholder device buttons
        for i in range(25):
            btn = ttk.Button(scrollable_frame, text=f"Placeholder Device {i+1}\n###.### MHz", style='DeviceButton.Inactive.TButton')
            btn.pack(fill='x', padx=5, pady=2)