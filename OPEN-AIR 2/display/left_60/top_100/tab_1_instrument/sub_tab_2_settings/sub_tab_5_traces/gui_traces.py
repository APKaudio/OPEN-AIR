# tabs/Instrument/tab_instrument_child_settings_traces.py
#
# This file defines the TraceSettingsTab, a Tkinter Frame for controlling a spectrum
# analyzer's trace settings. This refactored version removes dependencies on external
# utility and configuration files and implements a self-contained mock MQTT publisher for testing purposes.
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
# Version 20250823.130000.1

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import json
import paho.mqtt.client as mqtt
import threading
import pandas as pd
from collections import defaultdict

# --- Module Imports ---
# We are intentionally removing the following imports for this test version:
# from display.debug_logic import debug_log
# from display.console_logic import console_log
# from yak.utils_yakbeg_handler import handle_trace_modes_beg, handle_trace_data_beg
# from yak.utils_yaknab_handler import handle_all_traces_nab
# from display.utils_display_monitor import update_top_plot, update_middle_plot, update_bottom_plot, clear_monitor_plots
# from display.utils_scan_view import update_single_plot
# from settings_and_config.config_manager_instruments import _save_instrument_settings
# from settings_and_config.config_manager_save import save_program_config
from display.styling.style import THEMES, DEFAULT_THEME


# --- Global Scope Variables ---
CURRENT_DATE = datetime.datetime.now().strftime("%Y%m%d")
CURRENT_TIME = datetime.datetime.now().strftime("%H%M%S")
CURRENT_TIME_HASH = int(datetime.datetime.now().strftime("%H%M%S"))
REVISION_NUMBER = 1
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME_HASH * REVISION_NUMBER)
current_file = f"tabs/Instrument/tab_instrument_child_settings_traces.py"

# --- Mocking core dependencies for this standalone test file ---
def debug_log(message, file, version, function, console_print_func):
    """A mock debug log function for testing purposes."""
    print(f"DEBUG: {message}")

def console_log(message):
    """A mock console log function for testing purposes."""
    print(f"CONSOLE: {message}")

# Mocked preset lists for the UI
MOCK_TRACE_MODES = ["VIEW", "WRITE", "BLANK", "MAXHOLD", "MINHOLD"]

class TraceSettingsTab(ttk.Frame):
    """
    A Tkinter Frame that provides a user interface for trace settings.
    This is a refactored version for testing, implementing its own mock MQTT client.
    """
    def __init__(self, master=None, mqtt_util=None, *args, **kwargs):
        """
        Initializes the TraceSettingsTab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Initializing TraceSettingsTab. Setting up the GUI and its logic. �",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function,
                  console_print_func=console_log)
        
        super().__init__(master, **kwargs)
        self.pack(fill="both", expand=True)

        self.mqtt_util = mqtt_util
        self._message_counter = 0
        self._button_status = defaultdict(lambda: None)

        self.trace_modes = MOCK_TRACE_MODES
        self.trace_modes_result_var = tk.StringVar(value="Result: N/A")
        self.trace_data_count_var = tk.StringVar(value="0")
        self.mqtt_status_var = tk.StringVar(value="Last MQTT Payload: N/A")

        self.trace_mode_vars = {
            "trace1": tk.StringVar(value="WRITE"),
            "trace2": tk.StringVar(value="MAXHOLD"),
            "trace3": tk.StringVar(value="MINHOLD"),
            "trace4": tk.StringVar(value="BLANK")
        }

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
        style.configure('Treeview',
                        background=colors["table_bg"],
                        foreground=colors["table_fg"],
                        fieldbackground=colors["table_bg"],
                        bordercolor=colors["table_border"],
                        borderwidth=colors["border_width"])

    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Trace Settings tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering _create_widgets. Creating widgets for the Trace Settings Tab. 📈",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function,
                  console_print_func=console_log)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- TRACE/MODES Frame ---
        trace_modes_frame = ttk.LabelFrame(self, text="Trace Modes", padding=10)
        trace_modes_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        trace_modes_frame.grid_columnconfigure(0, weight=1)
        trace_modes_frame.grid_columnconfigure(1, weight=1)
        trace_modes_frame.grid_columnconfigure(2, weight=1)
        trace_modes_frame.grid_columnconfigure(3, weight=1)

        ttk.Label(trace_modes_frame, text="Trace 1 Mode:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        trace1_combo = ttk.Combobox(trace_modes_frame, textvariable=self.trace_mode_vars["trace1"], values=self.trace_modes, state="readonly")
        trace1_combo.grid(row=1, column=0, padx=5, pady=2, sticky="ew")
        self.trace_mode_vars["trace1"].trace_add('write', lambda *args: self._publish_test_message(button_id="trace1"))

        ttk.Label(trace_modes_frame, text="Trace 2 Mode:").grid(row=0, column=1, padx=5, pady=2, sticky="w")
        trace2_combo = ttk.Combobox(trace_modes_frame, textvariable=self.trace_mode_vars["trace2"], values=self.trace_modes, state="readonly")
        trace2_combo.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.trace_mode_vars["trace2"].trace_add('write', lambda *args: self._publish_test_message(button_id="trace2"))

        ttk.Label(trace_modes_frame, text="Trace 3 Mode:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        trace3_combo = ttk.Combobox(trace_modes_frame, textvariable=self.trace_mode_vars["trace3"], values=self.trace_modes, state="readonly")
        trace3_combo.grid(row=1, column=2, padx=5, pady=2, sticky="ew")
        self.trace_mode_vars["trace3"].trace_add('write', lambda *args: self._publish_test_message(button_id="trace3"))

        ttk.Label(trace_modes_frame, text="Trace 4 Mode:").grid(row=0, column=3, padx=5, pady=2, sticky="w")
        trace4_combo = ttk.Combobox(trace_modes_frame, textvariable=self.trace_mode_vars["trace4"], values=self.trace_modes, state="readonly")
        trace4_combo.grid(row=1, column=3, padx=5, pady=2, sticky="ew")
        self.trace_mode_vars["trace4"].trace_add('write', lambda *args: self._publish_test_message(button_id="trace4"))

        self.trace_modes_result_var = tk.StringVar(value="Result: N/A")
        ttk.Label(trace_modes_frame, textvariable=self.trace_modes_result_var).grid(row=2, column=0, columnspan=4, padx=5, pady=2, sticky="ew")

        # --- TRACE/DATA Frame ---
        trace_data_frame = ttk.LabelFrame(self, text="Trace Data", padding=10)
        trace_data_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        trace_data_frame.grid_columnconfigure(0, weight=1)
        
        self.trace_data_tree = ttk.Treeview(trace_data_frame, columns=("Frequency", "Value"), show="headings", height=6)
        self.trace_data_tree.heading("Frequency", text="Frequency (MHz)")
        self.trace_data_tree.heading("Value", text="Value (dBm)")
        self.trace_data_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        vsb = ttk.Scrollbar(trace_data_frame, orient="vertical", command=self.trace_data_tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.trace_data_tree.configure(yscrollcommand=vsb.set)
        
        # --- NEW: MQTT Status Label ---
        mqtt_status_frame = ttk.Frame(self)
        mqtt_status_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        mqtt_status_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(mqtt_status_frame, textvariable=self.mqtt_status_var, anchor="center").grid(row=0, column=0, sticky="ew")

        # Store a reference to the comboboxes for styling updates
        self._button_status["trace1"] = trace1_combo
        self._button_status["trace2"] = trace2_combo
        self._button_status["trace3"] = trace3_combo
        self._button_status["trace4"] = trace4_combo
        
        debug_log(message=f"Widgets for Trace Settings Tab created. The controls are ready to go! 🗺️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function,
                  console_print_func=console_log)


    def _update_button_style(self, button_id, value):
        """A simple function to update button styles based on the received payload."""
        button = self._button_status.get(button_id)
        if button:
            if value % 2 == 1:
                # For a combobox, this is a bit different. Let's just change the foreground color to simulate a status change.
                button.configure(foreground='orange')
            else:
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
            # The button_id is now in the subtopic, e.g., "test_traces_trace1"
            button_id = subtopic.split('_')[-1]
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
            self.mqtt_util.publish_message(topic=topic, subtopic=f"test_traces_{button_id}", value=payload)
            console_log(f"✅ Published message to '{topic}/test_traces_{button_id}': {payload}")
        except Exception as e:
            console_log(f"❌ Failed to publish message: {e}")

# Standalone block for testing purposes.
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Trace Settings Tab Test")
    
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
                if mqtt.topic_matches_sub(topic_filter, full_topic):
                    for callback in callbacks:
                        callback(full_topic, value)
    
    mqtt_utility = MockMqttUtil()
    app_frame = TraceSettingsTab(master=root, mqtt_util=mqtt_utility)
    root.mainloop()
