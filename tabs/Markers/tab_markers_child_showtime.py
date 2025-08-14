# tabs/Markers/tab_markers_child_showtime.py
#
# This file defines the ShowtimeTab, a Tkinter Frame for displaying markers
# organized by a new Zone/Group hierarchy. Its automatic update functionality
# is now driven entirely by the main application's Orchestrator.
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
# Version 20250814.005950.1

current_version = "20250814.005950.1"

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
from tabs.Markers.utils_markers_file_handling import load_markers_data, _group_by_zone_and_group

from src.program_style import COLOR_PALETTE
from src.settings_and_config.config_manager import save_config
from ref.frequency_bands import MHZ_TO_HZ


class ShowtimeTab(ttk.Frame):
    """
    A Tkinter Frame for displaying markers organized by Zone and Device.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        # Function Description:
        # Initializes the ShowtimeTab, setting up the UI frame and internal state.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing ShowtimeTab...",
                  file=f"{os.path.basename(__file__)}",
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
        self.device_buttons = {}
        
        self.selected_device_name = None
        self.selected_device_freq = None
        
        self.instrument_lock = threading.Lock()

        # --- State Variables for Controls ---
        self.span_var = tk.StringVar(value="1000000.0")
        self.rbw_var = tk.StringVar(value="30000.0")
        self.poke_freq_var = tk.StringVar()
        self.trace_live_mode = tk.BooleanVar(value=True)
        self.trace_max_hold_mode = tk.BooleanVar(value=True)
        self.trace_min_hold_mode = tk.BooleanVar(value=False)
        self.follow_zone_span_var = tk.BooleanVar(value=True)

        self.span_buttons = {}
        self.rbw_buttons = {}
        self.trace_buttons = {}
        
        self._create_widgets()
        self.after(100, self._on_tab_selected)
        self.after(200, lambda: self.orchestrated_update_loop())


    def _create_widgets(self):
        # Function Description:
        # Creates and arranges the widgets for the Showtime tab.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating ShowtimeTab widgets.",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)

        self.zone_buttons_frame = ttk.LabelFrame(self, text="Zones", padding=5, style='Dark.TLabelframe')
        self.zone_buttons_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.zone_button_subframe = ttk.Frame(self.zone_buttons_frame, style='Dark.TFrame')
        self.zone_button_subframe.pack(fill="x", expand=False)
        for i in range(8): self.zone_button_subframe.grid_columnconfigure(i, weight=1)

        self.group_buttons_frame = ttk.LabelFrame(self, text="Groups", padding=5, style='Dark.TLabelframe')
        self.group_buttons_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.group_button_subframe = ttk.Frame(self.group_buttons_frame, style='Dark.TFrame')
        self.group_button_subframe.pack(fill="x", expand=False)
        for i in range(8): self.group_button_subframe.grid_columnconfigure(i, weight=1)

        self.device_scrollable_frame = ttk.LabelFrame(self, text="Devices", padding=5, style='Dark.TLabelframe')
        self.device_scrollable_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        self.device_scrollable_frame.grid_columnconfigure(0, weight=1)
        self.device_scrollable_frame.grid_rowconfigure(0, weight=1)
        canvas = tk.Canvas(self.device_scrollable_frame, bg=COLOR_PALETTE['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.device_scrollable_frame, orient="vertical", command=canvas.yview)
        self.device_buttons_frame = ttk.Frame(canvas, style='Dark.TFrame')
        canvas.create_window((0, 0), window=self.device_buttons_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        for i in range(4): self.device_buttons_frame.grid_columnconfigure(i, weight=1)
        
        self.controls_notebook = ttk.Notebook(self, style='Markers.Child.TNotebook')
        self.controls_notebook.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        span_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(span_tab, text="Span")
        
        follow_btn = ttk.Button(span_tab, text="Follow Zone\nand Group", command=lambda s='Follow': self.on_span_button_click(s))
        follow_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.span_buttons['Follow'] = follow_btn
        
        for i, (name, span_hz) in enumerate(SPAN_OPTIONS.items()):
            btn_text = f"{name}\n{self.format_hz(span_hz)}"
            btn = ttk.Button(span_tab, text=btn_text, command=lambda s=span_hz: self.on_span_button_click(s))
            btn.grid(row=0, column=i + 1, padx=5, pady=5, sticky="ew")
            self.span_buttons[str(span_hz)] = btn
        
        for i in range(len(SPAN_OPTIONS) + 1):
             span_tab.grid_columnconfigure(i, weight=1)

        rbw_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(rbw_tab, text="RBW")
        for i, (name, rbw_hz) in enumerate(RBW_OPTIONS.items()):
            btn_text = f"{name}\n{rbw_hz / 1000:.0f} kHz"
            btn = ttk.Button(rbw_tab, text=btn_text, command=lambda r=rbw_hz: self.on_rbw_button_click(r))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.rbw_buttons[str(rbw_hz)] = btn
            rbw_tab.grid_columnconfigure(i, weight=1)
            
        trace_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(trace_tab, text="Trace")
        trace_modes = [("Live", self.trace_live_mode), ("Max Hold", self.trace_max_hold_mode), ("Min Hold", self.trace_min_hold_mode)]
        for i, (name, var) in enumerate(trace_modes):
            btn = ttk.Button(trace_tab, text=name, command=lambda v=var: self.on_trace_button_click(v))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.trace_buttons[name] = btn
            trace_tab.grid_columnconfigure(i, weight=1)

        poke_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(poke_tab, text="Poke")
        poke_tab.grid_columnconfigure(1, weight=1)
        ttk.Entry(poke_tab, textvariable=self.poke_freq_var).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(poke_tab, text="POKE", command=lambda: self.on_poke_action(), style='DeviceButton.Active.TButton').grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def _on_tab_selected(self, event=None):
        """Handles the tab selection event."""
        self.load_markers_data_wrapper()
        
        if not self.selected_zone and not self.markers_data.empty:
            first_zone = sorted(list(self.markers_data['ZONE'].unique()))[0]
            self.selected_zone = first_zone
        
        self.populate_zone_buttons()
        
        if self.selected_zone:
            self.on_zone_button_click(self.selected_zone)
        else:
            self.console_print_func("ℹ️ No zones found in MARKERS.CSV. Cannot populate groups or devices.")
            self.populate_group_buttons()
            self.populate_device_buttons()
            
    def _on_child_tab_selected(self, event=None):
        """Handles selection changes within the controls notebook."""
        selected_child_tab_id = self.controls_notebook.select()
        selected_child_tab_widget = self.controls_notebook.nametowidget(selected_child_tab_id)
        if hasattr(selected_child_tab_widget, '_on_tab_selected'):
            selected_child_tab_widget._on_tab_selected(event)
            
    def on_span_button_click(self, span_hz):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}. Span button clicked. Changing instrument span to {span_hz} Hz!",
                  file=f"{os.path.basename(__file__)} & {current_version}",
                  version=current_version,
                  function=current_function)
        
        if span_hz == 'Follow':
            current_state = self.follow_zone_span_var.get()
            self.follow_zone_span_var.set(not current_state)
            if self.selected_group and self.follow_zone_span_var.get():
                self.on_group_button_click(self.selected_group)
            self.console_print_func(f"✅ 'Follow Zone' mode {'enabled' if self.follow_zone_span_var.get() else 'disabled'}.")
        else:
            self.follow_zone_span_var.set(False)
            status, message = set_span_logic(app_instance=self.app_instance, span_hz=span_hz, console_print_func=self.console_print_func)
            self.console_print_func(message)
            if status:
                self.span_var.set(str(span_hz))
            
        self._update_control_styles()
        
    def on_rbw_button_click(self, rbw_hz):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}. RBW button clicked. Setting instrument RBW to {rbw_hz} Hz!",
                  file=f"{os.path.basename(__file__)} & {current_version}",
                  version=current_version,
                  function=current_function)
        
        status, message = set_rbw_logic(app_instance=self.app_instance, rbw_hz=rbw_hz, console_print_func=self.console_print_func)
        self.console_print_func(message)
        if status:
            self.rbw_var.set(str(rbw_hz))
            
        self._update_control_styles()
    
    def on_trace_button_click(self, trace_var):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}. Trace button clicked. Changing trace mode!",
                  file=f"{os.path.basename(__file__)} & {current_version}",
                  version=current_version,
                  function=current_function)

        trace_var.set(not trace_var.get())
        
        status, message = set_trace_modes_logic(
            app_instance=self.app_instance,
            live_mode=self.trace_live_mode.get(),
            max_hold_mode=self.trace_max_hold_mode.get(),
            min_hold_mode=self.trace_min_hold_mode.get(),
            console_print_func=self.console_print_func
        )
        self.console_print_func(message)
        
        self._update_control_styles()
        
    def on_poke_action(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}. Poke button pressed. Poking instrument with a custom frequency!",
                  file=f"{os.path.basename(__file__)} & {current_version}",
                  version=current_version,
                  function=current_function)
        
        try:
            poked_freq_mhz = float(self.poke_freq_var.get())
            poked_freq_hz = int(poked_freq_mhz * MHZ_TO_HZ)
            
            with self.instrument_lock:
                status_freq, message_freq = set_frequency_logic(app_instance=self.app_instance, frequency_hz=poked_freq_hz, console_print_func=self.console_print_func)
                status_marker, message_marker = set_marker_logic(app_instance=self.app_instance, frequency_hz=poked_freq_hz, console_print_func=self.console_print_func)

            self.console_print_func(message_freq)
            self.console_print_func(message_marker)
            
        except (ValueError, IndexError):
            self.console_print_func("❌ Invalid frequency for poke action. Please enter a numerical value in MHz.")
            debug_log(f"Error: Invalid frequency format for poke action. Poked frequency was '{self.poke_freq_var.get()}'",
                      file=f"{os.path.basename(__file__)} & {current_version}",
                      version=current_version,
                      function=current_function)
        
        self.selected_device_name = None
        self._update_control_styles()
        
    def orchestrated_update_loop(self):
        if not self.app_instance.orchestrator_gui.is_running:
            self.after(500, lambda: self.orchestrated_update_loop())
            return

        if self.app_instance.orchestrator_gui.is_paused:
            self.after(500, lambda: self.orchestrated_update_loop())
            return

        if self.selected_device_freq is not None:
            center_freq_hz = self.selected_device_freq
            span_hz = float(self.span_var.get())
            device_name = self.selected_device_name
            with self.instrument_lock:
                get_marker_traces(app_instance=self.app_instance,
                                  showtime_tab_instance=self,
                                  console_print_func=self.console_print_func,
                                  center_freq_hz=center_freq_hz,
                                  span_hz=span_hz,
                                  device_name=device_name)

        elif self.selected_zone is not None:
            devices_to_process = pd.DataFrame()
            name = ""
            if self.selected_group:
                name = f"Group: {self.selected_group}"
                devices_to_process = self.markers_data[
                    (self.markers_data['ZONE'] == self.selected_zone) &
                    (self.markers_data['GROUP'] == self.selected_group)
                ]
            else:
                name = f"Zone: {self.selected_zone}"
                devices_to_process = self.markers_data[
                    self.markers_data['ZONE'] == self.selected_zone
                ]
            
            if not devices_to_process.empty:
                self._peak_search_and_get_trace(devices=devices_to_process, name=name)
        
        self.after(500, lambda: self.orchestrated_update_loop())
    
    def format_hz(self, hz_val):
        try:
            hz = float(hz_val)
            if hz >= MHZ_TO_HZ:
                return f"{hz / MHZ_TO_HZ:.1f}".replace('.0', '') + " MHz"
            elif hz >= 1000:
                return f"{hz / 1000:.1f}".replace('.0', '') + " kHz"
            else:
                return f"{hz} Hz"
        except (ValueError, TypeError):
            return "N/A"

    def load_markers_data_wrapper(self):
        markers_data, status, message = load_markers_data(self.app_instance, self.console_print_func)
        self.console_print_func(message)
        self.markers_data = markers_data
        self.zones = _group_by_zone_and_group(markers_data)
        
    def populate_zone_buttons(self):
        for widget in self.zone_button_subframe.winfo_children():
            widget.destroy()

        self.zone_buttons = {}
        
        if not isinstance(self.zones, dict) or not self.zones:
            ttk.Label(self.zone_button_subframe, text="No zones found in MARKERS.CSV.").grid(row=0, column=0, columnspan=8)
            return
            
        max_cols = 8
        for i, zone_name in enumerate(sorted(self.zones.keys())):
            row = i // max_cols
            col = i % max_cols
            device_count = sum(len(group) for group in self.zones[zone_name].values())
            btn = ttk.Button(self.zone_button_subframe, 
                             text=f"{zone_name} ({device_count})",
                             command=lambda z=zone_name: self.on_zone_button_click(z))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            self.zone_buttons[zone_name] = btn
        
        self._update_zone_button_styles()

    def populate_group_buttons(self):
        for widget in self.group_button_subframe.winfo_children():
            widget.destroy()
        
        self.group_buttons = {}
        
        if not self.selected_zone or self.selected_zone not in self.zones:
            self.group_buttons_frame.grid_remove()
            return
        
        groups = self.zones[self.selected_zone]
        
        if not groups:
            self.group_buttons_frame.grid_remove()
            return
        
        self.group_buttons_frame.grid()
        
        max_cols = 8
        for i, group_name in enumerate(sorted(groups.keys())):
            row = i // max_cols
            col = i % max_cols
            device_count = len(groups[group_name])
            btn = ttk.Button(self.group_button_subframe, 
                             text=f"{group_name} ({device_count})",
                             command=lambda g=group_name: self.on_group_button_click(g))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            self.group_buttons[group_name] = btn
            
        self._update_group_button_styles()


    def on_zone_button_click(self, zone_name):
        self.selected_zone = zone_name
        self.selected_group = None
        self.selected_device_freq = None
        self._update_zone_button_styles()
        
        self.follow_zone_span_var.set(True)
        self._update_control_styles()

        self.populate_group_buttons()
        self.populate_device_buttons()
        self._update_group_button_styles()

    def on_group_button_click(self, group_name):
        self.selected_group = group_name
        self.selected_device_freq = None
        self._update_group_button_styles()
        
        self.follow_zone_span_var.set(True)
        self._update_control_styles()

        self.populate_device_buttons()

    def _peak_search_and_get_trace(self, devices, name):
        if not self.app_instance.inst or devices.empty:
            self.console_print_func("❌ Cannot perform peak search: no instrument connected or no devices selected.")
            return

        threading.Thread(target=self._perform_peak_search_task, args=(devices, name), daemon=True).start()

    def _perform_peak_search_task(self, devices, name):
        with self.instrument_lock:
            updated_markers_df = get_peak_values_and_update_csv(app_instance=self.app_instance, devices_to_process=devices, console_print_func=self.console_print_func)
        
        if updated_markers_df is None:
            self.app_instance.after(0, lambda: self.console_print_func("❌ Peak search failed."))
            return
            
        self.app_instance.after(0, lambda: self.load_markers_data_wrapper())
        
        all_freqs_mhz = devices['FREQ'].dropna().tolist()
        if not all_freqs_mhz:
            return
            
        min_freq_mhz = min(all_freqs_mhz)
        max_freq_mhz = max(all_freqs_mhz)
        span_mhz = max_freq_mhz - min_freq_mhz
        
        trace_center_freq_mhz = (min_freq_mhz + max_freq_mhz) / 2
        trace_span_mhz = span_mhz if span_mhz > 0 else 0.1 # Min span of 100 kHz
            
        trace_center_freq_hz = int(trace_center_freq_mhz * MHZ_TO_HZ)
        trace_span_hz = int(trace_span_mhz * MHZ_TO_HZ)
        
        with self.instrument_lock:
            # Set the span before getting the trace only if in "Follow Zone" mode
            if self.follow_zone_span_var.get():
                status, message = set_span_logic(app_instance=self.app_instance, span_hz=trace_span_hz, console_print_func=self.console_print_func)
                self.app_instance.after(0, lambda: self.console_print_func(message))
                status, message = set_frequency_logic(app_instance=self.app_instance, frequency_hz=trace_center_freq_hz, console_print_func=self.console_print_func)
                self.app_instance.after(0, lambda: self.console_print_func(message))

            # Now get the traces for the full view
            self.app_instance.after(0, lambda: get_marker_traces(
                app_instance=self.app_instance, 
                showtime_tab_instance=self, 
                console_print_func=self.console_print_func, 
                center_freq_hz=trace_center_freq_hz, 
                span_hz=trace_span_hz, 
                device_name=name
            ))
        
        self.app_instance.after(0, lambda: self.populate_device_buttons())

    def _update_zone_button_styles(self):
        for zone_name, btn in self.zone_buttons.items():
            if btn.winfo_exists():
                btn.config(style='SelectedPreset.Orange.TButton' if zone_name == self.selected_zone else 'LocalPreset.TButton')

    def _update_group_button_styles(self):
        for group_name, btn in self.group_buttons.items():
            if btn.winfo_exists():
                btn.config(style='SelectedPreset.Orange.TButton' if group_name == self.selected_group else 'LocalPreset.TButton')

    def populate_device_buttons(self):
        for widget in self.device_buttons_frame.winfo_children():
            widget.destroy()
        self.device_buttons = {}

        if not self.selected_zone:
            ttk.Label(self.device_buttons_frame, text="Select a zone/group.").grid()
            return

        devices = []
        if self.selected_group:
            devices = self.zones[self.selected_zone].get(self.selected_group, [])
        else:
            for group_data in self.zones[self.selected_zone].values():
                devices.extend(group_data)

        if not devices:
            ttk.Label(self.device_buttons_frame, text="No devices found.").grid()
            return

        for i, device in enumerate(devices):
            device_name = device.get('NAME', 'N/A')
            peak_value = device.get('Peak', None)
            style = 'LocalPreset.TButton'
            
            # FIXED: Check if peak_value is not an empty string before converting to float
            if pd.notna(peak_value) and peak_value != '':
                peak_value = float(peak_value)
                if -80 > peak_value >= -130: style = 'Red.TButton'
                elif -50 > peak_value >= -80: style = 'Orange.TButton'
                elif peak_value >= -50: style = 'Green.TButton'
                
                progress_bar = self._create_progress_bar_text(peak_value)
                text = f"{device_name}\n{device.get('FREQ', 'N/A')} MHz\nPeak: {peak_value:.2f} dBm\n{progress_bar}"
            else:
                text = f"{device_name}\n{device.get('FREQ', 'N/A')} MHz\nPeak: N/A"
            
            btn = ttk.Button(self.device_buttons_frame, text=text, style=style,
                             command=lambda d=device: self.on_device_button_click(d))
            btn.grid(row=i // 4, column=i % 4, padx=5, pady=5, sticky="nsew")
            self.device_buttons[device_name] = btn


    def _create_progress_bar_text(self, peak_value):
        if pd.isna(peak_value): return "[                        ]"
        min_dbm, max_dbm = -120.0, 0.0
        clamped_value = max(min_dbm, min(max_dbm, peak_value))
        num_filled_chars = int((clamped_value - min_dbm) / (max_dbm - min_dbm) * 24)
        return f"[{'█' * num_filled_chars}{' ' * (24 - num_filled_chars)}]"

    def on_device_button_click(self, device_data):
        try:
            freq_mhz = device_data.get('FREQ', 'N/A')
            device_name = device_data.get('NAME', 'N/A')
            zone_name = device_data.get('ZONE', 'N/A')
            group_name = device_data.get('GROUP', 'N/A')
            
            self.selected_device_name = f"{zone_name}/{group_name}/{device_name}" if group_name and group_name != 'No Group' else f"{zone_name}/{device_name}"
            self.selected_device_freq = float(freq_mhz) * MHZ_TO_HZ
            
            self.follow_zone_span_var.set(False)
            self._update_control_styles()

            if self.app_instance.inst:
                with self.instrument_lock:
                    status_span, message_span = set_span_logic(app_instance=self.app_instance, span_hz=float(self.span_var.get()), console_print_func=self.console_print_func)
                    self.console_print_func(message_span)
                    status_freq, message_freq = set_frequency_logic(app_instance=self.app_instance, frequency_hz=self.selected_device_freq, console_print_func=self.console_print_func)
                    self.console_print_func(message_freq)
                    status_marker, message_marker = set_marker_logic(app_instance=self.app_instance, frequency_hz=self.selected_device_freq, console_print_func=self.console_print_func)
                    self.console_print_func(message_marker)
        except (ValueError, TypeError) as e:
            self.console_print_func(f"❌ Error setting frequency on device click: {e}")

    def _update_control_styles(self):
        if self.follow_zone_span_var.get():
            self.span_buttons['Follow'].configure(style='ControlButton.Active.TButton')
            for span_val, button in self.span_buttons.items():
                if span_val != 'Follow' and button.winfo_exists():
                    button.configure(style='ControlButton.Inactive.TButton')
        else:
            self.span_buttons['Follow'].configure(style='ControlButton.Inactive.TButton')
            current_span_str = self.span_var.get()
            for span_val, button in self.span_buttons.items():
                if span_val != 'Follow' and button.winfo_exists():
                    style = 'ControlButton.Active.TButton' if float(span_val) == float(current_span_str) else 'ControlButton.Inactive.TButton'
                    button.configure(style=style)

        current_rbw_str = self.rbw_var.get()
        for rbw_val, button in self.rbw_buttons.items():
            if button.winfo_exists():
                button.configure(style='ControlButton.Active.TButton' if float(rbw_val) == float(current_rbw_str) else 'ControlButton.Inactive.TButton')
        
        for name, var in [("Live", self.trace_live_mode), ("Max Hold", self.trace_max_hold_mode), ("Min Hold", self.trace_min_hold_mode)]:
            if name in self.trace_buttons and self.trace_buttons[name].winfo_exists():
                self.trace_buttons[name].configure(style='ControlButton.Active.TButton' if var.get() else 'ControlButton.Inactive.TButton')
    
    def on_span_button_click(self, span_hz):
        if span_hz == 'Follow':
            self.follow_zone_span_var.set(True)
        else:
            self.follow_zone_span_var.set(False)
            self.span_var.set(str(span_hz))
        
        self._update_control_styles()
        
        if self.app_instance and self.app_instance.inst:
            if not self.follow_zone_span_var.get():
                try:
                    with self.instrument_lock:
                        status, message = set_span_logic(app_instance=self.app_instance, span_hz=float(span_hz), console_print_func=self.console_print_func)
                        self.console_print_func(message)
                except (ValueError, TypeError) as e:
                     debug_log(f"Span logic error: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function=inspect.currentframe().f_code.co_name)
        save_config(config=self.app_instance.config, file_path=self.app_instance.CONFIG_FILE_PATH, console_print_func=self.console_print_func, app_instance=self.app_instance)

    def on_rbw_button_click(self, rbw_hz):
        self.rbw_var.set(str(rbw_hz))
        self._update_control_styles()
        if self.app_instance and self.app_instance.inst:
            try:
                with self.instrument_lock:
                    status, message = set_rbw_logic(app_instance=self.app_instance, rbw_hz=float(rbw_hz), console_print_func=self.console_print_func)
                    self.console_print_func(message)
            except (ValueError, TypeError) as e:
                debug_log(f"RBW logic error: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function=inspect.currentframe().f_code.co_name)
        save_config(config=self.app_instance.config, file_path=self.app_instance.CONFIG_FILE_PATH, console_print_func=self.console_print_func, app_instance=self.app_instance)

    def on_trace_button_click(self, trace_var):
        trace_var.set(not trace_var.get())
        self._update_control_styles()
        if self.app_instance and self.app_instance.inst:
            with self.instrument_lock:
                status, message = set_trace_modes_logic(app_instance=self.app_instance, live_mode=self.trace_live_mode.get(), max_hold_mode=self.trace_max_hold_mode.get(), min_hold_mode=self.trace_min_hold_mode.get(), console_print_func=self.console_print_func)
                self.console_print_func(message)
        save_config(config=self.app_instance.config, file_path=self.app_instance.CONFIG_FILE_PATH, console_print_func=self.console_print_func, app_instance=self.app_instance)

    def on_poke_action(self):
        if self.app_instance and self.app_instance.inst:
            try:
                freq_mhz = self.poke_freq_var.get()
                freq_hz = float(freq_mhz) * MHZ_TO_HZ
                poke_marker_name = f"POKE: {freq_mhz} MHz"
                span_hz = float(self.span_var.get())

                with self.instrument_lock:
                    status_span, message_span = set_span_logic(self.app_instance, span_hz, self.console_print_func)
                    self.console_print_func(message_span)
                    status_trace, message_trace = set_trace_modes_logic(self.app_instance, self.trace_live_mode.get(), self.trace_max_hold_mode.get(), self.trace_min_hold_mode.get(), self.console_print_func)
                    self.console_print_func(message_trace)
                    status_freq, message_freq = set_frequency_logic(self.app_instance, freq_hz, self.console_print_func)
                    self.console_print_func(message_freq)
                    status_marker, message_marker = set_marker_logic(app_instance=self.app_instance, frequency_hz=self.selected_device_freq, console_print_func=self.console_print_func)
                    self.console_print_func(message_marker)

                self.selected_device_name = poke_marker_name
                self.selected_device_freq = freq_hz

            except (ValueError, TypeError) as e:
                self.console_print_func(f"❌ Invalid POKE frequency: {e}")