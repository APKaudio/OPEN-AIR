# tabs/Instrument/tab_instrument_child_settings_traces.py
#
# This file defines the TraceSettingsTab, a Tkinter Frame for controlling a spectrum
# analyzer's trace settings.
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
# Version 20250815.105500.1
# NEW: Added YakBeg functionality for traces.

current_version = "20250815.105500.1"
current_version_hash = 20250815 * 105500 * 1

import tkinter as tk
from tkinter import ttk, scrolledtext
import inspect
import os

from display.debug_logic import debug_log
from display.console_logic import console_log
from yak.utils_yakbeg_handler import handle_trace_modes_beg, handle_trace_data_beg

class TraceSettingsTab(ttk.Frame):
    """
    A Tkinter Frame that provides a user interface for trace settings.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the TraceSettingsTab.
        """
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        self.trace_modes = ["VIEW", "WRITE", "BLANK", "MAXHOLD", "MINHOLD"]
        self.trace_vars = [
            self.app_instance.trace1_mode_var,
            self.app_instance.trace2_mode_var,
            self.app_instance.trace3_mode_var,
            self.app_instance.trace4_mode_var
        ]

        # Tkinter variables for trace data
        self.trace_data_start_freq_var = tk.DoubleVar(value=500)
        self.trace_data_stop_freq_var = tk.DoubleVar(value=1000)
        self.trace_select_var = tk.StringVar(value="1")
        self.trace_data_count_var = tk.StringVar(value="0")
        
        self.trace_modes_result_var = tk.StringVar(value="Result: N/A")
        
        self._create_widgets()

    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Trace Settings tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering _create_widgets. Creating widgets for the Trace Settings Tab. 📈",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        self.grid_columnconfigure(0, weight=1)

        # --- TRACE/MODES Frame (from YakBegTab) ---
        trace_modes_frame = ttk.LabelFrame(self, text="YakBeg - TRACE/MODES", padding=10)
        trace_modes_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        trace_modes_frame.grid_columnconfigure(0, weight=1)
        trace_modes_frame.grid_columnconfigure(1, weight=1)
        trace_modes_frame.grid_columnconfigure(2, weight=1)
        trace_modes_frame.grid_columnconfigure(3, weight=1)

        ttk.Label(trace_modes_frame, text="Trace 1 Mode:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.trace1_combo = ttk.Combobox(trace_modes_frame, textvariable=self.trace_vars[0], values=self.trace_modes, state="readonly")
        self.trace1_combo.grid(row=1, column=0, padx=5, pady=2, sticky="ew")
        ttk.Label(trace_modes_frame, text="Trace 2 Mode:").grid(row=0, column=1, padx=5, pady=2, sticky="w")
        self.trace2_combo = ttk.Combobox(trace_modes_frame, textvariable=self.trace_vars[1], values=self.trace_modes, state="readonly")
        self.trace2_combo.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        ttk.Label(trace_modes_frame, text="Trace 3 Mode:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.trace3_combo = ttk.Combobox(trace_modes_frame, textvariable=self.trace_vars[2], values=self.trace_modes, state="readonly")
        self.trace3_combo.grid(row=1, column=2, padx=5, pady=2, sticky="ew")
        ttk.Label(trace_modes_frame, text="Trace 4 Mode:").grid(row=0, column=3, padx=5, pady=2, sticky="w")
        self.trace4_combo = ttk.Combobox(trace_modes_frame, textvariable=self.trace_vars[3], values=self.trace_modes, state="readonly")
        self.trace4_combo.grid(row=1, column=3, padx=5, pady=2, sticky="ew")
        
        self.trace_modes_result_var = tk.StringVar(value="Result: N/A")
        ttk.Label(trace_modes_frame, textvariable=self.trace_modes_result_var, style="Dark.TLabel.Value").grid(row=2, column=0, columnspan=4, padx=5, pady=2, sticky="ew")
        
        ttk.Button(trace_modes_frame, text="YakBeg - TRACE/MODES", command=self._on_trace_modes_beg).grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="ew")


        # --- TRACE/DATA Frame (from YakBegTab) ---
        trace_data_frame = ttk.LabelFrame(self, text="YakBeg - TRACE/DATA", padding=10)
        trace_data_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        trace_data_frame.grid_columnconfigure(0, weight=1)
        trace_data_frame.grid_rowconfigure(2, weight=1)
        
        trace_data_controls_frame = ttk.Frame(trace_data_frame)
        trace_data_controls_frame.grid(row=0, column=0, sticky="ew")
        trace_data_controls_frame.grid_columnconfigure(0, weight=1)
        trace_data_controls_frame.grid_columnconfigure(1, weight=1)
        trace_data_controls_frame.grid_columnconfigure(2, weight=1)

        ttk.Label(trace_data_controls_frame, text="Trace #:", style="TLabel").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.trace_select_combo = ttk.Combobox(trace_data_controls_frame, textvariable=self.trace_select_var, values=["1", "2", "3", "4"], state="readonly")
        self.trace_select_combo.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.trace_select_combo.set("1")

        ttk.Label(trace_data_controls_frame, text="# of points:", style="TLabel").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(trace_data_controls_frame, textvariable=self.trace_data_count_var, style="Dark.TLabel.Value").grid(row=0, column=3, padx=5, pady=2, sticky="ew")

        ttk.Label(trace_data_controls_frame, text="Start Freq (MHz):", style="TLabel").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(trace_data_controls_frame, textvariable=self.trace_data_start_freq_var).grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(trace_data_controls_frame, text="Stop Freq (MHz):", style="TLabel").grid(row=1, column=2, padx=5, pady=2, sticky="w")
        ttk.Entry(trace_data_controls_frame, textvariable=self.trace_data_stop_freq_var).grid(row=1, column=3, padx=5, pady=2, sticky="ew")
        
        ttk.Button(trace_data_controls_frame, text="YakBeg - TRACE/DATA", command=None).grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky="ew")

        # Table to display trace data
        columns = ("Frequency (MHz)", "Value (dBm)")
        self.trace_data_tree = ttk.Treeview(trace_data_frame, columns=columns, show="headings", style='Treeview')
        self.trace_data_tree.heading("Frequency (MHz)", text="Frequency (MHz)", anchor=tk.W)
        self.trace_data_tree.heading("Value (dBm)", text="Value (dBm)", anchor=tk.W)
        self.trace_data_tree.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        vsb = ttk.Scrollbar(trace_data_frame, orient="vertical", command=self.trace_data_tree.yview)
        vsb.grid(row=1, column=1, sticky="ns")
        self.trace_data_tree.configure(yscrollcommand=vsb.set)
        
        # New button to push data to monitor
        ttk.Button(self, text="Push Trace Data to Monitor", command=None, style="Green.TButton").grid(row=2, column=0, padx=10, pady=5, sticky="ew")


    def _on_tab_selected(self, event):
        """Called when this tab is selected."""
        pass # No specific actions needed on selection
