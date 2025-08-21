# FolderName/main.py
#
# This is the main entry point for the RF Spectrum Analyzer Controller application.
# It handles initial setup, checks for dependencies, and launches the main GUI.
# This refactored version uses a cleaner, two-pane layout managed by dedicated parent components.
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
# Version 20250821.125800.13
# NEW: Corrected the AttributeError by assigning VISA_COMMANDS_FILE_PATH to the main app instance.
# FIXED: Resolved circular dependency issues by moving app instance creation to a single location.
# FIXED: Initialized the band_vars Tkinter variable to prevent AttributeError on startup.
# FIXED: Ensured paned window sash position is explicitly saved on shutdown to guarantee persistence.
# NEW: Moved sash position restoration to post-GUI setup to ensure it is set with the correct window width.
# NEW: Modified sash movement handler to trigger a deferred save.
# FIXED: Corrected the `after` method call to prevent the "AttributeError: '_tkinter.tkapp' object has no attribute..." bug.

import sys
import os
import inspect
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import subprocess

# Local application imports
from orchestrator.orchestrator_logic import OrchestratorLogic
from src.program_initialization import initialize_program_environment
from src.program_gui_utils import create_main_layout_and_widgets, apply_saved_geometry
from src.program_shared_values import setup_shared_values
from src.program_style import apply_styles
from settings_and_config.config_manager import save_config, load_config
# Corrected import to get all global paths
from settings_and_config.program_default_values import DEFAULT_CONFIG, CONFIG_FILE_PATH, DATA_FOLDER_PATH, VISA_COMMANDS_FILE_PATH
from display.debug_logic import debug_log, set_debug_redirectors, set_debug_to_file_mode, set_include_console_messages_to_debug_file_mode, set_log_truncation_mode, set_debug_mode, set_log_visa_commands_mode, set_include_visa_messages_to_debug_file_mode
from display.console_logic import console_log, set_gui_console_redirector, set_debug_file_hooks
from src.gui_elements import TextRedirector

class App(tk.Tk):
    """
    The main application class for the RF Spectrum Analyzer Controller.
    """
    def __init__(self):
        super().__init__()
        # UPDATED VERSION NUMBER
        self.current_version = "20250821.125800.13"
        self.current_version_hash = (20250821 * 125800 * 13)
        self.current_file = os.path.basename(__file__)
        self.config = None
        self.CONFIG_FILE_PATH = CONFIG_FILE_PATH
        self.DATA_FOLDER_PATH = DATA_FOLDER_PATH
        # NEW: Assigned the global path to the instance to resolve the AttributeError
        self.VISA_COMMANDS_FILE_PATH = VISA_COMMANDS_FILE_PATH
        self.orchestrator_logic = None

        # --- Attach ALL path constants to the instance ---
        self.scan_thread = None
        self.active_tab_name = None
        self.defer_config_save_id = None
        self.collected_scans_dataframes = []
        self.inst = None
        self.paned_window = None
        self.is_initial_resize = True

        # --- IMPORTANT: Initialize all shared variables first to prevent AttributeError ---
        self.band_vars = []
        self.visa_resource_var = tk.StringVar(self, value="")
        self.gui_console = None
        self.gui_debug = None
        self.general_debug_enabled_var = tk.BooleanVar(self, value=False)
        self.log_visa_commands_enabled_var = tk.BooleanVar(self, value=False)
        self.debug_to_file_var = tk.BooleanVar(self, value=False)
        self.include_console_messages_to_debug_file_var = tk.BooleanVar(self, value=False)
        self.log_truncation_enabled_var = tk.BooleanVar(self, value=False)
        self.include_visa_messages_to_debug_file_var = tk.BooleanVar(self, value=False)
        self.last_config_save_time_var = tk.StringVar(self, value="")
        self.debug_to_gui_console_var = tk.BooleanVar(self, value=False)

        self.tab_art_map = {}
        
        self.title(f"OPEN-AIR - Zone Awareness Processor (v{self.current_version})")
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.bind("<Configure>", self._on_app_resize_or_move)

        self.style_obj = ttk.Style(self)
        self.setting_var_map = {}
        
        # This call must happen before the GUI is created to apply the theme
        apply_styles(self.style_obj, debug_log, self.current_version)
        
        # These need to be called before the GUI is created as they set Tkinter vars
        setup_shared_values(self) 
        
        # This call needs to happen before the GUI is created to load config values
        initialize_program_environment(self) 
        
        # This function must be called after the GUI is created as it affects window geometry
        apply_saved_geometry(self)
        
        # --- Instantiate Orchestrator Logic ---
        self.orchestrator_logic = OrchestratorLogic(app_instance=self, gui=None)
        
        # --- Create GUI and pass the logic to it ---
        create_main_layout_and_widgets(self, self.orchestrator_logic)

        # FIXED: Pass a lambda to ensure the correct 'self' is used for the callback
        self.after(100, lambda: self._post_gui_setup())

        debug_log(f"App initialized. Version: {self.current_version}.",
                  file=self.current_file, version=self.current_version, function="__init__", special=True)

    def _post_gui_setup(self):
        """
        Performs setup tasks that must happen after the main GUI is fully initialized.
        This includes setting up console redirection and restoring the sash position.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Post-GUI setup tasks starting.",
                  file=self.current_file, version=self.current_version, function=current_function)
        
        # The redirection MUST happen after all the widgets are created
        self._set_console_redirectors()
        
        # Restore the paned window sash position
        try:
            sash_position_percentage = int(self.config.get('Application', 'paned_window_sash_position_percentage', fallback='45'))
            self.paned_window.sashpos(0, (self.winfo_width() * sash_position_percentage) // 100)
            debug_log(f"✅ Paned window sash position restored to {sash_position_percentage}%.",
                      file=self.current_file, version=self.current_version, function=current_function)
        except Exception as e:
            debug_log(f"❌ Error restoring sash position. The error be: {e}",
                      file=self.current_file, version=self.current_version, function=current_function)
        
        # display_splash_screen()
        self.is_initial_resize = False
        debug_log("Initial resize flag set to False. Geometry saving is now enabled. ",
                  file=self.current_file, version=self.current_version, function=current_function, special=True)
        
        debug_log("Post-GUI setup complete.",
                  file=self.current_file, version=self.current_version, function=current_function)

    def _set_console_redirectors(self):
        """
        Sets up the console redirection to the GUI and registers the console functions.
        """
        current_function = inspect.currentframe().f_code.co_name
        
        if hasattr(self, 'display_parent_tab') and hasattr(self.display_parent_tab, 'console_tab'):
            console_tab = self.display_parent_tab.console_tab
            debug_tab = self.display_parent_tab.debug_tab
            
            # FIXED: Pass both stdout and stderr redirectors to the function.
            set_gui_console_redirector(TextRedirector(console_tab.console_text), TextRedirector(console_tab.console_text, "stderr"))
            
            # CORRECTED: Use the existing function 'set_debug_redirectors' with the correct arguments.
            # This is the fix for the ImportError.
            set_debug_redirectors(TextRedirector(debug_tab.software_log_text), TextRedirector(debug_tab.software_log_text, "stderr"))
            
            # Since `set_debug_to_gui_console_mode` no longer exists, we simply set the flag on the instance
            # This logic needs to be moved or re-evaluated, but for now we'll set the flag
            self.debug_to_gui_console_var.set(self.general_debug_enabled_var.get())
            
            # Set the console clearing function
            # set_clear_console_func(console_tab._clear_applications_console_action)

            debug_log("GUI console redirectors set up successfully.",
                      file=self.current_file, version=self.current_version, function=current_function, special=True)
        else:
            debug_log("Console widgets not found. GUI console redirection not available. This is a critical failure!",
                      file=self.current_file, version=self.current_version, function=current_function, special=True)

    def _on_app_resize_or_move(self, event):
        """
        Event handler for when the main window is resized or moved.
        """
        if event.widget is self and not self.is_initial_resize:
            
            # --- Check and log sash position if it has changed, and trigger a save ---
            if hasattr(self, 'paned_window') and self.paned_window and self.winfo_width() > 0:
                current_sash_pos = self.paned_window.sashpos(0)
                
                # Check if the sash has moved
                if not hasattr(self, '_last_sash_pos'):
                    self._last_sash_pos = current_sash_pos

                if current_sash_pos != self._last_sash_pos:
                    sash_pos_percentage = (current_sash_pos / self.winfo_width()) * 100
                    debug_log(f"Paned window sash position changed to {current_sash_pos} ({sash_pos_percentage:.2f}%)",
                              file=self.current_file, version=self.current_version, function="_on_app_resize_or_move")
                    
                    # Trigger the deferred save
                    if self.defer_config_save_id:
                        self.after_cancel(self.defer_config_save_id)
                    self.defer_config_save_id = self.after_idle(
                        lambda: self._save_config_on_idle(f"Sash position updated.")
                    )

                    self._last_sash_pos = current_sash_pos
            
    def _save_config_on_idle(self, message):
        """Helper function to save config after a delay."""
        self.defer_config_save_id = None
        save_config(self.config, self.CONFIG_FILE_PATH, console_log, self)
        debug_log(f"Deferred config save triggered. {message}",
                  file=self.current_file, version=self.current_version,
                  function="_save_config_on_idle", special=True)
        
    def _on_closing(self):
        """Handles application shutdown.
        FIXED: Explicitly captures and saves the sash position before closing.
        """
        if hasattr(self, 'config') and self.config:
            console_log("Saving configuration on shutdown...")
            
            # Get the current sash position and save it to the config
            if hasattr(self, 'paned_window') and self.paned_window and self.winfo_width() > 0:
                sash_pos = self.paned_window.sashpos(0)
                sash_pos_percentage = int((sash_pos / self.winfo_width()) * 100)
                self.config.set('Application', 'paned_window_sash_position_percentage', str(sash_pos_percentage))
            
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
                      file=self.current_file, version=self.current_version, function=current_function)
            return None

        parent_tab = self.tabs_parent.tab_content_frames.get(parent_tab_name)
        if not parent_tab:
            return None
            
        if child_tab_name and hasattr(parent_tab, 'child_tabs'):
            return parent_tab.child_tabs.get(child_tab_name)
        
        return parent_tab

if __name__ == "__main__":
    app = App()
    app.mainloop()