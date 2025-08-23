# tabs/Instrument/tab_instrument_child_settings_frequency.py
#
# This file defines the FrequencySettingsTab as a standalone ttk.Frame.
# All GUI elements are directly connected to MQTT publishing, with all
# complex logic for data handling and rendering removed.
#
# Author: Anthony Peter Kuzub
#
# Version 20250824.180000.2

import tkinter as tk
from tkinter import ttk
import os
import pathlib
import json
from collections import defaultdict
import inspect
import datetime
import threading

# Import core utilities and style module
from datasets.logging import debug_log, console_log
from workers.mqtt_controller_util import MqttControllerUtility
from styling.style import THEMES, DEFAULT_THEME


class FrequencySettingsTab(ttk.Frame):
    """
    A standalone Tkinter Frame that provides a user interface for frequency settings.
    All interactions are connected to MQTT.
    """
    def __init__(self, parent_frame, mqtt_util, **kwargs):
        super().__init__(parent_frame, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)

        self.mqtt_util = mqtt_util
        self.current_topic_prefix = self._get_topic_prefix()

        # Tkinter variables for frequency settings, now in MHz
        self.freq_start_var = tk.DoubleVar(value=100.0)
        self.freq_stop_var = tk.DoubleVar(value=200.0)
        self.freq_center_var = tk.DoubleVar(value=150.0)
        self.freq_span_var = tk.DoubleVar(value=100.0)
        
        self.freq_common_result_var = tk.StringVar(value="Result: N/A")
        
        self.span_buttons = {}

        self._apply_styles(theme_name=DEFAULT_THEME)
        self._create_widgets()

    def _get_topic_prefix(self):
        """Constructs the MQTT topic prefix based on the file path."""
        # This is a key part of the new standalone design
        current_file_path = pathlib.Path(__file__).resolve()
        project_root = current_file_path.parent.parent.parent.parent
        relative_path = current_file_path.relative_to(project_root)
        topic = str(relative_path).replace(os.sep, '/')
        return os.path.splitext(topic)[0]

    def _apply_styles(self, theme_name: str):
        """Applies a theme based on the central style definition."""
        colors = THEMES.get(theme_name)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure('TFrame', background=colors["bg"])
        style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
        style.configure('TButton', background=colors["accent"], foreground=colors["text"])
        style.map('Orange.TButton', background=[('!active', 'orange'), ('active', 'orange')])
        style.map('Blue.TButton', background=[('!active', colors['accent']), ('active', colors['secondary'])])
        style.map('TButton', background=[('active', colors['secondary'])])
        style.map('Red.TButton', background=[('!active', 'red'), ('active', 'darkred')])
        style.map('Green.TButton', background=[('!active', 'green'), ('active', 'darkgreen')])
        style.configure('Dark.TLabelframe', background=colors["bg"], foreground=colors["fg"])
        style.configure('Dark.TLabel.Value', background=colors["bg"], foreground=colors["fg"])

    def _create_widgets(self):
        """Creates the UI widgets for the tab."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)

        # --- FREQUENCY/START-STOP Frame ---
        freq_ss_frame = ttk.Frame(self, padding=10)
        freq_ss_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        freq_ss_frame.grid_columnconfigure(0, weight=1)

        main_start_stop_frame = ttk.Frame(freq_ss_frame)
        main_start_stop_frame.grid(row=0, column=0, sticky="ew")
        main_start_stop_frame.grid_columnconfigure(0, weight=1)
        main_start_stop_frame.grid_columnconfigure(1, weight=1)

        start_frame = ttk.Frame(main_start_stop_frame, padding=5)
        start_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        start_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(start_frame, text="Start:").grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        start_entry = ttk.Entry(start_frame, textvariable=self.freq_start_var)
        start_entry.grid(row=1, column=0, sticky="ew")
        start_entry.bind("<Return>", lambda e: self._publish_value("start_frequency_entry", self.freq_start_var.get()))
        start_entry.bind("<FocusOut>", lambda e: self._publish_value("start_frequency_focusout", self.freq_start_var.get()))
        start_scale = ttk.Scale(start_frame, from_=100, to=1000, orient=tk.HORIZONTAL, variable=self.freq_start_var)
        start_scale.grid(row=2, column=0, sticky="ew")
        start_scale.bind("<ButtonRelease-1>", lambda e: self._publish_value("start_frequency_slider", self.freq_start_var.get()))

        stop_frame = ttk.Frame(main_start_stop_frame, padding=5)
        stop_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        stop_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(stop_frame, text="Stop:").grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        stop_entry = ttk.Entry(stop_frame, textvariable=self.freq_stop_var)
        stop_entry.grid(row=1, column=0, sticky="ew")
        stop_entry.bind("<Return>", lambda e: self._publish_value("stop_frequency_entry", self.freq_stop_var.get()))
        stop_entry.bind("<FocusOut>", lambda e: self._publish_value("stop_frequency_focusout", self.freq_stop_var.get()))
        stop_scale = ttk.Scale(stop_frame, from_=100, to=1000, orient=tk.HORIZONTAL, variable=self.freq_stop_var)
        stop_scale.grid(row=2, column=0, sticky="ew")
        stop_scale.bind("<ButtonRelease-1>", lambda e: self._publish_value("stop_frequency_slider", self.freq_stop_var.get()))

        # --- FREQUENCY/CENTER-SPAN Frame ---
        freq_cs_frame = ttk.Frame(self, padding=10)
        freq_cs_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        freq_cs_frame.grid_columnconfigure(0, weight=1)
        freq_cs_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(freq_cs_frame, text="Center Frequency:", justify=tk.RIGHT).grid(row=0, column=0, padx=5, pady=2, sticky="e")
        center_scale = ttk.Scale(freq_cs_frame, from_=100, to=1000, orient=tk.HORIZONTAL, variable=self.freq_center_var)
        center_scale.grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        center_scale.bind("<ButtonRelease-1>", lambda e: self._publish_value("center_frequency_slider", self.freq_center_var.get()))
        center_entry = ttk.Entry(freq_cs_frame, textvariable=self.freq_center_var)
        center_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        center_entry.bind("<Return>", lambda e: self._publish_value("center_frequency_entry", self.freq_center_var.get()))
        center_entry.bind("<FocusOut>", lambda e: self._publish_value("center_frequency_focusout", self.freq_center_var.get()))

        ttk.Label(freq_cs_frame, text="Span:", justify=tk.RIGHT).grid(row=2, column=0, padx=5, pady=2, sticky="e")
        span_scale = ttk.Scale(freq_cs_frame, from_=0, to=500, orient=tk.HORIZONTAL, variable=self.freq_span_var)
        span_scale.grid(row=3, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        span_scale.bind("<ButtonRelease-1>", lambda e: self._publish_value("span_frequency_slider", self.freq_span_var.get()))
        span_entry = ttk.Entry(freq_cs_frame, textvariable=self.freq_span_var)
        span_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        span_entry.bind("<Return>", lambda e: self._publish_value("span_frequency_entry", self.freq_span_var.get()))
        span_entry.bind("<FocusOut>", lambda e: self._publish_value("span_frequency_focusout", self.freq_span_var.get()))

        span_buttons_frame = ttk.Frame(freq_cs_frame, padding=5)
        span_buttons_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self._create_span_preset_buttons(parent_frame=span_buttons_frame)

        # --- COMMON RESULT FRAME ---
        common_result_frame = ttk.Frame(self, padding=10)
        common_result_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        common_result_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(common_result_frame, textvariable=self.freq_common_result_var).grid(row=0, column=0, padx=5, pady=2, sticky="ew")

    def _create_span_preset_buttons(self, parent_frame):
        """Creates mock buttons for predefined frequency spans and links them to MQTT."""
        # Mocked presets to avoid external file dependency
        mock_presets = {
            "300 kHz": {"span_mhz": 0.3, "center_mhz": 400.0},
            "1 MHz": {"span_mhz": 1.0, "center_mhz": 400.0},
            "5 MHz": {"span_mhz": 5.0, "center_mhz": 400.0},
            "20 MHz": {"span_mhz": 20.0, "center_mhz": 400.0},
        }

        for i, (label, preset) in enumerate(mock_presets.items()):
            button_text = f"{label}\n{preset['span_mhz']:.2f} MHz"
            button = ttk.Button(parent_frame,
                                text=button_text,
                                command=lambda p=preset: self._publish_value("span_preset_button", f"span:{p['span_mhz']},center:{p['center_mhz']}"))
            button.grid(row=0, column=i, sticky="ew", padx=2, pady=5)

        parent_frame.grid_rowconfigure(0, weight=1)
        for i in range(len(mock_presets)):
            parent_frame.grid_columnconfigure(i, weight=1)

    def _publish_value(self, element_name, value):
        """Publishes a value to a topic based on the file path and element name."""
        if self.mqtt_util:
            self.mqtt_util.publish_message(
                topic=self.current_topic_prefix,
                subtopic=element_name,
                value=value
            )

if __name__ == "__main__":
    # Example for standalone testing
    root = tk.Tk()
    root.title("Standalone Instrument Frequency Tab Demo")
    root.geometry("1000x600")

    class MockMqttUtil:
        def add_subscriber(self, topic_filter, callback_func):
            pass
        def publish_message(self, topic, subtopic, value):
            full_topic = f"{topic}/{subtopic}" if subtopic else topic
            print(f"MOCK MQTT PUBLISH: Topic='{full_topic}', Value='{value}'")
    
    mqtt_utility = MockMqttUtil()
    app_frame = FrequencySettingsTab(parent_frame=root, mqtt_util=mqtt_utility)
    root.mainloop()
