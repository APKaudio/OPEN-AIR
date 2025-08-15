# tabs/Instrument/tab_instrument_child_settings_Bandwidth.py
#
# This file defines the BandwidthSettingsTab, a Tkinter Frame for controlling a spectrum
# analyzer's bandwidth and initiate settings.
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
# Version 20250815.103000.1
# NEW: Created a new file to encapsulate bandwidth and initiate widgets from the original SettingsTab.

current_version = "20250815.103000.1"
current_version_hash = 20250815 * 103000 * 1

import tkinter as tk
from tkinter import ttk
import inspect
import os

from display.debug_logic import debug_log
from display.console_logic import console_log

class BandwidthSettingsTab(ttk.Frame):
    """
    A Tkinter Frame that provides a user interface for bandwidth and initiate settings.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the BandwidthSettingsTab.
        """
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        self.vbw_auto_state_var = self.app_instance.vbw_auto_on_var
        self._create_widgets()
        self._set_ui_initial_state()
        
    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Bandwidth Settings tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering _create_widgets. Creating widgets for the Bandwidth Settings Tab. ⚙️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Bandwidth Settings Frame ---
        bandwidth_frame = ttk.LabelFrame(self, text="Bandwidth Settings", style='Dark.TLabelframe')
        bandwidth_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        bandwidth_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(bandwidth_frame, text="Resolution BW (MHz):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.rbw_entry = ttk.Entry(bandwidth_frame, textvariable=self.app_instance.rbw_mhz_var, style='TEntry')
        self.rbw_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        # command=lambda e, app_ref=self.app_instance: set_resolution_bandwidth(app_ref, app_ref.rbw_mhz_var.get(), self.console_print_func)
        self.rbw_entry.bind("<FocusOut>", None)
        
        ttk.Label(bandwidth_frame, text="Video BW (MHz):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.vbw_entry = ttk.Entry(bandwidth_frame, textvariable=self.app_instance.vbw_mhz_var, style='TEntry')
        self.vbw_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        # command=lambda e, app_ref=self.app_instance: set_video_bandwidth(app_ref, app_ref.vbw_mhz_var.get(), self.console_print_func)
        self.vbw_entry.bind("<FocusOut>", None)

        ttk.Label(bandwidth_frame, text="VBW Auto:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.vbw_auto_toggle_button = ttk.Button(bandwidth_frame, command=None)
        self.vbw_auto_toggle_button.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        # --- Initiate Settings Frame ---
        initiate_frame = ttk.LabelFrame(self, text="Initiate Settings", style='Dark.TLabelframe')
        initiate_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        initiate_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(initiate_frame, text="Continuous Mode:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        initiate_modes = ["ON", "OFF"]
        self.initiate_continuous_dropdown = ttk.Combobox(initiate_frame, textvariable=self.app_instance.initiate_continuous_on_var, values=initiate_modes, state='readonly')
        self.initiate_continuous_dropdown.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        # command=lambda e, app_ref=self.app_instance: set_continuous_initiate_mode(app_ref, app_ref.initiate_continuous_on_var.get(), self.console_print_func)
        self.initiate_continuous_dropdown.bind("<<ComboboxSelected>>", None)
        
        self.initiate_immediate_button = ttk.Button(initiate_frame, text="Initiate Immediate", command=None)
        self.initiate_immediate_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        debug_log(f"Widgets for Bandwidth Settings Tab created. Bandwidth controls are ready! 🛠️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

    def _set_ui_initial_state(self):
        """Sets the initial state of the UI elements."""
        self._update_toggle_button_style(self.vbw_auto_toggle_button, self.vbw_auto_state_var.get())

    def _update_toggle_button_style(self, button, state):
        """Updates the style and text of a toggle button based on its state."""
        if state:
            button.config(style='Orange.TButton', text="ON")
        else:
            button.config(style='Dark.TButton', text="OFF")
