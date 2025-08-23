# display/base_gui_component.py
#
# A base class for common GUI components, re-written to work with the centralized orchestrator.
# This version corrects the styling of tables and entry widgets for a more cohesive look.
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
# Version 20250823.001500.20

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import pathlib
import sys
import json
import paho.mqtt.client as mqtt

# --- Module Imports ---
from datasets.logging import debug_log, console_log
from workers.mqtt_controller_util import MqttControllerUtility
from display.styling.style import THEMES, DEFAULT_THEME

# --- Global Scope Variables ---
CURRENT_DATE = 20250823
CURRENT_TIME = 1500
CURRENT_TIME_HASH = 1500
REVISION_NUMBER = 20
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME_HASH * REVISION_NUMBER)
# Dynamically get the file path relative to the project root
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")


class TranslatorGUI(ttk.Frame):
    """
    A GUI component for interacting with the instrument translator via MQTT.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        current_function_name = inspect.currentframe().f_code.co_name

        debug_log(
            message="🖥️🟢 Initializing the Translator GUI.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            super().__init__(parent, *args, **kwargs)
            self.pack(fill=tk.BOTH, expand=True)

            self.current_file = current_file
            self.current_version = current_version
            self.current_version_hash = current_version_hash
            self.mqtt_util = mqtt_util

            self._apply_styles(theme_name=DEFAULT_THEME)

            # --- New MQTT Buttons Section ---
            mqtt_frame = ttk.LabelFrame(self, text="MQTT Translator Controls")
            mqtt_frame.pack(fill=tk.X, padx=10, pady=10)

            # Button 1: Get Configuration
            self.get_config_button = ttk.Button(
                mqtt_frame,
                text="Get Configuration",
                command=lambda: self._publish_translator_message("GET_CONFIG", "request")
            )
            self.get_config_button.pack(side=tk.LEFT, padx=5, pady=5)

            # Button 2: Test Configuration
            self.test_config_button = ttk.Button(
                mqtt_frame,
                text="Test Configuration",
                command=lambda: self._publish_translator_message("TEST_CONFIG", "request")
            )
            self.test_config_button.pack(side=tk.LEFT, padx=5, pady=5)

            # Button 3: Subscribe to Commands
            self.subscribe_button = ttk.Button(
                mqtt_frame,
                text="Subscribe to Commands",
                command=lambda: self._publish_translator_message("SUBSCRIBE", "request")
            )
            self.subscribe_button.pack(side=tk.LEFT, padx=5, pady=5)
            
            # Button 4: Future functionality
            self.future_button = ttk.Button(
                mqtt_frame,
                text="Future",
                command=lambda: self._publish_translator_message("FUTURE", "request")
            )
            self.future_button.pack(side=tk.LEFT, padx=5, pady=5)


            # --- New MQTT Message Log Table ---
            self.subscriptions_table_frame = ttk.Frame(self)
            self.subscriptions_table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            # Treeview table for commands
            self.commands_table = ttk.Treeview(self.subscriptions_table_frame, columns=("Parameter", "Function", "Description"), show="headings", style="Custom.Treeview")
            self.commands_table.heading("Parameter", text="Parameter")
            self.commands_table.heading("Function", text="Function")
            self.commands_table.heading("Description", text="Description")
            self.commands_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            table_scrollbar = ttk.Scrollbar(self.subscriptions_table_frame, orient=tk.VERTICAL, command=self.commands_table.yview)
            self.commands_table.configure(yscrollcommand=table_scrollbar.set)
            table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # We now register our callback with the central utility.
            self.mqtt_util.add_subscriber(topic_filter="datasets/dataset_visa_commands/COMMANDS/list_item", callback_func=self._on_commands_message)


            # --- New Status Bar at the bottom ---
            status_bar = ttk.Frame(self, relief=tk.SUNKEN, borderwidth=1)
            status_bar.pack(side=tk.BOTTOM, fill=tk.X, expand=False)

            file_parts = self.current_file.rsplit('/', 1)
            file_folder = file_parts[0] if len(file_parts) > 1 else ""
            file_name = file_parts[-1]

            status_text = f"Version: {self.current_version} | Folder: {file_folder} | File: {file_name}"
            status_label = ttk.Label(status_bar, text=status_text, anchor='w')
            status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            console_log("✅ Translator GUI initialized successfully!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _apply_styles(self, theme_name: str):
        """
        Applies the specified theme to the GUI elements using ttk.Style.
        """
        colors = THEMES.get(theme_name, THEMES["dark"])
        style = ttk.Style(self)
        style.theme_use("clam")

        # General widget styling
        style.configure('TFrame', background=colors["bg"])
        style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
        style.configure('TLabelframe', background=colors["bg"], foreground=colors["fg"])

        # Table (Treeview) styling
        style.configure('Custom.Treeview',
                        background=colors["table_bg"],
                        foreground=colors["table_fg"],
                        fieldbackground=colors["table_bg"],
                        bordercolor=colors["table_border"],
                        borderwidth=colors["border_width"])

        style.configure('Custom.Treeview.Heading',
                        background=colors["table_heading_bg"],
                        foreground=colors["fg"],
                        relief=colors["relief"],
                        borderwidth=colors["border_width"])

        # Entry (textbox) styling
        style.configure('Custom.TEntry',
                        fieldbackground=colors["entry_bg"],
                        foreground=colors["entry_fg"],
                        bordercolor=colors["table_border"])

    def _publish_translator_message(self, child_topic: str, message: str):
        """
        Publishes a message to the instrument translator topic with a specific child topic.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        parent_topic = "Root: Instrument"
        
        debug_log(
            message=f"🖥️🟢 Publishing '{message}' to MQTT topic '{parent_topic}/{child_topic}'.",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            self.mqtt_util.publish_message(topic=parent_topic, subtopic=f"TRANSLATOR/{child_topic}", value=message)
            console_log(f"✅ Command '{message}' published successfully to '{parent_topic}/TRANSLATOR/{child_topic}'!")
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _on_commands_message(self, topic, payload):
        """
        Callback for when an MQTT message is received on the commands topic.
        Populates the Treeview table with the received list of commands.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🖥️🔵 Received MQTT message on topic '{topic}'.",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            # Clear existing data
            self.commands_table.delete(*self.commands_table.get_children())
            
            commands_list = json.loads(payload)["value"]
            if isinstance(commands_list, list):
                for item in commands_list:
                    if isinstance(item, dict) and 'parameter' in item and 'function' in item and 'description' in item:
                        self.commands_table.insert('', 'end', values=(item['parameter'], item['function'], item['description']))
            
            console_log("✅ Commands table updated with new data!")
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Translator GUI Test")

    mqtt_utility = MqttControllerUtility(print_to_gui_func=console_log, log_treeview_func=lambda *args: None)
    mqtt_utility.connect_mqtt()

    app_frame = TranslatorGUI(parent=root, mqtt_util=mqtt_utility)

    root.mainloop()