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
# Version 20250815.105500.1
# NEW: Added YakBeg functionality for markers.

current_version = "20250815.105500.1"
current_version_hash = 20250815 * 105500 * 1

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
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the MarkerSettingsTab.
        """
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        self.marker_vars = [
            self.app_instance.marker1_on_var,
            self.app_instance.marker2_on_var,
            self.app_instance.marker3_on_var,
            self.app_instance.marker4_on_var,
            self.app_instance.marker5_on_var,
            self.app_instance.marker6_on_var,
        ]
        self.marker_value_labels = []

        # Tkinter variables for Marker/Place/All
        self.marker_freq_vars = [tk.StringVar(self, value="111"), tk.StringVar(self, value="222"),
                                 tk.StringVar(self, value="333"), tk.StringVar(self, value="444"),
                                 tk.StringVar(self, value="555"), tk.StringVar(self, value="666")]
        self.marker_place_all_result_var = tk.StringVar(self, value="Result: N/A")
        self._create_widgets()

    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Marker Settings tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering _create_widgets. Creating widgets for the Marker Settings Tab. 📍",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Marker Settings Frame ---
        marker_frame = ttk.LabelFrame(self, text="Marker Settings", style='Dark.TLabelframe')
        marker_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        marker_frame.grid_columnconfigure(0, weight=1)
        marker_frame.grid_columnconfigure(1, weight=1)

        # --- Frame for "Turn On All Markers" and "Peak search" ---
        turn_on_markers_frame = ttk.Frame(marker_frame, style='Dark.TFrame')
        turn_on_markers_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        turn_on_markers_frame.grid_columnconfigure(0, weight=1)
        turn_on_markers_frame.grid_columnconfigure(1, weight=1)

        self.turn_all_markers_on_button = ttk.Button(turn_on_markers_frame, text="Turn All Markers On", command=None)
        self.turn_all_markers_on_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Peak search button
        self.peak_search_button = ttk.Button(turn_on_markers_frame, text="Peak search", command=None, style='Blue.TButton')
        self.peak_search_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # --- Frame for "Read All Markers" ---
        read_markers_frame = ttk.Frame(marker_frame, style='Dark.TFrame')
        read_markers_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        read_markers_frame.grid_columnconfigure(1, weight=1)
        read_markers_frame.grid_rowconfigure(7, weight=1)
        
        ttk.Label(read_markers_frame, text="Marker Values:").grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        # Marker On/Off checkboxes
        for i in range(6):
            cb = ttk.Checkbutton(read_markers_frame, text=f"Marker {i+1} On", variable=self.marker_vars[i], command=None)
            cb.grid(row=i+1, column=0, padx=5, pady=2, sticky="w")
        
            # Placeholder for Marker X/Y display
            label = ttk.Label(read_markers_frame, text="X: N/A, Y: N/A", style='Dark.TLabel.Value')
            label.grid(row=i+1, column=1, padx=5, pady=2, sticky="ew")
            self.marker_value_labels.append(label)

        # Read marker values button
        self.read_markers_button = ttk.Button(read_markers_frame, text="Read All Markers", command=None)
        self.read_markers_button.grid(row=7, column=1, padx=5, pady=5, sticky="ew")

        # --- MARKER/PLACE/ALL Frame (from YakBegTab) ---
        marker_place_all_frame = ttk.LabelFrame(self, text="YakBeg - MARKER/PLACE/ALL", padding=10)
        marker_place_all_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        marker_place_all_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        for i in range(6):
            ttk.Label(marker_place_all_frame, text=f"M{i+1} Freq (MHz):").grid(row=0, column=i, padx=5, pady=2, sticky="w")
            ttk.Entry(marker_place_all_frame, textvariable=self.marker_freq_vars[i]).grid(row=1, column=i, padx=5, pady=2, sticky="ew")

        self.marker_place_all_result_var = tk.StringVar(self, value="Result: N/A")
        ttk.Label(marker_place_all_frame, textvariable=self.marker_place_all_result_var, style="Dark.TLabel.Value").grid(row=2, column=0, columnspan=6, padx=5, pady=2, sticky="ew")

        ttk.Button(marker_place_all_frame, text="YakBeg - MARKER/PLACE/ALL", command=self._on_marker_place_all_beg).grid(row=3, column=0, columnspan=6, padx=5, pady=5, sticky="ew")


        debug_log(f"Widgets for Marker Settings Tab created. The marker controls are ready! 📊",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
