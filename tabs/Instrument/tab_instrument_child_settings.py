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
# Version 20250811.215000.3

current_version = "20250811.215000.3"
current_version_hash = 20250811 * 215000 * 3

import tkinter as tk
from tkinter import ttk
import inspect
import os

from display.debug_logic import debug_log
from display.console_logic import console_log

# Import the new high-level Yak functions
from tabs.Instrument.Yakety_Yak import YakSet, YakDo, YakGet

# Conversion constant for Megahertz to Hertz
MHZ_TO_HZ_CONVERSION = 1_000_000


class SettingsTab(ttk.Frame):
    """
    A Tkinter Frame that provides a simple interface to control the
    instrument's key settings like Reference Level and Trace Mode.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log

        # Tkinter variables for various settings
        self.center_freq_var = tk.StringVar(self)
        self.span_freq_var = tk.StringVar(self)
        self.start_freq_var = tk.StringVar(self)
        self.stop_freq_var = tk.StringVar(self)
        self.power_attenuation_var = tk.StringVar(self)
        
        # New variables for Bandwidth settings
        self.rbw_var = tk.StringVar(self)
        self.vbw_var = tk.StringVar(self)
        
        # New variable for Continuous Initiate state
        self.initiate_continuous_var = tk.StringVar(self)

        # Local variables to hold the state of the toggle buttons
        self.preamp_state_var = tk.StringVar(self, value="OFF")
        self.high_sensitivity_state_var = tk.StringVar(self, value="OFF")
        self.vbw_auto_state_var = tk.StringVar(self, value="OFF")

        # Marker variables
        self.marker_vars = [tk.BooleanVar(self, False) for _ in range(6)]
        self.marker_value_labels = []  # Initialize here to be accessible

        self._create_widgets()
        self._set_ui_initial_state()

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
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(5, weight=1)

        # --- Instrument Info Frame ---
        info_frame = ttk.LabelFrame(self, text="Connected Instrument", style='Dark.TLabelframe')
        info_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        info_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(info_frame, text="Manufacturer:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(info_frame, textvariable=self.app_instance.connected_instrument_manufacturer, style='Dark.TLabel.Value').grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(info_frame, text="Model:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(info_frame, textvariable=self.app_instance.connected_instrument_model, style='Dark.TLabel.Value').grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # Add the Reset button to this frame
        self.reset_button = ttk.Button(info_frame, text="RESET (*RST)", command=self._on_reset_button_click, style='Red.TButton')
        self.reset_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # --- Frequency Settings Frame ---
        freq_frame = ttk.LabelFrame(self, text="Frequency Settings", style='Dark.TLabelframe')
        freq_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        freq_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(freq_frame, text="Center Frequency (MHz):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.center_freq_entry = ttk.Entry(freq_frame, textvariable=self.center_freq_var, style='TEntry')
        self.center_freq_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.center_freq_entry.bind("<FocusOut>", lambda e: self._on_freq_set("CENTER", self.center_freq_var.get()))
        
        ttk.Label(freq_frame, text="Span (MHz):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.span_freq_entry = ttk.Entry(freq_frame, textvariable=self.span_freq_var, style='TEntry')
        self.span_freq_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.span_freq_entry.bind("<FocusOut>", lambda e: self._on_freq_set("SPAN", self.span_freq_var.get()))
        
        ttk.Label(freq_frame, text="Start Frequency (MHz):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.start_freq_entry = ttk.Entry(freq_frame, textvariable=self.start_freq_var, style='TEntry')
        self.start_freq_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.start_freq_entry.bind("<FocusOut>", lambda e: self._on_freq_set("START", self.start_freq_var.get()))
        
        ttk.Label(freq_frame, text="Stop Frequency (MHz):").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.stop_freq_entry = ttk.Entry(freq_frame, textvariable=self.stop_freq_var, style='TEntry')
        self.stop_freq_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        self.stop_freq_entry.bind("<FocusOut>", lambda e: self._on_freq_set("STOP", self.stop_freq_var.get()))
        
        self.get_freq_button = ttk.Button(freq_frame, text="Get Current Frequencies", command=self._on_get_freq_click)
        self.get_freq_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # --- Bandwidth Settings Frame (NEW) ---
        bandwidth_frame = ttk.LabelFrame(self, text="Bandwidth Settings", style='Dark.TLabelframe')
        bandwidth_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        bandwidth_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(bandwidth_frame, text="Resolution BW (MHz):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.rbw_entry = ttk.Entry(bandwidth_frame, textvariable=self.rbw_var, style='TEntry')
        self.rbw_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.rbw_entry.bind("<FocusOut>", lambda e: self._on_bandwidth_set("RESOLUTION", self.rbw_var.get()))
        
        ttk.Label(bandwidth_frame, text="Video BW (MHz):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.vbw_entry = ttk.Entry(bandwidth_frame, textvariable=self.vbw_var, style='TEntry')
        self.vbw_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.vbw_entry.bind("<FocusOut>", lambda e: self._on_bandwidth_set("VIDEO", self.vbw_var.get()))

        ttk.Label(bandwidth_frame, text="VBW Auto:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.vbw_auto_toggle_button = ttk.Button(bandwidth_frame, textvariable=self.vbw_auto_state_var, command=self._on_vbw_auto_toggle_click)
        self.vbw_auto_toggle_button.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        # --- Initiate Settings Frame (NEW) ---
        initiate_frame = ttk.LabelFrame(self, text="Initiate Settings", style='Dark.TLabelframe')
        initiate_frame.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        initiate_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(initiate_frame, text="Continuous Mode:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        initiate_modes = ["ON", "OFF"]
        self.initiate_continuous_dropdown = ttk.Combobox(initiate_frame, textvariable=self.initiate_continuous_var, values=initiate_modes, state='readonly')
        self.initiate_continuous_dropdown.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.initiate_continuous_dropdown.bind("<<ComboboxSelected>>", self._on_continuous_initiate_select)
        
        self.initiate_immediate_button = ttk.Button(initiate_frame, text="Initiate Immediate", command=self._on_immediate_initiate_click)
        self.initiate_immediate_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")


        # --- Amplitude/Ref Level Frame ---
        amplitude_frame = ttk.LabelFrame(self, text="Amplitude Settings", style='Dark.TLabelframe')
        amplitude_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        amplitude_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(amplitude_frame, text="Reference Level:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.ref_level_var = tk.StringVar(self)
        ref_levels = [40, 30, 20, 10, 0, -10, -20, -30, -40, -50, -60, -70, -80, -90, -100]
        self.ref_level_dropdown = ttk.Combobox(amplitude_frame, textvariable=self.ref_level_var, values=ref_levels, state='readonly')
        self.ref_level_dropdown.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.ref_level_dropdown.bind("<<ComboboxSelected>>", self._on_ref_level_select)
        
        # Preamp Gain toggle button
        ttk.Label(amplitude_frame, text="Preamp Gain:", style='TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.preamp_toggle_button = ttk.Button(amplitude_frame, textvariable=self.preamp_state_var, command=self._on_preamp_toggle_click)
        self.preamp_toggle_button.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # Attenuation Level dropdown
        ttk.Label(amplitude_frame, text="Power Attenuation:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.power_attenuation_var = tk.StringVar(self)
        att_levels = ["0", "10", "20", "30", "40", "50", "60", "70"]
        self.power_attenuation_dropdown = ttk.Combobox(amplitude_frame, textvariable=self.power_attenuation_var, values=att_levels, state='readonly')
        self.power_attenuation_dropdown.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.power_attenuation_dropdown.bind("<<ComboboxSelected>>", self._on_power_attenuation_select)

        # High Sensitivity toggle button
        ttk.Label(amplitude_frame, text="High Sensitivity:", style='TLabel').grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.hs_toggle_button = ttk.Button(amplitude_frame, textvariable=self.high_sensitivity_state_var, command=self._on_hs_toggle_click)
        self.hs_toggle_button.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        # --- Trace Settings Frame ---
        trace_frame = ttk.LabelFrame(self, text="Trace Settings", style='Dark.TLabelframe')
        trace_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        trace_frame.grid_columnconfigure(1, weight=1)

        trace_modes = ["VIEW", "WRITE", "BLANK", "MAXHOLD", "MINHOLD"]
        self.trace_vars = [tk.StringVar(self) for _ in range(4)]
        
        for i in range(4):
            ttk.Label(trace_frame, text=f"Trace {i+1} Mode:").grid(row=i, column=0, padx=5, pady=2, sticky="w")
            trace_dropdown = ttk.Combobox(trace_frame, textvariable=self.trace_vars[i], values=trace_modes, state='readonly')
            trace_dropdown.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
            trace_dropdown.bind("<<ComboboxSelected>>", lambda event, trace=i+1, var=self.trace_vars[i]: self._on_trace_mode_select(event, trace, var))

        self.get_trace_button = ttk.Button(trace_frame, text="Get Trace Data", command=self._on_get_trace_data_click)
        self.get_trace_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # --- Marker Settings Frame ---
        marker_frame = ttk.LabelFrame(self, text="Marker Settings", style='Dark.TLabelframe')
        marker_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        marker_frame.grid_columnconfigure(0, weight=1)
        marker_frame.grid_columnconfigure(1, weight=1)

        self.turn_all_markers_on_button = ttk.Button(marker_frame, text="Turn All Markers On", command=self._on_turn_all_markers_on_click)
        self.turn_all_markers_on_button.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Marker On/Off checkboxes
        for i in range(6):
            cb = ttk.Checkbutton(marker_frame, text=f"Marker {i+1} On", variable=self.marker_vars[i], command=lambda marker=i+1, var=self.marker_vars[i]: self._on_marker_state_toggle(marker, var))
            cb.grid(row=i+1, column=0, padx=5, pady=2, sticky="w")
        
        # Placeholder for Marker X/Y display
        ttk.Label(marker_frame, text="Marker Values:").grid(row=0, column=1, padx=5, pady=2, sticky="w")
        # I'll create a list of labels to hold the values
        for i in range(6):
            label = ttk.Label(marker_frame, text="X: N/A, Y: N/A", style='Dark.TLabel.Value')
            label.grid(row=i+1, column=1, padx=5, pady=2, sticky="ew")
            self.marker_value_labels.append(label)

        # Read marker values button
        self.read_markers_button = ttk.Button(marker_frame, text="Read All Markers", command=self._on_read_all_markers_click)
        self.read_markers_button.grid(row=7, column=1, padx=5, pady=5, sticky="ew")
        
        debug_log(f"Widgets for Settings Tab created. The GUI is alive! 🥳",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

    def _set_ui_initial_state(self):
        """Sets the initial state of the UI elements."""
        self._update_toggle_button_style(self.preamp_toggle_button, self.preamp_state_var.get() == "ON")
        self._update_toggle_button_style(self.hs_toggle_button, self.high_sensitivity_state_var.get() == "ON")
        self._update_toggle_button_style(self.vbw_auto_toggle_button, self.vbw_auto_state_var.get() == "ON")

    def _update_toggle_button_style(self, button, state):
        """Updates the style of a toggle button based on its state."""
        if state:
            button.config(style='Orange.TButton')
        else:
            button.config(style='Dark.TButton')

    def _on_get_freq_click(self):
        """
        Handles the button click for getting current frequency settings.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Get Current Frequencies button clicked. Querying instrument.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        if not self.app_instance.is_connected.get():
            self.console_print_func("❌ Not connected to an instrument. Cannot get frequency settings.")
            debug_log("Cannot get frequency settings. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return

        # Query and update GUI
        center_freq = YakGet(self.app_instance, "FREQUENCY/CENTER", self.console_print_func)
        if center_freq is not None:
            self.center_freq_var.set(f"{float(center_freq) / MHZ_TO_HZ_CONVERSION:.3f}")
        
        span_freq = YakGet(self.app_instance, "FREQUENCY/SPAN", self.console_print_func)
        if span_freq is not None:
            self.span_freq_var.set(f"{float(span_freq) / MHZ_TO_HZ_CONVERSION:.3f}")

        start_freq = YakGet(self.app_instance, "FREQUENCY/START", self.console_print_func)
        if start_freq is not None:
            self.start_freq_var.set(f"{float(start_freq) / MHZ_TO_HZ_CONVERSION:.3f}")
        
        stop_freq = YakGet(self.app_instance, "FREQUENCY/STOP", self.console_print_func)
        if stop_freq is not None:
            self.stop_freq_var.set(f"{float(stop_freq) / MHZ_TO_HZ_CONVERSION:.3f}")


    def _on_freq_set(self, command_part, value):
        """
        Handles setting a frequency value when a text box loses focus.
        Converts the UI value from MHz to an integer Hz before sending.
        """
        current_function = inspect.currentframe().f_code.co_name
        
        if not self.app_instance.is_connected.get():
            self.console_print_func("❌ Not connected to an instrument. Cannot set frequency.")
            debug_log("Cannot set frequency. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return

        try:
            # Convert user input to float MHz, then to integer Hz
            hz_value = int(float(value) * MHZ_TO_HZ_CONVERSION)
            debug_log(f"{command_part} Frequency set to: {value} MHz, converted to {hz_value} Hz for the instrument.",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            
            command_type = f"FREQUENCY/{command_part}"
            YakSet(self.app_instance, command_type.upper(), str(hz_value), self.console_print_func)
        except ValueError:
            self.console_print_func(f"❌ Invalid frequency value: '{value}'. Please enter a number.")
            debug_log(f"Invalid frequency value entered: '{value}'. What a disaster!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)

    def _on_bandwidth_set(self, command_part, value):
        """
        Handles setting a bandwidth value when a text box loses focus.
        Converts the UI value from MHz to an integer Hz before sending.
        """
        current_function = inspect.currentframe().f_code.co_name
        
        if not self.app_instance.is_connected.get():
            self.console_print_func("❌ Not connected to an instrument. Cannot set bandwidth.")
            debug_log("Cannot set bandwidth. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return
        
        try:
            # Convert user input to float MHz, then to integer Hz
            hz_value = int(float(value) * MHZ_TO_HZ_CONVERSION)
            debug_log(f"{command_part} Bandwidth set to: {value} MHz, converted to {hz_value} Hz for the instrument.",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            
            command_type = f"BANDWIDTH/{command_part}"
            YakSet(self.app_instance, command_type.upper(), str(hz_value), self.console_print_func)
        except ValueError:
            self.console_print_func(f"❌ Invalid bandwidth value: '{value}'. Please enter a number.")
            debug_log(f"Invalid bandwidth value entered: '{value}'. What a disaster!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)


    def _on_vbw_auto_toggle_click(self):
        """Toggles VBW auto on/off."""
        current_function = inspect.currentframe().f_code.co_name
        
        if not self.app_instance.is_connected.get():
            self.console_print_func("❌ Not connected to an instrument. Cannot set VBW Auto.")
            debug_log("Cannot set VBW Auto. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return
        
        current_state = self.vbw_auto_state_var.get()
        new_state = "OFF" if current_state == "ON" else "ON"
        
        command_type = f"BANDWIDTH/VIDEO/AUTO/{new_state}"
        YakDo(self.app_instance, command_type.upper(), self.console_print_func)
        self.vbw_auto_state_var.set(new_state)
        self._update_toggle_button_style(self.vbw_auto_toggle_button, new_state == "ON")

    def _on_continuous_initiate_select(self, event):
        """
        Handles the selection of Continuous Initiate mode.
        """
        current_function = inspect.currentframe().f_code.co_name
        mode = self.initiate_continuous_var.get()
        debug_log(f"Initiate Continuous mode selected: {mode}.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        if not self.app_instance.is_connected.get():
            self.console_print_func("❌ Not connected to an instrument. Cannot set continuous initiate mode.")
            debug_log("Cannot set continuous initiate mode. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return
        
        command_type = f"INITIATE/CONTINUOUS/{mode}"
        YakDo(self.app_instance, command_type.upper(), self.console_print_func)
        
    def _on_immediate_initiate_click(self):
        """
        Handles the button click for the Initiate Immediate command.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initiate Immediate button clicked. Sending command.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        if not self.app_instance.is_connected.get():
            self.console_print_func("❌ Not connected to an instrument. Cannot initiate immediate scan.")
            debug_log("Cannot initiate immediate scan. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return
            
        command_type = "INITIATE/IMMEDIATE"
        YakDo(self.app_instance, command_type.upper(), self.console_print_func)


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

        command_type = f"AMPLITUDE/REFERENCE LEVEL/{ref_level}"
        YakDo(self.app_instance, command_type.upper(), self.console_print_func)

    def _on_preamp_toggle_click(self):
        """Toggles the preamp on/off."""
        current_function = inspect.currentframe().f_code.co_name
        
        if not self.app_instance.is_connected.get():
            self.console_print_func("❌ Not connected to an instrument. Cannot set preamp gain.")
            debug_log("Cannot set preamp gain. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return
        
        current_state = self.preamp_state_var.get()
        new_state = "OFF" if current_state == "ON" else "ON"
        
        command_type = f"AMPLITUDE/POWER/GAIN/{new_state}"
        YakDo(self.app_instance, command_type.upper(), self.console_print_func)
        self.preamp_state_var.set(new_state)
        self._update_toggle_button_style(self.preamp_toggle_button, new_state == "ON")


    def _on_power_attenuation_select(self, event):
        """
        Handles the selection of a new power attenuation from the dropdown.
        """
        current_function = inspect.currentframe().f_code.co_name
        attenuation_level = self.power_attenuation_var.get()
        debug_log(f"Power Attenuation selected: {attenuation_level} dB.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        if not self.app_instance.is_connected.get():
            self.console_print_func("❌ Not connected to an instrument. Cannot set power attenuation.")
            debug_log("Cannot set power attenuation. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return

        command_type = f"AMPLITUDE/POWER/ATTENUATION/{attenuation_level}DB"
        YakDo(self.app_instance, command_type.upper(), self.console_print_func)

    def _on_hs_toggle_click(self):
        """Toggles the high sensitivity on/off."""
        current_function = inspect.currentframe().f_code.co_name
        
        if not self.app_instance.is_connected.get():
            self.console_print_func("❌ Not connected to an instrument. Cannot set high sensitivity.")
            debug_log("Cannot set high sensitivity. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return
        
        current_state = self.high_sensitivity_state_var.get()
        new_state = "OFF" if current_state == "ON" else "ON"

        command_type = f"AMPLITUDE/POWER/HIGH SENSITIVE/{new_state}"
        YakDo(self.app_instance, command_type.upper(), self.console_print_func)
        self.high_sensitivity_state_var.set(new_state)
        self._update_toggle_button_style(self.hs_toggle_button, new_state == "ON")


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
        
        command_type = f"TRACE/{trace_number}/MODE/{mode}"
        YakDo(self.app_instance, command_type.upper(), self.console_print_func)

    def _on_get_trace_data_click(self):
        """
        Handles the button click to get trace data for all traces.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Get Trace Data button clicked. Querying all trace data.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        if not self.app_instance.is_connected.get():
            self.console_print_func("❌ Not connected to an instrument. Cannot get trace data.")
            debug_log("Cannot get trace data. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return
        
        for i in range(4):
            trace_number = i + 1
            command_type = f"TRACE/{trace_number}/DATA"
            trace_data = YakGet(self.app_instance, command_type.upper(), self.console_print_func)
            if trace_data is not None:
                self.console_print_func(f"✅ Trace {trace_number} data received: {trace_data[:50]}...")
                debug_log(f"Received data for Trace {trace_number}. Fucking awesome!",
                            file=os.path.basename(__file__),
                            version=current_version,
                            function=current_function)
            else:
                self.console_print_func(f"❌ Failed to get data for Trace {trace_number}.")
                debug_log(f"Failed to get data for Trace {trace_number}. What a disaster!",
                            file=os.path.basename(__file__),
                            version=current_version,
                            function=current_function)

    def _on_turn_all_markers_on_click(self):
        """
        Handles the button click to turn on all markers.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Turn All Markers On button clicked. Toggling all markers.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        if not self.app_instance.is_connected.get():
            self.console_print_func("❌ Not connected to an instrument. Cannot turn on markers.")
            debug_log("Cannot turn on markers. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return
        
        for i in range(6):
            marker_number = i + 1
            command_type = f"MARKER/{marker_number}/CALCULATE/STATE"
            YakSet(self.app_instance, command_type.upper(), "ON", self.console_print_func)
            self.marker_vars[i].set(True)
        self.console_print_func("✅ All markers turned on.")
        debug_log("All markers turned on. Fucking brilliant!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)


    def _on_marker_state_toggle(self, marker_number, var):
        """
        Handles the state change of a marker checkbox.
        """
        current_function = inspect.currentframe().f_code.co_name
        state = "ON" if var.get() else "OFF"
        debug_log(f"Marker {marker_number} state toggled to: {state}.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        if not self.app_instance.is_connected.get():
            self.console_print_func("❌ Not connected to an instrument. Cannot set marker state.")
            debug_log("Cannot set marker state. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return
        
        command_type = f"MARKER/{marker_number}/CALCULATE/STATE"
        YakSet(self.app_instance, command_type.upper(), state, self.console_print_func)


    def _on_read_all_markers_click(self):
        """
        Handles the button click for reading all marker values.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Read All Markers button clicked. Querying all markers.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        if not self.app_instance.is_connected.get():
            self.console_print_func("❌ Not connected to an instrument. Cannot read markers.")
            debug_log("Cannot read markers. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return
        
        for i in range(6):
            if self.marker_vars[i].get():
                marker_number = i + 1
                x_command = f"MARKER/{marker_number}/CALCULATE/X"
                y_command = f"MARKER/{marker_number}/CALCULATE/Y"
                
                x_value = YakGet(self.app_instance, x_command.upper(), self.console_print_func)
                y_value = YakGet(self.app_instance, y_command.upper(), self.console_print_func)

                # Assuming X values are in Hz and Y values are in dBm
                try:
                    x_value_mhz = float(x_value) / MHZ_TO_HZ_CONVERSION
                    self.marker_value_labels[i].config(text=f"X: {x_value_mhz:.3f} MHz, Y: {y_value} dBm")
                    self.console_print_func(f"✅ Marker {marker_number} values: X:{x_value_mhz:.3f} MHz, Y:{y_value} dBm")
                    debug_log(f"Read values for Marker {marker_number}: X:{x_value_mhz:.3f} MHz, Y:{y_value} dBm. Fucking awesome!",
                                file=os.path.basename(__file__),
                                version=current_version,
                                function=current_function)
                except (ValueError, TypeError):
                    self.marker_value_labels[i].config(text=f"X: {x_value}, Y: {y_value}")
                    self.console_print_func(f"⚠️ Could not parse marker {marker_number} values: X:{x_value}, Y:{y_value}")
                    debug_log(f"Failed to parse marker values for Marker {marker_number}. What a disaster!",
                                file=os.path.basename(__file__),
                                version=current_version,
                                function=current_function)


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
        
        command_type = "SYSTEM/RESET"
        YakDo(self.app_instance, command_type.upper(), self.console_print_func)
    
    def _on_tab_selected(self, event=None):
        """
        Handles when this tab is selected. This can be used to query the current
        instrument settings and update the dropdowns and buttons to reflect them.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Settings Tab selected. Checking connection status. What's the instrument doing? 🤔",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        is_connected = self.app_instance.is_connected.get()
        if is_connected:
            self.console_print_func("✅ Instrument is connected. You can now change settings.")
            
            # Query and update frequency settings
            self._on_get_freq_click()
            
            # Query and update bandwidth settings
            rbw_value = YakGet(self.app_instance, "BANDWIDTH/RESOLUTION", self.console_print_func)
            if rbw_value is not None:
                self.rbw_var.set(f"{float(rbw_value) / MHZ_TO_HZ_CONVERSION:.3f}")
            
            vbw_value = YakGet(self.app_instance, "BANDWIDTH/VIDEO", self.console_print_func)
            if vbw_value is not None:
                self.vbw_var.set(f"{float(vbw_value) / MHZ_TO_HZ_CONVERSION:.3f}")

            vbw_auto_state = YakGet(self.app_instance, "BANDWIDTH/VIDEO/AUTO", self.console_print_func)
            if vbw_auto_state is not None:
                self.vbw_auto_state_var.set("ON" if vbw_auto_state.upper() == "ON" else "OFF")
                self._update_toggle_button_style(self.vbw_auto_toggle_button, vbw_auto_state.upper() == "ON")
            
            # Query and update continuous initiate state
            continuous_state = YakGet(self.app_instance, "INITIATE/CONTINUOUS", self.console_print_func)
            if continuous_state is not None:
                self.initiate_continuous_var.set("ON" if continuous_state.upper() == "ON" else "OFF")
            
        else:
            self.console_print_func("❌ Instrument is not connected. Connect first to change settings.")