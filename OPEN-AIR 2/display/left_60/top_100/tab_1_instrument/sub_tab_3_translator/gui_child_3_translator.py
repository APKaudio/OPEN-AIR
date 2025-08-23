# tabs/Instrument/tab_instrument_child_visa_interpreter_gui.py
#
# A GUI-only prototype of the VISA Interpreter tab, structured as a self-contained element.
# This file handles the visual layout and user interactions, while delegating any
# business logic to other modules (currently simulated with dummy functions).
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
# Version 20250822.213500.1

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import pathlib
import sys

# --- Module Imports ---
# 📚 We need to add the parent directory to the path to import our styling
# and logging modules, as they are located outside of this component's directory.
if str(pathlib.Path(__file__).resolve().parent.parent.parent) not in sys.path:
    sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent.parent))

# Now that the path is set, we can confidently import our logging and theme data.
from configuration.logging import debug_log, console_log
from styling.style import THEMES, DEFAULT_THEME


# --- Global Scope Variables ---
# ⏰ As requested, the version is now hardcoded to the time this file was generated.
# The version strings and numbers below are static and will not change at runtime.
# This represents the date (YYYYMMDD) of file creation.
CURRENT_DATE = 20250822
# This represents the time (HHMMSS) of file creation.
CURRENT_TIME = 213500
# This is a numeric hash of the time, useful for unique IDs.
CURRENT_TIME_HASH = 213500
# Our project's current revision number, which is manually incremented.
REVISION_NUMBER = 1
# Assembling the full version string as per the protocol (W.X.Y).
current_version = "20250822.213500.1"
# Creating a unique integer hash for the current version for internal tracking.
current_version_hash = (CURRENT_DATE * CURRENT_TIME_HASH * REVISION_NUMBER)
# Getting the name of the current file to use in our logs, ensuring it's always accurate.
current_file = f"{os.path.basename(__file__)}"


# --- Constant Variables (No Magic Numbers) ---
COLUMNS = ("Manufacturer", "Model", "Command Type", "Action", "VISA Command", "Variable", "Validated")
EDITABLE_COLUMNS = ["VISA Command", "Variable", "Validated"]
STATUS_DISCONNECTED_TEXT = "Status: Disconnected"
STATUS_DISCONNECTED_COLOR = "red"
CONTROL_FRAME_TEXT = "Controls"
COMMAND_LABEL_TEXT = "Command:"
EXECUTE_BUTTON_TEXT = "Execute"
QUERY_BUTTON_TEXT = "Query"
SET_BUTTON_TEXT = "Set"
DO_BUTTON_TEXT = "Do"
LOAD_DATA_BUTTON_TEXT = "Load Data"
ADD_ROW_BUTTON_TEXT = "Add New Row"
SAVE_DATA_BUTTON_TEXT = "Save Data"
DELETE_ROW_BUTTON_TEXT = "Delete Row"
# A style name for our buttons.
BUTTON_STYLE_NAME = 'TButton'
# A constant for our dynamic topic name.
BASE_TOPIC = "visa_interpreter"


class Translatorframe(ttk.Frame):
    """
    This is the GUI-only version of VisaInterpreterTab. It provides the visual
    layout and interactive elements without any external logic for file
    handling, instrument communication, or logging.
    """
    def __init__(self, parent, *args, **kwargs):
        """
        Initializes the Translatorframe, setting up the GUI and data structures.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        # 🟢 We log the entry into the function with the "mad scientist" personality.
        debug_log(
            message=f"🖥️🟢 Initializing the '{self.__class__.__name__}' GUI frame. The framework is taking shape!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            # --- Function logic goes here ---
            # We call the parent class's constructor, passing in the parent widget.
            super().__init__(parent, *args, **kwargs)
            self.sort_direction = {}
            self.last_selected_item = None
            
            # We apply the global style from our styling/style.py file
            self._apply_styles(theme_name=DEFAULT_THEME)

            # Dummy data for demonstration purposes
            self.data = [
                ["Tektronix", "MDO3000", "Query", "Read", "*IDN?", "", "True"],
                ["Tektronix", "MDO3000", "Action", "Set", "MEASUrement:IMMed:TYPe FREQuency", "", "False"],
                ["Keysight", "34461A", "Query", "Read", ":MEASure:VOLTage:DC?", "", "True"],
                ["Rohde & Schwarz", "HMC8012", "Action", "Do", "*RST", "", "True"],
            ]

            self.create_widgets()
            self.setup_layout()
            self.bind_events()
            self.load_data_to_treeview()
            self._set_ui_initial_state()

            console_log("✅ Celebration of success!")

        except Exception as e:
            # ❌ If an error occurs, we catch it here to prevent the application from crashing.
            console_log(f"❌ Error in {current_function_name}: {e}")
            # We log a detailed error message with our "mad scientist" personality.
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
    def _apply_styles(self, theme_name: str):
        """
        Applies the specified theme to the GUI elements using ttk.Style.
        
        This helper method ensures that all the widgets in this frame use the
        colors and configurations defined in our style.py file.
        """
        # We get the color dictionary from the THEMES defined in style.py
        colors = THEMES.get(theme_name, THEMES["dark"])
        
        style = ttk.Style(self)
        style.theme_use("clam")

        # We configure the default style for all widgets
        style.configure('TFrame', background=colors["bg"])
        style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
        style.configure('TLabelframe', background=colors["bg"], foreground=colors["fg"])
        
        # Configure the Treeview widget specifically
        style.configure('Treeview',
                        background=colors["primary"],
                        foreground=colors["fg"],
                        fieldbackground=colors["primary"],
                        bordercolor=colors["border"])
        
        # Configure the Treeview heading
        style.configure('Treeview.Heading',
                        background=colors["secondary"],
                        foreground=colors["fg"],
                        relief=colors["relief"],
                        borderwidth=colors["border_width"])

        # Configure the Entry widget
        style.configure('TEntry',
                        fieldbackground=colors["primary"],
                        foreground=colors["fg"],
                        bordercolor=colors["border"])
                        
    def _set_ui_initial_state(self):
        """
        Sets the initial disabled/disconnected state of the UI controls.
        """
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        
        # 🟢 Entry log with the appropriate emoji prefix.
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to set initial UI state.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            # --- Function logic goes here ---
            self.status_label.configure(text=STATUS_DISCONNECTED_TEXT, foreground=STATUS_DISCONNECTED_COLOR)
            self.command_entry.config(state=tk.DISABLED)
            self.execute_command_button.config(state=tk.DISABLED)
            self.query_button.config(state=tk.DISABLED)
            self.set_button.config(state=tk.DISABLED)
            self.do_button.config(state=tk.DISABLED)

            console_log("✅ Celebration of success!")

        except Exception as e:
            # ❌ Error handling for this specific function.
            console_log(f"❌ Error in {current_function_name}: {e}")
            # Detailed debug log with the error message.
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def load_data_to_treeview(self):
        """
        Loads data from the internal list into the Treeview widget.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        # 🟢 Entry log with the appropriate emoji prefix.
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to load data.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # --- Function logic goes here ---
            for item in self.treeview.get_children():
                self.treeview.delete(item)
            
            for row in self.data:
                self.treeview.insert('', 'end', values=row)

            console_log("✅ Celebration of success!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def create_widgets(self):
        """
        Creates all the UI widgets for the tab.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to create widgets.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            # --- Function logic goes here ---
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

            self.treeview = ttk.Treeview(tree_frame, columns=COLUMNS, show="headings")
            self.treeview.pack(side="left", fill="both", expand=True)

            for col in COLUMNS:
                # We use named arguments for the command, as per the protocol.
                self.treeview.heading(col, text=col, command=lambda c=col: self._sort_treeview(tv=self.treeview, col=c))
                self.treeview.column(col, anchor="w", width=100)
                self.sort_direction[col] = 'asc'

            scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.treeview.yview)
            self.treeview.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            
            control_frame = ttk.LabelFrame(self, text=CONTROL_FRAME_TEXT)
            control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
            control_frame.columnconfigure(1, weight=1)

            self.status_label = ttk.Label(control_frame, text=STATUS_DISCONNECTED_TEXT, foreground=STATUS_DISCONNECTED_COLOR)
            self.status_label.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=2)

            ttk.Label(control_frame, text=COMMAND_LABEL_TEXT).grid(row=1, column=0, sticky="w", padx=5, pady=2)
            self.command_entry = ttk.Entry(control_frame)
            self.command_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
            # We use named arguments for the command, as per the protocol.
            self.command_entry.bind('<Return>', lambda e: self._on_execute_command(command=self.command_entry.get().strip()))

            button_frame = ttk.Frame(control_frame)
            button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
            for i in range(4): button_frame.columnconfigure(i, weight=1)

            # We use named arguments for the command, as per the protocol.
            self.execute_command_button = ttk.Button(button_frame, text=EXECUTE_BUTTON_TEXT, command=lambda: self._on_execute_command(command=self.command_entry.get().strip()))
            self.execute_command_button.grid(row=0, column=0, sticky="ew", padx=2, pady=2)

            # We use named arguments for the command, as per the protocol.
            self.query_button = ttk.Button(button_frame, text=QUERY_BUTTON_TEXT, command=lambda: self._on_query_command(command=self.command_entry.get().strip()))
            self.query_button.grid(row=0, column=1, sticky="ew", padx=2, pady=2)
            
            # We use named arguments for the command, as per the protocol.
            self.set_button = ttk.Button(button_frame, text=SET_BUTTON_TEXT, command=lambda: self._on_set_command(command=self.command_entry.get().strip()))
            self.set_button.grid(row=0, column=2, sticky="ew", padx=2, pady=2)
            
            # We use named arguments for the command, as per the protocol.
            self.do_button = ttk.Button(button_frame, text=DO_BUTTON_TEXT, command=lambda: self._on_do_command(command=self.command_entry.get().strip()))
            self.do_button.grid(row=0, column=3, sticky="ew", padx=2, pady=2)

            action_frame = ttk.Frame(control_frame)
            action_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
            for i in range(4): action_frame.columnconfigure(i, weight=1)

            # We use named arguments for the command, as per the protocol.
            ttk.Button(action_frame, text=LOAD_DATA_BUTTON_TEXT, command=self.load_data_to_treeview).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
            ttk.Button(action_frame, text=ADD_ROW_BUTTON_TEXT, command=self._add_new_row).grid(row=0, column=1, sticky="ew", padx=2, pady=2)
            ttk.Button(action_frame, text=SAVE_DATA_BUTTON_TEXT, command=self._save_data_dummy).grid(row=0, column=2, sticky="ew", padx=2, pady=2)
            ttk.Button(action_frame, text=DELETE_ROW_BUTTON_TEXT, command=self._delete_selected_row).grid(row=0, column=3, sticky="ew", padx=2, pady=2)
            
            console_log("✅ Celebration of success!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
    def setup_layout(self):
        """
        Configures the grid layout for the main frame.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to configure layout.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            # --- Function logic goes here ---
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)

            console_log("✅ Celebration of success!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )


    def bind_events(self):
        """
        Binds all the necessary UI events to their handlers.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to bind events.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # --- Function logic goes here ---
            self.treeview.bind("<Double-1>", self._on_double_click)
            self.treeview.bind("<<TreeviewSelect>>", self._on_treeview_select)
            self.treeview.bind("<FocusIn>", self._on_treeview_focus)

            console_log("✅ Celebration of success!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _on_treeview_focus(self, event):
        """
        Restores selection when the treeview gains focus.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to restore focus.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # --- Function logic goes here ---
            if not self.treeview.selection() and self.last_selected_item:
                self.treeview.selection_set(self.last_selected_item)
                self.treeview.focus(self.last_selected_item)

            console_log("✅ Celebration of success!")
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _on_treeview_select(self, event):
        """
        Handles row selection, updating the command entry box.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to update command entry.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # --- Function logic goes here ---
            selection = self.treeview.selection()
            if selection:
                self.last_selected_item = selection[0]
                values = self.treeview.item(selection[0], 'values')
                if values:
                    self.command_entry.delete(0, tk.END)
                    if len(values) > 4 and values[4] is not None:
                        self.command_entry.insert(0, values[4])

            console_log("✅ Celebration of success!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _on_double_click(self, event):
        """
        Handles double-click events to enable cell editing.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to initiate cell edit.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # --- Function logic goes here ---
            item = self.treeview.identify_row(event.y)
            col = self.treeview.identify_column(event.x)
            if item and col:
                col_index = int(col.replace('#', '')) - 1
                column_name = self.treeview['columns'][col_index]
                if column_name in EDITABLE_COLUMNS:
                    self._edit_cell(item=item, col_index=col_index)

            console_log("✅ Celebration of success!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _edit_cell(self, item, col_index):
        """
        Creates an entry widget for editing a treeview cell.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to display a cell editor.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # --- Function logic goes here ---
            x, y, width, height = self.treeview.bbox(item, col_index)
            original_text = self.treeview.item(item, 'values')[col_index]

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
                self._save_data_dummy()

            entry.bind("<Return>", on_entry_change)
            entry.bind("<FocusOut>", lambda e: entry.destroy())

            console_log("✅ Celebration of success!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _add_new_row(self):
        """
        Adds a new, empty row to the Treeview and the internal data list.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to add a new row.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # --- Function logic goes here ---
            new_row = [""] * len(COLUMNS)
            self.data.append(new_row)
            self.treeview.insert('', 'end', values=new_row)
            self._save_data_dummy()

            console_log("✅ Celebration of success!")
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _delete_selected_row(self):
        """
        Deletes the currently selected row from the Treeview and internal data.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to delete a row.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # --- Function logic goes here ---
            selected_items = self.treeview.selection()
            if not selected_items:
                return
            
            for item in selected_items:
                values = self.treeview.item(item, 'values')
                self.treeview.delete(item)
                # This check is needed because values can be a mix of strings and other types
                if list(values) in self.data:
                    self.data.remove(list(values))
            
            self._save_data_dummy()

            console_log("✅ Celebration of success!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _save_data_dummy(self):
        """
        This is a dummy function. The actual save logic has been removed.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to perform dummy save.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # --- Function logic goes here ---
            print("GUI Action: Save data (dummy).")
            
            console_log("✅ Celebration of success!")
            
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _sort_treeview(self, tv, col):
        """
        Sorts the treeview column when a heading is clicked.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to sort treeview.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # --- Function logic goes here ---
            items = list(tv.get_children(''))
            
            direction = self.sort_direction.get(col, 'asc')
            reverse = (direction == 'desc')

            # Simple string sort for GUI-only version
            sorted_items = sorted(items, key=lambda x: tv.set(x, col), reverse=reverse)

            for index, item in enumerate(sorted_items):
                tv.move(item, '', index)

            self.sort_direction[col] = 'asc' if reverse else 'desc'
            
            # Reset other column headers
            for c in COLUMNS:
                tv.heading(c, text=c)
            
            # Update current column header with sort indicator
            indicator = ' ▲' if not reverse else ' ▼'
            tv.heading(col, text=col + indicator)

            console_log("✅ Celebration of success!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
    def _on_execute_command(self, command):
        """
        Logs a message for a simulated command execution.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to simulate a command.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            # We construct a dynamic topic name using the class name.
            topic = f"{BASE_TOPIC}/{self.__class__.__name__}/{EXECUTE_BUTTON_TEXT.lower()}"
            console_log(f"Simulating publish to topic: '{topic}' with command: {command}")
            console_log("✅ Celebration of success!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
        
    def _on_query_command(self, command):
        """
        Logs a message for a simulated query command.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to simulate a query.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            # We construct a dynamic topic name using the class name.
            topic = f"{BASE_TOPIC}/{self.__class__.__name__}/{QUERY_BUTTON_TEXT.lower()}"
            console_log(f"Simulating publish to topic: '{topic}' with command: {command}")
            console_log("✅ Celebration of success!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
        
    def _on_set_command(self, command):
        """
        Logs a message for a simulated set command.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to simulate a set.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # We construct a dynamic topic name using the class name.
            topic = f"{BASE_TOPIC}/{self.__class__.__name__}/{SET_BUTTON_TEXT.lower()}"
            console_log(f"Simulating publish to topic: '{topic}' with command: {command}")
            console_log("✅ Celebration of success!")
            
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
        
    def _on_do_command(self, command):
        """
        Logs a message for a simulated do command.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message=f"🖥️🟢 Entering '{current_function_name}' to simulate a do.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # We construct a dynamic topic name using the class name.
            topic = f"{BASE_TOPIC}/{self.__class__.__name__}/{DO_BUTTON_TEXT.lower()}"
            console_log(f"Simulating publish to topic: '{topic}' with command: {command}")
            console_log("✅ Celebration of success!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

def create_visa_interpreter_tab(parent_widget):
    """
    Creates and returns an instance of the VisaInterpreterTab frame.
    """
    current_function_name = inspect.currentframe().f_code.co_name

    try:
        # --- Function logic goes here ---
        frame = Translatorframe(parent_widget)
        return frame
    except Exception as e:
        console_log(f"❌ Error creating VisaInterpreterTab in {current_function_name}: {e}")
        return None
