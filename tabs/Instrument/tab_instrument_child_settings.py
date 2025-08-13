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
# Version 20250817.184500.1
#
# Version 20250811.215000.4 (UPDATED: Restructured the marker settings frame into two separate sections and added a 'Peak search' button.)

current_version = "20250817.184500.1"
current_version_hash = 20250817 * 184500 * 1

import tkinter as tk
from tkinter import ttk
import inspect
import os

from display.debug_logic import debug_log
from display.console_logic import console_log

# Import all API functions from the centralized handler file
from tabs.Instrument.utils_instrument_setting_handler import (
    set_center_frequency, set_span_frequency, set_start_frequency, set_stop_frequency,
    set_resolution_bandwidth, set_video_bandwidth, toggle_vbw_auto,
    set_continuous_initiate_mode, do_immediate_initiate,
    set_reference_level, toggle_preamp, set_power_attenuation, toggle_high_sensitivity,
    set_trace_mode, do_turn_all_markers_on, toggle_marker_state, do_peak_search,
    get_trace_data_logic, refresh_all_from_instrument, reset_device,
    get_all_marker_values_logic
)

# Conversion constant for Megahertz to Hertz
MHZ_TO_HZ_CONVERSION = 1_000_000


class SettingsTab(ttk.Frame):
    """
    A Tkinter Frame that provides a simple interface to control the
    instrument's key settings like Reference Level and Trace Mode.
    
    This class has been refactored to serve as a pure UI component. It calls 
    functions from utils_instrument_setting_handler.py to perform actions.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log

        self.preamp_state_var = self.app_instance.preamp_on_var
        self.high_sensitivity_state_var = self.app_instance.high_sensitivity_on_var
        self.vbw_auto_state_var = self.app_instance.vbw_auto_on_var
        
        self.trace_modes = ["VIEW", "WRITE", "BLANK", "MAXHOLD", "MINHOLD"]
        
        self.marker_vars = [
            self.app_instance.marker1_on_var,
            self.app_instance.marker2_on_var,
            self.app_instance.marker3_on_var,
            self.app_instance.marker4_on_var,
            self.app_instance.marker5_on_var,
            self.app_instance.marker6_on_var,
        ]
        self.marker_value_labels = []

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
        self.center_freq_entry = ttk.Entry(freq_frame, textvariable=self.app_instance.center_freq_mhz_var, style='TEntry')
        self.center_freq_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.center_freq_entry.bind("<FocusOut>", lambda e: set_center_frequency(self.app_instance, self.app_instance.center_freq_mhz_var.get(), self.console_print_func))
        
        ttk.Label(freq_frame, text="Span (MHz):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.span_freq_entry = ttk.Entry(freq_frame, textvariable=self.app_instance.span_freq_mhz_var, style='TEntry')
        self.span_freq_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.span_freq_entry.bind("<FocusOut>", lambda e: set_span_frequency(self.app_instance, self.app_instance.span_freq_mhz_var.get(), self.console_print_func))
        
        ttk.Label(freq_frame, text="Start Frequency (MHz):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.start_freq_entry = ttk.Entry(freq_frame, textvariable=self.app_instance.start_freq_mhz_var, style='TEntry')
        self.start_freq_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.start_freq_entry.bind("<FocusOut>", lambda e: set_start_frequency(self.app_instance, self.app_instance.start_freq_mhz_var.get(), self.console_print_func))
        
        ttk.Label(freq_frame, text="Stop Frequency (MHz):").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.stop_freq_entry = ttk.Entry(freq_frame, textvariable=self.app_instance.stop_freq_mhz_var, style='TEntry')
        self.stop_freq_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        self.stop_freq_entry.bind("<FocusOut>", lambda e: set_stop_frequency(self.app_instance, self.app_instance.stop_freq_mhz_var.get(), self.console_print_func))
        
        self.get_freq_button = ttk.Button(freq_frame, text="Get Current Frequencies", command=self._on_get_freq_click)
        self.get_freq_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # --- Bandwidth Settings Frame ---
        bandwidth_frame = ttk.LabelFrame(self, text="Bandwidth Settings", style='Dark.TLabelframe')
        bandwidth_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        bandwidth_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(bandwidth_frame, text="Resolution BW (MHz):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.rbw_entry = ttk.Entry(bandwidth_frame, textvariable=self.app_instance.rbw_mhz_var, style='TEntry')
        self.rbw_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.rbw_entry.bind("<FocusOut>", lambda e: set_resolution_bandwidth(self.app_instance, self.app_instance.rbw_mhz_var.get(), self.console_print_func))
        
        ttk.Label(bandwidth_frame, text="Video BW (MHz):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.vbw_entry = ttk.Entry(bandwidth_frame, textvariable=self.app_instance.vbw_mhz_var, style='TEntry')
        self.vbw_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.vbw_entry.bind("<FocusOut>", lambda e: set_video_bandwidth(self.app_instance, self.app_instance.vbw_mhz_var.get(), self.console_print_func))

        ttk.Label(bandwidth_frame, text="VBW Auto:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.vbw_auto_toggle_button = ttk.Button(bandwidth_frame, command=lambda: toggle_vbw_auto(self.app_instance, self.console_print_func))
        self.vbw_auto_toggle_button.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        # --- Initiate Settings Frame ---
        initiate_frame = ttk.LabelFrame(self, text="Initiate Settings", style='Dark.TLabelframe')
        initiate_frame.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        initiate_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(initiate_frame, text="Continuous Mode:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        initiate_modes = ["ON", "OFF"]
        self.initiate_continuous_dropdown = ttk.Combobox(initiate_frame, textvariable=self.app_instance.initiate_continuous_on_var, values=initiate_modes, state='readonly')
        self.initiate_continuous_dropdown.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.initiate_continuous_dropdown.bind("<<ComboboxSelected>>", lambda e: set_continuous_initiate_mode(self.app_instance, self.app_instance.initiate_continuous_on_var.get(), self.console_print_func))
        
        self.initiate_immediate_button = ttk.Button(initiate_frame, text="Initiate Immediate", command=lambda: do_immediate_initiate(self.app_instance, self.console_print_func))
        self.initiate_immediate_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")


        # --- Amplitude/Ref Level Frame ---
        amplitude_frame = ttk.LabelFrame(self, text="Amplitude Settings", style='Dark.TLabelframe')
        amplitude_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        amplitude_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(amplitude_frame, text="Reference Level:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ref_levels = [40, 30, 20, 10, 0, -10, -20, -30, -40, -50, -60, -70, -80, -90, -100]
        self.ref_level_dropdown = ttk.Combobox(amplitude_frame, textvariable=self.app_instance.ref_level_dbm_var, values=ref_levels, state='readonly')
        self.ref_level_dropdown.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.ref_level_dropdown.bind("<<ComboboxSelected>>", lambda e: set_reference_level(self.app_instance, self.app_instance.ref_level_dbm_var.get(), self.console_print_func))
        
        # Preamp Gain toggle button
        ttk.Label(amplitude_frame, text="Preamp Gain:", style='TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.preamp_toggle_button = ttk.Button(amplitude_frame, command=lambda: toggle_preamp(self.app_instance, self.console_print_func))
        self.preamp_toggle_button.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # Attenuation Level dropdown
        ttk.Label(amplitude_frame, text="Power Attenuation:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.power_attenuation_var = tk.StringVar(self)
        att_levels = ["0", "10", "20", "30", "40", "50", "60", "70"]
        self.power_attenuation_dropdown = ttk.Combobox(amplitude_frame, textvariable=self.power_attenuation_var, values=att_levels, state='readonly')
        self.power_attenuation_dropdown.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.power_attenuation_dropdown.bind("<<ComboboxSelected>>", lambda e: set_power_attenuation(self.app_instance, self.app_instance.power_attenuation_db_var.get(), self.console_print_func))

        # High Sensitivity toggle button
        ttk.Label(amplitude_frame, text="High Sensitivity:", style='TLabel').grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.hs_toggle_button = ttk.Button(amplitude_frame, command=lambda: toggle_high_sensitivity(self.app_instance, self.console_print_func))
        self.hs_toggle_button.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        # --- Trace Settings Frame ---
        trace_frame = ttk.LabelFrame(self, text="Trace Settings", style='Dark.TLabelframe')
        trace_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        trace_frame.grid_columnconfigure(1, weight=1)

        self.trace_vars = [
            self.app_instance.trace1_mode_var,
            self.app_instance.trace2_mode_var,
            self.app_instance.trace3_mode_var,
            self.app_instance.trace4_mode_var
        ]
        
        for i in range(4):
            ttk.Label(trace_frame, text=f"Trace {i+1} Mode:").grid(row=i, column=0, padx=5, pady=2, sticky="w")
            trace_dropdown = ttk.Combobox(trace_frame, textvariable=self.trace_vars[i], values=self.trace_modes, state='readonly')
            trace_dropdown.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
            trace_dropdown.bind("<<ComboboxSelected>>", lambda event, trace=i+1, var=self.trace_vars[i]: set_trace_mode(self.app_instance, trace, var.get(), self.console_print_func))

        # FIXED: Corrected button binding to call the handler function.
        self.get_trace_button = ttk.Button(trace_frame, text="Get Trace Data", command=lambda: get_trace_data_logic(self.app_instance, self.console_print_func))
        self.get_trace_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # --- Marker Settings Frame ---
        marker_frame = ttk.LabelFrame(self, text="Marker Settings", style='Dark.TLabelframe')
        marker_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        marker_frame.grid_columnconfigure(0, weight=1)
        marker_frame.grid_columnconfigure(1, weight=1)

        # --- NEW: Frame for "Turn On All Markers" and "Peak search" ---
        turn_on_markers_frame = ttk.Frame(marker_frame, style='Dark.TFrame')
        turn_on_markers_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        turn_on_markers_frame.grid_columnconfigure(0, weight=1)
        turn_on_markers_frame.grid_columnconfigure(1, weight=1)

        self.turn_all_markers_on_button = ttk.Button(turn_on_markers_frame, text="Turn All Markers On", command=lambda: do_turn_all_markers_on(self.app_instance, self.console_print_func))
        self.turn_all_markers_on_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # NEW: Peak search button
        self.peak_search_button = ttk.Button(turn_on_markers_frame, text="Peak search", command=lambda: do_peak_search(self.app_instance, self.console_print_func), style='Blue.TButton')
        self.peak_search_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # --- NEW: Frame for "Read All Markers" ---
        read_markers_frame = ttk.Frame(marker_frame, style='Dark.TFrame')
        read_markers_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        read_markers_frame.grid_columnconfigure(1, weight=1)
        read_markers_frame.grid_rowconfigure(7, weight=1)
        
        ttk.Label(read_markers_frame, text="Marker Values:").grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        # Marker On/Off checkboxes
        for i in range(6):
            cb = ttk.Checkbutton(read_markers_frame, text=f"Marker {i+1} On", variable=self.marker_vars[i], command=lambda marker=i+1, var=self.marker_vars[i]: toggle_marker_state(self.app_instance, marker, var.get(), self.console_print_func))
            cb.grid(row=i+1, column=0, padx=5, pady=2, sticky="w")
        
            # Placeholder for Marker X/Y display
            label = ttk.Label(read_markers_frame, text="X: N/A, Y: N/A", style='Dark.TLabel.Value')
            label.grid(row=i+1, column=1, padx=5, pady=2, sticky="ew")
            self.marker_value_labels.append(label)

        # Read marker values button
        self.read_markers_button = ttk.Button(read_markers_frame, text="Read All Markers", command=self._on_read_all_markers_click)
        self.read_markers_button.grid(row=7, column=1, padx=5, pady=5, sticky="ew")
        
        debug_log(f"Widgets for Settings Tab created. The GUI is alive! 🥳",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

    def _set_ui_initial_state(self):
        """Sets the initial state of the UI elements."""
        self._update_toggle_button_style(self.preamp_toggle_button, self.preamp_state_var.get())
        self._update_toggle_button_style(self.hs_toggle_button, self.high_sensitivity_state_var.get())
        self._update_toggle_button_style(self.vbw_auto_toggle_button, self.vbw_auto_state_var.get())

    def _update_toggle_button_style(self, button, state):
        """Updates the style and text of a toggle button based on its state."""
        if state:
            button.config(style='Orange.TButton', text="ON")
        else:
            button.config(style='Dark.TButton', text="OFF")

    def _on_get_freq_click(self):
        self.console_print_func("💬 Getting frequencies from instrument...")
        self._refresh_all_from_instrument()

    def _on_reset_button_click(self):
        self.console_print_func("💬 Resetting instrument...")
        reset_device(self.app_instance, self.console_print_func)
        self.console_print_func("✅ Instrument reset command sent. GUI refreshing...")
        self._refresh_all_from_instrument()
    
    def _on_read_all_markers_click(self):
        self.console_print_func("💬 Reading all marker values from instrument...")
        # Now call the handler function, which will handle the logic and update the UI
        get_all_marker_values_logic(self.app_instance, self.console_print_func)

    def _refresh_all_from_instrument(self):
        """
        Queries all settings from the instrument and updates the GUI variables.
        This ensures the UI reflects the true state of the hardware.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Refreshing all GUI settings from the instrument. Syncing the UI with the hardware.",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        if not self.app_instance.is_connected.get():
            self.console_print_func("❌ Not connected to an instrument. Cannot refresh settings.")
            return

        settings = refresh_all_from_instrument(self.app_instance, self.console_print_func)
        if not settings:
            self.console_print_func("❌ Failed to retrieve settings from instrument.")
            return

        # Update Tkinter variables from the settings dictionary
        # Frequency
        self.app_instance.center_freq_mhz_var.set(f"{float(settings.get('center_freq_hz')) / MHZ_TO_HZ_CONVERSION:.3f}")
        self.app_instance.span_freq_mhz_var.set(f"{float(settings.get('span_hz')) / MHZ_TO_HZ_CONVERSION:.3f}")
        self.app_instance.start_freq_mhz_var.set(f"{float(settings.get('start_freq_hz')) / MHZ_TO_HZ_CONVERSION:.3f}")
        self.app_instance.stop_freq_mhz_var.set(f"{float(settings.get('stop_freq_hz')) / MHZ_TO_HZ_CONVERSION:.3f}")

        # Bandwidth
        self.app_instance.rbw_mhz_var.set(f"{float(settings.get('rbw_hz')) / MHZ_TO_HZ_CONVERSION:.3f}")
        self.app_instance.vbw_mhz_var.set(f"{float(settings.get('vbw_hz')) / MHZ_TO_HZ_CONVERSION:.3f}")
        self.app_instance.vbw_auto_on_var.set(settings.get('vbw_auto_on'))
        self._update_toggle_button_style(self.vbw_auto_toggle_button, settings.get('vbw_auto_on'))
        
        # Initiate
        self.app_instance.initiate_continuous_on_var.set(settings.get('initiate_continuous_on'))
        
        # Amplitude
        self.app_instance.ref_level_dbm_var.set(settings.get('ref_level_dbm'))
        self.app_instance.power_attenuation_db_var.set(settings.get('power_attenuation_db'))
        self.app_instance.preamp_on_var.set(settings.get('preamp_on'))
        self.app_instance.high_sensitivity_on_var.set(settings.get('high_sensitivity_on'))
        self._update_toggle_button_style(self.preamp_toggle_button, settings.get('preamp_on'))
        self._update_toggle_button_style(self.hs_toggle_button, settings.get('high_sensitivity_on'))
        
        # Trace Modes
        self.app_instance.trace1_mode_var.set(settings.get('trace1_mode'))
        self.app_instance.trace2_mode_var.set(settings.get('trace2_mode'))
        self.app_instance.trace3_mode_var.set(settings.get('trace3_mode'))
        self.app_instance.trace4_mode_var.set(settings.get('trace4_mode'))
        
        # Markers
        for i in range(6):
            marker_state = settings.get(f'marker{i+1}_on')
            self.marker_vars[i].set(marker_state)
            
        self.console_print_func("✅ GUI settings refreshed from the instrument.")

    def _on_tab_selected(self, event=None):
        """
        Handles when this tab is selected. This is the main point of entry
        for refreshing the UI from the instrument.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Settings Tab selected. Checking connection status. What's the instrument doing? 🤔",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        is_connected = self.app_instance.is_connected.get()
        if is_connected:
            self.console_print_func("✅ Instrument is connected. You can now change settings.")
            self._refresh_all_from_instrument()
        else:
            self.console_print_func("❌ Instrument is not connected. Connect first to change settings.")
