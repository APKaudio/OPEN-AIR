# tabs/Instrument/tab_instrument_child_connection.py
#
# This file defines the InstrumentTab, a Tkinter Frame for handling instrument
# connection and disconnection. This refactored version is a mock for testing,
# using a shared MQTT utility for communication instead of direct device control.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250827.195000.1

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import json
import paho.mqtt.client as mqtt
import paho.mqtt.client as paho
import threading
from collections import defaultdict

# --- Module Imports ---
# We are intentionally removing the following imports for this test version:
# from .instrument_logic import connect_instrument_logic, disconnect_instrument_logic, populate_resources_logic
# from yak.utils_yak_setting_handler import reset_device, do_power_cycle
# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from display.styling.style import THEMES, DEFAULT_THEME

# --- Global Scope Variables ---
current_version = "20250827.195000.1"
current_version_hash = (20250827 * 195000 * 1)
current_file = f"{os.path.basename(__file__)}"

# --- Constant Variables (No Magic Numbers) ---
DEFAULT_TITLE_FONT = ("Helvetica", 12, "bold")


class InstrumentTab(ttk.Frame):
    """
    A Tkinter Frame for handling instrument connection and disconnection.
    """

    def __init__(self, parent, mqtt_util, *args, **kwargs):
        """
        Initializes the InstrumentTab frame.
        """
        super().__init__(parent, *args, **kwargs)

        self.mqtt_util = mqtt_util
        self.pack(fill=tk.BOTH, expand=True)
        self.style = ttk.Style()

        self._create_widgets()

    def _create_widgets(self):
        """
        Creates the widgets for the Instrument Connection Tab.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🟢 Entering {current_function_name}. Creating simplified widgets for the Connection Tab. 🛠️",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            # Main Frame for the widgets
            main_frame = ttk.Frame(self, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Title
            title_label = ttk.Label(main_frame, text="Instrument Connection", font=DEFAULT_TITLE_FONT)
            title_label.pack(pady=10)

            # --- Connection Status Display ---
            # We use a StringVar to dynamically update the status message.
            self.status_text = tk.StringVar(value="Status: Not Connected")
            # The style was changed from 'Dark.TLabel.Value' to 'Dark.TLabel'.
            self.status_label = ttk.Label(main_frame, textvariable=self.status_text, style='Dark.TLabel')
            self.status_label.pack(pady=5)
            self.style.configure('Dark.TLabel', foreground='red')

            # --- Buttons ---
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(pady=10)

            self.connect_button = ttk.Button(button_frame, text="Connect", command=self._connect_button_handler, style='Dark.TButton')
            self.connect_button.pack(side=tk.LEFT, padx=5)

            self.disconnect_button = ttk.Button(button_frame, text="Disconnect", command=self._disconnect_button_handler, style='Dark.TButton')
            self.disconnect_button.pack(side=tk.LEFT, padx=5)

            # --- Log Display ---
            self.log_text = tk.Text(main_frame, height=10, state=tk.DISABLED, bg=THEMES[DEFAULT_THEME]['entry_bg'], fg=THEMES[DEFAULT_THEME]['entry_fg'])
            self.log_text.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # --- Success Log ---
            console_log("✅ Celebration of success! The connection tab did build its simplified widgets.")

        except Exception as e:
            console_log(f"❌ Error in _create_widgets: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
    def _log_to_gui(self, message):
        """
        Adds a message to the GUI log display.
        """
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _connect_button_handler(self):
        """
        Handles the Connect button click.
        """
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🛠️🟢 Entering '{current_function_name}' to handle connect button click.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            # We mock the connection logic here.
            self.status_text.set("Status: Connecting...")
            self.status_label.configure(foreground='yellow')
            
            # Publish a message to signal the connection attempt.
            self.mqtt_util.publish_message(topic="OPEN-AIR/commands/instrument", subtopic="connect", value={"action": "connect"})
            
            self._log_to_gui("Attempting to connect...")
            
            # A mock success message.
            self._log_to_gui("✅ Connection attempt signaled. Waiting for instrument confirmation...")
            self.status_text.set("Status: Connected")
            self.status_label.configure(foreground='green')

            console_log("✅ Celebration of success! The connect button did handle its connection attempt.")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _disconnect_button_handler(self):
        """
        Handles the Disconnect button click.
        """
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name

        debug_log(
            message=f"🛠️🟢 Entering '{current_function_name}' to handle disconnect button click.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            # We mock the disconnection logic here.
            self.status_text.set("Status: Disconnecting...")
            self.status_label.configure(foreground='yellow')
            
            # Publish a message to signal the disconnection attempt.
            self.mqtt_util.publish_message(topic="OPEN-AIR/commands/instrument", subtopic="disconnect", value={"action": "disconnect"})

            self._log_to_gui("Attempting to disconnect...")
            
            # A mock success message.
            self._log_to_gui("✅ Disconnection attempt signaled. Waiting for instrument confirmation...")
            self.status_text.set("Status: Not Connected")
            self.status_label.configure(foreground='red')

            console_log("✅ Celebration of success! The disconnect button did handle its disconnection attempt.")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )