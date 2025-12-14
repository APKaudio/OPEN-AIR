# tabs/Presets/tab_presets_child_device.py
#
# A simplified GUI component for managing presets on an instrument. This file
# serves as the "view," with a single button that triggers a command in the
# PresetFromDeviceWorker.
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
# Version 20251127.000000.1

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import inspect
import os
from collections import defaultdict
from datetime import datetime

# --- Module Imports ---
from display.logger import debug_log, console_log, log_visa_command
from display.styling.style import THEMES, DEFAULT_THEME
from workers.presets.worker_preset_from_device import PresetFromDeviceWorker
from workers.mqtt.worker_mqtt_controller_util import MqttControllerUtility
import pathlib


# --- Global Scope Variables (as per your instructions) ---
current_version = "20251127.000000.1"
current_version_hash = (20251127 * 0 * 1)
current_file = f"{os.path.basename(__file__)}"

class DevicePresetsTab(ttk.Frame):
    """
    A minimal GUI component for the Presets Tab with a single button.
    """
    def __init__(self, parent, mqtt_util: MqttControllerUtility = None, *args, **kwargs):
        if 'config' in kwargs:
            kwargs.pop('config')
        super().__init__(parent, *args, **kwargs)

        self.mqtt_util = mqtt_util
        self.preset_worker = PresetFromDeviceWorker(mqtt_util=self.mqtt_util)
        
        self.collect_presets_button = None

        self.create_widgets()
        self.setup_layout()

    def create_widgets(self):
        self._apply_styles(theme_name=DEFAULT_THEME)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)

        self.collect_presets_button = ttk.Button(main_frame,
                                                 text="Collect presets",
                                                 command=self._on_collect_button_click,
                                                 style='Blue.TButton')
        self.collect_presets_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    def setup_layout(self):
        pass

    def _apply_styles(self, theme_name: str):
        """Applies a theme based on the central style definition."""
        colors = THEMES.get(theme_name)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure('TFrame', background=colors["bg"])
        style.configure('TButton', background=colors["accent"], foreground=colors["text"])
        style.map('Blue.TButton',
                  background=[('!active', colors['accent']), ('active', colors['secondary'])])

    def _on_collect_button_click(self):
        """
        Calls the worker to initiate the process of collecting presets from the device.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🖥️🟢 'Collect presets' button clicked. Initiating worker task.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        self.preset_worker.get_presets_from_device()
        console_log("✅ Preset collection task initiated.")

# Standalone block for testing purposes.
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Device Presets Tab Test")
    
    class MockMqttUtil:
        def __init__(self):
            self.subscribers = defaultdict(list)
        def add_subscriber(self, topic_filter, callback_func):
            self.subscribers[topic_filter].append(callback_func)
        def publish_message(self, topic, subtopic, value, retain=False):
            full_topic = f"{topic}/{subtopic}" if subtopic else topic
            print(f"Mock publish: {full_topic} -> {value}")
            
    mqtt_utility = MockMqttUtil()
    app_frame = DevicePresetsTab(parent=root, mqtt_util=mqtt_utility)
    root.mainloop()