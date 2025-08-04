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
# Version 20250803.215000.0 (REFACTORED: Implemented switch_tab logic for custom button-based UI.)
# Version 20250803.220000.0 (REFACTORED: Final update to call the new GUI builder, completing the UI restoration.)

current_version_string = "20250803.215000.0"
current_version_hash_value = 20250803 * 215000 * 0

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
    CONFIG_FILE_PATH, DATA_FOLDER_PATH
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
        
        # --- Initialize runtime state attributes ---
        self.scan_thread = None 
        self.active_tab_name = None # For custom tab system
        
        self.title(f"OPEN-AIR RF Spectrum Analyzer Controller (v{self.current_version})")
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # --- Setup Backend (Variables, Configs) ---
        self.style = ttk.Style(self)
        setup_tkinter_variables(self)
        initialize_program_environment(self)
        
        # --- Build Frontend (GUI) ---
        apply_saved_geometry(self)
        apply_styles(self.style, debug_log, self.current_version)
        create_main_layout_and_widgets(self)
        
        # --- Connect Backend to Frontend ---
        if hasattr(self, 'console_tab') and hasattr(self.console_tab, 'console_text'):
            set_gui_console_redirector(self.console_tab.console_text)
            set_debug_redirectors(self.console_tab.console_text)
            set_clear_console_func(self.console_tab._clear_applications_console_action)
        
        # --- Finalize Setup ---
        self.after(100, self._post_gui_setup)
        self.switch_tab("Instruments") # Set the initial active tab

        debug_log(f"App initialized with custom tab UI. Version: {self.current_version}.",
                    file=f"{os.path.basename(__file__)}", function="init", special=True)

    def switch_tab(self, new_tab_name):
        """Switches the active tab in the custom button-based tab system."""
        if self.active_tab_name == new_tab_name:
            return # Do nothing if clicking the already active tab

        for name, button in self.tab_buttons.items():
            content_frame = self.tab_content_frames[name]
            if name == new_tab_name:
                # Activate the selected tab
                button.config(style=f'{name}.Active.TButton')
                content_frame.tkraise() # Bring the content to the front
                
                # Call the tab's selection handler if it exists
                if hasattr(content_frame, '_on_parent_tab_selected'):
                    content_frame._on_parent_tab_selected(None) # Pass None for event object
            else:
                # Deactivate all other tabs
                button.config(style=f'{name}.Inactive.TButton')
        
        self.active_tab_name = new_tab_name
        debug_log(f"Switched to tab: {new_tab_name}", file=f"{os.path.basename(__file__)}", function="switch_tab")


    def _post_gui_setup(self):
        """
        Performs setup tasks that need to run after the Tkinter mainloop has started.
        """
        pass

    def _on_closing(self):
        """
        Handles the application closing event.
        """
        if hasattr(self, 'config') and self.config:
            save_config(self.config, self.CONFIG_FILE_PATH, console_log, self)
        self.destroy()

    def get_tab_instance(self, parent_tab_name, child_tab_name=None):
        """
        Retrieves an instance of a specified tab.
        """
        parent_tab = self.tab_content_frames.get(parent_tab_name)
        if not parent_tab:
            return None
        
        if child_tab_name:
            # Assumes child tabs are stored in a dict named 'child_tabs' on the parent
            if hasattr(parent_tab, 'child_tabs'):
                return parent_tab.child_tabs.get(child_tab_name)
            return None
        return parent_tab

if __name__ == "__main__":
    app = App()
    app.mainloop()