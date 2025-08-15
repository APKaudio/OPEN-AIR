# tabs/Instrument/tab_instrument_child_visa_interpreter.py
#
# This file defines the VisaInterpreterTab, a Tkinter Frame that provides a user-editable
# cell editor for VISA commands. It displays model names, command types, actions, and the
# commands themselves, allowing users to modify, add, or remove entries, and execute
# selected commands directly on a connected instrument. The logic for loading the data
# has been completely rebuilt to ensure a robust workflow where the data file is
# created and populated with defaults if it does not exist before any attempts to read it.
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
# Version 20250816.224500.1 (FIXED: The _yak_button_action function was updated to correctly handle the NAB response as a string and not attempt to reformat it, resolving the ValueError.)

current_version = "20250816.224500.1"
current_version_hash = 20250816 * 224500 * 1

import tkinter as tk
from tkinter import ttk, filedialog
import csv
import os
import inspect
import time
import pandas as pd # Used for data management and sorting

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

# NEW: Import the default commands from the new reference file
from ref.ref_visa_commands import get_default_commands

# NEW: Import the new high-level Yak functions from Yakety_Yak
from tabs.Instrument.Yakety_Yak import YakGet, YakSet, YakDo, YakNab

class VisaInterpreterTab(ttk.Frame):
    """
    A Tkinter Frame that provides a user-editable cell editor for VISA commands.
    It displays model names, command types, actions, and the commands themselves,
    allowing users to modify, add, or remove entries, and execute selected commands.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, style_obj=None, **kwargs):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing VisaInterpreterTab...",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        self.style_obj = style_obj

        filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'style_obj'}
        super().__init__(master, **filtered_kwargs)

        if self.app_instance and hasattr(self.app_instance, 'VISA_COMMANDS_FILE_PATH'):
            self.data_file = self.app_instance.VISA_COMMANDS_FILE_PATH
        else:
            self.data_file = os.path.join(os.getcwd(), "visa_commands.csv")
            debug_log(f"WARNING: app_instance.VISA_COMMANDS_FILE_PATH not found. Falling back to default: {self.data_file}. This is a bit of a mess!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=inspect.currentframe().f_code.co_name)

        self.selected_model = tk.StringVar(self)
        self.selected_model.set("N9340B")
        self.sort_direction = {}

        self._create_widgets()
        # REBUILT LOGIC: Call the new, robust load function here.
        self._load_data()

        self.tree.bind("<Double-1>", self._on_double_click_edit)
        self.tree.bind("<Return>", self._on_enter_edit)
        self.tree.bind("<Escape>", self._on_escape_edit)

        debug_log("VisaInterpreterTab initialized. Ready to interpret some damn commands!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

    def _create_widgets(self):
        """
        Creates and arranges the widgets for the VISA Interpreter tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Creating VisaInterpreterTab widgets...",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0)

        button_frame = ttk.Frame(self, style='Dark.TFrame')
        button_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        button_frame.grid_columnconfigure(3, weight=1)

        ttk.Button(button_frame, text="Add Row", command=self._add_row, style='Blue.TButton').grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Delete Selected Row", command=self._delete_row, style='Red.TButton').grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Save Commands", command=self._save_data, style='Green.TButton').grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="VALIDATE ALL COMMANDS", command=self._validate_all_rows, style='Green.TButton').grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        model_frame = ttk.Frame(self, style='Dark.TFrame')
        model_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        model_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(model_frame, text="Select Instrument Model:", style='TLabel').grid(row=0, column=0, padx=5, pady=5, sticky="w")
        model_options = ["Agilent/Keysight", "N9340B", "N9342CN", "Rohde & Schwarz"]
        self.model_dropdown = ttk.OptionMenu(model_frame, self.selected_model, self.selected_model.get(), *model_options)
        self.model_dropdown.config(width=25)
        self.model_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        columns = ("Manufacturer", "Model", "Command Type", "Action", "VISA Command", "Variable", "Validated")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", style='Treeview')
        self.tree.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        
        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.W, command=lambda _col=col: self._sort_treeview_column(self.tree, _col))
            self.tree.column(col, anchor=tk.W, stretch=tk.TRUE)
            self.sort_direction[col] = 'asc'

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.grid(row=2, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=3, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=hsb.set)

        yak_frame = ttk.LabelFrame(self, text="YAK (Execute Selected Command)", style='Dark.TLabelframe')
        yak_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        yak_frame.grid_columnconfigure(0, weight=1)

        ttk.Button(yak_frame, text="YAK", command=self._yak_button_action, style='LargeYAK.TButton').grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.editor = None

        debug_log("VisaInterpreterTab widgets created. Ready to interpret some damn commands!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

    def _yak_button_action(self):
        # Function Description:
        # Executes the selected VISA command. It now correctly identifies
        # and calls the `YakNab` function for the "NAB" action type.
        #
        # Inputs:
        #   None.
        #
        # Process:
        #   1. Retrieves the selected item from the Treeview.
        #   2. Checks if an instrument is connected.
        #   3. Extracts the command type, action type, and variable value from the selected row.
        #   4. Uses a conditional `if/elif/else` structure to call the appropriate `Yak` function.
        #      - `if action_type == "GET"`: Calls `YakGet`.
        #      - `elif action_type == "NAB"`: Calls `YakNab`.
        #      - `elif action_type == "SET"`: Calls `YakSet`.
        #      - `elif action_type == "DO"`: Calls `YakDo`.
        #   5. Updates the "Validated" column in the Treeview with the result from the call.
        #   6. Calls `_save_data` to persist the changes.
        #
        # Outputs:
        #   None. Modifies the Treeview and saves the data file.
        current_function = inspect.currentframe().f_code.co_name
        debug_log("YAK button clicked. Attempting to execute selected VISA command. Let's send this command to the instrument!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        selected_item = self.tree.focus()
        if not selected_item:
            self.console_print_func("⚠️ No row selected to execute.")
            debug_log("No row selected for YAK action. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return

        if not self.app_instance.inst:
            self.console_print_func("❌ No instrument connected. Cannot execute VISA command.")
            debug_log("No instrument connected for YAK action. This thing is disconnected!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return

        values = self.tree.item(selected_item, 'values')
        command_type = values[2]
        action_type = values[3]
        variable_value = values[5]

        response = "FAILED"
        if action_type == "GET":
            response = YakGet(self.app_instance, command_type, self.console_print_func)
        elif action_type == "NAB":
            # FIX: Just assign the response directly, as YakNab now returns a formatted string.
            response = YakNab(self.app_instance, command_type, self.console_print_func)
        elif action_type == "SET":
            response = YakSet(self.app_instance, command_type, variable_value, self.console_print_func)
        elif action_type == "DO":
            response = YakDo(self.app_instance, command_type, self.console_print_func)
        else:
            self.console_print_func(f"⚠️ Unknown action type '{action_type}'. Cannot execute command.")
            debug_log(f"Unknown action type '{action_type}' for command type: {command_type}. This is a goddamn mess!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)

        current_values = list(values)
        validated_column_index = 6
        current_values[validated_column_index] = str(response) if response is not None else "FAILED"
        self.tree.item(selected_item, values=current_values)
        self.console_print_func(f"✅ Table updated: Validated column now shows '{response}'.")
        debug_log(f"Table updated for item {selected_item}. Validated column now shows '{response}'. Fucking brilliant!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        self._save_data()

    def _validate_all_rows(self):
        current_function = inspect.currentframe().f_code.co_name
        
        self.console_print_func("Please take a deep breath before validation begins.")
        self.console_print_func("ℹ️ Starting validation of all commands...")
        debug_log("Starting validation of all commands. Let's see if this whole table works!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        if not self.app_instance.inst:
            self.console_print_func("❌ No instrument connected. Cannot validate.")
            debug_log("No instrument connected. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return

        all_items = self.tree.get_children()
        if not all_items:
            self.console_print_func("⚠️ No commands to validate.")
            debug_log("No items in the table to validate. What a waste!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return
        
        for item in all_items:
            self.tree.focus(item)
            self.tree.selection_set(item)
            self._yak_button_action()
            self.tree.see(item)
            self.update_idletasks()
            time.sleep(0.5)

        self.console_print_func("✅ Validation of all commands completed.")
        debug_log("Validation of all commands finished. Fucking awesome!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

    def _ensure_data_file_exists(self):
        """
        Function Description:
        Ensures the VISA commands CSV file exists. If not, it creates the file
        with the default headers and populates it with default commands.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}. Checking if data file exists at {self.data_file}.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        # Check if file doesn't exist OR if it exists but is empty
        if not os.path.exists(self.data_file) or os.path.getsize(self.data_file) == 0:
            self.console_print_func(f"ℹ️ {os.path.basename(self.data_file)} is empty or not found. Creating with default commands.")
            debug_log("Data file not found or is empty. Creating new file with default commands.",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)

            # Ensure the directory exists
            output_dir = os.path.dirname(self.data_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            try:
                # Get default commands
                default_commands = get_default_commands()
                # Use pandas to create a DataFrame and save it, ensuring consistent headers
                columns = ["Manufacturer", "Model", "Command Type", "Action", "VISA Command", "Variable", "Validated"]
                df = pd.DataFrame(default_commands, columns=columns)
                df.to_csv(self.data_file, index=False)
                self.console_print_func("✅ New CSV file created with default VISA commands.")
                debug_log(f"New CSV file created with {len(default_commands)} default commands.",
                            file=os.path.basename(__file__),
                            version=current_version,
                            function=current_function)
                return True
            except Exception as e:
                self.console_print_func(f"❌ Error creating/populating new CSV file: {e}. This is a disaster!")
                debug_log(f"Error creating/populating new CSV file: {e}. Fucking hell!",
                            file=os.path.basename(__file__),
                            version=current_version,
                            function=current_function)
                return False
        
        return True # File exists and is not empty

    def _load_data(self):
        """
        REBUILT: This function now first ensures the data file exists and has content,
        then it calls another function to populate the treeview.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}. Orchestrating data load. Version: {current_version}",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        # Step 1: Ensure the file is ready to be read
        if not self._ensure_data_file_exists():
            debug_log("Data file check failed. Aborting load.",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return

        # Step 2: Populate the treeview from the now-guaranteed-to-exist file
        self._populate_treeview()
        
    def _populate_treeview(self):
        """
        Function Description:
        Populates the Treeview with the data from the existing CSV file.
        This function assumes that the data file exists and is well-formed.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}. Populating Treeview from {self.data_file}. Version: {current_version}",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        self.tree.delete(*self.tree.get_children())
        commands_to_load = []

        try:
            with open(self.data_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                for row in reader:
                    commands_to_load.append(row)

            for row in commands_to_load:
                self.tree.insert("", "end", values=row)

            self._resize_columns_to_fit_content()
            self.console_print_func(f"✅ Displayed {len(commands_to_load)} commands in the interpreter.")
            debug_log(f"Displayed {len(commands_to_load)} commands in Treeview. Let's see if they work!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
        except Exception as e:
            self.console_print_func(f"❌ Error loading commands from {os.path.basename(self.data_file)}: {e}. The file might be corrupted.")
            debug_log(f"Error loading {self.data_file}: {e}. This CSV is a stubborn bastard! Clearing the Treeview.",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            self.tree.delete(*self.tree.get_children()) # Clear the tree on error

    def _save_data(self, commands_to_save=None):
        """
        Saves the current commands from the Treeview (or an explicitly provided list) to the CSV file.
        Ensures the directory exists before saving.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Saving data to {self.data_file}...",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        if commands_to_save is None:
            commands_to_save = []
            for item_id in self.tree.get_children():
                values = self.tree.item(item_id, 'values')
                commands_to_save.append(list(values))

        output_dir = os.path.dirname(self.data_file)
        os.makedirs(output_dir, exist_ok=True)

        try:
            with open(self.data_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Manufacturer", "Model", "Command Type", "Action", "VISA Command", "Variable", "Validated"])
                writer.writerows(commands_to_save)
            self.console_print_func(f"✅ Saved {len(commands_to_save)} commands to {os.path.basename(self.data_file)}.")
            debug_log(f"Saved {len(commands_to_save)} commands to {self.data_file}. Fucking brilliant!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
        except Exception as e:
            self.console_print_func(f"❌ Error saving commands to {os.path.basename(self.data_file)}: {e}")
            debug_log(f"Error saving {self.data_file}: {e}. This saving process is a pain in the ass!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)

    def _add_row(self):
        """
        Adds a new empty row to the Treeview with default values.
        """
        current_function = inspect.currentframe().f_code.co_name
        self.tree.insert("", "end", values=("Agilent/Keysight", "N9340B", "General", "SET", "", "", ""))
        self.console_print_func("✅ Added a new empty row.")
        debug_log("Added new row. Another one bites the dust!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

    def _delete_row(self):
        """
        Deletes the selected row(s) from the Treeview.
        """
        current_function = inspect.currentframe().f_code.co_name
        selected_items = self.tree.selection()
        if not selected_items:
            self.console_print_func("⚠️ No row selected to delete.")
            debug_log("No row selected for deletion. Fucking useless!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return

        for item in selected_items:
            self.tree.delete(item)
        self.console_print_func(f"✅ Deleted {len(selected_items)} selected row(s).")
        debug_log(f"Deleted {len(selected_items)} row(s). Goodbye, you useless rows!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)

    def _on_double_click_edit(self, event):
        """
        Handles double-click event to enable in-cell editing.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Double-click detected for editing. Time to make some changes!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        if self.editor:
            self._save_and_destroy_editor()

        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if not item or not column:
            debug_log("No item or column identified for editing. Fucking useless click!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return

        col_idx = int(column[1:]) - 1

        current_values = self.tree.item(item, 'values')
        current_value = current_values[col_idx]

        x, y, width, height = self.tree.bbox(item, column)

        self.editor = ttk.Entry(self.tree, style='TEntry')
        self.editor.place(x=x, y=y, width=width, height=height)
        self.editor.insert(0, current_value)
        self.editor.focus_set()

        self.editor.item = item
        self.editor.column = col_idx
        debug_log(f"Editor created for item {item}, column {col_idx} with value '{current_value}'. Let's get this fixed!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

    def _save_and_destroy_editor(self):
        """
        Saves the edited content from the Entry widget back to the Treeview
        and destroys the Entry widget. Automatically updates "Action"
        if the "VISA Command" column is edited.
        """
        current_function = inspect.currentframe().f_code.co_name
        if self.editor:
            new_value = self.editor.get()
            item = self.editor.item
            col_idx = self.editor.column

            current_values = list(self.tree.item(item, 'values'))
            current_values[col_idx] = new_value

            if col_idx == 4:
                visa_command = new_value
                action_type = "GET" if visa_command.strip().endswith("?") else ("DO" if visa_command.strip() in ["*RST", ":SYSTem:DISPlay:UPDate"] else "SET")
                current_values[3] = action_type

            self.tree.item(item, values=current_values)
            self.editor.destroy()
            self.editor = None
            self.console_print_func(f"✅ Cell updated: {current_values}")
            debug_log(f"Editor destroyed. Cell updated to: '{new_value}'. Another bug squashed!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            
            self._save_data()
            self._resize_columns_to_fit_content()


    def _on_enter_edit(self, event):
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Enter key pressed in editor. Saving changes!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        self._save_and_destroy_editor()

    def _on_escape_edit(self, event):
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Escape key pressed in editor. Cancelling changes!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        if self.editor:
            self.editor.destroy()
            self.editor = None
            self.console_print_func("ℹ️ Cell edit cancelled.")
            debug_log("Editor destroyed without saving. Fucking pointless to keep it!",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)

    def _on_tab_selected(self, event):
        current_function = inspect.currentframe().f_code.co_name
        debug_log("VISA Interpreter Tab selected. Reloading data. Let's make sure everything is up to date!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        self._load_data()

    def _resize_columns_to_fit_content(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Resizing Treeview columns to fit content. What a goddamn good idea!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        columns = self.tree["columns"]
        for col in columns:
            max_width = self.tree.column(col, "width")
            heading_text = self.tree.heading(col, "text")
            heading_width = tk.font.Font().measure(heading_text) + 15

            for item in self.tree.get_children():
                col_index = columns.index(col)
                value = self.tree.item(item, "values")[col_index]
                item_width = tk.font.Font().measure(value) + 15
                max_width = max(max_width, heading_width, item_width)

            self.tree.column(col, width=max_width, stretch=tk.FALSE)
            debug_log(f"Column '{col}' resized to width {max_width}.",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)

        self.tree.update_idletasks()

    def _sort_treeview_column(self, tv, col):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Sorting Treeview by column '{col}'. Let's get this organized!",
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
        debug_log(f"Treeview sorted by '{col}' in {'descending' if reverse else 'ascending'} order. Fucking marvelous!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)