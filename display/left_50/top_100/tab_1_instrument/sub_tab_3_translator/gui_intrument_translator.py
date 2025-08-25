MQTT_TOPIC_FILTER = "OPEN-AIR/devices/scpi"


# display/gui_instrument_translator.py
#
# A GUI component for editing markers, designed to handle both full data sets
# and single-value updates intelligently via MQTT.
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
# Version 20250825.170951.1

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
CURRENT_DATE = 20250825
CURRENT_TIME = 170951
REVISION_NUMBER = 1
current_version = "20250825.170951.1"
current_version_hash = 20250825 * 170951 * 1
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")

# --- No Magic Numbers (as per your instructions) ---




class gui_instrument_translator(ttk.Frame):
    """
    A GUI component for interacting with the instrument translator via MQTT.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        current_function_name = inspect.currentframe().f_code.co_name

        debug_log(
            message=f"🖥️🟢 Initializing the {self.__class__.__name__}.",
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

            # --- MQTT Topic Entry Section ---
            topic_frame = ttk.LabelFrame(self, text="MQTT Topic Filter")
            topic_frame.pack(fill=tk.X, padx=10, pady=5)
            self.topic_entry = ttk.Entry(topic_frame, width=80)
            self.topic_entry.insert(0, MQTT_TOPIC_FILTER)
            self.topic_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
            
            # --- MQTT Message Log Table ---
            self.table_frame = ttk.Frame(self)
            self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            horizontal_scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL)
            self.commands_table = ttk.Treeview(self.table_frame, xscrollcommand=horizontal_scrollbar.set, show="headings", style="Custom.Treeview")
            horizontal_scrollbar.config(command=self.commands_table.xview)
            
            vertical_scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.commands_table.yview)
            self.commands_table.config(yscrollcommand=vertical_scrollbar.set)

            horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.commands_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            self.mqtt_util.add_subscriber(topic_filter=f"{self.topic_entry.get()}/#", callback_func=self._on_commands_message)

            # --- File Controls Section ---
            file_frame = ttk.LabelFrame(self, text="File")
            file_frame.pack(fill=tk.X, padx=10, pady=5)
           
            # Button: Export to CSV
            self.export_button = ttk.Button(
                file_frame,
                text="Export to CSV",
                command=self._export_table_data
            )
            self.export_button.pack(side=tk.LEFT, padx=5, pady=5)


            # --- Status Bar at the bottom ---
            status_bar = ttk.Frame(self, relief=tk.SUNKEN, borderwidth=1)
            status_bar.pack(side=tk.BOTTOM, fill=tk.X, expand=False)

            file_parts = self.current_file.rsplit('/', 1)
            file_folder = file_parts[0] if len(file_parts) > 1 else ""
            file_name = file_parts[-1]

            status_text = f"Version: {self.current_version} | Folder: {file_folder} | File: {file_name}"
            status_label = ttk.Label(status_bar, text=status_text, anchor='w')
            status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            console_log("✅ Instrument Translator GUI initialized successfully!")

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

        style.configure('TFrame', background=colors["bg"])
        style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
        style.configure('TLabelframe', background=colors["bg"], foreground=colors["fg"])
        style.configure('TButton', background=colors["accent"], foreground=colors["text"], padding=colors["padding"] * 5, relief=colors["relief"], borderwidth=colors["border_width"] * 2)
        style.map('TButton', background=[('active', colors["secondary"])])
        
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

    def _on_commands_message(self, topic, payload):
        """
        Callback for when an MQTT message is received on the commands topic.
        Aggregates messages into a buffer before processing.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🖥️🔵 Received MQTT message on topic '{topic}'. Processing message...",
            file=self.current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            pivoted_rows = self.data_flattener.process_mqtt_message_and_pivot(
                topic=topic,
                payload=payload,
                topic_prefix=self.topic_entry.get()
            )

            # The GUI's job is to simply react to the flattener's output.
            if pivoted_rows:
                # Dynamically configure columns ONLY IF this is the first data payload.
                if not self.commands_table["columns"]:
                    new_headers = list(pivoted_rows[0].keys())
                    self.commands_table["columns"] = tuple(new_headers)
                    for col in new_headers:
                        self.commands_table.heading(col, text=col.replace("_", " ").title())
                        self.commands_table.column(col, width=150, stretch=True)

                # Iterate through each row of the new data to update or add
                for row in pivoted_rows:
                    parameter_path = row.get("Parameter")
                    
                    # Find if a row with this Parameter already exists
                    item_id_to_update = None
                    for item_id in self.commands_table.get_children():
                        row_values = self.commands_table.item(item_id, 'values')
                        if row_values and row_values[0] == parameter_path:
                            item_id_to_update = item_id
                            break
                    
                    if item_id_to_update:
                        # Update the existing row
                        new_values = [row.get(col, '') for col in self.commands_table["columns"]]
                        self.commands_table.item(item_id_to_update, values=new_values)
                        console_log(f"✅ Updated existing row for '{parameter_path}'.")
                    else:
                        # Insert a new row if it doesn't exist
                        new_values = [row.get(col, '') for col in self.commands_table["columns"]]
                        self.commands_table.insert('', tk.END, values=new_values)
                        console_log(f"✅ Added new row for '{parameter_path}'.")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 The data table construction has failed! A plague upon this error: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
    def _update_table_intelligently(self, topic: str, payload: str):
        """
        This function is now deprecated and is no longer used by the new workflow.
        All updates are handled by the data flattener.
        """
        # This function is now deprecated and will not be used.
        pass

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
    root.title("Instrument Translator Test")
    
    def mock_debug_log(message, file, version, function, console_print_func):
        print(f"DEBUG: {message}")

    def mock_console_log(message):
        print(f"CONSOLE: {message}")

    class MockMqttControllerUtility:
        def __init__(self, print_to_gui_func):
            self.subscribers = {}
        def connect_mqtt(self):
            print("Mock MQTT connected.")
        def add_subscriber(self, topic_filter, callback_func):
            self.subscribers[topic_filter] = callback_func
        def publish_message(self, topic, subtopic=None, value=None):
            if subtopic:
                full_topic = f"{topic}/{subtopic}"
            else:
                full_topic = topic
            print(f"Mock MQTT published: {full_topic} with value '{value}'")
    
    class MockCsvExportUtility:
        def __init__(self, print_to_gui_func):
            pass
        def export_data_to_csv(self, data, file_path):
            print(f"Mock export to CSV: {len(data)} rows exported to {file_path}")

    class MockMqttDataFlattenerUtility:
        def __init__(self, print_to_gui_func):
            self._print_to_gui_console = print_to_gui_func
            self.data_buffer = {}
            self.first_key_name = None

        def clear_buffer(self):
            self.data_buffer = {}
            self.first_key_name = None

        def process_mqtt_message_and_pivot(self, topic: str, payload: str, topic_prefix: str) -> list:
            # Simple mock to simulate different payloads for testing
            if "N9340B" in topic:
                mock_pivoted_data = [
                    {
                        "Parameter": "COMMANDS/AMPLITUDE/DO/HIGH SENSITIVE/POWER/OFF/Keysight Technologies/N9340B",
                        "VISA_Command": ":DISPlay:WINDow:TRACe:Y:RLEVel 0; :POWer:ATTenuation 20; :POWer:GAIN OFF",
                        "validated": "NOT YET"
                    }
                ]
            else:
                mock_pivoted_data = [
                    {
                        "Parameter": "COMMANDS/AMPLITUDE/DO/HIGH SENSITIVE/POWER/OFF/Keysight Technologies/N9342CN",
                        "Active": "true",
                        "Default_value": "OFF",
                        "VISA_Command": ":POWer:HSENsitive",
                        "validated": "NOT YET"
                    }
                ]
            return mock_pivoted_data

    # Override the imports with mocks
    sys.modules['workers.worker_logging'] = type('Module', (), {'debug_log': mock_debug_log, 'console_log': mock_console_log})
    sys.modules['workers.mqtt_controller_util'] = MockMqttControllerUtility
    sys.modules['workers.worker_file_csv_export'] = MockCsvExportUtility
    sys.modules['workers.worker_mqtt_data_flattening'] = MockMqttDataFlattenerUtility
    
    from display.styling.style import THEMES, DEFAULT_THEME
    
    
    mqtt_utility = MockMqttControllerUtility(print_to_gui_func=mock_console_log)
    mqtt_utility.connect_mqtt()

    app_frame = gui_instrument_translator(parent=root, mqtt_util=mqtt_utility)
    
    root.mainloop()