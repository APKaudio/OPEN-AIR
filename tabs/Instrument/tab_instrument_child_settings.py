# tabs/Instrument/tab_instrument_child_settings.py
#
# This file defines the SettingsTab, a Tkinter Frame for controlling a spectrum
# analyzer's basic settings such as reference level, preamp gain, and trace modes.
# It acts as a user-friendly interface that calls high-level `Yakety_Yak` functions
# to send commands to the connected instrument.
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
# Version 20250811.203204.0

current_version = "20250811.203204.0"
current_version_hash = 20250811 * 203204 * 0

import tkinter as tk
from tkinter import ttk
import inspect
import os

from display.debug_logic import debug_log
from display.console_logic import console_log

# Import the new high-level Yak functions
from tabs.Instrument.Yakety_Yak import YakSet, YakDo


class SettingsTab(ttk.Frame):
    """
    A Tkinter Frame that provides a simple interface to control the
    instrument's key settings like Reference Level and Trace Mode.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log

        self._create_widgets()

    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Settings tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering _create_widgets. Creating widgets for the Settings Tab.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Instrument Info Frame ---
        info_frame = ttk.LabelFrame(self, text="Connected Instrument", style='Dark.TLabelframe')
        info_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        info_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(info_frame, text="Manufacturer:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(info_frame, textvariable=self.app_instance.connected_instrument_manufacturer, style='Dark.TLabel.Value').grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(info_frame, text="Model:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(info_frame, textvariable=self.app_instance.connected_instrument_model, style='Dark.TLabel.Value').grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # Add the Reset button to this frame
        self.reset_button = ttk.Button(info_frame, text="RESET (*RST)", command=self._on_reset_button_click, style='Red.TButton')
        self.reset_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")


        # --- Amplitude/Ref Level Frame ---
        amplitude_frame = ttk.LabelFrame(self, text="Amplitude Settings", style='Dark.TLabelframe')
        amplitude_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        amplitude_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(amplitude_frame, text="Reference Level:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.ref_level_var = tk.StringVar(self)
        ref_levels = [40, 30, 20, 10, 0, -10, -20, -30, -40, -50, -60, -70, -80, -90, -100]
        self.ref_level_dropdown = ttk.Combobox(amplitude_frame, textvariable=self.ref_level_var, values=ref_levels, state='readonly')
        self.ref_level_dropdown.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.ref_level_dropdown.bind("<<ComboboxSelected>>", self._on_ref_level_select)
        
        # Preamp Gain buttons
        ttk.Label(amplitude_frame, text="Preamp Gain:", style='TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        gain_button_frame = ttk.Frame(amplitude_frame)
        gain_button_frame.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        ttk.Button(gain_button_frame, text="On", command=lambda: self._on_gain_toggle("on"), style='Green.TButton').pack(side="left", fill="both", expand=True, padx=(0, 2))
        ttk.Button(gain_button_frame, text="Off", command=lambda: self._on_gain_toggle("off"), style='Red.TButton').pack(side="left", fill="both", expand=True, padx=(2, 0))
        
        # --- Trace Settings Frame ---
        trace_frame = ttk.LabelFrame(self, text="Trace Settings", style='Dark.TLabelframe')
        trace_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        trace_frame.grid_columnconfigure(1, weight=1)

        trace_modes = ["view", "write", "blank", "maxhold", "minhold"]

        for i in range(1, 5):
            ttk.Label(trace_frame, text=f"Trace {i} Mode:").grid(row=i-1, column=0, padx=5, pady=2, sticky="w")
            trace_var = tk.StringVar(self)
            trace_dropdown = ttk.Combobox(trace_frame, textvariable=trace_var, values=trace_modes, state='readonly')
            trace_dropdown.grid(row=i-1, column=1, padx=5, pady=2, sticky="ew")
            trace_dropdown.bind("<<ComboboxSelected>>", lambda event, trace=i, var=trace_var: self._on_trace_mode_select(event, trace, var))

        debug_log(f"Widgets for Settings Tab created. The GUI is alive! 🥳",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

    def _on_ref_level_select(self, event):
        """
        Handles the selection of a new reference level from the dropdown.
        """
        current_function = inspect.currentframe().f_code.co_name
        ref_level = self.ref_level_var.get()
        debug_log(f"Ref Level selected: {ref_level} dBm.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        if not self.app_instance.is_connected.get():
            self.console_print_func("❌ Not connected to an instrument. Cannot set reference level.")
            debug_log("Cannot set ref level. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return

        command_type = f"Amplitude/Reference Level/{ref_level}"
        YakDo(self.app_instance, command_type, self.console_print_func)

    def _on_gain_toggle(self, state):
        """
        Handles the ON/OFF buttons for Preamp Gain.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Preamp Gain toggle to: {state}.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        if not self.app_instance.is_connected.get():
            self.console_print_func("❌ Not connected to an instrument. Cannot set preamp gain.")
            debug_log("Cannot set preamp gain. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return
        
        command_type = f"Amplitude/Power/Gain/{state}"
        YakDo(self.app_instance, command_type, self.console_print_func)
    
    def _on_trace_mode_select(self, event, trace_number, trace_var):
        """
        Handles the selection of a new trace mode from a dropdown.
        """
        current_function = inspect.currentframe().f_code.co_name
        mode = trace_var.get()
        debug_log(f"Trace {trace_number} Mode selected: {mode}.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        if not self.app_instance.is_connected.get():
            self.console_print_func("❌ Not connected to an instrument. Cannot set trace mode.")
            debug_log("Cannot set trace mode. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return
        
        command_type = f"Trace/Mode/{trace_number}/{mode}"
        YakDo(self.app_instance, command_type, self.console_print_func)

    def _on_reset_button_click(self):
        """
        Handles the button click for the *RST command.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"RESET button clicked. Sending the *RST command.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        if not self.app_instance.is_connected.get():
            self.console_print_func("❌ Not connected to an instrument. Cannot reset.")
            debug_log("Cannot reset instrument. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return
        
        command_type = "System/Reset"
        YakDo(self.app_instance, command_type, self.console_print_func)
    
    def _on_tab_selected(self, event=None):
        """
        Handles when this tab is selected. This can be used to query the current
        instrument settings and update the dropdowns and buttons to reflect them.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Settings Tab selected. Checking connection status. What's the instrument doing? 🧐",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        is_connected = self.app_instance.is_connected.get()
        if is_connected:
            self.console_print_func("✅ Instrument is connected. You can now change settings.")
            # Here you would typically query the current settings and update the UI
            # For now, we will just log that we are ready.
        else:
            self.console_print_func("❌ Instrument is not connected. Connect first to change settings.")