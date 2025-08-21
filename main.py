# FolderName/main_app.py
#
# This is the main entry point for the RF Spectrum Analyzer Controller application.
# It handles initial setup, checks for dependencies, and launches the main GUI.
# This refactored version uses a cleaner, two-pane layout managed by dedicated parent components.
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
# Version 20250814.225500.1 (FIXED: Removed the incorrect import of 'set_debug_to_gui_console_mode' to resolve ImportError.)

current_version = "20250814.225500.1"
current_version_hash = (20250814 * 225500 * 1)

import tkinter as tk
from tkinter import ttk
import os
import sys
import inspect
from datetime import datetime

# Import functions from refactored modules
from src.program_check_Dependancies import check_and_install_dependencies
from src.program_initialization import initialize_program_environment
from src.program_shared_values import setup_tkinter_variables
from src.program_style import apply_styles
from src.program_gui_utils import create_main_layout_and_widgets, apply_saved_geometry
from src.settings_and_config.config_manager import save_config

from display.debug_logic import debug_log, set_debug_redirectors, set_console_log_func, set_log_truncation_mode
from display.console_logic import console_log, set_gui_console_redirector, set_clear_console_func

from src.gui_elements import (_print_inst_ascii, _print_marks_ascii, _print_presets_ascii,
                              _print_scan_ascii, _print_plot_ascii, _print_xxx_ascii, display_splash_screen,
                              TextRedirector)

from src.settings_and_config.program_default_values import (
    CONFIG_FILE_PATH, DATA_FOLDER_PATH, PRESETS_FILE_PATH,
    MARKERS_FILE_PATH, VISA_COMMANDS_FILE_PATH, DEBUG_COMMANDS_FILE_PATH
)
from ref.frequency_bands import MHZ_TO_HZ
from orchestrator.orchestrator_logic import OrchestratorLogic

class App(tk.Tk):
    """
    The main application class for the RF Spectrum Analyzer Controller.
    """
    def __init__(self):
        super().__init__()
        self.current_version = current_version
        self.current_version_hash = current_version_hash

        # --- Attach ALL path constants to the instance ---
        self.DATA_FOLDER_PATH = DATA_FOLDER_PATH
        self.CONFIG_FILE_PATH = CONFIG_FILE_PATH
        self.PRESETS_FILE_PATH = PRESETS_FILE_PATH
        self.MARKERS_FILE_PATH = MARKERS_FILE_PATH
        self.VISA_COMMANDS_FILE_PATH = VISA_COMMANDS_FILE_PATH
        self.DEBUG_COMMANDS_FILE_PATH = DEBUG_COMMANDS_FILE_PATH
        self.MHZ_TO_HZ = MHZ_TO_HZ
        
        # --- Initialize runtime state attributes ---
        self.scan_thread = None 
        self.active_tab_name = None
        self.defer_config_save_id = None
        self.collected_scans_dataframes = []
        self.inst = None
        self.paned_window = None
        self.is_initial_resize = True

        self.tab_art_map = {
            "Instruments": _print_inst_ascii,
            "Markers": _print_marks_ascii,
            "Presets": _print_presets_ascii,
            "Scanning": _print_scan_ascii,
            "Plotting": _print_plot_ascii,
            "Experiments": _print_xxx_ascii,
        }
        
        self.title(f"OPEN-AIR - Zone Awareness Processor (v{self.current_version})")
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.bind("<Configure>", self._on_app_resize_or_move)
        
        self.style = ttk.Style(self)
        self.setting_var_map = {}
        
        # This call must happen before the GUI is created to apply the theme
        apply_styles(self.style, debug_log, self.current_version)
        
        # These need to be called before the GUI is created as they set Tkinter vars
        setup_tkinter_variables(self) 
        
        # This call needs to happen before the GUI is created to load config values
        initialize_program_environment(self) 
        
        # This function must be called after the GUI is created as it affects window geometry
        apply_saved_geometry(self)
        
        # --- NEW: Instantiate Orchestrator Logic ---
        self.orchestrator_logic = OrchestratorLogic(app_instance=self, gui=None)
        
        # --- Create GUI and pass the logic to it ---
        create_main_layout_and_widgets(self, self.orchestrator_logic)

        self.after(100, self._post_gui_setup)

        debug_log(f"App initialized. Version: {self.current_version}.",
                  file=f"{os.path.basename(__file__)} - {current_version}", function="__init__", special=True)

    def _post_gui_setup(self):
        """
        Performs setup tasks that must happen after the main GUI is fully initialized.
        This includes setting up console redirection.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Post-GUI setup tasks starting.",
                  file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)
        
        # The redirection MUST happen after all the widgets are created
        self._set_console_redirectors()
        
        display_splash_screen()
        self.is_initial_resize = False
        debug_log("Initial resize flag set to False. Geometry saving is now enabled. ",
                  file=f"{os.path.basename(__file__)} - {current_version}", function=current_function, special=True)
        
        debug_log("Post-GUI setup complete.",
                  file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)

    def _set_console_redirectors(self):
        """
        Sets up the console redirection to the GUI and registers the console functions.
        """
        current_function = inspect.currentframe().f_code.co_name
        
        if hasattr(self, 'display_parent_tab') and hasattr(self.display_parent_tab, 'bottom_pane') and hasattr(self.display_parent_tab.bottom_pane, 'console_tab'):
            console_tab = self.display_parent_tab.bottom_pane.console_tab
            debug_tab = self.display_parent_tab.bottom_pane.debug_tab
            
            # Use the single TextRedirector instance from ConsoleTab for all console output
            set_gui_console_redirector(console_tab.redirector, console_tab.redirector)
            
            # Since `set_debug_to_gui_console_mode` no longer exists, we simply set the flag on the instance
            self.debug_to_gui_console_var.set(self.general_debug_enabled_var.get())
            
            # Set the console clearing function
            set_clear_console_func(console_tab._clear_applications_console_action)

            debug_log("GUI console redirectors set up successfully.",
                      file=f"{os.path.basename(__file__)} - {current_version}", function=current_function, special=True)
        else:
            debug_log("Console widgets not found. GUI console redirection not available. This is a critical failure!",
                      file=f"{os.path.basename(__file__)} - {current_version}", function=current_function, special=True)

    def _on_app_resize_or_move(self, event):
        """
        Event handler for when the main window is resized or moved.
        """
        if event.widget is self and not self.is_initial_resize:
            if self.defer_config_save_id:
                self.after_cancel(self.defer_config_save_id)
            
            self.defer_config_save_id = self.after_idle(
                lambda: self._save_config_on_idle(f"Geometry updated to: {self.geometry()}")
            )

    def _save_config_on_idle(self, message):
        """Helper function to save config after a delay."""
        self.defer_config_save_id = None
        save_config(self.config, self.CONFIG_FILE_PATH, console_log, self)
        debug_log(f"Deferred config save triggered. {message}",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  function="_save_config_on_idle", special=True)
        
    def _on_closing(self):
        """Handles application shutdown."""
        if hasattr(self, 'config') and self.config:
            console_log("Saving configuration on shutdown...")
            save_config(self.config, self.CONFIG_FILE_PATH, console_log, self)
            console_log("✅ Configuration saved successfully on shutdown.")
        self.destroy()

    def get_tab_instance(self, parent_tab_name, child_tab_name=None):
        """
        Retrieves a reference to a parent or child tab instance.
        """
        current_function = inspect.currentframe().f_code.co_name
        
        if not hasattr(self, 'tabs_parent'):
            debug_log(f"Attempted to get tab instance before tabs_parent is created.",
                      file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)
            return None

        parent_tab = self.tabs_parent.tab_content_frames.get(parent_tab_name)
        if not parent_tab:
            return None
            
        if child_tab_name and hasattr(parent_tab, 'child_tabs'):
            return parent_tab.child_tabs.get(child_tab_name)
        
        return parent_tab

if __name__ == "__main__":
    check_and_install_dependencies(current_version)
    app = App()
    app.mainloop()
