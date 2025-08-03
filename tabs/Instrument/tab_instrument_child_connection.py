# tabs/Instrument/tab_instrument_child_connection.py
#
# This file manages the Instrument Connection tab in the GUI, handling
# VISA resource discovery, instrument connection/disconnection, and
# displaying current instrument settings. This version restores the
# simplified step-by-step user workflow.
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
# Version 20250803.191600.0 (FIXED: TclError by properly handling 'style_obj' in constructor.)
# Version 20250803.191500.0 (Refactored to restore simplified step-by-step connection workflow.)

current_version = "20250803.191600.0"

import tkinter as tk
from tkinter import ttk
import inspect
import os

from src.debug_logic import debug_log
from src.console_logic import console_log
from src.settings_and_config.config_manager import save_config

# Import instrument logic and utility functions
from tabs.Instrument.instrument_logic import (
    populate_resources_logic, connect_instrument_logic, disconnect_instrument_logic,
    query_current_settings_logic
)
from ref.frequency_bands import MHZ_TO_HZ

class InstrumentTab(ttk.Frame):
    """
    Manages the Instrument Connection tab with a step-by-step workflow.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        # Pop the custom 'style_obj' argument before it gets to the ttk.Frame constructor
        kwargs.pop('style_obj', None)
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log

        # Tkinter variables for displaying current instrument settings
        self.current_center_freq_var = tk.StringVar(self, value="N/A")
        self.current_span_var = tk.StringVar(self, value="N/A")
        self.current_rbw_var = tk.StringVar(self, value="N/A")
        self.current_ref_level_var = tk.StringVar(self, value="N/A")
        self.current_freq_shift_var = tk.StringVar(self, value="N/A")
        self.current_max_hold_var = tk.StringVar(self, value="N/A")
        self.current_high_sensitivity_var = tk.StringVar(self, value="N/A")

        self._create_widgets()
        self.after(100, self._update_ui_state) # Initial UI state update

    def _create_widgets(self):
        """Creates and arranges the widgets for the tab."""
        self.grid_columnconfigure(0, weight=1)

        # --- Main Connection Frame ---
        connection_frame = ttk.LabelFrame(self, text="Instrument Connection", padding="10", style='Dark.TLabelframe')
        connection_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        connection_frame.grid_columnconfigure(0, weight=1)

        # Step 1: Find Instruments
        self.find_button = ttk.Button(connection_frame, text="STEP 1 - Find Instruments", command=self._find_instruments_action)
        self.find_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Step 2: Choose Resource (created but hidden)
        self.resource_label = ttk.Label(connection_frame, text="STEP 2 - Choose Visa Resource from list:")
        self.resource_combobox = ttk.Combobox(connection_frame, textvariable=self.app_instance.visa_resource_var, state="readonly")
        self.resource_combobox.bind("<<ComboboxSelected>>", self._on_resource_selected)

        # Step 3: Connect Button (created but hidden)
        self.connect_button = ttk.Button(connection_frame, text="STEP 3 - CONNECT", command=self._connect_instrument)

        # --- Current Values Frame ---
        values_frame = ttk.LabelFrame(self, text="Current Instrument Values", padding="10", style='Dark.TLabelframe')
        values_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        values_frame.grid_columnconfigure(1, weight=1)

        # Step 4: Test Connection Button (created but hidden)
        self.query_button = ttk.Button(values_frame, text="STEP 4 - Test connection", command=self._query_settings)

        # Display fields
        labels = ["Center Freq (MHz):", "Span (MHz):", "RBW (Hz):", "Reference Level (dBm):", "Frequency Shift (Hz):", "Max Hold:", "High Sensitivity:"]
        variables = [self.current_center_freq_var, self.current_span_var, self.current_rbw_var, self.current_ref_level_var, self.current_freq_shift_var, self.current_max_hold_var, self.current_high_sensitivity_var]

        for i, (label, var) in enumerate(zip(labels, variables), 1):
            ttk.Label(values_frame, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            ttk.Entry(values_frame, textvariable=var, state='readonly').grid(row=i, column=1, sticky="ew", padx=5, pady=2)

        # Disconnect Button (created but hidden)
        self.disconnect_button = ttk.Button(self, text="Disconnect", command=self._disconnect_instrument)

    def _update_ui_state(self):
        """Updates the visibility and state of all widgets based on the application state."""
        is_connected = self.app_instance.is_connected.get()
        resources_exist = self.resource_combobox['values']

        # Forget all dynamic widgets first
        self.resource_label.grid_forget()
        self.resource_combobox.grid_forget()
        self.connect_button.grid_forget()
        self.query_button.grid_forget()
        self.disconnect_button.grid_forget()

        if is_connected:
            self.find_button.config(state=tk.DISABLED)
            self.query_button.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
            self.disconnect_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        else:
            self.find_button.config(state=tk.NORMAL)
            self._clear_settings_display()
            if resources_exist:
                self.resource_label.grid(row=1, column=0, sticky="w", padx=5, pady=(10, 2))
                self.resource_combobox.grid(row=2, column=0, sticky="ew", padx=5, pady=2)
                self.connect_button.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

    def _find_instruments_action(self):
        """Action for the 'Find Instruments' button."""
        self.console_print_func("Searching for VISA resources...")
        resources = populate_resources_logic(self.app_instance, self.console_print_func)
        self.resource_combobox['values'] = resources
        if resources:
            self.app_instance.visa_resource_var.set(resources[0])
            self.console_print_func(f"Found {len(resources)} device(s). Please select one and connect.")
        else:
            self.app_instance.visa_resource_var.set("")
            self.console_print_func("No VISA devices found.")
        self._update_ui_state()

    def _on_resource_selected(self, event):
        """Saves the selected resource to config when changed."""
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)

    def _connect_instrument(self):
        """Action for the 'Connect' button."""
        connect_instrument_logic(self.app_instance, self.console_print_func)
        self._update_ui_state()
        if self.app_instance.is_connected.get():
            self._query_settings()

    def _disconnect_instrument(self):
        """Action for the 'Disconnect' button."""
        disconnect_instrument_logic(self.app_instance, self.console_print_func)
        self._update_ui_state()

    def _query_settings(self):
        """Action for the 'Test connection' button."""
        if not self.app_instance.is_connected.get():
            self.console_print_func("Not connected. Cannot query settings.")
            return
            
        settings = query_current_settings_logic(self.app_instance, self.console_print_func)
        if settings:
            self.current_center_freq_var.set(f"{settings.get('center_freq_mhz', 'N/A'):.3f}")
            self.current_span_var.set(f"{settings.get('span_mhz', 'N/A'):.3f}")
            self.current_rbw_var.set(f"{settings.get('rbw_hz', 'N/A'):.0f}")
            self.current_ref_level_var.set(f"{settings.get('ref_level_dbm', 'N/A'):.1f}")
            self.current_freq_shift_var.set(f"{settings.get('freq_shift_hz', 'N/A'):.0f}")
            self.current_max_hold_var.set("ON" if settings.get('max_hold_mode', False) else "OFF")
            self.current_high_sensitivity_var.set("ON" if settings.get('high_sensitivity', False) else "OFF")
            self.console_print_func("Successfully queried instrument settings.")
        else:
            self.console_print_func("Failed to query instrument settings.")
            self._clear_settings_display()

    def _clear_settings_display(self):
        """Clears the instrument settings display fields."""
        self.current_center_freq_var.set("N/A")
        self.current_span_var.set("N/A")
        self.current_rbw_var.set("N/A")
        self.current_ref_level_var.set("N/A")
        self.current_freq_shift_var.set("N/A")
        self.current_max_hold_var.set("N/A")
        self.current_high_sensitivity_var.set("N/A")

    def _on_tab_selected(self, event):
        """Called when the tab is selected."""
        self._update_ui_state()
