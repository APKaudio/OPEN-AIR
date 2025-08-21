# tabs/Experiments/tab_experiments_child_YakBeg.py
#
# This file defines the YakBegTab, a Tkinter Frame that provides functionality
# to test and demonstrate the new YakBeg command. It includes UI elements for
# configuring and querying frequency, span, trace modes, and trace data in a
# single, efficient operation.
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
# Version 20250818.193300.1 (NEW: Initial version to test the YakBeg function.)
# Version 20250818.193600.1 (FIXED: Moved YakBeg import inside methods to resolve circular import error.)
# Version 20250818.194000.1 (FIXED: Corrected _on_trace_data_beg to use YakBeg with correct command type from CSV.)
# Version 20250818.194100.1 (FIXED: Corrected the parsing of the trace data response string from the BEG command.)
# Version 20250818.194200.1 (FIXED: The _on_trace_data_beg function was updated to correctly parse the mixed separator response.)
# Version 20250818.194500.1 (FIXED: Corrected the parsing of the trace data response string from the BEG command to handle mixed separators.)
# Version 20250818.194600.1 (FIXED: Implemented parsing logic to correctly handle the semicolon-separated frequency values and comma-separated trace data.)
# Version 20250818.194800.1 (FIXED: The _on_trace_data_beg function was updated to correctly parse the comma-separated response with known start/stop frequencies.)
# Version 20250818.195000.1 (NEW: Added "Push to Monitor" button and functionality.)
# Version 20250818.195200.1 (FIXED: Corrected the command_type for TRACE/DATA to use the correct format from the CSV.)
# Version 20250818.195300.1 (FIXED: The _on_trace_data_beg function was updated to use the correct hardcoded command type from the CSV.)
# Version 20250818.195500.1 (NEW: Added MARKER/PLACE/ALL experiment.)
# Version 20250818.195700.1 (FIXED: Corrected the trace data parsing to use the comma separator, and added a marker experiment frame.)
# Version 20250818.200000.1 (FIXED: Corrected the command type string for trace data to match the CSV file, fixing the persistent KeyError.)
# Version 20250818.200200.1 (FIXED: Added logic to turn markers on before a YakBeg call and off afterwards.)
# Version 20250818.200300.1 (FIXED: The trace data command type string was corrected to use the hardcoded command from the CSV, not a dynamic string, fixing the KeyError.)
# Version 20250818.200500.1 (FIXED: Corrected frequency conversions to integers to fix instrument communication errors.)
# Version 20250818.201500.1 (REFACTORED: Moved all core logic to utils_yakbeg_handler.py to decouple UI from business logic.)
# Version 20250818.202500.1 (REFACTORED: Updated UI layer to call new handler functions and correctly process their return values.)
# Version 20250818.202800.1 (FIXED: Corrected the _on_marker_place_all_beg function to extract string values from StringVar objects before passing to handler.)

current_version = "20250818.202800.1"
current_version_hash = (20250818 * 202800 * 1)

import tkinter as tk
from tkinter import ttk, scrolledtext
import inspect
import os
import numpy as np

# Import the new handler module
from yak.utils_yakbeg_handler import (
    handle_freq_start_stop_beg,
    handle_freq_center_span_beg,
    handle_marker_place_all_beg,
    handle_trace_modes_beg,
    handle_trace_data_beg)
from display.debug_logic import debug_log
from display.console_logic import console_log

class YakBegTab(ttk.Frame):
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing YakBegTab. Version: {current_version}. Get ready to beg for some data! 🙏",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)

        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func

        # Tkinter variables for frequency settings
        self.freq_start_var = tk.DoubleVar(value=500000000)
        self.freq_stop_var = tk.DoubleVar(value=1000000000)
        self.freq_center_var = tk.DoubleVar(value=750000000)
        self.freq_span_var = tk.DoubleVar(value=500000000)

        # Tkinter variables for trace modes
        self.trace_mode_options = ["VIEW", "MAXHold", "MINHold", "WRITe", "BLANK"]
        self.trace1_mode_var = tk.StringVar(value=self.trace_mode_options[3])
        self.trace2_mode_var = tk.StringVar(value=self.trace_mode_options[1])
        self.trace3_mode_var = tk.StringVar(value=self.trace_mode_options[2])
        self.trace4_mode_var = tk.StringVar(value=self.trace_mode_options[0])

        # Tkinter variables for trace data
        self.trace_data_start_freq_var = tk.DoubleVar(value=500)
        self.trace_data_stop_freq_var = tk.DoubleVar(value=1000)
        self.trace_select_var = tk.StringVar(value="1")
        self.trace_data_count_var = tk.StringVar(value="0")
        
        # Tkinter variables for Marker/Place/All
        self.marker_freq_vars = [tk.StringVar(self, value="111"), tk.StringVar(self, value="222"),
                                 tk.StringVar(self, value="333"), tk.StringVar(self, value="444"),
                                 tk.StringVar(self, value="555"), tk.StringVar(self, value="666")]
        self.marker_place_all_result_var = tk.StringVar(self, value="Result: N/A")

        self.edit_entry = None
        self.current_edit_cell = None

        self._create_widgets()

        debug_log(f"YakBegTab initialized. The Begging begins! Version: {current_version}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)

    def _create_widgets(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Creating YakBegTab widgets...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # --- FREQUENCY/START-STOP Frame ---
        freq_ss_frame = ttk.LabelFrame(self, text="FREQUENCY/START-STOP", padding=10)
        freq_ss_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        freq_ss_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(freq_ss_frame, text="Start Frequency (Hz):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(freq_ss_frame, textvariable=self.freq_start_var).grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(freq_ss_frame, text="Stop Frequency (Hz):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(freq_ss_frame, textvariable=self.freq_stop_var).grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        self.freq_ss_result_var = tk.StringVar(value="Result: N/A")
        ttk.Label(freq_ss_frame, textvariable=self.freq_ss_result_var, style="Dark.TLabel.Value").grid(row=2, column=0, columnspan=2, padx=5, pady=2, sticky="ew")

        ttk.Button(freq_ss_frame, text="YakBeg - FREQUENCY/START-STOP", command=self._on_freq_start_stop_beg).grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")


        # --- FREQUENCY/CENTER-SPAN Frame ---
        freq_cs_frame = ttk.LabelFrame(self, text="FREQUENCY/CENTER-SPAN", padding=10)
        freq_cs_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        freq_cs_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(freq_cs_frame, text="Center Frequency (Hz):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(freq_cs_frame, textvariable=self.freq_center_var).grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(freq_cs_frame, text="Span (Hz):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(freq_cs_frame, textvariable=self.freq_span_var).grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        self.freq_cs_result_var = tk.StringVar(value="Result: N/A")
        ttk.Label(freq_cs_frame, textvariable=self.freq_cs_result_var, style="Dark.TLabel.Value").grid(row=2, column=0, columnspan=2, padx=5, pady=2, sticky="ew")

        ttk.Button(freq_cs_frame, text="YakBeg - FREQUENCY/CENTER-SPAN", command=self._on_freq_center_span_beg).grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # --- MARKER/PLACE/ALL Frame ---
        marker_place_all_frame = ttk.LabelFrame(self, text="MARKER/PLACE/ALL", padding=10)
        marker_place_all_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        marker_place_all_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        for i in range(6):
            ttk.Label(marker_place_all_frame, text=f"M{i+1} Freq (MHz):").grid(row=0, column=i, padx=5, pady=2, sticky="w")
            ttk.Entry(marker_place_all_frame, textvariable=self.marker_freq_vars[i]).grid(row=1, column=i, padx=5, pady=2, sticky="ew")

        self.marker_place_all_result_var = tk.StringVar(value="Result: N/A")
        ttk.Label(marker_place_all_frame, textvariable=self.marker_place_all_result_var, style="Dark.TLabel.Value").grid(row=2, column=0, columnspan=6, padx=5, pady=2, sticky="ew")

        ttk.Button(marker_place_all_frame, text="YakBeg - MARKER/PLACE/ALL", command=self._on_marker_place_all_beg).grid(row=3, column=0, columnspan=6, padx=5, pady=5, sticky="ew")


        # --- TRACE/MODES Frame ---
        trace_modes_frame = ttk.LabelFrame(self, text="TRACE/MODES", padding=10)
        trace_modes_frame.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        trace_modes_frame.grid_columnconfigure(0, weight=1)
        trace_modes_frame.grid_columnconfigure(1, weight=1)
        trace_modes_frame.grid_columnconfigure(2, weight=1)
        trace_modes_frame.grid_columnconfigure(3, weight=1)

        ttk.Label(trace_modes_frame, text="Trace 1 Mode:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.trace1_combo = ttk.Combobox(trace_modes_frame, textvariable=self.trace1_mode_var, values=self.trace_mode_options, state="readonly")
        self.trace1_combo.grid(row=1, column=0, padx=5, pady=2, sticky="ew")
        ttk.Label(trace_modes_frame, text="Trace 2 Mode:").grid(row=0, column=1, padx=5, pady=2, sticky="w")
        self.trace2_combo = ttk.Combobox(trace_modes_frame, textvariable=self.trace2_mode_var, values=self.trace_mode_options, state="readonly")
        self.trace2_combo.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        ttk.Label(trace_modes_frame, text="Trace 3 Mode:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.trace3_combo = ttk.Combobox(trace_modes_frame, textvariable=self.trace3_mode_var, values=self.trace_mode_options, state="readonly")
        self.trace3_combo.grid(row=1, column=2, padx=5, pady=2, sticky="ew")
        ttk.Label(trace_modes_frame, text="Trace 4 Mode:").grid(row=0, column=3, padx=5, pady=2, sticky="w")
        self.trace4_combo = ttk.Combobox(trace_modes_frame, textvariable=self.trace4_mode_var, values=self.trace_mode_options, state="readonly")
        self.trace4_combo.grid(row=1, column=3, padx=5, pady=2, sticky="ew")
        
        self.trace_modes_result_var = tk.StringVar(value="Result: N/A")
        ttk.Label(trace_modes_frame, textvariable=self.trace_modes_result_var, style="Dark.TLabel.Value").grid(row=2, column=0, columnspan=4, padx=5, pady=2, sticky="ew")
        
        ttk.Button(trace_modes_frame, text="YakBeg - TRACE/MODES", command=self._on_trace_modes_beg).grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="ew")


        # --- TRACE/DATA Frame ---
        trace_data_frame = ttk.LabelFrame(self, text="TRACE/DATA", padding=10)
        trace_data_frame.grid(row=6, column=0, padx=10, pady=5, sticky="nsew")
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
        
        ttk.Button(trace_data_controls_frame, text="YakBeg - TRACE/DATA", command=self._on_trace_data_beg).grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky="ew")

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
        ttk.Button(self, text="Push Trace Data to Monitor", command=self._on_push_to_monitor, style="Green.TButton").grid(row=7, column=0, padx=10, pady=5, sticky="ew")


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


    def _on_marker_place_all_beg(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"YakBeg for MARKER/PLACE/ALL triggered.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        
        # FIXED: Get the string value from each StringVar before passing to the handler.
        marker_freqs_mhz = [v.get() for v in self.marker_freq_vars]
        
        response = handle_marker_place_all_beg(self.app_instance, marker_freqs_mhz, self.console_print_func)
        self.marker_place_all_result_var.set(f"Result: {response}")


    def _on_trace_modes_beg(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"YakBeg for TRACE/MODES triggered.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        
        trace_modes = [
            self.trace1_mode_var.get(),
            self.trace2_mode_var.get(),
            self.trace3_mode_var.get(),
            self.trace4_mode_var.get()
        ]
        
        response = handle_trace_modes_beg(self.app_instance, trace_modes, self.console_print_func)
        self.trace_modes_result_var.set(f"Result: {response}")


    def _on_trace_data_beg(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"YakBeg for TRACE/DATA triggered.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        
        trace_number = self.trace_select_var.get()
        start_freq_mhz = self.trace_data_start_freq_var.get()
        stop_freq_mhz = self.trace_data_stop_freq_var.get()
        
        processed_data = handle_trace_data_beg(self.app_instance, trace_number, start_freq_mhz, stop_freq_mhz, self.console_print_func)

        if processed_data:
            self.trace_data_count_var.set(str(len(processed_data)))
            self.trace_data_tree.delete(*self.trace_data_tree.get_children())
            
            for freq, value in processed_data:
                self.trace_data_tree.insert("", "end", values=(f"{freq:.3f}", f"{value:.2f}"))
            
            self.console_print_func(f"✅ Received and displayed {len(processed_data)} data points.")
        else:
            self.trace_data_count_var.set("0")
            self.trace_data_tree.delete(*self.trace_data_tree.get_children())
            self.console_print_func("❌ Trace data retrieval failed.")

    def _on_tab_selected(self, event):
        """Called when this tab is selected."""
        pass # No specific actions needed on selection
        
    def _on_push_to_monitor(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Push to Monitor button clicked. Let's see if we can get this trace on screen! 🖥️",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        
        trace_number = self.trace_select_var.get()
        data = []
        for item in self.trace_data_tree.get_children():
            values = self.trace_data_tree.item(item, 'values')
            data.append((float(values[0]), float(values[1])))
        
        start_freq_mhz = self.trace_data_start_freq_var.get()
        stop_freq_mhz = self.trace_data_stop_freq_var.get()
        
        handle_push_to_monitor(self.app_instance, self.trace_select_var, self.trace_data_tree, start_freq_mhz, stop_freq_mhz, self.console_print_func)
