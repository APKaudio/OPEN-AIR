# tabs/Markers/tab_markers_child_controls.py
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
# Version 20250814.172000.1

current_version = "20250814.172000.1"
current_version_hash = (20250814 * 172000 * 1)

import tkinter as tk
from tkinter import ttk

from .utils_showtime_controls import (
    on_span_button_click, on_rbw_button_click, on_trace_button_click, on_poke_action, 
    format_hz, sync_trace_modes, SPAN_OPTIONS, RBW_OPTIONS
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
        
        self.span_buttons = {}
        self.rbw_buttons = {}
        self.trace_buttons = {}

        self._create_controls_notebook()
        
        self.after(100, lambda: sync_trace_modes(self))

    def _create_controls_notebook(self):
        controls_notebook = ttk.Notebook(self, style='Markers.Child.TNotebook')
        controls_notebook.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

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
        
        # --- Poke Tab ---
        poke_tab = ttk.Frame(controls_notebook, style='TFrame', padding=5)
        controls_notebook.add(poke_tab, text="Poke Frequency")
        poke_tab.columnconfigure(0, weight=1)
        
        poke_entry = ttk.Entry(poke_tab, textvariable=self.poke_freq_var)
        poke_entry.pack(side='left', fill='x', expand=True, padx=2, pady=2)
        
        poke_btn = ttk.Button(poke_tab, text="Poke", style='ControlButton.Inactive.TButton', command=lambda: on_poke_action(self))
        poke_btn.pack(side='left', padx=2, pady=2)

    def console_print_func(self, message, level="INFO"):
        # [A brief, one-sentence description of the function's purpose.]
        # Safely prints a message to the main application console.
        if hasattr(self.app_instance, 'console_tab') and hasattr(self.app_instance.console_tab, 'console_log'):
             self.app_instance.console_tab.console_log(message, level)
        else:
             print(f"[{level.upper()}] {message}")