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
# Version 20250818.205500.2 (FIXED: Corrected the Tkinter variable name to prevent AttributeError.)

current_version = "20250818.205500.2"
current_version_hash = 20250818 * 205500 * 2

import tkinter as tk
from tkinter import ttk, messagebox
import inspect
import os
import threading
import time

# Import low-level VISA utilities
from .instrument_logic import connect_instrument_logic, disconnect_instrument_logic, populate_resources_logic
from yak.utils_yak_setting_handler import reset_device, do_power_cycle
from display.debug_logic import debug_log
from display.console_logic import console_log

class InstrumentTab(ttk.Frame):
    def __init__(self, master=None, app_instance=None, console_print_func=None, parent_notebook_ref=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        self.parent_notebook_ref = parent_notebook_ref

        # Tkinter StringVars for displaying instrument details
        self.manufacturer_var = tk.StringVar(value="N/A")
        self.model_var = tk.StringVar(value="N/A")
        self.serial_number_var = tk.StringVar(value="N/A")
        self.version_var = tk.StringVar(value="N/A")

        self._create_widgets()

    def _create_widgets(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering _create_widgets. Creating simplified widgets for the Connection Tab. 🛠️",
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
        # FIXED: Changed variable name to app_instance.instrument_visa_resource_var
        self.resource_combobox = ttk.Combobox(main_frame, textvariable=self.app_instance.instrument_visa_resource_var, style='TCombobox', state='readonly')
        self.resource_combobox.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Connect/Disconnect button
        self.connect_button = ttk.Button(main_frame, text="Connect", command=self._toggle_connection, style='Green.TButton')
        self.connect_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # NEW: Instrument Details Frame
        self.details_frame = ttk.LabelFrame(main_frame, text="Device Details", style='Dark.TLabelframe', padding=10)
        self.details_frame.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        self.details_frame.grid_columnconfigure(1, weight=1)
        self.details_frame.grid_remove() # Hide initially

        ttk.Label(self.details_frame, text="Manufacturer:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(self.details_frame, textvariable=self.manufacturer_var, style='Dark.TLabel.Value').grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(self.details_frame, text="Model:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(self.details_frame, textvariable=self.model_var, style='Dark.TLabel.Value').grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(self.details_frame, text="Serial Number:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(self.details_frame, textvariable=self.serial_number_var, style='Dark.TLabel.Value').grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(self.details_frame, text="Firmware Version:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(self.details_frame, textvariable=self.version_var, style='Dark.TLabel.Value').grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        # NEW: Reset and Power Cycle Buttons Frame
        control_buttons_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        control_buttons_frame.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        control_buttons_frame.grid_columnconfigure(0, weight=1)
        control_buttons_frame.grid_columnconfigure(1, weight=1)

        self.reset_button = ttk.Button(control_buttons_frame, text="Reset Instrument (*RST)", command=self._reset_instrument, style='Orange.TButton')
        self.reset_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.reset_button.config(state=tk.DISABLED) # Start disabled
        
        self.power_cycle_button = ttk.Button(control_buttons_frame, text="Power Cycle", command=self._power_cycle_instrument, style='Red.TButton')
        self.power_cycle_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.power_cycle_button.config(state=tk.DISABLED) # Start disabled

        self.app_instance.is_connected.trace_add('write', self._update_connection_status)
        
        debug_log(f"Simplified widgets for Connection Tab created. Ready to go! ",
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
            self.reset_button.config(state=tk.NORMAL)
            self.power_cycle_button.config(state=tk.NORMAL)
            self.details_frame.grid()
            
            # Populate the new labels
            self.manufacturer_var.set(self.app_instance.connected_instrument_manufacturer.get())
            self.model_var.set(self.app_instance.connected_instrument_model.get())
            self.serial_number_var.set(self.app_instance.connected_instrument_serial.get())
            self.version_var.set(self.app_instance.connected_instrument_version.get())

            # FIXED: Add a check to ensure the settings_tab exists before trying to switch to it.
            if self.parent_notebook_ref and hasattr(self.parent_notebook_ref, 'settings_tab'):
                self.parent_notebook_ref.switch_to_settings_tab()
                self.console_print_func("✅ Connection successful. Switched to Settings tab.")
        else:
            self.connect_button.config(text="Connect", style='Green.TButton')
            self.populate_button.config(state=tk.NORMAL)
            self.resource_combobox.config(state='readonly')
            self.reset_button.config(state=tk.DISABLED)
            self.power_cycle_button.config(state=tk.DISABLED)
            self.details_frame.grid_remove()
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
    
    # NEW: Reset Button Functionality
    def _reset_instrument(self):
        # [A brief, one-sentence description of the function's purpose.]
        # Sends a soft reset command to the instrument in a separate thread.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Reset button clicked. Starting reset thread. ♻️",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        reset_thread = threading.Thread(target=reset_device, args=(self.app_instance, self.console_print_func))
        reset_thread.start()
    
    # NEW: Power Cycle Functionality
    def _power_cycle_instrument(self):
        # [A brief, one-sentence description of the function's purpose.]
        # Sends a power reset command to the instrument in a separate thread.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Power Cycle button clicked. Starting power cycle thread. 💥",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        power_cycle_thread = threading.Thread(target=do_power_cycle, args=(self.app_instance, self.console_print_func))
        power_cycle_thread.start()
        
    def _on_tab_selected(self, event=None):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Connection Tab selected. What are we doing now? 🤔",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        is_connected = self.app_instance.is_connected.get()
        if not is_connected:
            self._populate_resources()

