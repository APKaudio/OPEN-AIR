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
# Version 20250813.001000.3

import tkinter as tk
from tkinter import ttk
import inspect
import os
from datetime import datetime

# Import logical functions
from tabs.Instrument.instrument_logic import connect_instrument_logic, disconnect_instrument_logic, populate_resources_logic
from display.debug_logic import debug_log
from display.console_logic import console_log
from src.connection_status_logic import update_connection_status_logic
from tabs.Instrument.utils_instrument_read_and_write import write_safe

# --- Version Information ---
current_version = "20250813.001000.3"
current_version_hash = (20250813 * 1000 * 3)

class InstrumentTab(ttk.Frame):
    """
    A Tkinter Frame that allows connecting to a spectrum analyzer via VISA.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, parent_notebook_ref=None, **kwargs):
        # Function Description
        # Initializes the Instrument Connection Tab.
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        self.parent_notebook_ref = parent_notebook_ref # Store reference to parent

        self.resources_found = False # Flag to track if instruments have been found

        self._create_widgets()
        self._update_ui_state()
        self.app_instance.after(100, self._on_tab_selected)

    def _create_widgets(self):
        # Function Description
        # Creates and arranges the streamlined widgets for the Instrument Connection tab.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating streamlined connection widgets.",
                  file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # -- Row 0: Find Instruments --
        self.find_button = ttk.Button(self, text="Find Instruments", command=self._find_instruments_action, style='Blue.TButton')
        self.find_button.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), ipady=5, sticky="ew")

        # -- Row 1: Available Resources --
        ttk.Label(self, text="Available Resources:", style='TLabel').grid(row=1, column=0, padx=(10,5), pady=2, sticky="w")
        self.resource_combobox = ttk.Combobox(self, textvariable=self.app_instance.visa_resource_var, state="readonly", style='TCombobox')
        self.resource_combobox.grid(row=1, column=1, padx=(5,10), pady=2, sticky="ew")
        self.resource_combobox.bind("<<ComboboxSelected>>", self._on_resource_selected)

        # -- Row 2: Combined Connect/Disconnect Button --
        self.connect_disconnect_button = ttk.Button(self, text="Connect")
        self.connect_disconnect_button.grid(row=2, column=0, columnspan=2, padx=10, pady=(5, 10), ipady=10, sticky="ew")

    def _find_instruments_action(self):
        """Action performed when 'Find Instruments' button is clicked."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Find Instruments button clicked.",
                    file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)
        
        resources = populate_resources_logic(self.app_instance, self.resource_combobox, self.console_print_func)
        if resources:
            self.resources_found = True
        else:
            self.resources_found = False

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
            # Switch to settings tab on successful connection
            if self.parent_notebook_ref:
                self.parent_notebook_ref.switch_to_settings_tab()
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
            self.resources_found = False # Reset the found flag
        else:
            self.console_print_func("❌ Failed to disconnect instrument.")
        
        self._update_ui_state()
        update_connection_status_logic(app_instance=self.app_instance, is_connected=self.app_instance.is_connected.get(), is_scanning=False, console_print_func=self.console_print_func)

    def _update_ui_state(self):
        """Updates all widget states and styles based on connection and resource status."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating connection UI state.",
                  file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)
                  
        is_connected = self.app_instance.is_connected.get()
        resource_selected = bool(self.app_instance.visa_resource_var.get())

        # Find Instruments Button Logic
        if is_connected:
            self.find_button.config(state='disabled', style='TButton') # Default greyed-out
        elif self.resources_found:
            self.find_button.config(state='normal', style='Green.TButton')
        else:
            self.find_button.config(state='normal', style='Blue.TButton')
        
        # Resource ComboBox Logic
        self.resource_combobox.config(state='disabled' if is_connected else 'readonly')

        # Connect/Disconnect Button Logic
        if is_connected:
            self.connect_disconnect_button.config(
                text="Disconnect",
                command=self._disconnect_instrument,
                style='Red.TButton',
                state='normal'
            )
        else:
            self.connect_disconnect_button.config(
                text="Connect",
                command=self._connect_instrument,
                style='Green.TButton',
                state='normal' if resource_selected else 'disabled'
            )

    def _on_tab_selected(self, event=None):
        """Handles when this tab is selected."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Instrument Tab selected. Updating UI state.",
                    file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)
        self._update_ui_state()