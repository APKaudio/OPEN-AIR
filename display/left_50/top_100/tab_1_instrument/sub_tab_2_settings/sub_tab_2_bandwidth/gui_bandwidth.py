# tabs/Instrument/tab_instrument_child_settings_bandwidth.py
#
# This file defines the BandwidthSettingsTab, a Tkinter Frame for controlling a spectrum
# analyzer's bandwidth and initiate settings. This refactored version removes dependencies
# on external utility and configuration files and implements a self-contained mock MQTT publisher
# for testing purposes.
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
# Version 20250823.130530.1

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import re
import json
import paho.mqtt.client as mqtt
import threading
from collections import defaultdict


# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from display.styling.style import THEMES, DEFAULT_THEME
from workers.mqtt_controller_util import MqttControllerUtility

# --- Module Imports ---
# We are intentionally removing the following imports for this test version:
# from display.debug_logic import debug_log
# from display.console_logic import console_log
# from yak import utils_yak_setting_handler
# from ref.ref_scanner_setting_lists import (
#     PRESET_BANDWIDTH_RBW,
#     PRESET_BANDWIDTH_VIDEO,
#     PRESET_CONTINUOUS_MODE,
#     PRESET_AVERAGING
# )
# from yak.utils_yaknab_handler import handle_bandwidth_settings_nab
# from settings_and_config.config_manager_instruments import _save_instrument_settings
# from settings_and_config.config_manager_save import save_program_config


# --- Global Scope Variables ---
CURRENT_DATE = datetime.datetime.now().strftime("%Y%m%d")
CURRENT_TIME = datetime.datetime.now().strftime("%H%M%S")
CURRENT_TIME_HASH = int(datetime.datetime.now().strftime("%H%M%S"))
REVISION_NUMBER = 1
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME_HASH * REVISION_NUMBER)
current_file = f"tabs/Instrument/tab_instrument_child_settings_bandwidth.py"

# --- Mocking core dependencies for this standalone test file ---
def debug_log(message, file, version, function, console_print_func):
    """A mock debug log function for testing purposes."""
    print(f"DEBUG: {message}")

def console_log(message):
    """A mock console log function for testing purposes."""
    print(f"CONSOLE: {message}")

# Mocked preset lists for the UI, as the original imports have been removed.
PRESET_BANDWIDTH_RBW = [
    {"label": "1M", "value": 1000000},
    {"label": "100k", "value": 100000},
    {"label": "10k", "value": 10000},
]
PRESET_BANDWIDTH_VIDEO = [
    {"label": "30k", "value": 30000},
    {"label": "10k", "value": 10000},
    {"label": "3k", "value": 3000},
]
PRESET_CONTINUOUS_MODE = [
    {"label": "ON", "value": "ON"},
    {"label": "OFF", "value": "OFF"}
]
PRESET_AVERAGING = [
    {"label": "AVG OFF", "value": 0},
    {"label": "10", "value": 10},
    {"label": "20", "value": 20}
]

class BandwidthSettingsTab(ttk.Frame):
    """
    A Tkinter Frame that provides a user interface for bandwidth and initiate settings.
    This is a refactored version for testing, implementing its own mock MQTT client.
    """
    def __init__(self, master=None, mqtt_util=None, *args, **kwargs):
        """
        Initializes the BandwidthSettingsTab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Initializing BandwidthSettingsTab. Setting up the GUI and its logic. 💻",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function,
                  console_print_func=console_log)
        
        super().__init__(master, **kwargs)
        self.pack(fill="both", expand=True)

        self.mqtt_util = mqtt_util
        self._message_counter = 0
        self._button_status = defaultdict(lambda: None)

        self.rbw_labels = [f"{p['label']} ({p['value']} Hz)" for p in PRESET_BANDWIDTH_RBW]
        self.vbw_labels = [f"{p['label']} ({p['value']} Hz)" for p in PRESET_BANDWIDTH_VIDEO]
        self.initiate_modes = [p['value'] for p in PRESET_CONTINUOUS_MODE]
        self.avg_labels = [f"{p['value']}" for p in PRESET_AVERAGING]

        self.rbw_hz_var = tk.DoubleVar(self, value=PRESET_BANDWIDTH_RBW[0]['value'])
        self.vbw_hz_var = tk.DoubleVar(self, value=PRESET_BANDWIDTH_VIDEO[0]['value'])
        self.vbw_auto_state_var = tk.BooleanVar(self, value=False)
        self.continuous_mode_var = tk.StringVar(self, value=PRESET_CONTINUOUS_MODE[0]['value'])
        self.average_on_var = tk.BooleanVar(self, value=False)
        self.average_count_var = tk.IntVar(self, value=PRESET_AVERAGING[0]['value'])
        
        self.mqtt_status_var = tk.StringVar(value="Last MQTT Payload: N/A")

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
        style.configure('Treeview',
                        background=colors["table_bg"],
                        foreground=colors["table_fg"],
                        fieldbackground=colors["table_bg"],
                        bordercolor=colors["table_border"],
                        borderwidth=colors["border_width"])

    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Bandwidth Settings tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering _create_widgets. Creating widgets for the Bandwidth Settings Tab. ⚙️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function,
                  console_print_func=console_log)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Bandwidth Settings Frame ---
        bandwidth_frame = ttk.LabelFrame(self, text="Bandwidth Settings", style='Dark.TLabelframe')
        bandwidth_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew", columnspan=2)
        bandwidth_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(bandwidth_frame, text="Resolution BW (Hz):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        self.rbw_combobox = ttk.Combobox(bandwidth_frame,
                                         textvariable=self.rbw_hz_var,
                                         values=self.rbw_labels,
                                         state='readonly')
        self.rbw_combobox.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.rbw_combobox.bind("<<ComboboxSelected>>", lambda event, id="rbw": self._publish_test_message(event, id))
        
        ttk.Label(bandwidth_frame, text="Video BW (Hz):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        
        self.vbw_combobox = ttk.Combobox(bandwidth_frame,
                                         textvariable=self.vbw_hz_var,
                                         values=self.vbw_labels,
                                         state='readonly')
        self.vbw_combobox.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.vbw_combobox.bind("<<ComboboxSelected>>", lambda event, id="vbw": self._publish_test_message(event, id))

        ttk.Label(bandwidth_frame, text="VBW Auto:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.vbw_auto_toggle_button = ttk.Button(bandwidth_frame,
                                                 text="OFF",
                                                 command=lambda: self._publish_test_message(None, "vbw_auto"),
                                                 style='Red.TButton')
        self.vbw_auto_toggle_button.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        # --- Initiate Settings Frame ---
        initiate_frame = ttk.LabelFrame(self, text="Initiate Settings", style='Dark.TLabelframe')
        initiate_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew", columnspan=2)
        initiate_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(initiate_frame, text="Continuous Mode:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.initiate_continuous_dropdown = ttk.Combobox(initiate_frame,
                                                         textvariable=self.continuous_mode_var,
                                                         values=self.initiate_modes,
                                                         state='readonly')
        self.initiate_continuous_dropdown.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.initiate_continuous_dropdown.bind("<<ComboboxSelected>>", lambda event, id="continuous": self._publish_test_message(event, id))
        
        self.initiate_immediate_button = ttk.Button(initiate_frame,
                                                     text="Initiate Immediate",
                                                     command=lambda: self._publish_test_message(None, "immediate"),
                                                     style='Blue.TButton')
        self.initiate_immediate_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # --- Averaging Frame (Updated layout for Trace 1 only) ---
        averaging_frame = ttk.LabelFrame(self, text="Averaging", style='Dark.TLabelframe')
        averaging_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew", columnspan=2)
        averaging_frame.grid_columnconfigure((1, 3), weight=1)

        ttk.Label(averaging_frame, text="Trace 1 Averaging:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.average_on_button = ttk.Button(averaging_frame, text="OFF", command=lambda: self._publish_test_message(None, "avg_toggle"), style='Red.TButton')
        self.average_on_button.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(averaging_frame, text="Count:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.average_count_dropdown = ttk.Combobox(averaging_frame, textvariable=self.average_count_var, values=self.avg_labels, state='readonly')
        self.average_count_dropdown.grid(row=0, column=3, padx=5, pady=2, sticky="ew")
        self.average_count_dropdown.bind("<<ComboboxSelected>>", lambda event, id="avg_count": self._publish_test_message(event, id))

        # --- NEW: MQTT Status Label ---
        mqtt_status_frame = ttk.Frame(self)
        mqtt_status_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew", columnspan=2)
        mqtt_status_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(mqtt_status_frame, textvariable=self.mqtt_status_var, anchor="center").grid(row=0, column=0, sticky="ew")

        # Store a reference to the comboboxes and buttons for styling updates
        self._button_status["rbw"] = self.rbw_combobox
        self._button_status["vbw"] = self.vbw_combobox
        self._button_status["vbw_auto"] = self.vbw_auto_toggle_button
        self._button_status["continuous"] = self.initiate_continuous_dropdown
        self._button_status["immediate"] = self.initiate_immediate_button
        self._button_status["avg_toggle"] = self.average_on_button
        self._button_status["avg_count"] = self.average_count_dropdown
        
        debug_log(message=f"Widgets for Bandwidth Settings Tab created. Bandwidth controls are ready! 🛠️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function,
                  console_print_func=console_log)


    def _update_button_style(self, button_id, value):
        """A simple function to update button styles based on the received payload."""
        button = self._button_status.get(button_id)
        if button:
            if value % 2 == 1:
                if isinstance(button, ttk.Button):
                    button.configure(style='Orange.TButton')
                else: # Combobox
                    button.configure(foreground='orange')
            else:
                if isinstance(button, ttk.Button):
                    button.configure(style='Blue.TButton')
                else: # Combobox
                    button.configure(foreground='white')

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
            self._update_button_style(button_id, value)
            console_log("✅ Received message and updated result label.")
        except json.JSONDecodeError:
            console_log("❌ Failed to decode message payload as JSON.")

    def _publish_test_message(self, event=None, button_id=""):
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
            self.mqtt_util.publish_message(topic=topic, subtopic=f"test_bandwidth_{button_id}", value=payload)
            console_log(f"✅ Published message to '{topic}/test_bandwidth_{button_id}': {payload}")
        except Exception as e:
            console_log(f"❌ Failed to publish message: {e}")

# Standalone block for testing purposes.
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Bandwidth Settings Tab Test")
    
    import paho.mqtt.client as paho

    class MockMqttUtil:
        def __init__(self):
            self.subscribers = defaultdict(list)
            self._message_id = 0
            self.lock = threading.Lock()

        def add_subscriber(self, topic_filter, callback_func):
            with self.lock:
                self.subscribers[topic_filter].append(callback_func)
                print(f"Mocking add_subscriber: {topic_filter}")

        def publish_message(self, topic, subtopic, value):
            with self.lock:
                full_topic = f"{topic}/{subtopic}" if subtopic else topic
                print(f"Mocking publish_message: {full_topic} -> {value}")
                self._message_id += 1
                for topic_filter, callbacks in self.subscribers.items():
                    if paho.mqtt.client.topic_matches_sub(topic_filter, full_topic):
                        for callback in callbacks:
                            callback(full_topic, value)
    
    mqtt_utility = MockMqttUtil()
    app_frame = BandwidthSettingsTab(master=root, mqtt_util=mqtt_utility)
    root.mainloop()
