# tabs/Markers/tab_markers_child_showtime.py
#
# This file defines the ShowtimeTab, a Tkinter Frame for displaying markers
# organized by Zone. It provides buttons to select a zone and then displays
# a row of buttons for each device within that selected zone.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
#
#
# Version 20250812.161300.1 (UPDATED: Modified button layout to support multiple rows for zones and ensure all buttons are visible.)

current_version = "20250812.161300.1"
current_version_hash = 20250812 * 161300 * 1

import tkinter as tk
from tkinter import ttk
import os
import csv
import inspect

from display.debug_logic import debug_log
from display.console_logic import console_log

class ShowtimeTab(ttk.Frame):
    """
    A Tkinter Frame for displaying markers organized by Zone and Device.
    """
    def __init__(self, master=None, app_instance=None, **kwargs):
        # Function Description:
        # Initializes the ShowtimeTab, setting up the UI frame and internal state.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing ShowtimeTab...",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.markers_data = []
        self.zones = {}
        self.selected_zone = None
        
        self.zone_buttons = {}
        self.device_buttons = {}

        self._create_widgets()
        self.after(100, self._on_tab_selected) # Defer initial load to after GUI is drawn

    def _create_widgets(self):
        # Function Description:
        # Creates and arranges the widgets for the Showtime tab.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating ShowtimeTab widgets.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Zone buttons row
        self.grid_rowconfigure(1, weight=1) # Device buttons frame
        self.grid_rowconfigure(2, weight=0) # Get Show Details button

        # --- Zone Buttons Frame ---
        self.zone_buttons_frame = ttk.LabelFrame(self, text="Zones", padding=5, style='Dark.TLabelframe')
        self.zone_buttons_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.zone_buttons_frame.grid_columnconfigure(0, weight=1)

        self.zone_button_subframe = ttk.Frame(self.zone_buttons_frame, style='Dark.TFrame')
        self.zone_button_subframe.pack(fill="x", expand=False)
        
        # Make the subframe expandable in a grid layout
        self.zone_button_subframe.grid_columnconfigure(0, weight=1)
        self.zone_button_subframe.grid_columnconfigure(1, weight=1)
        self.zone_button_subframe.grid_columnconfigure(2, weight=1)
        self.zone_button_subframe.grid_columnconfigure(3, weight=1)
        self.zone_button_subframe.grid_columnconfigure(4, weight=1)
        self.zone_button_subframe.grid_columnconfigure(5, weight=1)
        self.zone_button_subframe.grid_columnconfigure(6, weight=1)
        self.zone_button_subframe.grid_columnconfigure(7, weight=1)
        self.zone_button_subframe.grid_columnconfigure(8, weight=1)
        self.zone_button_subframe.grid_columnconfigure(9, weight=1)


        # --- Device Buttons Frame ---
        self.device_buttons_frame = ttk.LabelFrame(self, text="Devices", padding=5, style='Dark.TLabelframe')
        self.device_buttons_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.device_buttons_frame.grid_columnconfigure(0, weight=1)
        self.device_buttons_frame.grid_rowconfigure(0, weight=1)

        self.device_button_subframe = ttk.Frame(self.device_buttons_frame, style='Dark.TFrame')
        self.device_button_subframe.pack(fill="both", expand=True)

        # --- Get Show Details Button ---
        self.get_details_button = ttk.Button(self, text="Get Show Details (Placeholder)", command=self._on_get_show_details, style='Blue.TButton')
        self.get_details_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    def _load_markers_data(self):
        # Function Description:
        # Loads marker data from the internal MARKERS.CSV file.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Loading markers from the CSV file. 🤠",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
        self.markers_data = []
        self.zones = {}
        
        if self.app_instance and hasattr(self.app_instance, 'MARKERS_FILE_PATH'):
            path = self.app_instance.MARKERS_FILE_PATH
            if os.path.exists(path):
                try:
                    with open(path, mode='r', newline='', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        self.markers_data = list(reader)
                        self.zones = self._group_by_zone(self.markers_data)
                    console_log(f"✅ Loaded {len(self.markers_data)} markers from MARKERS.CSV.")
                except Exception as e:
                    console_log(f"❌ Error loading MARKERS.CSV: {e}")
                    debug_log(f"A file loading calamity! The MARKERS.CSV file couldn't be loaded. Error: {e}",
                              file=f"{os.path.basename(__file__)} - {current_version}",
                              version=current_version,
                              function=current_function, special=True)
            else:
                console_log("ℹ️ MARKERS.CSV not found. Please create one.")

    def _group_by_zone(self, data):
        # Function Description:
        # Groups marker data by zone.
        zones = {}
        for row in data:
            zone = row.get('ZONE', 'Uncategorized').strip()
            if zone not in zones:
                zones[zone] = []
            zones[zone].append(row)
        return zones

    def _populate_zone_buttons(self):
        # Function Description:
        # Creates buttons for each zone, arranged in a grid with a maximum of 10 columns.
        for widget in self.zone_button_subframe.winfo_children():
            widget.destroy()

        if not self.zones:
            ttk.Label(self.zone_button_subframe, text="No zones found in MARKERS.CSV.").pack()
            return
            
        max_cols = 10
        for i, zone_name in enumerate(sorted(self.zones.keys())):
            row = i // max_cols
            col = i % max_cols
            
            btn = ttk.Button(self.zone_button_subframe, 
                             text=f"{zone_name} ({len(self.zones[zone_name])})",
                             command=lambda z=zone_name: self._on_zone_button_click(z),
                             style='Orange.TButton')
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            self.zone_buttons[zone_name] = btn
            
    def _on_zone_button_click(self, zone_name):
        # Function Description:
        # Handles a click on a zone button.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Zone button '{zone_name}' clicked.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
        self.selected_zone = zone_name
        self._update_zone_button_styles()
        self._populate_device_buttons()
        
    def _update_zone_button_styles(self):
        # Function Description:
        # Updates the styles of the zone buttons to show which is active.
        for zone_name, btn in self.zone_buttons.items():
            if zone_name == self.selected_zone:
                btn.config(style='SelectedPreset.Orange.TButton')
            else:
                btn.config(style='Orange.TButton')

    def _populate_device_buttons(self):
        # Function Description:
        # Creates buttons for each device in the selected zone.
        for widget in self.device_button_subframe.winfo_children():
            widget.destroy()

        if not self.selected_zone or self.selected_zone not in self.zones:
            ttk.Label(self.device_button_subframe, text="Select a zone to view devices.").pack(pady=10)
            return

        devices = self.zones[self.selected_zone]
        
        # Use a scrollable area if needed, or just pack them
        for device in devices:
            text = f"{device.get('NAME', 'N/A')}\n{device.get('DEVICE', 'N/A')}\n{device.get('FREQ', 'N/A')} MHz"
            btn = ttk.Button(self.device_button_subframe, text=text, style='LocalPreset.TButton',
                             command=lambda d=device: self._on_device_button_click(d))
            btn.pack(side="left", padx=5, pady=5)

    def _on_device_button_click(self, device_data):
        # Function Description:
        # Handles a click on a device button.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Device button clicked: {device_data.get('NAME', 'N/A')}",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        console_log(f"Device '{device_data.get('NAME', 'N/A')}' selected in Zone '{self.selected_zone}'.")
        # Placeholder for future functionality
        pass

    def _on_get_show_details(self):
        # Function Description:
        # Placeholder for future functionality to retrieve show details.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Get Show Details button clicked. Placeholder function executed.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        console_log("Get Show Details button pressed. This feature is not yet implemented.")

    def _on_tab_selected(self, event=None):
        # Function Description:
        # Handles the tab selection event.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"The Showtime tab has been selected. Loading markers from the file.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        self._load_markers_data()
        self._populate_zone_buttons()
        # Clear device buttons on first load
        self._populate_device_buttons()
