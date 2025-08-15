# tabs/Presets/tab_presets_child_initial_configuration.py
#
# This file defines the InitialConfigurationTab, a Tkinter Frame that provides
# functionality to manage application configuration settings from config.ini.
# It allows loading default/previous configurations, saving current settings
# to a new file, and viewing/editing the current config directly within the GUI.
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
# Version 20250813.013444.1
#
# Version 20250802.1701.20 (Removed style_obj from kwargs passed to super().__init__.)

current_version = "20250813.013444.1"
current_version_hash = 20250813 * 13444 * 1

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import inspect
import os
import configparser
import datetime
import numpy as np

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

from src.settings_and_config.restore_settings_logic import restore_default_settings_logic, restore_last_used_settings_logic
from src.settings_and_config.config_manager import save_config_as_new_file, save_config

class InitialConfigurationTab(ttk.Frame):
    """
    A Tkinter Frame that provides functionality to manage application configuration
    settings from config.ini. It allows loading default/previous configurations,
    saving current settings to a new file, and viewing/editing the current config.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, style_obj=None, **kwargs):
        # Filter out style_obj from kwargs before passing to super()
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'style_obj'}
        super().__init__(master, **filtered_kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        self.style_obj = style_obj

        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing InitialConfigurationTab. Version: {current_version}. Let's get this config sorted!",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)

        self.edit_entry = None
        self.current_edit_cell = None

        self._create_widgets()
        self._populate_config_table()

        # Bindings are now on the widget itself, not the class.
        # This prevents the AttributeError when the method is not found.
        # The correct binding logic is within _start_edit
        
        debug_log(f"InitialConfigurationTab initialized. Version: {current_version}. Ready for configuration!",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)

    def _create_widgets(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Creating InitialConfigurationTab widgets... Building the interface!",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        
        ttk.Button(button_frame, text="Save Running Configuration", command=self._save_running_config).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Load Default Configuration", command=self._load_default_config).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Load Previous Configuration", command=self._load_previous_config).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        config_table_frame = ttk.LabelFrame(self, text="Current config.ini Contents (Editable)")
        config_table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        config_table_frame.grid_columnconfigure(0, weight=1)
        config_table_frame.grid_rowconfigure(0, weight=1)

        self.config_tree = ttk.Treeview(config_table_frame, columns=("Key", "Value"), show="headings")
        self.config_tree.heading("Key", text="Key", anchor="w")
        self.config_tree.heading("Value", text="Value", anchor="w")

        self.config_tree.column("Key", width=200, stretch=True)
        self.config_tree.column("Value", width=300, stretch=True)

        self.config_tree.grid(row=0, column=0, sticky="nsew")

        tree_scrollbar = ttk.Scrollbar(config_table_frame, orient="vertical", command=self.config_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        self.config_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        push_save_frame = ttk.Frame(self)
        push_save_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        push_save_frame.grid_columnconfigure(0, weight=1)
        push_save_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Button(push_save_frame, text="Push Edits to config.ini", command=self._push_edits_to_file).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(push_save_frame, text="Save Current Config as New File", command=self._save_current_config_as_new_file).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        debug_log("InitialConfigurationTab widgets created. Looking good!",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)
    
    def _push_edits_to_file(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Pushing edits to config.ini. Initiating explicit save. 💾",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)
        
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
        self.console_print_func("✅ Edits pushed to config.ini successfully.")

    def _on_focus_out(self, event):
        if hasattr(self, 'edit_entry') and self.edit_entry and self.edit_entry.winfo_exists():
            editor_bbox = self.edit_entry.winfo_rootx(), self.edit_entry.winfo_rooty(), self.edit_entry.winfo_rootx() + self.edit_entry.winfo_width(), self.edit_entry.winfo_rooty() + self.edit_entry.winfo_height()
            x, y = self.winfo_pointerx(), self.winfo_pointery()
            if not (editor_bbox[0] <= x <= editor_bbox[2] and editor_bbox[1] <= y <= editor_bbox[3]):
                self._end_edit()
    
    def _populate_config_table(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Populating config table... Filling with data!",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)

        for item in self.config_tree.get_children():
            self.config_tree.delete(item)

        for section in self.app_instance.config.sections():
            section_id = self.config_tree.insert("", "end", text=f"[{section}]", open=True, tags=("section",))
            self.config_tree.tag_configure("section", font=("Helvetica", 10, "bold"))

            for key, value in self.app_instance.config.items(section):
                self.config_tree.insert(section_id, "end", values=(key, value), tags=("editable",))
        debug_log("Config table populated. All set!",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)
    
    def _on_double_click_edit(self, event):
        current_function = inspect.currentframe().f_code.co_name
        region = self.config_tree.identify("region", event.x, event.y)
        if region == "heading":
            debug_log("Attempted to edit heading. Not allowed, you cheeky bastard!",
                        file=f"{os.path.basename(__file__)}",
                        version=current_function)
            return
        column = self.config_tree.identify_column(event.x)
        if column != "#2":
            debug_log("Attempted to edit non-value column. Stick to the values!",
                        file=f"{os.path.basename(__file__)}",
                        version=current_function)
            return
        item_id = self.config_tree.identify_row(event.y)
        if not item_id:
            debug_log("No item selected for editing. Pick something!",
                        file=f"{os.path.basename(__file__)}",
                        version=current_function)
            return
        if "section" in self.config_tree.item(item_id, "tags"):
            debug_log("Attempted to edit section header. That's a no-go!",
                        file=f"{os.path.basename(__file__)}",
                        version=current_function)
            return

        self._start_edit(item_id, column)

    def _start_edit(self, item_id, column_id):
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Starting edit for a cell. A temporary editor will appear.",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)
        
        if hasattr(self, 'edit_entry') and self.edit_entry and self.edit_entry.winfo_exists():
            self._end_edit()
        
        x, y, width, height = self.config_tree.bbox(item_id, column_id)
        current_value = self.config_tree.item(item_id, 'values')[1]

        self.edit_entry = ttk.Entry(self.config_tree, style='TEntry')
        self.edit_entry.place(x=x, y=y, width=width, height=height, anchor="nw")
        self.edit_entry.insert(0, current_value)
        self.edit_entry.focus_set()
        self.edit_entry.select_range(0, tk.END)

        self.current_edit_cell = (item_id, column_id)
        
        self.edit_entry.bind("<Return>", self._on_edit_return)
        self.edit_entry.bind("<FocusOut>", self._on_focus_out_editor)
        self.edit_entry.bind("<Escape>", self._on_edit_escape)
    
    def _on_edit_return(self, event):
        self._end_edit()
        if self.current_edit_cell:
            self._navigate_and_edit(self.current_edit_cell[0], self.current_edit_cell[1], "down")

    def _on_edit_escape(self, event):
        if self.edit_entry and self.edit_entry.winfo_exists():
            self.edit_entry.destroy()
            self.current_edit_cell = None
            self.config_tree.focus_set()

    def _on_focus_out_editor(self, event):
        self._end_edit()

    def _end_edit(self):
        current_function = inspect.currentframe().f_code.co_name
        if not hasattr(self, 'edit_entry') or not self.edit_entry or not self.edit_entry.winfo_exists() or not self.current_edit_cell:
            return
        
        item_id, column_id = self.current_edit_cell
        new_value = self.edit_entry.get()
        self.edit_entry.destroy()
        self.current_edit_cell = None
        
        self._save_edit(item_id, column_id, new_value)

    def _save_edit(self, item_id, column_id, new_value):
        current_function = inspect.currentframe().f_code.co_name
        
        values = list(self.config_tree.item(item_id, 'values'))
        old_value = values[1]
        
        if new_value == old_value:
            return
            
        values[1] = new_value
        self.config_tree.item(item_id, values=values)
        
        key = values[0]
        parent_id = self.config_tree.parent(item_id)
        section_name = self.config_tree.item(parent_id, "text").strip('[]')
        
        self.app_instance.config[section_name][key] = new_value

        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
        self._update_tkinter_var_from_config(section_name, key, new_value)

        self.console_print_func(f"✅ Updated config: [{section_name}]{key} = {new_value}. Saved to file.")
        debug_log(f"Config updated for [{section_name}]{key}. Saved to file. ✅",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)

    def _navigate_and_edit(self, current_item_id, current_col_id, direction):
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Navigating to the next cell and starting a new edit. 🏃‍♀️", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        
        parent = self.config_tree.parent(current_item_id)
        children = self.config_tree.get_children(parent)
        
        try:
            current_index = children.index(current_item_id)
            next_index = current_index + 1
            
            if next_index < len(children):
                next_item_id = children[next_index]
                self.config_tree.selection_set(next_item_id)
                self.config_tree.focus(next_item_id)
                self._start_edit(next_item_id, current_col_id)
            else:
                self.console_print_func("ℹ️ End of section reached. No more cells to edit.")
                debug_log("End of section reached. No more cells to edit.", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        except ValueError:
            self.console_print_func("❌ Error during navigation. The selected item could not be found.")
            debug_log("ValueError: The selected item could not be found in its parent's children. 🤯", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
    
    def _update_tkinter_var_from_config(self, section_name, key, new_value_str):
        current_function = inspect.currentframe().f_code.co_name
        
        found_match = False
        for var_key, var_info in self.app_instance.setting_var_map.items():
            if var_info['section'] == section_name and var_info['key'] == key:
                found_match = True
                try:
                    tk_var_instance = var_info['var']
                    if isinstance(tk_var_instance, tk.BooleanVar):
                        tk_var_instance.set(new_value_str.lower() == 'true')
                    elif isinstance(tk_var_instance, tk.IntVar):
                        tk_var_instance.set(int(float(new_value_str)))
                    elif isinstance(tk_var_instance, tk.DoubleVar):
                        tk_var_instance.set(float(new_value_str))
                    elif isinstance(tk_var_instance, tk.StringVar):
                        tk_var_instance.set(new_value_str)
                    
                    debug_log(f"Synced Tkinter var '{var_key}' to '{new_value_str}'. GUI updated! ✅",
                                file=f"{os.path.basename(__file__)}",
                                version=current_version,
                                function=current_function)
                    
                    if var_key == 'notes_var' and hasattr(self.app_instance, 'scanning_parent_tab') and hasattr(self.app_instance.scanning_parent_tab, 'scan_meta_data_tab'):
                        notes_widget = self.app_instance.scanning_parent_tab.scan_meta_data_tab.notes_text
                        notes_widget.delete("1.0", tk.END)
                        notes_widget.insert("1.0", new_value_str)
                        debug_log("Updated notes_text_widget from config edit. Looking good! 👍",
                                    file=f"{os.path.basename(__file__)}",
                                    version=current_version,
                                    function=current_function)
                    
                    break
                except ValueError as e:
                    self.console_print_func(f"❌ Error syncing Tkinter var '{var_key}': {e}. Invalid value!")
                    debug_log(f"Error syncing Tkinter var '{var_key}': {e}. What a pain! 🤯",
                                file=f"{os.path.basename(__file__)}",
                                version=current_version,
                                function=current_function)
                    
                except Exception as e:
                    self.console_print_func(f"❌ Unexpected error syncing Tkinter var '{var_key}': {e}. This is a disaster!")
                    debug_log(f"Unexpected error syncing Tkinter var '{var_key}': {e}. Fucking hell! 💥",
                                file=f"{os.path.basename(__file__)}",
                                version=current_version,
                                function=current_function)
        
        if not found_match:
            debug_log(f"No corresponding Tkinter variable found in setting_var_map for key '{key}' in section '{section_name}'. Skipping sync. 🤷‍♀️", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)


    def _load_default_config(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Loading default configuration... Getting back to basics!",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)
        restore_default_settings_logic(self.app_instance, self.console_print_func)
        self._populate_config_table()
        self.console_print_func("✅ Default configuration loaded and applied. Fresh start!")
        self.app_instance.update_idletasks()
        for parent_tab_name, parent_tab_widget in self.app_instance.parent_tab_widgets.items():
            if hasattr(parent_tab_widget, '_on_tab_selected'):
                parent_tab_widget._on_tab_selected(None)
        debug_log("Default config loaded and GUI refreshed. All good!",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)


    def _load_previous_config(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Loading previous configuration... Back to where we were!",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)
        restore_last_used_settings_logic(self.app_instance, self.console_print_func)
        self._populate_config_table()
        self.console_print_func("✅ Previous configuration loaded and applied. Familiar territory!")
        self.app_instance.update_idletasks()
        for parent_tab_name, parent_tab_widget in self.app_instance.parent_tab_widgets.items():
            if hasattr(parent_tab_widget, '_on_tab_selected'):
                parent_tab_widget._on_tab_selected(None)
        debug_log("Previous config loaded and GUI refreshed. Good to be back!",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)


    def _save_current_config_as_new_file(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Saving current config as new file... Let's make a copy!",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)

        file_path = filedialog.asksaveasfilename(
            defaultextension=".ini",
            filetypes=[("INI files", "*.ini"), ("All files", "*.*")],
            title="Save Configuration As",
            initialfile="custom_config.ini"
        )
        if file_path:
            try:
                save_config_as_new_file(self.app_instance.config, file_path, self.console_print_func)
                self.console_print_func(f"✅ Configuration saved to: {file_path}. Success!")
                debug_log(f"Configuration saved to new file: {file_path}. File created!",
                            file=f"{os.path.basename(__file__)}",
                            version=current_version,
                            function=current_function)
            except Exception as e:
                self.console_print_func(f"❌ Error saving configuration to new file: {e}. This is a disaster!")
                debug_log(f"Error saving configuration to new file '{file_path}': {e}. Fucking hell!",
                            file=f"{os.path.basename(__file__)}",
                            version=current_version,
                            function=current_function)
        else:
            self.console_print_func("ℹ️ Configuration save cancelled. Fine, be that way!")
            debug_log("Configuration save cancelled. What a waste!",
                        file=f"{os.path.basename(__file__)}",
                        version=current_version,
                        function=current_function)

    def _on_tab_selected(self, event):
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Initial Configuration Tab selected. Refreshing table... Let's get this updated!",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)
        self._populate_config_table()

    def _save_running_config(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Manual save of running configuration requested. Triggering immediate save. 💾",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)
        
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
        self.console_print_func("✅ Running configuration saved successfully.")
        self._populate_config_table()