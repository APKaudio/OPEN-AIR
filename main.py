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
# Version 20250821.171500.9
# FIXED: Removed the save on closing. Sash position is now ONLY saved on mouse button release.

import sys
import tkinter as tk
from tkinter import ttk
import inspect
from datetime import datetime
import os
import ttkthemes # ADDED: Import ttkthemes for ThemedStyle

# Import local modules
from display.debug_logic import debug_log
from display.console_logic import console_log
from src.gui_elements import _print_inst_ascii, _print_marks_ascii, _print_presets_ascii, _print_scan_ascii, _print_plot_ascii, _print_collaboration_ascii, _print_xxx_ascii

from src.program_initialization import initialize_program_environment
from src.program_style import apply_styles
from src.program_gui_utils import create_main_layout_and_widgets,  apply_saved_geometry
from settings_and_config.config_manager import save_config
from ref.ref_file_paths import VISA_COMMANDS_FILE_PATH


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # Initializing core application variables
        current_function = inspect.currentframe().f_code.co_name
        self.current_file = os.path.basename(__file__)
        self.current_version = "20250821.171500.9" # INCREMENTED VERSION

        # FIXED: Initialize the `inst` attribute here to prevent an AttributeError later.
        self.inst = None

        debug_log(f"Initializing application. Version: {self.current_version}. Let's get this show on the road! 🚀",
                  file=self.current_file, version=self.current_version, function=current_function)
        
        # Call the main initialization function
        initialize_program_environment(self)
        
        # This attribute is a placeholder. It will be set later during GUI creation.
        self.tabs_parent = None
        self.display_parent = None
        self.paned_window = None
        
        # We also need to add a reference to the VisaCommands file path for other modules to use
        self.visa_commands_file_path = VISA_COMMANDS_FILE_PATH
        
        # NEW: Create the tab_art_map dictionary right here so TABS_PARENT can find it.
        self.tab_art_map = {
            "Instruments": _print_inst_ascii,
            "Scanning": _print_scan_ascii,
            "Plotting": _print_plot_ascii,
            "Markers": _print_marks_ascii,
            "Presets": _print_presets_ascii,
            "Experiments": _print_xxx_ascii
        }

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self._create_gui()
        self._post_gui_setup()

        debug_log(f"App initialized. Version: {self.current_version}.",
                  file=self.current_file, version=self.current_version, function=current_function, special=True)


    def _create_gui(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"⚙️ 🟢 Entering {current_function}",
                  file=self.current_file, version=self.current_version, function=current_function)
        
        self.title("OPEN-AIR: RF Spectrum Analyzer Controller")
        
        # FIXED: Corrected the call to pass the debug_log function and version
        self.style_obj = ttkthemes.ThemedStyle(self) # NEW: Instantiate the style object
        apply_styles(self.style_obj, debug_log_func=debug_log, current_app_version=self.current_version)
        
        # This will create the main UI elements and set the self.paned_window,
        # self.tabs_parent, and self.display_parent attributes.
        self.paned_window, self.tabs_parent, self.display_parent = create_main_layout_and_widgets(self, self.style_obj) # CORRECTED: Pass the style_obj
        
        
        
        debug_log(f"⚙️ ✅ Exiting {current_function}",
                  file=self.current_file, version=self.current_version, function=current_function)
    
    def _post_gui_setup(self):
        """
        Performs tasks that require the GUI to be fully created, like restoring geometry.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Post-GUI setup tasks starting.",
                  file=self.current_file, version=self.current_version, function=current_function, special=True)
        
        apply_saved_geometry(self)

        # Re-initialize the console redirector now that the GUI exists
        self._set_console_redirectors()
        
        # Restore sash position if available
        if hasattr(self, 'program_config') and self.program_config.has_option('Application', 'paned_window_sash_position_percentage'):
            sash_pos_percentage = int(self.program_config.get('Application', 'paned_window_sash_position_percentage'))
            current_width = self.winfo_width()
            if current_width > 0:
                sash_pos_absolute = (current_width * sash_pos_percentage) / 100
                self.paned_window.sashpos(0, int(sash_pos_absolute)) # FIXED: Cast to int to resolve TclError
                debug_log(f"✅ Paned window sash position restored to {sash_pos_percentage}",
                          file=self.current_file, version=self.current_version, function=current_function, special=True)
        
        # This is the correct binding. It will only save the sash position when the mouse button is released.
        self.paned_window.bind("<ButtonRelease-1>", self._save_sash_position)

    def _set_console_redirectors(self):
        """
        Sets up console redirection to the GUI console text widget.
        """
        current_function = inspect.currentframe().f_code.co_name
        if hasattr(self.display_parent, 'console_output_widget'):
            sys.stdout.write = self.display_parent.console_output_widget.insert_and_scroll
            sys.stderr.write = self.display_parent.console_output_widget.insert_and_scroll
            self.redirector_set = True
            debug_log("Console output redirected to GUI. All systems go! 📺",
                      file=self.current_file, version=self.current_version, function=current_function, special=True)
        else:
            self.redirector_set = False
            debug_log("Console widgets not found. GUI console redirection not available. This is a critical failure!",
                      file=self.current_file, version=self.current_version, function=current_function, special=True)
    
    # NEW: Function to handle saving sash position on button release
    def _save_sash_position(self, event=None):
        """
        Saves the paned window sash position to the config file.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Paned window sash position save triggered. 💾",
                  file=self.current_file, version=self.current_version, function=current_function, special=True)
        
        if hasattr(self, 'program_config') and hasattr(self, 'paned_window') and self.paned_window and self.winfo_width() > 0:
            sash_pos = self.paned_window.sashpos(0)
            sash_pos_percentage = int((sash_pos / self.winfo_width()) * 100)
            self.program_config.set('Application', 'paned_window_sash_position_percentage', str(sash_pos_percentage))
            save_config(config=self.program_config, console_print_func=console_log, app_instance=self)
            console_log("✅ Sash position saved.")

    def on_closing(self):
        """
        Handles the graceful shutdown of the application.
        This function no longer saves the geometry or sash position.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Closing application. Time for a long nap! 😴",
                  file=self.current_file, version=self.current_version, function=current_function)
        
        if hasattr(self, 'program_config'):
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.program_config.set('Application', 'last_config_save_time', current_time)
            
            # The following lines have been removed as per your request:
            # self.program_config.set('Application', 'window_state', self.state())
            # self.program_config.set('Application', 'geometry', self.winfo_geometry())
            # self.program_config.set('Application', 'paned_window_sash_position_percentage', ...)
            
            save_config(config=self.program_config, console_print_func=console_log, app_instance=self)
            console_log("✅ Final configuration saved on shutdown.")
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()