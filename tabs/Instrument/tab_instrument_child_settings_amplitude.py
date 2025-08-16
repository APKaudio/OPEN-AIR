# tabs/Instrument/tab_instrument_child_settings_amplitude.py
#
# This file defines the AmplitudeSettingsTab, a Tkinter Frame for controlling a spectrum
# analyzer's amplitude-related settings. It has been updated to use vertical sliders
# and a single 'apply' button to push all settings at once.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250815.174900.3
# REFACTOR: Replaced comboboxes with vertical sliders for reference level and power attenuation.
# NEW: Added a single 'Apply' button to push all amplitude settings at once.
# REFACTOR: Now imports and uses the preset values from ref_scanner_setting_lists.py.
# NEW: Added labels to display the descriptions of the selected amplitude settings.
# FIX: Removed the 'console_print_func' argument from the debug_log calls to fix a TypeError.

current_version = "20250815.174900.3"
current_version_hash = (20250815 * 174900 * 3)

import tkinter as tk
from tkinter import ttk
import inspect
import os

from display.debug_logic import debug_log
from display.console_logic import console_log
from yak import utils_yak_setting_handler
from ref.ref_scanner_setting_lists import PREST_AMPLITUDE_REFERENCE_LEVEL, PREST_AMPLITUDE_POWER_ATTENUATION

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
        debug_log(message=f"Entering {current_function}. The mad scientist is preparing the amplitude controls! 🔊🧪",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Amplitude/Ref Level Frame ---
        amplitude_frame = ttk.LabelFrame(self, text="Amplitude Settings", style='Dark.TLabelframe')
        amplitude_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        amplitude_frame.grid_columnconfigure(0, weight=1)
        amplitude_frame.grid_rowconfigure(0, weight=1)

        # Container for sliders and labels
        slider_container = ttk.Frame(amplitude_frame, style='Dark.TFrame')
        slider_container.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        slider_container.grid_columnconfigure(0, weight=1)
        slider_container.grid_columnconfigure(1, weight=1)
        
        # Reference Level Slider
        ttk.Label(slider_container, text="Reference Level (dBm)").grid(row=0, column=0, padx=5, pady=2)
        ref_values = [p["value"] for p in PREST_AMPLITUDE_REFERENCE_LEVEL]
        ref_min = min(ref_values)
        ref_max = max(ref_values)
        self.ref_level_slider = ttk.Scale(slider_container,
                                         orient="vertical",
                                         variable=self.app_instance.ref_level_dbm_var,
                                         from_=ref_max,
                                         to=ref_min,
                                         command=lambda value: self._update_descriptions(value=value, preset_list=PREST_AMPLITUDE_REFERENCE_LEVEL, label=self.ref_level_description_label, var=self.app_instance.ref_level_dbm_var),
                                         length=200)
        self.ref_level_slider.grid(row=1, column=0, padx=10, pady=5, sticky="ns")
        self.ref_level_label = ttk.Label(slider_container, textvariable=self.app_instance.ref_level_dbm_var, style='TLabel')
        self.ref_level_label.grid(row=2, column=0)
        self.ref_level_description_label = ttk.Label(slider_container, text="", wraplength=150, style='Description.TLabel')
        self.ref_level_description_label.grid(row=3, column=0, padx=5, pady=2)

        # Power Attenuation Slider
        ttk.Label(slider_container, text="Power Attenuation (dB)").grid(row=0, column=1, padx=5, pady=2)
        att_values = [p["value"] for p in PREST_AMPLITUDE_POWER_ATTENUATION]
        att_min = min(att_values)
        att_max = max(att_values)
        self.power_attenuation_slider = ttk.Scale(slider_container,
                                                orient="vertical",
                                                variable=self.app_instance.power_attenuation_db_var,
                                                from_=att_max,
                                                to=att_min,
                                                command=lambda value: self._update_descriptions(value=value, preset_list=PREST_AMPLITUDE_POWER_ATTENUATION, label=self.power_attenuation_description_label, var=self.app_instance.power_attenuation_db_var),
                                                length=200)
        self.power_attenuation_slider.grid(row=1, column=1, padx=10, pady=5, sticky="ns")
        self.power_attenuation_label = ttk.Label(slider_container, textvariable=self.app_instance.power_attenuation_db_var, style='TLabel')
        self.power_attenuation_label.grid(row=2, column=1)
        self.power_attenuation_description_label = ttk.Label(slider_container, text="", wraplength=150, style='Description.TLabel')
        self.power_attenuation_description_label.grid(row=3, column=1, padx=5, pady=2)

        # Toggle buttons container
        button_container = ttk.Frame(amplitude_frame, style='Dark.TFrame')
        button_container.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        button_container.grid_columnconfigure(0, weight=1)
        button_container.grid_columnconfigure(1, weight=1)

        # Preamp Gain toggle button
        ttk.Label(button_container, text="Preamp Gain:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.preamp_toggle_button = ttk.Button(button_container,
                                               command=lambda: utils_yak_setting_handler.toggle_preamp(app_instance=self.app_instance, console_print_func=self.console_print_func))
        self.preamp_toggle_button.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        # High Sensitivity toggle button
        ttk.Label(button_container, text="High Sensitivity:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.hs_toggle_button = ttk.Button(button_container,
                                           command=lambda: utils_yak_setting_handler.toggle_high_sensitivity(app_instance=self.app_instance, console_print_func=self.console_print_func))
        self.hs_toggle_button.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # Apply All Settings button
        apply_button = ttk.Button(amplitude_frame,
                                  text="Apply All Amplitude Settings",
                                  style='Orange.TButton',
                                  command=self._apply_amplitude_settings)
        apply_button.grid(row=2, column=0, padx=5, pady=10, sticky="ew")

        debug_log(message=f"Widgets for Amplitude Settings Tab created. The amplitude controls are ready! 📉👍",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

    def _set_ui_initial_state(self):
        """Sets the initial state of the UI elements."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function}. Initializing UI state. 🎨",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        self._update_toggle_button_style(button=self.preamp_toggle_button, state=self.preamp_state_var.get())
        self._update_toggle_button_style(button=self.hs_toggle_button, state=self.high_sensitivity_state_var.get())
        
        self.ref_level_slider.set(self.app_instance.ref_level_dbm_var.get())
        self.power_attenuation_slider.set(self.app_instance.power_attenuation_db_var.get())

        self._update_descriptions(value=self.app_instance.ref_level_dbm_var.get(), preset_list=PREST_AMPLITUDE_REFERENCE_LEVEL, label=self.ref_level_description_label, var=self.app_instance.ref_level_dbm_var)
        self._update_descriptions(value=self.app_instance.power_attenuation_db_var.get(), preset_list=PREST_AMPLITUDE_POWER_ATTENUATION, label=self.power_attenuation_description_label, var=self.app_instance.power_attenuation_db_var)


    def _update_toggle_button_style(self, button, state):
        """Updates the style and text of a toggle button based on its state."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function}. Updating button style for state: {state} 🤔",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        if state:
            button.config(style='Orange.TButton', text="ON")
        else:
            button.config(style='Dark.TButton', text="OFF")

    def _update_descriptions(self, value, preset_list, label, var):
        """
        Updates a description label based on the slider value by finding the closest preset.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function}. Seeking the closest preset for a value of {value}...",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        var.set(round(float(value)))

        closest_preset = None
        min_diff = float('inf')

        for preset in preset_list:
            diff = abs(preset["value"] - var.get())
            if diff < min_diff:
                min_diff = diff
                closest_preset = preset

        if closest_preset:
            label.config(text=closest_preset["description"])
            debug_log(message=f"Found a description! ' {closest_preset['description']} '",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
        else:
            label.config(text="No matching description found.")
            debug_log(message=f"Arrr, no description to be found! Shiver me timbers! 🏴‍☠️",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)

    def _apply_amplitude_settings(self):
        """
        Pushes the current settings from the GUI to the instrument.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function}. Acknowledging a request to apply settings. This could be a quantum leap! ⚛️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        try:
            ref_level = self.app_instance.ref_level_dbm_var.get()
            attenuation = self.app_instance.power_attenuation_db_var.get()

            # Using named arguments as requested
            utils_yak_setting_handler.set_reference_level(app_instance=self.app_instance, value=ref_level, console_print_func=self.console_print_func)
            utils_yak_setting_handler.set_power_attenuation(app_instance=self.app_instance, value=attenuation, console_print_func=self.console_print_func)

            self.console_print_func("✅ All amplitude settings applied successfully.")
            debug_log(message=f"The Amplitude Settings have been applied! Reference Level: {ref_level}, Attenuation: {attenuation} 🎉",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)

        except Exception as e:
            self.console_print_func(f"❌ Error applying amplitude settings: {e}")
            debug_log(message=f"Arrr, the code be capsized! Error applying amplitude settings: {e} 🏴‍☠️",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
