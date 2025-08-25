# display/gui_translator.py
#
# A GUI component for interacting with the instrument translator via MQTT.
# This version now correctly parses the incoming JSON payload to populate the table.
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
# Version 20250824.210000.9

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import pathlib
import sys
import json
import paho.mqtt.client as mqtt
from tkinter import filedialog
import csv

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from workers.mqtt_controller_util import MqttControllerUtility
from workers.worker_file_csv_export import CsvExportUtility
from workers.worker_mqtt_data_flattening import MqttDataFlattenerUtility
from display.styling.style import THEMES, DEFAULT_THEME

# --- Global Scope Variables ---
CURRENT_DATE = 20250824
CURRENT_TIME = 210000
CURRENT_TIME_HASH = 210000
REVISION_NUMBER = 9
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME_HASH * REVISION_NUMBER)
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")

# --- No Magic Numbers (as per your instructions) ---
MQTT_TOPIC_CONFIG_REQUEST = "OPEN-AIR/devices/scpi/COMMANDS"
MQTT_TOPIC_TRANSLATOR = "Root: Instrument"


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
            self.csv_export_util = CsvExportUtility(print_to_gui_func=console_log)
            self.data_flattener = MqttDataFlattenerUtility(print_to_gui_func=console_log)
            self.current_class_name = self.__class__.__name__

            self._apply_styles(theme_name=DEFAULT_THEME)

            # --- MQTT Buttons Section ---
            mqtt_frame = ttk.LabelFrame(self, text="MQTT Translator Controls")
            mqtt_frame.pack(fill=tk.X, padx=10, pady=10)

            # Button 1: Get Configuration
            self.get_config_button = ttk.Button(
                mqtt_frame,
                text="Get Configuration",
                command=self._get_config_mqtt_request
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
            
            # Button 4: Export to CSV
            self.export_button = ttk.Button(
                mqtt_frame,
                text="Export to CSV",
                command=self._export_table_data
            )
            self.export_button.pack(side=tk.LEFT, padx=5, pady=5)

            # --- MQTT Message Log Table ---
            self.table_frame = ttk.Frame(self)
            self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            # The table is now created dynamically on the first data payload.
            # It starts as an empty placeholder to be populated later.
            self.commands_table = ttk.Treeview(self.table_frame, show="headings", style="Custom.Treeview")
            self.commands_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            table_scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.commands_table.yview)
            self.commands_table.configure(yscrollcommand=table_scrollbar.set)
            table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # We now register our callback with the central utility.
            self.mqtt_util.add_subscriber(topic_filter=f"{MQTT_TOPIC_CONFIG_REQUEST}/#", callback_func=self._on_commands_message)

            # --- Status Bar at the bottom ---
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
        style.configure('TButton', background=colors["accent"], foreground=colors["text"], padding=colors["padding"] * 5, relief=colors["relief"], borderwidth=colors["border_width"] * 2)
        style.map('TButton', background=[('active', colors["secondary"])])
        
        # Treeview styling for the new table
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

    def _get_config_mqtt_request(self):
        """
        Publishes a message to the specific MQTT topic for a configuration request.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        # FIX: Clear the table and the data buffer before sending the request.
        self.commands_table.delete(*self.commands_table.get_children())
        self.data_flattener.clear_buffer()
        console_log("Clearing table and data buffer before requesting new data...")

        topic_parts = MQTT_TOPIC_CONFIG_REQUEST.split("/")
        root_topic = topic_parts[0]
        subtopic = "/".join(topic_parts[1:])
        message = "request"

        debug_log(
            message=f"🖥️🟢 Publishing '{message}' to specific MQTT topic '{root_topic}/{subtopic}'.",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            self.mqtt_util.publish_message(topic=root_topic, subtopic=subtopic, value=message)
            console_log(f"✅ Command '{message}' published successfully to '{root_topic}/{subtopic}'!")
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=console_log
            )

    def _publish_translator_message(self, child_topic: str, message: str):
        """
        Publishes a message to the instrument translator topic with a specific child topic.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        parent_topic = MQTT_TOPIC_TRANSLATOR
        
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
        Aggregates messages into a buffer before processing.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🖥️🔵 Received MQTT message on topic '{topic}'. Processing message one-by-one...",
            file=self.current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            pivoted_rows = self.data_flattener.process_mqtt_message_and_pivot(
                topic=topic,
                payload=payload,
                topic_prefix=MQTT_TOPIC_CONFIG_REQUEST
            )

            # Check if the utility returned a non-empty list of rows
            if pivoted_rows:
                # Dynamically configure columns if this is the first data payload
                if not self.commands_table["columns"]:
                    new_headers = list(pivoted_rows[0].keys())
                    self.commands_table["columns"] = new_headers
                
                    # Set headings for the new columns
                    for col in new_headers:
                        self.commands_table.heading(col, text=col.replace("_", " ").title())
                        # Adjust column widths if necessary
                        self.commands_table.column(col, width=150, stretch=True)
                
                # Insert the new pivoted data at the end of the table
                for row in pivoted_rows:
                    self.commands_table.insert('', tk.END, values=list(row.values()))

                console_log("✅ Commands table updated with new, beautifully-pivoted data!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 The data table construction has failed! A plague upon this error: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _export_table_data(self):
        """
        Exports the data from the Treeview to a CSV file.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🖥️🔵 Preparing to export table data to CSV.",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            file_path = filedialog.asksaveasfilename(
                initialdir=os.getcwd(),
                title="Save Table Data as CSV",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                defaultextension=".csv"
            )
            
            if file_path:
                data = []
                headers = self.commands_table["columns"]
                for item_id in self.commands_table.get_children():
                    row_values = self.commands_table.item(item_id, 'values')
                    row_dict = dict(zip(headers, row_values))
                    data.append(row_dict)
                    
                self.csv_export_util.export_data_to_csv(data=data, file_path=file_path)
                console_log(f"✅ Data successfully exported to {file_path}!")
            else:
                console_log("🟡 CSV export canceled by user.")

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
    
    # This is a temporary placeholder for logging functions to make the file runnable
    def mock_debug_log(message, file, version, function, console_print_func):
        print(f"DEBUG: {message}")

    def mock_console_log(message):
        print(f"CONSOLE: {message}")

    class MockMqttControllerUtility:
        def __init__(self, print_to_gui_func, log_treeview_func):
            self.subscribers = {}
        def connect_mqtt(self):
            print("Mock MQTT connected.")
        def add_subscriber(self, topic_filter, callback_func):
            self.subscribers[topic_filter] = callback_func
        def publish_message(self, topic, subtopic, value):
            print(f"Mock MQTT published: {topic}/{subtopic} with value '{value}'")
    
    # Mocking the `worker_file_csv_export` to run the example
    class MockCsvExportUtility:
        def __init__(self, print_to_gui_func):
            pass
        def export_data_to_csv(self, data, file_path):
            print(f"Mock export to CSV: {len(data)} rows exported to {file_path}")

    # Override the imports with our mocks
    sys.modules['workers.worker_logging'] = type('Module', (), {'debug_log': mock_debug_log, 'console_log': mock_console_log})
    sys.modules['workers.mqtt_controller_util'] = MockMqttControllerUtility
    sys.modules['workers.worker_file_csv_export'] = MockCsvExportUtility
    
    # This is a mock implementation of the data flattening and pivoting
    # It simulates the expected output for the `_on_commands_message` function
    class MockMqttDataFlattenerUtility:
        def __init__(self, print_to_gui_func):
            self._print_to_gui_console = print_to_gui_func
            self.data_buffer = {}
            
        def clear_buffer(self):
            self.data_buffer = {}

        def process_mqtt_message_and_pivot(self, topic: str, payload: str, topic_prefix: str) -> list:
            self.data_buffer[topic] = payload
            if topic.endswith('validated_value'):
                # Simulate the pivoting process
                mock_pivoted_data = [
                    {
                        "Topic": "OPEN-AIR/devices/scpi/COMMANDS/AMPLITUDE/DO/ATTENUATION/POWER/0DB",
                        "Parameter": "AMPLITUDE/DO/ATTENUATION/POWER/0DB/ANY/ANY",
                        "default_value": "0",
                        "VISA_Command_value": ":POWer:ATTenuation",
                        "validated_value": "NOT YET"
                    }
                ]
                # Reset the buffer
                self.data_buffer = {}
                return mock_pivoted_data
            return []

    sys.modules['workers.worker_mqtt_data_flattening'] = MockMqttDataFlattenerUtility
    
    # Re-import the class now that the mocks are in place
    from .gui_translator import TranslatorGUI
    
    mqtt_utility = MockMqttControllerUtility(print_to_gui_func=mock_console_log, log_treeview_func=lambda *args: None)
    mqtt_utility.connect_mqtt()

    app_frame = TranslatorGUI(parent=root, mqtt_util=mqtt_utility)

    root.mainloop()