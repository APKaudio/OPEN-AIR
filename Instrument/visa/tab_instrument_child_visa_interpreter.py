# tabs/Instrument/tab_instrument_child_visa_interpreter.py
#
# This file defines the VisaInterpreterTab, a Tkinter Frame that provides a user-editable
# cell editor for VISA commands. It displays model names, command types, actions, and the
# commands themselves, allowing users to modify, add, or remove entries, and execute
# selected commands directly on a connected instrument.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250821.175600.1
# FIXED: The Treeview now correctly displays all 7 columns of data from the updated file.
#        The cell editing functionality has also been updated to handle these new columns.

import tkinter as tk
from tkinter import ttk
import os
import inspect
from datetime import datetime
import threading
import time

from display.debug_logic import debug_log
from display.console_logic import console_log
from src.program_style import COLOR_PALETTE
from ref.ref_file_paths import VISA_COMMANDS_FILE_PATH
from .utils_visa_interpreter_files import initialize_data_file_and_load, save_visa_commands_data
from .utils_visa_interpreter_commands import VisaCommandExecutor

# --- Versioning ---
w = 20250821
x_str = '175600'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"{w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"


class VisaInterpreterTab(ttk.Frame):
    """
    VisaInterpreterTab provides a user-friendly interface for executing and managing
    VISA commands. It presents a treeview of commands, allowing for direct editing
    and execution on a connected instrument.
    """
    def __init__(self, parent, app_instance, console_print_func, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func
        self.data = []
        self.sort_direction = {}
        self.last_selected_item = None
        
        # Instantiate the new command executor class
        self.command_executor = VisaCommandExecutor(app_instance, console_print_func)
        
        self.create_widgets()
        self.setup_layout()
        self.bind_events()
        
        # Call file utility to handle all file-related logic
        self.data = initialize_data_file_and_load()
        self.load_data_to_treeview()
        self._set_ui_initial_state()

        self.app_instance.bind("<<ConnectionStatusChanged>>", self._handle_connection_status_change_event)
        self._handle_connection_status_change_event()
        
        current_function = inspect.currentframe().f_code.co_name
        debug_log("VisaInterpreterTab initialized. Ready for battle! ⚔️",
                    file=current_file,
                    version=current_version,
                    function=current_function)

    def _set_ui_initial_state(self):
        self.status_label.configure(text="Status: Disconnected", foreground="red")
        self.command_entry.config(state=tk.DISABLED)
        self.execute_command_button.config(state=tk.DISABLED)
        self.query_button.config(state=tk.DISABLED)
        self.set_button.config(state=tk.DISABLED)
        self.do_button.config(state=tk.DISABLED)

    def _handle_connection_status_change_event(self, event=None):
        current_function = inspect.currentframe().f_code.co_name
        is_connected = self.app_instance.inst is not None
        instrument_model = self.app_instance.connected_instrument_model.get() if hasattr(self.app_instance, 'connected_instrument_model') else ""
        
        debug_log(f"Connection status changed event received: Connected={is_connected}, Model={instrument_model}. Updating UI state.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        
        if is_connected:
            self.status_label.configure(text=f"Status: Connected to {instrument_model}", foreground="green")
            self.command_entry.config(state=tk.NORMAL)
            self.execute_command_button.config(state=tk.NORMAL)
            self.query_button.config(state=tk.NORMAL)
            self.set_button.config(state=tk.NORMAL)
            self.do_button.config(state=tk.NORMAL)
            self.console_print_func(f"✅ VISA Interpreter connected to instrument.")
        else:
            self.status_label.configure(text="Status: Disconnected", foreground="red")
            self.command_entry.config(state=tk.DISABLED)
            self.execute_command_button.config(state=tk.DISABLED)
            self.query_button.config(state=tk.DISABLED)
            self.set_button.config(state=tk.DISABLED)
            self.do_button.config(state=tk.DISABLED)
            self.console_print_func("❌ VISA Interpreter disconnected from instrument.")
    
    def load_data_to_treeview(self):
        """
        Loads data from the internal list into the Treeview widget.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Loading data from list to Treeview... 💾",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        
        for row in self.data:
            self.treeview.insert('', 'end', values=row)

        self.console_print_func(f"✅ Loaded {len(self.data)} entries into the table.")
        debug_log(f"Loaded {len(self.data)} entries into Treeview.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

    def create_widgets(self):
        """
        Creates the UI widgets for the VisaInterpreterTab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Creating widgets for VisaInterpreterTab...",
                    file=current_file,
                    version=current_version,
                    function=current_function)

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

        # CORRECTED: Updated columns to display all 7 data fields
        columns = ("Manufacturer", "Model", "Command Type", "Action", "VISA Command", "Variable", "Validated")
        self.treeview = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.treeview.pack(side="left", fill="both", expand=True)

        for col in columns:
            self.treeview.heading(col, text=col, command=lambda c=col: self._sort_treeview(self.treeview, c))
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
        self.command_entry.bind('<Return>', lambda e: self.command_executor.on_execute_command(self.command_entry.get().strip()))

        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)

        self.execute_command_button = ttk.Button(button_frame, text="Execute", command=lambda: self.command_executor.on_execute_command(self.command_entry.get().strip()))
        self.execute_command_button.grid(row=0, column=0, sticky="ew", padx=2, pady=2)

        self.query_button = ttk.Button(button_frame, text="Query", command=lambda: self.command_executor.on_query_command(self.command_entry.get().strip()))
        self.query_button.grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        
        self.set_button = ttk.Button(button_frame, text="Set", command=lambda: self.command_executor.on_set_command(self.command_entry.get().strip()))
        self.set_button.grid(row=0, column=2, sticky="ew", padx=2, pady=2)
        
        self.do_button = ttk.Button(button_frame, text="Do", command=lambda: self.command_executor.on_do_command(self.command_entry.get().strip()))
        self.do_button.grid(row=0, column=3, sticky="ew", padx=2, pady=2)

        action_frame = ttk.Frame(control_frame)
        action_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        action_frame.columnconfigure(2, weight=1)
        action_frame.columnconfigure(3, weight=1)

        ttk.Button(action_frame, text="Load Data", command=lambda: self._refresh_data()).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(action_frame, text="Add New Row", command=self._add_new_row).grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        ttk.Button(action_frame, text="Save Data", command=self._save_data_to_csv).grid(row=0, column=2, sticky="ew", padx=2, pady=2)
        ttk.Button(action_frame, text="Delete Row", command=self._delete_selected_row).grid(row=0, column=3, sticky="ew", padx=2, pady=2)
        
        debug_log("Widgets created successfully. All systems go! 🚀",
                    file=current_file,
                    version=current_version,
                    function=current_function)

    def setup_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def bind_events(self):
        self.treeview.bind("<Double-1>", self._on_double_click)
        self.treeview.bind("<<TreeviewSelect>>", self._on_treeview_select)
        self.treeview.bind("<FocusIn>", self._on_treeview_focus)

    def _on_treeview_focus(self, event):
        if not self.treeview.selection():
            if self.last_selected_item:
                self.treeview.selection_set(self.last_selected_item)
                self.treeview.focus(self.last_selected_item)

    def _on_treeview_select(self, event):
        selection = self.treeview.selection()
        if selection:
            self.last_selected_item = selection[0]
            values = self.treeview.item(self.last_selected_item, 'values')
            if values:
                self.command_entry.delete(0, tk.END)
                if len(values) > 4 and values[4] is not None:
                    self.command_entry.insert(0, values[4])

    def _on_double_click(self, event):
        item = self.treeview.identify_row(event.y)
        col = self.treeview.identify_column(event.x)
        if item and col:
            col_index = int(col.replace('#', '')) - 1
            column_name = self.treeview['columns'][col_index]

            # CORRECTED: Allow editing of VISA Command, Variable, and Validated columns
            editable_columns = ["VISA Command", "Variable", "Validated"]
            if column_name in editable_columns:
                self._edit_cell(item, col_index)

    def _edit_cell(self, item, col_index):
        x, y, width, height = self.treeview.bbox(item, col_index)
        
        values = self.treeview.item(item, 'values')
        original_text = values[col_index]

        entry = ttk.Entry(self.treeview)
        entry.place(x=x, y=y, width=width, height=height, anchor='nw')
        entry.insert(0, original_text)
        entry.focus_set()

        def on_entry_change(e):
            new_values = list(self.treeview.item(item, 'values'))
            new_values[col_index] = entry.get()
            self.treeview.item(item, values=new_values)
            entry.destroy()
            self.last_selected_item = item
            self._save_data_to_csv()

        def on_focus_out(e):
            entry.destroy()
            self._save_data_to_csv()

        entry.bind("<Return>", on_entry_change)
        entry.bind("<FocusOut>", on_focus_out)

    def _add_new_row(self):
        """
        Adds a new, empty row to the Treeview and the internal data list.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Adding a new empty row to the Treeview. A fresh start!",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        new_row = ["", "", "", "", "", "", ""]
        self.data.append(new_row)
        self.treeview.insert('', 'end', values=new_row)
        self.console_print_func("✅ New row added. Don't forget to save!")
        self._save_data_to_csv()
        debug_log("New row added and saved.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

    def _delete_selected_row(self):
        """
        Deletes the currently selected row from the Treeview and the internal data list.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Attempting to delete the selected row. Goodbye, cruel data!",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        selected_item = self.treeview.selection()
        if not selected_item:
            self.console_print_func("❌ No row selected to delete. You must choose!")
            debug_log("Delete failed: No row selected.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return

        for item in selected_item:
            values = self.treeview.item(item, 'values')
            self.treeview.delete(item)
            if list(values) in self.data:
                self.data.remove(list(values))
            self.console_print_func(f"✅ Row deleted: {values[2]} - {values[3]}")
        
        self._save_data_to_csv()
        debug_log("Row deleted and file saved.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

    def _save_data_to_csv(self):
        """
        Saves the current data from the Treeview back to the CSV file.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Saving data to CSV file. Committing the changes to memory!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        
        current_data = [self.treeview.item(item, 'values') for item in self.treeview.get_children()]

        try:
            save_visa_commands_data(VISA_COMMANDS_FILE_PATH, current_data)
            self.console_print_func(f"✅ Saved data to {os.path.basename(VISA_COMMANDS_FILE_PATH)} successfully.")
            debug_log("Data saved successfully.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        except Exception as e:
            self.console_print_func(f"❌ Error saving data: {e}. Oh no, the data is lost!")
            debug_log(f"Error saving data to CSV: {e}.",
                        file=current_file,
                        version=current_version,
                        function=current_function)

    def _sort_treeview(self, tv, col):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Sorting Treeview by column '{col}'. Let's get this organized! 📚",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        items = list(tv.get_children(''))
        col_index = tv['columns'].index(col)

        is_numeric = False
        if items:
            try:
                float(tv.item(items[0], 'values')[col_index])
                is_numeric = True
            except (ValueError, IndexError):
                is_numeric = False

        direction = self.sort_direction.get(col, 'asc')
        reverse = (direction == 'desc')

        if is_numeric:
            def numeric_sort_key(x):
                try:
                    return float(tv.set(x, col))
                except (ValueError, IndexError):
                    return float('-inf')
            sorted_items = sorted(items, key=numeric_sort_key, reverse=reverse)
        else:
            sorted_items = sorted(items, key=lambda x: tv.set(x, col), reverse=reverse)

        for index, item in enumerate(sorted_items):
            tv.move(item, '', index)

        self.sort_direction[col] = 'asc' if reverse else 'desc'
        
        tv.heading(col, text=f"{col} ({'▲' if not reverse else '▼'})")
        debug_log(f"Treeview sorted by '{col}' in {'descending' if reverse else 'ascending'} order. All tidy now. ✅",
                    file=current_file,
                    version=current_version,
                    function=current_function)

    def _refresh_data(self):
        """Reloads data from the file and updates the treeview."""
        self.data = initialize_data_file_and_load()
        self.load_data_to_treeview()
        self.console_print_func("✅ Data reloaded from file.")
        debug_log("Data reloaded from file.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)