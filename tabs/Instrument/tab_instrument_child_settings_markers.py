# tabs/Instrument/tab_instrument_child_settings_markers.py
#
# This file defines the MarkerSettingsTab, a Tkinter Frame for controlling a spectrum
# analyzer's marker settings.
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
# Version 20250815.113847.7
# FIX: Corrected keyword argument for handle_marker_place_all_beg. Reverted the incorrect console_log call.

current_version = "20250815.113847.7"
current_version_hash = 20250815 * 113847 * 7

import tkinter as tk
from tkinter import ttk
import inspect
import os

from display.debug_logic import debug_log
from display.console_logic import console_log
from yak.utils_yakbeg_handler import handle_marker_place_all_beg

class MarkerSettingsTab(ttk.Frame):
    """
    A Tkinter Frame that provides a user interface for marker settings.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing MarkerSettingsTab. This should be a walk in the park! 🚶‍♀️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        self.app_instance = app_instance
        self.console_print_func = console_print_func

        super().__init__(master)
        self.pack(fill="both", expand=True)
        self._set_default_variables()
        self._create_widgets()

    def _set_default_variables(self):
        """Initializes Tkinter variables for the widgets."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Setting default variables for MarkerSettingsTab. ⚙️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        self.read_markers_all_data = tk.StringVar(self, value="N/A")
        # Set default values to match the experiment tab
        default_freqs = [111.0, 222.0, 333.0, 444.0, 555.0, 666.0]
        self.marker_freq_vars = [tk.DoubleVar(self, value=f) for f in default_freqs]
        
    def _create_widgets(self):
        """Creates the GUI widgets for the tab."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating widgets for MarkerSettingsTab. The puzzle pieces are coming together! 🧩",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        # Main frame for the MarkerSettingsTab
        main_frame = ttk.LabelFrame(self, text="Marker Settings", padding=10)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- MARKER/READ/ALL Frame ---
        read_markers_frame = ttk.LabelFrame(main_frame, text="Read All Markers", padding=10)
        read_markers_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(read_markers_frame, text="Marker Data:", style='TLabel').grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(read_markers_frame, textvariable=self.read_markers_all_data, style='Dark.TLabel.Value').grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        
        # Spacer
        ttk.Frame(read_markers_frame, height=10).grid(row=2, column=0, columnspan=2)

        # --- MARKER/PEAK Frame ---
        marker_peak_frame = ttk.LabelFrame(read_markers_frame, text="Peak Search", padding=10)
        marker_peak_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.peak_search_button = ttk.Button(marker_peak_frame, text="Peak Search", command=None)
        self.peak_search_button.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

        self.peak_search_next_button = ttk.Button(marker_peak_frame, text="Next Peak", command=None)
        self.peak_search_next_button.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        # --- MARKER/READ Button ---
        self.read_markers_button = ttk.Button(read_markers_frame, text="Read All Markers", command=None)
        self.read_markers_button.grid(row=7, column=1, padx=5, pady=5, sticky="ew")

        # --- MARKER/PLACE/ALL Frame (from YakBegTab) ---
        marker_place_all_frame = ttk.LabelFrame(self, text="YakBeg - MARKER/PLACE/ALL", padding=10)
        marker_place_all_frame.pack(fill="x", padx=10, pady=5)
        marker_place_all_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        for i in range(6):
            ttk.Label(marker_place_all_frame, text=f"M{i+1} Freq (MHz):").grid(row=0, column=i, padx=5, pady=2, sticky="w")
            ttk.Entry(marker_place_all_frame, textvariable=self.marker_freq_vars[i]).grid(row=1, column=i, padx=5, pady=2, sticky="ew")

        self.marker_place_all_result_var = tk.StringVar(self, value="Result: N/A")
        ttk.Label(marker_place_all_frame, textvariable=self.marker_place_all_result_var, style="Dark.TLabel.Value").grid(row=2, column=0, columnspan=6, padx=5, pady=2, sticky="ew")
        
        ttk.Button(marker_place_all_frame, text="YakBeg - MARKER/PLACE/ALL", command=self._on_marker_place_all_beg).grid(row=3, column=0, columnspan=6, padx=5, pady=5, sticky="ew")

        debug_log(f"Widgets for Marker Settings Tab created. The controls are ready to go! 🗺️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

    def _on_marker_place_all_beg(self):
        """
        Handles the YakBeg - MARKER/PLACE/ALL command.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering function: {current_function}. Arrr, let's get these markers placed! 🧭",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        try:
            marker_freqs = [v.get() for v in self.marker_freq_vars]
            
            result = handle_marker_place_all_beg(
                app_instance=self.app_instance, 
                marker_freqs_mhz=marker_freqs,
                console_print_func=self.console_print_func
            )
            
            if result is not None:
                self.marker_place_all_result_var.set(f"Result: {result}")
            else:
                self.marker_place_all_result_var.set("Result: FAILED")
                
        except Exception as e:
            console_log(f"❌ Error in {current_function}: {e}", self.console_print_func)
            debug_log(f"Arrr, the code be capsized! The error be: {e}",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)