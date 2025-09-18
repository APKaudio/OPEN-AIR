# gui_preset_editor.py
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
# Version 20250918.010500.5

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import pathlib
from tkinter import filedialog

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility
from workers.worker_file_csv_export import CsvExportUtility
from workers.worker_mqtt_data_flattening import MqttDataFlattenerUtility
from display.styling.style import THEMES, DEFAULT_THEME

# --- Global Scope Variables ---
CURRENT_DATE = 20250918
CURRENT_TIME = 10500
REVISION_NUMBER = 5
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = CURRENT_DATE * CURRENT_TIME * REVISION_NUMBER
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")

# --- No Magic Numbers (as per your instructions) ---
MQTT_TOPIC_FILTER = "OPEN-AIR/repository/presets"


class InstrumentTranslatorGUI(ttk.Frame):
    """
    A GUI component for displaying MQTT data in a table and exporting it.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        """
        Initializes the GUI, sets up the layout, and subscribes to the MQTT topic.
        
        Args:
            parent (tk.Widget): The parent widget for this frame.
            mqtt_util (MqttControllerUtility): The MQTT utility instance for communication.
        """
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

            # --- NEW: Create headers on initialization so the table is always populated ---
            self._create_headers()
            
            self.mqtt_util.add_subscriber(topic_filter=f"{self.topic_entry.get()}/#", callback_func=self._on_commands_message)

            # --- NEW: Bind double-click event for cell editing ---
            self.commands_table.bind("<Double-1>", self._on_edit_cell)

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
    
    def _create_headers(self):
        """
        Creates all the columns in the Treeview when the GUI is initialized.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🖥️🟢 Creating table headers on initialization.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        # Manually define all the columns based on the expected flattened data structure
        headers = [
            "Parameter", "Active", "FileName", "NickName", "Start", "Stop", 
            "Center", "Span", "RBW", "VBW", "RefLevel", "Attenuation", 
            "MaxHold", "HighSens", "PreAmp", "Trace1Mode", "Trace2Mode", 
            "Trace3Mode", "Trace4Mode", "Marker1Max", "Marker2Max", 
            "Marker3Max", "Marker4Max", "Marker5Max", "Marker6Max"
        ]
        
        self.commands_table["columns"] = tuple(headers)
        for col in headers:
            self.commands_table.heading(col, text=col.replace("_", " ").title())
            self.commands_table.column(col, width=150, stretch=True)

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
        It processes the message, flattens the data, and updates or adds rows to the table.
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

            if pivoted_rows:
                # Add any new columns that might have appeared dynamically
                current_columns = list(self.commands_table["columns"])
                for new_header in pivoted_rows[0].keys():
                    if new_header not in current_columns:
                        self.commands_table["columns"] = current_columns + [new_header]
                        self.commands_table.heading(new_header, text=new_header.replace("_", " ").title())
                        self.commands_table.column(new_header, width=150, stretch=True)
                        current_columns.append(new_header)
                            
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
                    
                    # Create a full list of values based on the current column order
                    full_values = [row.get(col, '') for col in self.commands_table["columns"]]

                    if item_id_to_update:
                        # Update the existing row
                        self.commands_table.item(item_id_to_update, values=full_values)
                        console_log(f"✅ Updated existing row for '{parameter_path}'.")
                    else:
                        # Insert a new row if it doesn't exist
                        self.commands_table.insert('', tk.END, values=full_values)
                        console_log(f"✅ Added new row for '{parameter_path}'.")
            else:
                # NEW: Handle row deletion if the payload is empty
                topic_parts = topic.split('/')
                # The parameter path is everything after the topic prefix
                parameter_path = '/'.join(topic_parts[len(self.topic_entry.get().split('/')):])
                
                # Find the item with the matching Parameter path and remove it
                for item_id in self.commands_table.get_children():
                    if self.commands_table.item(item_id, 'values')[0] == parameter_path:
                        self.commands_table.delete(item_id)
                        console_log(f"✅ Removed row for deleted topic: '{parameter_path}'.")
                        break
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 The data table construction has failed! A plague upon this error: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _on_edit_cell(self, event):
        """
        Event handler for a double-click on a table cell. It creates a temporary
        Entry widget for in-place editing.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        # Get the item and column that were double-clicked
        item_id = self.commands_table.identify_row(event.y)
        column_id = self.commands_table.identify_column(event.x)
        
        if not item_id or not column_id:
            return  # Not on a cell

        # Get column index from column ID string
        column_index = int(column_id.replace("#", "")) - 1
        
        # Get the current value of the cell
        current_value = self.commands_table.item(item_id, 'values')[column_index]
        
        # Get the bounding box of the cell to place the entry widget
        bbox = self.commands_table.bbox(item_id, column_id)
        if not bbox:
            return
            
        x, y, width, height = bbox

        # Create a temporary Entry widget for editing
        edit_entry = ttk.Entry(self.commands_table)
        edit_entry.place(x=x, y=y, width=width, height=height)
        edit_entry.insert(0, current_value)
        edit_entry.focus_set()
        edit_entry.select_range(0, tk.END)

        def on_update_cell(event):
            """
            Inner function to capture the new value and push it to MQTT.
            """
            new_value = edit_entry.get()
            
            # Get the column header from the column index
            column_header = self.commands_table.heading(column_id, 'text').replace(' ', '_').lower()

            # Get the parameter path from the first column
            parameter_path = self.commands_table.item(item_id, 'values')[0]
            
            # Construct the full MQTT topic
            # The format is ROOT_TOPIC/Parameter/column_header
            topic = f"{self.topic_entry.get()}/{parameter_path}/{column_header}"
            
            debug_log(
                message=f"🖥️🔵 Cell edited. Publishing new value '{new_value}' to topic '{topic}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
            # Publish the new value to MQTT
            self.mqtt_util.publish_message(topic=topic, subtopic="", value=new_value, retain=True)

            # Update the Treeview cell directly with the new value
            all_values = list(self.commands_table.item(item_id, 'values'))
            all_values[column_index] = new_value
            self.commands_table.item(item_id, values=all_values)

            # Clean up the entry widget
            edit_entry.destroy()
            
            # A celebratory message to signal success
            console_log(f"✅ Cell updated and new value pushed to MQTT: '{new_value}'.")

        # Bind events to the entry widget for finishing editing
        edit_entry.bind("<Return>", on_update_cell)
        edit_entry.bind("<FocusOut>", on_update_cell)

        # A quick debug log to show we've entered edit mode
        debug_log(
            message=f"🛠️🟢 Initiating cell edit mode for Item '{item_id}' at Column '{column_id}'.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

    def _export_table_data(self):
        """
        Opens a file dialog and exports the current data from the table to a CSV file.
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