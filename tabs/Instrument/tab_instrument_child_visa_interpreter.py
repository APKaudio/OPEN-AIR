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
# Version 20250802.0149.1 (Explicitly filtered style_obj from kwargs passed to super().__init__.)

current_version = "20250802.0149.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250801 * 2210 * 1 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk, filedialog
import csv
import os
import inspect # Import inspect module for debug_log

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

from tabs.Instrument.utils_yak_visa import execute_visa_command # Corrected import path for utils_yak_visa

class VisaInterpreterTab(ttk.Frame):
    """
    A Tkinter Frame that provides a user-editable cell editor for VISA commands.
    It displays model names, command types, actions, and the commands themselves,
    allowing users to modify, add, or remove entries, and execute selected commands.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, style_obj=None, **kwargs): # Added style_obj
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing VisaInterpreterTab...",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
        self.style_obj = style_obj # Store the style object

        # Explicitly remove 'style_obj' from kwargs before passing them to the superclass
        # This is a defensive measure to prevent TclError if it somehow ends up in kwargs.
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'style_obj'}
        super().__init__(master, **filtered_kwargs) # Pass filtered kwargs

        # Use the VISA_COMMANDS_FILE_PATH from the app_instance
        if self.app_instance and hasattr(self.app_instance, 'VISA_COMMANDS_FILE_PATH'):
            self.data_file = self.app_instance.VISA_COMMANDS_FILE_PATH
            debug_log(f"Using VISA commands file from app_instance: {self.data_file}",
                        file=__file__,
                        version=current_version,
                        function=inspect.currentframe().f_code.co_name)
        else:
            # Fallback if app_instance or path is not available (should not happen if main_app is set up correctly)
            self.data_file = os.path.join(os.getcwd(), "visa_commands.csv")
            debug_log(f"WARNING: app_instance.VISA_COMMANDS_FILE_PATH not found. Falling back to default: {self.data_file}. This is a bit of a mess!",
                        file=__file__,
                        version=current_version,
                        function=inspect.currentframe().f_code.co_name)


        # Tkinter variable for the model selection dropdown (for filtering/defaulting new rows)
        self.selected_model = tk.StringVar(self)
        self.selected_model.set("N9340B") # Default value for the dropdown filter

        self._create_widgets()
        self._load_data() # Load existing data when the tab is initialized

        # Bind double-click event for cell editing
        self.tree.bind("<Double-1>", self._on_double_click_edit)
        # Bind <Return> key to save and close editor
        self.tree.bind("<Return>", self._on_enter_edit)
        # Bind <Escape> key to close editor without saving
        self.tree.bind("<Escape>", self._on_escape_edit)

        debug_log("VisaInterpreterTab initialized. Ready to interpret some damn commands!",
                    file=__file__,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

    def _create_widgets(self):
        """
        Creates and arranges the widgets for the VISA Interpreter tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Creating VisaInterpreterTab widgets...",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        # Re-configure grid rows to place buttons first
        self.grid_rowconfigure(0, weight=0) # Row for Add/Delete/Save buttons
        self.grid_rowconfigure(1, weight=0) # Row for Model Selection dropdown
        self.grid_rowconfigure(2, weight=1) # Treeview takes most space
        self.grid_rowconfigure(3, weight=0) # Scrollbar for Treeview (horizontal)
        self.grid_rowconfigure(4, weight=0) # New row for YAK buttons

        # Button Frame (Add, Delete, Save) - Moved to row 0
        button_frame = ttk.Frame(self, style='Dark.TFrame')
        button_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)

        ttk.Button(button_frame, text="Add Row", command=self._add_row, style='Blue.TButton').grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Delete Selected Row", command=self._delete_row, style='Red.TButton').grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Save Commands", command=self._save_data, style='Green.TButton').grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Model Selection Dropdown (for filtering/defaulting new rows) - Moved to row 1
        model_frame = ttk.Frame(self, style='Dark.TFrame')
        model_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        model_frame.grid_columnconfigure(1, weight=1) # Allow dropdown to expand

        ttk.Label(model_frame, text="Select Instrument Model:", style='TLabel').grid(row=0, column=0, padx=5, pady=5, sticky="w")
        model_options = ["N9340B", "Agilent/Keysight", "Rohde & Schwarz"] # Added N9340B as a specific option
        self.model_dropdown = ttk.OptionMenu(model_frame, self.selected_model, self.selected_model.get(), *model_options)
        self.model_dropdown.config(width=25)
        self.model_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")


        # Treeview for displaying and editing commands - Moved to row 2
        # Updated columns to include "Model" at the beginning
        columns = ("Model", "Command Type", "Action", "VISA Command", "Variable")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", style='Treeview')
        self.tree.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        # Configure column headings
        self.tree.heading("Model", text="Model", anchor=tk.W) # New heading for Model
        self.tree.heading("Command Type", text="Command Type", anchor=tk.W)
        self.tree.heading("Action", text="Action", anchor=tk.W)
        self.tree.heading("VISA Command", text="VISA Command", anchor=tk.W)
        self.tree.heading("Variable", text="Variable", anchor=tk.W)

        # Configure column widths (adjust as needed)
        self.tree.column("Model", width=100, minwidth=80, stretch=False) # Fixed width for Model
        self.tree.column("Command Type", width=120, minwidth=100, stretch=False)
        self.tree.column("Action", width=80, minwidth=60, stretch=False)
        self.tree.column("VISA Command", width=250, minwidth=150, stretch=True)
        self.tree.column("Variable", width=100, minwidth=80, stretch=True)

        # Scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.grid(row=2, column=1, sticky="ns") # Aligned with Treeview
        self.tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=3, column=0, sticky="ew") # Below Treeview
        self.tree.configure(xscrollcommand=hsb.set)

        # --- YAK Button Row (Execute Selected Command) - Moved to row 4 ---
        yak_frame = ttk.LabelFrame(self, text="YAK (Execute Selected Command)", style='Dark.TLabelframe')
        yak_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        yak_frame.grid_columnconfigure(0, weight=1) # Single column to center the button

        # YAK button to execute the selected VISA command (2x taller)
        # The style 'LargeYAK.TButton' is defined in style.py and applied here.
        ttk.Button(yak_frame, text="YAK", command=self._yak_button_action, style='LargeYAK.TButton').grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.editor = None # To hold the Entry widget for editing

        debug_log("VisaInterpreterTab widgets created. Ready to serve!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    def _yak_button_action(self):
        """
        Action to perform when the YAK button is clicked.
        Queries or sets the VISA command of the selected row using the utility function.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("YAK button clicked. Attempting to execute selected VISA command. Let's send this command to the instrument!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        selected_item = self.tree.focus() # Get the currently focused/selected item
        if not selected_item:
            self.console_print_func("⚠️ No row selected to execute.")
            debug_log("No row selected for YAK action. Fucking useless!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        if not self.app_instance.inst:
            self.console_print_func("❌ No instrument connected. Cannot execute VISA command.")
            debug_log("No instrument connected for YAK action. This thing is disconnected!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        values = self.tree.item(selected_item, 'values')
        # Columns: (Model, Command Type, Action, VISA Command, Variable)
        # Note: Model is at index 0, Command Type at 1, Action at 2, VISA Command at 3, Variable at 4
        action_type = values[2] # "Action" column
        visa_command = values[3] # "VISA Command" column
        variable_value = values[4] # "Variable" column

        # Call the new utility function to execute the VISA command
        execute_visa_command(
            self.app_instance.inst,
            action_type,
            visa_command,
            variable_value,
            self.console_print_func
        )


    def _load_data(self):
        """
        Loads VISA commands from the CSV file. If the file doesn't exist or is empty,
        it loads default commands and then attempts to save them to the file.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Loading data from {self.data_file}...",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        self.tree.delete(*self.tree.get_children()) # Clear existing data

        commands_to_load = []
        file_exists = os.path.exists(self.data_file)
        file_needs_defaults = False # Flag to indicate if defaults should be loaded and saved

        if file_exists:
            try:
                with open(self.data_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    # Try to read the header. If no header, file is truly empty.
                    try:
                        header = next(reader)
                    except StopIteration:
                        debug_log(f"CSV file '{self.data_file}' is empty (no header). Fucking empty!",
                                    file=__file__,
                                    version=current_version,
                                    function=current_function)
                        file_needs_defaults = True
                        # No need to break, commands_to_load remains empty
                        pass

                    if not file_needs_defaults: # Only read rows if header was found
                        for row in reader:
                            commands_to_load.append(row)

                if not commands_to_load: # If file existed but contained no data rows (only header or completely empty)
                    file_needs_defaults = True
                    self.console_print_func(f"ℹ️ {os.path.basename(self.data_file)} found but contains no commands. Loading default commands.")
                    debug_log(f"CSV file '{self.data_file}' found but no data rows. Loading defaults. What a waste of a file!",
                                file=__file__,
                                version=current_version,
                                function=current_function)
                else:
                    self.console_print_func(f"✅ Loaded {len(commands_to_load)} commands from {os.path.basename(self.data_file)}.")
                    debug_log(f"Loaded {len(commands_to_load)} commands from {self.data_file}. Fucking awesome!",
                                file=__file__,
                                version=current_version,
                                function=current_function)

            except Exception as e:
                self.console_print_func(f"❌ Error loading commands from {os.path.basename(self.data_file)}: {e}. Loading default commands.")
                debug_log(f"Error loading {self.data_file}: {e}. This CSV is a stubborn bastard! Loading default commands.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                file_needs_defaults = True # Treat as "empty" for default loading purposes
        else: # File does not exist
            self.console_print_func(f"ℹ️ {os.path.basename(self.data_file)} not found. Loading default commands and saving them.")
            debug_log(f"{self.data_file} not found. Loading default commands. Where the hell is it?!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            file_needs_defaults = True # Treat as "empty" for default loading purposes

        if file_needs_defaults:
            commands_to_load = self._get_default_commands()
            self._save_data() # Save defaults to the file

        for model_name, cmd_type, action, command, variable in commands_to_load:
            self.tree.insert("", "end", values=(model_name, cmd_type, action, command, variable))
        debug_log(f"Displayed {len(commands_to_load)} commands in Treeview. Let's see if they work!",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _save_data(self):
        """
        Saves the current commands from the Treeview to the CSV file defined by self.data_file.
        Ensures the directory exists before saving.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Saving data to {self.data_file}...",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        data_to_save = []
        for item_id in self.tree.get_children():
            values = self.tree.item(item_id, 'values')
            data_to_save.append(list(values)) # Convert tuple to list for consistency

        # Ensure the directory for self.data_file exists
        output_dir = os.path.dirname(self.data_file)
        os.makedirs(output_dir, exist_ok=True)

        try:
            with open(self.data_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Updated header to include 'Model'
                writer.writerow(["Model", "Command Type", "Action", "VISA Command", "Variable"])
                writer.writerows(data_to_save)
            self.console_print_func(f"✅ Saved {len(data_to_save)} commands to {os.path.basename(self.data_file)}.")
            debug_log(f"Saved {len(data_to_save)} commands to {self.data_file}. Fucking brilliant!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except Exception as e:
            self.console_print_func(f"❌ Error saving commands to {os.path.basename(self.data_file)}: {e}")
            debug_log(f"Error saving {self.data_file}: {e}. This saving process is a pain in the ass!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    def _add_row(self):
        """
        Adds a new empty row to the Treeview with default values.
        """
        current_function = inspect.currentframe().f_code.co_name
        # New rows will have default model ("N9340B"), "General" type, "SET" action, empty command, empty variable
        self.tree.insert("", "end", values=("N9340B", "General", "SET", "", ""))
        self.console_print_func("✅ Added a new empty row.")
        debug_log("Added new row. Another one bites the dust!",
                    file=__file__,
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
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        for item in selected_items:
            self.tree.delete(item)
        self.console_print_func(f"✅ Deleted {len(selected_items)} selected row(s).")
        debug_log(f"Deleted {len(selected_items)} row(s). Goodbye, you useless rows!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    def _on_double_click_edit(self, event):
        """
        Handles double-click event to enable in-cell editing.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Double-click detected for editing. Time to make some changes!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        if self.editor: # If an editor is already open, destroy it first
            self._save_and_destroy_editor()

        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if not item or not column:
            debug_log("No item or column identified for editing. Fucking useless click!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        # Get column index (0-indexed)
        col_idx = int(column[1:]) - 1

        # Get current value
        current_values = self.tree.item(item, 'values')
        current_value = current_values[col_idx]

        # Get bounding box of the cell
        x, y, width, height = self.tree.bbox(item, column)

        # Create an Entry widget for editing
        self.editor = ttk.Entry(self.tree, style='TEntry')
        self.editor.place(x=x, y=y, width=width, height=height)
        self.editor.insert(0, current_value)
        self.editor.focus_set()

        # Store item and column info for saving
        self.editor.item = item
        self.editor.column = col_idx
        debug_log(f"Editor created for item {item}, column {col_idx} with value '{current_value}'. Let's get this fixed!",
                    file=__file__,
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

            # Get current values as a list, update the specific column, then set back
            current_values = list(self.tree.item(item, 'values'))
            current_values[col_idx] = new_value

            # If the edited column is the VISA Command column (index 3), update the Action (index 2)
            # The "Command Type" column (index 1) should NOT be updated here.
            if col_idx == 3: # This is the "VISA Command" column
                visa_command = new_value
                action_type = "GET" if visa_command.strip().endswith("?") else ("DO" if visa_command.strip() in ["*RST", ":SYSTem:DISPlay:UPDate"] else "SET")
                current_values[2] = action_type # Update the 'Action' column

            self.tree.item(item, values=current_values)
            self.editor.destroy()
            self.editor = None
            self.console_print_func(f"✅ Cell updated: {current_values}")
            debug_log(f"Editor destroyed. Cell updated to: '{new_value}'. Another bug squashed!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    def _on_enter_edit(self, event):
        """Handles Enter key press to save and destroy editor."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Enter key pressed in editor. Saving changes!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        self._save_and_destroy_editor()

    def _on_escape_edit(self, event):
        """Handles Escape key press to destroy editor without saving."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Escape key pressed in editor. Cancelling changes!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        if self.editor:
            self.editor.destroy()
            self.editor = None
            self.console_print_func("ℹ️ Cell edit cancelled.")
            debug_log("Editor destroyed without saving. Fucking pointless to keep it!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

    def _get_default_commands(self):
        """
        Returns a list of default VISA commands.
        Each entry is a tuple: (Model, Category, Action, VISA Command, Default Value for Variable).
        """
        default_raw_commands = [
            # System/Identification
            ("N9340B", "System/ID", "GET", "*IDN?", ""),
            ("N9340B", "System/Reset", "DO", "*RST", ""),
            ("N9340B", "System/Errors", "GET", ":SYSTem:ERRor?", ""),
            ("N9340B", "System/Display Update", "DO", ":SYSTem:DISPlay:UPDate", ""),

            # Frequency/Span/Sweep
            ("N9340B", "Frequency/Center", "SET", ":SENSe:FREQuency:CENTer", "1000"),
            ("N9340B", "Frequency/Center", "GET", ":SENSe:FREQuency:CENTer?", ""),
            ("N9340B", "Frequency/Span", "SET", ":SENSe:FREQuency:SPAN", "1000"),
            ("N9340B", "Frequency/Span", "GET", ":SENSe:FREQuency:SPAN?", ""),
            ("N9340B", "Frequency/Start", "GET", ":FREQuency:STARt?", ""),
            ("N9340B", "Frequency/Start", "SET", ":FREQuency:STARt", "100000"),
            ("N9340B", "Frequency/Stop", "GET", ":FREQuency:STOP?", ""),
            ("N9340B", "Frequency/Stop", "SET", ":FREQuency:STOP", "200000"),
            ("N9340B", "Frequency/Sweep/Points", "GET", ":SENSe:SWEep:POINts?", ""),
            ("N9340B", "Frequency/Sweep/Time", "SET", ":SENSe:SWEep:TIME:AUTO", "ON"),
            ("N9340B", "Frequency/Sweep/Spacing", "SET", ":SENSe:X:SPACing LINear", "LINear"),
            ("N9340B", "Frequency/Offset", "GET", ":FREQuency:OFFSet?", ""),
            ("N9340B", "Frequency/Shift", "GET", ":INPut:RFSense:FREQuency:SHIFt?", ""),
            ("N9340B", "Frequency/Shift", "SET", ":INPut:RFSense:FREQuency:SHIFt", "0"),


            # Bandwidth (RBW/VBW)
            ("N9340B", "Bandwidth/Resolution", "SET", ":SENSe:BANDwidth:RESolution", "1000"),
            ("N9340B", "Bandwidth/Resolution", "GET", ":SENSe:BANDwidth:RESolution?", ""),
            ("N9340B", "Bandwidth/Video", "SET", ":SENSe:BANDwidth:VIDeo", "100"),
            ("N9340B", "Bandwidth/Video", "GET", ":SENSe:BANDwidth:VIDeo?", ""),
            ("N9340B", "Bandwidth/Resolution/Auto", "SET", ":SENSe:BANDwidth:RESolution:AUTO", "ON"),
            ("N9340B", "Bandwidth/Video/Auto", "SET", ":SENSe:BANDwidth:VIDeo:AUTO", "ON"),

            # Amplitude/Reference Level/Attenuation/Gain
            ("N9340B", "Amplitude/Reference Level", "SET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-20"),
            ("N9340B", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel?", ""),
            ("N9340B", "Amplitude/Attenuation/Auto", "SET", ":INPut:ATTenuation:AUTO", "ON"),
            ("N9340B", "Amplitude/Attenuation/Auto", "GET", ":INPut:ATTenuation:AUTO?", ""),
            ("N9340B", "Amplitude/Gain/State", "SET", ":INPut:GAIN:STATe", "ON"),
            ("N9340B", "Amplitude/Gain/State", "GET", ":INPut:GAIN:STATe?", ""),
            ("N9340B", "Amplitude/Power/Attenuation/Auto", "SET", ":POWer:ATTenuation:AUTO", "ON"),
            ("N9340B", "Amplitude/Power/Attenuation/0dB", "SET", ":POWer:ATTenuation", "0"),
            ("N9340B", "Amplitude/Power/Attenuation/10dB", "SET", ":POWer:ATTenuation", "10"),
            ("N9340B", "Amplitude/Power/Gain/On", "SET", ":POWer:GAIN", "ON"),
            ("N9340B", "Amplitude/Power/Gain/Off", "SET", ":POWer:GAIN", "OFF"),
            ("N9340B", "Amplitude/Power/Gain/1", "SET", ":POWer:GAIN", "1"),
            ("N9340B", "Amplitude/Power/High Sensitive/On", "SET", ":POWer:HSENsitive", "ON"),
            ("N9340B", "Amplitude/Power/High Sensitive/Off", "SET", ":POWer:HSENsitive", "OFF"),

            # Trace/Display - Expanded for 4 traces
            # Trace Data Query
            ("N9340B", "Trace/1/Data", "GET", ":TRACe:DATA? TRACE1", ""),
            ("N9340B", "Trace/2/Data", "GET", ":TRACe:DATA? TRACE2", ""),
            ("N9340B", "Trace/3/Data", "GET", ":TRACe:DATA? TRACE3", ""),
            ("N9340B", "Trace/4/Data", "GET", ":TRACe:DATA? TRACE4", ""),

            # Trace Mode Write
            ("N9340B", "Trace/1/Mode/Write", "SET", ":TRAC1:MODE", "WRITe"),
            ("N9340B", "Trace/2/Mode/Write", "SET", ":TRAC2:MODE", "WRITe"),
            ("N9340B", "Trace/3/Mode/Write", "SET", ":TRAC3:MODE", "WRITe"),
            ("N9340B", "Trace/4/Mode/Write", "SET", ":TRAC4:MODE", "WRITe"),

            # Trace Mode MaxHold
            ("N940B", "Trace/1/Mode/MaxHold", "SET", ":TRAC1:MODE", "MAXHold"),
            ("N9340B", "Trace/2/Mode/MaxHold", "SET", ":TRAC2:MODE", "MAXHold"),
            ("N9340B", "Trace/3/Mode/MaxHold", "SET", ":TRAC3:MODE", "MAXHold"),
            ("N9340B", "Trace/4/Mode/MaxHold", "SET", ":TRAC4:MODE", "MAXHold"),

            # Trace Mode Average
            ("N9340B", "Trace/1/Mode/Average", "SET", ":TRAC1:MODE", "AVERage"),
            ("N9340B", "Trace/2/Mode/Average", "SET", ":TRAC2:MODE", "AVERage"),
            ("N9340B", "Trace/3/Mode/Average", "SET", ":TRAC3:MODE", "AVERage"),
            ("N9340B", "Trace/4/Mode/Average", "SET", ":TRAC4:MODE", "AVERage"),

            # Trace Mode MinHold
            ("N9340B", "Trace/1/Mode/MinHold", "SET", ":TRAC1:MODE", "MINHold"),
            ("N9340B", "Trace/2/Mode/MinHold", "SET", ":TRAC2:MODE", "MINHold"),
            ("N9340B", "Trace/3/Mode/MinHold", "SET", ":TRAC3:MODE", "MINHold"),
            ("N9340B", "Trace/4/Mode/MinHold", "SET", ":TRAC4:MODE", "MINHold"),

            ("N9340B", "Trace/Display/Type", "GET", ":DISPlay:WINDow:TRACe:TYPE?", ""),
            ("N9340B", "Trace/Display/Y Scale/Spacing", "SET", ":DISPlay:WINDow:TRACe:Y:SCALe:SPACing", "LOGarithmic"),
            ("N9342CN", "Trace/Format/Data/ASCII (N9340B)", "SET", ":TRACe:FORMat:DATA", "ASCii"), # For N9340B
            ("N9340B", "Trace/Format/Data/ASCII (General)", "SET", ":FORMat:DATA", "ASCii"), # General

            # Marker - Expanded for 6 markers
            # Marker Calculate Max
            ("N9340B", "Marker/1/Calculate/Max", "DO", ":CALCulate:MARKer1:MAX", ""),
            ("N9340B", "Marker/2/Calculate/Max", "DO", ":CALCulate:MARKer2:MAX", ""),
            ("N9340B", "Marker/3/Calculate/Max", "DO", ":CALCulate:MARKer3:MAX", ""),
            ("N9340B", "Marker/4/Calculate/Max", "DO", ":CALCulate:MARKer4:MAX", ""),
            ("N9340B", "Marker/5/Calculate/Max", "DO", ":CALCulate:MARKer5:MAX", ""),
            ("N9340B", "Marker/6/Calculate/Max", "DO", ":CALCulate:MARKer6:MAX", ""),

            # Marker Calculate State
            ("N9340B", "Marker/1/Calculate/State", "SET", ":CALCulate:MARKer1:STATe", "ON"),
            ("N9340B", "Marker/2/Calculate/State", "SET", ":CALCulate:MARKer2:STATe", "ON"),
            ("N940B", "Marker/3/Calculate/State", "SET", ":CALCulate:MARKer3:STATe", "ON"),
            ("N9340B", "Marker/4/Calculate/State", "SET", ":CALCulate:MARKer4:STATe", "ON"),
            ("N9340B", "Marker/5/Calculate/State", "SET", ":CALCulate:MARKer5:STATe", "ON"),
            ("N9340B", "Marker/6/Calculate/State", "SET", ":CALCulate:MARKer6:STATe", "ON"),

            # Marker Calculate X (Frequency)
            ("N9340B", "Marker/1/Calculate/X", "GET", ":CALCulate:MARKer1:X?", ""),
            ("N9340B", "Marker/2/Calculate/X", "GET", ":CALCulate:MARKer2:X?", ""),
            ("N9340B", "Marker/3/Calculate/X", "GET", ":CALCulate:MARKer3:X?", ""),
            ("N9340B", "Marker/4/Calculate/X", "GET", ":CALCulate:MARKer4:X?", ""),
            ("N9340B", "Marker/5/Calculate/X", "GET", ":CALCulate:MARKer5:X?", ""),
            ("N9340B", "Marker/6/Calculate/X", "GET", ":CALCulate:MARKer6:X?", ""),

            # Marker Calculate Y (Amplitude)
            ("N9340B", "Marker/1/Calculate/Y", "GET", ":CALCulate:MARKer1:Y?", ""),
            ("N9340B", "Marker/2/Calculate/Y", "GET", ":CALCulate:MARKer2:Y?", ""),
            ("N9340B", "Marker/3/Calculate/Y", "GET", ":CALCulate:MARKer3:Y?", ""),
            ("N9340B", "Marker/4/Calculate/Y", "GET", ":CALCulate:MARKer4:Y?", ""),
            ("N9340B", "Marker/5/Calculate/Y", "GET", ":CALCulate:MARKer5:Y?", ""),
            ("N9340B", "Marker/6/Calculate/Y", "GET", ":CALCulate:MARKer6:Y?", ""),

            # Memory/Preset
            ("N9340B", "Memory/Preset/Catalog", "GET", ":MMEMory:CATalog:STATe?", ""),
            ("N9340B", "Memory/Preset/Load", "SET", ":MMEMory:LOAD:STATe", "0"),
            ("N9340B", "Memory/Preset/Store", "SET", ":MMEMory:STORe:STATe", "0"),
        ]

        processed_commands = []
        for model, category, action, cmd, default_var_value in default_raw_commands:
            processed_commands.append((model, category, action, cmd, default_var_value))
        return processed_commands

    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Can be used to refresh data or update UI elements specific to this tab.
        For the interpreter, we ensure data is loaded/reloaded.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("VISA Interpreter Tab selected. Reloading data. Let's make sure everything is up to date!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        self._load_data() # Reload data to ensure it's up-to-date

