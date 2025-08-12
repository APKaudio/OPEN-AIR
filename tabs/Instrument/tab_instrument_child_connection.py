# tabs/Instrument/tab_instrument_child_connection.py
#
# This file defines the InstrumentTab, a Tkinter Frame for connecting to
# a spectrum analyzer via VISA and displaying its current settings.
# It allows users to find available instruments, connect/disconnect,
# and query the device for its configuration.
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
# Version 20250811.215500.2 (REMOVED: The initialize_instrument_logic call has been removed from the connection process to streamline the workflow and reduce potential issues. The reset command is now called directly.)

current_version = "20250811.215500.2"
current_version_hash = 20250811 * 215500 * 2

import tkinter as tk
from tkinter import ttk
import inspect
import os

# Import logical functions
from tabs.Instrument.instrument_logic import connect_instrument_logic, disconnect_instrument_logic, populate_resources_logic, query_current_settings_logic
from display.debug_logic import debug_log
from display.console_logic import console_log
from src.connection_status_logic import update_connection_status_logic
from ref.frequency_bands import MHZ_TO_HZ, KHZ_TO_HZ
from tabs.Instrument.utils_instrument_read_and_write import write_safe

class InstrumentTab(ttk.Frame):
    """
    A Tkinter Frame that allows connecting to a spectrum analyzer via VISA
    and displaying its current settings.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log

        self._create_widgets()
        self._update_ui_state()
        self.app_instance.after(100, self._on_tab_selected)

    def _create_widgets(self):
        """Creates and arranges widgets for the Instrument Connection tab."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        conn_frame = ttk.LabelFrame(self, text="Instrument Connection", style='Dark.TLabelframe')
        conn_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        conn_frame.grid_columnconfigure(1, weight=1)

        self.find_button = ttk.Button(conn_frame, text="Find Instruments", command=self._find_instruments_action, style='Blue.TButton')
        self.find_button.grid(row=0, column=0, columnspan=3, padx=5, pady=2, sticky="ew")

        ttk.Label(conn_frame, text="Available Resources:", style='TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.resource_combobox = ttk.Combobox(conn_frame, textvariable=self.app_instance.visa_resource_var, state="readonly", style='TCombobox')
        self.resource_combobox.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.resource_combobox.bind("<<ComboboxSelected>>", self._on_resource_selected)

        self.connect_button = ttk.Button(conn_frame, text="Connect", command=self._connect_instrument, style='Green.TButton')
        self.connect_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        self.disconnect_button = ttk.Button(conn_frame, text="Disconnect", command=self._disconnect_instrument, style='Red.TButton')
        self.disconnect_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        settings_frame = ttk.LabelFrame(self, text="Current Instrument Settings", style='Dark.TLabelframe')
        settings_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        settings_frame.grid_columnconfigure(1, weight=1)
        
        self.query_settings_button = ttk.Button(settings_frame, text="Query Settings", command=self._query_settings, style='Blue.TButton')
        self.query_settings_button.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        ttk.Label(settings_frame, text="Manufacturer:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.manufacturer_label = ttk.Label(settings_frame, textvariable=self.app_instance.connected_instrument_manufacturer, style='Dark.TLabel.Value')
        self.manufacturer_label.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(settings_frame, text="Model:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.model_label = ttk.Label(settings_frame, textvariable=self.app_instance.connected_instrument_model, style='Dark.TLabel.Value')
        self.model_label.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(settings_frame, text="Serial Number:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.serial_label = ttk.Label(settings_frame, textvariable=self.app_instance.connected_instrument_serial, style='Dark.TLabel.Value')
        self.serial_label.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(settings_frame, text="Firmware Version:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.version_label = ttk.Label(settings_frame, textvariable=self.app_instance.connected_instrument_version, style='Dark.TLabel.Value')
        self.version_label.grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        ttk.Separator(settings_frame, orient='horizontal').grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)

        ttk.Label(settings_frame, text="Center Freq:").grid(row=6, column=0, padx=5, pady=2, sticky="w")
        self.center_freq_label = ttk.Label(settings_frame, textvariable=self.app_instance.current_center_freq_var, style='Dark.TLabel.Value')
        self.center_freq_label.grid(row=6, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(settings_frame, text="Span:").grid(row=7, column=0, padx=5, pady=2, sticky="w")
        self.span_label = ttk.Label(settings_frame, textvariable=self.app_instance.current_span_var, style='Dark.TLabel.Value')
        self.span_label.grid(row=7, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(settings_frame, text="RBW:").grid(row=8, column=0, padx=5, pady=2, sticky="w")
        self.rbw_label = ttk.Label(settings_frame, textvariable=self.app_instance.current_rbw_var, style='Dark.TLabel.Value')
        self.rbw_label.grid(row=8, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(settings_frame, text="Ref Level:").grid(row=9, column=0, padx=5, pady=2, sticky="w")
        self.ref_level_label = ttk.Label(settings_frame, textvariable=self.app_instance.current_ref_level_var, style='Dark.TLabel.Value')
        self.ref_level_label.grid(row=9, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(settings_frame, text="Trace Mode:").grid(row=10, column=0, padx=5, pady=2, sticky="w")
        self.trace_mode_label = ttk.Label(settings_frame, textvariable=self.app_instance.current_trace_mode_var, style='Dark.TLabel.Value')
        self.trace_mode_label.grid(row=10, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(settings_frame, text="Preamp:").grid(row=11, column=0, padx=5, pady=2, sticky="w")
        self.preamp_status_label = ttk.Label(settings_frame, textvariable=self.app_instance.current_preamp_status_var, style='Dark.TLabel.Value')
        self.preamp_status_label.grid(row=11, column=1, padx=5, pady=2, sticky="ew")

    def _find_instruments_action(self):
        """Action performed when 'Find Instruments' button is clicked."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Find Instruments button clicked.",
                    file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)
        populate_resources_logic(self.app_instance, self.resource_combobox, self.console_print_func)
        self._update_ui_state()

    def _on_resource_selected(self, event):
        """Handles selection of a VISA resource from the combobox."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Resource selected: {self.app_instance.visa_resource_var.get()}",
                    file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)
        self._update_ui_state()

    def _connect_instrument(self):
        """Action performed when 'Connect' button is clicked."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Connect button clicked.",
                    file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)
        if connect_instrument_logic(app_instance=self.app_instance, console_print_func=self.console_print_func):
            self.console_print_func(f"✅ Connected to {self.app_instance.visa_resource_var.get()}")
            write_safe(self.app_instance.inst, "*RST", self.app_instance, self.console_print_func)
            self._query_settings()
        else:
            self.console_print_func(f"❌ Failed to connect to {self.app_instance.visa_resource_var.get()}")
        self._update_ui_state()
        update_connection_status_logic(app_instance=self.app_instance, is_connected=self.app_instance.is_connected.get(), is_scanning=False, console_print_func=self.console_print_func)

    def _disconnect_instrument(self):
        """Action performed when 'Disconnect' button is clicked."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Disconnect button clicked.",
                    file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)
        if disconnect_instrument_logic(app_instance=self.app_instance, console_print_func=self.console_print_func):
            self.console_print_func("✅ Instrument disconnected.")
            self._clear_settings_display()
        else:
            self.console_print_func("❌ Failed to disconnect instrument.")
        self._update_ui_state()
        update_connection_status_logic(app_instance=self.app_instance, is_connected=self.app_instance.is_connected.get(), is_scanning=False, console_print_func=self.console_print_func)

    def _query_settings(self):
        """Queries the connected instrument for its current settings and updates the display."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Query Settings button clicked.",
                    file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)
        settings = query_current_settings_logic(app_instance=self.app_instance, console_print_func=self.console_print_func)
        if settings:
            # Get and parse the IDN string
            idn_string = settings.get('idn_string', 'N/A')
            if idn_string != 'N/A':
                idn_parts = idn_string.split(',')
                if len(idn_parts) == 4:
                    self.app_instance.connected_instrument_manufacturer.set(idn_parts[0].strip())
                    self.app_instance.connected_instrument_model.set(idn_parts[1].strip())
                    self.app_instance.connected_instrument_serial.set(idn_parts[2].strip())
                    self.app_instance.connected_instrument_version.set(idn_parts[3].strip())
                else:
                    self.app_instance.connected_instrument_manufacturer.set("N/A")
                    self.app_instance.connected_instrument_model.set(idn_string)
                    self.app_instance.connected_instrument_serial.set("N/A")
                    self.app_instance.connected_instrument_version.set("N/A")
            else:
                self.app_instance.connected_instrument_manufacturer.set("N/A")
                self.app_instance.connected_instrument_model.set("N/A")
                self.app_instance.connected_instrument_serial.set("N/A")
                self.app_instance.connected_instrument_version.set("N/A")

            # Update other settings
            center_freq_hz = settings.get('center_freq_hz')
            if center_freq_hz is not None and center_freq_hz != 'N/A':
                self.app_instance.current_center_freq_var.set(f"{float(center_freq_hz) / MHZ_TO_HZ:.3f} MHz")
            else:
                self.app_instance.current_center_freq_var.set("N/A")

            span_hz = settings.get('span_hz')
            if span_hz is not None and span_hz != 'N/A':
                self.app_instance.current_span_var.set(f"{float(span_hz) / MHZ_TO_HZ:.3f} MHz")
            else:
                self.app_instance.current_span_var.set("N/A")

            rbw_hz = settings.get('rbw_hz')
            if rbw_hz is not None and rbw_hz != 'N/A':
                self.app_instance.current_rbw_var.set(f"{float(rbw_hz) / KHZ_TO_HZ:.3f} kHz")
            else:
                self.app_instance.current_rbw_var.set("N/A")

            self.app_instance.current_ref_level_var.set(f"{settings.get('ref_level_dbm', 'N/A')} dBm")
            
            self.app_instance.current_trace_mode_var.set(settings.get('trace_mode', 'N/A'))
            self.app_instance.current_preamp_status_var.set("ON" if settings.get('preamp_on', False) else "OFF")
            
            self.console_print_func("✅ Instrument settings queried and displayed.")
        else:
            self.console_print_func("❌ Failed to query instrument settings.")
        self._update_ui_state()

    def _clear_settings_display(self):
        """Clears the displayed instrument settings."""
        self.app_instance.connected_instrument_manufacturer.set("")
        self.app_instance.connected_instrument_model.set("")
        self.app_instance.connected_instrument_serial.set("")
        self.app_instance.connected_instrument_version.set("")
        self.app_instance.current_center_freq_var.set("")
        self.app_instance.current_span_var.set("")
        self.app_instance.current_rbw_var.set("")
        self.app_instance.current_ref_level_var.set("")
        self.app_instance.current_trace_mode_var.set("")
        self.app_instance.current_preamp_status_var.set("")

    def _update_ui_state(self):
        """Updates button states based on connection status."""
        is_connected = self.app_instance.is_connected.get()
        self.connect_button.config(state='disabled' if is_connected else 'normal')
        self.disconnect_button.config(state='normal' if is_connected else 'disabled')
        self.query_settings_button.config(state='normal' if is_connected else 'disabled')
        self.resource_combobox.config(state='disabled' if is_connected else 'readonly')
        self.find_button.config(state='disabled' if is_connected else 'normal')

    def _on_tab_selected(self, event=None):
        """Handles when this tab is selected."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Instrument Tab selected. Populating resources and updating UI state.",
                    file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)
        populate_resources_logic(self.app_instance, self.resource_combobox, self.console_print_func)
        self._update_ui_state()