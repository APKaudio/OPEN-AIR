# This is a specialized GUI component designed for the Configuration tab.
# It acts as a test harness for features related to configuration management within the main
# section. This refactored version is a standalone test harness with mock functionality.
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
# Version 20251127.000000.1

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext # Added scrolledtext
import pathlib
import sys
import json

# --- Module Imports ---
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
from display.styling.style import THEMES, DEFAULT_THEME

# --- Global Scope Variables ---
CURRENT_DATE = 20251127
CURRENT_TIME = 0
CURRENT_TIME_HASH = 0
REVISION_NUMBER = 1
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME_HASH * REVISION_NUMBER)
current_file = f"tabs/Experiments/tab_experiments_child_initial_configuration.py"


class InitialConfigurationTab(ttk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        """
        Initializes the InitialConfigurationTab, a Tkinter Frame for viewing and
        editing the application's configuration.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📕🟢 Initializing InitialConfigurationTab...",
                  file=current_file, version=current_version, function=current_function, 

)

        super().__init__(master, **kwargs)
        
        self._create_widgets()
        self._populate_config_table()
        
        debug_log(message=f"📕✅ InitialConfigurationTab initialized.",
                  file=current_file, version=current_version, function=current_function, 

)

    def _create_widgets(self):
        """
        Creates and lays out the widgets for the configuration tab, including a
        text area for displaying the config and buttons for saving and reloading.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📕🟢 Creating widgets for InitialConfigurationTab.",
                  file=current_file, version=current_version, function=current_function, 

)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        control_frame = ttk.Frame(self)
        control_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        
        save_button = ttk.Button(control_frame, text="Save Config", command=self._save_program_configure_action, style='Green.TButton')
        save_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        reload_button = ttk.Button(control_frame, text="Reload Config", command=self._reload_config_action, style='Orange.TButton')
        reload_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.config_text_widget = scrolledtext.ScrolledText(self, wrap="word", height=25, bg="#2b2b2b", fg="#cccccc", insertbackground="white", font=("Courier", 10))
        self.config_text_widget.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        debug_log(message=f"📕✅ Widgets created.",
                  file=current_file, version=current_version, function=current_function, 

)
    
    def _populate_config_table(self):
        """
        Reads a mock config file and populates the text widget with its content.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📕🟢 Populating config table from a mock file.",
                  file=current_file, version=current_version, function=current_function, 

)

        try:
            mock_config_content = """[GENERAL]
theme = dark
log_level = DEBUG

[INSTRUMENT]
visa_resource = ASRL1::INSTR
ref_level_dBm = -20
power_attenuation_dB = 10
preamp_on = False
high_sensitivity_on = False

[MARKERS]
marker1_freq_MHz = 111.0
marker2_freq_MHz = 222.0
marker3_freq_MHz = 333.0
"""
            self.config_text_widget.config(state=tk.NORMAL)
            self.config_text_widget.delete('1.0', tk.END)
            self.config_text_widget.insert(tk.END, mock_config_content)
            self.config_text_widget.config(state=tk.DISABLED)
            
            debug_log(message=f"📕✅ Config table populated successfully.",
                      file=current_file, version=current_version, function=current_function, 

)

        except Exception as e:
            debug_log(message=f"❌ Error populating config table: {e}")
            debug_log(message=f"📕🔴 Failed to populate config table. Error: {e}",
                      file=current_file, version=current_version, function=current_function, 

)
    
    def _save_program_configure_action(self):
        """
        Handles the action of saving the edited config back to a mock file.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📕🟢 Attempting to save mock config file...",
                  file=current_file, version=current_version, function=current_function, 

)

        try:
            current_content = self.config_text_widget.get('1.0', tk.END)
            # In a real app, this would write to a file. Here, we just log the action.
            
            debug_log(message=f"📕✅ Mock configuration saved. Arrr, the treasure be safely stowed! ⚓️",
                      file=current_file, version=current_version, function=current_function, 

)

        except Exception as e:
            
            debug_log(message=f"📕🔴 Failed to save configuration. Error: {e}",
                      file=current_file, version=current_version, function=current_function, 

)

    def _reload_config_action(self):
        """
        Handles the action of reloading a mock config from disk.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(message=f"📕🟢 Reloading config from mock disk...",
                  file=current_file, version=current_version, function=current_function, 

)
        
        self._populate_config_table()
        
        
        debug_log(message=f"📕✅ Reloaded mock config. The map be fresh! 🗺️",
                  file=current_file, version=current_version, function=current_function, 

)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Initial Configuration Tab Test")
    
    app_frame = InitialConfigurationTab(master=root)
    
    root.mainloop()