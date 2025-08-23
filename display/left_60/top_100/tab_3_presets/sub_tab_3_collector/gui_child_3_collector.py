# tabs/Presets/tab_presets_child_device.py
#
# This file defines the DevicePresetsTab, a Tkinter Frame that provides
# functionality for managing instrument-defined presets. This refactored version
# is a mock for testing, using a shared MQTT utility for communication.
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
# Version 20250823.133400.1

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import inspect
import os
import json
import paho.mqtt.client as mqtt
import threading
from collections import defaultdict
from datetime import datetime

# --- Module Imports ---
# We are intentionally removing the following imports for this test version:
# from display.debug_logic import debug_log
# from display.console_logic import console_log
# from src.program_style import COLOR_PALETTE
# from Presets.utils_preset_csv_process import load_user_presets_from_csv, overwrite_user_presets_csv
# from Presets.utils_preset_query_and_load import query_device_presets_logic, load_selected_preset_logic
# from Instrument.connection.instrument_logic import query_current_settings_logic

# --- Mocking core dependencies for this standalone test file ---
from display.styling.style import THEMES, DEFAULT_THEME
from workers.mqtt_controller_util import MqttControllerUtility

from datasets.logging import console_log, debug_log
current_version = "GEMINI SUCKS"

# Mocked resources for the UI
MOCK_DEVICE_PRESETS = ["PRESET1.STA", "PRESET2.STA", "PRESET3.STA"]


class DevicePresetsTab(ttk.Frame):
    def __init__(self, parent, mqtt_util=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pack(fill="both", expand=True)
        self.mqtt_util = mqtt_util
        self._message_counter = 0

        self.last_clicked_button = None
        self.cached_user_presets = {}
        self.device_preset_listbox = None
        self.device_preset_listbox_label = None
        self.query_device_presets_button = None
        self.load_device_preset_button = None
        self.save_current_button = None
        self.filename_entry = None
        self.nickname_entry = None

        self.mqtt_status_var = tk.StringVar(self, value="Last MQTT Payload: N/A")
        
        self.create_widgets()
        self.setup_layout()

        if self.mqtt_util:
            self.mqtt_util.add_subscriber(topic_filter="conductor/test/#", callback_func=self._on_message)

    def create_widgets(self):
        self._apply_styles(theme_name=DEFAULT_THEME)

        self.device_presets_frame = ttk.LabelFrame(self, text="Device Presets", style='Dark.TLabelframe')
        self.device_presets_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.query_device_presets_button = ttk.Button(self.device_presets_frame,
                                                    text="Query Device Presets",
                                                    command=lambda: self._publish_test_message(button_id="query"),
                                                    style='Blue.TButton')
        self.query_device_presets_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.device_preset_listbox_label = ttk.Label(self.device_presets_frame, text="Available Device Presets:")
        self.device_preset_listbox_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")

        self.device_preset_listbox_frame = ttk.Frame(self.device_presets_frame, style='TFrame')
        self.device_preset_listbox_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        self.device_preset_listbox = tk.Listbox(self.device_preset_listbox_frame, height=10, width=50,
                                                selectmode=tk.SINGLE, exportselection=False)
        self.device_preset_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.device_preset_listbox.insert(tk.END, *MOCK_DEVICE_PRESETS)
        self.device_preset_listbox.bind("<<ListboxSelect>>", lambda e: self._publish_test_message(e, button_id="listbox_select"))


        self.device_preset_scrollbar = ttk.Scrollbar(self.device_preset_listbox_frame, orient="vertical", command=self.device_preset_listbox.yview)
        self.device_preset_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.device_preset_listbox.config(yscrollcommand=self.device_preset_scrollbar.set)

        self.load_device_preset_button = ttk.Button(self.device_presets_frame,
                                                    text="Load Selected Device Preset",
                                                    command=lambda: self._publish_test_message(button_id="load"),
                                                    style='Blue.TButton')
        self.load_device_preset_button.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

        self.save_current_frame = ttk.LabelFrame(self, text="Save Current Instrument Settings as User Preset", style='Dark.TLabelframe')
        self.save_current_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        self.filename_label = ttk.Label(self.save_current_frame, text="Filename (e.g., MY_PRESET.STA):")
        self.filename_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.filename_entry = ttk.Entry(self.save_current_frame, style='TEntry')
        self.filename_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        self.nickname_label = ttk.Label(self.save_current_frame, text="Nickname (optional):")
        self.nickname_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.nickname_entry = ttk.Entry(self.save_current_frame, style='TEntry')
        self.nickname_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        self.save_current_button = ttk.Button(self.save_current_frame,
                                            text="Save Current Settings to PRESETS.CSV",
                                            command=lambda: self._publish_test_message(button_id="save"),
                                            style='Blue.TButton')
        self.save_current_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # NEW: MQTT Status Label
        mqtt_status_frame = ttk.Frame(self)
        mqtt_status_frame.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        mqtt_status_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(mqtt_status_frame, textvariable=self.mqtt_status_var, anchor="center").grid(row=0, column=0, sticky="ew")

        self._button_status = defaultdict(lambda: None)
        self._button_status["query"] = self.query_device_presets_button
        self._button_status["load"] = self.load_device_preset_button
        self._button_status["save"] = self.save_current_button
        self._button_status["listbox_select"] = self.device_preset_listbox

    def setup_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.device_presets_frame.grid_columnconfigure(0, weight=1)
        self.device_preset_listbox_frame.grid_columnconfigure(0, weight=1)
        self.save_current_frame.grid_columnconfigure(1, weight=1)

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
            self.mqtt_util.publish_message(topic=topic, subtopic=f"test_presets_device_{button_id}", value=payload)
            console_log(f"✅ Published message to '{topic}/test_presets_device_{button_id}': {payload}")
        except Exception as e:
            console_log(f"❌ Failed to publish message: {e}")

# Standalone block for testing purposes.
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Device Presets Tab Test")
    
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
    app_frame = DevicePresetsTab(parent=root, mqtt_util=mqtt_utility)
    root.mainloop()

