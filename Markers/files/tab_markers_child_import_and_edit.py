# tabs/Markers/tab_markers_child_import_and_edit.py
#
# This file manages the Report Converter tab in the GUI, handling
# It provides functionality to convert spectrum analyzer report files (HTML, SHW, or Soundbase PDF)
# into CSV format. Crucially, it now displays the converted data in an editable, sortable table
# (Treeview) and allows users to load, save, and save as MARKERS.CSV files directly.
# The previous text-based conversion log has been replaced by this data table.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
#
#
# Version 20250802.0055.1 (Fixed TclError: expected integer but got "" for Treeview rowheight.)
# Version 20250804.000014.0 (FIXED: Ensured MarkersDisplayTab reloads from file when updated by ReportConverterTab.)
# Version 20250804.000015.0 (FIXED: ReportConverterTab now explicitly tells MarkersDisplayTab to load_markers_from_file.)

current_version = "20250804.000015.0" # Incremented version
# current_version_hash = 20250802 * 55 * 1 # Example hash, needs adjustment based on new versioning format

import tkinter as tk
from tkinter import filedialog, ttk
import os
import csv
import xml.etree.ElementTree as ET
import sys
import inspect
import threading
import json 
import datetime 
import re 

# Import the new report converter utility functions
from ..files.utils_marker_report_converter import convert_html_report_to_csv, generate_csv_from_shw, convert_pdf_report_to_csv
from src.gui_elements import TextRedirector 
from display.debug_logic import debug_log 
from display.console_logic import console_log 
# Removed: from tabs.Markers.tab_markers_child_display import load_markers_from_file
# The load_markers_from_file from display tab will be called via the instance.


class ReportConverterTab(ttk.Frame):
    """
    A Tkinter Frame that provides functionality to convert spectrum analyzer
    report files (HTML, SHW, or Soundbase PDF) into CSV format.
    It now also displays the converted data in an editable, sortable table
    and allows loading/saving of MARKERS.CSV files.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs): # console_print_func will be removed later
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) 
        debug_log(f"[{current_file} - {current_function}] Initializing ReportConverterTab...",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        # self.console_print_func is removed, using console_log directly

        self.output_csv_path = None # To store the path of the last generated/loaded CSV

        self.tree_headers = [] # Stores current headers of the Treeview
        self.tree_data = []    # Stores current data of the Treeview (list of dicts)
        self.sort_column = None # To keep track of the last sorted column
        self.sort_direction = False # True for ascending, False for descending

        self._create_widgets()


    def _create_widgets(self):
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) 
        debug_log(f"[{current_file} - {current_function}] Creating ReportConverterTab widgets.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1) 
        self.grid_rowconfigure(2, weight=0) 


        load_markers_frame = ttk.LabelFrame(self, text="Load Markers", padding=(5,5,5,5), style='Dark.TLabelframe')
        load_markers_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        load_markers_frame.grid_columnconfigure(0, weight=1)
        load_markers_frame.grid_columnconfigure(1, weight=1)
        load_markers_frame.grid_columnconfigure(2, weight=1)
        load_markers_frame.grid_columnconfigure(3, weight=1) 

        self.load_csv_button = ttk.Button(load_markers_frame, text="Load CSV Marker Set", command=self._load_markers_file, style='Green.TButton')
        self.load_csv_button.grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        self.load_ias_html_button = ttk.Button(load_markers_frame, text="Load IAS HTML", command=lambda: self._initiate_conversion("HTML"), style='Blue.TButton')
        self.load_ias_html_button.grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        self.load_wwb_shw_button = ttk.Button(load_markers_frame, text="Load WWB.shw", command=lambda: self._initiate_conversion("SHW"), style='Blue.TButton')
        self.load_wwb_shw_button.grid(row=0, column=2, padx=2, pady=2, sticky="ew")

        self.load_sb_pdf_button = ttk.Button(load_markers_frame, text="Load SB PDF", command=lambda: self._initiate_conversion("PDF"), style='Blue.TButton')
        self.load_sb_pdf_button.grid(row=0, column=3, padx=2, pady=2, sticky="ew")


        marker_table_frame = ttk.LabelFrame(self, text="Marker Editor", padding=(5,5,5,5), style='Dark.TLabelframe')
        marker_table_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        marker_table_frame.grid_columnconfigure(0, weight=1)
        marker_table_frame.grid_rowconfigure(0, weight=1)

        self.marker_tree = ttk.Treeview(marker_table_frame, show="headings", style="Treeview")
        self.marker_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        tree_yscroll = ttk.Scrollbar(marker_table_frame, orient="vertical", command=self.marker_tree.yview)
        tree_yscroll.grid(row=0, column=1, sticky="ns")
        self.marker_tree.configure(yscrollcommand=tree_yscroll.set)

        tree_xscroll = ttk.Scrollbar(marker_table_frame, orient="horizontal", command=self.marker_tree.xview)
        tree_xscroll.grid(row=1, column=0, sticky="ew")
        self.marker_tree.configure(xscrollcommand=tree_xscroll.set)

        self.marker_tree.bind("<Double-1>", self._on_tree_double_click) 
        self.marker_tree.bind("<ButtonRelease-1>", self._on_tree_header_click) 


        self.save_open_air_button = ttk.Button(self, text="Save Markers as Open Air.csv", command=self._save_open_air_csv, style='Orange.TButton')
        self.save_open_air_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")


    def _populate_marker_tree(self):
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) 
        debug_log(f"[{current_file} - {current_function}] Populating marker treeview.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        self.marker_tree.delete(*self.marker_tree.get_children())

        if not self.tree_headers:
            console_log("ℹ️ No headers available to display in Marker Editor table.", function=current_function)
            self.marker_tree["columns"] = ()
            return

        self.marker_tree["columns"] = self.tree_headers
        
        try:
            row_height_str = ttk.Style().lookup("Treeview", "rowheight")
            row_height = int(row_height_str) if row_height_str else 25 
        except (TclError, ValueError):
            row_height = 25 

        for col_name in self.tree_headers:
            self.marker_tree.heading(col_name, text=col_name, anchor="w")
            self.marker_tree.column(col_name, width=row_height * 5, stretch=tk.YES) 

        for i, row_data in enumerate(self.tree_data):
            values = [row_data.get(header, "") for header in self.tree_headers]
            self.marker_tree.insert("", "end", iid=str(i), values=values, tags=('editable',))

        console_log(f"✅ Displayed {len(self.tree_data)} rows in Marker Editor table.", function=current_function)
        debug_log(f"[{current_file} - {current_function}] Marker treeview populated with {len(self.tree_data)} rows.",
                    file=current_file,
                    version=current_version,
                    function=current_function)


    def _on_tree_double_click(self, event):
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) 
        debug_log(f"[{current_file} - {current_function}] Treeview double-clicked for editing.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        if not self.marker_tree.identify_region(event.x, event.y) == "cell":
            return 

        column_id = self.marker_tree.identify_column(event.x)
        item_id = self.marker_tree.identify_row(event.y)

        if not item_id or not column_id:
            return

        col_index = int(column_id[1:]) - 1
        if col_index < 0 or col_index >= len(self.tree_headers):
            debug_log(f"[{current_file} - {current_function}] Invalid column index {col_index} for editing.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return

        current_value = self.marker_tree.item(item_id, 'values')[col_index]

        self._start_editing_cell(item_id, col_index, initial_value=current_value)


    def _start_editing_cell(self, item, col_index, initial_value=""):
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) 

        for widget in self.marker_tree.winfo_children():
            if isinstance(widget, ttk.Entry) and widget.winfo_name() == "cell_editor":
                widget.destroy()

        entry_editor = ttk.Entry(self.marker_tree, style="Markers.TEntry", name="cell_editor")
        entry_editor.insert(0, initial_value)
        entry_editor.focus_force()

        x, y, width, height = self.marker_tree.bbox(item, self.marker_tree["columns"][col_index])
        entry_editor.place(x=x, y=y, width=width, height=height)

        entry_editor.current_item = item
        entry_editor.current_col_index = col_index

        def on_edit_complete_and_navigate(event, navigate_direction=None):
            new_value = entry_editor.get()
            entry_editor.destroy()

            current_values = list(self.marker_tree.item(item, 'values'))
            current_values[col_index] = new_value
            self.marker_tree.item(item, values=current_values)

            row_idx = int(item) 
            if row_idx < len(self.tree_data):
                self.tree_data[row_idx][self.tree_headers[col_index]] = new_value
                console_log(f"Updated cell: Row {row_idx+1}, Column '{self.tree_headers[col_index]}' to '{new_value}'", function=current_function)
                debug_log(f"[{current_file} - {current_function}] Updated tree_data[{row_idx}]['{self.tree_headers[col_index]}'] to '{new_value}'.",
                            file=current_file,
                            version=current_version,
                            function=current_function)
                
                # Inform MarkersDisplayTab about the change and save
                self._update_markers_display_tab_data()
                self._save_markers_file_internally() 

            else:
                debug_log(f"[{current_file} - {current_function}] Error: Row index {row_idx} out of bounds for self.tree_data.",
                            file=current_file,
                            version=current_version,
                            function=current_function)

            if navigate_direction:
                self._navigate_cells(item, col_index, navigate_direction)

        entry_editor.bind("<Return>", lambda e: on_edit_complete_and_navigate(e, "down"))
        entry_editor.bind("<Tab>", lambda e: on_edit_complete_and_navigate(e, "right"))
        entry_editor.bind("<Shift-Tab>", lambda e: on_edit_complete_and_navigate(e, "left"))
        entry_editor.bind("<Control-Return>", lambda e: on_edit_complete_and_navigate(e, "ctrl_down"))
        entry_editor.bind("<FocusOut>", lambda e: on_edit_complete_and_navigate(e, None)) 
        entry_editor.bind("<Up>", lambda e: on_edit_complete_and_navigate(e, "up"))
        entry_editor.bind("<Down>", lambda e: on_edit_complete_and_navigate(e, "down"))
        entry_editor.bind("<Left>", lambda e: on_edit_complete_and_navigate(e, "left"))
        entry_editor.bind("<Right>", lambda e: on_edit_complete_and_navigate(e, "right"))


    def _navigate_cells(self, current_item, current_col_index, direction):
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) 
        debug_log(f"[{current_file} - {current_function}] Navigating cells.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        items = self.marker_tree.get_children()
        num_rows = len(items)
        num_cols = len(self.tree_headers)

        current_row_idx = items.index(current_item) if current_item in items else -1
        
        next_item = None
        next_col_index = -1
        initial_value_for_next_cell = "" 

        if current_row_idx == -1:
            debug_log(f"[{current_file} - {current_function}] Current item not found in tree for navigation.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return

        if direction == "down":
            next_row_idx = current_row_idx + 1
            next_col_index = current_col_index
            if next_row_idx < num_rows:
                next_item = items[next_row_idx]
        elif direction == "up": 
            next_row_idx = current_row_idx - 1
            next_col_index = current_col_index
            if next_row_idx >= 0:
                next_item = items[next_row_idx]
        elif direction == "right":
            next_col_index = current_col_index + 1
            if next_col_index < num_cols:
                next_item = current_item
            else: 
                next_row_idx = current_row_idx + 1
                if next_row_idx < num_rows:
                    next_item = items[next_row_idx]
                    next_col_index = 0 
        elif direction == "left":
            next_col_index = current_col_index - 1
            if next_col_index >= 0:
                next_item = current_item
            else: 
                next_row_idx = current_row_idx - 1
                if next_row_idx >= 0:
                    next_item = items[next_row_idx]
                    next_col_index = num_cols - 1 
        elif direction == "ctrl_down":
            next_row_idx = current_row_idx + 1
            next_col_index = current_col_index
            if next_row_idx < num_rows:
                next_item = items[next_row_idx]
                prev_cell_value = self.marker_tree.item(current_item, 'values')[current_col_index]
                initial_value_for_next_cell = self._increment_string_with_trailing_digits(prev_cell_value)
            else:
                debug_log(f"[{current_file} - {current_function}] Cannot Ctrl+Enter: No row below.",
                            file=current_file,
                            version=current_version,
                            function=current_function)
                return

        if next_item is not None and next_col_index != -1:
            if direction != "ctrl_down":
                try:
                    next_item_values = self.marker_tree.item(next_item, 'values')
                    if 0 <= next_col_index < len(next_item_values):
                        initial_value_for_next_cell = next_item_values[next_col_index]
                    else:
                        debug_log(f"[{current_file} - {current_function}] Next column index {next_col_index} out of bounds for next item values. Setting empty.",
                                    file=current_file,
                                    version=current_version,
                                    function=current_function)
                        initial_value_for_next_cell = "" 
                except Exception as e:
                    debug_log(f"[{current_file} - {current_function}] Error getting initial value for next cell: {e}. Setting empty.",
                                file=current_file,
                                version=current_version,
                                function=current_function)
                    initial_value_for_next_cell = "" 

            self.marker_tree.focus(next_item)
            self.marker_tree.selection_set(next_item)
            self.app_instance.after(10, lambda: self._start_editing_cell(next_item, next_col_index, initial_value_for_next_cell))
        else:
            debug_log(f"[{current_file} - {current_function}] No cell to navigate to in direction: {direction}",
                        file=current_file,
                        version=current_version,
                        function=current_function)


    def _increment_string_with_trailing_digits(self, text):
        match = re.search(r'(\d+)$', text)
        if match:
            num_str = match.group(1)
            num_int = int(num_str)
            incremented_num = num_int + 1
            new_num_str = str(incremented_num).zfill(len(num_str))
            return text[:-len(num_str)] + new_num_str
        return text


    def _on_tree_header_click(self, event):
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) 
        debug_log(f"[{current_file} - {current_function}] Treeview header clicked for sorting.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        region = self.marker_tree.identify_region(event.x, event.y)
        if region == "heading":
            column_id = self.marker_tree.identify_column(event.x)
            col_index = int(column_id[1:]) - 1
            if col_index < 0 or col_index >= len(self.tree_headers):
                debug_log(f"[{current_file} - {current_function}] Invalid column index {col_index} for sorting.",
                            file=current_file,
                            version=current_version,
                            function=current_function)
                return

            column_name = self.tree_headers[col_index]

            if self.sort_column == column_name:
                self.sort_direction = not self.sort_direction 
            else:
                self.sort_column = column_name
                self.sort_direction = True 

            self._sort_treeview(column_name, self.sort_direction)


    def _sort_treeview(self, column_name, ascending):
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) 
        debug_log(f"[{current_file} - {current_function}] Sorting treeview by '{column_name}', ascending: {ascending}.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        def get_sort_key(item):
            value = item.get(column_name, "")
            try:
                return float(value)
            except ValueError:
                return str(value)

        self.tree_data.sort(key=get_sort_key, reverse=not ascending)

        self._populate_marker_tree()
        console_log(f"Sorted by '{column_name}' {'Ascending' if ascending else 'Descending'}.", function=current_function)


    def _load_markers_file(self):
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) 
        debug_log(f"[{current_file} - {current_function}] Loading MARKERS.CSV file (Load Marker Set button)...",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        initial_dir = os.path.dirname(self.app_instance.MARKERS_FILE_PATH) if self.app_instance and hasattr(self.app_instance, 'MARKERS_FILE_PATH') else os.getcwd()

        file_path = filedialog.askopenfilename(
            title="Load MARKERS.CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=initial_dir
        )
        if not file_path:
            console_log("ℹ️ Info: Load Marker Set cancelled.", function=current_function)
            return

        self._disable_buttons() 
        try:
            headers = []
            rows = []
            with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                headers = reader.fieldnames
                for row_data in reader:
                    rows.append(row_data)

            if headers and rows:
                self.tree_headers = headers
                self.tree_data = rows
                self.app_instance.after(0, self._populate_marker_tree) 
                self.output_csv_path = file_path 
                console_log(f"✅ Successfully loaded {len(rows)} markers from '{os.path.basename(file_path)}'.", function=current_function)
                debug_log(f"[{current_file} - {current_function}] Loaded {len(rows)} markers from '{file_path}'.",
                            file=current_file,
                            version=current_version,
                            function=current_function)
                
                self._update_markers_display_tab_data()
                self._save_markers_file_internally()
            else:
                console_log("ℹ️ Info: Selected CSV file is empty or has no data.", function=current_function)
                debug_log(f"[{current_file} - {current_function}] Selected CSV file '{file_path}' is empty.",
                            file=current_file,
                            version=current_version,
                            function=current_function)
                self.tree_headers = []
                self.tree_data = []
                self.app_instance.after(0, self._populate_marker_tree) 
        except Exception as e:
            console_log(f"❌ Error loading CSV: {e}", function=current_function)
            debug_log(f"[{current_file} - {current_function}] Error loading CSV from '{file_path}': {e}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        finally:
            self.app_instance.after(0, self._enable_buttons) 


    def _save_markers_file_internally(self): 
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) 
        debug_log(f"[{current_file} - {current_function}] Saving current marker data to internal MARKERS.CSV...",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        if not self.tree_data:
            debug_log(f"[{current_file} - {current_function}] No data to save to internal MARKERS.CSV. Creating empty file if headers exist.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            if self.tree_headers:
                markers_file_path = self.app_instance.MARKERS_FILE_PATH
                output_dir = os.path.dirname(markers_file_path)
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    with open(markers_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=self.tree_headers)
                        writer.writeheader()
                    self.output_csv_path = markers_file_path
                    console_log(f"✅ Auto-saved empty MARKERS.CSV with headers to '{os.path.basename(markers_file_path)}'.", function=current_function)
                    debug_log(f"[{current_file} - {current_function}] Auto-saved empty MARKERS.CSV with headers to '{markers_file_path}'.",
                                file=current_file,
                                version=current_version,
                                function=current_function)
                except Exception as e:
                    console_log(f"❌ Error creating empty internal MARKERS.CSV: {e}", function=current_function)
                    debug_log(f"[{current_file} - {current_function}] Error creating empty internal MARKERS.CSV at '{markers_file_path}': {e}",
                                file=current_file,
                                version=current_version,
                                function=current_function)
            return

        markers_file_path = self.app_instance.MARKERS_FILE_PATH
        output_dir = os.path.dirname(markers_file_path) 

        if not markers_file_path:
            console_log("⚠️ Warning: Internal MARKERS.CSV path not configured. Cannot save automatically.", function=current_function)
            debug_log(f"[{current_file} - {current_function}] Internal MARKERS.CSV path not configured. Cannot save.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return

        try:
            os.makedirs(output_dir, exist_ok=True) 
            with open(markers_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.tree_headers)
                writer.writeheader()
                writer.writerows(self.tree_data)
            self.output_csv_path = markers_file_path 
            console_log(f"✅ Auto-saved MARKERS.CSV to '{os.path.basename(markers_file_path)}'.", function=current_function)
            debug_log(f"[{current_file} - {current_function}] Auto-saved MARKERS.CSV to '{markers_file_path}'.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            
            # --- NEW: Explicitly trigger reload in MarkersDisplayTab after saving ---
            self._update_markers_display_tab_data() # This will now call load_markers_from_file on the display tab
            # --- END NEW ---

        except Exception as e:
            console_log(f"❌ Error auto-saving internal MARKERS.CSV: {e}", function=current_function)
            debug_log(f"[{current_file} - {current_function}] Error auto-saving internal MARKERS.CSV to '{markers_file_path}': {e}",
                        file=current_file,
                        version=current_version,
                        function=current_function)


    def _save_open_air_csv(self):
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) 
        debug_log(f"[{current_file} - {current_function}] Saving Markers as Open_Air_Markers.csv...",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        if not self.tree_data:
            console_log("ℹ️ Info: No data to save.", function=current_function)
            return

        scan_name = ""
        if self.app_instance and hasattr(self.app_instance, 'scan_name_var'):
            scan_name = self.app_instance.scan_name_var.get().strip()
            if scan_name:
                scan_name = f" - {scan_name}" 

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")

        default_filename = f"Open_Air_Markers{scan_name} - {timestamp}.csv"

        initial_dir = os.path.dirname(self.app_instance.MARKERS_FILE_PATH) if self.app_instance and hasattr(self.app_instance, 'MARKERS_FILE_PATH') else os.getcwd()

        file_path = filedialog.asksaveasfilename(
            title="Save Markers as Open Air CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=initial_dir, 
            initialfile=default_filename
        )
        if not file_path:
            console_log("ℹ️ Info: Save As cancelled.", function=current_function)
            return

        self._disable_buttons() 
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.tree_headers)
                writer.writeheader()
                writer.writerows(self.tree_data)
            console_log(f"✅ Successfully saved markers to '{os.path.basename(file_path)}'.", function=current_function)
            debug_log(f"[{current_file} - {current_function}] Saved markers to '{file_path}'.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            
            # --- NEW: Explicitly trigger reload in MarkersDisplayTab after saving to a *new* file ---
            # This is important if "Save As" changes the primary MARKERS.CSV
            # If the user saves to a *different* file, the MarkersDisplayTab should still reflect the main MARKERS.CSV
            # So, we should trigger a reload of the *main* MARKERS.CSV.
            self._update_markers_display_tab_data() # This will call load_markers_from_file on the display tab
            # --- END NEW ---

        except Exception as e:
            console_log(f"❌ Error saving markers: {e}", function=current_function)
            debug_log(f"[{current_file} - {current_function}] Error saving markers to '{file_path}': {e}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        finally:
            self.app_instance.after(0, self._enable_buttons) 


    def _disable_buttons(self):
        self.load_csv_button.config(state=tk.DISABLED)
        self.load_ias_html_button.config(state=tk.DISABLED)
        self.load_wwb_shw_button.config(state=tk.DISABLED)
        self.load_sb_pdf_button.config(state=tk.DISABLED)
        self.save_open_air_button.config(state=tk.DISABLED)


    def _enable_buttons(self):
        self.load_csv_button.config(state=tk.NORMAL)
        self.load_ias_html_button.config(state=tk.NORMAL)
        self.load_wwb_shw_button.config(state=tk.NORMAL)
        self.load_sb_pdf_button.config(state=tk.NORMAL)
        self.save_open_air_button.config(state=tk.NORMAL)


    def _initiate_conversion(self, file_type):
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) 
        debug_log(f"[{current_file} - {current_function}] Initiating conversion for type: {file_type}.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        file_types_map = {
            "HTML": [("HTML files", "*.html"), ("All files", "*.*")],
            "SHW": [("SHW files", "*.shw"), ("XML files", "*.xml"), ("All files", "*.*")],
            "PDF": [("PDF files", "*.pdf"), ("All files", "*.*")]
        }
        title_map = {
            "HTML": "Select IAS HTML Report File",
            "SHW": "Select WWB.shw Report File",
            "PDF": "Select Soundbase PDF Report File"
        }

        file_path = filedialog.askopenfilename(
            title=title_map.get(file_type, "Select Report File"),
            filetypes=file_types_map.get(file_type, [("All files", "*.*")])
        )
        if not file_path:
            console_log(f"ℹ️ Info: {file_type} conversion cancelled.", function=current_function)
            return

        self._disable_buttons()
        conversion_thread = threading.Thread(target=self._perform_conversion, args=(file_path, file_type))
        conversion_thread.daemon = True
        conversion_thread.start()


    def _perform_conversion(self, file_path, file_type):
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) 
        console_log(f"Processing '{os.path.basename(file_path)}'...", function=current_function)
        debug_log(f"[{current_file} - {current_function}] Performing conversion for {file_path} (type: {file_type}) in thread.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        headers = []
        rows = []
        error_message = None
        # output_csv_path is now handled by _save_markers_file_internally

        try:
            file_name = os.path.basename(file_path)
            # No longer using output_dir from app_instance for MARKERS.CSV operations
            # Instead, ensure the directory for MARKERS_FILE_PATH exists
            markers_dir = os.path.dirname(self.app_instance.MARKERS_FILE_PATH)
            os.makedirs(markers_dir, exist_ok=True)

            if file_type == 'HTML':
                console_log("Detected HTML file. Converting...", function=current_function)
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                headers, rows = convert_html_report_to_csv(html_content, console_print_func=console_log) 
            elif file_type == 'SHW':
                console_log("Detected SHW file. Converting...", function=current_function)
                headers, rows = generate_csv_from_shw(file_path, console_print_func=console_log) 
            elif file_type == 'PDF':
                console_log("Detected PDF file. Converting...", function=current_function)
                headers, rows = convert_pdf_report_to_csv(file_path, console_print_func=console_log) 
            else:
                error_message = f"Unsupported file type: {file_type}. This should not happen."
                console_log(f"❌ {error_message}", function=current_function)
                debug_log(f"Unsupported file type: {file_type}",
                            file=current_file,
                            version=current_version,
                            function=current_function)

            if not error_message and headers and rows:
                # Update the Treeview with the new data
                self.tree_headers = headers
                self.tree_data = rows
                self.app_instance.after(0, self._populate_marker_tree) # Update GUI on main thread

                # Call the method on the main App instance to update the Markers Display tab
                self._update_markers_display_tab_data()
                # NEW: Save the converted data to MARKERS.CSV immediately
                self._save_markers_file_internally() 

                console_log(f"\n✅ Successfully converted '{file_name}' and saved to MARKERS.CSV.", function=current_function)
            else:
                error_message = f"No relevant data could be extracted from '{file_name}'. CSV file was not created."
                console_log(f"🚫 {error_message}", function=current_function)

        except FileNotFoundError as e:
            error_message = f"File not found: {e}"
            console_log(f"❌ {error_message}", function=current_function)
        except ET.ParseError as e:
            error_message = f"Error parsing XML (SHW) file: {e}"
            console_log(f"❌ {error_message}", function=current_function)
        except Exception as e:
            error_message = f"An unexpected error occurred during conversion: {e}"
            console_log(f"❌ {error_message}", function=current_function)
        
        finally:
            if error_message:
                debug_log(f"Conversion failed for {file_name}: {error_message}",
                            file=current_file,
                            version=current_version,
                            function=current_function)
                self.app_instance.after(0, lambda: console_log(f"❌ Conversion failed for {file_name}. See Report Converter Log for details.", function=current_function))
            self.app_instance.after(0, self._enable_buttons)


    def _update_markers_display_tab_data(self):
        """
        Function Description:
        This method is called to propagate the current marker data
        from the Report Converter Tab (marker editor) to the Markers Display Tab.
        It finds the MarkersDisplayTab instance and calls its `load_markers_from_file` method.
        This ensures the display tab always reloads from the saved MARKERS.CSV.

        Inputs to this function:
        - None
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) 
        debug_log(f"[{current_file} - {current_function}] Attempting to tell Markers Display Tab to reload its data from file...",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        if self.app_instance and hasattr(self.app_instance, 'markers_parent_tab') and \
           hasattr(self.app_instance.markers_parent_tab, 'markers_display_tab') and \
           self.app_instance.markers_parent_tab.markers_display_tab is not None:
            try:
                # NEW: Call MarkersDisplayTab's load_markers_from_file() to make it read from disk
                self.app_instance.markers_parent_tab.markers_display_tab.load_markers_from_file()
                console_log("✅ Markers Display Tab signaled to reload data.", function=current_function)
                debug_log(f"[{current_file} - {current_function}] Signaled MarkersDisplayTab to reload its data from file. 🎉",
                            file=current_file,
                            version=current_version,
                            function=current_function)
            except Exception as e:
                console_log(f"❌ Error signaling Markers Display Tab to reload: {e}", function=current_function)
                debug_log(f"[{current_file} - {current_function}] Error signaling MarkersDisplayTab to reload: {e}. Fucking hell, what went wrong now?!",
                            file=current_file,
                            version=current_version,
                            function=current_function)
        else:
            console_log("⚠️ Warning: Markers Display Tab instance not found or accessible in app_instance. Cannot signal reload.", function=current_function)
            debug_log(f"[{current_file} - {current_function}] MarkersDisplayTab instance not found in app_instance. Current app_instance attributes: {dir(self.app_instance)}. This is a goddamn mess!",
                        file=current_file,
                        version=current_version,
                        function=current_function)

    def _on_tab_selected(self, event):
        """
        Callback when this tab is selected. Ensures the marker tree is populated
        if MARKERS.CSV exists in the designated internal data folder.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) 
        console_log("ReportConverterTab selected. Checking for MARKERS.CSV in internal data folder...", function=current_function)
        debug_log(f"[{current_file} - {current_function}] ReportConverterTab selected. Checking for MARKERS.CSV in internal data folder...",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        markers_file_path = None
        if self.app_instance and hasattr(self.app_instance, 'MARKERS_FILE_PATH'):
            markers_file_path = self.app_instance.MARKERS_FILE_PATH
            debug_log(f"[{current_file} - {current_function}] Attempting to load MARKERS.CSV from configured internal path: {markers_file_path}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        else:
            console_log("⚠️ Warning: App instance or MARKERS_FILE_PATH not available. Cannot check for MARKERS.CSV.", function=current_function)
            debug_log(f"[{current_file} - {current_function}] App instance or MARKERS_FILE_PATH not available. Cannot check for MARKERS.CSV.",
                        file=current_file,
                        version=current_version,
                        function=current_function)

        if markers_file_path and os.path.exists(markers_file_path):
            debug_log(f"[{current_file} - {current_function}] MARKERS.CSV found at: {markers_file_path}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            try:
                headers = []
                rows = []
                with open(markers_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    headers = reader.fieldnames
                    for row_data in reader:
                        rows.append(row_data)

                if headers and rows:
                    self.tree_headers = headers
                    self.tree_data = rows
                    self._populate_marker_tree()
                    self.output_csv_path = markers_file_path 
                    console_log(f"✅ Displayed {len(rows)} markers from MARKERS.CSV.", function=current_function)
                else:
                    console_log("ℹ️ Info: The MARKERS.CSV file was found but contains no data.", function=current_function)
                    self.tree_headers = []
                    self.tree_data = []
                    self._populate_marker_tree() 
            except Exception as e:
                console_log(f"❌ Error loading MARKERS.CSV for display: {e}", function=current_function)
                debug_log(f"[{current_file} - {current_function}] Error loading MARKERS.CSV for display: {e}",
                            file=current_file,
                            version=current_version,
                            function=current_function)
                self.tree_headers = []
                self.tree_data = []
                self._populate_marker_tree() 
        else:
            console_log("ℹ️ Info: MARKERS.CSV not found in internal data folder. Table is empty.", function=current_function)
            self.tree_headers = []
            self.tree_data = []
            self._populate_marker_tree()