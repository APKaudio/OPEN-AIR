# display/left_50/top_100/tab_3_presets/sub_tab_2_editor/gui_preset_editor.py
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251129  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 1 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


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
# Version 20251127.000000.1

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import pathlib
from tkinter import filedialog
import csv
import json
from decimal import Decimal
from tkinter import TclError

# --- Module Imports ---
from workers.worker_active_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility
from workers.worker_file_csv_export import CsvExportUtility
from display.styling.style import THEMES, DEFAULT_THEME
import workers.worker_project_paths

Local_Debug_Enable = False

def debug_log_switch(message, file, version, function, console_print_func):
    if Local_Debug_Enable:
        debug_log(message, file, version, function, console_print_func)

def console_log_switch(message):
    if Local_Debug_Enable:
        console_log(message)

# --- Global Scope Variables ---
CURRENT_DATE = 20251129
CURRENT_TIME = 222500
REVISION_NUMBER = 1
current_version = "20251127.000000.1"
current_version_hash = 20251127 * 0 * 1
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")
# --- No Magic Numbers (as per your instructions) ---
MQTT_TOPIC_FILTER = "OPEN-AIR/repository/presets"
# Fallback path definition (actual path will be dynamically imported)
PRESET_REPO_PATH_FALLBACK = pathlib.Path("DATA/PRESET.CSV")

# FIXED LIST OF ATTRIBUTES (New static columns)
ATTRIBUTES = [
    "Active", "FileName", "NickName", "Start", "Stop", 
    "Center", "Span", "RBW", "VBW", "RefLevel", "Attenuation", 
    "MaxHold", "HighSens", "PreAmp", "Trace1Mode", "Trace2Mode", 
    "Trace3Mode", "Trace4Mode"
]
# The first column is always 'Parameter' (The Preset Key, e.g., PRESET_001)
HEADERS = ["Parameter"] + ATTRIBUTES 
# Fixed column width for all columns
COLUMN_WIDTH = 150


class PresetEditorGUI(ttk.Frame):
    """
    A GUI component for displaying and editing preset data from a CSV,
    normalized for table display.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        current_function_name = inspect.currentframe().f_code.co_name

        debug_log_switch(
            message=f"🖥️🟢 Initializing the {self.__class__.__name__}. Normalized view active.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            if 'config' in kwargs:
                kwargs.pop('config')
            super().__init__(parent, *args, **kwargs)

            self.current_file = current_file
            self.current_version = current_version
            self.current_version_hash = current_version_hash
            self.mqtt_util = mqtt_util
            self.csv_export_util = CsvExportUtility(print_to_gui_func=console_log)
            # Normalized data model: {preset_key: {attribute: value, ...}, ...}
            self.normalized_data = {} 
            self.current_class_name = self.__class__.__name__

            self._apply_styles(theme_name=DEFAULT_THEME)

            # --- MQTT Message Log Table ---
            self.table_frame = ttk.Frame(self)
            self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            horizontal_scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL)
            self.commands_table = ttk.Treeview(self.table_frame, 
                                               xscrollcommand=horizontal_scrollbar.set, 
                                               show="headings", 
                                               columns=HEADERS, 
                                               style="Custom.Treeview")
            horizontal_scrollbar.config(command=self.commands_table.xview)
            
            vertical_scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.commands_table.yview)
            self.commands_table.config(yscrollcommand=vertical_scrollbar.set)

            horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.commands_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # --- Create headers based on HEADERS (Columns) ---
            self._create_headers()
            
            self.mqtt_util.add_subscriber(topic_filter=f"{MQTT_TOPIC_FILTER}/#", callback_func=self._on_commands_message) 

            # --- NEW: Bind double-click event for cell editing ---
            self.commands_table.bind("<Double-1>", self._on_edit_cell)

            # --- Persistence Bindings (Load on Init, Save on Exit) ---
            parent_widget = parent
            while not isinstance(parent_widget, tk.Tk):
                if isinstance(parent_widget, ttk.Notebook):
                    parent_widget.bind("<<NotebookTabChanged>>", self._on_tab_change_save_data, add="+ ")
                    break
                parent_widget = parent_widget.master

            # --- File Controls Section ---
            file_frame = ttk.LabelFrame(self, text="File")
            file_frame.pack(fill=tk.X, padx=10, pady=5)
           
            # Button: Export to CSV (Normalized, Flat Structure)
            self.export_button = ttk.Button(
                file_frame,
                text="Export to CSV (Normalized)",
                command=self._export_table_data
            )
            self.export_button.pack(side=tk.LEFT, padx=5, pady=5)
            
            # Button: Save to Internal Repository (Original Transposed Structure)
            # UPDATED TEXT to reflect the new normalized save format.
            self.save_repo_button = ttk.Button(
                file_frame,
                text="Save to Internal Repo (Normalized)",
                command=lambda: self._save_data_to_csv_from_normalized_model(file_path=self._resolve_preset_repo_path())
            )
            self.save_repo_button.pack(side=tk.LEFT, padx=5, pady=5)


            # --- Status Bar at the bottom ---
            status_bar = ttk.Frame(self, relief=tk.SUNKEN, borderwidth=1)
            status_bar.pack(side=tk.BOTTOM, fill=tk.X, expand=False)

            file_parts = self.current_file.rsplit('/', 1)
            file_folder = file_parts[0] if len(file_parts) > 1 else ""
            file_name = file_parts[-1]

            status_text = f"Version: {self.current_version} | Folder: {file_folder} | File: {file_name}"
            status_label = ttk.Label(status_bar, text=status_text, anchor='w')
            status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            console_log_switch("✅ Preset Editor GUI initialized successfully!")
            
            # --- Load initial data from CSV and render ---
            self._load_data_from_csv()
            self._update_treeview()

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log_switch(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
    
    def _create_headers(self):
        """
        Creates all the columns in the Treeview and configures them with a fixed width.
        """
        self.commands_table["columns"] = HEADERS
        
        for col_name in HEADERS:
            display_name = col_name.replace('_', ' ').title()
            
            self.commands_table.heading(col_name, text=display_name, command=lambda c=col_name: self._sort_treeview(c, False))
            
            # All columns are fixed width 150px
            if col_name == "Parameter":
                self.commands_table.column(col_name, width=150, stretch=False, anchor='w')
            else:
                self.commands_table.column(col_name, width=COLUMN_WIDTH, stretch=False, anchor='center')
            
    def _load_data_from_csv(self):
        """
        Reads the original presets.csv, extracts preset data, and populates the 
        normalized_data dictionary.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        # 1. Resolve the correct path 
        csv_file_path = self._resolve_preset_repo_path()
        
        if not csv_file_path.exists():
            console_log_switch("🟡 presets.csv not found. Starting with an empty table.")
            return

        try:
            with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                
                # Clear existing data
                self.normalized_data = {}

                for row in csv_reader:
                    preset_key = row.get("Parameter")
                    if preset_key:
                        self.normalized_data[preset_key] = {"Parameter": preset_key}
                        for attribute in ATTRIBUTES:
                            # Directly assign attributes from CSV, converting 'Active' to boolean
                            value = row.get(attribute, 'N/A')
                            if attribute == "Active":
                                self.normalized_data[preset_key][attribute] = value.lower() == 'true'
                            else:
                                self.normalized_data[preset_key][attribute] = value
                        
            console_log_switch(f"✅ Data successfully loaded from {csv_file_path} and normalized in memory.")
        except Exception as e:
            console_log(f"❌ Error loading data from presets.csv: {e}")
            debug_log_switch(
                message=f"❌🔴 Failed to load and normalize CSV data. The error be: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
    def _update_treeview(self):
        """
        Re-populates the Treeview from the internal normalized_data model.
        """
        current_function_name = inspect.currentframe().f_code.co_name

        # Clear existing rows
        self.commands_table.delete(*self.commands_table.get_children())
        
        # Insert new rows
        for preset_key in sorted(self.normalized_data.keys()):
            row_data = self.normalized_data[preset_key]
            
            # Create a list of values matching the column order (HEADERS)
            row_values = [row_data.get(header, 'N/A') for header in HEADERS]
            
            # Use the preset_key as the item ID (iid) for easy lookups
            self.commands_table.insert("", tk.END, iid=preset_key, values=row_values)

        debug_log_switch(
            message=f"🖥️✅ Treeview updated with {len(self.normalized_data)} preset rows.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

    def _on_commands_message(self, topic, payload):
        """
        Callback for when an MQTT message is received.
        Updates the internal normalized_data model and triggers a UI refresh and save.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        try:
            topic_parts = topic.split('/')
            
            # --- Case 1: Monolithic Preset Update (from another component/device) ---
            if len(topic_parts) == len(MQTT_TOPIC_FILTER.split('/')) + 1 and topic_parts[-2] == "presets":
                preset_key = topic_parts[-1]
                
                # 1. Check for a delete message (empty payload or null value)
                if payload == "" or payload.lower() == 'null':
                    self._delete_preset(preset_key)
                    # Trigger immediate save after deletion
                    self._save_data_to_csv_from_normalized_model(file_path=self._resolve_preset_repo_path())
                    return

                # 2. Parse the monolithic JSON blob
                preset_data_str = json.loads(payload)["value"]
                if preset_data_str.startswith('"') and preset_data_str.endswith('"'):
                    preset_data_str = preset_data_str.strip('"')

                preset_data = json.loads(preset_data_str)
                
                # 3. Update normalized_data model
                self.normalized_data[preset_key] = {"Parameter": preset_key}
                for attribute in ATTRIBUTES:
                    self.normalized_data[preset_key][attribute] = preset_data.get(attribute, 'N/A')
                    
                console_log_switch(f"✅ Updated preset '{preset_key}' from monolithic MQTT topic.")
                
                # Trigger immediate save after successful update
                self._save_data_to_csv_from_normalized_model(file_path=self._resolve_preset_repo_path())
                
            # --- Case 2: Single Field Update (robustness for external single-field updates) ---
            elif len(topic_parts) == len(MQTT_TOPIC_FILTER.split('/')) + 2 and topic_parts[-3] == "presets":
                preset_key = topic_parts[-2]
                attribute = topic_parts[-1] 
                payload_value = json.loads(payload)["value"]
                
                # 1. Update normalized_data model
                if preset_key in self.normalized_data and attribute in self.normalized_data[preset_key]:
                    self.normalized_data[preset_key][attribute] = payload_value
                    console_log_switch(f"✅ Updated attribute '{attribute}' for preset '{preset_key}'.")
                    
                # Trigger immediate save after single field update
                self._save_data_to_csv_from_normalized_model(file_path=self._resolve_preset_repo_path())
                
            # --- Final steps ---
            self._update_treeview()

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log_switch(
                message=f"❌🔴 Update failed! The error be: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _delete_preset(self, preset_key):
        """Removes a preset from the internal model and triggers a UI refresh."""
        if preset_key in self.normalized_data:
            del self.normalized_data[preset_key]
        self._update_treeview()

    def _on_edit_cell(self, event):
        """
        Event handler for a double-click on a table cell. Triggers **republish of the whole blob**
        after updating a single cell in the internal model.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        item_id = self.commands_table.identify_row(event.y)
        column_id = self.commands_table.identify_column(event.x)
        
        # Do not edit column #0 or the first column ('Parameter')
        if not item_id or not column_id or column_id == '#0' or column_id == '#1': 
            return 

        try:
            # 1. Identify the Preset (Row ID) and Attribute (Column Header)
            preset_key = item_id 
            col_identifier = self.commands_table.heading(column_id, 'id')
            attribute = col_identifier 
            current_value = self.commands_table.set(item_id, attribute)
            
            # 2. Create the editor widget (standard process)
            bbox = self.commands_table.bbox(item_id, column_id)
            if not bbox: return
            x, y, width, height = bbox
            edit_entry = ttk.Entry(self.commands_table, style="Markers.TEntry", name="cell_editor")
            edit_entry.place(x=x, y=y, width=width, height=height)
            edit_entry.insert(0, current_value)
            edit_entry.focus_set()
            edit_entry.select_range(0, tk.END)

            def on_update_cell(event):
                new_value = edit_entry.get()
                
                try:
                    # Update the internal model immediately
                    if preset_key in self.normalized_data:
                        self.normalized_data[preset_key][attribute] = new_value
                    
                    # 1. Rebuild the monolithic JSON blob from the updated internal model
                    updated_preset_data = {}
                    for attr in ATTRIBUTES:
                        updated_preset_data[attr] = self.normalized_data[preset_key].get(attr, 'N/A')
                        
                    monolithic_blob = json.dumps(updated_preset_data)
                    
                    # 2. Publish the monolithic blob to the single preset topic (triggers Case 1 logic)
                    topic = f"{MQTT_TOPIC_FILTER}/{preset_key}"
                    self.mqtt_util.publish_message(topic=topic, subtopic="", value=monolithic_blob, retain=True)

                    console_log_switch(f"✅ Full blob for '{preset_key}' republished after '{attribute}' edit.")
                except Exception as e:
                    console_log(f"❌ Error sending cell update to MQTT. Error: {e}")

                edit_entry.destroy()
            
            edit_entry.bind("<Return>", on_update_cell)
            edit_entry.bind("<FocusOut>", on_update_cell)

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")

    def _export_table_data(self):
        """
        Opens a file dialog and exports the current data from the internal model to a new CSV file 
        in the clean, normalized format (rows are presets, columns are attributes), matching the table exactly.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log_switch(
            message=f"🖥️🔵 Preparing to export table data to CSV.",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            file_path = filedialog.asksaveasfilename(
                initialdir=os.getcwd(),
                title="Save Table Data as CSV (Normalized)",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                defaultextension=".csv"
            )
            
            if file_path:
                # Use the core saving logic, passing the path for user export
                self._save_data_to_csv_from_normalized_model(file_path=file_path)
                console_log_switch(f"✅ Data successfully exported to {file_path}!")
            else:
                console_log_switch("🟡 CSV export canceled by user.")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            
    # --- CORE FIX IMPLEMENTATION: Unifying the save logic ---
    def _save_data_to_csv_from_normalized_model(self, file_path: pathlib.Path):
        """
        Saves the normalized table data (Preset rows, Attribute columns) directly to a CSV,
        matching the table view exactly.
        
        This function is now the *only* core saving mechanism, used for both 
        user exports and internal repository persistence, ensuring identical formats.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log_switch(
            message=f"💾🟢 Saving normalized data (table format) to: '{file_path}'",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            # 1. Prepare the data for the normalized CSV structure (table view)
            final_csv_rows = []
            for preset_key in sorted(self.normalized_data.keys()):
                 final_csv_rows.append(self.normalized_data[preset_key])
                
            # 2. Write to the CSV file
            csv_headers = HEADERS # ["Parameter", "Active", "FileName", ...]
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_headers) 
                
                writer.writeheader()
                writer.writerows(final_csv_rows)

            if file_path == self._resolve_preset_repo_path():
                 console_log_switch(f"✅ Internal preset repository synchronized (Normalized format).")
            else:
                console_log_switch(f"✅ Table data exported to '{file_path}'.")

        except Exception as e:
            console_log(f"❌ Error saving normalized CSV: {e}")
            debug_log_switch(
                message=f"❌🔴 Failed to save normalized CSV. The error be: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
    def _on_tab_change_save_data(self, event):
        """Saves data to the internal repository path when the tab is exited."""
        current_function_name = inspect.currentframe().f_code.co_name
        
        tab_widget = event.widget
        selected_tab = tab_widget.select()
        
        current_tabs = [tab_widget.tab(i, "text") for i in tab_widget.tabs()]
        if not current_tabs:
            return

        try:
            current_tab_index = tab_widget.index(selected_tab)
        except TclError:
            return

        if current_tabs[current_tab_index] != "Preset Editor": 
            # Now calls the core, unified save function, ensuring the repo file is normalized.
            self._save_data_to_csv_from_normalized_model(file_path=self._resolve_preset_repo_path())
            debug_log_switch(
                message="💾🔵 Saving presets on tab exit.",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
    def _resolve_preset_repo_path(self):
        """Attempts to import the constant PRESET_REPO_PATH, falling back if necessary."""
        try:
            # Use the imported module
            import workers.worker_project_paths
            if hasattr(workers.worker_project_paths, 'PRESET_REPO_PATH'):
                return workers.worker_project_paths.PRESET_REPO_PATH
        except Exception:
            return PRESET_REPO_PATH_FALLBACK


    def _sort_treeview(self, column_name, ascending):
        """
        Sorts the treeview rows based on the values in the selected column.
        """
        preset_names = list(self.commands_table["columns"])
        try:
            col_index = preset_names.index(column_name)
        except ValueError:
            return 

        l = [(self.commands_table.set(k, column_name), k) for k in self.commands_table.get_children('')]
        
        l.sort(key=lambda x: str(x[0]), reverse=not ascending)
        
        for index, (val, k) in enumerate(l):
            self.commands_table.move(k, '', index)

        self.sort_column = column_name
        self.sort_direction = ascending

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
