# tabs/Markers/tab_markers_child_import_and_edit.py
#
# This file manages the Report Converter tab in the GUI, handling
# functionality to convert spectrum analyzer report files (HTML, SHW, or Soundbase PDF)
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
# Version 20250801.1028.1 (Updated header and imports for new folder structure)

current_version = "20250801.1028.1" # this variable should always be defined below the header to make the debugging better

import tkinter as tk
from tkinter import filedialog, ttk
import os
import csv
import xml.etree.ElementTree as ET
import sys
import inspect
import threading
import json # Import json for serializing/deserializing row data for Treeview editing
import datetime # NEW: Import datetime for timestamp
import re # NEW: Import regex for Ctrl+Enter logic

# Import the new report converter utility functions - CORRECTED PATHS
from process_math.report_converter_utils import convert_html_report_to_csv, generate_csv_from_shw, convert_pdf_report_to_csv
from src.gui_elements import TextRedirector # Keep TextRedirector for console output
from utils.utils_instrument_control import debug_print # Import debug_print

class ReportConverterTab(ttk.Frame):
    """
    A Tkinter Frame that provides functionality to convert spectrum analyzer
    report files (HTML, SHW, or Soundbase PDF) into CSV format.
    It now also displays the converted data in an editable, sortable table
    and allows loading/saving of MARKERS.CSV files.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the ReportConverterTab.

        Inputs:
            master (tk.Widget): The parent widget.
            app_instance (App): The main application instance, used for accessing
                                shared state like output directory.
            console_print_func (function, optional): Function to use for console output.
            **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/tab_markers_child_report_converter.py - {current_version}"
        debug_print("Initializing ReportConverterTab...", file=current_file, function=current_function, console_print_func=console_print_func)

        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else print # Use provided func or default print
        self.output_csv_path = None # To store the path of the last generated/loaded CSV

        self.tree_headers = [] # Stores current headers of the Treeview
        self.tree_data = []    # Stores current data of the Treeview (list of dicts)
        self.sort_column = None # To keep track of the last sorted column
        self.sort_direction = False # True for ascending, False for descending

        self._create_widgets()


    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Report Converter tab.
        This includes conversion buttons, the new editable/sortable Treeview,
        and Load/Save/Save As buttons for marker files.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/tab_markers_child_report_converter.py - {current_version}"
        debug_print("Creating ReportConverterTab widgets.", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Configure grid for responsiveness
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Load Markers box (fixed height)
        self.grid_rowconfigure(1, weight=1) # Marker Editor table (expands)
        self.grid_rowconfigure(2, weight=0) # Save button (fixed height)


        # --- Load Markers Frame (Top) ---
        # (2025-07-31) Change: Renamed label frame to "Load Markers".
        load_markers_frame = ttk.LabelFrame(self, text="Load Markers", padding=(5,5,5,5), style='Dark.TLabelframe')
        load_markers_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        load_markers_frame.grid_columnconfigure(0, weight=1)
        load_markers_frame.grid_columnconfigure(1, weight=1)
        load_markers_frame.grid_columnconfigure(2, weight=1)
        load_markers_frame.grid_columnconfigure(3, weight=1) # Added column for Load Marker Set button

        # (2025-07-31) Change: Renamed button text and updated commands.
        self.load_csv_button = ttk.Button(load_markers_frame, text="Load CSV Marker Set", command=self._load_markers_file, style='Green.TButton')
        self.load_csv_button.grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        self.load_ias_html_button = ttk.Button(load_markers_frame, text="Load IAS HTML", command=lambda: self._initiate_conversion("HTML"), style='Blue.TButton')
        self.load_ias_html_button.grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        self.load_wwb_shw_button = ttk.Button(load_markers_frame, text="Load WWB.shw", command=lambda: self._initiate_conversion("SHW"), style='Blue.TButton')
        self.load_wwb_shw_button.grid(row=0, column=2, padx=2, pady=2, sticky="ew")

        self.load_sb_pdf_button = ttk.Button(load_markers_frame, text="Load SB PDF", command=lambda: self._initiate_conversion("PDF"), style='Blue.TButton')
        self.load_sb_pdf_button.grid(row=0, column=3, padx=2, pady=2, sticky="ew")


        # --- Marker Editor Table (Middle) ---
        marker_table_frame = ttk.LabelFrame(self, text="Marker Editor", padding=(5,5,5,5), style='Dark.TLabelframe')
        marker_table_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        marker_table_frame.grid_columnconfigure(0, weight=1)
        marker_table_frame.grid_rowconfigure(0, weight=1)

        # Treeview for displaying and editing marker data
        self.marker_tree = ttk.Treeview(marker_table_frame, show="headings", style="Treeview")
        self.marker_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Scrollbars for the Treeview
        tree_yscroll = ttk.Scrollbar(marker_table_frame, orient="vertical", command=self.marker_tree.yview)
        tree_yscroll.grid(row=0, column=1, sticky="ns")
        self.marker_tree.configure(yscrollcommand=tree_yscroll.set)

        tree_xscroll = ttk.Scrollbar(marker_table_frame, orient="horizontal", command=self.marker_tree.xview)
        tree_xscroll.grid(row=1, column=0, sticky="ew")
        self.marker_tree.configure(xscrollcommand=tree_xscroll.set)

        # Bindings for editing and sorting
        self.marker_tree.bind("<Double-1>", self._on_tree_double_click) # Double-click to edit
        self.marker_tree.bind("<ButtonRelease-1>", self._on_tree_header_click) # Click header to sort


        # --- Save Markers as Open Air.csv Button (Bottom) ---
        # (2025-07-31) Change: Replaced previous save buttons with a single "Save Markers as Open Air.csv" button.
        self.save_open_air_button = ttk.Button(self, text="Save Markers as Open Air.csv", command=self._save_open_air_csv, style='Orange.TButton')
        self.save_open_air_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")


    def _populate_marker_tree(self):
        """
        Populates the Treeview with the data stored in self.tree_data.
        Configures columns and inserts rows.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/tab_markers_child_report_converter.py - {current_version}"
        debug_print("Populating marker treeview.", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Clear existing treeview content
        self.marker_tree.delete(*self.marker_tree.get_children())

        if not self.tree_headers:
            self.marker_tree["columns"] = ()
            self.console_print_func("ℹ️ No headers available to display in Marker Editor table.")
            return

        self.marker_tree["columns"] = self.tree_headers
        for col_name in self.tree_headers:
            self.marker_tree.heading(col_name, text=col_name, anchor="w")
            self.marker_tree.column(col_name, width=ttk.Style().lookup("Treeview", "rowheight") * 5, stretch=tk.YES) # Default width

        for i, row_data in enumerate(self.tree_data):
            # Convert dictionary values to a list in the order of headers
            values = [row_data.get(header, "") for header in self.tree_headers]
            self.marker_tree.insert("", "end", iid=str(i), values=values, tags=('editable',))

        self.console_print_func(f"✅ Displayed {len(self.tree_data)} rows in Marker Editor table.")


    def _on_tree_double_click(self, event):
        """
        Handles double-click events on the Treeview to enable cell editing.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/tab_markers_child_report_converter.py - {current_version}"
        debug_print("Treeview double-clicked for editing.", file=current_file, function=current_function, console_print_func=self.console_print_func)

        if not self.marker_tree.identify_region(event.x, event.y) == "cell":
            return # Only allow editing on cells

        column_id = self.marker_tree.identify_column(event.x)
        item_id = self.marker_tree.identify_row(event.y)

        if not item_id or not column_id:
            return

        # Get column index (e.g., #1, #2, ...)
        col_index = int(column_id[1:]) - 1
        if col_index < 0 or col_index >= len(self.tree_headers):
            debug_print(f"Invalid column index {col_index} for editing.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            return

        # Get current value
        current_value = self.marker_tree.item(item_id, 'values')[col_index]

        self._start_editing_cell(item_id, col_index, initial_value=current_value)


    def _start_editing_cell(self, item, col_index, initial_value=""):
        """
        Creates and places an Entry widget for cell editing at the specified item and column.
        Binds navigation keys to the entry widget.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/tab_markers_child_report_converter.py - {current_version}"

        # Ensure no other editor is open
        for widget in self.marker_tree.winfo_children():
            if isinstance(widget, ttk.Entry) and widget.winfo_name() == "cell_editor":
                widget.destroy()

        entry_editor = ttk.Entry(self.marker_tree, style="Markers.TEntry", name="cell_editor")
        entry_editor.insert(0, initial_value)
        entry_editor.focus_force()

        x, y, width, height = self.marker_tree.bbox(item, self.marker_tree["columns"][col_index])
        entry_editor.place(x=x, y=y, width=width, height=height)

        # Store current item and column for navigation
        entry_editor.current_item = item
        entry_editor.current_col_index = col_index

        def on_edit_complete_and_navigate(event, navigate_direction=None):
            new_value = entry_editor.get()
            entry_editor.destroy()

            # Update the Treeview
            current_values = list(self.marker_tree.item(item, 'values'))
            current_values[col_index] = new_value
            self.marker_tree.item(item, values=current_values)

            # Update the underlying data model (self.tree_data)
            row_idx = int(item) # iid is the row index
            if row_idx < len(self.tree_data):
                self.tree_data[row_idx][self.tree_headers[col_index]] = new_value
                self.console_print_func(f"Updated cell: Row {row_idx+1}, Column '{self.tree_headers[col_index]}' to '{new_value}'")
                debug_print(f"Updated tree_data[{row_idx}]['{self.tree_headers[col_index]}'] to '{new_value}'.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                
                # Inform MarkersDisplayTab about the change and save
                self._update_markers_display_tab_data()
                self._save_markers_file_to_output_folder()
            else:
                debug_print(f"Error: Row index {row_idx} out of bounds for self.tree_data.", file=current_file, function=current_function, console_print_func=self.console_print_func)

            # NEW: Handle navigation after edit
            if navigate_direction:
                self._navigate_cells(item, col_index, navigate_direction)

        # Bind events to save changes and navigate
        entry_editor.bind("<Return>", lambda e: on_edit_complete_and_navigate(e, "down"))
        entry_editor.bind("<Tab>", lambda e: on_edit_complete_and_navigate(e, "right"))
        entry_editor.bind("<Shift-Tab>", lambda e: on_edit_complete_and_navigate(e, "left"))
        entry_editor.bind("<Control-Return>", lambda e: on_edit_complete_and_navigate(e, "ctrl_down"))
        entry_editor.bind("<FocusOut>", lambda e: on_edit_complete_and_navigate(e, None)) # Save on focus out without navigation
        # NEW: Bind arrow keys
        entry_editor.bind("<Up>", lambda e: on_edit_complete_and_navigate(e, "up"))
        entry_editor.bind("<Down>", lambda e: on_edit_complete_and_navigate(e, "down"))
        entry_editor.bind("<Left>", lambda e: on_edit_complete_and_navigate(e, "left"))
        entry_editor.bind("<Right>", lambda e: on_edit_complete_and_navigate(e, "right"))


    def _navigate_cells(self, current_item, current_col_index, direction):
        """
        Navigates to the next/previous cell based on the direction and starts editing it.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/tab_markers_child_report_converter.py - {current_version}"

        items = self.marker_tree.get_children()
        num_rows = len(items)
        num_cols = len(self.tree_headers)

        current_row_idx = items.index(current_item) if current_item in items else -1
        
        next_item = None
        next_col_index = -1
        initial_value_for_next_cell = "" # Initialize to empty string by default

        if current_row_idx == -1:
            debug_print("Current item not found in tree for navigation.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            return

        if direction == "down":
            next_row_idx = current_row_idx + 1
            next_col_index = current_col_index
            if next_row_idx < num_rows:
                next_item = items[next_row_idx]
        elif direction == "up": # NEW: Up arrow navigation
            next_row_idx = current_row_idx - 1
            next_col_index = current_col_index
            if next_row_idx >= 0:
                next_item = items[next_row_idx]
        elif direction == "right":
            next_col_index = current_col_index + 1
            if next_col_index < num_cols:
                next_item = current_item
            else: # Wrap to next row
                next_row_idx = current_row_idx + 1
                if next_row_idx < num_rows:
                    next_item = items[next_row_idx]
                    next_col_index = 0 # First column of next row
        elif direction == "left":
            next_col_index = current_col_index - 1
            if next_col_index >= 0:
                next_item = current_item
            else: # Wrap to previous row
                next_row_idx = current_row_idx - 1
                if next_row_idx >= 0:
                    next_item = items[next_row_idx]
                    next_col_index = num_cols - 1 # Last column of previous row
        elif direction == "ctrl_down":
            next_row_idx = current_row_idx + 1
            next_col_index = current_col_index
            if next_row_idx < num_rows:
                next_item = items[next_row_idx]
                # Get value from cell above for Ctrl+Enter logic
                prev_cell_value = self.marker_tree.item(current_item, 'values')[current_col_index]
                initial_value_for_next_cell = self._increment_string_with_trailing_digits(prev_cell_value)
            else:
                debug_print("Cannot Ctrl+Enter: No row below.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                return

        if next_item is not None and next_col_index != -1:
            # Retrieve the value of the target cell if it's not a Ctrl+Enter (which sets its own initial_value)
            if direction != "ctrl_down":
                try:
                    # Get the values for the next item (row)
                    next_item_values = self.marker_tree.item(next_item, 'values')
                    # Ensure the column index is valid for the next item's values
                    if 0 <= next_col_index < len(next_item_values):
                        initial_value_for_next_cell = next_item_values[next_col_index]
                    else:
                        debug_print(f"Next column index {next_col_index} out of bounds for next item values. Setting empty.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                        initial_value_for_next_cell = "" # Fallback to empty string
                except Exception as e:
                    debug_print(f"Error getting initial value for next cell: {e}. Setting empty.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                    initial_value_for_next_cell = "" # Fallback to empty string on error

            self.marker_tree.focus(next_item)
            self.marker_tree.selection_set(next_item)
            # Use app_instance.after to ensure the GUI update happens on the main thread
            self.app_instance.after(10, lambda: self._start_editing_cell(next_item, next_col_index, initial_value_for_next_cell))
        else:
            debug_print(f"No cell to navigate to in direction: {direction}", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def _increment_string_with_trailing_digits(self, text):
        """
        Increments a string that ends with digits by 1.
        e.g., "Device 01" -> "Device 02", "Item 10" -> "Item 11".
        If no trailing digits, returns the original text.
        """
        match = re.search(r'(\d+)$', text) # Find trailing digits
        if match:
            num_str = match.group(1)
            num_int = int(num_str)
            incremented_num = num_int + 1
            # Reconstruct with leading zeros if necessary
            new_num_str = str(incremented_num).zfill(len(num_str))
            return text[:-len(num_str)] + new_num_str
        return text


    def _on_tree_header_click(self, event):
        """
        Handles clicks on Treeview headers to sort the data.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/tab_markers_child_report_converter.py - {current_version}"
        debug_print("Treeview header clicked for sorting.", file=current_file, function=current_function, console_print_func=self.console_print_func)

        region = self.marker_tree.identify_region(event.x, event.y)
        if region == "heading":
            column_id = self.marker_tree.identify_column(event.x)
            # Convert column_id (e.g., #1) to column name
            col_index = int(column_id[1:]) - 1
            if col_index < 0 or col_index >= len(self.tree_headers):
                debug_print(f"Invalid column index {col_index} for sorting.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                return

            column_name = self.tree_headers[col_index]

            # Determine sort direction
            if self.sort_column == column_name:
                self.sort_direction = not self.sort_direction # Toggle direction
            else:
                self.sort_column = column_name
                self.sort_direction = True # Default to ascending for new column

            self._sort_treeview(column_name, self.sort_direction)


    def _sort_treeview(self, column_name, ascending):
        """
        Sorts the Treeview data by the specified column.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/tab_markers_child_report_converter.py - {current_version}"
        debug_print(f"Sorting treeview by '{column_name}', ascending: {ascending}.", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Sort the underlying data (self.tree_data)
        def get_sort_key(item):
            value = item.get(column_name, "")
            try:
                # Try to convert to float for numerical sorting
                return float(value)
            except ValueError:
                # Otherwise, treat as string
                return str(value)

        self.tree_data.sort(key=get_sort_key, reverse=not ascending)

        # Repopulate the treeview with sorted data
        self._populate_marker_tree()
        self.console_print_func(f"Sorted by '{column_name}' {'Ascending' if ascending else 'Descending'}.")


    def _load_markers_file(self):
        """
        Prompts the user to select a MARKERS.CSV file and loads its content
        into the Treeview. This is for the "Load CSV Marker Set" button.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/tab_markers_child_report_converter.py - {current_version}"
        debug_print("Loading MARKERS.CSV file (Load Marker Set button)...", file=current_file, function=current_function, console_print_func=self.console_print_func)

        file_path = filedialog.askopenfilename(
            title="Load MARKERS.CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=self.app_instance.output_folder_var.get() if self.app_instance else os.getcwd()
        )
        if not file_path:
            self.console_print_func("ℹ️ Info: Load Marker Set cancelled.")
            return

        self._disable_buttons() # Disable buttons during load
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
                self.app_instance.after(0, self._populate_marker_tree) # Update GUI on main thread
                self.output_csv_path = file_path # Set this as the current working path
                self.console_print_func(f"✅ Successfully loaded {len(rows)} markers from '{os.path.basename(file_path)}'.")
                debug_print(f"Loaded {len(rows)} markers from '{file_path}'.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                # Inform MarkersDisplayTab about the new data
                self._update_markers_display_tab_data()
                # NEW: Save the loaded data to MARKERS.CSV in the output folder
                self._save_markers_file_to_output_folder()
            else:
                self.console_print_func("ℹ️ Info: Selected CSV file is empty or has no data.")
                debug_print(f"Selected CSV file '{file_path}' is empty.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                self.tree_headers = []
                self.tree_data = []
                self.app_instance.after(0, self._populate_marker_tree) # Clear the treeview
        except Exception as e:
            self.console_print_func(f"❌ Error loading CSV: {e}")
            debug_print(f"Error loading CSV from '{file_path}': {e}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        finally:
            self.app_instance.after(0, self._enable_buttons) # Re-enable buttons


    def _save_markers_file_to_output_folder(self):
        """
        Saves the current Treeview content to MARKERS.CSV in the application's output folder.
        This is an internal helper function called after edits, loads, or conversions.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/tab_markers_child_report_converter.py - {current_version}"
        debug_print("Saving current marker data to MARKERS.CSV in output folder...", file=current_file, function=current_function, console_print_func=self.console_print_func)

        if not self.tree_data:
            debug_print("No data to save to MARKERS.CSV in output folder.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            return

        output_dir = self.app_instance.output_folder_var.get()
        if not output_dir:
            self.console_print_func("⚠️ Warning: Output folder not configured. Cannot save MARKERS.CSV automatically.")
            debug_print("Output folder not configured. Cannot save MARKERS.CSV.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            return

        markers_file_path = os.path.join(output_dir, "MARKERS.CSV")
        try:
            os.makedirs(output_dir, exist_ok=True) # Ensure output directory exists
            with open(markers_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.tree_headers)
                writer.writeheader()
                writer.writerows(self.tree_data)
            self.output_csv_path = markers_file_path # Update the current working path
            self.console_print_func(f"✅ Auto-saved MARKERS.CSV to '{os.path.basename(markers_file_path)}'.")
            debug_print(f"Auto-saved MARKERS.CSV to '{markers_file_path}'.", file=current_file, function=current_function, console_print_func=self.console_print_func)
        except Exception as e:
            self.console_print_func(f"❌ Error auto-saving MARKERS.CSV: {e}")
            debug_print(f"Error auto-saving MARKERS.CSV to '{markers_file_path}': {e}", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def _save_open_air_csv(self):
        """
        Prompts the user for a new file path and saves the current Treeview content
        to "Open_Air_Markers - [Scan Name] - YYYYMMDD_HHMM.csv".
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/tab_markers_child_report_converter.py - {current_version}"
        debug_print("Saving Markers as Open_Air_Markers.csv...", file=current_file, function=current_function, console_print_func=self.console_print_func)

        if not self.tree_data:
            self.console_print_func("ℹ️ Info: No data to save.")
            return

        # Get scan name from app_instance if available, otherwise default
        scan_name = ""
        if self.app_instance and hasattr(self.app_instance, 'scan_name_var'):
            scan_name = self.app_instance.scan_name_var.get().strip()
            if scan_name:
                scan_name = f" - {scan_name}" # Add " - " prefix if scan name exists

        # Get current date and time for timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")

        # Construct default filename
        default_filename = f"Open_Air_Markers{scan_name} - {timestamp}.csv"

        file_path = filedialog.asksaveasfilename(
            title="Save Markers as Open Air CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=self.app_instance.output_folder_var.get() if self.app_instance else os.getcwd(),
            initialfile=default_filename # Use the new default filename
        )
        if not file_path:
            self.console_print_func("ℹ️ Info: Save As cancelled.")
            return

        self._disable_buttons() # Disable buttons during save
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.tree_headers)
                writer.writeheader()
                writer.writerows(self.tree_data)
            self.console_print_func(f"✅ Successfully saved markers to '{os.path.basename(file_path)}'.")
            debug_print(f"Saved markers to '{file_path}'.", file=current_file, function=current_function, console_print_func=self.console_print_func)
        except Exception as e:
            self.console_print_func(f"❌ Error saving markers: {e}")
            debug_print(f"Error saving markers to '{file_path}': {e}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        finally:
            self.app_instance.after(0, self._enable_buttons) # Re-enable buttons


    def _disable_buttons(self):
        """Disables all conversion and marker file buttons during a process."""
        self.load_csv_button.config(state=tk.DISABLED)
        self.load_ias_html_button.config(state=tk.DISABLED)
        self.load_wwb_shw_button.config(state=tk.DISABLED)
        self.load_sb_pdf_button.config(state=tk.DISABLED)
        self.save_open_air_button.config(state=tk.DISABLED)


    def _enable_buttons(self):
        """Enables all conversion and marker file buttons after a process."""
        self.load_csv_button.config(state=tk.NORMAL)
        self.load_ias_html_button.config(state=tk.NORMAL)
        self.load_wwb_shw_button.config(state=tk.NORMAL)
        self.load_sb_pdf_button.config(state=tk.NORMAL)
        self.save_open_air_button.config(state=tk.NORMAL)


    def _initiate_conversion(self, file_type):
        """
        Initiates the file dialog and then starts the conversion in a separate thread.
        This handles "Load IAS HTML", "Load WWB.shw", and "Load SB PDF" buttons.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/tab_markers_child_report_converter.py - {current_version}"
        debug_print(f"Initiating conversion for type: {file_type}.", file=current_file, function=current_function, console_print_func=self.console_print_func)

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
            self.console_print_func(f"ℹ️ Info: {file_type} conversion cancelled.")
            return

        self._disable_buttons()
        conversion_thread = threading.Thread(target=self._perform_conversion, args=(file_path, file_type))
        conversion_thread.daemon = True
        conversion_thread.start()


    def _perform_conversion(self, file_path, file_type):
        """
        Performs the actual file conversion based on file type.
        Updates the Treeview with the converted data.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/tab_markers_child_report_converter.py - {current_version}"
        self.console_print_func(f"Processing '{os.path.basename(file_path)}'...")
        debug_print(f"Performing conversion for {file_path} (type: {file_type}) in thread.", file=current_file, function=current_function, console_print_func=self.console_print_func)

        headers = []
        rows = []
        error_message = None
        # output_csv_path is now handled by _save_markers_file_to_output_folder

        try:
            file_name = os.path.basename(file_path)
            output_dir = self.app_instance.output_folder_var.get()
            os.makedirs(output_dir, exist_ok=True) # Ensure output directory exists

            if file_type == 'HTML':
                self.console_print_func("Detected HTML file. Converting...")
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                headers, rows = convert_html_report_to_csv(html_content, console_print_func=self.console_print_func)
            elif file_type == 'SHW':
                self.console_print_func("Detected SHW file. Converting...")
                headers, rows = generate_csv_from_shw(file_path, console_print_func=self.console_print_func)
            elif file_type == 'PDF':
                self.console_print_func("Detected PDF file. Converting...")
                headers, rows = convert_pdf_report_to_csv(file_path, console_print_func=self.console_print_func)
            else:
                error_message = f"Unsupported file type: {file_type}. This should not happen."
                self.console_print_func(f"❌ {error_message}")
                debug_print(f"Unsupported file type: {file_type}", file=current_file, function=current_function, console_print_func=self.console_print_func)

            if not error_message and headers and rows:
                # Update the Treeview with the new data
                self.tree_headers = headers
                self.tree_data = rows
                self.app_instance.after(0, self._populate_marker_tree) # Update GUI on main thread

                # Call the method on the main App instance to update the Markers Display tab
                self._update_markers_display_tab_data()
                # NEW: Save the converted data to MARKERS.CSV immediately
                self._save_markers_file_to_output_folder()

                self.console_print_func(f"\n✅ Successfully converted '{file_name}' and saved to MARKERS.CSV.")
            else:
                error_message = f"No relevant data could be extracted from '{file_name}'. CSV file was not created."
                self.console_print_func(f"🚫 {error_message}")

        except FileNotFoundError as e:
            error_message = f"File not found: {e}"
            self.console_print_func(f"❌ {error_message}")
        except ET.ParseError as e:
            error_message = f"Error parsing XML (SHW) file: {e}"
            self.console_print_func(f"❌ {error_message}")
        except Exception as e:
            error_message = f"An unexpected error occurred during conversion: {e}"
            self.console_print_func(f"❌ {error_message}")
        
        finally:
            if error_message:
                debug_print(f"Conversion failed for {file_name}: {error_message}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                self.app_instance.after(0, lambda: self.app_instance._print_to_gui_console(f"❌ Conversion failed for {file_name}. See Report Converter Log for details."))
            # Removed the success message here as it's now handled after auto-save
            self.app_instance.after(0, self._enable_buttons)


    def _update_markers_display_tab_data(self):
        """
        Function Description:
        This method is called to propagate the current marker data
        from the Report Converter Tab (marker editor) to the Markers Display Tab.
        It finds the MarkersDisplayTab instance and calls its update method.

        Inputs to this function:
        - None (uses self.tree_headers and self.tree_data)

        Process of this function:
        1. Logs the attempt to update.
        2. Attempts to find the MarkersDisplayTab instance via the main application.
        3. If found, calls the MarkersDisplayTab's `update_marker_data` method
           with the current headers and data from this tab.
        4. Logs success or failure.

        Outputs of this function:
        - Triggers an update in the MarkersDisplayTab's display.

        (2025-08-01 00:30) Change: Implemented logic to push updated marker data to MarkersDisplayTab.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/tab_markers_child_report_converter.py - {current_version}"
        debug_print(f"🚫🐛 [{current_file}] Attempting to update Markers Display Tab data...",
                    file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Assuming app_instance holds a direct reference to the markers_display_tab
        # This is the most straightforward way if the main app manages these instances
        if self.app_instance and hasattr(self.app_instance, 'markers_display_tab') and self.app_instance.markers_display_tab is not None:
            try:
                # Call the new update_marker_data method on the MarkersDisplayTab instance
                self.app_instance.markers_display_tab.update_marker_data(self.tree_headers, self.tree_data)
                self.console_print_func("✅ Markers Display Tab updated successfully.")
            except Exception as e:
                self.console_print_func(f"❌ Error updating Markers Display Tab: {e}")
                debug_print(f"Error calling update_marker_data on MarkersDisplayTab: {e}. Fucking hell, what went wrong now?!",
                            file=current_file, function=current_function, console_print_func=self.console_print_func)
        else:
            self.console_print_func("⚠️ Warning: Markers Display Tab instance not found or accessible in app_instance. Cannot update display.")
            debug_print(f"MarkersDisplayTab instance not found in app_instance. Current app_instance attributes: {dir(self.app_instance)}. This is a goddamn mess!",
                        file=current_file, function=current_function, console_print_func=self.console_print_func)

    def _on_tab_selected(self, event):
        """
        Callback when this tab is selected. Ensures the marker tree is populated
        if MARKERS.CSV exists in the output folder.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = f"src/tab_markers_child_report_converter.py - {current_version}"
        self.console_print_func("ReportConverterTab selected. Checking for MARKERS.CSV in output folder...")
        debug_print("ReportConverterTab selected. Checking for MARKERS.CSV in output folder...", file=current_file, function=current_function, console_print_func=self.console_print_func)

        markers_file_path = None
        if self.app_instance and hasattr(self.app_instance, 'output_folder_var'):
            output_folder = self.app_instance.output_folder_var.get()
            if output_folder:
                markers_file_path = os.path.join(output_folder, 'MARKERS.CSV')
                debug_print(f"Attempting to load MARKERS.CSV from configured output folder: {markers_file_path}", file=current_file, function=current_function, console_print_func=self.console_print_func)
            else:
                self.console_print_func("⚠️ Warning: Output folder not configured in main app. Cannot check for MARKERS.CSV.")
                debug_print("Output folder not configured in main app. Cannot check for MARKERS.CSV.", file=current_file, function=current_function, console_print_func=self.console_print_func)
        else:
            self.console_print_func("⚠️ Warning: App instance or output_folder_var not available. Cannot check for MARKERS.CSV.")
            debug_print("App instance or output_folder_var not available. Cannot check for MARKERS.CSV.", file=current_file, function=current_function, console_print_func=self.console_print_func)

        if markers_file_path and os.path.exists(markers_file_path):
            debug_print(f"MARKERS.CSV found at: {markers_file_path}", file=current_file, function=current_function, console_print_func=self.console_print_func)
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
                    self.output_csv_path = markers_file_path # Set this as the current working path
                    self.console_print_func(f"✅ Displayed {len(rows)} markers from MARKERS.CSV.")
                else:
                    self.console_print_func("ℹ️ Info: The MARKERS.CSV file was found but contains no data.")
                    self.tree_headers = []
                    self.tree_data = []
                    self._populate_marker_tree() # Clear the treeview
            except Exception as e:
                self.console_print_func(f"❌ Error loading MARKERS.CSV for display: {e}")
                debug_print(f"Error loading MARKERS.CSV for display: {e}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                self.tree_headers = []
                self.tree_data = []
                self._populate_marker_tree() # Clear the treeview
        else:
            self.console_print_func("ℹ️ Info: MARKERS.CSV not found in output folder. Table is empty.")
            self.tree_headers = []
            self.tree_data = []
            self._populate_marker_tree() # Clear the treeview
