# tabs/Instrument/tab_instrument_child_connection.py
#
# This file defines the InstrumentTab, a Tkinter Frame for handling instrument
# connection and disconnection.
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
# Version 20250817.183400.1 (FIXED: Added a check for the settings_tab before attempting to switch to it.)
#
# Version 20250811.215000.4 (UPDATED: Restructured the marker settings frame into two separate sections and added a 'Peak search' button.)

current_version = "20250817.183400.1"
current_version_hash = 20250817 * 183400 * 1

import tkinter as tk
from tkinter import ttk, messagebox
import inspect
import os
import threading
from datetime import datetime

# Import low-level VISA utilities
from tabs.Instrument.instrument_logic import connect_instrument_logic, disconnect_instrument_logic, populate_resources_logic
from display.debug_logic import debug_log
from display.console_logic import console_log

class InstrumentTab(ttk.Frame):
    def __init__(self, master=None, app_instance=None, console_print_func=None, parent_notebook_ref=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        self.parent_notebook_ref = parent_notebook_ref
        self._create_widgets()

    def _create_widgets(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering _create_widgets. Creating simplified widgets for the Connection Tab.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        self.grid_columnconfigure(0, weight=1)

        # Main frame
        main_frame = ttk.Frame(self, style='Dark.TFrame')
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)

        # Button to populate VISA resources
        self.populate_button = ttk.Button(main_frame, text="Populate list of available VISA Devices", command=self._populate_resources, style='Blue.TButton')
        self.populate_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Dropdown for VISA resources
        self.resource_combobox = ttk.Combobox(main_frame, textvariable=self.app_instance.visa_resource_var, style='TCombobox', state='readonly')
        self.resource_combobox.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Connect/Disconnect button
        self.connect_button = ttk.Button(main_frame, text="Connect", command=self._toggle_connection, style='Green.TButton')
        self.connect_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        self.app_instance.is_connected.trace_add('write', self._update_connection_status)
        
        debug_log(f"Simplified widgets for Connection Tab created. Ready to go! 🚀",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

    def _update_connection_status(self, *args):
        current_function = inspect.currentframe().f_code.co_name
        is_connected = self.app_instance.is_connected.get()
        debug_log(f"Updating connection status. Is it connected? {is_connected}. 🤔",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        if is_connected:
            self.connect_button.config(text="Disconnect", style='Red.TButton')
            self.populate_button.config(state=tk.DISABLED)
            self.resource_combobox.config(state='disabled')
            
            # FIXED: Add a check to ensure the settings_tab exists before trying to switch to it.
            if self.parent_notebook_ref and hasattr(self.parent_notebook_ref, 'settings_tab'):
                self.parent_notebook_ref.switch_to_settings_tab()
                self.console_print_func("✅ Connection successful. Switched to Settings tab.")
        else:
            self.connect_button.config(text="Connect", style='Green.TButton')
            self.populate_button.config(state=tk.NORMAL)
            self.resource_combobox.config(state='readonly')
            self.console_print_func("❌ Disconnected from instrument.")

    def _toggle_connection(self):
        is_connected = self.app_instance.is_connected.get()
        if is_connected:
            self._disconnect_instrument()
        else:
            self._connect_instrument()

    def _populate_resources(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Populate resources button clicked. Finding devices! 🔎",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        populate_resources_logic(self.app_instance, self.resource_combobox, self.console_print_func)
    
    def _connect_instrument(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Connect button clicked. Starting connection thread. 🔗",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        connection_thread = threading.Thread(target=connect_instrument_logic, args=(self.app_instance, self.console_print_func))
        connection_thread.start()
        
    def _disconnect_instrument(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Disconnect button clicked. Starting disconnection thread. 🔌",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        disconnection_thread = threading.Thread(target=disconnect_instrument_logic, args=(self.app_instance, self.console_print_func))
        disconnection_thread.start()
        
    def _on_tab_selected(self, event=None):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Connection Tab selected. What are we doing now? 🤔",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        is_connected = self.app_instance.is_connected.get()
        if not is_connected:
            self._populate_resources()