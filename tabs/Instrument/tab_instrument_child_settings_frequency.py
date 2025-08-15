# tabs/Instrument/tab_instrument_child_settings_frequency.py
#
# This file defines the FrequencySettingsTab, a Tkinter Frame for controlling a spectrum
# analyzer's frequency settings.
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
# Version 20250815.140830.11
# FIX: Corrected ValueError by updating UI functions to unpack 4 values from YakBeg handlers.
# FIX: Reverted console_log calls in except blocks to fix TypeError.

current_version = "20250815.140830.11"
current_version_hash = 20250815 * 140830 * 11

import tkinter as tk
from tkinter import ttk
import inspect
import os

from display.debug_logic import debug_log
from display.console_logic import console_log
from yak.utils_yakbeg_handler import handle_freq_start_stop_beg, handle_freq_center_span_beg

class FrequencySettingsTab(ttk.Frame):
    """
    A Tkinter Frame that provides a user interface for frequency settings.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing FrequencySettingsTab. This should be a walk in the park! 🚶‍♀️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        self.app_instance = app_instance
        self.console_print_func = console_print_func
        self.is_tracing = False

        super().__init__(master)
        self.pack(fill="both", expand=True)
        self._set_default_variables()
        self._create_widgets()

    def _set_default_variables(self):
        """Initializes Tkinter variables for the widgets."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Setting default variables for FrequencySettingsTab. ⚙️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        # New variables to hold the query results in MHz
        self.freq_ss_result_var = tk.StringVar(value="Result: N/A")
        self.freq_cs_result_var = tk.StringVar(value="Result: N/A")

        # Tkinter variables for frequency settings, now in MHz
        self.freq_start_var = tk.DoubleVar(value=100.0)
        self.freq_stop_var = tk.DoubleVar(value=200.0)
        self.freq_center_var = tk.DoubleVar(value=150.0)
        self.freq_span_var = tk.DoubleVar(value=100.0)
        
        # NEW: Add traces to round the variable values
        self.freq_start_var.trace_add('write', self._round_variables)
        self.freq_stop_var.trace_add('write', self._round_variables)
        self.freq_center_var.trace_add('write', self._round_variables)
        self.freq_span_var.trace_add('write', self._round_variables)

    def _round_variables(self, *args):
        """
        Callback to round the values of the DoubleVar to 3 decimal places.
        It also truncates values with more than 6 decimal places.
        """
        if self.is_tracing:
            return
        self.is_tracing = True

        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Rounding variables to 3 decimal places. A meticulous process, for sure! 🔬",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        try:
            current_start = self.freq_start_var.get()
            current_stop = self.freq_stop_var.get()
            current_center = self.freq_center_var.get()
            current_span = self.freq_span_var.get()

            # Truncate values if they have more than 6 decimal places
            # Helper function to truncate float at 6 decimal places
            def truncate_float(f):
                s = f"{f:.7f}" # Get a string representation with enough precision
                if '.' in s:
                    parts = s.split('.')
                    if len(parts[1]) > 6:
                        return float(f"{parts[0]}.{parts[1][:6]}")
                return f

            self.freq_start_var.set(round(truncate_float(current_start), 3))
            self.freq_stop_var.set(round(truncate_float(current_stop), 3))
            self.freq_center_var.set(round(truncate_float(current_center), 3))
            self.freq_span_var.set(round(truncate_float(current_span), 3))
            
        except Exception as e:
            console_log(f"❌ Error while rounding variables: {e}", self.console_print_func)
            debug_log(f"Rounding failed! The numbers be acting up! The error be: {e}",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
        finally:
            self.is_tracing = False
        
    def _create_widgets(self):
        """Creates the GUI widgets for the tab."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating widgets for FrequencySettingsTab. The puzzle pieces are coming together! 🧩",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        self.grid_columnconfigure(0, weight=1)

        # --- FREQUENCY/START-STOP Frame ---
        freq_ss_frame = ttk.LabelFrame(self, text="FREQUENCY/START-STOP (MHz)", padding=10)
        freq_ss_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        freq_ss_frame.grid_columnconfigure(0, weight=1)
        freq_ss_frame.grid_columnconfigure(1, weight=1)

        # Start Frequency Slider & Entry
        ttk.Label(freq_ss_frame, text="Start Frequency:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Scale(freq_ss_frame, from_=100, to=1000, orient=tk.HORIZONTAL, variable=self.freq_start_var).grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        ttk.Entry(freq_ss_frame, textvariable=self.freq_start_var).grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        # Stop Frequency Slider & Entry
        ttk.Label(freq_ss_frame, text="Stop Frequency:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Scale(freq_ss_frame, from_=100, to=1000, orient=tk.HORIZONTAL, variable=self.freq_stop_var).grid(row=3, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        ttk.Entry(freq_ss_frame, textvariable=self.freq_stop_var).grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        # Result Label and YakBeg Button
        ttk.Label(freq_ss_frame, textvariable=self.freq_ss_result_var, style="Dark.TLabel.Value").grid(row=4, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        ttk.Button(freq_ss_frame, text="YakBeg - FREQUENCY/START-STOP", command=self._on_freq_start_stop_beg).grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")


        # --- FREQUENCY/CENTER-SPAN Frame ---
        freq_cs_frame = ttk.LabelFrame(self, text="FREQUENCY/CENTER-SPAN (MHz)", padding=10)
        freq_cs_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        freq_cs_frame.grid_columnconfigure(0, weight=1)
        freq_cs_frame.grid_columnconfigure(1, weight=1)

        # Center Frequency Slider & Entry
        ttk.Label(freq_cs_frame, text="Center Frequency:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Scale(freq_cs_frame, from_=100, to=1000, orient=tk.HORIZONTAL, variable=self.freq_center_var).grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        ttk.Entry(freq_cs_frame, textvariable=self.freq_center_var).grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        # Span Slider & Entry
        ttk.Label(freq_cs_frame, text="Span:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Scale(freq_cs_frame, from_=100, to=1000, orient=tk.HORIZONTAL, variable=self.freq_span_var).grid(row=3, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        ttk.Entry(freq_cs_frame, textvariable=self.freq_span_var).grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        # Result Label and YakBeg Button
        ttk.Label(freq_cs_frame, textvariable=self.freq_cs_result_var, style="Dark.TLabel.Value").grid(row=4, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        ttk.Button(freq_cs_frame, text="YakBeg - FREQUENCY/CENTER-SPAN", command=self._on_freq_center_span_beg).grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    def _on_freq_start_stop_beg(self):
        """
        Handles the YakBeg for FREQUENCY/START-STOP.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering function: {current_function}. Arrr, a treasure map for frequencies! 🗺️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        try:
            start_freq_mhz = self.freq_start_var.get()
            stop_freq_mhz = self.freq_stop_var.get()

            # NEW: If start is >= stop, adjust stop
            if start_freq_mhz >= stop_freq_mhz:
                new_stop_mhz = start_freq_mhz + 10.0
                console_log(f"⚠️ Start frequency ({start_freq_mhz:.3f} MHz) is greater than or equal to stop frequency ({stop_freq_mhz:.3f} MHz). Automatically setting stop to {new_stop_mhz:.3f} MHz.", self.console_print_func)
                debug_log(f"The start frequency ({start_freq_mhz} MHz) is greater than or equal to the stop frequency ({stop_freq_mhz} MHz). The captain has corrected the course! 📈",
                          file=os.path.basename(__file__),
                          version=current_version,
                          function=current_function)
                self.freq_stop_var.set(new_stop_mhz)
                # Re-read the adjusted value for the YakBeg command
                stop_freq_mhz = self.freq_stop_var.get()


            # Get values in MHz and convert to Hz, ensuring no decimal points
            start_freq_hz = int(start_freq_mhz * 1e6)
            stop_freq_hz = int(stop_freq_mhz * 1e6)

            # FIXED: Expect 4 values to be returned from the handler
            start_resp_hz, stop_resp_hz, span_resp_hz, center_resp_hz = handle_freq_start_stop_beg(
                app_instance=self.app_instance,
                start_freq=start_freq_hz,
                stop_freq=stop_freq_hz,
                console_print_func=self.console_print_func
            )

            if start_resp_hz is not None and stop_resp_hz is not None:
                # Convert response back to MHz for display
                start_resp_mhz = start_resp_hz / 1e6
                stop_resp_mhz = stop_resp_hz / 1e6
                self.freq_start_var.set(start_resp_mhz)
                self.freq_stop_var.set(stop_resp_mhz)
                # Display all four values
                self.freq_ss_result_var.set(f"Result: Start: {start_resp_mhz:.3f} MHz; Stop: {stop_resp_mhz:.3f} MHz; Center: {center_resp_hz / 1e6:.3f} MHz; Span: {span_resp_hz / 1e6:.3f} MHz")
            else:
                self.freq_ss_result_var.set("Result: FAILED")

        except Exception as e:
            # FIXED: Reverted console_log call to its proper format
            console_log(f"❌ Error in {current_function}: {e}", self.console_print_func)
            debug_log(f"Arrr, the code be capsized! The error be: {e}",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)

    def _on_freq_center_span_beg(self):
        """
        Handles the YakBeg for FREQUENCY/CENTER-SPAN.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering function: {current_function}. Plotting a course to the center! 🧭",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        try:
            # Get values in MHz and convert to Hz, ensuring no decimal points
            center_freq_mhz = self.freq_center_var.get()
            span_freq_mhz = self.freq_span_var.get()
            
            center_freq_hz = int(center_freq_mhz * 1e6)
            span_freq_hz = int(span_freq_mhz * 1e6)

            # FIXED: Expect 4 values to be returned from the handler
            center_resp_hz, span_resp_hz, start_resp_hz, stop_resp_hz = handle_freq_center_span_beg(
                app_instance=self.app_instance,
                center_freq=center_freq_hz,
                span_freq=span_freq_hz,
                console_print_func=self.console_print_func
            )

            if center_resp_hz is not None and span_resp_hz is not None:
                # Convert response back to MHz for display
                center_resp_mhz = center_resp_hz / 1e6
                span_resp_mhz = span_resp_hz / 1e6
                self.freq_center_var.set(center_resp_mhz)
                self.freq_span_var.set(span_resp_mhz)
                # Display all four values
                self.freq_cs_result_var.set(f"Result: Center: {center_resp_mhz:.3f} MHz; Span: {span_resp_mhz:.3f} MHz; Start: {start_resp_hz / 1e6:.3f} MHz; Stop: {stop_resp_hz / 1e6:.3f} MHz")
            else:
                self.freq_cs_result_var.set("Result: FAILED")

        except Exception as e:
            # FIXED: Reverted console_log call to its proper format
            console_log(f"❌ Error in {current_function}: {e}", self.console_print_func)
            debug_log(f"Arrr, the code be capsized! The error be: {e}",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
