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
# Version 20250803.220000.0 (REFACTORED: Final update to call the new GUI builder, completing the UI restoration.)
# Version 20250803.205028.0 (REFACTORED: Moved trace logic here to break circular import. Fixed style import.)
# Version 20250803.190500.0 (FIXED: Added safety check for config object on closing.)
# Version 20250803.190100.0 (FIXED: Initialized scan_thread attribute to prevent AttributeError on startup.)
# Version 20250803.184800.0 (FIXED: Added path constants to the App instance.)

current_version_string = "20250803.220000.0"
current_version_hash_value = 20250803 * 220000 * 0

import tkinter as tk
from tkinter import ttk
import os
import sys
import inspect

# Import functions from refactored modules
from src.program_check_Dependancies import check_and_install_dependencies
from src.program_initialization import initialize_program_environment
from src.program_shared_values import setup_tkinter_variables
from src.program_style import apply_styles
from src.program_gui_utils import create_main_layout_and_widgets, apply_saved_geometry
from src.settings_and_config.config_manager import save_config
from src.debug_logic import debug_log, set_debug_redirectors
from src.console_logic import console_log, set_gui_console_redirector, set_clear_console_func
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
        self.scan_thread = None 
        self.is_paused_by_user = False
        self.console_log_func = console_log
        
        self.title(f"OPEN-AIR RF Spectrum Analyzer Controller (v{self.current_version})")
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # --- Setup Backend (Variables, Configs) ---
        self.style = ttk.Style(self)
        setup_tkinter_variables(self)

        def create_trace_callback(var_name):
            """Creates a callback function for Tkinter variable traces."""
            def callback(*args):
                if hasattr(self, 'config'): 
                    debug_log(f"Variable '{var_name}' changed. Saving config.", file=f"{os.path.basename(__file__)} - {self.current_version}", function="trace_callback")
                    save_config(self.config, self.CONFIG_FILE_PATH, self.console_log_func, self)
            return callback

        if hasattr(self, 'setting_var_map'):
            for var_name, (_, _, var) in self.setting_var_map.items():
                var.trace_add("write", create_trace_callback(var_name))

        initialize_program_environment(self)
        
        # --- Build Frontend (GUI) ---
        apply_saved_geometry(self)
        apply_styles(self.style, debug_log, self.current_version)
        create_main_layout_and_widgets(self) # This single function now builds the entire UI.
        
        # --- Connect Backend to Frontend ---
        if hasattr(self, 'console_tab') and hasattr(self.console_tab, 'console_text'):
            set_gui_console_redirector(self.console_tab.console_text)
            set_debug_redirectors(self.console_tab.console_text)
            set_clear_console_func(self.console_tab._clear_applications_console_action)
        
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
        instrument_tab = self.get_tab_instance("Instruments", "Connection")
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
        try:
            selected_tab_id = self.parent_notebook.select()
            active_parent_tab_name = self.parent_notebook.tab(selected_tab_id, "text")
            active_parent_tab_instance = self.parent_tab_widgets.get(active_parent_tab_name)

            if active_parent_tab_instance:
                if hasattr(active_parent_tab_instance, '_on_parent_tab_selected'):
                    active_parent_tab_instance._on_parent_tab_selected(event)
                
                if hasattr(active_parent_tab_instance, 'child_notebook'):
                    child_notebook = active_parent_tab_instance.child_notebook
                    if child_notebook and child_notebook.tabs():
                        selected_child_tab_id = child_notebook.select()
                        selected_child_tab_widget = child_notebook.nametowidget(selected_child_tab_id)
                        if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                            selected_child_tab_widget._on_tab_selected(event)
        except tk.TclError:
            # This can happen if tabs are in the process of being created/destroyed.
            pass

    def get_tab_instance(self, parent_tab_name, child_tab_name=None):
        """
        Retrieves an instance of a specified tab (either parent or child).
        """
        if not hasattr(self, 'tab_instances') or parent_tab_name not in self.tab_instances:
            # tab_instances is populated within each PARENT_TAB class
            return None
        if child_tab_name:
            return self.tab_instances[parent_tab_name].get(child_tab_name)
        else:
            return self.parent_tab_widgets.get(parent_tab_name)

def current_version():
    return current_version_string

def current_version_hash():
    return current_version_hash_value

if __name__ == "__main__":
    # check_and_install_dependencies(current_version_string) # You may need to uncomment this
    app = App()
    app.mainloop()