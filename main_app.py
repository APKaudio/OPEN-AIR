# OPEN-AIR/main_app.py
#
# This is the main entry point for the RF Spectrum Analyzer Controller application.
# It handles initial setup, checks for and installs necessary Python dependencies,
# and then launches the main graphical user interface (GUI).
# This file ensures that the application environment is ready before starting the UI.
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
# Version 20250803.190500.0 (FIXED: Added safety check for config object on closing.)
# Version 20250803.190100.0 (FIXED: Initialized scan_thread attribute to prevent AttributeError on startup.)
# Version 20250803.184800.0 (FIXED: Added path constants to the App instance.)
# Version 20250803.1635.0 (Fixed TypeError: check_and_install_dependencies() missing 1 required positional argument: 'current_app_version'.)
# Version 20250803.1630.0 (Fixed ImportError: cannot import name 'get_clear_console_func' by correcting registration to set_clear_console_func and updated Program Map.)


current_version_string = "20250803.190500.0" 
current_version_hash_value = 20250803 * 190500 * 0

import tkinter as tk
from tkinter import ttk
import os
import sys
import inspect 
import configparser

# Import functions from refactored modules
from src.program_check_Dependancies import check_and_install_dependencies
from src.program_initialization import initialize_program_environment
from src.program_shared_values import setup_tkinter_variables
from src.program_gui_utils import apply_saved_geometry, setup_styles, create_widgets
from src.settings_and_config.config_manager import save_config
from src.debug_logic import debug_log, set_debug_redirectors
from src.console_logic import console_log, set_gui_console_redirector, set_clear_console_func
# CORRECTED: Import all necessary path constants
from src.program_default_values import (
    CONFIG_FILE_PATH, DATA_FOLDER_PATH, PRESETS_FILE_PATH,
    MARKERS_FILE_PATH, VISA_COMMANDS_FILE_PATH, DEBUG_COMMANDS_FILE_PATH
)


class App(tk.Tk):
    """
    The main application class for the RF Spectrum Analyzer Controller.
    """
    def __init__(self):
        super().__init__()
        self.current_version = current_version_string
        self.current_version_hash = current_version_hash_value

        # --- Attach path constants to the instance ---
        self.DATA_FOLDER_PATH = DATA_FOLDER_PATH
        self.CONFIG_FILE_PATH = CONFIG_FILE_PATH
        self.PRESETS_FILE_PATH = PRESETS_FILE_PATH
        self.MARKERS_FILE_PATH = MARKERS_FILE_PATH
        self.VISA_COMMANDS_FILE_PATH = VISA_COMMANDS_FILE_PATH
        self.DEBUG_COMMANDS_FILE_PATH = DEBUG_COMMANDS_FILE_PATH
        
        # --- Initialize runtime state attributes ---
        self.scan_thread = None # Initialize scan_thread to None
        self.is_paused_by_user = False # Initialize pause state
        
        # Also store the console_log function for easy access by callbacks
        self.console_log_func = console_log
        
        self.title(f"OPEN-AIR RF Spectrum Analyzer Controller (v{self.current_version})")
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.style = ttk.Style(self)

        setup_tkinter_variables(self)
        initialize_program_environment(self)
        apply_saved_geometry(self)
        setup_styles(self)
        create_widgets(self)

        if self.console_tab and hasattr(self.console_tab, 'console_text'):
            set_gui_console_redirector(self.console_tab.console_text, self.console_tab.console_text)
            set_debug_redirectors(self.console_tab.console_text, self.console_tab.console_text)
            set_clear_console_func(self.console_tab.clear_console_text)
        
        self.after(100, self._post_gui_setup)

        debug_log(f"App initialized. Version: {self.current_version}. GUI is ready!",
                    file=f"{os.path.basename(__file__)} - {self.current_version}",
                    version=self.current_version,
                    function=inspect.currentframe().f_code.co_name,
                    special=True)

    def _post_gui_setup(self):
        """
        Performs setup tasks that need to run after the Tkinter mainloop has started.
        """
        instrument_tab = self.get_tab_instance("Instrument", "Connection")
        if instrument_tab and hasattr(instrument_tab, '_refresh_devices'):
            instrument_tab._refresh_devices()

    def _on_closing(self):
        """
        Handles the application closing event.
        """
        if hasattr(self, 'config') and self.config:
            save_config(self.config, self.CONFIG_FILE_PATH, console_log, self)
        self.destroy()

    def _on_parent_tab_change(self, event):
        """
        Event handler for when the main (parent) notebook tab is changed.
        """
        selected_tab_id = self.parent_notebook.select()
        selected_tab_widget = self.parent_notebook.nametowidget(selected_tab_id)

        if hasattr(selected_tab_widget, '_on_parent_tab_selected'):
            selected_tab_widget._on_parent_tab_selected(event)

        active_parent_tab_name = self.parent_notebook.tab(selected_tab_id, "text")
        active_parent_tab_instance = self.parent_tab_widgets.get(active_parent_tab_name)

        if active_parent_tab_instance and hasattr(active_parent_tab_instance, 'child_notebook'):
            child_notebook = active_parent_tab_instance.child_notebook
            if child_notebook:
                selected_child_tab_id = child_notebook.select()
                if selected_child_tab_id:
                    selected_child_tab_widget = child_notebook.nametowidget(selected_child_tab_id)
                    if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                        selected_child_tab_widget._on_tab_selected(event)

    def get_tab_instance(self, parent_tab_name, child_tab_name=None):
        """
        Retrieves an instance of a specified tab (either parent or child).
        """
        if parent_tab_name not in self.tab_instances:
            return None
        if child_tab_name:
            if child_tab_name not in self.tab_instances[parent_tab_name]:
                return None
            return self.tab_instances[parent_tab_name][child_tab_name]
        else:
            return self.parent_tab_widgets.get(parent_tab_name)

def current_version():
    return current_version_string

def current_version_hash():
    return current_version_hash_value

if __name__ == "__main__":
    check_and_install_dependencies(current_version_string)
    app = App()
    app.mainloop()
