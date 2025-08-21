# tabs/Experiments/tab_experiments_child_initial_configuration.py
#
# This file defines the InitialConfigurationTab, a child tab for the Experiments
# section. It provides a GUI for viewing and editing the application's configuration
# file in a user-friendly manner, allowing for dynamic updates without restarting.
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
# Version 20250821.112000.1
# NEW: Created a new child tab for managing the initial configuration.
# FIXED: Corrected the load_config call to use the proper arguments, resolving the TypeError.

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import inspect
import os
from configparser import ConfigParser

# Import logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

# Import config management functions
from settings_and_config.config_manager import load_config, save_config
from settings_and_config.program_default_values import DEFAULT_CONFIG, DATA_FOLDER_PATH

# --- Version Information ---
w = 20250821
x_str = '112000'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"


class InitialConfigurationTab(ttk.Frame):
    def __init__(self, master=None, app_instance=None, console_print_func=None, style_obj=None, **kwargs):
        # This function description tells me what this function does
        # Initializes the InitialConfigurationTab, a Tkinter Frame for viewing and
        # editing the application's configuration.
        #
        # Inputs to this function
        #   master (tk.Widget): The parent widget, typically a ttk.Notebook.
        #   app_instance (object): A reference to the main application instance.
        #   console_print_func (function): A function to print messages to the console.
        #   style_obj (ttk.Style): The application's style object.
        #   **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        #
        # Outputs of this function
        #   None. Initializes the Tkinter frame and its internal state.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"📕🟢 Initializing InitialConfigurationTab...",
                  file=current_file, version=current_version, function=current_function)

        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func
        self.style_obj = style_obj
        self.config_file_path = self.app_instance.CONFIG_FILE_PATH
        self.config_data = None
        self.config_text_widget = None

        self._create_widgets()
        self._populate_config_table()
        
        debug_log(f"📕✅ InitialConfigurationTab initialized.",
                  file=current_file, version=current_version, function=current_function)

    def _create_widgets(self):
        # This function description tells me what this function does
        # Creates and lays out the widgets for the configuration tab, including a
        # text area for displaying the config and buttons for saving and reloading.
        #
        # Inputs to this function
        #   None.
        #
        # Outputs of this function
        #   None. Populates the tab with GUI elements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"📕🟢 Creating widgets for InitialConfigurationTab.",
                  file=current_file, version=current_version, function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        control_frame = ttk.Frame(self)
        control_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        
        save_button = ttk.Button(control_frame, text="Save Config", command=self._save_config_action, style='Green.TButton')
        save_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        reload_button = ttk.Button(control_frame, text="Reload Config", command=self._reload_config_action, style='Orange.TButton')
        reload_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.config_text_widget = scrolledtext.ScrolledText(self, wrap="word", height=25, bg="#2b2b2b", fg="#cccccc", insertbackground="white", font=("Courier", 10))
        self.config_text_widget.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        debug_log(f"📕✅ Widgets created.",
                  file=current_file, version=current_version, function=current_function)
    
    def _populate_config_table(self):
        # This function description tells me what this function does
        # Reads the config file and populates the text widget with its content.
        #
        # Inputs to this function
        #   None.
        #
        # Outputs of this function
        #   None. Updates the text widget with the config file content.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"📕🟢 Populating config table from file: {self.config_file_path}",
                  file=current_file, version=current_version, function=current_function)

        try:
            # FIXED: Corrected the load_config call to match the function's signature
            # It now passes the DEFAULT_CONFIG dictionary and the file path as separate arguments.
            self.config_data, _, _ = load_config(DEFAULT_CONFIG, self.config_file_path)

            self.config_text_widget.config(state=tk.NORMAL)
            self.config_text_widget.delete('1.0', tk.END)
            
            with open(self.config_file_path, 'r') as f:
                content = f.read()
                self.config_text_widget.insert(tk.END, content)
            
            self.config_text_widget.config(state=tk.DISABLED)
            
            debug_log(f"📕✅ Config table populated successfully.",
                      file=current_file, version=current_version, function=current_function)

        except Exception as e:
            console_log(f"❌ Error populating config table: {e}")
            debug_log(f"📕🔴 Failed to populate config table. Error: {e}",
                      file=current_file, version=current_version, function=current_function)
    
    def _save_config_action(self):
        # This function description tells me what this function does
        # Handles the action of saving the edited config back to the file.
        #
        # Inputs to this function
        #   None.
        #
        # Outputs of this function
        #   None. Saves the config file.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"📕🟢 Attempting to save config file...",
                  file=current_file, version=current_version, function=current_function)

        try:
            current_content = self.config_text_widget.get('1.0', tk.END)
            # This is a dangerous operation - it overwrites the config
            # We'll re-implement a safer save later, but for now this works.
            with open(self.config_file_path, 'w') as f:
                f.write(current_content)
            
            console_log(f"✅ Configuration saved successfully! You'll need to restart to see all changes take effect.")
            debug_log(f"📕✅ Configuration saved. Arrr, the treasure be safely stowed! ⚓️",
                      file=current_file, version=current_version, function=current_function)

        except Exception as e:
            console_log(f"❌ Error saving configuration: {e}")
            debug_log(f"📕🔴 Failed to save configuration. Error: {e}",
                      file=current_file, version=current_version, function=current_function)

    def _reload_config_action(self):
        # This function description tells me what this function does
        # Handles the action of reloading the config file from disk.
        #
        # Inputs to this function
        #   None.
        #
        # Outputs of this function
        #   None. Reloads the config file and updates the text widget.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"📕🟢 Reloading config from disk...",
                  file=current_file, version=current_version, function=current_function)
        
        self._populate_config_table()
        
        console_log("✅ Configuration reloaded from disk.")
        debug_log(f"📕✅ Reloaded config. The map be fresh! 🗺️",
                  file=current_file, version=current_version, function=current_function)