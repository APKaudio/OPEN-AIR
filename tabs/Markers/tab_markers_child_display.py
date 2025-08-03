# tabs/Markers/tab_markers_child_display.py
#
# This file manages the Markers Display tab in the GUI, handling
# the display of extracted frequency markers, span control, and trace mode selection.
# It is designed to ONLY interact with the instrument when a user explicitly
# clicks a relevant button (device button, span button, or trace mode button).
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
# Version 20250803.184600.0 (FIXED: Restored missing _on_tree_select method and verified hasattr checks.)
# Version 20250803.184500.1 (FIXED: Added hasattr safety checks for app_instance.inst to prevent AttributeError.)
# Version 20250803.0930.0 (Enabled device buttons during POKE mode, added tab focus on device select, ensured button height fills container.)
# Version 20250803.0925.0 (Adjusted Manual Marker tab to horizontal layout and removed LabelFrames from control tabs.)
# Version 20250803.0920.0 (FIXED: Device buttons not populating on tab re-entry. Implemented new layout for Manual Marker tab.)

current_version = "20250803.184600.0" 

import tkinter as tk
from tkinter import scrolledtext, filedialog, ttk 
import os
import csv
import inspect
import json 
import math 

from tabs.Markers.utils_markers import SPAN_OPTIONS, RBW_OPTIONS, set_span_logic, set_frequency_logic, set_trace_modes_logic, set_marker_logic, blank_hold_traces_logic, set_rbw_logic
from src.debug_logic import debug_log 
from src.console_logic import console_log 
from ref.frequency_bands import MHZ_TO_HZ 


class MarkersDisplayTab(ttk.Frame):
    """
    A Tkinter Frame that displays extracted frequency markers in a hierarchical treeview
    and as clickable buttons.
    """
    def __init__(self, master=None, headers=None, rows=None, app_instance=None, **kwargs):
        super().__init__(master, **kwargs)
        self.headers = headers if headers is not None else []
        self.rows = rows if rows is not None else [] 
        self.app_instance = app_instance 

        self.config(style="Markers.TFrame")
        self.last_selected_span_button = None 
        self.current_span_hz = None 

        self.live_mode_var = tk.BooleanVar(self, value=True)
        self.max_hold_mode_var = tk.BooleanVar(self, value=False)
        self.min_hold_mode_var = tk.BooleanVar(self, value=False)
        self.trace_mode_buttons = {} 

        self.current_selected_device_button = None 
        self.selected_device_unique_id = None
        self.current_selected_device_data = None 

        self.current_displayed_device_name_var = tk.StringVar(self, value="N/A")
        self.current_displayed_device_type_var = tk.StringVar(self, value="N/A")
        self.current_displayed_center_freq_var = tk.StringVar(self, value="N/A")
        self.current_span_var = tk.StringVar(self, value="N/A")
        self.current_trace_modes_var = tk.StringVar(self, value="N/A")
        self.current_rbw_var = tk.StringVar(self, value="N/A") 
        self.last_selected_rbw_button = None 
        self.manual_freq_entry_var = tk.StringVar(self, value="") 

        self.poke_mode_active = tk.BooleanVar(self, value=False) 

        self._create_widgets()

    def _create_widgets(self):
        """
        Creates the widgets for the Markers Display tab, including the treeview
        for zones/groups and the frame for device buttons.
        """
        main_split_frame = ttk.Frame(self, style="Markers.TFrame")
        main_split_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_split_frame.grid_columnconfigure(0, weight=0, minsize=300)
        main_split_frame.grid_columnconfigure(1, weight=1)
        main_split_frame.grid_rowconfigure(0, weight=1)
        main_split_frame.grid_rowconfigure(1, weight=0)

        tree_frame = ttk.LabelFrame(main_split_frame, text="Zones & Groups", padding=(1,1,1,1), style='Dark.TLabelframe')
        tree_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.zone_group_tree = ttk.Treeview(tree_frame, show="tree", style="Markers.Inner.Treeview")
        self.zone_group_tree.pack(fill=tk.BOTH, expand=True)

        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.zone_group_tree.yview)
        tree_scrollbar.pack(side=tk.RIGHT, fill="y")
        self.zone_group_tree.configure(yscrollcommand=tree_scrollbar.set)
        self.zone_group_tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        self.buttons_frame = ttk.LabelFrame(main_split_frame, text="Devices", padding=(1,1,1,1), style='Dark.TLabelframe')
        self.buttons_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)

        self.inner_buttons_frame = ttk.Frame(self.buttons_frame, style='Dark.TFrame')
        self.inner_buttons_frame.pack(fill=tk.BOTH, expand=True)
        self.inner_buttons_frame.grid_columnconfigure(0, weight=1)
        self.inner_buttons_frame.grid_columnconfigure(1, weight=1)

        self.control_notebook = ttk.Notebook(main_split_frame, style="Parent.TNotebook")
        self.control_notebook.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        self.span_tab_frame = ttk.Frame(self.control_notebook, style="Markers.TFrame")
        self.control_notebook.add(self.span_tab_frame, text="Span Control")
        self.span_tab_frame.grid_columnconfigure(0, weight=1)

        span_control_container = ttk.Frame(self.span_tab_frame, padding=(1,1,1,1), style="Dark.TFrame")
        span_control_container.pack(fill="both", expand=True, padx=5, pady=5)
        span_control_container.grid_rowconfigure(0, weight=1)

        for i in range(len(SPAN_OPTIONS)):
            span_control_container.grid_columnconfigure(i, weight=1)

        self.span_buttons = {}
        col = 0
        for text_key, span_hz_value in SPAN_OPTIONS.items():
            display_value = f"{span_hz_value / MHZ_TO_HZ:.3f} MHz" if span_hz_value >= MHZ_TO_HZ else f"{span_hz_value / 1000:.0f} KHz"
            button_text = f"{text_key}\n{display_value}"
            btn = ttk.Button(span_control_container, text=button_text, style="Markers.Config.Default.TButton",
                             command=lambda s=span_hz_value, t=text_key: self._on_span_button_click(s, self.span_buttons[t], t))
            self.span_buttons[text_key] = btn
            btn.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
            col += 1

        normal_span_hz = SPAN_OPTIONS["Normal"]
        normal_button_widget = self.span_buttons["Normal"]
        self._on_span_button_click(normal_span_hz, normal_button_widget, "Normal")

        self.manual_marker_tab_frame = ttk.Frame(self.control_notebook, style="Markers.TFrame")
        self.control_notebook.add(self.manual_marker_tab_frame, text="Manual Marker")
        self.manual_marker_tab_frame.grid_columnconfigure(0, weight=1)
        self.manual_marker_tab_frame.grid_columnconfigure(1, weight=1)
        self.manual_marker_tab_frame.grid_columnconfigure(2, weight=1)
        self.manual_marker_tab_frame.grid_rowconfigure(0, weight=1)

        self.manual_freq_frame = ttk.LabelFrame(self.manual_marker_tab_frame, text="Manual Frequency Control", padding=(1,1,1,1), style="Dark.TLabelframe")
        self.manual_freq_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.manual_freq_frame.grid_columnconfigure(0, weight=1)
        self.manual_freq_frame.grid_rowconfigure(0, weight=0)
        self.manual_freq_frame.grid_rowconfigure(1, weight=0)

        self.manual_freq_entry = ttk.Entry(self.manual_freq_frame, textvariable=self.manual_freq_entry_var, width=20, style="Markers.TEntry")
        self.manual_freq_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.poke_button = ttk.Button(self.manual_freq_frame, text="POKE", style="LargePreset.TButton", command=self._on_poke_button_toggle)
        self.poke_button.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.selected_info_frame = ttk.LabelFrame(self.manual_marker_tab_frame, text="Selected Device Info", padding=(1,1,1,1), style="Dark.TLabelframe")
        self.selected_info_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.selected_info_frame.grid_columnconfigure(0, weight=1)
        self.selected_info_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(self.selected_info_frame, text="Name:", style="Markers.TLabel").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.current_name_label = ttk.Label(self.selected_info_frame, textvariable=self.current_displayed_device_name_var, style="Markers.TLabel")
        self.current_name_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(self.selected_info_frame, text="Type:", style="Markers.TLabel").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.current_device_label = ttk.Label(self.selected_info_frame, textvariable=self.current_displayed_device_type_var, style="Markers.TLabel")
        self.current_device_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        self.current_settings_frame = ttk.LabelFrame(self.manual_marker_tab_frame, text="Current Instrument Settings", padding=(1,1,1,1), style="Dark.TLabelframe")
        self.current_settings_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        self.current_settings_frame.grid_columnconfigure(0, weight=1)
        self.current_settings_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(self.current_settings_frame, text="Frequency (MHz):", style="Markers.TLabel").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.current_freq_label = ttk.Label(self.current_settings_frame, textvariable=self.current_displayed_center_freq_var, style="Markers.TLabel")
        self.current_freq_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(self.current_settings_frame, text="Span:", style="Markers.TLabel").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.current_span_label = ttk.Label(self.current_settings_frame, textvariable=self.current_span_var, style="Markers.TLabel")
        self.current_span_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(self.current_settings_frame, text="Trace Modes:", style="Markers.TLabel").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.current_trace_modes_label = ttk.Label(self.current_settings_frame, textvariable=self.current_trace_modes_var, style="Markers.TLabel")
        self.current_trace_modes_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(self.current_settings_frame, text="RBW:", style="Markers.TLabel").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.current_rbw_label = ttk.Label(self.current_settings_frame, textvariable=self.current_rbw_var, style="Markers.TLabel")
        self.current_rbw_label.grid(row=3, column=1, sticky="w", padx=5, pady=2)

        self.trace_mode_tab_frame = ttk.Frame(self.control_notebook, style="Markers.TFrame")
        self.control_notebook.add(self.trace_mode_tab_frame, text="Trace Mode Control")
        self.trace_mode_tab_frame.grid_columnconfigure(0, weight=1)

        trace_mode_control_container = ttk.Frame(self.trace_mode_tab_frame, padding=(1,1,1,1), style="Dark.TFrame")
        trace_mode_control_container.pack(fill="both", expand=True, padx=5, pady=5)
        trace_mode_control_container.grid_rowconfigure(0, weight=1)
        trace_mode_control_container.grid_columnconfigure(0, weight=1)
        trace_mode_control_container.grid_columnconfigure(1, weight=1)
        trace_mode_control_container.grid_columnconfigure(2, weight=1)

        btn_live = ttk.Button(trace_mode_control_container, text="Live", style="Markers.Config.Default.TButton", command=lambda: self._on_trace_mode_button_click("Live"))
        btn_max_hold = ttk.Button(trace_mode_control_container, text="Max Hold", style="Markers.Config.Default.TButton", command=lambda: self._on_trace_mode_button_click("Max Hold"))
        btn_min_hold = ttk.Button(trace_mode_control_container, text="Min Hold", style="Markers.Config.Default.TButton", command=lambda: self._on_trace_mode_button_click("Min Hold"))

        self.trace_mode_buttons["Live"] = {"button": btn_live, "var": self.live_mode_var}
        self.trace_mode_buttons["Max Hold"] = {"button": btn_max_hold, "var": self.max_hold_mode_var}
        self.trace_mode_buttons["Min Hold"] = {"button": btn_min_hold, "var": self.min_hold_mode_var}

        btn_live.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
        btn_max_hold.grid(row=0, column=1, padx=2, pady=2, sticky="nsew")
        btn_min_hold.grid(row=0, column=2, padx=2, pady=2, sticky="nsew")
        self._update_trace_mode_button_styles()

        self.rbw_tab_frame = ttk.Frame(self.control_notebook, style="Markers.TFrame")
        self.control_notebook.add(self.rbw_tab_frame, text="Resolution Bandwidth")
        self.rbw_tab_frame.grid_columnconfigure(0, weight=1)

        rbw_control_container = ttk.Frame(self.rbw_tab_frame, padding=(1,1,1,1), style="Dark.TFrame")
        rbw_control_container.pack(fill="both", expand=True, padx=5, pady=5)
        rbw_control_container.grid_rowconfigure(0, weight=1)

        for i in range(len(RBW_OPTIONS)):
            rbw_control_container.grid_columnconfigure(i, weight=1)

        self.rbw_buttons = {}
        col = 0
        for text_key, rbw_hz_value in RBW_OPTIONS.items():
            btn = ttk.Button(rbw_control_container, text=text_key, style="Markers.Config.Default.TButton",
                             command=lambda r=rbw_hz_value, t=text_key: self._on_rbw_button_click(r, self.rbw_buttons[t], t))
            self.rbw_buttons[text_key] = btn
            btn.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
            col += 1

        default_rbw_key = "1 MHz"
        if default_rbw_key in self.rbw_buttons:
            self._on_rbw_button_click(RBW_OPTIONS[default_rbw_key], self.rbw_buttons[default_rbw_key], default_rbw_key)

        self._set_mode_device_selection()
        self._populate_zone_group_tree()
        self._populate_device_buttons([])

    def _set_mode_poke(self):
        self.poke_mode_active.set(True)
        self.poke_button.config(style="SelectedPreset.Orange.TButton")
        self._set_widget_state(self.manual_freq_entry, "normal")
        self.current_selected_device_button = None
        self.selected_device_unique_id = None
        self.current_selected_device_data = None
        self._reset_device_button_styles(exclude_button=None)
        self._update_current_settings_display()

    def _set_mode_device_selection(self):
        self.poke_mode_active.set(False)
        self.poke_button.config(style="LargePreset.TButton")
        self._set_widget_state(self.manual_freq_entry, "disabled")
        if self.selected_device_unique_id and self.current_selected_device_data:
            self._populate_device_buttons(self._current_displayed_devices if hasattr(self, '_current_displayed_devices') else [])
        else:
            self._reset_device_button_styles(exclude_button=None)
        self._update_current_settings_display()

    def _on_poke_button_toggle(self):
        if self.poke_mode_active.get():
            self._set_mode_device_selection()
        else:
            self._set_mode_poke()
            self._on_poke_action()

    def _on_poke_action(self):
        current_function = inspect.currentframe().f_code.co_name
        if not self.poke_mode_active.get():
            return
        manual_freq_str = self.manual_freq_entry_var.get().strip()
        if not manual_freq_str:
            console_log("⚠️ Warning: Please enter a frequency in the manual control box before POKING.", function=current_function)
            return
        try:
            manual_freq_mhz = float(manual_freq_str)
            freq_hz = manual_freq_mhz * MHZ_TO_HZ
        except ValueError:
            console_log("❌ Error: Invalid frequency entered. Please enter a numerical value in MHz for POKE.", function=current_function)
            return
        console_log(f"\nPOKE: Setting instrument frequency to {manual_freq_mhz:.3f} MHz (Manual Input)...", function=current_function)
        
        if self.app_instance and hasattr(self.app_instance, 'inst') and self.app_instance.inst:
            inst = self.app_instance.inst
            original_live_mode = self.live_mode_var.get()
            original_max_hold_mode = self.max_hold_mode_var.get()
            original_min_hold_mode = self.min_hold_mode_var.get()
            if original_max_hold_mode or original_min_hold_mode:
                blank_hold_traces_logic(inst, console_log)
            set_frequency_logic(inst, freq_hz, console_log)
            set_trace_modes_logic(inst, original_live_mode, original_max_hold_mode, original_min_hold_mode, console_log)
            self.current_displayed_center_freq_var.set(f"{manual_freq_mhz:.3f}")
            self.current_displayed_device_name_var.set(f"POKE: {manual_freq_mhz:.3f}")
            self.current_displayed_device_type_var.set("N/A")
            self._update_current_settings_display()
        else:
            console_log("⚠️ Warning: Cannot POKE frequency: Instrument not connected.", function=current_function)

    def _set_widget_state(self, widget, state):
        for child in widget.winfo_children():
            try:
                child.config(state=state)
            except tk.TclError:
                pass
            if child.winfo_children():
                self._set_widget_state(child, state)

    def _populate_zone_group_tree(self):
        self.zone_group_tree.delete(*self.zone_group_tree.get_children())
        nested_grouped_data = {}
        for row in self.rows:
            zone = row.get('ZONE', 'Uncategorized Zone').strip()
            group = row.get('GROUP', '').strip()
            if zone not in nested_grouped_data:
                nested_grouped_data[zone] = {}
            group_key = group if group else "__NO_GROUP__"
            if group_key not in nested_grouped_data[zone]:
                nested_grouped_data[zone][group_key] = []
            nested_grouped_data[zone][group_key].append(row)
        for zone_name in sorted(nested_grouped_data.keys()):
            zone_id = self.zone_group_tree.insert("", "end", text=zone_name, open=True, tags=('zone',))
            for group_key in sorted(nested_grouped_data[zone_name].keys()):
                if group_key != "__NO_GROUP__":
                    self.zone_group_tree.insert(zone_id, "end", text=group_key, open=True, tags=('group',))

    def _on_tree_select(self, event):
        selected_items = self.zone_group_tree.selection()
        if self.poke_mode_active.get():
            self._set_mode_device_selection()
        selected_rows_data = []
        if selected_items:
            for item_id in selected_items:
                item_tags = self.zone_group_tree.item(item_id, 'tags')
                if 'zone' in item_tags:
                    zone_name = self.zone_group_tree.item(item_id, 'text')
                    for row in self.rows:
                        if row.get('ZONE', '').strip() == zone_name:
                            selected_rows_data.append(row)
                elif 'group' in item_tags:
                    group_name = self.zone_group_tree.item(item_id, 'text')
                    parent_id = self.zone_group_tree.parent(item_id)
                    zone_name = self.zone_group_tree.item(parent_id, 'text')
                    for row in self.rows:
                        if row.get('ZONE', '').strip() == zone_name and row.get('GROUP', '').strip() == group_name:
                            selected_rows_data.append(row)
        if self.selected_device_unique_id:
            is_prev_selected_device_still_present = False
            for device_data in selected_rows_data:
                unique_device_id_candidate = f"{device_data.get('ZONE', '')}-{device_data.get('GROUP', '')}-{device_data.get('DEVICE', '')}-{device_data.get('NAME', '')}-{device_data.get('FREQ', '')}"
                if unique_device_id_candidate == self.selected_device_unique_id:
                    is_prev_selected_device_still_present = True
                    break
            if not is_prev_selected_device_still_present:
                if self.current_selected_device_button:
                    self.current_selected_device_button.config(style="LargePreset.TButton")
                self.current_selected_device_button = None
                self.selected_device_unique_id = None
                self.current_selected_device_data = None
        else:
            if self.current_selected_device_button:
                self.current_selected_device_button.config(style="LargePreset.TButton")
                self.current_selected_device_button = None
            self.current_selected_device_data = None
        self._populate_device_buttons(selected_rows_data)
        self._update_current_settings_display()

    def _populate_device_buttons(self, devices_to_display):
        for widget in self.inner_buttons_frame.winfo_children():
            widget.destroy()
        if not devices_to_display:
            ttk.Label(self.inner_buttons_frame, text="Select a zone or group from the left to display devices.",
                      background="#1e1e1e", foreground="#cccccc", style='Markers.TLabel').grid(row=0, column=0, columnspan=2, padx=5, pady=5)
            self.inner_buttons_frame.update_idletasks()
            return
        num_devices = len(devices_to_display)
        num_columns = 3 if num_devices > 20 else 2
        current_max_col = 0
        if self.inner_buttons_frame.grid_size():
            current_max_col = self.inner_buttons_frame.grid_size()[0]
        for i in range(current_max_col):
            self.inner_buttons_frame.grid_columnconfigure(i, weight=0)
        for i in range(num_columns):
            self.inner_buttons_frame.grid_columnconfigure(i, weight=1)
        row_idx = 0
        col_idx = 0
        self._current_displayed_devices = devices_to_display
        for i, device_data in enumerate(devices_to_display):
            name = device_data.get('NAME', '').strip()
            device = device_data.get('DEVICE', '').strip()
            freq_mhz = device_data.get('FREQ')
            if freq_mhz is not None:
                try:
                    unique_device_id = f"{device_data.get('ZONE', '')}-{device_data.get('GROUP', '')}-{device_data.get('DEVICE', '')}-{device_data.get('NAME', '')}-{freq_mhz}"
                    display_name = name if name else "N/A Name"
                    display_device = device if device and device.lower() != "none - none - n/a" else "N/A Device"
                    display_freq_mhz = int(float(freq_mhz)) if float(freq_mhz) == int(float(freq_mhz)) else f"{float(freq_mhz):.3f}"
                    button_text = f"{display_name}\n{display_device}\n{display_freq_mhz} MHz"
                    btn = ttk.Button(self.inner_buttons_frame, text=button_text, style="LargePreset.TButton",
                                     command=lambda d=device_data, btn_w=None: self._on_device_button_click(d, btn_w))
                    btn.configure(command=lambda d=device_data, u_id=unique_device_id, b_w=btn: self._on_device_button_click(d, b_w))
                    button_style = "LargePreset.TButton"
                    is_currently_scanned = False
                    if self.app_instance and hasattr(self.app_instance, 'scanning_active_var') and self.app_instance.scanning_active_var.get():
                        if hasattr(self.app_instance, 'current_scanned_device_unique_id') and self.app_instance.current_scanned_device_unique_id.get() == unique_device_id:
                            is_currently_scanned = True
                    if is_currently_scanned:
                        button_style = "ActiveScan.TButton"
                    elif unique_device_id == self.selected_device_unique_id:
                        button_style = "SelectedPreset.Orange.TButton"
                        self.current_selected_device_button = btn
                    btn.config(style=button_style)
                    btn.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="nsew")
                    col_idx += 1
                    if col_idx >= num_columns:
                        col_idx = 0
                        row_idx += 1
                except ValueError:
                    pass
            else:
                pass
        for r in range(row_idx + 1):
            self.inner_buttons_frame.grid_rowconfigure(r, weight=1)
        self.inner_buttons_frame.update_idletasks()

    def _reset_span_button_styles(self, exclude_button=None):
        for btn in self.span_buttons.values():
            if btn != exclude_button:
                btn.config(style="Markers.Config.Default.TButton")
        self.last_selected_span_button = exclude_button

    def _reset_rbw_button_styles(self, exclude_button=None):
        for btn in self.rbw_buttons.values():
            if btn != exclude_button:
                btn.config(style="Markers.Config.Default.TButton")
        self.last_selected_rbw_button = exclude_button

    def _reset_device_button_styles(self, exclude_button=None):
        for widget in self.inner_buttons_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.config(style="LargePreset.TButton")

    def _on_device_button_click(self, device_data, clicked_button_widget):
        current_function = inspect.currentframe().f_code.co_name
        if self.poke_mode_active.get():
            self._set_mode_device_selection()
        freq_hz = float(device_data.get('FREQ')) * MHZ_TO_HZ
        name = device_data.get('NAME', '').strip()
        device_type = device_data.get('DEVICE', '').strip()
        unique_device_id = f"{device_data.get('ZONE', '')}-{device_data.get('GROUP', '')}-{device_data.get('DEVICE', '')}-{device_data.get('NAME', '')}-{device_data.get('FREQ')}"
        display_freq_mhz = int(freq_hz / MHZ_TO_HZ) if (freq_hz / MHZ_TO_HZ) == int(freq_hz / MHZ_TO_HZ) else f"{freq_hz / MHZ_TO_HZ:.3f}"
        console_log(f"\nSetting instrument to '{name}' at {display_freq_mhz} MHz...", function=current_function)
        
        self._reset_device_button_styles(exclude_button=clicked_button_widget)
        clicked_button_widget.config(style="SelectedPreset.Orange.TButton")
        self.current_selected_device_button = clicked_button_widget
        self.selected_device_unique_id = unique_device_id
        self.current_selected_device_data = device_data
        
        self.current_displayed_device_name_var.set(name if name else "N/A")
        self.current_displayed_device_type_var.set(device_type if device_type else "N/A")
        self.current_displayed_center_freq_var.set(display_freq_mhz)
        self.control_notebook.select(self.span_tab_frame)
        
        if self.app_instance and hasattr(self.app_instance, 'inst') and self.app_instance.inst:
            inst = self.app_instance.inst
            original_live_mode = self.live_mode_var.get()
            original_max_hold_mode = self.max_hold_mode_var.get()
            original_min_hold_mode = self.min_hold_mode_var.get()
            if original_max_hold_mode or original_min_hold_mode:
                blank_hold_traces_logic(inst, console_log)
            set_frequency_logic(inst, freq_hz, console_log)
            span_to_use_hz = self.current_span_hz if self.current_span_hz is not None else float(self.app_instance.desired_default_focus_width_var.get()) * MHZ_TO_HZ
            set_span_logic(inst, span_to_use_hz, console_log)
            set_marker_logic(inst, freq_hz, name, console_log)
            set_trace_modes_logic(inst, original_live_mode, original_max_hold_mode, original_min_hold_mode, console_log)
            self._update_current_settings_display()
        else:
            console_log("⚠️ Warning: Cannot set focus frequency: Instrument not connected.", function=current_function)

    def _on_span_button_click(self, span_hz, button_widget, button_text_key):
        current_function = inspect.currentframe().f_code.co_name
        console_log(f"Setting span to {span_hz / MHZ_TO_HZ:.3f} MHz...", function=current_function)
        self._reset_span_button_styles(exclude_button=button_widget)
        self.current_span_hz = span_hz
        button_widget.config(style="Markers.Config.Selected.TButton")
        self.last_selected_span_button = button_widget
        
        if self.app_instance and hasattr(self.app_instance, 'inst') and self.app_instance.inst:
            inst = self.app_instance.inst
            original_live_mode = self.live_mode_var.get()
            original_max_hold_mode = self.max_hold_mode_var.get()
            original_min_hold_mode = self.min_hold_mode_var.get()
            if original_max_hold_mode or original_min_hold_mode:
                blank_hold_traces_logic(inst, console_log)
            set_span_logic(inst, span_hz, console_log)
            if self.current_selected_device_data:
                try:
                    center_freq_to_use = float(self.current_selected_device_data.get('FREQ')) * MHZ_TO_HZ
                    set_frequency_logic(inst, center_freq_to_use, console_log)
                except (ValueError, TypeError):
                    pass
            set_trace_modes_logic(inst, original_live_mode, original_max_hold_mode, original_min_hold_mode, console_log)
            self._update_current_settings_display()
        else:
            console_log("⚠️ Warning: Cannot set span: Instrument not connected.", function=current_function)

    def _on_rbw_button_click(self, rbw_hz, button_widget, button_text_key):
        current_function = inspect.currentframe().f_code.co_name
        console_log(f"Setting RBW to {button_text_key}...", function=current_function)
        self._reset_rbw_button_styles(exclude_button=button_widget)
        self.current_rbw_var.set(button_text_key)
        button_widget.config(style="Markers.Config.Selected.TButton")
        self.last_selected_rbw_button = button_widget
        
        if self.app_instance and hasattr(self.app_instance, 'inst') and self.app_instance.inst:
            inst = self.app_instance.inst
            original_live_mode = self.live_mode_var.get()
            original_max_hold_mode = self.max_hold_mode_var.get()
            original_min_hold_mode = self.min_hold_mode_var.get()
            if original_max_hold_mode or original_min_hold_mode:
                blank_hold_traces_logic(inst, console_log)
            set_rbw_logic(inst, rbw_hz, console_log)
            set_trace_modes_logic(inst, original_live_mode, original_max_hold_mode, original_min_hold_mode, console_log)
            self._update_current_settings_display()
        else:
            console_log("⚠️ Warning: Cannot set RBW: Instrument not connected.", function=current_function)

    def _on_trace_mode_button_click(self, mode_name):
        if mode_name == "Live":
            self.live_mode_var.set(not self.live_mode_var.get())
        elif mode_name == "Max Hold":
            self.max_hold_mode_var.set(not self.max_hold_mode_var.get())
        elif mode_name == "Min Hold":
            self.min_hold_mode_var.set(not self.min_hold_mode_var.get())
        self._update_trace_mode_button_styles()
        
        if self.app_instance and hasattr(self.app_instance, 'inst') and self.app_instance.inst:
            inst = self.app_instance.inst
            set_trace_modes_logic(inst, self.live_mode_var.get(), self.max_hold_mode_var.get(), self.min_hold_mode_var.get(), console_log)
            self._update_current_settings_display()
        else:
            console_log("⚠️ Warning: Cannot set trace mode: Instrument not connected.", function=inspect.currentframe().f_code.co_name)

    def _update_trace_mode_button_styles(self):
        for mode_name, data in self.trace_mode_buttons.items():
            button = data["button"]
            var = data["var"]
            if var.get():
                button.config(style="Markers.Config.Selected.TButton")
            else:
                button.config(style="Markers.Config.Default.TButton")

    def _update_current_settings_display(self):
        display_span = "N/A"
        if self.current_span_hz is not None:
            if self.current_span_hz == 0.0:
                display_span = "Full Span"
            elif self.current_span_hz >= MHZ_TO_HZ:
                display_span = f"{self.current_span_hz / MHZ_TO_HZ:.3f} MHz"
            else:
                display_span = f"{self.current_span_hz / 1000:.0f} KHz"
        self.current_span_var.set(display_span)
        active_modes = []
        if self.live_mode_var.get(): active_modes.append("Live")
        if self.max_hold_mode_var.get(): active_modes.append("Max Hold")
        if self.min_hold_mode_var.get(): active_modes.append("Min Hold")
        self.current_trace_modes_var.set(', '.join(active_modes) if active_modes else "None Active")
        if self.poke_mode_active.get():
            try:
                manual_freq_mhz = float(self.manual_freq_entry_var.get())
                self.current_displayed_device_name_var.set(f"POKE: {manual_freq_mhz:.3f}")
                self.current_displayed_center_freq_var.set(f"{manual_freq_mhz:.3f}")
            except ValueError:
                self.current_displayed_device_name_var.set("POKE: Invalid Freq")
                self.current_displayed_center_freq_var.set("Invalid Freq")
            self.current_displayed_device_type_var.set("N/A")
        elif self.current_selected_device_data:
            name = self.current_selected_device_data.get('NAME', '').strip()
            device_type = self.current_selected_device_data.get('DEVICE', '').strip()
            freq_mhz = self.current_selected_device_data.get('FREQ')
            display_name = name if name else "N/A"
            display_device = device_type if device_type else "N/A"
            display_freq = "N/A"
            if freq_mhz is not None:
                try:
                    display_freq = int(float(freq_mhz)) if float(freq_mhz) == int(float(freq_mhz)) else f"{float(freq_mhz):.3f}"
                except ValueError:
                    display_freq = "Invalid Freq"
            self.current_displayed_device_name_var.set(display_name)
            self.current_displayed_device_type_var.set(display_device)
            self.current_displayed_center_freq_var.set(display_freq)
        else:
            self.current_displayed_device_name_var.set("N/A")
            self.current_displayed_device_type_var.set("N/A")
            self.current_displayed_center_freq_var.set("N/A")

    def update_marker_data(self, new_headers, new_rows):
        self.headers = new_headers
        self.rows = new_rows
        self._populate_zone_group_tree()
        first_item = self.zone_group_tree.get_children()
        if first_item:
            self.zone_group_tree.selection_set(first_item[0])
            self.zone_group_tree.focus(first_item[0])
            self._on_tree_select(None)
        else:
            self._populate_device_buttons([])
            self.current_selected_device_button = None
            self.selected_device_unique_id = None
            self.current_selected_device_data = None
            self._update_current_settings_display()

    def load_markers_from_file(self):
        markers_file_path = None
        if self.app_instance and hasattr(self.app_instance, 'MARKERS_FILE_PATH'):
            markers_file_path = self.app_instance.MARKERS_FILE_PATH
        if markers_file_path and os.path.exists(markers_file_path):
            try:
                headers = []
                rows = []
                with open(markers_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    headers = reader.fieldnames
                    for row_data in reader:
                        rows.append(row_data)
                if headers and rows:
                    self.update_marker_data(headers, rows)
                else:
                    self.update_marker_data([], [])
            except Exception:
                self.update_marker_data([], [])
        else:
            self.update_marker_data([], [])
        self._update_current_settings_display()

    def _on_tab_selected(self, event):
        self.load_markers_from_file()
        self._update_current_settings_display()

    def update_device_button_styles(self):
        if hasattr(self, '_current_displayed_devices'):
            self._reset_device_button_styles(exclude_button=None)
            self._populate_device_buttons(self._current_displayed_devices)
        else:
            if self.zone_group_tree.selection():
                self._on_tree_select(None)
            else:
                self._populate_device_buttons([])
