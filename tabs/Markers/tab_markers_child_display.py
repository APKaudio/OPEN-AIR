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
# Version 20250804.000009.0 (FIXED: Ensured MARKERS.CSV loads on init. Applied default Span/RBW/Trace modes to instrument on load.)
# Version 20250804.000010.0 (FIXED: AttributeError by passing and storing console_log in __init__.)
# Version 20250804.000011.0 (REFINED: Ensured device buttons are always populated after treeview update/selection.)
# Version 20250804.000012.0 (DEBUG: Added extensive logging to pinpoint MARKERS.CSV refresh issue.)
# Version 20250804.000013.0 (DEBUG: Added extreme path and file content verification logging.)
# Version 20250804.000015.0 (DEBUG: Added more specific path logging and file contents on reload.)

current_version = "20250804.000015.0" # Incremented version for debug logging
current_version_hash = (20250803 * 233500 * 0 + 2039482) # Example hash

import tkinter as tk
from tkinter import ttk 
import os
import csv
import inspect
import time # NEW: Import time for potential delays in debugging

from tabs.Markers.utils_markers import SPAN_OPTIONS, RBW_OPTIONS, set_span_logic, set_frequency_logic, set_trace_modes_logic, set_marker_logic, set_rbw_logic
from src.debug_logic import debug_log 
from src.console_logic import console_log # Keep this import, as it's the global function
from ref.frequency_bands import MHZ_TO_HZ 
from src.program_style import COLOR_PALETTE


class MarkersDisplayTab(ttk.Frame):
    """
    A Tkinter Frame that displays extracted frequency markers and provides instrument control.
    """
    def __init__(self, master=None, headers=None, rows=None, app_instance=None, console_print_func=None, **kwargs):
        super().__init__(master, **kwargs)
        self.headers = headers if headers is not None else []
        self.rows = rows if rows is not None else [] 
        self.app_instance = app_instance 
        self.console_log = console_print_func if console_print_func else console_log # Store console_log

        self.selected_device_unique_id = None
        
        # --- State Variables for Controls ---
        config = self.app_instance.config
        default_span_name = 'NORMAL'
        default_rbw_name = '1MHz' 
        
        default_span_hz_fallback = SPAN_OPTIONS.get(default_span_name, 10_000_000.0) 
        default_rbw_hz_fallback = RBW_OPTIONS.get(default_rbw_name, 1_000_000.0)    

        default_span_cfg = config.get('MarkerTabDefaults', 'span', fallback=str(default_span_hz_fallback))
        default_rbw_cfg = config.get('MarkerTabDefaults', 'rbw', fallback=str(default_rbw_hz_fallback))
        default_live_cfg = config.getboolean('MarkerTabDefaults', 'trace_live', fallback=True)
        default_max_cfg = config.getboolean('MarkerTabDefaults', 'trace_max_hold', fallback=True)
        default_min_cfg = config.getboolean('MarkerTabDefaults', 'trace_min_hold', fallback=True)

        self.span_var = tk.StringVar(value=default_span_cfg)
        self.rbw_var = tk.StringVar(value=default_rbw_cfg)
        self.poke_freq_var = tk.StringVar()
        self.trace_live_mode = tk.BooleanVar(value=default_live_cfg)
        self.trace_max_hold_mode = tk.BooleanVar(value=default_max_cfg)
        self.trace_min_hold_mode = tk.BooleanVar(value=default_min_cfg)
        
        self.span_buttons = {}
        self.rbw_buttons = {}
        self.trace_buttons = {}

        self._create_widgets()
        
        # --- DEBUG: Initial Load & Apply Settings from __init__ ---
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] [INIT] Calling load_markers_from_file() and _apply_initial_instrument_settings() from __init__.",
                    file=__file__,
                    version=current_version,
                    function=current_function,
                    special=True)

        self.load_markers_from_file() # Load MARKERS.CSV
        self._apply_initial_instrument_settings() # Apply current defaults to instrument
        self._update_control_styles() # Update button styles based on current state

        debug_log(f"[{os.path.basename(__file__)} - {current_function}] Initializing MarkersDisplayTab completed. Version: {current_version}. Marker display ready! ✅",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    def _apply_initial_instrument_settings(self):
        """
        Applies the default span, RBW, and trace modes to the instrument on tab load.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] [APPLY INITIAL SETTINGS] Applying initial default instrument settings for Markers tab. 🔧",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if self.app_instance and self.app_instance.inst:
            try:
                span_hz = float(self.span_var.get())
                set_span_logic(self.app_instance.inst, span_hz, self.console_log) 
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] Initial Span set to: {span_hz} Hz.",
                            file=__file__,
                            version=current_version,
                            function=current_function)

                rbw_hz = float(self.rbw_var.get())
                set_rbw_logic(self.app_instance.inst, rbw_hz, self.console_log) 
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] Initial RBW set to: {rbw_hz} Hz.",
                            file=__file__,
                            version=current_version,
                            function=current_function)

                set_trace_modes_logic(
                    self.app_instance.inst,
                    self.trace_live_mode.get(),
                    self.trace_max_hold_mode.get(),
                    self.trace_min_hold_mode.get(),
                    self.console_log 
                )
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] Initial Trace Modes set: Live={self.trace_live_mode.get()}, MaxHold={self.trace_max_hold_mode.get()}, MinHold={self.trace_min_hold_mode.get()}.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                
                self.console_log("✅ Default Markers tab instrument settings applied.")

            except ValueError as e:
                self.console_log(f"❌ Error applying default marker settings (invalid value): {e}. This is a disaster!")
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] ValueError applying initial marker settings: {e}",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            except Exception as e:
                self.console_log(f"❌ Unexpected error applying default marker settings: {e}. What a mess!")
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] Unexpected error applying initial marker settings: {e}",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        else:
            debug_log(f"[{os.path.basename(__file__)} - {current_function}] No instrument connected. Skipping initial marker settings application to instrument.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            self.console_log("ℹ️ No instrument connected. Default marker settings applied to UI only.")

    def _create_widgets(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] Creating MarkersDisplayTab widgets.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

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

        debug_log(f"[{os.path.basename(__file__)} - {current_function}] MarkersDisplayTab widgets created. Ready for action! 🎨",
                    file=__file__,
                    version=current_version,
                    function=current_function)

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
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] Updating control button styles... Looking sharp! 💅",
                    file=__file__,
                    version=current_version,
                    function=current_function)

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
        
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] Control button styles updated. ✨",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    def _populate_zone_group_tree(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] Populating zone/group treeview...",
                    file=__file__,
                    version=current_version,
                    function=current_function)

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
        
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] Zone/group treeview populated with {len(nested_data)} zones. 🌳",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    def _on_tree_select(self, event):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] Treeview item selected. Updating device buttons... 🌲",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        selected_item = self.zone_group_tree.selection()
        if not selected_item:
            debug_log(f"[{os.path.basename(__file__)} - {current_function}] No item selected in treeview. Clearing device buttons.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            self._populate_device_buttons([]) 
            return

        item = selected_item[0]
        parent_id = self.zone_group_tree.parent(item)
        text = self.zone_group_tree.item(item, 'text')
        devices = []

        if not parent_id: 
            for row in self.rows:
                if row.get('ZONE', '').strip() == text:
                    devices.append(row)
            debug_log(f"[{os.path.basename(__file__)} - {current_function}] Selected Zone: '{text}'. Found {len(devices)} devices.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else: 
            zone_name = self.zone_group_tree.item(parent_id, 'text')
            for row in self.rows:
                if row.get('ZONE', '').strip() == zone_name and row.get('GROUP', '').strip() == text:
                    devices.append(row)
            debug_log(f"[{os.path.basename(__file__)} - {current_function}] Selected Group: '{text}' in Zone '{zone_name}'. Found {len(devices)} devices.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        self._populate_device_buttons(devices)

    def _populate_device_buttons(self, devices):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] Populating device buttons with {len(devices)} devices. Clicking time! 🤖",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        for widget in self.inner_buttons_frame.winfo_children():
            widget.destroy()

        if not devices:
            ttk.Label(self.inner_buttons_frame, text="Select a zone or group.").pack(padx=10, pady=10)
            debug_log(f"[{os.path.basename(__file__)} - {current_function}] No devices to populate. Showing placeholder message.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        num_columns = 3 if len(devices) > 10 else 2 
        for i in range(num_columns):
            self.inner_buttons_frame.grid_columnconfigure(i, weight=1)

        for i, data in enumerate(devices):
            freq = data.get('FREQ', 'N/A')
            try:
                freq_display = f"{float(freq):.3f}" 
            except (ValueError, TypeError):
                freq_display = "N/A"

            uid = f"{data.get('NAME', '')}-{freq}" 
            text = f"{data.get('NAME', 'N/A')}\n{data.get('DEVICE', 'N/A')}\n{freq_display} MHz"
            
            style = 'DeviceButton.Active.TButton' if uid == self.selected_device_unique_id else 'DeviceButton.Inactive.TButton'
            
            btn = ttk.Button(self.inner_buttons_frame, text=text, style=style, command=lambda d=data: self._on_device_button_click(d))
            btn.grid(row=i // num_columns, column=i % num_columns, padx=5, pady=5, sticky="ew")

        debug_log(f"[{os.path.basename(__file__)} - {current_function}] Device buttons populated in {num_columns} columns.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    def _on_device_button_click(self, device_data):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] Device button clicked for: {device_data.get('NAME', 'Unnamed Device')}. Poking instrument! 🎯",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        freq_mhz_str = device_data.get('FREQ', 'N/A')
        
        self.selected_device_unique_id = f"{device_data.get('NAME', '')}-{freq_mhz_str}" 
        self.poke_freq_var.set(str(freq_mhz_str)) 

        self.controls_notebook.select(0) 

        self._populate_device_buttons(self.get_current_displayed_devices())

        if self.app_instance and self.app_instance.inst:
            try:
                freq_hz = float(freq_mhz_str) * MHZ_TO_HZ
                set_frequency_logic(self.app_instance.inst, freq_hz, self.console_log) 
                set_marker_logic(self.app_instance.inst, freq_hz, device_data.get('NAME', 'Unnamed'), self.console_log) 
                self.console_log(f"✅ Set instrument frequency to {freq_mhz_str} MHz and marker for '{device_data.get('NAME', 'Unnamed')}'.")
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] Instrument frequency set to {freq_hz} Hz and marker for '{device_data.get('NAME', 'Unnamed')}'.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            except (ValueError, TypeError) as e:
                self.console_log(f"❌ Error setting frequency/marker for device '{device_data.get('NAME', 'Unnamed')}': {e}. Invalid frequency value!")
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] Error setting frequency/marker: {e}. Value: {freq_mhz_str}.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            except Exception as e:
                self.console_log(f"❌ Unexpected error setting frequency/marker for device '{device_data.get('NAME', 'Unnamed')}': {e}. What a mess!")
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] Unexpected error setting frequency/marker: {e}.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        else:
            self.console_log("ℹ️ No instrument connected. Frequency and marker set in UI only.")
            debug_log(f"[{os.path.basename(__file__)} - {current_function}] No instrument connected. Skipping freq/marker set for instrument.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    def get_current_displayed_devices(self):
        self.load_markers_from_file()
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
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] [UPDATE MARKER DATA] Updating marker data. New rows count: {len(new_rows)}. 🔄",
                    file=__file__,
                    version=current_version,
                    function=current_function,
                    special=True)

        self.headers = new_headers if new_headers is not None else []
        self.rows = new_rows if new_rows is not None else []
        
        self._populate_zone_group_tree()
        
        first_item = self.zone_group_tree.get_children()
        if first_item:
            self.zone_group_tree.selection_set(first_item[0])
            self.zone_group_tree.focus(first_item[0])
            self._on_tree_select(None) 
        else:
            self._populate_device_buttons([]) 

        debug_log(f"[{os.path.basename(__file__)} - {current_function}] Marker data updated and UI refreshed. ✅",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    def load_markers_from_file(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] [LOAD MARKERS] Attempting to load MARKERS.CSV from: {self.app_instance.MARKERS_FILE_PATH}. 📂",
                    file=__file__,
                    version=current_version,
                    function=current_function,
                    special=True) # Tag as special for easy filtering

        # --- EXTREME DEBUGGING FOR PATH RESOLUTION ---
        # Use the MARKERS_FILE_PATH from app_instance directly
        markers_file_path = self.app_instance.MARKERS_FILE_PATH
        output_dir = os.path.dirname(markers_file_path) # Get the directory part
        markers_file_path_from_file = os.path.join(output_dir, 'MARKERS.CSV')

        debug_log(f"[{os.path.basename(__file__)} - {current_function}] === PATH RESOLUTION DEBUG START ===",
                    file=__file__, version=current_version, function=current_function, special=True)
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] BASE_DIR (from this file's location): '{markers_file_path_from_file}'",
                    file=__file__, version=current_version, function=current_function, special=True)
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] DATA_FOLDER_PATH (computed): '{output_dir}'",
                    file=__file__, version=current_version, function=current_function, special=True)
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] MARKERS_FILE_PATH (computed): '{markers_file_path_from_file}'",
                    file=__file__, version=current_version, function=current_function, special=True)
        
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] Does DATA_FOLDER_PATH exist?: {os.path.exists(output_dir)}",
                    file=__file__, version=current_version, function=current_function, special=True)
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] Does MARKERS_FILE_PATH exist (computed)?: {os.path.exists(markers_file_path_from_file)}",
                    file=__file__, version=current_version, function=current_function, special=True)
        
        if os.path.exists(output_dir):
            try:
                data_folder_contents = os.listdir(output_dir)
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] Contents of DATA folder: {data_folder_contents}",
                            file=__file__, version=current_version, function=current_function, special=True)
            except Exception as e:
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] ERROR listing DATA folder contents: {e}",
                            file=__file__, version=current_version, function=current_function, special=True)

        debug_log(f"[{os.path.basename(__file__)} - {current_function}] === PATH RESOLUTION DEBUG END ===",
                    file=__file__, version=current_version, function=current_function, special=True)
        # --- END EXTREME DEBUGGING ---


        if self.app_instance and hasattr(self.app_instance, 'MARKERS_FILE_PATH'):
            path = self.app_instance.MARKERS_FILE_PATH # This is the path we're actually using
            debug_log(f"[{os.path.basename(__file__)} - {current_function}] Path used by app_instance: '{path}'",
                        file=__file__, version=current_version, function=current_function, special=True)


            if os.path.exists(path):
                # --- DEBUG: Verify file content before reading ---
                try:
                    with open(path, 'r', newline='', encoding='utf-8') as f_debug:
                        content_start = f_debug.read(500) # Read first 500 chars for better context
                        debug_log(f"[{os.path.basename(__file__)} - {current_function}] MARKERS.CSV content start (first 500 chars from '{path}'): \n---START CONTENT---\n'{content_start.strip()}'\n---END CONTENT---",
                                    file=__file__,
                                    version=current_version,
                                    function=current_function,
                                    special=True)
                except Exception as e:
                    debug_log(f"[{os.path.basename(__file__)} - {current_function}] DEBUG ERROR: Could not read first 500 chars of MARKERS.CSV for content verification: {e}",
                                file=__file__,
                                version=current_version,
                                function=current_function,
                                special=True)
                # --- END DEBUG ---

                try:
                    with open(path, mode='r', newline='', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        all_fieldnames = reader.fieldnames if reader.fieldnames else []
                        
                        rows_with_all_headers = []
                        for row in reader:
                            cleaned_row = {k: v if v is not None else '' for k, v in row.items()}
                            for header in all_fieldnames: 
                                if header not in cleaned_row:
                                    cleaned_row[header] = ''
                            rows_with_all_headers.append(cleaned_row)

                        debug_log(f"[{os.path.basename(__file__)} - {current_function}] Successfully read {len(rows_with_all_headers)} rows from MARKERS.CSV. Fieldnames: {all_fieldnames}",
                                    file=__file__,
                                    version=current_version,
                                    function=current_function,
                                    special=True)
                        
                        self.update_marker_data(all_fieldnames, rows_with_all_headers)
                        self.console_log(f"✅ Loaded {len(rows_with_all_headers)} markers from {os.path.basename(path)}.")
                        debug_log(f"[{os.path.basename(__file__)} - {current_function}] Successfully loaded {len(rows_with_all_headers)} markers from {path}. Good job!",
                                    file=__file__,
                                    version=current_version,
                                    function=current_function)
                except Exception as e:
                    self.console_log(f"❌ Error loading MARKERS.CSV '{os.path.basename(path)}': {e}. What a mess!")
                    debug_log(f"[{os.path.basename(__file__)} - {current_function}] ERROR: Failed to read/parse MARKERS.CSV '{path}': {e}",
                                file=__file__,
                                version=current_version,
                                function=current_function,
                                special=True)
                    self.update_marker_data([], []) 
            else:
                self.console_log(f"ℹ️ MARKERS.CSV not found at '{os.path.basename(path)}'. No markers loaded.")
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] MARKERS.CSV file does NOT exist at '{path}'.",
                            file=__file__,
                            version=current_version,
                            function=current_function,
                            special=True)
                self.update_marker_data([], []) 
        else:
            self.console_log("❌ Application instance or MARKERS_FILE_PATH not available. Cannot load markers.")
            debug_log(f"[{os.path.basename(__file__)} - {current_function}] app_instance or MARKERS_FILE_PATH is None. Cannot load markers.",
                        file=__file__,
                        version=current_version,
                        function=current_function,
                        special=True)
            self.update_marker_data([], []) 

    def _on_span_button_click(self, span_hz):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] Span button clicked. Setting span to {span_hz} Hz. 📡",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        self.span_var.set(str(span_hz))
        self._update_control_styles() 

        if self.app_instance and self.app_instance.inst:
            try:
                set_span_logic(self.app_instance.inst, span_hz, self.console_log) 
                self.console_log(f"✅ Instrument Span set to {self._format_hz(span_hz)}.")
            except (ValueError, TypeError) as e:
                self.console_log(f"❌ Error setting Span to {self._format_hz(span_hz)}: {e}. Invalid value!")
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] ValueError/TypeError setting Span: {e}. Value: {span_hz}",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            except Exception as e:
                self.console_log(f"❌ Unexpected error setting Span: {e}. This is a disaster!")
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] Unexpected error setting Span: {e}",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        else:
            self.console_log("ℹ️ No instrument connected. Span set in UI only.")
            debug_log(f"[{os.path.basename(__file__)} - {current_function}] No instrument connected. Skipping Span set for instrument.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    def _on_rbw_button_click(self, rbw_hz):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] RBW button clicked. Setting RBW to {rbw_hz} Hz. 📏",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        self.rbw_var.set(str(rbw_hz))
        self._update_control_styles() 

        if self.app_instance and self.app_instance.inst:
            try:
                set_rbw_logic(self.app_instance.inst, rbw_hz, self.console_log) 
                self.console_log(f"✅ Instrument RBW set to {self._format_hz(rbw_hz)}.")
            except (ValueError, TypeError) as e:
                self.console_log(f"❌ Error setting RBW to {self._format_hz(rbw_hz)}: {e}. Invalid value!")
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] ValueError/TypeError setting RBW: {e}. Value: {rbw_hz}",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            except Exception as e:
                self.console_log(f"❌ Unexpected error setting RBW: {e}. What a mess!")
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] Unexpected error setting RBW: {e}",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        else:
            self.console_log("ℹ️ No instrument connected. RBW set in UI only.")
            debug_log(f"[{os.path.basename(__file__)} - {current_function}] No instrument connected. Skipping RBW set for instrument.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    def _on_trace_button_click(self, trace_var):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] Trace button clicked. Toggling trace mode. ✨",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        trace_var.set(not trace_var.get()) 
        self._update_control_styles() 

        if self.app_instance and self.app_instance.inst:
            try:
                set_trace_modes_logic(self.app_instance.inst, self.trace_live_mode.get(), self.trace_max_hold_mode.get(), self.trace_min_hold_mode.get(), self.console_log) 
                self.console_log(f"✅ Instrument Trace Modes updated. Live: {self.trace_live_mode.get()}, Max Hold: {self.trace_max_hold_mode.get()}, Min Hold: {self.trace_min_hold_mode.get()}.")
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] Instrument Trace Modes updated.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            except Exception as e:
                self.console_log(f"❌ Error setting Trace Modes: {e}. This is a disaster!")
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] Error setting Trace Modes: {e}",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        else:
            self.console_log("ℹ️ No instrument connected. Trace Modes set in UI only.")
            debug_log(f"[{os.path.basename(__file__)} - {current_function}] No instrument connected. Skipping Trace Modes set for instrument.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    def _on_poke_action(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] Poke button clicked. Setting frequency and marker. 🎯",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if self.app_instance and self.app_instance.inst:
            try:
                freq_mhz_str = self.poke_freq_var.get()
                freq_hz = float(freq_mhz_str) * MHZ_TO_HZ
                set_frequency_logic(self.app_instance.inst, freq_hz, self.console_log) 
                set_marker_logic(self.app_instance.inst, freq_hz, f"Poke {freq_mhz_str} MHz", self.console_log) 
                self.selected_device_unique_id = None 
                self._populate_device_buttons(self.get_current_displayed_devices()) 
                self.console_log(f"✅ Instrument POKED to {freq_mhz_str} MHz with marker.")
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] Instrument POKED to {freq_hz} Hz.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            except (ValueError, TypeError) as e:
                self.console_log(f"❌ Invalid POKE frequency: '{self.poke_freq_var.get()}'. Error: {e}. Please enter a number!")
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] Invalid POKE frequency: {e}. Value: {self.poke_freq_var.get()}",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            except Exception as e:
                self.console_log(f"❌ Unexpected error during POKE action: {e}. This thing is a pain in the ass!")
                debug_log(f"[{os.path.basename(__file__)} - {current_function}] Unexpected error during POKE action: {e}",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        else:
            self.console_log("ℹ️ No instrument connected. POKE action skipped.")
            debug_log(f"[{os.path.basename(__file__)} - {current_function}] No instrument connected. Skipping POKE action.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    def _on_parent_tab_selected(self, event):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] [PARENT TAB SELECTED] 🚀 Markers tab selected, reloading {os.path.basename(self.app_instance.MARKERS_FILE_PATH)} and applying defaults.",
                    file=__file__,
                    version=current_version,
                    function=current_function,
                    special=True) # Tag as special for easy filtering
        
        debug_log(f"[{os.path.basename(__file__)} - {current_function}] app_instance.MARKERS_FILE_PATH is: '{self.app_instance.MARKERS_FILE_PATH}'",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        self.load_markers_from_file()
        self._apply_initial_instrument_settings() 
        self._update_control_styles()