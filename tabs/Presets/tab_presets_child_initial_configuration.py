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
#
#
# Version 20250801.1920.1 (Updated header to reflect circular import fix.)

current_version = "20250801.1920.1" # this variable should always be defined below the header to make the debugging better

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import inspect
import os
import configparser

from utils.utils_instrument_control import debug_print
from src.settings_logic import restore_default_settings_logic, restore_last_used_settings_logic
from src.config_manager import save_config_as_new_file # Will be added in config_manager.py

class InitialConfigurationTab(ttk.Frame):
    """
    A Tkinter Frame that provides functionality to manage application configuration
    settings from config.ini. It allows loading default/previous configurations,
    saving current settings to a new file, and viewing/editing the current config.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the InitialConfigurationTab.

        Inputs:
            master (tk.Widget): The parent widget.
            app_instance (App): The main application instance, used for accessing
                                shared state like its config object and console print function.
            console_print_func (function): Function to print messages to the GUI console.
            **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        """
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else print

        self._create_widgets()
        self._populate_config_table() # Populate table on initialization

    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Initial Configuration tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Creating InitialConfigurationTab widgets...", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Configure grid for the main frame of this tab
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Buttons frame
        self.grid_rowconfigure(1, weight=1) # Config table frame

        # --- Buttons Frame ---
        button_frame = ttk.Frame(self)
        button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)

        ttk.Button(button_frame, text="Load Default Configuration", command=self._load_default_config).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Load Previous Configuration", command=self._load_previous_config).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Save Current Config as New File", command=self._save_current_config_as_new_file).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # --- Config Table Frame ---
        config_table_frame = ttk.LabelFrame(self, text="Current config.ini Contents (Editable)")
        config_table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        config_table_frame.grid_columnconfigure(0, weight=1)
        config_table_frame.grid_rowconfigure(0, weight=1)

        # Treeview for displaying config
        self.config_tree = ttk.Treeview(config_table_frame, columns=("Key", "Value"), show="headings")
        self.config_tree.heading("Key", text="Key", anchor="w")
        self.config_tree.heading("Value", text="Value", anchor="w")

        self.config_tree.column("Key", width=200, stretch=True)
        self.config_tree.column("Value", width=300, stretch=True)

        self.config_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar for Treeview
        tree_scrollbar = ttk.Scrollbar(config_table_frame, orient="vertical", command=self.config_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        self.config_tree.configure(yscrollcommand=tree_scrollbar.set)

        # Bind double-click for editing
        self.config_tree.bind("<Double-1>", self._on_double_click_edit)

        debug_print("InitialConfigurationTab widgets created.", file=current_file, function=current_function, console_print_func=self.console_print_func)

    def _populate_config_table(self):
        """
        Populates the Treeview with the current contents of app_instance.config.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Populating config table...", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Clear existing data
        for item in self.config_tree.get_children():
            self.config_tree.delete(item)

        # Insert data
        for section in self.app_instance.config.sections():
            # Insert section as a parent item
            section_id = self.config_tree.insert("", "end", text=f"[{section}]", open=True, tags=("section",))
            self.config_tree.tag_configure("section", font=("Helvetica", 10, "bold"))

            for key, value in self.app_instance.config.items(section):
                self.config_tree.insert(section_id, "end", values=(key, value), tags=("editable",))
        debug_print("Config table populated.", file=current_file, function=current_function, console_print_func=self.console_print_func)

    def _on_double_click_edit(self, event):
        """
        Handles double-click events on the Treeview to allow editing of values.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__

        region = self.config_tree.identify("region", event.x, event.y)
        if region == "heading": # Don't edit headings
            return

        column = self.config_tree.identify_column(event.x)
        if column != "#2": # Only allow editing the "Value" column
            return

        item_id = self.config_tree.identify_row(event.y)
        if not item_id:
            return

        # Check if it's a section header (not editable)
        if "section" in self.config_tree.item(item_id, "tags"):
            return

        # Get current value
        current_values = self.config_tree.item(item_id, "values")
        if not current_values:
            return

        key = current_values[0]
        old_value = current_values[1]

        # Find the parent section
        parent_id = self.config_tree.parent(item_id)
        section_text = self.config_tree.item(parent_id, "text")
        section_name = section_text.strip('[]')

        debug_print(f"Attempting to edit: Section='{section_name}', Key='{key}', Old Value='{old_value}'", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Create a temporary entry widget for editing
        x, y, width, height = self.config_tree.bbox(item_id, column)
        editor = ttk.Entry(self.config_tree)
        editor.place(x=x, y=y, width=width, height=height, anchor="nw")
        editor.insert(0, old_value)
        editor.focus_set()

        def on_edit_complete(event=None):
            new_value = editor.get()
            editor.destroy()
            if new_value != old_value:
                debug_print(f"Edit complete: New Value='{new_value}'", file=current_file, function=current_function, console_print_func=self.console_print_func)
                try:
                    # Update the Treeview
                    self.config_tree.item(item_id, values=(key, new_value))
                    # Update the app_instance.config object
                    self.app_instance.config[section_name][key] = new_value
                    self.console_print_func(f"✅ Updated config: [{section_name}]{key} = {new_value}")
                    debug_print(f"ConfigParser updated: [{section_name}]{key} = {new_value}", file=current_file, function=current_function, console_print_func=self.console_print_func)

                    # Trigger a save to the main config.ini file immediately
                    # This ensures the changes are persistent
                    self.app_instance.save_config(self.app_instance) # Call save_config from main_app

                    # Attempt to update the corresponding Tkinter variable if mapped
                    self._update_tkinter_var_from_config(section_name, key, new_value)

                except Exception as e:
                    self.console_print_func(f"❌ Error updating config: {e}")
                    debug_print(f"Error updating config: {e}", file=current_file, function=current_function, console_print_func=self.console_print_func)
            else:
                debug_print("Value not changed.", file=current_file, function=current_function, console_print_func=self.console_print_func)

        editor.bind("<Return>", on_edit_complete)
        editor.bind("<FocusOut>", on_edit_complete)

    def _update_tkinter_var_from_config(self, section_name, key, new_value_str):
        """
        Attempts to update the corresponding Tkinter variable if a mapping exists.
        This is crucial for keeping the GUI in sync with direct config edits.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__

        # Iterate through the setting_var_map to find a match
        for tk_var_name, (last_key, default_key, tk_var_instance) in self.app_instance.setting_var_map.items():
            # Check if the key matches either the last_key or default_key
            # We need to map config keys to the variable names.
            # This logic is a bit complex as setting_var_map uses both last_key and default_key.
            # For simplicity, let's assume direct mapping or a more robust lookup.
            # A better approach might be to have a reverse map or a clearer naming convention.

            # Simple approach: Check if the key is present in either last_key or default_key
            # This is a heuristic and might need refinement if keys are not unique.
            if last_key == key or default_key == key:
                try:
                    if isinstance(tk_var_instance, tk.BooleanVar):
                        tk_var_instance.set(new_value_str.lower() == 'true')
                    elif isinstance(tk_var_instance, tk.IntVar):
                        tk_var_instance.set(int(float(new_value_str)))
                    elif isinstance(tk_var_instance, tk.DoubleVar):
                        tk_var_instance.set(float(new_value_str))
                    elif isinstance(tk_var_instance, tk.StringVar):
                        tk_var_instance.set(new_value_str)
                    self.console_print_func(f"✅ Synced Tkinter var '{tk_var_name}' with new config value.")
                    debug_print(f"Synced Tkinter var '{tk_var_name}' to '{new_value_str}'", file=current_file, function=current_function, console_print_func=self.console_print_func)

                    # Special handling for notes_var if it's a ScrolledText
                    if tk_var_name == 'notes_var' and hasattr(self.app_instance, 'scanning_parent_tab') and hasattr(self.app_instance.scanning_parent_tab, 'scan_meta_data_tab') and hasattr(self.app_instance.scanning_parent_tab.scan_meta_data_tab, 'notes_text_widget'):
                        self.app_instance.scanning_parent_tab.scan_meta_data_tab.notes_text_widget.delete("1.0", tk.END)
                        self.app_instance.scanning_parent_tab.scan_meta_data_tab.notes_text_widget.insert("1.0", new_value_str)
                        debug_print("Updated notes_text_widget from config edit.", file=current_file, function=current_function, console_print_func=self.console_print_func)

                    # For band selections, if the key is 'last_selected_bands' or 'default_selected_bands'
                    # This needs to be handled via the ScanConfigurationTab
                    if (key == 'last_scan_configuration__selected_bands' or
                        key == 'default_scan_configuration__selected_bands'):
                        if hasattr(self.app_instance, 'scanning_parent_tab') and hasattr(self.app_instance.scanning_parent_tab, 'scan_configuration_tab'):
                            self.app_instance.scanning_parent_tab.scan_configuration_tab._load_band_selections_from_config() # Reload checkboxes
                            debug_print("Reloaded band selections in Scan Configuration Tab after config edit.", file=current_file, function=current_function, console_print_func=self.console_print_func)

                    break # Found and updated the variable
                except ValueError as e:
                    self.console_print_func(f"❌ Error syncing Tkinter var '{tk_var_name}': {e}")
                    debug_print(f"Error syncing Tkinter var '{tk_var_name}': {e}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                except Exception as e:
                    self.console_print_func(f"❌ Unexpected error syncing Tkinter var '{tk_var_name}': {e}")
                    debug_print(f"Unexpected error syncing Tkinter var '{tk_var_name}': {e}", file=current_file, function=current_function, console_print_func=self.console_print_func)

    def _load_default_config(self):
        """
        Loads the default configuration settings into the application and refreshes the table.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Loading default configuration...", file=current_file, function=current_function, console_print_func=self.console_print_func)
        restore_default_settings_logic(self.app_instance, self.console_print_func)
        self._populate_config_table() # Refresh the table
        self.console_print_func("✅ Default configuration loaded and applied.")
        # Ensure all tabs that display settings are refreshed
        self.app_instance.update_idletasks()
        # Iterate through parent tabs and then their child tabs to trigger _on_tab_selected
        for parent_tab_name, parent_tab_widget in self.app_instance.parent_tab_widgets.items():
            if hasattr(parent_tab_widget, '_on_tab_selected'):
                parent_tab_widget._on_tab_selected(None) # Trigger parent tab's refresh
        debug_print("Default config loaded and GUI refreshed.", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def _load_previous_config(self):
        """
        Loads the last used configuration settings into the application and refreshes the table.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Loading previous configuration...", file=current_file, function=current_function, console_print_func=self.console_print_func)
        restore_last_used_settings_logic(self.app_instance, self.console_print_func)
        self._populate_config_table() # Refresh the table
        self.console_print_func("✅ Previous configuration loaded and applied.")
        # Ensure all tabs that display settings are refreshed
        self.app_instance.update_idletasks()
        # Iterate through parent tabs and then their child tabs to trigger _on_tab_selected
        for parent_tab_name, parent_tab_widget in self.app_instance.parent_tab_widgets.items():
            if hasattr(parent_tab_widget, '_on_tab_selected'):
                parent_tab_widget._on_tab_selected(None) # Trigger parent tab's refresh
        debug_print("Previous config loaded and GUI refreshed.", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def _save_current_config_as_new_file(self):
        """
        Saves the current application configuration to a new config.ini file chosen by the user.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Saving current config as new file...", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Before saving, ensure the app_instance.config object is fully up-to-date
        # by calling the main app's save_config method without writing to file yet.
        # This updates the in-memory config object.
        # Note: app_instance.save_config is designed to save to the default path.
        # For "Save As", we need to ensure the in-memory config is current, then use save_config_as_new_file.
        # The app_instance.save_config method implicitly updates the in-memory config from Tkinter vars.
        # So, we can directly proceed to ask for file path and use save_config_as_new_file.

        file_path = filedialog.asksaveasfilename(
            defaultextension=".ini",
            filetypes=[("INI files", "*.ini"), ("All files", "*.*")],
            title="Save Configuration As",
            initialfile="custom_config.ini"
        )
        if file_path:
            try:
                # Use the new utility function to save the current in-memory config to the chosen file
                save_config_as_new_file(self.app_instance.config, file_path, self.console_print_func)
                self.console_print_func(f"✅ Configuration saved to: {file_path}")
                debug_print(f"Configuration saved to new file: {file_path}", file=current_file, function=current_function, console_print_func=self.console_print_func)
            except Exception as e:
                self.console_print_func(f"❌ Error saving configuration to new file: {e}")
                debug_print(f"Error saving configuration to new file '{file_path}': {e}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        else:
            self.console_print_func("ℹ️ Configuration save cancelled.")
            debug_print("Configuration save cancelled.", file=current_file, function=current_function, console_print_func=self.console_print_func)

    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Refreshes the config table to show the most current values.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Initial Configuration Tab selected. Refreshing table...", file=current_file, function=current_function, console_print_func=self.console_print_func)
        self._populate_config_table()
