# tabs/Markers/controls/tab_markers_child_bottom_controls.py
#
# This file defines the ControlsFrame, a reusable ttk.Frame containing the
# Span, RBW, Trace Modes, and Poke Frequency controls in a notebook.
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
# Version 20250818.145024.1

current_version = "20250818.145024.1"
current_version_hash = (20250818 * 145024 * 1)

import tkinter as tk
from tkinter import ttk
import os
import inspect

from tabs.Markers.controls.utils_showtime_controls import (
    on_span_button_click, on_rbw_button_click, on_trace_button_click, on_poke_action,
    format_hz, sync_trace_modes, _update_control_styles, SPAN_OPTIONS, RBW_OPTIONS
)

from tabs.Markers.controls.utils_showtime_zone_zoom import (
    set_span_to_zone, set_span_to_group, set_span_to_device, set_span_to_all_markers
)


class ControlsFrame(ttk.Frame):
    def __init__(self, parent, app_instance):
        super().__init__(parent, style='TFrame')
        self.app_instance = app_instance
        self.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)

        # --- Initialize Tkinter Control Variables ---
        self.span_var = tk.StringVar(value="1000000")
        self.rbw_var = tk.StringVar(value="100000")
        self.follow_zone_span_var = tk.BooleanVar(value=True)
        self.trace_live_mode = tk.BooleanVar(value=True)
        self.trace_max_hold_mode = tk.BooleanVar(value=True)
        self.trace_min_hold_mode = tk.BooleanVar(value=True)
        self.poke_freq_var = tk.StringVar()

        # --- NEW: StringVars for PEAKS tab labels ---
        self.peaks_label_left_var = tk.StringVar(value="All Markers")
        self.peaks_label_center_var = tk.StringVar(value="Start: N/A")
        self.peaks_label_right_var = tk.StringVar(value="Stop: N/A (0 Markers)")

        self.span_buttons = {}
        self.rbw_buttons = {}
        self.trace_buttons = {}
        self.peaks_buttons = {}

        self._create_controls_notebook()

        self.after(100, lambda: sync_trace_modes(self))
        self.after(110, lambda: _update_control_styles(self))

    def _create_controls_notebook(self):
        controls_notebook = ttk.Notebook(self, style='Markers.Child.TNotebook')
        controls_notebook.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # --- Span, RBW, Trace, TRACES, Poke Tabs (Code is unchanged, omitted for brevity) ---
        # --- Span Tab ---
        span_tab = ttk.Frame(controls_notebook, style='TFrame', padding=5)
        controls_notebook.add(span_tab, text="Span")
        follow_btn = ttk.Button(span_tab, text="Follow Zone\n(Active)", style='ControlButton.Inactive.TButton', command=lambda: on_span_button_click(self, 'Follow'))
        follow_btn.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        self.span_buttons['Follow'] = follow_btn
        for i, (name, span_hz) in enumerate(SPAN_OPTIONS.items()):
            btn_text = f"{name}\n({format_hz(span_hz)})"
            btn = ttk.Button(span_tab, text=btn_text, style='ControlButton.Inactive.TButton', command=lambda s=span_hz: on_span_button_click(self, s))
            btn.grid(row=0, column=i + 1, padx=2, pady=2, sticky="ew")
            self.span_buttons[str(span_hz)] = btn
        for i in range(len(SPAN_OPTIONS) + 1):
            span_tab.grid_columnconfigure(i, weight=1)

        # --- RBW Tab ---
        rbw_tab = ttk.Frame(controls_notebook, style='TFrame', padding=5)
        controls_notebook.add(rbw_tab, text="RBW")
        for i, (name, rbw_hz) in enumerate(RBW_OPTIONS.items()):
            btn_text = f"{name}\n({format_hz(rbw_hz)})"
            btn = ttk.Button(rbw_tab, text=btn_text, style='ControlButton.Inactive.TButton', command=lambda r=rbw_hz: on_rbw_button_click(self, r))
            btn.grid(row=0, column=i, padx=2, pady=2, sticky="ew")
            self.rbw_buttons[str(rbw_hz)] = btn
            rbw_tab.grid_columnconfigure(i, weight=1)

        # --- Trace Tab ---
        trace_tab = ttk.Frame(controls_notebook, style='TFrame', padding=5)
        controls_notebook.add(trace_tab, text="Trace Modes")
        live_btn = ttk.Button(trace_tab, text="Live\nTrace", style='ControlButton.Inactive.TButton', command=lambda: on_trace_button_click(self, self.trace_live_mode))
        live_btn.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        self.trace_buttons['Live'] = live_btn
        max_btn = ttk.Button(trace_tab, text="Max Hold\nTrace", style='ControlButton.Inactive.TButton', command=lambda: on_trace_button_click(self, self.trace_max_hold_mode))
        max_btn.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        self.trace_buttons['Max Hold'] = max_btn
        min_btn = ttk.Button(trace_tab, text="Min Hold\nTrace", style='ControlButton.Inactive.TButton', command=lambda: on_trace_button_click(self, self.trace_min_hold_mode))
        min_btn.grid(row=0, column=2, padx=2, pady=2, sticky="ew")
        self.trace_buttons['Min Hold'] = min_btn
        for i in range(3):
            trace_tab.grid_columnconfigure(i, weight=1)

        # --- PEAKS Tab (UPDATED) ---
        peaks_tab = ttk.Frame(controls_notebook, style='TFrame', padding=5)
        controls_notebook.add(peaks_tab, text="PEAKS")
        peaks_tab.columnconfigure((0, 1, 2, 3), weight=1)

        # Labels now use the new StringVars
        ttk.Label(peaks_tab, textvariable=self.peaks_label_left_var, anchor="w").grid(row=0, column=0, columnspan=2, pady=2, padx=2, sticky="w")
        ttk.Label(peaks_tab, textvariable=self.peaks_label_center_var, anchor="e").grid(row=0, column=2, pady=2, padx=2, sticky="e")
        ttk.Label(peaks_tab, textvariable=self.peaks_label_right_var, anchor="e").grid(row=0, column=3, pady=2, padx=2, sticky="e")

        # Buttons with commands and storing references
        btn_zone = ttk.Button(peaks_tab, text="Set Span to Zone", style='ControlButton.Inactive.TButton', command=self._on_set_span_to_zone_click)
        btn_zone.grid(row=1, column=0, padx=2, pady=2, sticky="ew")
        self.peaks_buttons['Zone'] = btn_zone

        btn_group = ttk.Button(peaks_tab, text="Set Span to Group", style='ControlButton.Inactive.TButton', command=self._on_set_span_to_group_click)
        btn_group.grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        self.peaks_buttons['Group'] = btn_group

        btn_device = ttk.Button(peaks_tab, text="Set Span to Device", style='ControlButton.Inactive.TButton', command=self._on_set_span_to_device_click)
        btn_device.grid(row=1, column=2, padx=2, pady=2, sticky="ew")
        self.peaks_buttons['Device'] = btn_device
        
        btn_all = ttk.Button(peaks_tab, text="Set Span to All Markers", style='ControlButton.Inactive.TButton', command=self._on_set_span_to_all_markers_click)
        btn_all.grid(row=1, column=3, padx=2, pady=2, sticky="ew")
        self.peaks_buttons['All'] = btn_all

        # --- TRACES Tab ---
        traces_tab = ttk.Frame(controls_notebook, style='TFrame', padding=5)
        controls_notebook.add(traces_tab, text="TRACES")
        traces_tab.columnconfigure((0, 1, 2), weight=1)
        ttk.Button(traces_tab, text="Get View, Min and Max", style='ControlButton.Inactive.TButton').grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        ttk.Button(traces_tab, text="Get view", style='ControlButton.Inactive.TButton').grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        ttk.Button(traces_tab, text="BEG", style='ControlButton.Inactive.TButton').grid(row=0, column=2, padx=2, pady=2, sticky="ew")

        # --- Poke Tab ---
        poke_tab = ttk.Frame(controls_notebook, style='TFrame', padding=5)
        controls_notebook.add(poke_tab, text="Poke Frequency")
        poke_tab.columnconfigure(0, weight=1)
        poke_entry = ttk.Entry(poke_tab, textvariable=self.poke_freq_var)
        poke_entry.pack(side='left', fill='x', expand=True, padx=2, pady=2)
        poke_btn = ttk.Button(poke_tab, text="Poke", style='ControlButton.Inactive.TButton', command=lambda: on_poke_action(self))
        poke_btn.pack(side='left', padx=2, pady=2)

    def _get_zgd_frame(self):
        """Helper to safely get the ZoneGroupsDevicesFrame instance."""
        try:
            return self.app_instance.tabs_parent.tab_content_frames['Markers'].showtime_tab.zgd_frame
        except (AttributeError, KeyError):
            self.console_print_func("❌ Error: Could not find the main markers display frame.", "ERROR")
            return None

    def _on_set_span_to_zone_click(self):
        zgd_frame = self._get_zgd_frame()
        if not zgd_frame or not zgd_frame.selected_zone:
            self.console_print_func("⚠️ No zone selected.", "WARNING")
            return
        
        devices = zgd_frame._get_all_devices_in_zone(zgd_frame.structured_data, zgd_frame.selected_zone)
        freqs = [d.get('CENTER') for d in devices if d.get('CENTER')]
        
        if not freqs:
            self.console_print_func("⚠️ Selected zone has no markers with frequencies.", "WARNING")
            return
            
        set_span_to_zone(self, ZoneName=zgd_frame.selected_zone, NumberOfMarkers=len(freqs),
                         StartFreq=min(freqs), StopFreq=max(freqs), selected=True)

    def _on_set_span_to_group_click(self):
        zgd_frame = self._get_zgd_frame()
        if not zgd_frame or not zgd_frame.selected_group:
            self.console_print_func("⚠️ No group selected.", "WARNING")
            return
            
        devices = zgd_frame.structured_data.get(zgd_frame.selected_zone, {}).get(zgd_frame.selected_group, [])
        freqs = [d.get('CENTER') for d in devices if d.get('CENTER')]

        if not freqs:
            self.console_print_func("⚠️ Selected group has no markers with frequencies.", "WARNING")
            return
            
        set_span_to_group(self, GroupName=zgd_frame.selected_group, NumberOfMarkers=len(freqs),
                          StartFreq=min(freqs), StopFreq=max(freqs))

    def _on_set_span_to_device_click(self):
        zgd_frame = self._get_zgd_frame()
        if not zgd_frame or not hasattr(zgd_frame, 'selected_device_info') or not zgd_frame.selected_device_info:
            self.console_print_func("⚠️ No device selected.", "WARNING")
            return
            
        device_info = zgd_frame.selected_device_info
        device_name = device_info.get('NAME', 'N/A')
        center_freq = device_info.get('CENTER')

        if not center_freq:
            self.console_print_func("⚠️ Selected device has no frequency.", "WARNING")
            return
            
        set_span_to_device(self, DeviceName=device_name, CenterFreq=center_freq)

    def _on_set_span_to_all_markers_click(self):
        zgd_frame = self._get_zgd_frame()
        if not zgd_frame:
            return
            
        all_devices = zgd_frame._get_all_devices_in_zone(zgd_frame.structured_data, zone_name=None)
        freqs = [d.get('CENTER') for d in all_devices if d.get('CENTER')]

        if not freqs:
            self.console_print_func("⚠️ No markers loaded.", "WARNING")
            return

        set_span_to_all_markers(self, NumberOfMarkers=len(freqs), StartFreq=min(freqs),
                                StopFreq=max(freqs), selected=True)

    def console_print_func(self, message, level="INFO"):
        # Safely prints a message to the main application console.
        if hasattr(self.app_instance, 'console_tab') and hasattr(self.app_instance.console_tab, 'console_log'):
             self.app_instance.console_tab.console_log(message, level)
        else:
             print(f"[{level.upper()}] {message}")