# tabs/Markers/showtime/zones_groups_devices/tab_markers_child_zone_groups_devices.py
#
# This file defines the ZoneGroupsDevicesFrame as a standalone ttk.Frame.
# All GUI elements are directly connected to MQTT publishing, with all
# complex logic for data handling and rendering removed.
#
# Author: Anthony Peter Kuzub
#
# Version 20250824.180000.1

import tkinter as tk
from tkinter import ttk
import os
import pathlib
import json
import inspect
import threading
from datetime import datetime
from collections import defaultdict

# Import core utilities and style module
from datasets.logging import debug_log, console_log
from workers.mqtt_controller_util import MqttControllerUtility
from styling.style import THEMES, DEFAULT_THEME


class ZoneGroupsDevicesFrame(ttk.Frame):
    """
    A standalone Tkinter Frame that provides a user interface for selecting
    zones, groups, and devices, with all interactions connected to MQTT.
    """
    def __init__(self, parent_frame, mqtt_util, **kwargs):
        super().__init__(parent_frame, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)

        self.mqtt_util = mqtt_util
        self.current_topic_prefix = self._get_topic_prefix()

        self.structured_data = {
            'Zone A': {
                'Group 1': [{'NAME': 'Device 1', 'DEVICE': 'Type A', 'CENTER': '100.0', 'PEAK': -50.0}, {'NAME': 'Device 2', 'DEVICE': 'Type A', 'CENTER': '101.0', 'PEAK': -60.0}],
                'Group 2': [{'NAME': 'Device 3', 'DEVICE': 'Type B', 'CENTER': '150.0', 'PEAK': -45.0}]
            },
            'Zone B': {
                'Group 3': [{'NAME': 'Device 4', 'DEVICE': 'Type C', 'CENTER': '200.0', 'PEAK': -70.0}]
            }
        }
        self.active_zone_button = None
        self.active_group_button = None

        self._apply_styles(theme_name=DEFAULT_THEME)
        self._create_widgets()

    def _get_topic_prefix(self):
        """Constructs the MQTT topic prefix based on the file path."""
        relative_path = pathlib.Path(__file__).resolve().relative_to(pathlib.Path(__file__).resolve().parent.parent.parent.parent)
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
        """Creates the main layout with zones, groups, and the scrollable device frame."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        
        self.zones_frame = ttk.LabelFrame(self, text="Zones")
        self.zones_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self._make_zone_buttons()
        
        self.groups_frame = ttk.LabelFrame(self, text="Groups")
        self.groups_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self._make_group_buttons('Zone A')
        
        self.devices_outer_frame = ttk.LabelFrame(self, text="Devices")
        self.devices_outer_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.devices_outer_frame.grid_rowconfigure(0, weight=1)
        self.devices_outer_frame.grid_columnconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(self.devices_outer_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.devices_outer_frame, orient="vertical", command=self.canvas.yview)
        self.devices_scrollable_frame = ttk.Frame(self.canvas)
        self.devices_scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.devices_scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self._make_device_buttons('Zone A', 'Group 1')

    def _make_zone_buttons(self):
        """Creates the zone selection buttons in a grid."""
        for widget in self.zones_frame.winfo_children():
            widget.destroy()

        max_columns = 6
        for i, zone_name in enumerate(self.structured_data.keys()):
            row, col = divmod(i, max_columns)
            btn = ttk.Button(self.zones_frame, text=zone_name,
                             command=lambda z=zone_name: self._publish_value("zone_selected", z))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            self.zones_frame.columnconfigure(col, weight=1)

    def _make_group_buttons(self, zone_name):
        """Creates group buttons, dynamically showing/hiding the frame."""
        for widget in self.groups_frame.winfo_children():
            widget.destroy()

        groups = self.structured_data.get(zone_name, {})
        max_columns = 6
        for i, group_name in enumerate(groups.keys()):
            row, col = divmod(i, max_columns)
            btn = ttk.Button(self.groups_frame, text=group_name,
                             command=lambda g=group_name: self._publish_value("group_selected", g))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            self.groups_frame.columnconfigure(col, weight=1)

    def _make_device_buttons(self, zone_name, group_name):
        """Creates the detailed, multi-line device buttons in the scrollable frame."""
        for widget in self.devices_scrollable_frame.winfo_children():
            widget.destroy()
        
        devices_to_display = self.structured_data.get(zone_name, {}).get(group_name, [])
        self.devices_outer_frame.config(text=f"Devices ({len(devices_to_display)})")

        max_cols = 4
        for col in range(max_cols):
            self.devices_scrollable_frame.grid_columnconfigure(col, weight=1)
            
        for i, device in enumerate(devices_to_display):
            name = device.get('NAME', 'N/A')
            device_type = device.get('DEVICE', 'N/A')
            center = device.get('CENTER', 'N/A')
            peak = device.get('PEAK', -120.0)
            
            btn_text = f"{name}\n{device_type}\n{center} MHz\n{peak} dBm"
            
            btn = ttk.Button(self.devices_scrollable_frame, text=btn_text,
                             command=lambda d=device: self._publish_value("device_selected", d.get('NAME', 'N/A')))
            
            row, col = divmod(i, max_cols)
            btn.grid(row=row, column=col, padx=5, pady=2, sticky="ew")

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
    root.title("Standalone GUI Demo")
    root.geometry("800x600")

    class MockMqttUtil:
        def __init__(self):
            self.subscribers = defaultdict(list)
            self._message_id = 0
            self.lock = threading.Lock()

        def add_subscriber(self, topic_filter, callback_func):
            pass

        def publish_message(self, topic, subtopic, value):
            full_topic = f"{topic}/{subtopic}" if subtopic else topic
            print(f"MOCK MQTT PUBLISH: Topic='{full_topic}', Value='{value}'")
    
    mqtt_utility = MockMqttUtil()
    app_frame = ZoneGroupsDevicesFrame(parent_frame=root, mqtt_util=mqtt_utility)
    root.mainloop()
