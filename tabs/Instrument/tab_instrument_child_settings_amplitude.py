# tabs/Instrument/tab_instrument_child_settings_amplitude.py
#
# This file defines the AmplitudeSettingsTab, a Tkinter Frame for controlling a spectrum
# analyzer's amplitude-related settings.
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
# NEW: Created a new file to encapsulate amplitude-related widgets from the original SettingsTab.

current_version = "20250815.103000.1"
current_version_hash = 20250815 * 103000 * 1

import tkinter as tk
from tkinter import ttk
import inspect
import os

from display.debug_logic import debug_log
from display.console_logic import console_log

class AmplitudeSettingsTab(ttk.Frame):
    """
    A Tkinter Frame that provides a user interface for amplitude settings.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the AmplitudeSettingsTab.
        """
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        self._create_widgets()
        self.preamp_state_var = self.app_instance.preamp_on_var
        self.high_sensitivity_state_var = self.app_instance.high_sensitivity_on_var
        self._set_ui_initial_state()
        
    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Amplitude Settings tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering _create_widgets. Creating widgets for the Amplitude Settings Tab. 🔊",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Amplitude/Ref Level Frame ---
        amplitude_frame = ttk.LabelFrame(self, text="Amplitude Settings", style='Dark.TLabelframe')
        amplitude_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        amplitude_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(amplitude_frame, text="Reference Level:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ref_levels = [40, 30, 20, 10, 0, -10, -20, -30, -40, -50, -60, -70, -80, -90, -100]
        self.ref_level_dropdown = ttk.Combobox(amplitude_frame, textvariable=self.app_instance.ref_level_dbm_var, values=ref_levels, state='readonly')
        self.ref_level_dropdown.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        # command=lambda e, app_ref=self.app_instance: set_reference_level(app_ref, app_ref.ref_level_dbm_var.get(), self.console_print_func)
        self.ref_level_dropdown.bind("<<ComboboxSelected>>", None)
        
        # Preamp Gain toggle button
        ttk.Label(amplitude_frame, text="Preamp Gain:", style='TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.preamp_toggle_button = ttk.Button(amplitude_frame, command=None)
        self.preamp_toggle_button.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # Attenuation Level dropdown
        ttk.Label(amplitude_frame, text="Power Attenuation:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.power_attenuation_var = tk.StringVar(self)
        att_levels = ["0", "10", "20", "30", "40", "50", "60", "70"]
        self.power_attenuation_dropdown = ttk.Combobox(amplitude_frame, textvariable=self.power_attenuation_var, values=att_levels, state='readonly')
        self.power_attenuation_dropdown.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        # command=lambda e, app_ref=self.app_instance: set_power_attenuation(app_ref, app_ref.power_attenuation_db_var.get(), self.console_print_func)
        self.power_attenuation_dropdown.bind("<<ComboboxSelected>>", None)

        # High Sensitivity toggle button
        ttk.Label(amplitude_frame, text="High Sensitivity:", style='TLabel').grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.hs_toggle_button = ttk.Button(amplitude_frame, command=None)
        self.hs_toggle_button.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        debug_log(f"Widgets for Amplitude Settings Tab created. The amplitude controls are ready! 📉",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

    def _set_ui_initial_state(self):
        """Sets the initial state of the UI elements."""
        self._update_toggle_button_style(self.preamp_toggle_button, self.preamp_state_var.get())
        self._update_toggle_button_style(self.hs_toggle_button, self.high_sensitivity_state_var.get())

    def _update_toggle_button_style(self, button, state):
        """Updates the style and text of a toggle button based on its state."""
        if state:
            button.config(style='Orange.TButton', text="ON")
        else:
            button.config(style='Dark.TButton', text="OFF")
