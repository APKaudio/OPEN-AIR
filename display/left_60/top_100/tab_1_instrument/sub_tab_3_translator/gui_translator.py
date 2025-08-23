# tabs/Instrument/tab_instrument_child_visa_interpreter.py
#
# This file defines the VisaInterpreterTab as a standalone ttk.Frame.
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
from collections import defaultdict
import inspect
import datetime
import threading

# Import core utilities and style module
from datasets.logging import debug_log, console_log
from workers.mqtt_controller_util import MqttControllerUtility
from styling.style import THEMES, DEFAULT_THEME


class VisaInterpreterTab(ttk.Frame):
    """
    A standalone Tkinter Frame that provides a user interface for executing and
    managing VISA commands. All interactions are connected to MQTT.
    """
    def __init__(self, parent_frame, mqtt_util, **kwargs):
        super().__init__(parent_frame, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)

        self.mqtt_util = mqtt_util
        self.current_topic_prefix = self._get_topic_prefix()

        # Mock data for the Treeview
        self.mock_data = [
            ("Keysight", "N9912A", "QUERY", "*IDN?", "", "IDN", "True"),
            ("Keysight", "N9912A", "SET", ":SYST:PRES", "1", "Preset", "True"),
            ("Keysight", "N9912A", "DO", ":MMEM:STOR:STAT", "", "Store State", "False")
        ]
        
        self.sort_direction = {}
        self.last_selected_item = None
        
        self.manufacturer_var = tk.StringVar(self, value="N/A")
        self.model_var = tk.StringVar(self, value="N/A")
        self.serial_number_var = tk.StringVar(self, value="N/A")
        self.version_var = tk.StringVar(self, value="N/A")

        self._apply_styles(theme_name=DEFAULT_THEME)
        self._create_widgets()
        self._load_data_to_treeview()

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
        style.configure('Treeview', fieldbackground=colors["table_bg"], foreground=colors["table_fg"])
        style.configure('Treeview.Heading', background=colors["table_heading_bg"], foreground=colors["fg"])


    def _create_widgets(self):
        """Creates the UI widgets for the VisaInterpreterTab."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=0, column=0, sticky="nsew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        columns = ("Manufacturer", "Model", "Command Type", "Action", "VISA Command", "Variable", "Validated")
        self.treeview = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.treeview.pack(side="left", fill="both", expand=True)

        for col in columns:
            self.treeview.heading(col, text=col, command=lambda c=col: self._publish_value("sort_column", c))
            self.treeview.column(col, anchor="w", width=100)
            self.sort_direction[col] = 'asc'

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        control_frame = ttk.LabelFrame(self, text="Controls")
        control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        control_frame.columnconfigure(1, weight=1)

        self.status_label = ttk.Label(control_frame, text="Status: Disconnected", foreground="red")
        self.status_label.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=2)

        ttk.Label(control_frame, text="Command:", style='TLabel').grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.command_entry = ttk.Entry(control_frame)
        self.command_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.command_entry.bind('<Return>', lambda e: self._publish_value("command_entry_return", self.command_entry.get().strip()))

        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)

        self.execute_command_button = ttk.Button(button_frame, text="Execute", command=lambda: self._publish_value("execute_command", self.command_entry.get().strip()))
        self.execute_command_button.grid(row=0, column=0, sticky="ew", padx=2, pady=2)

        self.query_button = ttk.Button(button_frame, text="Query", command=lambda: self._publish_value("query_command", self.command_entry.get().strip()))
        self.query_button.grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        
        self.set_button = ttk.Button(button_frame, text="Set", command=lambda: self._publish_value("set_command", self.command_entry.get().strip()))
        self.set_button.grid(row=0, column=2, sticky="ew", padx=2, pady=2)
        
        self.do_button = ttk.Button(button_frame, text="Do", command=lambda: self._publish_value("do_command", self.command_entry.get().strip()))
        self.do_button.grid(row=0, column=3, sticky="ew", padx=2, pady=2)

        action_frame = ttk.Frame(control_frame)
        action_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        action_frame.columnconfigure(2, weight=1)
        action_frame.columnconfigure(3, weight=1)

        ttk.Button(action_frame, text="Load Data", command=lambda: self._publish_value("load_data", "clicked")).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(action_frame, text="Add New Row", command=lambda: self._publish_value("add_new_row", "clicked")).grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        ttk.Button(action_frame, text="Save Data", command=lambda: self._publish_value("save_data", "clicked")).grid(row=0, column=2, sticky="ew", padx=2, pady=2)
        ttk.Button(action_frame, text="Delete Row", command=lambda: self._publish_value("delete_row", "clicked")).grid(row=0, column=3, sticky="ew", padx=2, pady=2)
        
    def _load_data_to_treeview(self):
        """Loads data from the internal list into the Treeview widget."""
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        for row in self.mock_data:
            self.treeview.insert('', 'end', values=row)

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
    root.title("Standalone VISA Interpreter Tab Demo")
    root.geometry("1000x600")

    class MockMqttUtil:
        def add_subscriber(self, topic_filter, callback_func):
            pass
        def publish_message(self, topic, subtopic, value):
            full_topic = f"{topic}/{subtopic}" if subtopic else topic
            print(f"MOCK MQTT PUBLISH: Topic='{full_topic}', Value='{value}'")
    
    mqtt_utility = MockMqttUtil()
    app_frame = VisaInterpreterTab(parent_frame=root, mqtt_util=mqtt_utility)
    root.mainloop()
