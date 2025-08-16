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
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250816.123518.26
# FIX: Sliders now snap to and only use values from the provided preset lists.
# FIX: The displayed values for the sliders no longer show decimal points.
# FIX: The _on_ref_level_change and _on_power_attenuation_change functions now correctly handle the push to YakSet.
# FIX: The `_update_descriptions` function has been improved to ensure discrete values are used.
# FIX: The `_update_toggle_button_style` function now correctly references the `tab_instance`.
# FIX: High Sensitivity toggle now explicitly refreshes UI values for reference level, power attenuation, and preamp.
# FIX: Corrected the TypeError by passing the tab_instance to the handler functions.
# FIX: Adjusted the grid layout to lock the Reference Level and Power Attenuation frames to a 50/50 proportional split,
#      preventing them from "jumping" due to text length changes.
# ADD: New logic to automatically disable High Sensitivity mode when other amplitude settings are adjusted.
# FIX: The logic in toggle_preamp has been updated to also turn off High Sensitivity when the preamp is disabled.

current_version = "Version 20250816.123518.26"
current_version_hash = (20250816 * 123518 * 26)

import tkinter as tk
from tkinter import ttk
import inspect
import os

from display.debug_logic import debug_log
from display.console_logic import console_log
from yak import utils_yak_setting_handler
from ref.ref_scanner_setting_lists import PRESET_AMPLITUDE_REFERENCE_LEVEL, PRESET_AMPLITUDE_POWER_ATTENUATION, PRESET_AMPLITUDE_PREAMP_STATE, PRESET_AMPLITUDE_HIGH_SENSITIVITY_STATE
from yak.Yakety_Yak import YakGet

class AmplitudeSettingsTab(ttk.Frame):
    """
    A Tkinter Frame that provides a user interface for amplitude settings.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the AmplitudeSettingsTab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Initializing AmplitudeSettingsTab. Setting up the GUI and its logic. 💻",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        
        self.is_ref_level_tracing = False
        self.is_attenuation_tracing = False

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
        amplitude_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        # --- FIX: Ensure 50/50 proportional split for child frames ---
        # We explicitly set weights and a minimum width to prevent the layout from "jumping"
        # when the description text changes.
        amplitude_frame.grid_columnconfigure(0, weight=1, minsize=100)
        amplitude_frame.grid_columnconfigure(1, weight=1, minsize=100)
        amplitude_frame.grid_rowconfigure(0, weight=1)

        # Container for Ref Level slider and labels
        ref_level_frame = ttk.LabelFrame(amplitude_frame, text="Reference Level (dBm)", style='Dark.TLabelframe')
        ref_level_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ref_level_frame.grid_columnconfigure(0, weight=1)
        ref_level_frame.grid_columnconfigure(1, weight=1)
        
        ref_values = [p["value"] for p in PRESET_AMPLITUDE_REFERENCE_LEVEL]
        ref_min = min(ref_values)
        ref_max = max(ref_values)
        self.ref_level_slider = ttk.Scale(ref_level_frame,
                                           orient="vertical",
                                           variable=self.app_instance.ref_level_dbm_var,
                                           from_=ref_max,
                                           to=ref_min,
                                           command=self._update_ref_level_display,
                                           length=200)
        self.ref_level_slider.grid(row=0, column=0, padx=10, pady=5, sticky="ns")
        self.ref_level_slider.bind("<ButtonRelease-1>", self._on_ref_level_change)
        
        ref_description_container = ttk.Frame(ref_level_frame)
        ref_description_container.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.ref_level_label = ttk.Label(ref_description_container, textvariable=self.app_instance.ref_level_dbm_var, style='TLabel')
        self.ref_level_label.grid(row=0, column=0)
        self.ref_level_description_label = ttk.Label(ref_description_container, text="", wraplength=150, style='Description.TLabel')
        self.ref_level_description_label.grid(row=1, column=0, padx=5, pady=2)


        # Container for Power Attenuation slider and labels
        power_att_frame = ttk.LabelFrame(amplitude_frame, text="Power Attenuation (dB)", style='Dark.TLabelframe')
        power_att_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        power_att_frame.grid_columnconfigure(0, weight=1)
        power_att_frame.grid_columnconfigure(1, weight=1)

        att_values = [p["value"] for p in PRESET_AMPLITUDE_POWER_ATTENUATION]
        att_min = min(att_values)
        att_max = max(att_values)
        self.power_attenuation_slider = ttk.Scale(power_att_frame,
                                                   orient="vertical",
                                                   variable=self.app_instance.power_attenuation_db_var,
                                                   from_=att_min,
                                                   to=att_max,
                                                   command=self._update_power_attenuation_display,
                                                   length=200)
        self.power_attenuation_slider.grid(row=0, column=0, padx=10, pady=5, sticky="ns")
        self.power_attenuation_slider.bind("<ButtonRelease-1>", self._on_power_attenuation_change)

        power_att_description_container = ttk.Frame(power_att_frame)
        power_att_description_container.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.power_attenuation_label = ttk.Label(power_att_description_container, textvariable=self.app_instance.power_attenuation_db_var, style='TLabel')
        self.power_attenuation_label.grid(row=0, column=0)
        self.power_attenuation_description_label = ttk.Label(power_att_description_container, text="", wraplength=150, style='Description.TLabel')
        self.power_attenuation_description_label.grid(row=1, column=0, padx=5, pady=2)

        # --- Preamp Gain Frame ---
        preamp_frame = ttk.LabelFrame(self, text="Preamp Gain", style='Dark.TLabelframe')
        preamp_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        preamp_frame.grid_columnconfigure(0, weight=1)

        self.preamp_toggle_button = ttk.Button(preamp_frame,
                                                command=lambda: utils_yak_setting_handler.toggle_preamp(tab_instance=self, app_instance=self.app_instance, console_print_func=self.console_print_func))
        self.preamp_toggle_button.grid(row=0, column=0, padx=5, pady=2, sticky="ew")

        # --- High Sensitivity Frame ---
        hs_frame = ttk.LabelFrame(self, text="High Sensitivity", style='Dark.TLabelframe')
        hs_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        hs_frame.grid_columnconfigure(0, weight=1)

        self.hs_toggle_button = ttk.Button(hs_frame,
                                            command=lambda: utils_yak_setting_handler.toggle_high_sensitivity(tab_instance=self, app_instance=self.app_instance, console_print_func=self.console_print_func))
        self.hs_toggle_button.grid(row=0, column=0, padx=5, pady=2, sticky="ew")

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

        self._update_descriptions(value=self.app_instance.ref_level_dbm_var.get(), preset_list=PRESET_AMPLITUDE_REFERENCE_LEVEL, label=self.ref_level_description_label, var=self.app_instance.ref_level_dbm_var)
        self._update_descriptions(value=self.app_instance.power_attenuation_db_var.get(), preset_list=PRESET_AMPLITUDE_POWER_ATTENUATION, label=self.power_attenuation_description_label, var=self.app_instance.power_attenuation_db_var)

    def _update_ref_level_display(self, value):
        if self.is_ref_level_tracing:
            return
        self.is_ref_level_tracing = True
        
        rounded_value = self._find_closest_preset_value(float(value), PRESET_AMPLITUDE_REFERENCE_LEVEL)
        self.app_instance.ref_level_dbm_var.set(rounded_value)
        self._update_descriptions(value=rounded_value, preset_list=PRESET_AMPLITUDE_REFERENCE_LEVEL, label=self.ref_level_description_label, var=self.app_instance.ref_level_dbm_var)
        
        self.is_ref_level_tracing = False

    def _update_power_attenuation_display(self, value):
        if self.is_attenuation_tracing:
            return
        self.is_attenuation_tracing = True
        
        rounded_value = self._find_closest_preset_value(float(value), PRESET_AMPLITUDE_POWER_ATTENUATION)
        self.app_instance.power_attenuation_db_var.set(rounded_value)
        self._update_descriptions(value=rounded_value, preset_list=PRESET_AMPLITUDE_POWER_ATTENUATION, label=self.power_attenuation_description_label, var=self.app_instance.power_attenuation_db_var)
        
        self.is_attenuation_tracing = False

    def _on_ref_level_change(self, event):
        """Updates the reference level and pushes the setting on slider release."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function}. Slider released, pushing new value to instrument. 📤",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        # New Logic: Turn off High Sensitivity if it's on
        if self.app_instance.high_sensitivity_on_var.get():
            self.console_print_func("⚠️ High Sensitivity turned off to adjust Reference Level.")
            utils_yak_setting_handler.toggle_high_sensitivity(tab_instance=self, app_instance=self.app_instance, console_print_func=self.console_print_func)

        ref_level = int(self._find_closest_preset_value(self.app_instance.ref_level_dbm_var.get(), PRESET_AMPLITUDE_REFERENCE_LEVEL))
        utils_yak_setting_handler.set_reference_level(tab_instance=self, app_instance=self.app_instance, value=ref_level, console_print_func=self.console_print_func)

    def _on_power_attenuation_change(self, event):
        """Updates the power attenuation and pushes the setting on slider release."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function}. Slider released, pushing new value to instrument. 📤",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        # New Logic: Turn off High Sensitivity if it's on
        if self.app_instance.high_sensitivity_on_var.get():
            self.console_print_func("⚠️ High Sensitivity turned off to adjust Power Attenuation.")
            utils_yak_setting_handler.toggle_high_sensitivity(tab_instance=self, app_instance=self.app_instance, console_print_func=self.console_print_func)

        power_attenuation = int(self._find_closest_preset_value(self.app_instance.power_attenuation_db_var.get(), PRESET_AMPLITUDE_POWER_ATTENUATION))
        utils_yak_setting_handler.set_power_attenuation(tab_instance=self, app_instance=self.app_instance, value=power_attenuation, console_print_func=self.console_print_func)

    def _update_toggle_button_style(self, button, state):
        """Updates the style and text of a toggle button based on its state."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function}. Updating button style for state: {state} 🤔",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        # Determine the correct preset list to use based on the button instance
        preset_list = None
        if button == self.preamp_toggle_button:
            preset_list = PRESET_AMPLITUDE_PREAMP_STATE
        elif button == self.hs_toggle_button:
            preset_list = PRESET_AMPLITUDE_HIGH_SENSITIVITY_STATE
            
        if preset_list:
            if state:
                button.config(style='Orange.TButton', text=next((p['label'] for p in preset_list if p['value'] == 'ON'), "ON"))
            else:
                button.config(style='Dark.TButton', text=next((p['label'] for p in preset_list if p['value'] == 'OFF'), "OFF"))

        # After toggling, refresh all status on the page
        app_instance = self.app_instance
        YakGet(app_instance, "AMPLITUDE/REFERENCE LEVEL", self.console_print_func)
        YakGet(app_instance, "AMPLITUDE/POWER/ATTENUATION", self.console_print_func)
        YakGet(app_instance, "AMPLITUDE/POWER/GAIN", self.console_print_func)
        YakGet(app_instance, "AMPLITUDE/POWER/HIGH SENSITIVE", self.console_print_func)

    def _find_closest_preset_value(self, value, preset_list):
        """Finds the closest discrete preset value for a given float value."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function}. Finding closest preset for value: {value}",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        values = [p["value"] for p in preset_list]
        return min(values, key=lambda x: abs(x - value))

    def _update_descriptions(self, value, preset_list, label, var):
        """
        Updates a description label and the variable value based on the slider value
        by finding the closest preset and snapping to it.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function}. Seeking the closest preset for a value of {value}...",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        # Find the closest preset value first
        closest_value = self._find_closest_preset_value(value, preset_list)
        
        closest_preset = next((preset for preset in preset_list if preset["value"] == closest_value), None)

        if closest_preset:
            var.set(closest_preset["value"])
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