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

current_version = "20250818.193300.1"
current_version_hash = (20250818 * 193300 * 1)

import tkinter as tk
from tkinter import ttk, scrolledtext
import inspect
import os
import numpy as np

# Import Yak commands from the library
from tabs.Instrument.Yakety_Yak import YakBeg, YakRig, YakNab
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


        # --- TRACE/MODES Frame ---
        trace_modes_frame = ttk.LabelFrame(self, text="TRACE/MODES", padding=10)
        trace_modes_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        trace_modes_frame.grid_columnconfigure(0, weight=1)
        trace_modes_frame.grid_columnconfigure(1, weight=1)
        trace_modes_frame.grid_columnconfigure(2, weight=1)
        trace_modes_frame.grid_columnconfigure(3, weight=1)

        ttk.Label(trace_modes_frame, text="Trace 1 Mode:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(trace_modes_frame, text="Trace 2 Mode:").grid(row=0, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(trace_modes_frame, text="Trace 3 Mode:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(trace_modes_frame, text="Trace 4 Mode:").grid(row=0, column=3, padx=5, pady=2, sticky="w")
        
        self.trace1_combo = ttk.Combobox(trace_modes_frame, textvariable=self.trace1_mode_var, values=self.trace_mode_options, state="readonly")
        self.trace1_combo.grid(row=1, column=0, padx=5, pady=2, sticky="ew")
        self.trace2_combo = ttk.Combobox(trace_modes_frame, textvariable=self.trace2_mode_var, values=self.trace_mode_options, state="readonly")
        self.trace2_combo.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.trace3_combo = ttk.Combobox(trace_modes_frame, textvariable=self.trace3_mode_var, values=self.trace_mode_options, state="readonly")
        self.trace3_combo.grid(row=1, column=2, padx=5, pady=2, sticky="ew")
        self.trace4_combo = ttk.Combobox(trace_modes_frame, textvariable=self.trace4_mode_var, values=self.trace_mode_options, state="readonly")
        self.trace4_combo.grid(row=1, column=3, padx=5, pady=2, sticky="ew")
        
        self.trace_modes_result_var = tk.StringVar(value="Result: N/A")
        ttk.Label(trace_modes_frame, textvariable=self.trace_modes_result_var, style="Dark.TLabel.Value").grid(row=2, column=0, columnspan=4, padx=5, pady=2, sticky="ew")
        
        ttk.Button(trace_modes_frame, text="YakBeg - TRACE/MODES", command=self._on_trace_modes_beg).grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="ew")


        # --- TRACE/DATA Frame ---
        trace_data_frame = ttk.LabelFrame(self, text="TRACE/DATA", padding=10)
        trace_data_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
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


    def _on_freq_start_stop_beg(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"YakBeg for FREQUENCY/START-STOP triggered.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        
        start_freq = self.freq_start_var.get()
        stop_freq = self.freq_stop_var.get()
        
        response = YakBeg(self.app_instance, "FREQUENCY/START-STOP", self.console_print_func, start_freq, stop_freq)
        self.freq_ss_result_var.set(f"Result: {response}")

    def _on_freq_center_span_beg(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"YakBeg for FREQUENCY/CENTER-SPAN triggered.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        
        center_freq = self.freq_center_var.get()
        span_freq = self.freq_span_var.get()
        
        response = YakBeg(self.app_instance, "FREQUENCY/CENTER-SPAN", self.console_print_func, center_freq, span_freq)
        self.freq_cs_result_var.set(f"Result: {response}")

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
        
        response = YakBeg(self.app_instance, "TRACE/MODES", self.console_print_func, *trace_modes)
        self.trace_modes_result_var.set(f"Result: {response}")

    def _on_trace_data_beg(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"YakBeg for TRACE/DATA triggered.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        
        trace_number = self.trace_select_var.get()
        start_freq = self.trace_data_start_freq_var.get() * 1000000
        stop_freq = self.trace_data_stop_freq_var.get() * 1000000
        
        # This is a complex command string that needs to be manually constructed
        # as it combines different commands in a specific order.
        full_command = f":FREQuency:STARt {int(start_freq)};:FREQuency:STOP {int(stop_freq)};:TRACe:DATA? TRACE{trace_number}"

        # We'll use YakNab here because we are asking for a single, long query response
        # after a SET command. The `BEG` action type in `visa_commands.csv` will be
        # replaced by this full command.
        response_string = YakNab(self.app_instance, f"TRACE/DATA/{trace_number}", self.console_print_func)

        if response_string and response_string != "FAILED":
            try:
                values = [float(val.strip()) for val in response_string.split(',')]
                self.trace_data_count_var.set(str(len(values)))
                
                # Clear existing data
                self.trace_data_tree.delete(*self.trace_data_tree.get_children())
                
                num_points = len(values)
                frequencies = np.linspace(start_freq, stop_freq, num_points)
                
                for i, value in enumerate(values):
                    freq_mhz = frequencies[i] / 1000000
                    self.trace_data_tree.insert("", "end", values=(f"{freq_mhz:.3f}", f"{value:.2f}"))
                
                self.console_print_func(f"✅ Received and displayed {len(values)} data points.")
            except (ValueError, IndexError, TypeError) as e:
                self.console_print_func(f"❌ Failed to parse trace data: {e}. What a disaster!")
                debug_log(f"Failed to parse trace data string: {response_string}. Error: {e}",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            function=current_function)
                self.trace_data_count_var.set("0")
        else:
            self.trace_data_count_var.set("0")
            self.trace_data_tree.delete(*self.trace_data_tree.get_children())
            self.console_print_func("❌ Trace data retrieval failed.")
        
    def _on_tab_selected(self, event):
        """Called when this tab is selected."""
        pass # No specific actions needed on selection


