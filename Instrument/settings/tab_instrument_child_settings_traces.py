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
# Version 20250821.141200.1
# UPDATED: Added a new handler to save instrument trace settings to the configuration file
#          after a successful update from the GUI or an instrument query.

current_version = "20250821.141200.1"
current_version_hash = 20250821 * 141200 * 1

import tkinter as tk
from tkinter import ttk, scrolledtext
import inspect
import os
import pandas as pd # Import pandas for data manipulation

from display.debug_logic import debug_log
from display.console_logic import console_log
from yak.utils_yakbeg_handler import handle_trace_modes_beg, handle_trace_data_beg
from yak.utils_yaknab_handler import handle_all_traces_nab

from display.utils_display_monitor import update_top_plot, update_middle_plot, update_bottom_plot, clear_monitor_plots
from display.utils_scan_view import update_single_plot

# ADDED: Imports for the configuration manager
from settings_and_config.config_manager_instruments import _save_instrument_settings
from settings_and_config.config_manager_save import save_program_config

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

        # UPDATED: Set default values for the trace mode variables
        self.trace1_mode_var = tk.StringVar(value="WRITE")
        self.trace2_mode_var = tk.StringVar(value="MAXHOLD")
        self.trace3_mode_var = tk.StringVar(value="MINHOLD")
        self.trace4_mode_var = tk.StringVar(value="BLANK")

        self.trace_vars = [
            self.trace1_mode_var,
            self.trace2_mode_var,
            self.trace3_mode_var,
            self.trace4_mode_var
        ]

        # Tkinter variables for trace data
        self.trace_data_start_freq_var = tk.DoubleVar(value=500)
        self.trace_data_stop_freq_var = tk.DoubleVar(value=1000)
        self.trace_select_var = tk.StringVar(value="1")
        self.trace_data_count_var = tk.StringVar(value="0")

        self.trace_modes_result_var = tk.StringVar(value="Result: N/A")

        # Variables to store the last successful NAB response data for plotting
        self.last_nab_trace_data = None
        self.last_nab_start_freq = None
        self.last_nab_stop_freq = None
        self.last_nab_trace_modes = None
        
        # NEW: StringVars for displaying the modes and frequencies from the NAB handler response
        self.all_traces_start_freq_display_var = tk.StringVar(value="N/A")
        self.all_traces_stop_freq_display_var = tk.StringVar(value="N/A")
        self.all_traces_trace1_mode_display_var = tk.StringVar(value="N/A")
        self.all_traces_trace2_mode_display_var = tk.StringVar(value="N/A")
        self.all_traces_trace3_mode_display_var = tk.StringVar(value="N/A")
        self.all_traces_count_var = tk.StringVar(value="0")

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
        self.grid_rowconfigure(2, weight=1)

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
        
        ttk.Button(trace_modes_frame, text="YakBeg - TRACE/MODES", command=lambda: self._on_trace_modes_beg()).grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="ew")


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
        
        ttk.Button(trace_data_controls_frame, text="YakBeg - TRACE/DATA", command=lambda: self._on_trace_data_beg()).grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky="ew")

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
        ttk.Button(self, text="Push Trace Data to Monitor", command=lambda: self._on_push_to_monitor(), style="Green.TButton").grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # NEW: Frame for NAB All Traces functionality
        all_traces_nab_frame = ttk.LabelFrame(self, text="YakNab - TRACE/ALL/ONETWOTHREE", padding=10)
        all_traces_nab_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        all_traces_nab_frame.grid_columnconfigure(0, weight=1)
        all_traces_nab_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(all_traces_nab_frame, text="Start Freq (MHz):", style="TLabel").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(all_traces_nab_frame, textvariable=self.all_traces_start_freq_display_var, style="Dark.TLabel.Value").grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(all_traces_nab_frame, text="Stop Freq (MHz):", style="TLabel").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(all_traces_nab_frame, textvariable=self.all_traces_stop_freq_display_var, style="Dark.TLabel.Value").grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(all_traces_nab_frame, text="Trace 1 Mode:", style="TLabel").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(all_traces_nab_frame, textvariable=self.all_traces_trace1_mode_display_var, style="Dark.TLabel.Value").grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(all_traces_nab_frame, text="Trace 2 Mode:", style="TLabel").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(all_traces_nab_frame, textvariable=self.all_traces_trace2_mode_display_var, style="Dark.TLabel.Value").grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(all_traces_nab_frame, text="Trace 3 Mode:", style="TLabel").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(all_traces_nab_frame, textvariable=self.all_traces_trace3_mode_display_var, style="Dark.TLabel.Value").grid(row=4, column=1, padx=5, pady=2, sticky="ew")
        
        self.all_traces_count_label = ttk.Label(all_traces_nab_frame, text="# of points:", style="TLabel")
        self.all_traces_count_label.grid(row=5, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(all_traces_nab_frame, textvariable=self.all_traces_count_var, style="Dark.TLabel.Value").grid(row=5, column=1, padx=5, pady=2, sticky="ew")

        ttk.Button(all_traces_nab_frame, text="YakNab - TRACE/ALL/ONETWOTHREE", command=self._on_all_traces_nab).grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        columns_all = ("Frequency (MHz)", "Trace 1", "Trace 2", "Trace 3")
        self.all_traces_tree = ttk.Treeview(all_traces_nab_frame, columns=columns_all, show="headings", style='Treeview')
        self.all_traces_tree.heading("Frequency (MHz)", text="Frequency (MHz)", anchor=tk.W)
        self.all_traces_tree.heading("Trace 1", text="Trace 1 (dBm)", anchor=tk.W)
        self.all_traces_tree.heading("Trace 2", text="Trace 2 (dBm)", anchor=tk.W)
        self.all_traces_tree.heading("Trace 3", text="Trace 3 (dBm)", anchor=tk.W)
        self.all_traces_tree.grid(row=7, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        vsb_all = ttk.Scrollbar(all_traces_nab_frame, orient="vertical", command=self.all_traces_tree.yview)
        vsb_all.grid(row=7, column=2, sticky="ns")
        self.all_traces_tree.configure(yscrollcommand=vsb_all.set)


        debug_log(f"Widgets for Trace Settings Tab created. The controls are ready to go! 🗺️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)


    def _on_all_traces_nab(self):
        """
        Handles the YakNab command for all traces, displaying the results in the new table.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"YakNab for all traces triggered.",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)
        
        # We call the handler function, which now returns a dictionary.
        all_trace_data = handle_all_traces_nab(self.app_instance, self.console_print_func)
        
        if all_trace_data:
            # Store the data for potential plotting later
            self.last_nab_trace_data = all_trace_data.get("TraceData", {})
            self.last_nab_start_freq = all_trace_data.get("StartFreq")
            self.last_nab_stop_freq = all_trace_data.get("StopFreq")
            self.last_nab_trace_modes = all_trace_data.get("TraceModes", {})

            # Extract the data and modes from the returned dictionary.
            trace_data_dict = self.last_nab_trace_data
            trace_modes = self.last_nab_trace_modes
            start_freq = self.last_nab_start_freq
            stop_freq = self.last_nab_stop_freq

            trace1_data = trace_data_dict.get("Trace1", [])
            trace2_data = trace_data_dict.get("Trace2", [])
            trace3_data = trace_data_dict.get("Trace3", [])

            # Update the display variables for the new UI labels.
            self.all_traces_start_freq_display_var.set(f"{start_freq / 1000000:.3f} MHz")
            self.all_traces_stop_freq_display_var.set(f"{stop_freq / 1000000:.3f} MHz")
            self.all_traces_trace1_mode_display_var.set(trace_modes.get("Trace1", "N/A"))
            self.all_traces_trace2_mode_display_var.set(trace_modes.get("Trace2", "N/A"))
            self.all_traces_trace3_mode_display_var.set(trace_modes.get("Trace3", "N/A"))
            self.all_traces_count_var.set(str(len(trace1_data)))

            # Clear and repopulate the Treeview table.
            self.all_traces_tree.delete(*self.all_traces_tree.get_children())
            
            for i in range(len(trace1_data)):
                freq = trace1_data[i][0]
                val1 = trace1_data[i][1] if i < len(trace1_data) else None
                val2 = trace2_data[i][1] if i < len(trace2_data) else None
                val3 = trace3_data[i][1] if i < len(trace3_data) else None
                
                self.all_traces_tree.insert("", "end", values=(f"{freq:.3f}", f"{val1:.2f}", f"{val2:.2f}", f"{val3:.2f}"))
            
            self.console_print_func(f"✅ Received and displayed data for 3 traces, with {len(trace1_data)} points each.")
            
            # Call the new function to plot the data
            self._plot_all_traces_to_monitor()
            
            # NEW: Switch to the Scan Monitor tab automatically
            self.app_instance.display_parent_tab.change_display_tab("Monitor")

            # ADDED: Call the save handler
            self._save_settings_handler()

        else:
            self.all_traces_start_freq_display_var.set("N/A")
            self.all_traces_stop_freq_display_var.set("N/A")
            self.all_traces_trace1_mode_display_var.set("N/A")
            self.all_traces_trace2_mode_display_var.set("N/A")
            self.all_traces_trace3_mode_display_var.set("N/A")
            self.all_traces_count_var.set("0")
            self.all_traces_tree.delete(*self.all_traces_tree.get_children())
            self.console_print_func("❌ Trace data retrieval failed.")


    def _on_trace_modes_beg(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"YakBeg for TRACE/MODES triggered.",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)
        
        # FIXED: Get values from the local StringVar objects
        trace_modes = [
            self.trace1_mode_var.get(),
            self.trace2_mode_var.get(),
            self.trace3_mode_var.get(),
            self.trace4_mode_var.get()
        ]
        
        response = handle_trace_modes_beg(self.app_instance, trace_modes, self.console_print_func)
        self.trace_modes_result_var.set(f"Result: {response}")
        
        if response != "FAILED":
            # ADDED: Call the save handler
            self._save_settings_handler()

    def _on_trace_data_beg(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"YakBeg for TRACE/DATA triggered.",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
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

            # NEW: Call update_plot to update the Scan View tab with the new data
            scan_view_tab = self.app_instance.display_parent_tab.bottom_pane.scan_view_tab
            df = pd.DataFrame(processed_data, columns=['Frequency_Hz', 'Power_dBm'])
            plot_title = f"Trace {trace_number} Data from YakBeg"
            update_single_plot(scan_view_tab, df, start_freq_mhz, stop_freq_mhz, plot_title)
            
            # NEW: Switch to the Scan View tab automatically
            self.app_instance.display_parent_tab.change_display_tab("View")

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
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)
        
        trace_number = self.trace_select_var.get()
        data = []
        for item in self.trace_data_tree.get_children():
            values = self.trace_data_tree.item(item, 'values')
            data.append((float(values[0]), float(values[1])))
        
        # We need to know which plot to update. The original code only had one push function.
        # Let's assume we're pushing to the top plot for now.
        plot_title = f"Trace {trace_number} Data"
        if trace_number == "1":
            update_top_plot(self.app_instance.display_parent_tab.scan_monitor_tab, data, self.trace_data_start_freq_var.get(), self.trace_data_stop_freq_var.get(), plot_title)
        elif trace_number == "2":
            update_middle_plot(self.app_instance.display_parent_tab.scan_monitor_tab, data, self.trace_data_start_freq_var.get(), self.trace_data_stop_freq_var.get(), plot_title)
        elif trace_number == "3":
            update_bottom_plot(self.app_instance.display_parent_tab.scan_monitor_tab, data, self.trace_data_start_freq_var.get(), self.trace_data_stop_freq_var.get(), plot_title)
        else:
            self.console_print_func("⚠️ Invalid trace number selected. Cannot push to monitor.")
            debug_log("Invalid trace number selected. This is a fucking waste of time!",
                        file=f"{os.path.basename(__file__)}",
                        version=current_version,
                        function=current_function)

    def _plot_all_traces_to_monitor(self):
        """
        Function Description:
        This function takes the last successful response from handle_all_traces_nab,
        converts the data to a DataFrame, and pushes it to the three monitor plots.
        
        Inputs:
            None (uses self.last_nab_trace_data and other class attributes)

        Outputs:
            None. Renders the plots to the GUI.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}. Plotting all three NAB traces to the monitor. 📊",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)

        if not self.last_nab_trace_data:
            self.console_print_func("❌ No NAB trace data available to plot. Press the NAB button first!")
            debug_log("No NAB trace data available. Aborting plot.",
                        file=f"{os.path.basename(__file__)}",
                        version=current_version,
                        function=current_function)
            return

        # Get the global plot instance
        monitor_tab = self.app_instance.display_parent_tab.bottom_pane.scan_monitor_tab
        if not monitor_tab:
            self.console_print_func("❌ Monitor tab not found. Cannot plot.")
            debug_log("Monitor tab instance not found. This is a critical failure!",
                        file=f"{os.path.basename(__file__)}",
                        version=current_version,
                        function=current_function)
            return

        start_freq_mhz = self.last_nab_start_freq / 1000000
        stop_freq_mhz = self.last_nab_stop_freq / 1000000

        # Plot Trace 1 (Live/View) on the top plot
        trace1_data = self.last_nab_trace_data.get("Trace1", [])
        trace1_mode = self.last_nab_trace_modes.get("Trace1", "N/A")
        if trace1_data and trace1_mode.upper() in ["VIEW", "WRIT"]:
            df1 = pd.DataFrame(trace1_data, columns=["Frequency_Hz", "Power_dBm"])
            update_top_plot(monitor_tab, df1, start_freq_mhz, stop_freq_mhz, f"Live/View ({trace1_mode})")
        else:
            # Clear the plot if the mode is 'BLANK' or no data is available
            df1 = pd.DataFrame(columns=["Frequency_Hz", "Power_dBm"])
            update_top_plot(monitor_tab, df1, start_freq_mhz, stop_freq_mhz, "Live/View (BLANK)")
            
        # Plot Trace 2 (Max Hold) on the middle plot
        trace2_data = self.last_nab_trace_data.get("Trace2", [])
        trace2_mode = self.last_nab_trace_modes.get("Trace2", "N/A")
        if trace2_data and trace2_mode.upper() == "MAXH":
            df2 = pd.DataFrame(trace2_data, columns=["Frequency_Hz", "Power_dBm"])
            update_middle_plot(monitor_tab, df2, start_freq_mhz, stop_freq_mhz, f"Max Hold ({trace2_mode})")
        else:
            df2 = pd.DataFrame(columns=["Frequency_Hz", "Power_dBm"])
            update_middle_plot(monitor_tab, df2, start_freq_mhz, stop_freq_mhz, "Max Hold (BLANK)")

        # Plot Trace 3 (Min Hold) on the bottom plot
        trace3_data = self.last_nab_trace_data.get("Trace3", [])
        trace3_mode = self.last_nab_trace_modes.get("Trace3", "N/A")
        if trace3_data and trace3_mode.upper() == "MINH":
            df3 = pd.DataFrame(trace3_data, columns=["Frequency_Hz", "Power_dBm"])
            update_bottom_plot(monitor_tab, df3, start_freq_mhz, stop_freq_mhz, f"Min Hold ({trace3_mode})")
        else:
            df3 = pd.DataFrame(columns=["Frequency_Hz", "Power_dBm"])
            update_bottom_plot(monitor_tab, df3, start_freq_mhz, stop_freq_mhz, "Min Hold (BLANK)")

        self.console_print_func("✅ Successfully plotted all traces to the monitor.")
        debug_log(f"All NAB traces plotted successfully. Mission accomplished! 🥳",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)

    def _save_settings_handler(self):
        """Handles saving the instrument trace settings to the config file."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"⚙️ 💾 Entering {current_function}. Time to save the instrument trace settings! 📈",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        try:
            # Call the specific save function from the modular config manager
            _save_instrument_settings(
                config=self.app_instance.program_config,
                app_instance=self.app_instance,
                console_print_func=self.console_print_func
            )
            # Call the main config save function to write the changes to the file
            save_program_config(
                app_instance=self.app_instance,
                config=self.app_instance.program_config,
                config_file_path=self.app_instance.config_file_path,
                console_print_func=self.console_print_func
            )
            debug_log("⚙️ ✅ Instrument trace settings saved successfully. Mission accomplished!",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
        except Exception as e:
            debug_log(f"❌ Error saving instrument trace settings: {e}",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
            self.console_print_func(f"❌ Error saving instrument trace settings: {e}")