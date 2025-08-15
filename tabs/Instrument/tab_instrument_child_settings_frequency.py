# tabs/Instrument/tab_instrument_child_settings_frequency.py
#
# This file defines the FrequencySettingsTab, a Tkinter Frame for controlling a spectrum
# analyzer's frequency-related settings.
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
# NEW: Added YakBeg functionality for frequency settings.

current_version = "20250815.105500.1"
current_version_hash = 20250815 * 105500 * 1

import tkinter as tk
from tkinter import ttk
import inspect
import os
import numpy as np # Keep import for future logic, even if not used now.

from display.debug_logic import debug_log
from display.console_logic import console_log
from yak.utils_yakbeg_handler import handle_freq_start_stop_beg, handle_freq_center_span_beg

class FrequencySettingsTab(ttk.Frame):
    """
    A Tkinter Frame that provides a user interface for frequency settings.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the FrequencySettingsTab.
        """
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        
        # Tkinter variables for frequency settings
        self.freq_start_var = tk.DoubleVar(value=500000000)
        self.freq_stop_var = tk.DoubleVar(value=1000000000)
        self.freq_center_var = tk.DoubleVar(value=750000000)
        self.freq_span_var = tk.DoubleVar(value=500000000)
        
        self._create_widgets()

    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Frequency Settings tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering _create_widgets. Creating widgets for the Frequency Settings Tab. 🎶",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Frequency Settings Frame ---
        freq_frame = ttk.LabelFrame(self, text="Frequency Settings", style='Dark.TLabelframe')
        freq_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        freq_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(freq_frame, text="Center Frequency (MHz):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.center_freq_entry = ttk.Entry(freq_frame, textvariable=self.app_instance.center_freq_mhz_var, style='TEntry')
        self.center_freq_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        # command=lambda e, app_ref=self.app_instance: set_center_frequency(app_ref, app_ref.center_freq_mhz_var.get(), self.console_print_func)
        self.center_freq_entry.bind("<FocusOut>", None) 
        
        ttk.Label(freq_frame, text="Span (MHz):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.span_freq_entry = ttk.Entry(freq_frame, textvariable=self.app_instance.span_freq_mhz_var, style='TEntry')
        self.span_freq_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        # command=lambda e, app_ref=self.app_instance: set_span_frequency(app_ref, app_ref.span_freq_mhz_var.get(), self.console_print_func)
        self.span_freq_entry.bind("<FocusOut>", None)
        
        ttk.Label(freq_frame, text="Start Frequency (MHz):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.start_freq_entry = ttk.Entry(freq_frame, textvariable=self.app_instance.start_freq_mhz_var, style='TEntry')
        self.start_freq_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        # command=lambda e, app_ref=self.app_instance: set_start_frequency(app_ref, app_ref.start_freq_mhz_var.get(), self.console_print_func)
        self.start_freq_entry.bind("<FocusOut>", None)
        
        ttk.Label(freq_frame, text="Stop Frequency (MHz):").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.stop_freq_entry = ttk.Entry(freq_frame, textvariable=self.app_instance.stop_freq_mhz_var, style='TEntry')
        self.stop_freq_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        # command=lambda e, app_ref=self.app_instance: set_stop_frequency(app_ref, app_ref.stop_freq_mhz_var.get(), self.console_print_func)
        self.stop_freq_entry.bind("<FocusOut>", None)
        
        self.get_freq_button = ttk.Button(freq_frame, text="Get Current Frequencies", command=None)
        self.get_freq_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # --- FREQUENCY/START-STOP YakBeg Frame ---
        freq_ss_beg_frame = ttk.LabelFrame(self, text="YakBeg - FREQUENCY/START-STOP", style='Dark.TLabelframe')
        freq_ss_beg_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        freq_ss_beg_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(freq_ss_beg_frame, text="Start Frequency (Hz):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.freq_ss_start_entry = ttk.Entry(freq_ss_beg_frame, textvariable=self.freq_start_var)
        self.freq_ss_start_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(freq_ss_beg_frame, text="Stop Frequency (Hz):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.freq_ss_stop_entry = ttk.Entry(freq_ss_beg_frame, textvariable=self.freq_stop_var)
        self.freq_ss_stop_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        self.freq_ss_result_var = tk.StringVar(value="Result: N/A")
        ttk.Label(freq_ss_beg_frame, textvariable=self.freq_ss_result_var, style="Dark.TLabel.Value").grid(row=2, column=0, columnspan=2, padx=5, pady=2, sticky="ew")

        ttk.Button(freq_ss_beg_frame, text="YakBeg - FREQUENCY/START-STOP", command=self._on_freq_start_stop_beg).grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # --- FREQUENCY/CENTER-SPAN YakBeg Frame ---
        freq_cs_beg_frame = ttk.LabelFrame(self, text="YakBeg - FREQUENCY/CENTER-SPAN", style='Dark.TLabelframe')
        freq_cs_beg_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        freq_cs_beg_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(freq_cs_beg_frame, text="Center Frequency (Hz):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.freq_cs_center_entry = ttk.Entry(freq_cs_beg_frame, textvariable=self.freq_center_var)
        self.freq_cs_center_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(freq_cs_beg_frame, text="Span (Hz):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.freq_cs_span_entry = ttk.Entry(freq_cs_beg_frame, textvariable=self.freq_span_var)
        self.freq_cs_span_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        self.freq_cs_result_var = tk.StringVar(value="Result: N/A")
        ttk.Label(freq_cs_beg_frame, textvariable=self.freq_cs_result_var, style="Dark.TLabel.Value").grid(row=2, column=0, columnspan=2, padx=5, pady=2, sticky="ew")

        ttk.Button(freq_cs_beg_frame, text="YakBeg - FREQUENCY/CENTER-SPAN", command=self._on_freq_center_span_beg).grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        debug_log(f"Widgets for Frequency Settings Tab created. The frequency controls are ready! 🎹",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

    def _on_freq_start_stop_beg(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"YakBeg for FREQUENCY/START-STOP triggered.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        
        start_freq = self.freq_start_var.get()
        stop_freq = self.freq_stop_var.get()
        
        start_resp, stop_resp = handle_freq_start_stop_beg(self.app_instance, start_freq, stop_freq, self.console_print_func)
        
        if start_resp is not None and stop_resp is not None:
            self.freq_start_var.set(start_resp)
            self.freq_stop_var.set(stop_resp)
            self.freq_ss_result_var.set(f"Result: {start_resp} Hz; {stop_resp} Hz")
        else:
            self.freq_ss_result_var.set("Result: FAILED")


    def _on_freq_center_span_beg(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"YakBeg for FREQUENCY/CENTER-SPAN triggered.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        
        center_freq = self.freq_center_var.get()
        span_freq = self.freq_span_var.get()
        
        center_resp, span_resp = handle_freq_center_span_beg(self.app_instance, center_freq, span_freq, self.console_print_func)

        if center_resp is not None and span_resp is not None:
            self.freq_center_var.set(center_resp)
            self.freq_span_var.set(span_resp)
            self.freq_cs_result_var.set(f"Result: {center_resp} Hz; {span_resp} Hz")
        else:
            self.freq_cs_result_var.set("Result: FAILED")
