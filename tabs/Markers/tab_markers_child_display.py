# tabs/Markers/tab_markers_child_display.py
#
# This file manages the Markers Display tab in the GUI, handling
# the display of extracted frequency markers, span control, and trace mode selection.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can benegotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
#
#
# Version 20250803.233500.0 (CHANGED: Loads defaults from config. Updated RBW button layout.)
# Version 20250803.232800.0 (CHANGED: Set default Span, RBW, and Trace modes on initialization.)
# Version 20250803.232500.0 (FIXED: Re-enabled initial data load to ensure tab populates on startup.)

current_version = "20250803.233500.0" 
current_version_hash = (20250803 * 233500 * 0 + 2039482) # Example hash

import tkinter as tk
from tkinter import ttk 
import os
import csv
import inspect

from tabs.Markers.utils_markers import SPAN_OPTIONS, RBW_OPTIONS, set_span_logic, set_frequency_logic, set_trace_modes_logic, set_marker_logic, set_rbw_logic
from src.debug_logic import debug_log 
from src.console_logic import console_log 
from ref.frequency_bands import MHZ_TO_HZ 
from src.program_style import COLOR_PALETTE


class MarkersDisplayTab(ttk.Frame):
    """
    A Tkinter Frame that displays extracted frequency markers and provides instrument control.
    """
    def __init__(self, master=None, headers=None, rows=None, app_instance=None, **kwargs):
        super().__init__(master, **kwargs)
        self.headers = headers if headers is not None else []
        self.rows = rows if rows is not None else [] 
        self.app_instance = app_instance 

        self.selected_device_unique_id = None
        
        # --- State Variables for Controls ---
        # Load defaults from the application's config object
        config = self.app_instance.config
        default_span = config.get('MarkerTabDefaults', 'span', fallback='1000000.0')
        default_rbw = config.get('MarkerTabDefaults', 'rbw', fallback='1000000.0')
        default_live = config.getboolean('MarkerTabDefaults', 'trace_live', fallback=True)
        default_max = config.getboolean('MarkerTabDefaults', 'trace_max_hold', fallback=True)
        default_min = config.getboolean('MarkerTabDefaults', 'trace_min_hold', fallback=True)

        self.span_var = tk.StringVar(value=default_span)
        self.rbw_var = tk.StringVar(value=default_rbw)
        self.poke_freq_var = tk.StringVar()
        self.trace_live_mode = tk.BooleanVar(value=default_live)
        self.trace_max_hold_mode = tk.BooleanVar(value=default_max)
        self.trace_min_hold_mode = tk.BooleanVar(value=default_min)
        
        # --- Dictionaries to hold control buttons for styling ---
        self.span_buttons = {}
        self.rbw_buttons = {}
        self.trace_buttons = {}

        self._create_widgets()
        self.after(100, self.load_markers_from_file) 
        self.after(150, self._update_control_styles)

    def _create_widgets(self):
        """
        Creates the widgets for the Markers Display tab.
        """
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_split_frame = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_split_frame.grid(row=0, column=0, sticky="nsew")

        # --- Left Pane (unchanged) ---
        # ...

        # --- Right Pane (unchanged) ---
        # ...

        # --- Device Buttons Frame (unchanged) ---
        # ...
        
        # --- Controls Notebook (Bottom Right) ---
        self.controls_notebook = ttk.Notebook(right_pane_frame, style='Markers.Child.TNotebook')
        self.controls_notebook.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # --- Span Tab ---
        span_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(span_tab, text="Span")
        for i, (name, span_hz) in enumerate(SPAN_OPTIONS.items()):
            val_text = self._format_hz(span_hz)
            btn_text = f"{name}\n{val_text}"
            
            btn = ttk.Button(span_tab, text=btn_text, command=lambda s=span_hz: self._on_span_button_click(s))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            
            self.span_buttons[str(span_hz)] = btn
            span_tab.grid_columnconfigure(i, weight=1)

        # --- RBW Tab (UPDATED) ---
        rbw_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(rbw_tab, text="RBW")
        for i, (name, rbw_hz) in enumerate(RBW_OPTIONS.items()):
            val_text = self._format_hz(rbw_hz)
            btn_text = f"{name}\n{val_text}"

            btn = ttk.Button(rbw_tab, text=btn_text, command=lambda r=rbw_hz: self._on_rbw_button_click(r))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.rbw_buttons[str(rbw_hz)] = btn
            rbw_tab.grid_columnconfigure(i, weight=1)

        # --- Trace Tab (unchanged) ---
        # ...

        # --- Poke Tab (unchanged) ---
        # ...

    # (All other methods remain unchanged)
    # ...
# Full file content is included for completeness, but unchanged parts are omitted from the visible response block.
# The following is the complete, correct code for the file.

    def __init__(self, master=None, headers=None, rows=None, app_instance=None, **kwargs):
        super().__init__(master, **kwargs)
        self.headers = headers if headers is not None else []
        self.rows = rows if rows is not None else [] 
        self.app_instance = app_instance 

        self.selected_device_unique_id = None
        
        # --- State Variables for Controls ---
        # Load defaults from the application's config object
        config = self.app_instance.config
        default_span = config.get('MarkerTabDefaults', 'span', fallback='1000000.0')
        default_rbw = config.get('MarkerTabDefaults', 'rbw', fallback='1000000.0')
        default_live = config.getboolean('MarkerTabDefaults', 'trace_live', fallback=True)
        default_max = config.getboolean('MarkerTabDefaults', 'trace_max_hold', fallback=True)
        default_min = config.getboolean('MarkerTabDefaults', 'trace_min_hold', fallback=True)

        self.span_var = tk.StringVar(value=default_span)
        self.rbw_var = tk.StringVar(value=default_rbw)
        self.poke_freq_var = tk.StringVar()
        self.trace_live_mode = tk.BooleanVar(value=default_live)
        self.trace_max_hold_mode = tk.BooleanVar(value=default_max)
        self.trace_min_hold_mode = tk.BooleanVar(value=default_min)
        
        # --- Dictionaries to hold control buttons for styling ---
        self.span_buttons = {}
        self.rbw_buttons = {}
        self.trace_buttons = {}

        self._create_widgets()
        self.after(100, self.load_markers_from_file) 
        self.after(150, self._update_control_styles)

    def _create_widgets(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        main_split_frame = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_split_frame.grid(row=0, column=0, sticky="nsew")
        tree_frame = ttk.LabelFrame(main_split_frame, text="Zones & Groups", padding=5, style='Dark.TLabelframe')
        main_split_frame.add(tree_frame, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        self.zone_group_tree = ttk.Treeview(tree_frame, show="tree")
        self.zone_group_tree.grid(row=0, column=0, sticky="nsew")
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.zone_group_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        self.zone_group_tree.configure(yscrollcommand=tree_scrollbar.set)
        self.zone_group_tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        right_pane_frame = ttk.Frame(main_split_frame, style='TFrame')
        main_split_frame.add(right_pane_frame, weight=3)
        right_pane_frame.grid_rowconfigure(0, weight=1)
        right_pane_frame.grid_rowconfigure(1, weight=0)
        right_pane_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame = ttk.LabelFrame(right_pane_frame, text="Devices", padding=5, style='Dark.TLabelframe')
        self.buttons_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.buttons_frame.grid_rowconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        canvas = tk.Canvas(self.buttons_frame, bg=COLOR_PALETTE['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.buttons_frame, orient="vertical", command=canvas.yview)
        self.inner_buttons_frame = ttk.Frame(canvas, style='Dark.TFrame')
        self.button_frame_window = canvas.create_window((0, 0), window=self.inner_buttons_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.inner_buttons_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind('<Configure>', self._on_canvas_configure)
        canvas.bind('<Enter>', lambda e: canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units")))
        canvas.bind('<Leave>', lambda e: canvas.unbind_all("<MouseWheel>"))
        self.controls_notebook = ttk.Notebook(right_pane_frame, style='Markers.Child.TNotebook')
        self.controls_notebook.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        span_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(span_tab, text="Span")
        for i, (name, span_hz) in enumerate(SPAN_OPTIONS.items()):
            val_text = self._format_hz(span_hz)
            btn_text = f"{name}\n{val_text}"
            btn = ttk.Button(span_tab, text=btn_text, command=lambda s=span_hz: self._on_span_button_click(s))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.span_buttons[str(span_hz)] = btn
            span_tab.grid_columnconfigure(i, weight=1)
        rbw_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(rbw_tab, text="RBW")
        for i, (name, rbw_hz) in enumerate(RBW_OPTIONS.items()):
            val_text = self._format_hz(rbw_hz)
            btn_text = f"{name}\n{val_text}"
            btn = ttk.Button(rbw_tab, text=btn_text, command=lambda r=rbw_hz: self._on_rbw_button_click(r))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.rbw_buttons[str(rbw_hz)] = btn
            rbw_tab.grid_columnconfigure(i, weight=1)
        trace_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(trace_tab, text="Trace")
        trace_modes = [("Live", self.trace_live_mode), ("Max Hold", self.trace_max_hold_mode), ("Min Hold", self.trace_min_hold_mode)]
        for i, (name, var) in enumerate(trace_modes):
            btn = ttk.Button(trace_tab, text=name, command=lambda v=var: self._on_trace_button_click(v))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.trace_buttons[name] = btn
            trace_tab.grid_columnconfigure(i, weight=1)
        poke_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(poke_tab, text="Poke")
        poke_tab.grid_columnconfigure(0, weight=1)
        poke_tab.grid_columnconfigure(1, weight=1)
        ttk.Entry(poke_tab, textvariable=self.poke_freq_var).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(poke_tab, text="POKE", command=self._on_poke_action, style='DeviceButton.Active.TButton').grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def _on_canvas_configure(self, event):
        canvas = event.widget
        canvas.itemconfig(self.button_frame_window, width=event.width)

    def _format_hz(self, hz_val):
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

    def _update_control_styles(self):
        current_span = self.span_var.get()
        for span_val, button in self.span_buttons.items():
            style = 'ControlButton.Active.TButton' if span_val == current_span else 'ControlButton.Inactive.TButton'
            button.configure(style=style)
        current_rbw = self.rbw_var.get()
        for rbw_val, button in self.rbw_buttons.items():
            style = 'ControlButton.Active.TButton' if rbw_val == current_rbw else 'ControlButton.Inactive.TButton'
            button.configure(style=style)
        self.trace_buttons['Live'].configure(style='ControlButton.Active.TButton' if self.trace_live_mode.get() else 'ControlButton.Inactive.TButton')
        self.trace_buttons['Max Hold'].configure(style='ControlButton.Active.TButton' if self.trace_max_hold_mode.get() else 'ControlButton.Inactive.TButton')
        self.trace_buttons['Min Hold'].configure(style='ControlButton.Active.TButton' if self.trace_min_hold_mode.get() else 'ControlButton.Inactive.TButton')

    def _populate_zone_group_tree(self):
        self.zone_group_tree.delete(*self.zone_group_tree.get_children())
        nested_data = {}
        for row in self.rows:
            zone = row.get('ZONE', 'Uncategorized').strip()
            group = row.get('GROUP', '').strip()
            if zone not in nested_data: nested_data[zone] = {}
            if group not in nested_data[zone]: nested_data[zone][group] = []
            nested_data[zone][group].append(row)
        for zone, groups in sorted(nested_data.items()):
            zone_id = self.zone_group_tree.insert("", "end", text=zone, open=True)
            for group in sorted(groups.keys()):
                if group:
                    self.zone_group_tree.insert(zone_id, "end", text=group, open=True)

    def _on_tree_select(self, event):
        selected_item = self.zone_group_tree.selection()
        if not selected_item: return
        item = selected_item[0]
        parent_id = self.zone_group_tree.parent(item)
        text = self.zone_group_tree.item(item, 'text')
        devices = []
        if not parent_id:
            for row in self.rows:
                if row.get('ZONE', '').strip() == text: devices.append(row)
        else:
            zone_name = self.zone_group_tree.item(parent_id, 'text')
            for row in self.rows:
                if row.get('ZONE', '').strip() == zone_name and row.get('GROUP', '').strip() == text:
                    devices.append(row)
        self._populate_device_buttons(devices)

    def _populate_device_buttons(self, devices):
        for widget in self.inner_buttons_frame.winfo_children():
            widget.destroy()
        if not devices:
            ttk.Label(self.inner_buttons_frame, text="Select a zone or group.").pack()
            return
        num_columns = 3 if len(devices) > 10 else 2
        for i in range(num_columns): self.inner_buttons_frame.grid_columnconfigure(i, weight=1)
        for i, data in enumerate(devices):
            freq = data.get('FREQ', 'N/A')
            uid = f"{data.get('NAME', '')}-{freq}"
            text = f"{data.get('NAME', 'N/A')}\n{data.get('DEVICE', 'N/A')}\n{freq} MHz"
            style = 'DeviceButton.Active.TButton' if uid == self.selected_device_unique_id else 'DeviceButton.Inactive.TButton'
            btn = ttk.Button(self.inner_buttons_frame, text=text, style=style, command=lambda d=data: self._on_device_button_click(d))
            btn.grid(row=i // num_columns, column=i % num_columns, padx=5, pady=5, sticky="ew")

    def _on_device_button_click(self, device_data):
        freq_mhz = device_data.get('FREQ', 'N/A')
        self.selected_device_unique_id = f"{device_data.get('NAME', '')}-{freq_mhz}"
        self.poke_freq_var.set(str(freq_mhz))
        self.controls_notebook.select(0)
        self._populate_device_buttons(self.get_current_displayed_devices())
        if self.app_instance and self.app_instance.inst:
            try:
                freq_hz = float(freq_mhz) * MHZ_TO_HZ
                set_frequency_logic(self.app_instance.inst, freq_hz, console_log)
                set_marker_logic(self.app_instance.inst, freq_hz, device_data.get('NAME', ''), console_log)
            except (ValueError, TypeError) as e:
                console_log(f"Error setting frequency: {e}")

    def get_current_displayed_devices(self):
        selected_item = self.zone_group_tree.selection()
        if not selected_item: return []
        item = selected_item[0]
        parent_id = self.zone_group_tree.parent(item)
        text = self.zone_group_tree.item(item, 'text')
        devices = []
        if not parent_id:
            for row in self.rows:
                if row.get('ZONE', '').strip() == text: devices.append(row)
        else:
            zone_name = self.zone_group_tree.item(parent_id, 'text')
            for row in self.rows:
                if row.get('ZONE', '').strip() == zone_name and row.get('GROUP', '').strip() == text:
                    devices.append(row)
        return devices

    def update_marker_data(self, new_headers, new_rows):
        self.headers = new_headers if new_headers is not None else []
        self.rows = new_rows if new_rows is not None else []
        self._populate_zone_group_tree()
        first_item = self.zone_group_tree.get_children()
        if first_item:
            self.zone_group_tree.selection_set(first_item[0])
            self.zone_group_tree.focus(first_item[0])
            self._on_tree_select(None)

    def load_markers_from_file(self):
        if self.app_instance and hasattr(self.app_instance, 'MARKERS_FILE_PATH'):
            path = self.app_instance.MARKERS_FILE_PATH
            if os.path.exists(path):
                try:
                    with open(path, mode='r', newline='', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        self.update_marker_data(list(reader.fieldnames or []), list(reader))
                except Exception as e:
                    console_log(f"Error loading MARKERS.CSV: {e}")
                    self.update_marker_data([], [])
            else: self.update_marker_data([], [])

    def _on_span_button_click(self, span_hz):
        self.span_var.set(str(span_hz))
        self._update_control_styles()
        if self.app_instance and self.app_instance.inst:
            try:
                set_span_logic(self.app_instance.inst, span_hz, console_log)
            except (ValueError, TypeError): pass

    def _on_rbw_button_click(self, rbw_hz):
        self.rbw_var.set(str(rbw_hz))
        self._update_control_styles()
        if self.app_instance and self.app_instance.inst:
            try:
                set_rbw_logic(self.app_instance.inst, rbw_hz, console_log)
            except (ValueError, TypeError): pass

    def _on_trace_button_click(self, trace_var):
        trace_var.set(not trace_var.get())
        self._update_control_styles()
        if self.app_instance and self.app_instance.inst:
            set_trace_modes_logic(self.app_instance.inst, self.trace_live_mode.get(), self.trace_max_hold_mode.get(), self.trace_min_hold_mode.get(), console_log)

    def _on_poke_action(self):
        if self.app_instance and self.app_instance.inst:
            try:
                freq_mhz = self.poke_freq_var.get()
                freq_hz = float(freq_mhz) * MHZ_TO_HZ
                set_frequency_logic(self.app_instance.inst, freq_hz, console_log)
                set_marker_logic(self.app_instance.inst, freq_hz, f"Poke {freq_mhz} MHz", console_log)
                self.selected_device_unique_id = None
                self._populate_device_buttons(self.get_current_displayed_devices())
            except (ValueError, TypeError) as e:
                console_log(f"Invalid POKE frequency: {e}")

    def _on_parent_tab_selected(self, event):
        debug_log(f"🚀 Markers tab selected, reloading {os.path.basename(self.app_instance.MARKERS_FILE_PATH)}.", file=f"{os.path.basename(__file__)} - {current_version}", function=inspect.currentframe().f_code.co_name)
        self.load_markers_from_file()