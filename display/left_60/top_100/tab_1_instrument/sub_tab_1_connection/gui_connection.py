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
# Version 20250823.132200.1

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import json
import paho.mqtt.client as mqtt
import threading
from collections import defaultdict

# --- Module Imports ---
# We are intentionally removing the following imports for this test version:
# from .instrument_logic import connect_instrument_logic, disconnect_instrument_logic, populate_resources_logic
# from yak.utils_yak_setting_handler import reset_device, do_power_cycle
from datasets.logging import debug_log, console_log
from display.styling.style import THEMES, DEFAULT_THEME
from workers.mqtt_controller_util import MqttControllerUtility

# --- Global Scope Variables ---
CURRENT_DATE = datetime.datetime.now().strftime("%Y%m%d")
CURRENT_TIME = datetime.datetime.now().strftime("%H%M%S")
CURRENT_TIME_HASH = int(datetime.datetime.now().strftime("%H%M%S"))
REVISION_NUMBER = 1
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME_HASH * REVISION_NUMBER)
current_file = f"tabs/Instrument/tab_instrument_child_connection.py"

# Mocked resources for the UI
MOCK_VISA_RESOURCES = ["ASRL1::INSTR", "GPIB0::2::INSTR", "TCPIP::192.168.1.1::INSTR"]


class InstrumentTab(ttk.Frame):
    """
    A Tkinter Frame for handling instrument connection and disconnection.
    This refactored version is a mock for testing, using a shared MQTT utility for communication instead of direct device control.
    """
    def __init__(self, master=None, mqtt_util=None, *args, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill="both", expand=True)

        self.mqtt_util = mqtt_util
        self._message_counter = 0

        # Tkinter StringVars for displaying instrument details
        self.manufacturer_var = tk.StringVar(self, value="N/A")
        self.model_var = tk.StringVar(self, value="N/A")
        self.serial_number_var = tk.StringVar(self, value="N/A")
        self.version_var = tk.StringVar(self, value="N/A")
        self.resource_var = tk.StringVar(self, value="")
        self.is_connected = tk.BooleanVar(self, value=False)
        self.mqtt_status_var = tk.StringVar(self, value="Last MQTT Payload: N/A")

        self._apply_styles(theme_name=DEFAULT_THEME)
        self._create_widgets()
        
        if self.mqtt_util:
            self.mqtt_util.add_subscriber(topic_filter="conductor/test/#", callback_func=self._on_message)

    def _apply_styles(self, theme_name: str):
        """Applies a theme based on the central style definition."""
        colors = THEMES.get(theme_name)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure('TFrame', background=colors["bg"])
        style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
        style.configure('TButton', background=colors["accent"], foreground=colors["text"])
        style.map('Orange.TButton',
                  background=[('!active', 'orange'), ('active', 'orange')])
        style.map('Blue.TButton',
                  background=[('!active', colors['accent']), ('active', colors['secondary'])])
        style.map('TButton',
                  background=[('active', colors['secondary'])])
        style.map('Red.TButton',
                  background=[('!active', 'red'), ('active', 'darkred')])
        style.map('Green.TButton',
                  background=[('!active', 'green'), ('active', 'darkgreen')])
        style.configure('Dark.TLabelframe', background=colors["bg"], foreground=colors["fg"])
        style.configure('Dark.TLabel.Value', background=colors["bg"], foreground=colors["fg"])

    def _create_widgets(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering _create_widgets. Creating simplified widgets for the Connection Tab. 🛠️",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function,
                    console_print_func=console_log)
        
        self.grid_columnconfigure(0, weight=1)

        # Main frame
        main_frame = ttk.Frame(self, style='Dark.TFrame')
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)

        # Button to populate VISA resources
        self.populate_button = ttk.Button(main_frame, text="Populate list of available VISA Devices", command=lambda: self._publish_test_message(button_id="populate"), style='Blue.TButton')
        self.populate_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Dropdown for VISA resources
        self.resource_combobox = ttk.Combobox(main_frame, textvariable=self.resource_var, values=MOCK_VISA_RESOURCES, state='readonly', style='TCombobox')
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

        self.reset_button = ttk.Button(control_buttons_frame, text="Reset Instrument (*RST)", command=lambda: self._publish_test_message(button_id="reset"), style='Orange.TButton')
        self.reset_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.reset_button.config(state=tk.DISABLED) # Start disabled
        
        self.power_cycle_button = ttk.Button(control_buttons_frame, text="Power Cycle", command=lambda: self._publish_test_message(button_id="power_cycle"), style='Red.TButton')
        self.power_cycle_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.power_cycle_button.config(state=tk.DISABLED) # Start disabled

        # NEW: MQTT Status Label
        mqtt_status_frame = ttk.Frame(self)
        mqtt_status_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        mqtt_status_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(mqtt_status_frame, textvariable=self.mqtt_status_var, anchor="center").grid(row=0, column=0, sticky="ew")

        # Store a reference to the buttons for styling updates
        self._button_status = defaultdict(lambda: None)
        self._button_status["populate"] = self.populate_button
        self._button_status["connect"] = self.connect_button
        self._button_status["disconnect"] = self.connect_button
        self._button_status["reset"] = self.reset_button
        self._button_status["power_cycle"] = self.power_cycle_button
        
        debug_log(f"Simplified widgets for Connection Tab created. Ready to go! ",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function,
                    console_print_func=console_log)


    def _update_connection_status(self, is_connected):
        """Updates the UI based on the mock connection status."""
        if is_connected:
            self.connect_button.config(text="Disconnect", style='Red.TButton')
            self.populate_button.config(state=tk.DISABLED)
            self.resource_combobox.config(state='disabled')
            self.reset_button.config(state=tk.NORMAL)
            self.power_cycle_button.config(state=tk.NORMAL)
            self.details_frame.grid()
            
            # Mock device details
            self.manufacturer_var.set("MockCo")
            self.model_var.set("MockModel-9000")
            self.serial_number_var.set("SN12345678")
            self.version_var.set("v1.0.0")

            console_log("✅ Connection successful. UI updated.")
        else:
            self.connect_button.config(text="Connect", style='Green.TButton')
            self.populate_button.config(state=tk.NORMAL)
            self.resource_combobox.config(state='readonly')
            self.reset_button.config(state=tk.DISABLED)
            self.power_cycle_button.config(state=tk.DISABLED)
            self.details_frame.grid_remove()
            self.manufacturer_var.set("N/A")
            self.model_var.set("N/A")
            self.serial_number_var.set("N/A")
            self.version_var.set("N/A")
            console_log("❌ Disconnected from instrument. UI updated.")
    
    def _toggle_connection(self):
        """Toggles the mock connection state and publishes a test message."""
        if self.is_connected.get():
            self._publish_test_message("disconnect")
        else:
            self._publish_test_message("connect")

    def _update_button_style(self, button_id, value):
        """A simple function to update button styles based on the received payload."""
        button = self._button_status.get(button_id)
        if button:
            if value % 2 == 1:
                if button_id == "connect":
                    button.configure(style='Green.TButton', text='Connected')
                elif button_id == "populate":
                    button.configure(style='Orange.TButton')
            else:
                if button_id == "connect":
                    button.configure(style='Red.TButton', text='Disconnect')
                elif button_id == "populate":
                    button.configure(style='Blue.TButton')

    def _on_message(self, topic, payload):
        """The callback for when a PUBLISH message is received from the server."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function} with arguments: topic: {topic}, payload: {payload}",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function,
                  console_print_func=console_log)
        try:
            payload_data = json.loads(payload)
            value = payload_data.get("value")
            subtopic = topic.split('/')[-1]
            self.mqtt_status_var.set(f"Last MQTT Payload: {value}")
            
            button_id = subtopic.split('_')[-1]
            if button_id == "connect":
                is_connected = True if value % 2 == 1 else False
                self.is_connected.set(is_connected)
            
            self._update_button_style(button_id, value)
            console_log("✅ Received message and updated result label.")
        except json.JSONDecodeError:
            console_log("❌ Failed to decode message payload as JSON.")

    def _publish_test_message(self, button_id):
        """Publishes an incrementing test message to the MQTT broker."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function} with argument: button_id: {button_id}",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function,
                  console_print_func=console_log)
        
        self._message_counter += 1
        topic = "conductor/test"
        payload = json.dumps({"value": self._message_counter})
        
        try:
            self.mqtt_util.publish_message(topic=topic, subtopic=f"test_connection_{button_id}", value=payload)
            console_log(f"✅ Published message to '{topic}/test_connection_{button_id}': {payload}")
        except Exception as e:
            console_log(f"❌ Failed to publish message: {e}")

# Standalone block for testing purposes.
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Instrument Connection Tab Test")
    
    class MockMqttUtil:
        def __init__(self):
            self.subscribers = defaultdict(list)
            self._message_id = 0

        def add_subscriber(self, topic_filter, callback_func):
            self.subscribers[topic_filter].append(callback_func)
            print(f"Mocking add_subscriber: {topic_filter}")

        def publish_message(self, topic, subtopic, value):
            full_topic = f"{topic}/{subtopic}" if subtopic else topic
            print(f"Mocking publish_message: {full_topic} -> {value}")
            self._message_id += 1
            for topic_filter, callbacks in self.subscribers.items():
                if paho.mqtt.client.topic_matches_sub(topic_filter, full_topic):
                    for callback in callbacks:
                        callback(full_topic, value)
    
    mqtt_utility = MockMqttUtil()
    app_frame = InstrumentTab(master=root, mqtt_util=mqtt_utility)
    root.mainloop()

