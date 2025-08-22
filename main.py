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
# Version 20250821.214200.1 (Diagnostic Version)

import sys
import tkinter as tk
from tkinter import ttk
import inspect
from datetime import datetime
import os

# Import local modules
from src.gui_elements import _print_inst_ascii, _print_marks_ascii, _print_presets_ascii, _print_scan_ascii, _print_plot_ascii, _print_collaboration_ascii, _print_xxx_ascii
from src.program_check_dependancies import check_and_install_dependencies
from src.program_initialization import initialize_application
from src.program_gui_utils import create_main_layout, apply_saved_geometry
from settings_and_config.config_manager_save import load_program_config, save_program_config
from ref.ref_file_paths import VISA_COMMANDS_FILE_PATH, CONFIG_FILE_PATH
from src.program_style import apply_styles
from ref.ref_program_default_values import DEFAULT_CONFIG
from settings_and_config.config_manager_restore import restore_last_used_settings

# --- Global Scope Variables (as per protocol) ---
current_version = "20250821.214200.1"
current_version_hash = (20250821 * 214200 * 1)
current_file = f"{os.path.basename(__file__)}"

def restart_program(app_instance):
    """
    Restarts the current program.
    """
    app_instance.destroy()
    python = sys.executable
    os.execl(python, python, *sys.argv)

class App(tk.Tk):
    """The main application class for the RF Spectrum Analyzer Controller."""
    def __init__(self):
        super().__init__()
        
        self.inst = None

        print(f"Initializing application. Version: {current_version}. Let's get this show on the road! 🚀")
        
        try:
            self.title("RF Spectrum Analyzer Controller")

            initialize_application(self)
            
            # --- DIAGNOSTIC CHECK ---
            # The next line will print True if the variable was created, and False if not.
            # This is the crucial test.
            print(f"DIAGNOSTIC CHECK: hasattr(self, 'general_debug_enabled_var') -> {hasattr(self, 'general_debug_enabled_var')}")

            self.tabs_parent = None
            self.display_parent = None
            self.paned_window = None
            

            self.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            self._create_gui()
            self._post_gui_setup()

            self.bind('<Configure>', self._save_state_on_configure)
            
            menubar = tk.Menu(self)
            self.config(menu=menubar)
            file_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="File", menu=file_menu)
            file_menu.add_command(label="Restart", command=lambda: restart_program(self))

        except Exception as e:
            print(f"❌ An error occurred during program initialization: {e}")
            self.destroy()

        print(f"App initialized. Version: {current_version}.")


    def _create_gui(self):
        current_function = inspect.currentframe().f_code.co_name
        print(f"⚙️ 🟢 Entering {current_function}")
        
        self.title("RF Spectrum Analyzer Controller")
        
        self.style_obj = ttk.Style(self)
        apply_styles(style=self.style_obj, debug_log_func=None, current_app_version=current_version)
        
        self.paned_window, self.tabs_parent, self.display_parent = create_main_layout(app_instance=self, style_obj=self.style_obj)
        
        print(f"⚙️ ✅ Exiting {current_function}")
    
    def _post_gui_setup(self):
        """
        Performs tasks that require the GUI to be fully created, like restoring geometry.
        """
        current_function = inspect.currentframe().f_code.co_name
        print(f"Post-GUI setup tasks starting.")
        
        apply_saved_geometry(app_instance=self)

        self._set_console_redirectors()

        restore_last_used_settings(app_instance=self, console_print_func=self.display_parent.console_tab.console_output_widget.insert_and_scroll)
        
        if hasattr(self, 'program_config') and self.program_config.has_option('Application', 'paned_window_sash_position_percentage'):
            sash_pos_percentage = int(self.program_config.get('Application', 'paned_window_sash_position_percentage'))
            self.after(100, lambda: self._apply_sash_position(percentage=sash_pos_percentage))
        
        self.paned_window.bind("<ButtonRelease-1>", self._save_sash_position)

    def _apply_sash_position(self, percentage):
        """Applies the sash position after the window is drawn."""
        current_width = self.winfo_width()
        if current_width > 0:
            sash_pos_absolute = (current_width * percentage) / 100
            self.paned_window.sashpos(0, int(sash_pos_absolute))
            print(f"✅ Paned window sash position restored to {percentage}%")

    def _set_console_redirectors(self):
        """
        Sets up console redirection to the GUI console text widget.
        """
        current_function = inspect.currentframe().f_code.co_name
        if hasattr(self.display_parent, 'console_tab') and hasattr(self.display_parent.console_tab, 'console_output_widget'):
            sys.stdout.write = self.display_parent.console_tab.console_output_widget.insert_and_scroll
            sys.stderr.write = self.display_parent.console_tab.console_output_widget.insert_and_scroll
            self.redirector_set = True
            print("Console output redirected to GUI. All systems go!")
        else:
            self.redirector_set = False
            print("Console widgets not found. GUI console redirection not available. This is a critical failure!")
    
    def _save_state_on_configure(self, event):
        """
        A single function to handle saving both window geometry and sash position
        on a window configure event. This makes the system more robust.
        """
        current_function = inspect.currentframe().f_code.co_name
        
        try:
            self.program_config.set(section='Application', option='window_state', value=self.state())
            self.program_config.set(section='Application', option='geometry', value=self.winfo_geometry())

            if hasattr(self, 'paned_window') and self.paned_window and self.winfo_width() > 0:
                sash_pos = self.paned_window.sashpos(0)
                sash_pos_percentage = int((sash_pos / self.winfo_width()) * 100)
                self.program_config.set(section='Application', option='paned_window_sash_position_percentage', value=str(sash_pos_percentage))
            
            save_program_config(config=self.program_config)
        
        except Exception as e:
            print(f"❌ Error saving window state on configure: {e}")
        
    def _save_sash_position(self, event=None):
        """
        Saves the paned window sash position to the config file when the mouse is released.
        This handles the explicit user interaction of dragging the sash.
        """
        current_function = inspect.currentframe().f_code.co_name
        
        if hasattr(self, 'program_config') and hasattr(self, 'paned_window') and self.paned_window and self.winfo_width() > 0:
            sash_pos = self.paned_window.sashpos(0)
            sash_pos_percentage = int((sash_pos / self.winfo_width()) * 100)
            self.program_config.set(section='Application', option='paned_window_sash_position_percentage', value=str(sash_pos_percentage))
            
            save_program_config(config=self.program_config)

    def on_closing(self):
        """
        Handles the graceful shutdown of the application.
        """
        current_function = inspect.currentframe().f_code.co_name
        print(f"Closing application. Time for a long nap! 😴")
        
        if hasattr(self, 'program_config'):
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.program_config.set(section='Application', option='last_config_save_time', value=current_time)
            
            save_program_config(config=self.program_config)
            
        self.destroy()

if __name__ == "__main__":
    check_and_install_dependencies()
    app_instance = App()
    app_instance.mainloop()