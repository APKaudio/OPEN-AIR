# display/display_child_orchestrator_tasks.py
#
# This file defines the Orchestrator Tasks tab, a GUI component that displays the
# real-time status of the main application orchestrator and logs check-in events from
# various modules.
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
# Version 20250814.113500.1

current_version = "20250814.113500.1"
current_version_hash = (20250814 * 113500 * 1)

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os
import inspect

from display.debug_logic import debug_log
from display.console_logic import console_log
# REMOVED: Unnecessary import that caused a circular dependency.
# from src.program_style import ProgramStyle

class OrchestratorTasksTab(ttk.Frame):
    def __init__(self, parent, app_instance, *args, **kwargs):
        # Initializes the Orchestrator Tasks tab GUI elements.
        super().__init__(parent, *args, **kwargs)
        self.app_instance = app_instance
        self.parent = parent
        
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._create_widgets()

    def _create_widgets(self):
        # Creates and arranges the widgets within the tab frame.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function_name}", file=f"{__name__}", version=current_version, function=current_function_name)

        try:
            # --- Status Display Frame ---
            status_frame = ttk.Frame(self, style='Dark.TFrame')
            status_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
            status_frame.grid_columnconfigure(1, weight=1)

            ttk.Label(status_frame, text="Orchestrator Status:", style='Header3.TLabel').grid(row=0, column=0, sticky="w")
            
            self.status_var = tk.StringVar(value="STOPPED")
            self.status_label = ttk.Label(status_frame, textvariable=self.status_var, style='Status.Stopped.TLabel')
            self.status_label.grid(row=0, column=1, sticky="w", padx=5)

            # --- Log Table Frame ---
            log_frame = ttk.Frame(self)
            log_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
            log_frame.grid_rowconfigure(0, weight=1)
            log_frame.grid_columnconfigure(0, weight=1)

            # --- Treeview for Logging ---
            columns = ("timestamp", "source", "event")
            self.log_tree = ttk.Treeview(log_frame, columns=columns, show="headings", style="Custom.Treeview")
            
            self.log_tree.heading("timestamp", text="Timestamp")
            self.log_tree.heading("source", text="Source Module")
            self.log_tree.heading("event", text="Event")

            self.log_tree.column("timestamp", width=160, anchor='w')
            self.log_tree.column("source", width=250, anchor='w')
            self.log_tree.column("event", width=300, anchor='w')

            # --- Scrollbar ---
            scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_tree.yview)
            self.log_tree.configure(yscrollcommand=scrollbar.set)

            self.log_tree.grid(row=0, column=0, sticky="nsew")
            scrollbar.grid(row=0, column=1, sticky="ns")

            console_log("✅ Celebration of success! Orchestrator Tasks tab created.")

        except Exception as e:
            console_log(f"❌ Error in _create_widgets for orchestrator tab: {e}")
            debug_log(f"The orchestrator display tab has imploded! The error be: {e}",
                      file=f"{__name__}", version=current_version, function=current_function_name)

    def log_event(self, source="Unknown", event="Status Checked"):
        # Adds a new entry to the log table.
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            values = (timestamp, os.path.basename(source).replace('.py', ''), event)
            
            self.log_tree.insert("", tk.END, values=values)
            self.log_tree.yview_moveto(1)

        except Exception as e:
            print(f"ERROR: Failed to log event to orchestrator tasks tab: {e}")

    def update_status_display(self, is_running, is_paused):
        # Updates the status label based on the orchestrator's state.
        try:
            if is_running and not is_paused:
                self.status_var.set("RUNNING")
                self.status_label.config(style='Status.Running.TLabel')
            elif is_running and is_paused:
                self.status_var.set("PAUSED")
                self.status_label.config(style='Status.Paused.TLabel')
            else:
                self.status_var.set("STOPPED")
                self.status_label.config(style='Status.Stopped.TLabel')
        
        except Exception as e:
            console_log(f"❌ Error in update_status_display for orchestrator tab: {e}")