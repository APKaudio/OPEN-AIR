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
# Version 20250803.231000.0 (FIXED: Attached all missing path constants to the app instance.)
# Version 20250803.220500.0 (REFACTORED: Moved ASCII art logic here to break circular import.)
# Version 20250803.215000.0 (REFACTORED: Implemented switch_tab logic for custom button-based UI.)

current_version_string = "20250803.231000.0"
current_version_hash_value = 20250803 * 231000 * 0

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
from src.gui_elements import (_print_inst_ascii, _print_marks_ascii, _print_presets_ascii,
                              _print_scan_ascii, _print_plot_ascii, _print_xxx_ascii)
# CORRECTED: Import all path constants
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

        # --- CORRECTED: Attach ALL path constants to the instance ---
        self.DATA_FOLDER_PATH = DATA_FOLDER_PATH
        self.CONFIG_FILE_PATH = CONFIG_FILE_PATH
        self.PRESETS_FILE_PATH = PRESETS_FILE_PATH
        self.MARKERS_FILE_PATH = MARKERS_FILE_PATH
        self.VISA_COMMANDS_FILE_PATH = VISA_COMMANDS_FILE_PATH
        self.DEBUG_COMMANDS_FILE_PATH = DEBUG_COMMANDS_FILE_PATH
        
        # --- Initialize runtime state attributes ---
        self.scan_thread = None 
        self.active_tab_name = None
        
        self.tab_art_map = {
            "Instruments": _print_inst_ascii,
            "Markers": _print_marks_ascii,
            "Presets": _print_presets_ascii,
            "Scanning": _print_scan_ascii,
            "Plotting": _print_plot_ascii,
            "Experiments": _print_xxx_ascii,
        }
        
        self.title(f"OPEN-AIR RF Spectrum Analyzer Controller (v{self.current_version})")
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.style = ttk.Style(self)
        setup_tkinter_variables(self)
        initialize_program_environment(self)
        
        apply_saved_geometry(self)
        apply_styles(self.style, debug_log, self.current_version)
        create_main_layout_and_widgets(self)
        
        if hasattr(self, 'console_tab') and hasattr(self.console_tab, 'console_text'):
            set_gui_console_redirector(self.console_tab.console_text)
            set_debug_redirectors(self.console_tab.console_text)
            set_clear_console_func(self.console_tab._clear_applications_console_action)
        
        self.after(100, self._post_gui_setup)
        self.switch_tab("Instruments")

        debug_log(f"App initialized. Version: {self.current_version}.",
                    file=f"{os.path.basename(__file__)}", function="init", special=True)

    def switch_tab(self, new_tab_name):
        """Switches the active tab and triggers associated actions like printing ASCII art."""
        if self.active_tab_name == new_tab_name:
            return

        for name, button in self.tab_buttons.items():
            content_frame = self.tab_content_frames[name]
            if name == new_tab_name:
                button.config(style=f'{name}.Active.TButton')
                content_frame.tkraise()
                
                if name in self.tab_art_map:
                    self.tab_art_map[name](console_log)

                if hasattr(content_frame, '_on_parent_tab_selected'):
                    content_frame._on_parent_tab_selected(None)
            else:
                button.config(style=f'{name}.Inactive.TButton')
        
        self.active_tab_name = new_tab_name
        debug_log(f"Switched to tab: {new_tab_name}", file=f"{os.path.basename(__file__)}", function="switch_tab")

    def _post_gui_setup(self):
        pass

    def _on_closing(self):
        if hasattr(self, 'config') and self.config:
            save_config(self.config, self.CONFIG_FILE_PATH, console_log, self)
        self.destroy()

    def get_tab_instance(self, parent_tab_name, child_tab_name=None):
        parent_tab = self.tab_content_frames.get(parent_tab_name)
        if not parent_tab:
            return None
        if child_tab_name and hasattr(parent_tab, 'child_tabs'):
            return parent_tab.child_tabs.get(child_tab_name)
        return parent_tab

if __name__ == "__main__":
    app = App()
    app.mainloop()