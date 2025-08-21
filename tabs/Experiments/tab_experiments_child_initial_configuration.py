# tabs/Experiments/tab_experiments_child_initial_configuration.py
#
# This file defines the InitialConfigurationTab, a child tab within the Experiments
# parent tab. It provides a user interface for viewing and editing application
# settings stored in the config.ini file, as well as loading and saving configurations.
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
# Version 20250824.110500.1
# REFACTORED: Converted to use the new `restore_settings_logic` for saving/loading.
# FIXED: Replaced old `config_manager` functions with new `restore_settings` functions.
# FIXED: Corrected the KeyError that occurred when accessing non-existent dictionary keys.

import os
import inspect
from tkinter import ttk, filedialog
import tkinter as tk
from datetime import datetime
import configparser
import numpy as np

from display.console_logic import console_log
from display.debug_logic import debug_log
from src.settings_and_config.config_manager import load_config, save_config
from src.settings_and_config.program_default_values import CONFIG_FILE_PATH, DATA_FOLDER_PATH
# FIXED: Corrected import names from `restore_settings_logic`
from src.settings_and_config.restore_settings_logic import restore_default_settings, restore_last_used_settings
from src.program_style import COLOR_PALETTE


# --- Versioning ---
w = 20250824
x_str = '110500'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"{w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"


class InitialConfigurationTab(ttk.Frame):
    """
    A tab for viewing and editing the application's configuration.
    """
    def __init__(self, master, app_instance, console_print_func, style_obj):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📘🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
        super().__init__(master, style='TFrame')
        self.master = master
        self.app_instance = app_instance
        self.console_print_func = console_print_func
        self.style_obj = style_obj
        self.config_data = None
        self.editor = None
        self.config_file_path = CONFIG_FILE_PATH

        self._create_widgets()
        self._populate_config_table()
        
        self.master.bind('<<NotebookTabChanged>>', self._on_tab_selected, add='+')
        debug_log(message=f"📘✅ Exiting {current_function}", file=current_file, version=current_version, function=current_function)

    def _create_widgets(self):
        """
        Builds the UI elements for the configuration tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📘🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
        
        # Main layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Controls Frame
        control_frame = ttk.Frame(self, style='TFrame')
        control_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        
        # Buttons
        ttk.Button(control_frame, text="Load Default Config", command=self._load_default_config).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Load Last Used Config", command=self._load_previous_config).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Save Running Config", command=self._save_running_config).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Save Config As New File", command=self._save_current_config_as_new_file).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Push Edits to File", command=self._push_edits_to_file).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Treeview for config display
        tree_frame = ttk.Frame(self, style='TFrame')
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=("Parameter", "Value", "Notes"), show="headings", style='Dark.Treeview')
        self.tree.heading("Parameter", text="Parameter")
        self.tree.heading("Value", text="Value")
        self.tree.heading("Notes", text="Notes")
        
        self.tree.column("Parameter", width=250)
        self.tree.column("Value", width=200)
        self.tree.column("Notes", width=400)

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<Double-1>", self._on_double_click_edit)
        self.tree.bind("<Return>", self._on_edit_return)
        self.tree.bind("<Escape>", self._on_edit_escape)
        
        debug_log(message=f"📘✅ Exiting {current_function}", file=current_file, version=current_version, function=current_function)

    def _populate_config_table(self):
        """
        Loads the current config into the treeview.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📘🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
        
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.config_data = load_config(self.config_file_path, self.console_print_func)
        
        for section in self.config_data.sections():
            self.tree.insert("", "end", text=section, values=(section, "", ""), open=False)
            section_id = self.tree.get_children()[-1]
            for key, value in self.config_data.items(section):
                self.tree.insert(section_id, "end", values=(key, value, ""))

        debug_log(message=f"📘✅ Exiting {current_function}", file=current_file, version=current_version, function=current_function)

    def _on_double_click_edit(self, event):
        """
        Enables in-cell editing on double-click.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📘🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
        
        item_id = self.tree.identify_row(event.y)
        column_id = self.tree.identify_column(event.x)
        
        if not item_id or column_id != "#2":
            return
            
        column_index = int(column_id.replace('#', '')) - 1
        item_values = self.tree.item(item_id, 'values')
        
        if self.tree.parent(item_id):  # Only allow editing for child items (key-value pairs)
            self._start_edit(item_id, column_index, item_values)
        
        debug_log(message=f"📘✅ Exiting {current_function}", file=current_file, version=current_version, function=current_function)
    
    def _start_edit(self, item_id, column_index, item_values):
        """
        Creates an entry widget for editing a cell's value.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📘🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
        
        x, y, width, height = self.tree.bbox(item_id, column=column_index)
        
        # Check if an editor already exists
        if self.editor:
            self.editor.destroy()
            
        self.editor = ttk.Entry(self.tree, style='TEntry')
        self.editor.insert(0, item_values[column_index])
        self.editor.bind("<Return>", lambda e, item_id=item_id, column_index=column_index: self._on_edit_return(e, item_id, column_index))
        self.editor.bind("<Escape>", self._on_edit_escape)
        self.editor.place(x=x, y=y, width=width, height=height)
        self.editor.focus_set()
        
        debug_log(message=f"📘✅ Exiting {current_function}", file=current_file, version=current_version, function=current_function)

    def _end_edit(self):
        """
        Destroys the editor widget.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📘🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
        if self.editor:
            self.editor.destroy()
            self.editor = None
        debug_log(message=f"📘✅ Exiting {current_function}", file=current_file, version=current_version, function=current_function)

    def _on_edit_return(self, event, item_id=None, column_index=None):
        """
        Saves the edited value and updates the treeview.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📘🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)

        new_value = self.editor.get()
        item = self.tree.focus()
        
        self._save_edit(item, 1, new_value) # Column index 1 is the 'Value' column
        self._end_edit()

        debug_log(message=f"📘✅ Exiting {current_function}", file=current_file, version=current_version, function=current_function)
        
    def _on_edit_escape(self, event):
        """
        Discards the edit and destroys the editor.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📘🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
        self._end_edit()
        debug_log(message=f"📘✅ Exiting {current_function}", file=current_file, version=current_version, function=current_function)

    def _save_edit(self, item_id, column_index, new_value):
        """
        Updates the treeview and the in-memory config object.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📘🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
        
        parent_id = self.tree.parent(item_id)
        if parent_id:
            section = self.tree.item(parent_id, 'values')[0]
            key = self.tree.item(item_id, 'values')[0]
            old_value = self.tree.item(item_id, 'values')[column_index]

            if self.config_data.has_section(section) and self.config_data.has_option(section, key):
                self.config_data.set(section, key, new_value)
                self.tree.item(item_id, values=(key, new_value, ""))
                self.console_print_func(f"✅ Changed setting '{key}' from '{old_value}' to '{new_value}' in section '{section}'.")
                debug_log(message=f"📘📝 Saved edit for key '{key}' in section '{section}' to value '{new_value}'.", file=current_file, version=current_version, function=current_function)
            else:
                self.console_print_func(f"❌ Error: Key '{key}' not found in section '{section}'. Cannot save.")
        
        debug_log(message=f"📘✅ Exiting {current_function}", file=current_file, version=current_version, function=current_function)

    def _load_default_config(self):
        """
        Loads the factory default configuration into the application.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📘🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
        
        # CORRECTED: Use the correct function name.
        restore_default_settings(self.app_instance, self.console_print_func)
        self._populate_config_table()
        
        debug_log(message=f"📘✅ Exiting {current_function}", file=current_file, version=current_version, function=current_function)
        
    def _load_previous_config(self):
        """
        Loads the last used configuration into the application.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📘🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
        
        # CORRECTED: Use the correct function name.
        restore_last_used_settings(self.app_instance, self.console_print_func)
        self._populate_config_table()
        
        debug_log(message=f"📘✅ Exiting {current_function}", file=current_file, version=current_version, function=current_function)
        
    def _save_running_config(self):
        """
        Saves the currently loaded configuration to the main config file.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📘🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)

        save_config(self.config_data, self.config_file_path, self.console_print_func, self.app_instance)
        
        debug_log(message=f"📘✅ Exiting {current_function}", file=current_file, version=current_version, function=current_function)

    def _save_current_config_as_new_file(self):
        """
        Saves the currently loaded configuration to a new file.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📘🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".ini",
            initialdir=DATA_FOLDER_PATH,
            title="Save Configuration As...",
            filetypes=[("INI files", "*.ini"), ("All files", "*.*")]
        )
        
        if file_path:
            save_config(self.config_data, file_path, self.console_print_func, self.app_instance)
            
        debug_log(message=f"📘✅ Exiting {current_function}", file=current_file, version=current_version, function=current_function)

    def _push_edits_to_file(self):
        """
        Pushes all in-memory changes to the config file.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📘🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
        
        try:
            with open(self.config_file_path, 'w') as configfile:
                self.config_data.write(configfile)
            self.console_print_func("✅ In-memory changes saved to config.ini.")
            debug_log(message=f"📘📝 All in-memory edits written to '{self.config_file_path}'.", file=current_file, version=current_version, function=current_function)
        except Exception as e:
            self.console_print_func(f"❌ Error saving changes to file: {e}")
            debug_log(message=f"📘❌ Failed to push in-memory changes to file. Error: {e}", file=current_file, version=current_version, function=current_function)
            
        debug_log(message=f"📘✅ Exiting {current_function}", file=current_file, version=current_version, function=current_function)
        
    def _on_tab_selected(self, event):
        """
        Handles the tab selection event for this notebook.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📘🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
        
        selected_tab_id = self.master.select()
        selected_tab_name = self.master.tab(selected_tab_id, "text")

        if selected_tab_name == "Initial Configuration":
            self._populate_config_table()
            
        debug_log(message=f"📘✅ Exiting {current_function}", file=current_file, version=current_version, function=current_function)