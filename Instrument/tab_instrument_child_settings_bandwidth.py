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
# Version 20250819.004500.1
# REFACTORED: Simplified averaging UI to a single toggle button and count dropdown for Trace 1.
# FIXED: Corrected the import path for the `handle_bandwidth_settings_nab` handler.
# FIXED: Corrected the `YakSet` command format in the `set_trace_averaging_count` handler.

current_version = "20250819.004500.1"
current_version_hash = 20250819 * 4500 * 1

import tkinter as tk
from tkinter import ttk
import inspect
import os
import re

from display.debug_logic import debug_log
from display.console_logic import console_log

# Import handler functions and preset lists
from yak import utils_yak_setting_handler
from ref.ref_scanner_setting_lists import (
    PRESET_BANDWIDTH_RBW,
    PRESET_BANDWIDTH_VIDEO,
    PRESET_CONTINUOUS_MODE,
    PRESET_AVERAGING
)
# FIXED: Corrected the import path for the NAB handler
from yak.utils_yaknab_handler import handle_bandwidth_settings_nab

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

        # Local Tkinter variables for the UI. They will be linked to app_instance's variables
        # when they become available.
        self.rbw_hz_var = tk.DoubleVar(self, value=0.0)
        self.vbw_hz_var = tk.DoubleVar(self, value=0.0)
        self.vbw_auto_state_var = tk.BooleanVar(self, value=False)
        self.continuous_mode_var = tk.StringVar(self, value="OFF")

        # NEW: Variables for averaging controls (single trace only)
        self.average_on_var = tk.BooleanVar(self, value=False)
        self.average_count_var = tk.IntVar(self, value=0)
        
        # NEW: Variables to hold the parsed NAB response values
        self.parsed_rbw_var = tk.StringVar(self, value="N/A")
        self.parsed_vbw_var = tk.StringVar(self, value="N/A")
        self.parsed_vbw_auto_var = tk.StringVar(self, value="N/A")
        self.parsed_continuous_mode_var = tk.StringVar(self, value="N/A")
        self.parsed_averaging_status_var = tk.StringVar(self, value="N/A")
        self.parsed_averaging_count_var = tk.StringVar(self, value="N/A")
        
        # NEW: Response variable for the averaging controls
        self.averaging_result_var = tk.StringVar(self, value="Result: N/A")
        
        self.last_known_rbw_hz = 0.0
        self.last_known_vbw_hz = 0.0

        self._create_widgets()

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

        ttk.Label(bandwidth_frame, text="Resolution BW (Hz):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        rbw_labels = [f"{p['label']} ({p['value']} Hz)" for p in PRESET_BANDWIDTH_RBW]
        self.rbw_combobox = ttk.Combobox(bandwidth_frame,
                                         textvariable=self.rbw_hz_var,
                                         values=rbw_labels,
                                         state='readonly')
        self.rbw_combobox.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.rbw_combobox.bind("<<ComboboxSelected>>", self._on_rbw_selected)
        
        # --- VBW Controls (Rebuilt as Combobox and Auto button) ---
        ttk.Label(bandwidth_frame, text="Video BW (Hz):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        
        vbw_values = [p["value"] for p in PRESET_BANDWIDTH_VIDEO]
        vbw_labels = [f"{p['label']} ({p['value']} Hz)" for p in PRESET_BANDWIDTH_VIDEO]
        self.vbw_combobox = ttk.Combobox(bandwidth_frame,
                                         textvariable=self.vbw_hz_var,
                                         values=vbw_labels,
                                         state='readonly')
        self.vbw_combobox.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.vbw_combobox.bind("<<ComboboxSelected>>", self._on_vbw_selected)

        ttk.Label(bandwidth_frame, text="VBW Auto:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.vbw_auto_toggle_button = ttk.Button(bandwidth_frame,
                                                 text="",
                                                 command=self._on_vbw_auto_toggle)
        self.vbw_auto_toggle_button.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        # --- Initiate Settings Frame ---
        initiate_frame = ttk.LabelFrame(self, text="Initiate Settings", style='Dark.TLabelframe')
        initiate_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        initiate_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(initiate_frame, text="Continuous Mode:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        initiate_modes = [p['value'] for p in PRESET_CONTINUOUS_MODE]
        self.initiate_continuous_dropdown = ttk.Combobox(initiate_frame,
                                                         textvariable=self.continuous_mode_var,
                                                         values=initiate_modes,
                                                         state='readonly')
        self.initiate_continuous_dropdown.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.initiate_continuous_dropdown.bind("<<ComboboxSelected>>", self._on_continuous_mode_change)
        
        self.initiate_immediate_button = ttk.Button(initiate_frame,
                                                     text="Initiate Immediate",
                                                     command=lambda: utils_yak_setting_handler.do_immediate_initiate(self.app_instance, self.console_print_func))
        self.initiate_immediate_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # NEW: Averaging Frame (Updated layout for Trace 1 only)
        averaging_frame = ttk.LabelFrame(self, text="Averaging", style='Dark.TLabelframe')
        averaging_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        averaging_frame.grid_columnconfigure((1, 3), weight=1)

        # Row 0: Averaging Toggle and Count
        ttk.Label(averaging_frame, text="Trace 1 Averaging:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.average_on_button = ttk.Button(averaging_frame, text="OFF", command=lambda: self._on_averaging_toggle(1, not self.average_on_var.get()), style='Red.TButton')
        self.average_on_button.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(averaging_frame, text="Count:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        avg_labels = [f"{p['value']} - {p['label']}" for p in PRESET_AVERAGING]
        self.average_count_dropdown = ttk.Combobox(averaging_frame, textvariable=self.average_count_var, values=avg_labels, state='readonly')
        self.average_count_dropdown.grid(row=0, column=3, padx=5, pady=2, sticky="ew")
        self.average_count_dropdown.bind("<<ComboboxSelected>>", lambda event: self._on_averaging_count_selected(event, 1))

        # NEW: Result label for averaging actions
        ttk.Label(averaging_frame, textvariable=self.averaging_result_var, style="Dark.TLabel.Value").grid(row=1, column=0, columnspan=4, padx=5, pady=2, sticky="ew")


        # Frame for NAB raw response display
        parsed_nab_response_frame = ttk.LabelFrame(self, text="Parsed NAB Response", style='Dark.TLabelframe')
        parsed_nab_response_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        parsed_nab_response_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(parsed_nab_response_frame, text="RBW (Hz):", style='TLabel').grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(parsed_nab_response_frame, textvariable=self.parsed_rbw_var, style='Dark.TLabel.Value').grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(parsed_nab_response_frame, text="VBW (Hz):", style='TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(parsed_nab_response_frame, textvariable=self.parsed_vbw_var, style='Dark.TLabel.Value').grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(parsed_nab_response_frame, text="VBW Auto:", style='TLabel').grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(parsed_nab_response_frame, textvariable=self.parsed_vbw_auto_var, style='Dark.TLabel.Value').grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(parsed_nab_response_frame, text="Continuous:", style='TLabel').grid(row=3, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(parsed_nab_response_frame, textvariable=self.parsed_continuous_mode_var, style='Dark.TLabel.Value').grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        
        # NEW: Add a sweep time display field
        ttk.Label(parsed_nab_response_frame, text="Sweep Time (s):", style='TLabel').grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.parsed_sweep_time_var = tk.StringVar(self, value="N/A")
        ttk.Label(parsed_nab_response_frame, textvariable=self.parsed_sweep_time_var, style='Dark.TLabel.Value').grid(row=4, column=1, padx=5, pady=2, sticky="ew")


        debug_log(f"Widgets for Bandwidth Settings Tab created. Bandwidth controls are ready! 🛠️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

    def _on_averaging_toggle(self, trace_number, state):
        """
        Handler for when an averaging toggle button is clicked.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Averaging toggle for trace {trace_number} clicked. State: {state}",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        if utils_yak_setting_handler.toggle_trace_averaging(app_instance=self.app_instance, trace_number=trace_number, is_on=state, console_print_func=self.console_print_func):
            self.averaging_result_var.set(f"Result: Trace {trace_number} averaging set to {'ON' if state else 'OFF'}.")
            self._sync_ui_from_app_state()
        else:
            self.averaging_result_var.set("Result: FAILED")
            self._sync_ui_from_app_state()


    def _on_averaging_count_selected(self, event, trace_number):
        current_function = inspect.currentframe().f_code.co_name
        selected_text = event.widget.get()
        match = re.search(r'(\d+)', selected_text)
        
        if 'Off' in selected_text:
            count = 0
            state = False
        elif match:
            count = int(match.group(1))
            state = True
        else:
            self.console_print_func(f"❌ Could not parse averaging count from '{selected_text}'.")
            self.averaging_result_var.set("Result: FAILED to parse count")
            return
            
        debug_log(f"Averaging count for trace {trace_number} selected: {count}, state: {state}", file=os.path.basename(__file__), version=current_version, function=current_function)
        
        if utils_yak_setting_handler.set_trace_averaging_count(app_instance=self.app_instance, trace_number=trace_number, count=count, console_print_func=self.console_print_func) and \
           utils_yak_setting_handler.toggle_trace_averaging(app_instance=self.app_instance, trace_number=trace_number, is_on=state, console_print_func=self.console_print_func):
            self.averaging_result_var.set(f"Result: Trace {trace_number} averaging set to {count} sweeps.")
            self._sync_ui_from_app_state()
        else:
            self.averaging_result_var.set("Result: FAILED")
            self._sync_ui_from_app_state()

    def _on_tab_selected(self, event=None):
        """
        Called when this tab is selected. Syncs the UI with the application's state.
        """
        if self.app_instance.is_connected.get():
            self._sync_ui_from_app_state()
        else:
            self.console_print_func("❌ No instrument connected. Skipping UI refresh.")


    def _sync_ui_from_app_state(self):
        """
        Sets the UI element values from the application's variables.
        This function now calls the NAB handler to get the current state from the instrument.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}. Syncing UI from app state. �",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
                  
        if not self.app_instance.is_connected.get():
            debug_log(f"Not connected, skipping NAB query and falling back to app instance variables.",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
            # Fall back to app_instance variables if not connected
            if hasattr(self.app_instance, 'rbw_hz_var'):
                self.rbw_hz_var.set(self.app_instance.rbw_hz_var.get())
            if hasattr(self.app_instance, 'vbw_hz_var'):
                self.vbw_hz_var.set(self.app_instance.vbw_hz_var.get())
            if hasattr(self.app_instance, 'vbw_auto_on_var'):
                self.vbw_auto_state_var.set(self.app_instance.vbw_auto_on_var.get())
            if hasattr(self.app_instance, 'initiate_continuous_on_var'):
                self.continuous_mode_var.set(self.app_instance.initiate_continuous_on_var.get())
            
            # NEW: Set averaging vars from app_instance
            if hasattr(self.app_instance, 'trace1_average_on_var'):
                self.average_on_var.set(self.app_instance.trace1_average_on_var.get())
            if hasattr(self.app_instance, 'trace1_average_count_var'):
                self.average_count_var.set(self.app_instance.trace1_average_count_var.get())


            self._update_rbw_combobox_display()
            self._update_vbw_combobox_display()
            self._update_toggle_button_style(self.vbw_auto_toggle_button, self.vbw_auto_state_var.get())
            
            if self.vbw_auto_state_var.get():
                self.vbw_combobox.config(state='disabled')
            else:
                self.vbw_combobox.config(state='readonly')
            return

        # Call the NAB handler to get all settings in one go.
        settings = handle_bandwidth_settings_nab(self.app_instance, self.console_print_func)

        # Update the parsed response display variables
        if settings:
            self.parsed_rbw_var.set(f"{settings['RBW_Hz']:.0f} Hz")
            self.parsed_vbw_var.set(f"{settings['VBW_Hz']:.0f} Hz")
            self.parsed_vbw_auto_var.set("ON" if settings["VBW_Auto_On"] else "OFF")
            self.parsed_continuous_mode_var.set("ON" if settings["Continuous_Mode_On"] else "OFF")
            
            # NEW: Set the sweep time variable
            self.parsed_sweep_time_var.set(f"{settings['Sweep_Time_s']:.3f} s")


            # Update local Tkinter variables and button states from the NAB response
            self.rbw_hz_var.set(settings["RBW_Hz"])
            self.vbw_hz_var.set(settings["VBW_Hz"])
            self.vbw_auto_state_var.set(settings["VBW_Auto_On"])
            self.continuous_mode_var.set("ON" if settings["Continuous_Mode_On"] else "OFF")
            
            # NEW: Update averaging vars from NAB response for Trace 1 only
            avg_on, avg_count = utils_yak_setting_handler.get_trace_averaging_settings(self.app_instance, 1, self.console_print_func)
            
            # Update the state toggle button
            self.average_on_var.set(avg_on)
            self._update_toggle_button_style(self.average_on_button, avg_on)
            
            # Update the count dropdown
            self.average_count_var.set(avg_count)
            
            # Update the combobox displays
            self._update_rbw_combobox_display()
            self._update_vbw_combobox_display()

            # Update the toggle button styles
            self._update_toggle_button_style(self.vbw_auto_toggle_button, settings["VBW_Auto_On"])

            # Disable VBW combobox if VBW auto is on
            if self.vbw_auto_state_var.get():
                self.vbw_combobox.config(state='disabled')
            else:
                self.vbw_combobox.config(state='readonly')
        else:
            debug_log("NAB query failed. Falling back to app instance variables.",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
            # If the NAB call failed, fall back to app_instance variables
            self.rbw_hz_var.set(self.app_instance.rbw_hz_var.get())
            self.vbw_hz_var.set(self.app_instance.vbw_hz_var.get())
            self.vbw_auto_state_var.set(self.app_instance.vbw_auto_on_var.get())
            self.continuous_mode_var.set(self.app_instance.initiate_continuous_on_var.get())
            
            # NEW: Set averaging vars from app_instance
            if hasattr(self.app_instance, 'trace1_average_on_var'):
                self.average_on_var.set(self.app_instance.trace1_average_on_var.get())
            if hasattr(self.app_instance, 'trace1_average_count_var'):
                self.average_count_var.set(self.app_instance.trace1_average_count_var.get())

            self._update_rbw_combobox_display()
            self._update_vbw_combobox_display()
            self._update_toggle_button_style(self.vbw_auto_toggle_button, self.vbw_auto_state_var.get())
            if self.vbw_auto_state_var.get():
                self.vbw_combobox.config(state='disabled')
            else:
                self.vbw_combobox.config(state='readonly')


    def _update_toggle_button_style(self, button, state):
        """Updates the style and text of a toggle button based on its state."""
        if state:
            button.config(text="ON", style='Green.TButton')
        else:
            button.config(text="OFF", style='Red.TButton')

    def _update_rbw_combobox_display(self):
        """Updates the RBW combobox to show the current value."""
        current_rbw_hz = int(self.rbw_hz_var.get())
        found_label = "Custom"
        for preset in PRESET_BANDWIDTH_RBW:
            if preset["value"] == current_rbw_hz:
                found_label = f"{preset['label']} ({preset['value']} Hz)"
                break
        self.rbw_combobox.set(found_label)

    def _update_vbw_combobox_display(self):
        """Updates the VBW combobox to show the current value."""
        current_vbw_hz = int(self.vbw_hz_var.get())
        found_label = "Custom"
        for preset in PRESET_BANDWIDTH_VIDEO:
            if preset["value"] == current_vbw_hz:
                found_label = f"{preset['label']} ({preset['value']} Hz)"
                break
        self.vbw_combobox.set(found_label)

    def _on_rbw_selected(self, event):
        """Handler for when an RBW preset is selected."""
        selected_text = self.rbw_combobox.get()
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"RBW preset selected: {selected_text}",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        try:
            # Use regex to extract the number and the unit
            match = re.search(r'\((\d+)\s*Hz\)', selected_text)
            if match:
                rbw_value = int(match.group(1))
            else:
                raise ValueError("Could not parse numeric value from combobox string.")
        except (ValueError, IndexError):
            console_log("❌ Error parsing RBW value from combobox. Using default.",
                        function=current_function)
            rbw_value = 1_000_000
        
        if utils_yak_setting_handler.set_resolution_bandwidth(
            app_instance=self.app_instance,
            value=rbw_value,
            console_print_func=self.console_print_func
        ):
            # No longer setting individual variables here, we call the NAB handler instead
            self._sync_ui_from_app_state()
        else:
            # If the set failed, resync from the instrument to show the real value.
            self._sync_ui_from_app_state()

    def _on_vbw_selected(self, event):
        """Handler for when a VBW preset is selected."""
        selected_text = self.vbw_combobox.get()
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"VBW preset selected: {selected_text}",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        try:
            # Use regex to extract the number and the unit
            match = re.search(r'\((\d+)\s*Hz\)', selected_text)
            if match:
                vbw_value = int(match.group(1))
            else:
                raise ValueError("Could not parse numeric value from combobox string.")
        except (ValueError, IndexError):
            console_log("❌ Error parsing VBW value from combobox. Using default.",
                        function=current_function)
            vbw_value = 30000

        if utils_yak_setting_handler.set_video_bandwidth(
            app_instance=self.app_instance,
            value=vbw_value,
            console_print_func=self.console_print_func
        ):
            # No longer setting individual variables here, we call the NAB handler instead
            self._sync_ui_from_app_state()
        else:
            # If the set failed, resync from the instrument to show the real value.
            self._sync_ui_from_app_state()


    def _on_vbw_auto_toggle(self):
        """Handler for the VBW Auto toggle button."""
        current_function = inspect.currentframe().f_code.co_name
        is_on = not self.vbw_auto_state_var.get()
        debug_log(f"VBW Auto toggle clicked. Setting to {is_on}",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        if utils_yak_setting_handler.toggle_vbw_auto(
            app_instance=self.app_instance,
            console_print_func=self.console_print_func
        ):
            # No longer setting individual variables here, we call the NAB handler instead
            self._sync_ui_from_app_state()
        else:
            # If the toggle failed, resync from the instrument to show the real value.
            self._sync_ui_from_app_state()

    def _on_continuous_mode_change(self, event):
        """Handler for when the continuous mode dropdown is changed."""
        current_function = inspect.currentframe().f_code.co_name
        is_on = self.continuous_mode_var.get() == "ON"
        debug_log(f"Continuous mode changed to {is_on}",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

        if utils_yak_setting_handler.set_continuous_initiate_mode(
            app_instance=self.app_instance,
            mode=is_on,
            console_print_func=self.console_print_func
        ):
            # No longer setting individual variables here, we call the NAB handler instead
            self._sync_ui_from_app_state()
        else:
            # If the set failed, resync from the instrument to show the real value.
            self._sync_ui_from_app_state()
