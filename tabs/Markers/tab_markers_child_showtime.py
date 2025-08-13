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
# Version 20250813.094700.2 (REFACTORED: Moved all logic to utils_markers_showtime.py, leaving this file as the primary GUI builder.)

current_version = "20250813.094700.2"
current_version_hash = (20250813 * 94700 * 2)

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
from ref.frequency_bands import MHZ_TO_HZ, KHZ_TO_HZ

# NEW: Import all the moved logic from the new utility file
from tabs.Markers.utils_markers_showtime import (
    format_hz,
    load_markers_data,
    _group_by_zone_and_group,
    populate_zone_buttons,
    populate_group_buttons,
    on_zone_button_click,
    on_group_button_click,
    _peak_search_and_get_trace,
    _perform_peak_search_task,
    _update_zone_button_styles,
    _update_group_button_styles,
    populate_device_buttons,
    _create_progress_bar_text,
    on_device_button_click,
    stop_loop_action,
    start_device_trace_loop,
    _blink_device_button,
    _update_control_styles,
    on_span_button_click,
    on_rbw_button_click,
    on_trace_button_click,
    on_poke_action,
    LOOP_DELAY_OPTIONS,
)


class ThresholdsTab(ttk.Frame):
    """
    A placeholder tab for future threshold settings.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        # Function Description:
        # Initializes the ThresholdsTab.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing ThresholdsTab. A blank canvas for future brilliance! 🎨",
                  file=f"{os.path.basename(__file__)}",
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
                  file=f"{os.path.basename(__file__)}",
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
        self.marker_trace_loop_job = None
        self.is_loop_running = False
        
        self.blinking_button_job = None
        self.currently_blinking_button = None
        self.loop_run_count = 0
        self.loop_limit = 10
        
        self.span_var = tk.StringVar(value="1000000.0")
        self.rbw_var = tk.StringVar(value="30000.0")
        self.poke_freq_var = tk.StringVar()
        self.trace_live_mode = tk.BooleanVar(value=True)
        self.trace_max_hold_mode = tk.BooleanVar(value=True)
        self.trace_min_hold_mode = tk.BooleanVar(value=False)
        self.loop_delay_var = tk.StringVar(value="500")
        self.loop_counter_var = tk.IntVar(value=0)
        
        self.span_buttons = {}
        self.rbw_buttons = {}
        self.trace_buttons = {}
        self.loop_stop_button = None
        
        self.instrument_lock = threading.Lock()

        self._create_widgets()
        self.after(100, self._on_tab_selected)

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

        # --- Zone Buttons Frame ---
        self.zone_buttons_frame = ttk.LabelFrame(self, text="Zones", padding=5, style='Dark.TLabelframe')
        self.zone_buttons_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.zone_buttons_frame.grid_columnconfigure(0, weight=1)

        self.zone_button_subframe = ttk.Frame(self.zone_buttons_frame, style='Dark.TFrame')
        self.zone_button_subframe.pack(fill="x", expand=False)
        
        for i in range(8):
            self.zone_button_subframe.grid_columnconfigure(i, weight=1)

        # --- Group Buttons Frame ---
        self.group_buttons_frame = ttk.LabelFrame(self, text="Groups", padding=5, style='Dark.TLabelframe')
        self.group_buttons_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.group_buttons_frame.grid_columnconfigure(0, weight=1)

        self.group_button_subframe = ttk.Frame(self.group_buttons_frame, style='Dark.TFrame')
        self.group_button_subframe.pack(fill="x", expand=False)
        
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
        
        for i in range(4):
            self.device_buttons_frame.grid_columnconfigure(i, weight=1)
        
        # --- Controls Notebook (Bottom Right) ---
        self.controls_notebook = ttk.Notebook(self, style='Markers.Child.TNotebook')
        self.controls_notebook.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        # --- Span Tab ---
        span_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(span_tab, text="Span")
        for i, (name, span_hz) in enumerate(SPAN_OPTIONS.items()):
            val_text = format_hz(span_hz)
            btn_text = f"{name}\n{val_text}"

            btn = ttk.Button(span_tab, text=btn_text, command=lambda s=span_hz: on_span_button_click(self, s))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")

            self.span_buttons[str(span_hz)] = btn
            span_tab.grid_columnconfigure(i, weight=1)

        # --- RBW Tab ---
        rbw_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(rbw_tab, text="RBW")
        for i, (name, rbw_hz) in enumerate(RBW_OPTIONS.items()):
            btn_text = f"{name}\n{rbw_hz / 1000:.0f} kHz"
            btn = ttk.Button(rbw_tab, text=btn_text, command=lambda r=rbw_hz: on_rbw_button_click(self, r))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.rbw_buttons[str(rbw_hz)] = btn
            rbw_tab.grid_columnconfigure(i, weight=1)

        # --- Trace Tab ---
        trace_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(trace_tab, text="Trace")
        trace_modes = [("Live", self.trace_live_mode), ("Max Hold", self.trace_max_hold_mode), ("Min Hold", self.trace_min_hold_mode)]
        for i, (name, var) in enumerate(trace_modes):
            btn = ttk.Button(trace_tab, text=name, command=lambda v=var: on_trace_button_click(self, v))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.trace_buttons[name] = btn
            trace_tab.grid_columnconfigure(i, weight=1)

        # --- Poke Tab ---
        poke_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(poke_tab, text="Poke")
        poke_tab.grid_columnconfigure(0, weight=1)
        poke_tab.grid_columnconfigure(1, weight=1)
        ttk.Entry(poke_tab, textvariable=self.poke_freq_var).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(poke_tab, text="POKE", command=lambda: on_poke_action(self), style='DeviceButton.Active.TButton').grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # --- Loop Tab ---
        loop_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(loop_tab, text="Loop")
        loop_tab.grid_columnconfigure(0, weight=1)
        loop_tab.grid_columnconfigure(1, weight=1)
        loop_tab.grid_columnconfigure(2, weight=1)

        ttk.Label(loop_tab, text="Delay (ms):").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        delay_combobox = ttk.Combobox(loop_tab, textvariable=self.loop_delay_var, values=LOOP_DELAY_OPTIONS, state="readonly")
        delay_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew", columnspan=2)

        ttk.Label(loop_tab, text="Loop Count:").grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ttk.Label(loop_tab, textvariable=self.loop_counter_var).grid(row=1, column=1, padx=5, pady=5, sticky="ew", columnspan=2)

        self.loop_stop_button = ttk.Button(loop_tab, text="Stop Loop", command=lambda: stop_loop_action(self), state=tk.DISABLED)
        self.loop_stop_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew", columnspan=3)

    def _on_tab_selected(self, event):
        # Function Description:
        # Handles the tab selection event.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"The tab has been selected. Loading markers from the file.",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)
        load_markers_data(self)
        
        if not self.selected_zone and not self.markers_data.empty:
            first_zone = sorted(list(self.markers_data['ZONE'].unique()))[0]
            self.selected_zone = first_zone
        
        populate_zone_buttons(self)
        
        if self.selected_zone:
            self.console_print_func(f"▶️ Automatically starting peak search for default zone: '{self.selected_zone}'.")
            on_zone_button_click(self, self.selected_zone)
        else:
            self.console_print_func("ℹ️ No zones found in MARKERS.CSV. Cannot populate groups or devices.")
            populate_group_buttons(self)
            populate_device_buttons(self)
            
    def _on_child_tab_selected(self, event=None):
        selected_child_tab_id = self.controls_notebook.select()
        selected_child_tab_widget = self.controls_notebook.nametowidget(selected_child_tab_id)
        if hasattr(selected_child_tab_widget, '_on_tab_selected'):
            selected_child_tab_widget._on_tab_selected(event)
