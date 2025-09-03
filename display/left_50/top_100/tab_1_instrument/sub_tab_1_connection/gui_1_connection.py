# display/left_50/top_100/tab_1_instrument/sub_tab_1_connection/gui_1_connection.py
#
# This file defines the InstrumentTab, a Tkinter Frame for handling instrument
# connection and disconnection. This version has been refactored to use the
# VisaDeviceManager directly for connection logic, as per the new definitive
# operating protocol.
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
# Version 20250902.234858.1

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from display.styling.style import THEMES, DEFAULT_THEME
# [A] Import the manager to be used directly by the GUI
from managers.manager_visa_device_search import VisaDeviceManager
from workers.worker_mqtt_controller_util import MqttControllerUtility

# --- Global Scope Variables ---
current_version = "20250902.234858.1"
current_version_hash = (20250902 * 234858 * 1)
current_file = f"{os.path.basename(__file__)}"

# --- Constant Variables (No Magic Numbers) ---
DEFAULT_TITLE_FONT = ("Helvetica", 12, "bold")


class InstrumentTab(ttk.Frame):
    """
    A Tkinter Frame for handling instrument connection and disconnection.
    This GUI now communicates directly with the VisaDeviceManager instance.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        """
        Initializes the InstrumentTab frame.
        """
        super().__init__(parent, *args, **kwargs)

        self.mqtt_util = mqtt_util
        self.pack(fill=tk.BOTH, expand=True)
        self.style = ttk.Style()
        
        # [A] The GUI now directly holds state variables for its display
        self.visa_manager = VisaDeviceManager(mqtt_controller=self.mqtt_util)
        self.visa_resource_var = tk.StringVar(value="Select a device...")
        self.is_connected = tk.BooleanVar(value=False)
        self.visa_resources = []

        self.manufacturer_var = tk.StringVar(value="N/A")
        self.model_var = tk.StringVar(value="N/A")
        self.serial_number_var = tk.StringVar(value="N/A")
        self.version_var = tk.StringVar(value="N/A")
        self.connection_time_var = tk.StringVar(value="N/A")

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
            main_frame = ttk.Frame(self, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)

            title_label = ttk.Label(main_frame, text="Instrument Connection", font=DEFAULT_TITLE_FONT)
            title_label.pack(pady=10)

            device_frame = ttk.LabelFrame(main_frame, text="Device Selection", padding="10")
            device_frame.pack(fill=tk.X, expand=True, padx=10, pady=5)
            
            self.search_button = ttk.Button(device_frame, text="Search for devices", command=self._on_search_button_press)
            self.search_button.pack(fill=tk.X, padx=5, pady=2)
            
            self.resource_combobox = ttk.Combobox(device_frame, textvariable=self.visa_resource_var, state='readonly')
            self.resource_combobox.pack(fill=tk.X, padx=5, pady=2)

            self.connect_button = ttk.Button(device_frame, text="Connect", command=self._on_connect_button_press)
            self.connect_button.pack(fill=tk.X, padx=5, pady=2)

            self.status_text = tk.StringVar(value="Status: Not Connected")
            self.status_label = ttk.Label(main_frame, textvariable=self.status_text)
            self.status_label.pack(pady=5)
            self.style.configure('Connected.TLabel', foreground='green')
            self.style.configure('Disconnected.TLabel', foreground='red')
            self.status_label.configure(style='Disconnected.TLabel')

            self.details_frame = ttk.LabelFrame(main_frame, text="Device Details", padding="10")
            self.details_frame.pack(fill=tk.X, expand=True, padx=10, pady=5)
            self.details_frame.pack_forget()




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
            
    def _update_ui_state(self, *args):
        # Callback to update the UI when the connection state changes.
        is_connected = self.is_connected.get()
        if is_connected:
            self.connect_button.config(text="Disconnect")
            self.status_text.set("Status: Connected")
            self.status_label.configure(style='Connected.TLabel')
            self.details_frame.pack(fill=tk.X, expand=True, padx=10, pady=5)
        else:
            self.connect_button.config(text="Connect")
            self.status_text.set("Status: Not Connected")
            self.status_label.configure(style='Disconnected.TLabel')
            self.details_frame.pack_forget()
            self.manufacturer_var.set("N/A")
            self.model_var.set("N/A")
            self.serial_number_var.set("N/A")
            self.version_var.set("N/A")
            self.connection_time_var.set("N/A")
            self.visa_resource_var.set("Select a device...")

    def _log_to_gui(self, message):
            console_log(message)
    def _on_search_button_press(self):
        self._log_to_gui("Searching for VISA devices...")
        # FIX: The GUI now calls the public method on the manager.
        self.visa_manager.search_resources(console_print_func=self._log_to_gui)

    def _on_resources_found(self, topic, payload):
        try:
            # FIX: The payload for the list is a JSON string.
            if topic.endswith("list"):
                resources = json.loads(json.loads(payload)["value"])
                self.visa_resources = resources
                self.resource_combobox['values'] = self.visa_resources
                if self.visa_resources:
                    self.visa_resource_var.set(self.visa_resources[0])
                else:
                    self.visa_resource_var.set("No devices found.")
            # FIX: This callback handles the selection message as well.
            elif topic.endswith("selected"):
                selected_resource = json.loads(payload)["value"]
                if selected_resource:
                     self.visa_resource_var.set(selected_resource)

        except json.JSONDecodeError:
            self._log_to_gui("❌ Failed to decode resources payload.")

    def _on_connect_button_press(self):
        is_connected = self.is_connected.get()
        if is_connected:
            self._log_to_gui("Attempting to disconnect...")
            # FIX: The GUI now calls the public method on the manager.
            self.visa_manager.disconnect_instrument(console_print_func=self._log_to_gui)
        else:
            selected_resource = self.visa_resource_var.get()
            if selected_resource and selected_resource != "Select a device...":
                self._log_to_gui(f"Attempting to connect to {selected_resource}...")
                # FIX: The GUI now calls the public method on the manager.
                self.visa_manager.connect_instrument(resource_name=selected_resource, console_print_func=self._log_to_gui)
            else:
                self._log_to_gui("❌ Please select a device to connect to.")

    def _on_connection_status_change(self, topic, payload):
        try:
            payload_data = json.loads(payload)
            status = payload_data.get('value')
            if status == "success":
                self.is_connected.set(True)
            elif status == "disconnected" or status == "failed":
                self.is_connected.set(False)
        except json.JSONDecodeError:
            self._log_to_gui("❌ Failed to decode connection status payload.")
    
 
       


# 🏃 This is the standard entry point for a Python script.
# The code inside this block only runs when the script is executed directly.
if __name__ == "__main__":
    class MockMqttUtil:
        def add_subscriber(self, topic_filter, callback_func):
            pass
        def publish_message(self, topic, subtopic, value, retain=False):
            pass
    
    console_log("--- Initializing the Dynamic GUI Builder ---")
    mock_mqtt_util = MockMqttUtil()
    app = InstrumentTab(parent=None, mqtt_util=mock_mqtt_util)
    app.mainloop()
    console_log("--- Application closed. ---")