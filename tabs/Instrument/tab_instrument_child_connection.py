# tabs/Instrument/tab_instrument_child_connection.py
#
# This file defines the InstrumentTab, a Tkinter Frame for connecting to
# a spectrum analyzer via VISA.
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
# Version 20250811.222500.1 (REMOVED: The entire query-and-display settings section has been removed to simplify the tab and align with the new, dedicated SettingsTab.)

current_version = "20250811.222500.1"
current_version_hash = 20250811 * 222500 * 1

import tkinter as tk
from tkinter import ttk
import inspect
import os

# Import logical functions
from tabs.Instrument.instrument_logic import connect_instrument_logic, disconnect_instrument_logic, populate_resources_logic
from display.debug_logic import debug_log
from display.console_logic import console_log
from src.connection_status_logic import update_connection_status_logic
from tabs.Instrument.utils_instrument_read_and_write import write_safe

class InstrumentTab(ttk.Frame):
    """
    A Tkinter Frame that allows connecting to a spectrum analyzer via VISA.
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
        self.grid_rowconfigure(0, weight=1)

        conn_frame = ttk.LabelFrame(self, text="Instrument Connection", style='Dark.TLabelframe')
        conn_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        conn_frame.grid_columnconfigure(1, weight=1)

        self.find_button = ttk.Button(conn_frame, text="Find Instruments", command=self._find_instruments_action, style='Blue.TButton')
        self.find_button.grid(row=0, column=0, columnspan=2, padx=5, pady=2, sticky="ew")

        ttk.Label(conn_frame, text="Available Resources:", style='TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.resource_combobox = ttk.Combobox(conn_frame, textvariable=self.app_instance.visa_resource_var, state="readonly", style='TCombobox')
        self.resource_combobox.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.resource_combobox.bind("<<ComboboxSelected>>", self._on_resource_selected)

        self.connect_button = ttk.Button(conn_frame, text="Connect", command=self._connect_instrument, style='Green.TButton')
        self.connect_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        self.disconnect_button = ttk.Button(conn_frame, text="Disconnect", command=self._disconnect_instrument, style='Red.TButton')
        self.disconnect_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

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
            # The user will now query and set their own settings in the dedicated tab
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
        else:
            self.console_print_func("❌ Failed to disconnect instrument.")
        self._update_ui_state()
        update_connection_status_logic(app_instance=self.app_instance, is_connected=self.app_instance.is_connected.get(), is_scanning=False, console_print_func=self.console_print_func)

    def _update_ui_state(self):
        """Updates button states based on connection status."""
        is_connected = self.app_instance.is_connected.get()
        self.connect_button.config(state='disabled' if is_connected else 'normal')
        self.disconnect_button.config(state='normal' if is_connected else 'disabled')
        self.resource_combobox.config(state='disabled' if is_connected else 'readonly')
        self.find_button.config(state='disabled' if is_connected else 'normal')

    def _on_tab_selected(self, event=None):
        """Handles when this tab is selected."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Instrument Tab selected. Updating UI state.",
                    file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)
        self._update_ui_state()