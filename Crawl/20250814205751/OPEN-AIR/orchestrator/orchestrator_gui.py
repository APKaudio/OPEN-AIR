# orchestrator/orchestrator_gui.py
#
# This file defines the GUI for the main application orchestrator,
# providing the user with Start, Stop, and Pause controls.
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
# Version 20250814.095000.1

current_version = "20250814.095000.1"
current_version_hash = (20250814 * 95000 * 1)

import tkinter as tk
from tkinter import ttk
import inspect
import os

from display.console_logic import console_log
from display.debug_logic import debug_log
# REMOVED incorrect import: from orchestrator.orchestrator_logic import toggle_pause_resume, stop_logic

class OrchestratorGUI(ttk.Frame):
    def __init__(self, parent, app_instance, orchestrator_logic, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app_instance = app_instance
        self.orchestrator = orchestrator_logic
        self.grid(row=0, column=0, sticky="ew")
        self._create_widgets()

    def _create_widgets(self):
        # [A brief, one-sentence description of the function's purpose.]
        # Creates and arranges the widgets for the orchestrator control bar.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function_name}", file=f"{__name__}", version=current_version, function=current_function_name)
        try:
            self.grid_columnconfigure(0, weight=1)

            # --- Button Definitions ---
            self.start_button = ttk.Button(self, text="Start", command=self.orchestrator.start_orchestrator, style='Start.TButton')
            self.pause_button = ttk.Button(self, text="Pause", command=self.orchestrator.toggle_pause, style='Stop.TButton', state=tk.DISABLED)
            self.stop_button = ttk.Button(self, text="Stop", command=self.orchestrator.stop_orchestrator, style='Stop.TButton', state=tk.DISABLED)

            # --- Grid Layout ---
            self.start_button.grid(row=0, column=1, padx=(10, 2), pady=10, sticky="ew")
            self.pause_button.grid(row=0, column=2, padx=2, pady=10, sticky="ew")
            self.stop_button.grid(row=0, column=3, padx=(2, 10), pady=10, sticky="ew")

            console_log("✅ Celebration of success! Orchestrator GUI created.")
        except Exception as e:
            console_log(f"❌ Error in _create_widgets for orchestrator GUI: {e}")
            debug_log(f"The GUI has gone rogue! The error be: {e}", file=f"{__name__}", version=current_version, function=current_function_name)

    def update_button_states(self):
        # [A brief, one-sentence description of the function's purpose.]
        # Updates the enabled/disabled state of the control buttons based on the orchestrator's status.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function_name} with state is_running={self.orchestrator.is_running}, is_paused={self.orchestrator.is_paused}",
                  file=f"{__name__}", version=current_version, function=current_function_name)
        try:
            if self.orchestrator.is_running:
                self.start_button.config(state=tk.DISABLED)
                self.pause_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.NORMAL)
                self.pause_button.config(text="Resume" if self.orchestrator.is_paused else "Pause")
            else:
                self.start_button.config(state=tk.NORMAL)
                self.pause_button.config(state=tk.DISABLED, text="Pause")
                self.stop_button.config(state=tk.DISABLED)

            # Update styles for visual feedback
            self.start_button.config(style='Start.TButton' if not self.orchestrator.is_running else 'Disabled.TButton')
            self.stop_button.config(style='Stop.TButton' if self.orchestrator.is_running else 'Disabled.TButton')
            
            if self.orchestrator.is_running:
                self.pause_button.config(style='Resume.TButton' if self.orchestrator.is_paused else 'Pause.TButton')
            else:
                self.pause_button.config(style='Disabled.TButton')

            console_log("✅ Orchestrator button states updated.")
        except Exception as e:
            console_log(f"❌ Error in update_button_states: {e}")
            debug_log(f"The buttons are rebelling! A mutiny! The error be: {e}",
                      file=f"{__name__}", version=current_version, function=current_function_name)