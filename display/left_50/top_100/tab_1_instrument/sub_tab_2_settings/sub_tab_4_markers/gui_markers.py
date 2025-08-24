# tabs/Instrument/tab_instrument_child_settings_markers.py
#
# This file defines the MarkerSettingsTab, a Tkinter Frame for controlling a spectrum
# analyzer's marker settings. This refactored version is now fully integrated into the
# main application, using a shared MQTT utility for communication.
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
# Version 20250823.131500.1

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import json
import paho.mqtt.client as mqtt
import threading
import numpy as np
from collections import defaultdict

# --- Module Imports ---
# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from display.styling.style import THEMES, DEFAULT_THEME
from workers.mqtt_controller_util import MqttControllerUtility

# --- Global Scope Variables ---
CURRENT_DATE = datetime.datetime.now().strftime("%Y%m%d")
CURRENT_TIME = datetime.datetime.now().strftime("%H%M%S")
CURRENT_TIME_HASH = int(datetime.datetime.now().strftime("%H%M%S"))
REVISION_NUMBER = 1
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME_HASH * REVISION_NUMBER)
current_file = f"tabs/Instrument/tab_instrument_child_settings_markers.py"


class MarkerSettingsTab(ttk.Frame):
    """
    A Tkinter Frame that provides a user interface for marker settings.
    This version correctly uses a parent-provided MQTT utility class.
    """
    def __init__(self, master=None, mqtt_util=None, *args, **kwargs):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Initializing MarkerSettingsTab. This should be a walk in the park! 🚶‍♀️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function,
                  console_print_func=console_log)

        super().__init__(master, *args, **kwargs)
        self.pack(fill="both", expand=True)

        self.mqtt_util = mqtt_util
        self._message_counter = 0
        self.marker_freq_vars = [tk.DoubleVar(self, value=f) for f in [111.0, 222.0, 333.0, 444.0, 555.0, 666.0]]
        self.marker_result_table = None
        self.marker_place_all_button = None
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
        style.configure('Description.TLabel', background=colors["bg"], foreground=colors["fg"], font=("Helvetica", 8, "italic"))
        style.configure('InteractionBars.TScale', troughcolor=colors["secondary"], background=colors["accent"])

    def _create_widgets(self):
        """Creates the GUI widgets for the tab."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Creating widgets for MarkerSettingsTab. The puzzle pieces are coming together! 🧩",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function,
                  console_print_func=console_log)
        
        main_container = ttk.Frame(self, padding="10")
        main_container.pack(fill="both", expand=True)
        main_container.grid_columnconfigure(0, weight=1)
        
        marker_input_frame = ttk.Frame(main_container)
        marker_input_frame.grid(row=0, column=0, pady=(0, 5), sticky="ew")
        for i in range(6):
            marker_input_frame.grid_columnconfigure(i, weight=1)
            ttk.Label(marker_input_frame, text=f"M{i+1} Freq (MHz):").grid(row=0, column=i, padx=2, pady=2)
            ttk.Entry(marker_input_frame, textvariable=self.marker_freq_vars[i], width=8).grid(row=1, column=i, padx=2, pady=2)

        self.marker_place_all_button = ttk.Button(main_container, 
                                                 text="YakBeg - MARKER/PLACE/ALL",
                                                 command=lambda: self._publish_test_message(button_id="place_all"),
                                                 style='Blue.TButton')
        self.marker_place_all_button.grid(row=1, column=0, pady=5, sticky="ew")

        results_frame = ttk.Frame(main_container)
        results_frame.grid(row=2, column=0, pady=(5, 0), sticky="nsew")
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)
        
        self.marker_result_table = ttk.Treeview(results_frame, columns=('Marker', 'Frequency', 'Amplitude'), show='headings', height=6)
        self.marker_result_table.heading('Marker', text='Marker')
        self.marker_result_table.heading('Frequency', text='Frequency (MHz)')
        self.marker_result_table.heading('Amplitude', text='Amplitude (dBm)')
        
        self.marker_result_table.column('Marker', width=80, stretch=tk.YES, anchor='center')
        self.marker_result_table.column('Frequency', width=120, stretch=tk.YES, anchor='center')
        self.marker_result_table.column('Amplitude', width=120, stretch=tk.YES, anchor='center')
        
        self.marker_result_table.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.marker_result_table.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.marker_result_table.configure(yscrollcommand=vsb.set)
        
        # NEW: MQTT Status Label
        mqtt_status_frame = ttk.Frame(main_container)
        mqtt_status_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        mqtt_status_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(mqtt_status_frame, textvariable=self.mqtt_status_var, anchor="center").grid(row=0, column=0, sticky="ew")

    def _update_button_style(self, button_id, value):
        """A simple function to update button styles based on the received payload."""
        if button_id == "place_all":
            if value % 2 == 1:
                self.marker_place_all_button.config(style='Orange.TButton')
            else:
                self.marker_place_all_button.config(style='Blue.TButton')

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
            self._update_button_style(subtopic.split('_')[-1], value)
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
            self.mqtt_util.publish_message(topic=topic, subtopic=f"test_markers_{button_id}", value=payload)
            console_log(f"✅ Published message to '{topic}/test_markers_{button_id}': {payload}")
        except Exception as e:
            console_log(f"❌ Failed to publish message: {e}")
