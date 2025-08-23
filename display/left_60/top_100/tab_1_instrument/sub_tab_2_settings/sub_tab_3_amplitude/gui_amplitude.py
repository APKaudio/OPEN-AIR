# tabs/Instrument/tab_instrument_child_settings_amplitude.py
#
# This file defines the AmplitudeSettingsTab, a Tkinter Frame for controlling a spectrum
# analyzer's amplitude-related settings. This version is now fully integrated into the
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
# Version 20250823.131230.1

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
# These are the dependencies needed for a stand-in test environment, simulating the original behavior.
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
current_file = f"tabs/Instrument/tab_instrument_child_settings_amplitude.py"

# Mocked preset lists for the UI, as the original imports have been removed.
PRESET_AMPLITUDE_REFERENCE_LEVEL = [
    {"label": "-10", "value": -10.0, "description": "High signal level, good for strong signals."},
    {"label": "0", "value": 0.0, "description": "General purpose level, standard for most signals."},
    {"label": "10", "value": 10.0, "description": "Higher signal level, for stronger signals."},
]
PRESET_AMPLITUDE_POWER_ATTENUATION = [
    {"label": "0", "value": 0.0, "description": "No attenuation, for very weak signals."},
    {"label": "10", "value": 10.0, "description": "Standard 10 dB attenuation."},
    {"label": "20", "value": 20.0, "description": "Higher 20 dB attenuation, for strong signals."},
]
PRESET_AMPLITUDE_PREAMP_STATE = [
    {"label": "PREAMP ON", "value": "ON"},
    {"label": "PREAMP OFF", "value": "OFF"}
]
PRESET_AMPLITUDE_HIGH_SENSITIVITY_STATE = [
    {"label": "HIGH SENSITIVITY ON", "value": "ON"},
    {"label": "HIGH SENSITIVITY OFF", "value": "OFF"}
]


class AmplitudeSettingsTab(ttk.Frame):
    """
    A Tkinter Frame that provides a user interface for amplitude settings.
    This version correctly uses a parent-provided MQTT utility class.
    """
    def __init__(self, master=None, mqtt_util=None, *args, **kwargs):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Initializing AmplitudeSettingsTab. Setting up the GUI and its logic. 💻",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function,
                  console_print_func=console_log)

        super().__init__(master, *args, **kwargs)
        self.pack(fill="both", expand=True)

        self.mqtt_util = mqtt_util
        self._message_counter = 0
        self._button_status = defaultdict(lambda: None)
        
        self.is_ref_level_tracing = False
        self.is_attenuation_tracing = False
        
        # Mock Tkinter variables for the UI
        self.preamp_state_var = tk.BooleanVar(self, value=False)
        self.high_sensitivity_state_var = tk.BooleanVar(self, value=False)
        self.ref_level_dbm_var = tk.DoubleVar(self, value=PRESET_AMPLITUDE_REFERENCE_LEVEL[1]['value'])
        self.power_attenuation_db_var = tk.DoubleVar(self, value=PRESET_AMPLITUDE_POWER_ATTENUATION[1]['value'])
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
        style.configure('Description.TLabel', background=colors["bg"], foreground=colors["fg"], font=("Helvetica", 8, "italic"))
        style.configure('InteractionBars.TScale', troughcolor=colors["secondary"], background=colors["accent"])

    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Amplitude Settings tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function}. The mad scientist is preparing the amplitude controls! 🔊🧪",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function,
                  console_print_func=console_log)

        self.grid_columnconfigure(0, weight=1)
        
        # --- Top Buttons for Preamp and High Sensitivity ---
        top_buttons_frame = ttk.Frame(self)
        top_buttons_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        top_buttons_frame.grid_columnconfigure(0, weight=1)
        top_buttons_frame.grid_columnconfigure(1, weight=1)
        
        self.preamp_toggle_button = ttk.Button(top_buttons_frame,
                                               text="PREAMP OFF",
                                               command=lambda: self._on_toggle_button_press(button_id="preamp"),
                                               style='Red.TButton')
        self.preamp_toggle_button.grid(row=0, column=0, padx=5, pady=2, sticky="ew")
        self._button_status["preamp"] = self.preamp_toggle_button

        self.hs_toggle_button = ttk.Button(top_buttons_frame,
                                           text="HIGH SENSITIVITY OFF",
                                           command=lambda: self._on_toggle_button_press(button_id="high_sensitivity"),
                                           style='Red.TButton')
        self.hs_toggle_button.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self._button_status["high_sensitivity"] = self.hs_toggle_button
        
        # --- Reference Level Controls (New layout) ---
        ref_level_frame = ttk.Frame(self)
        ref_level_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ref_level_frame.grid_columnconfigure(0, weight=1)

        ref_level_title_frame = ttk.Frame(ref_level_frame)
        ref_level_title_frame.grid(row=0, column=0, sticky="ew")
        ref_level_title_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(ref_level_title_frame, text="Reference Level (dBm):").grid(row=0, column=0, padx=5, sticky="w")
        self.ref_level_value_label = ttk.Label(ref_level_title_frame, textvariable=self.ref_level_dbm_var)
        self.ref_level_value_label.grid(row=0, column=1, padx=5, sticky="e")

        ref_values = [p["value"] for p in PRESET_AMPLITUDE_REFERENCE_LEVEL]
        ref_min = min(ref_values)
        ref_max = max(ref_values)
        self.ref_level_slider = ttk.Scale(ref_level_frame,
                                          orient="horizontal",
                                          variable=self.ref_level_dbm_var,
                                          from_=ref_min,
                                          to=ref_max,
                                          command=lambda v: self._update_descriptions(value=float(v), preset_list=PRESET_AMPLITUDE_REFERENCE_LEVEL, label=self.ref_level_description_label, var=self.ref_level_dbm_var))
        self.ref_level_slider.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.ref_level_slider.bind("<ButtonRelease-1>", lambda e: self._publish_test_message(button_id="ref_level_slider"))
        self._button_status["ref_level_slider"] = self.ref_level_slider
        
        self.ref_level_description_label = ttk.Label(ref_level_frame, text="", style='Description.TLabel', anchor="center")
        self.ref_level_description_label.grid(row=2, column=0, padx=5, pady=2, sticky="ew")
        
        # --- Spacer ---
        ttk.Frame(self, height=10).grid(row=2, column=0)

        # --- Power Attenuation Controls (New layout) ---
        power_att_frame = ttk.Frame(self)
        power_att_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        power_att_frame.grid_columnconfigure(0, weight=1)

        power_att_title_frame = ttk.Frame(power_att_frame)
        power_att_title_frame.grid(row=0, column=0, sticky="ew")
        power_att_title_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(power_att_title_frame, text="Power Attenuation (dB):").grid(row=0, column=0, padx=5, sticky="w")
        self.power_attenuation_value_label = ttk.Label(power_att_title_frame, textvariable=self.power_attenuation_db_var)
        self.power_attenuation_value_label.grid(row=0, column=1, padx=5, sticky="e")

        att_values = [p["value"] for p in PRESET_AMPLITUDE_POWER_ATTENUATION]
        att_min = min(att_values)
        att_max = max(att_values)
        self.power_attenuation_slider = ttk.Scale(power_att_frame,
                                                  orient="horizontal",
                                                  variable=self.power_attenuation_db_var,
                                                  from_=att_min,
                                                  to=att_max,
                                                  command=lambda v: self._update_descriptions(value=float(v), preset_list=PRESET_AMPLITUDE_POWER_ATTENUATION, label=self.power_attenuation_description_label, var=self.power_attenuation_db_var))
        self.power_attenuation_slider.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.power_attenuation_slider.bind("<ButtonRelease-1>", lambda e: self._publish_test_message(button_id="power_attenuation_slider"))
        self._button_status["power_attenuation_slider"] = self.power_attenuation_slider

        self.power_attenuation_description_label = ttk.Label(power_att_frame, text="", style='Description.TLabel', anchor="center")
        self.power_attenuation_description_label.grid(row=2, column=0, padx=5, pady=2, sticky="ew")
        
        # --- NEW: MQTT Status Label ---
        mqtt_status_frame = ttk.Frame(self)
        mqtt_status_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        mqtt_status_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(mqtt_status_frame, textvariable=self.mqtt_status_var, anchor="center").grid(row=0, column=0, sticky="ew")

        self._update_descriptions(value=self.ref_level_dbm_var.get(), preset_list=PRESET_AMPLITUDE_REFERENCE_LEVEL, label=self.ref_level_description_label, var=self.ref_level_dbm_var)
        self._update_descriptions(value=self.power_attenuation_db_var.get(), preset_list=PRESET_AMPLITUDE_POWER_ATTENUATION, label=self.power_attenuation_description_label, var=self.power_attenuation_db_var)

        debug_log(message=f"Widgets for Amplitude Settings Tab created. The amplitude controls are ready! 📉�",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function,
                  console_print_func=console_log)


    def _on_toggle_button_press(self, button_id):
        """Toggles the state of a button and publishes a test message."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function}. Button ID: {button_id}",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function,
                  console_print_func=console_log)
        
        if button_id == "preamp":
            current_state = self.preamp_state_var.get()
            self.preamp_state_var.set(not current_state)
            self._update_toggle_button_style(button=self._button_status["preamp"], state=not current_state)
        elif button_id == "high_sensitivity":
            current_state = self.high_sensitivity_state_var.get()
            self.high_sensitivity_state_var.set(not current_state)
            self._update_toggle_button_style(button=self._button_status["high_sensitivity"], state=not current_state)

        self._publish_test_message(button_id)
        
    def _find_closest_preset_value(self, value, preset_list):
        """Finds the closest discrete preset value for a given float value."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function}. Finding closest preset for value: {value}",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function,
                  console_print_func=console_log)

        values = [p["value"] for p in preset_list]
        return min(values, key=lambda x: abs(x - value))

    def _update_descriptions(self, value, preset_list, label, var):
        """
        Updates a description label and the variable value based on the slider value
        by finding the closest preset and snapping to it.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function}. Seeking the closest preset for a value of {value}...",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function,
                  console_print_func=console_log)
        
        closest_value = self._find_closest_preset_value(value, preset_list)
        
        closest_preset = next((preset for preset in preset_list if np.isclose(preset["value"], closest_value)), None)

        if closest_preset:
            var.set(closest_preset["value"])
            label.config(text=closest_preset["description"])
            debug_log(message=f"Found a description! ' {closest_preset['description']} '",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function,
                      console_print_func=console_log)
        else:
            label.config(text="No matching description found.")
            debug_log(message=f"Arrr, no description to be found! Shiver me timbers! 🏴‍☠️",
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
                else:
                    # Not a button, so we update the variable
                    pass
            else:
                if isinstance(button, ttk.Button):
                    button.configure(style='Blue.TButton')
                else:
                    # Not a button, so we update the variable
                    pass

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
            
            if button_id == "preamp":
                 if value % 2 == 1: # ON state
                     self._update_toggle_button_style(self._button_status["preamp"], state=True)
                 else: # OFF state
                     self._update_toggle_button_style(self._button_status["preamp"], state=False)
            elif button_id == "high_sensitivity":
                 if value % 2 == 1: # ON state
                     self._update_toggle_button_style(self._button_status["high_sensitivity"], state=True)
                 else: # OFF state
                     self._update_toggle_button_style(self._button_status["high_sensitivity"], state=False)
            else:
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
            self.mqtt_util.publish_message(topic=topic, subtopic=f"test_amplitude_{button_id}", value=payload)
            console_log(f"✅ Published message to '{topic}/test_amplitude_{button_id}': {payload}")
        except Exception as e:
            console_log(f"❌ Failed to publish message: {e}")

    def _update_toggle_button_style(self, button, state):
        """Updates the style and text of a toggle button based on its state."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"Entering {current_function}. Updating button style for state: {state} 🤔",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function,
                  console_print_func=console_log)
        
        # Determine the correct preset list to use based on the button instance
        preset_list = None
        if button == self._button_status.get("preamp"):
            preset_list = PRESET_AMPLITUDE_PREAMP_STATE
            if state:
                button.config(style='Green.TButton', text=next((p['label'] for p in preset_list if p['value'] == 'ON'), "ON"))
            else:
                button.config(style='Red.TButton', text=next((p['label'] for p in preset_list if p['value'] == 'OFF'), "OFF"))
        elif button == self._button_status.get("high_sensitivity"):
            preset_list = PRESET_AMPLITUDE_HIGH_SENSITIVITY_STATE
            if state:
                button.config(style='Green.TButton', text=next((p['label'] for p in preset_list if p['value'] == 'ON'), "ON"))
            else:
                button.config(style='Red.TButton', text=next((p['label'] for p in preset_list if p['value'] == 'OFF'), "OFF"))

