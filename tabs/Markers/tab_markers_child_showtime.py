# tabs/Markers/tab_markers_child_showtime.py
#
# This file defines the ShowtimeTab, a Tkinter Frame for displaying markers
# organized by a new Zone/Group hierarchy. It provides buttons to select a zone,
# then dynamically populated buttons for the groups within that zone. Clicking
# a group button filters the device list. The "Get Show Details" button is now
# triggered automatically on a zone or group selection, querying peak values from the
# instrument and updating the color-coded device buttons to reflect the measured signal strength.
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
# Version 20250815.200000.2 (FIXED: The `_perform_peak_search_task` function now correctly handles single-frequency groups by enforcing a minimum span of 100 kHz to prevent plotting errors.)

current_version = "20250815.200000.2"
current_version_hash = 20250815 * 200000 * 2

import tkinter as tk
from tkinter import ttk
import os
import csv
import inspect
import pandas as pd
import threading
import time
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log
from display.utils_display_monitor import update_top_plot, update_medium_plot, update_bottom_plot

# Import the utility functions for markers
from tabs.Markers.utils_marker_peaks import get_peak_values_and_update_csv
from tabs.Markers.utils_markers_get_traces import get_marker_traces
from tabs.Markers.utils_markers import (
    SPAN_OPTIONS,
    RBW_OPTIONS,
    set_span_logic,
    set_frequency_logic,
    set_trace_modes_logic,
    set_marker_logic,
    set_rbw_logic
)
from src.program_style import COLOR_PALETTE
from src.settings_and_config.config_manager import save_config
from ref.frequency_bands import MHZ_TO_HZ


class ThresholdsTab(ttk.Frame):
    """
    A placeholder tab for future threshold settings.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        # Function Description:
        # Initializes the ThresholdsTab.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing ThresholdsTab. A blank canvas for future brilliance! 🎨",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        super().__init__(master, **kwargs)
        ttk.Label(self, text="Thresholds settings coming soon...").pack(padx=10, pady=10)

    def _on_tab_selected(self, event=None):
        """
        Handles the tab selection event for the ThresholdsTab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"The Thresholds tab has been selected. It is currently a blank slate.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)


class ShowtimeTab(ttk.Frame):
    """
    A Tkinter Frame for displaying markers organized by Zone and Device.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        # Function Description:
        # Initializes the ShowtimeTab, setting up the UI frame and internal state.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing ShowtimeTab...",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func
        self.markers_data = pd.DataFrame()
        self.zones = {}
        self.selected_zone = None
        self.selected_group = None
        
        self.zone_buttons = {}
        self.group_buttons = {}
        self.device_buttons = {} # NEW: A dictionary to hold device buttons
        
        # Marker and trace loop variables
        self.selected_device_name = None
        self.selected_device_freq = None
        self.marker_trace_loop_job = None
        self.is_loop_running = False
        
        # New state variables for loop and blinking
        self.blinking_button_job = None
        self.currently_blinking_button = None
        self.loop_run_count = 0
        self.loop_limit = 10
        
        # State Variables for Controls (from MarkersDisplayTab)
        self.span_var = tk.StringVar(value="1000000.0") # Default to 1 MHz span
        self.rbw_var = tk.StringVar(value="30000.0")   # Default to 30 kHz RBW
        self.trace_live_mode = tk.BooleanVar(value=True)
        self.trace_max_hold_mode = tk.BooleanVar(value=True)
        self.trace_min_hold_mode = tk.BooleanVar(value=False)
        self.loop_delay_var = tk.StringVar(value="500")
        self.loop_counter_var = tk.IntVar(value=0)
        
        # Dictionaries to hold control buttons for styling
        self.span_buttons = {}
        self.rbw_buttons = {}
        self.trace_buttons = {}
        self.loop_stop_button = None

        self._create_widgets()
        self.after(100, self._on_tab_selected)

    def _create_widgets(self):
        # Function Description:
        # Creates and arranges the widgets for the Showtime tab.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating ShowtimeTab widgets.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)

        # --- Zone Buttons Frame ---
        self.zone_buttons_frame = ttk.LabelFrame(self, text="Zones", padding=5, style='Dark.TLabelframe')
        self.zone_buttons_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.zone_buttons_frame.grid_columnconfigure(0, weight=1)

        self.zone_button_subframe = ttk.Frame(self.zone_buttons_frame, style='Dark.TFrame')
        self.zone_button_subframe.pack(fill="x", expand=False)
        
        # Changed max columns to 8 from 10
        for i in range(8):
            self.zone_button_subframe.grid_columnconfigure(i, weight=1)

        # --- Group Buttons Frame ---
        self.group_buttons_frame = ttk.LabelFrame(self, text="Groups", padding=5, style='Dark.TLabelframe')
        self.group_buttons_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.group_buttons_frame.grid_columnconfigure(0, weight=1)

        self.group_button_subframe = ttk.Frame(self.group_buttons_frame, style='Dark.TFrame')
        self.group_button_subframe.pack(fill="x", expand=False)
        
        # Changed max columns to 8 from 10
        for i in range(8):
            self.group_button_subframe.grid_columnconfigure(i, weight=1)

        # --- Device Button Scrollable Frame ---
        self.device_scrollable_frame = ttk.LabelFrame(self, text="Devices", padding=5, style='Dark.TLabelframe')
        self.device_scrollable_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        self.device_scrollable_frame.grid_columnconfigure(0, weight=1)
        self.device_scrollable_frame.grid_rowconfigure(0, weight=1)

        canvas = tk.Canvas(self.device_scrollable_frame, bg='#2b2b2b', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.device_scrollable_frame, orient="vertical", command=canvas.yview)
        self.device_buttons_frame = ttk.Frame(canvas, style='Dark.TFrame')

        canvas.create_window((0, 0), window=self.device_buttons_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.device_buttons_frame.grid_columnconfigure(0, weight=1)
        self.device_buttons_frame.grid_columnconfigure(1, weight=1)


        # --- Controls Notebook (New) ---
        self.controls_notebook = ttk.Notebook(self, style='Markers.Child.TNotebook')
        self.controls_notebook.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        # --- NEW: Thresholds tab ---
        self.thresholds_tab = ThresholdsTab(self.controls_notebook, self.app_instance, self.console_print_func)
        self.controls_notebook.add(self.thresholds_tab, text="Thresholds")

        # --- Span Tab ---
        span_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(span_tab, text="Span")
        for i, (name, span_hz) in enumerate(SPAN_OPTIONS.items()):
            val_text = f"{float(span_hz) / 1e6:.1f} MHz" if float(span_hz) >= 1e6 else f"{float(span_hz) / 1e3:.0f} kHz"
            btn_text = f"{name}\n{val_text}"
            btn = ttk.Button(span_tab, text=btn_text, command=lambda s=span_hz: self._on_span_button_click(s))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.span_buttons[str(span_hz)] = btn
            span_tab.grid_columnconfigure(i, weight=1)

        # --- RBW Tab ---
        rbw_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(rbw_tab, text="RBW")
        for i, (name, rbw_hz) in enumerate(RBW_OPTIONS.items()):
            val_text = f"{float(rbw_hz) / 1e3:.0f} kHz"
            btn_text = f"{name}\n{val_text}"
            btn = ttk.Button(rbw_tab, text=btn_text, command=lambda r=rbw_hz: self._on_rbw_button_click(r))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.rbw_buttons[str(rbw_hz)] = btn
            rbw_tab.grid_columnconfigure(i, weight=1)

        # --- Trace Tab ---
        trace_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(trace_tab, text="Trace")
        trace_modes = [("Live", self.trace_live_mode), ("Max Hold", self.trace_max_hold_mode), ("Min Hold", self.trace_min_hold_mode)]
        for i, (name, var) in enumerate(trace_modes):
            btn = ttk.Button(trace_tab, text=name, command=lambda v=var: self._on_trace_button_click(v))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.trace_buttons[name] = btn
            trace_tab.grid_columnconfigure(i, weight=1)

        # --- Loop Tab ---
        loop_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(loop_tab, text="Loop")
        loop_tab.grid_columnconfigure(0, weight=1)
        loop_tab.grid_columnconfigure(1, weight=1)
        
        ttk.Label(loop_tab, text="Delay (ms):").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        delay_options = [500, 1000, 1500, 2000]
        delay_combobox = ttk.Combobox(loop_tab, textvariable=self.loop_delay_var, values=delay_options, state="readonly")
        delay_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(loop_tab, text="Loop Count:").grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ttk.Label(loop_tab, textvariable=self.loop_counter_var).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.loop_stop_button = ttk.Button(loop_tab, text="Stop Loop", command=self._stop_loop_action, state=tk.DISABLED)
        self.loop_stop_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew", columnspan=2)
        
        self.controls_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)

    def _load_markers_data(self):
        # Function Description:
        # Loads marker data from the internal MARKERS.CSV file.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Loading markers from the CSV file. 🤠",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
        self.markers_data = pd.DataFrame()
        self.zones = {}
        
        if self.app_instance and hasattr(self.app_instance, 'MARKERS_FILE_PATH'):
            path = self.app_instance.MARKERS_FILE_PATH
            if os.path.exists(path):
                try:
                    self.markers_data = pd.read_csv(path)
                    self.zones = self._group_by_zone_and_group(self.markers_data)
                    self.console_print_func(f"✅ Loaded {len(self.markers_data)} markers from MARKERS.CSV.")
                except Exception as e:
                    self.console_print_func(f"❌ Error loading MARKERS.CSV: {e}")
                    debug_log(f"A file loading calamity! The MARKERS.CSV file couldn't be loaded. Error: {e}",
                              file=f"{os.path.basename(__file__)} - {current_version}",
                              version=current_version,
                              function=current_function, special=True)
            else:
                self.console_print_func("ℹ️ MARKERS.CSV not found. Please create one.")

    def _group_by_zone_and_group(self, data):
        # Function Description:
        # Groups marker data by zone and then by group.
        if data.empty:
            return {}
        
        data['GROUP'] = data['GROUP'].fillna('No Group')
        
        zones = {}
        for zone, zone_data in data.groupby('ZONE'):
            groups = {group: group_data.to_dict('records') for group, group_data in zone_data.groupby('GROUP')}
            zones[zone] = groups
        return zones

    def _populate_zone_buttons(self):
        # Function Description:
        # Creates buttons for each zone, arranged in a grid with a maximum of 8 columns.
        for widget in self.zone_button_subframe.winfo_children():
            widget.destroy()

        self.zone_buttons = {} # Clear the dictionary
        
        if not isinstance(self.zones, dict) or not self.zones:
            ttk.Label(self.zone_button_subframe, text="No zones found in MARKERS.CSV.").grid(row=0, column=0, columnspan=8)
            return
            
        max_cols = 8 # Changed max columns to 8 from 10
        for i, zone_name in enumerate(sorted(self.zones.keys())):
            row = i // max_cols
            col = i % max_cols
            
            # Count the total number of devices in the zone
            device_count = sum(len(group) for group in self.zones[zone_name].values())
            
            btn = ttk.Button(self.zone_button_subframe, 
                             text=f"{zone_name} ({device_count})",
                             command=lambda z=zone_name: self._on_zone_button_click(z))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            self.zone_buttons[zone_name] = btn
        
        self._update_zone_button_styles()

    def _populate_group_buttons(self):
        # Function Description:
        # Creates buttons for each group in the selected zone.
        for widget in self.group_button_subframe.winfo_children():
            widget.destroy()
        
        self.group_buttons = {} # Clear the dictionary
        
        if not self.selected_zone or self.selected_zone not in self.zones:
            self.group_buttons_frame.grid_remove() # Hide the frame if no zone selected
            return
        
        groups = self.zones[self.selected_zone]
        
        if not groups:
            self.group_buttons_frame.grid_remove() # Hide the frame if no groups
            return
        
        # If there are groups, make sure the frame is visible
        self.group_buttons_frame.grid()
        
        max_cols = 8 # Changed max columns to 8 from 10
        for i, group_name in enumerate(sorted(groups.keys())):
            row = i // max_cols
            col = i % max_cols
            
            device_count = len(groups[group_name])
            btn = ttk.Button(self.group_button_subframe, 
                             text=f"{group_name} ({device_count})",
                             command=lambda g=group_name: self._on_group_button_click(g))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            self.group_buttons[group_name] = btn
            
        self._update_group_button_styles()

    def _on_zone_button_click(self, zone_name):
        # Function Description:
        # Handles a click on a zone button.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Zone button '{zone_name}' clicked. Initiating peak search for the entire zone.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
        self._stop_loop_action()
        self.selected_zone = zone_name
        self.selected_group = None
        self._update_zone_button_styles()
        
        # Filter the devices to be processed by the utility function
        devices_in_zone_df = self.markers_data[self.markers_data['ZONE'] == zone_name]

        if not devices_in_zone_df.empty:
            self.console_print_func(f"🔎 Starting batch peak search for all devices in zone '{zone_name}'...")
            self._peak_search_and_get_trace(devices=devices_in_zone_df, name=f"Zone: {zone_name}")
            self._populate_group_buttons()
            self._populate_device_buttons()
        else:
            self.console_print_func(f"ℹ️ No devices found in zone '{zone_name}'.")
            self._populate_group_buttons()
            self._populate_device_buttons()
            
        self._update_group_button_styles()

    def _on_group_button_click(self, group_name):
        # Function Description:
        # Handles a click on a group button.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Group button '{group_name}' clicked. Initiating peak search for the group.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)

        self._stop_loop_action()
        self.selected_group = group_name
        self._update_group_button_styles()

        devices_in_group_df = self.markers_data[(self.markers_data['ZONE'] == self.selected_zone) & (self.markers_data['GROUP'] == self.selected_group)]

        if not devices_in_group_df.empty:
            self.console_print_func(f"🔎 Starting batch peak search for all devices in group '{group_name}'...")
            self._peak_search_and_get_trace(devices=devices_in_group_df, name=f"Group: {group_name}")
            self._populate_device_buttons()
        else:
            self.console_print_func(f"ℹ️ No devices found in group '{group_name}'.")
            self._populate_device_buttons()

    def _peak_search_and_get_trace(self, devices, name):
        # Function Description:
        # Performs a batch peak search and then gets the trace for the full span of the devices.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering _peak_search_and_get_trace for {name}. Processing {len(devices)} devices.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
        if not self.app_instance.inst or devices.empty:
            self.console_print_func("❌ Cannot perform peak search: no instrument connected or no devices selected.")
            return

        # Perform peak search and update CSV in a separate thread to not block the UI
        threading.Thread(target=self._perform_peak_search_task, args=(devices, name), daemon=True).start()

    def _perform_peak_search_task(self, devices, name):
        """Worker function for the peak search task."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Starting background task for peak search on {name}.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
        # Get peak values and update CSV
        updated_markers_df = get_peak_values_and_update_csv(self.app_instance, devices, self.console_print_func)
        
        if updated_markers_df is None:
            self.app_instance.after(0, lambda: self.console_print_func("❌ Peak search failed. See console for details."))
            return
            
        self.app_instance.after(0, self._load_markers_data) # Reload data to get fresh peak values
        
        # Get min and max frequencies for the entire zone/group for the trace
        all_freqs_mhz = devices['FREQ'].dropna().tolist()
        if not all_freqs_mhz:
            self.app_instance.after(0, lambda: self.console_print_func(f"⚠️ No valid frequencies found in {name}. Cannot get a trace."))
            return
            
        min_freq_mhz = min(all_freqs_mhz)
        max_freq_mhz = max(all_freqs_mhz)
        
        span_mhz = max_freq_mhz - min_freq_mhz
        
        # FIX: Implement a minimum span for single frequencies to prevent plotting errors
        MIN_SPAN_KHZ = 100
        
        if span_mhz == 0:
            trace_center_freq_mhz = min_freq_mhz
            trace_span_mhz = MIN_SPAN_KHZ / 1e3
        else:
            buffer_mhz = span_mhz * 0.1
            trace_start_freq_mhz = max(0, min_freq_mhz - buffer_mhz)
            trace_end_freq_mhz = max_freq_mhz + buffer_mhz
            trace_center_freq_mhz = (trace_start_freq_mhz + trace_end_freq_mhz) / 2
            trace_span_mhz = trace_end_freq_mhz - trace_start_freq_mhz
            
        trace_center_freq_hz = trace_center_freq_mhz * MHZ_TO_HZ
        trace_span_hz = trace_span_mhz * MHZ_TO_HZ
        
        self.app_instance.after(0, lambda: self.console_print_func(f"📊 Displaying trace for {name} over a buffered span of {trace_span_mhz:.3f} MHz."))
        
        # Get trace for the entire span
        self.app_instance.after(0, lambda: get_marker_traces(app_instance=self.app_instance, console_print_func=self.console_print_func, center_freq_hz=trace_center_freq_hz, span_hz=trace_span_hz, device_name=name))
        
        self.app_instance.after(0, self._populate_device_buttons)

    def _update_zone_button_styles(self):
        # Function Description:
        # Updates the styles of the zone buttons to show which is active.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function}. Updating zone button styles.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        for zone_name, btn in self.zone_buttons.items():
            if btn.winfo_exists(): # Check if button exists before configuring
                if zone_name == self.selected_zone:
                    btn.config(style='SelectedPreset.Orange.TButton')
                else:
                    btn.config(style='LocalPreset.TButton')

    def _update_group_button_styles(self):
        # Function Description:
        # Updates the styles of the group buttons to show which is active.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function}. Updating group button styles.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        for group_name, btn in self.group_buttons.items():
            if btn.winfo_exists(): # Check if button exists before configuring
                if group_name == self.selected_group:
                    btn.config(style='SelectedPreset.Orange.TButton')
                else:
                    btn.config(style='LocalPreset.TButton')

    def _populate_device_buttons(self):
        # Function Description:
        # Creates buttons for each device in the selected zone or group.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function}. Populating device buttons.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
        for widget in self.device_buttons_frame.winfo_children():
            widget.destroy()

        self.device_buttons = {} # Clear the dictionary

        if not self.selected_zone:
            ttk.Label(self.device_buttons_frame, text="Select a zone and a group to view devices.").grid(row=0, column=0, columnspan=2, padx=10, pady=10)
            return

        devices = []
        if self.selected_group:
            devices = self.zones[self.selected_zone][self.selected_group]
        else:
            for group in self.zones[self.selected_zone].values():
                devices.extend(group)

        if not devices:
            ttk.Label(self.device_buttons_frame, text="No devices found in this selection.").grid(row=0, column=0, columnspan=2, padx=10, pady=10)
            return

        row_idx = 0
        col_idx = 0
        for device in devices:
            device_name = device.get('NAME', 'N/A')
            peak_value = device.get('Peak', None)
            
            if pd.notna(peak_value):
                peak_value = float(peak_value)
                if -130 <= peak_value < -80:
                    style = 'Red.TButton'
                elif -80 <= peak_value < -50:
                    style = 'Orange.TButton'
                elif peak_value >= -50:
                    style = 'Green.TButton'
                else:
                    style = 'LocalPreset.TButton'
            else:
                style = 'LocalPreset.TButton'

            text = f"{device_name}\n{device.get('FREQ', 'N/A')} MHz\nPeak: {peak_value:.2f} dBm" if pd.notna(peak_value) else f"{device_name}\n{device.get('FREQ', 'N/A')} MHz\nPeak: N/A"
            
            btn = ttk.Button(self.device_buttons_frame, text=text, style=style,
                             command=lambda d=device: self._on_device_button_click(d))
            btn.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="nsew")
            self.device_buttons[device_name] = btn # Store the button reference in the dictionary

            col_idx += 1
            if col_idx > 1:
                col_idx = 0
                row_idx += 1


    def _on_device_button_click(self, device_data):
        # Function Description:
        # Handles a click on a device button.
        current_function = inspect.currentframe().f_code.co_name
        device_name = device_data.get('NAME', 'N/A')
        debug_log(f"Device button clicked: {device_name}",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
        # Stop any existing loop
        if self.is_loop_running:
            self._stop_loop_action()

        # Update controls and instrument state based on device data
        try:
            freq_mhz = device_data.get('FREQ', 'N/A')
            zone_name = device_data.get('ZONE', 'N/A')
            group_name = device_data.get('GROUP', 'N/A')
            
            # Update internal state for the loop
            if group_name and group_name != 'N/A' and group_name.strip():
                self.selected_device_name = f"{zone_name} / {group_name} / {device_name}"
            else:
                self.selected_device_name = f"{zone_name} / {device_name}"
            
            self.selected_device_freq = float(freq_mhz) * MHZ_TO_HZ
            
            # Push settings to instrument if connected
            if self.app_instance.inst:
                freq_hz = self.selected_device_freq
                span_hz = float(self.span_var.get())
                
                # Set frequency, span, traces and marker
                set_span_logic(self.app_instance, span_hz, self.console_print_func)
                set_trace_modes_logic(self.app_instance, self.trace_live_mode.get(), self.trace_max_hold_mode.get(), self.trace_min_hold_mode.get(), self.console_print_func)
                set_frequency_logic(self.app_instance, freq_hz, self.console_print_func)
                set_marker_logic(self.app_instance, freq_hz, self.selected_device_name, self.console_print_func)
                
                # Start the trace update loop
                self.loop_counter_var.set(0)
                self.loop_run_count = 0
                # Get a reference to the button that was clicked
                if device_name in self.device_buttons:
                    clicked_button = self.device_buttons[device_name]
                    self._start_device_trace_loop(center_freq_hz=freq_hz, span_hz=span_hz, button_to_blink=clicked_button)
                else:
                    self.console_print_func(f"❌ Cannot find button for device '{device_name}'.")

                
        except (ValueError, TypeError) as e:
            self.console_print_func(f"❌ Error setting frequency and starting trace loop: {e}")
            debug_log(f"Dastardly bug! A TypeError or ValueError has struck our brave loop! Error: {e}",
                      file=f"{os.path.basename(__file__)} - {current_version}",
                      version=current_version,
                      function=current_function, special=True)
    
    def _stop_loop_action(self):
        # Function Description:
        # Handles the "Stop Loop" button action.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Stopping the loop! All systems, cease and desist!",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)

        if self.is_loop_running:
            self.is_loop_running = False
            if self.marker_trace_loop_job:
                self.after_cancel(self.marker_trace_loop_job)
                self.marker_trace_loop_job = None
            if self.blinking_button_job:
                self.after_cancel(self.blinking_button_job)
                self.blinking_button_job = None
            if self.currently_blinking_button:
                # Reset the style of the blinking button
                self.currently_blinking_button.config(style='LocalPreset.TButton')
                self.currently_blinking_button = None
            self.loop_counter_var.set(0)
            self.loop_run_count = 0
            self.console_print_func("✅ Marker trace loop stopped.")
            self._update_control_styles()
        else:
            self.console_print_func("❌ No active loop to stop.")

    def _start_device_trace_loop(self, center_freq_hz=None, span_hz=None, button_to_blink=None):
        # Function Description:
        # Starts a recurring loop to fetch marker traces for a specific device, limited to 10 cycles.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Starting the device trace loop. Get ready for some data! 📈",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
        if self.app_instance and self.app_instance.inst and center_freq_hz is not None and span_hz is not None:
            self.is_loop_running = True
            self.currently_blinking_button = button_to_blink
            self._blink_device_button()
            
            def loop_func():
                if not self.winfo_ismapped() or self.loop_run_count >= self.loop_limit or not self.is_loop_running:
                    self._stop_loop_action()
                    return
                    
                get_marker_traces(app_instance=self.app_instance, console_print_func=self.console_print_func, center_freq_hz=center_freq_hz, span_hz=span_hz, device_name=self.selected_device_name)
                self.loop_counter_var.set(self.loop_counter_var.get() + 1)
                self.loop_run_count += 1
                
                try:
                    delay = int(self.loop_delay_var.get())
                    self.marker_trace_loop_job = self.after(delay, loop_func)
                except ValueError:
                    self.console_print_func("❌ Invalid loop delay. Please enter a valid number (e.g., 500, 1000). Stopping loop.")
                    self.is_loop_running = False
                    self.loop_stop_button.config(state=tk.DISABLED)
                    return
            
            self.loop_stop_button.config(state=tk.NORMAL)
            self.marker_trace_loop_job = self.after(0, loop_func)
            
        else:
            self.console_print_func("❌ Invalid parameters for marker trace loop. Cannot start.")
            debug_log(f"Invalid parameters! We need a center frequency and a span to begin our voyage! Parameters were: center_freq_hz={center_freq_hz}, span_hz={span_hz}",
                      file=f"{os.path.basename(__file__)} - {current_version}",
                      version=current_version,
                      function=current_function, special=True)
                      
    def _blink_device_button(self):
        """Toggles the style of the selected device button to create a blinking effect."""
        if not self.is_loop_running or not self.currently_blinking_button or not self.currently_blinking_button.winfo_exists():
            return
            
        current_style = self.currently_blinking_button.cget('style')
        
        # This will alternate between two styles
        if current_style == 'DeviceButton.Blinking.TButton':
            # Use the original style of the button, determined by its peak value
            device_name = self.currently_blinking_button.cget('text').split('\n')[0]
            device_data = self.markers_data[self.markers_data['NAME'] == device_name].iloc[0]
            peak_value = device_data.get('Peak')
            
            if pd.notna(peak_value):
                peak_value = float(peak_value)
                if -130 <= peak_value < -80:
                    new_style = 'Red.TButton'
                elif -80 <= peak_value < -50:
                    new_style = 'Orange.TButton'
                elif peak_value >= -50:
                    new_style = 'Green.TButton'
                else:
                    new_style = 'LocalPreset.TButton'
            else:
                new_style = 'LocalPreset.TButton'
        else:
            new_style = 'DeviceButton.Blinking.TButton'
        
        self.currently_blinking_button.config(style=new_style)
        self.blinking_button_job = self.after(200, self._blink_device_button)


    def _on_tab_selected(self, event=None):
        # Function Description:
        # Handles the tab selection event.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"The Showtime tab has been selected. Loading markers from the file.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        self._load_markers_data()
        
        # FIX: Check if a zone is already selected, otherwise select the first one.
        if not self.selected_zone and not self.markers_data.empty:
            first_zone = sorted(list(self.markers_data['ZONE'].unique()))[0]
            self.selected_zone = first_zone
        
        self._populate_zone_buttons()
        
        if self.selected_zone:
            self._populate_group_buttons()
            self._populate_device_buttons()
        else:
            self.console_print_func("ℹ️ No zones found in MARKERS.CSV. Cannot populate groups or devices.")
            self._populate_group_buttons() # Will clear the group buttons frame
            self._populate_device_buttons() # Will clear the device buttons frame
            
    def _on_child_tab_selected(self, event=None):
        """Handles tab change events within this parent's child notebook."""
        selected_child_tab_id = self.controls_notebook.select()
        selected_child_tab_widget = self.controls_notebook.nametowidget(selected_child_tab_id)
        if hasattr(selected_child_tab_widget, '_on_tab_selected'):
            selected_child_tab_widget._on_tab_selected(event)
    
    # --- NEW METHODS FROM MarkersDisplayTab ---
    def _update_control_styles(self):
        # Function Description:
        # Updates the style of control buttons to reflect the current state.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating control button styles.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        current_span_str = self.span_var.get()
        for span_val, button in self.span_buttons.items():
            if button.winfo_exists():
                style = 'ControlButton.Active.TButton' if float(span_val) == float(current_span_str) else 'ControlButton.Inactive.TButton'
                button.configure(style=style)

        current_rbw_str = self.rbw_var.get()
        for rbw_val, button in self.rbw_buttons.items():
            if button.winfo_exists():
                style = 'ControlButton.Active.TButton' if float(rbw_val) == float(current_rbw_str) else 'ControlButton.Inactive.TButton'
                button.configure(style=style)
        
        if self.trace_buttons['Live'].winfo_exists():
            self.trace_buttons['Live'].configure(style='ControlButton.Active.TButton' if self.trace_live_mode.get() else 'ControlButton.Inactive.TButton')
        if self.trace_buttons['Max Hold'].winfo_exists():
            self.trace_buttons['Max Hold'].configure(style='ControlButton.Active.TButton' if self.trace_max_hold_mode.get() else 'ControlButton.Inactive.TButton')
        if self.trace_buttons['Min Hold'].winfo_exists():
            self.trace_buttons['Min Hold'].configure(style='ControlButton.Active.TButton' if self.trace_min_hold_mode.get() else 'ControlButton.Inactive.TButton')
        
        if self.loop_stop_button.winfo_exists():
            if self.is_loop_running:
                self.loop_stop_button.config(state=tk.NORMAL)
            else:
                self.loop_stop_button.config(state=tk.DISABLED)

    def _on_span_button_click(self, span_hz):
        # Function Description:
        # Handles a span button click.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"A span button has been clicked. Updating the instrument's span to {span_hz} Hz!",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        self.span_var.set(str(span_hz))
        self._update_control_styles()
        if self.app_instance and self.app_instance.inst:
            try:
                set_span_logic(self.app_instance, float(span_hz), self.console_print_func)
                # Restart the loop with the new span
                if self.selected_device_freq is not None and self.is_loop_running:
                    self.after_cancel(self.marker_trace_loop_job)
                    self._start_device_trace_loop(center_freq_hz=self.selected_device_freq, span_hz=float(span_hz), button_to_blink=self.currently_blinking_button)
            except (ValueError, TypeError) as e:
                debug_log(f"A ValueError or TypeError has corrupted our span logic! Error: {e}",
                          file=f"{os.path.basename(__file__)} - {current_version}",
                          version=current_version,
                          function=current_function, special=True)
                pass
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)

    def _on_rbw_button_click(self, rbw_hz):
        # Function Description:
        # Handles an RBW button click.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"An RBW button has been clicked. Setting the RBW to {rbw_hz} Hz!",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        self.rbw_var.set(str(rbw_hz))
        self._update_control_styles()
        if self.app_instance and self.app_instance.inst:
            try:
                set_rbw_logic(self.app_instance, float(rbw_hz), self.console_print_func)
            except (ValueError, TypeError) as e:
                debug_log(f"An RBW ValueError or TypeError! It's a disaster! Error: {e}",
                          file=f"{os.path.basename(__file__)} - {current_version}",
                          version=current_version,
                          function=current_function, special=True)
                pass
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)

    def _on_trace_button_click(self, trace_var):
        # Function Description:
        # Handles a trace button click.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"A trace mode button has been toggled.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        trace_var.set(not trace_var.get())
        self._update_control_styles()
        if self.app_instance and self.app_instance.inst:
            set_trace_modes_logic(self.app_instance, self.trace_live_mode.get(), self.trace_max_hold_mode.get(), self.trace_min_hold_mode.get(), self.console_print_func)
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
