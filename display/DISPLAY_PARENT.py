# DISPLAY_PARENT.py
#
# This file defines the display parent container for the application's GUI,
# which is comprised of a TopPane (for the orchestrator) and a BottomPane
# (for various display tabs).
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
# Version 20250814.114500.1

current_version = "20250814.114500.1"
current_version_hash = (20250814 * 114500 * 1)

import tkinter as tk
from tkinter import ttk
import os
import inspect

# --- Import UI Components ---
from orchestrator.orchestrator_gui import OrchestratorGUI
from display.display_child_scan_monitor import ScanMonitorTab
from display.display_child_application_console import ConsoleTab
from orchestrator.display_child_orchestrator_tasks import OrchestratorTasksTab
from display.display_child_debug import DebugTab
from display.console_logic import console_log
from display.debug_logic import debug_log


class TopPane(ttk.Frame):
    """ The top pane, which contains ONLY the orchestrator GUI. """
    def __init__(self, parent, app_instance, orchestrator_logic, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app_instance = app_instance
        self.orchestrator_logic = orchestrator_logic
        self.pack(expand=True, fill='both')
        self._create_widgets()

    def _create_widgets(self):
        orchestrator = OrchestratorGUI(self, self.app_instance, self.orchestrator_logic)
        orchestrator.pack(expand=True, fill='x', padx=5, pady=5)
        self.app_instance.orchestrator_gui = orchestrator
        self.orchestrator_logic.gui = orchestrator

class BottomPane(ttk.Frame):
    """ The bottom pane, containing the notebook for all display tabs. """
    def __init__(self, parent, app_instance, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app_instance = app_instance
        self.pack(expand=True, fill='both')
        self._create_widgets()

    def _create_widgets(self):
        self.notebook = ttk.Notebook(self, style='Bottom.TNotebook')
        self.notebook.pack(expand=True, fill='both', padx=10, pady=(0, 10))

        self.scan_monitor_tab = ScanMonitorTab(self.notebook, self.app_instance)
        self.console_tab = ConsoleTab(self.notebook, self.app_instance)
        self.orchestrator_tasks_tab = OrchestratorTasksTab(self.notebook, self.app_instance)
        self.debug_tab = DebugTab(self.notebook, self.app_instance)

        self.tab_name_to_widget_map = {
            "Monitor": self.scan_monitor_tab,
            "Console": self.console_tab,
            "Orchestrator": self.orchestrator_tasks_tab,
            "Debug": self.debug_tab
        }

        self.notebook.add(self.scan_monitor_tab, text='Scan Monitor')
        self.notebook.add(self.console_tab, text='Console')
        self.notebook.add(self.orchestrator_tasks_tab, text='Orchestrator Tasks')
        self.notebook.add(self.debug_tab, text='Debug')

        self.app_instance.scan_monitor_tab = self.scan_monitor_tab
        self.app_instance.console_tab = self.console_tab
        self.app_instance.orchestrator_tasks_tab = self.orchestrator_tasks_tab
        self.app_instance.debug_tab = self.debug_tab
        
        self.notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)

    def change_display_tab(self, new_tab_name):
        current_function = inspect.currentframe().f_code.co_name
        target_widget = self.tab_name_to_widget_map.get(new_tab_name)
        if target_widget:
            self.notebook.select(target_widget)
            debug_log(f"Switched display tab to '{new_tab_name}'.",
                      file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)
        else:
            console_log(f"❌ Error: Invalid display tab name '{new_tab_name}'.")

    def _on_child_tab_selected(self, event):
        pass # Logic for this can be added if needed

class TAB_DISPLAY_PARENT(ttk.Frame):
    """ The main container for the top and bottom display panes. """
    def __init__(self, parent, app_instance, orchestrator_logic, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app_instance = app_instance
        self.orchestrator_logic = orchestrator_logic
        self.pack(expand=True, fill='both')

        main_paned_window = ttk.PanedWindow(self, orient=tk.VERTICAL)
        main_paned_window.pack(expand=True, fill='both')
        
        top_frame = ttk.Frame(main_paned_window, style='Dark.TFrame')
        bottom_frame = ttk.Frame(main_paned_window, style='Dark.TFrame')
        main_paned_window.add(top_frame, weight=0) 
        main_paned_window.add(bottom_frame, weight=1)

        self.top_pane = TopPane(parent=top_frame, app_instance=self.app_instance, orchestrator_logic=self.orchestrator_logic)
        self.bottom_pane = BottomPane(parent=bottom_frame, app_instance=self.app_instance)

    def change_display_tab(self, new_tab_name):
        # [A brief, one-sentence description of the function's purpose.]
        # Passes the tab change request down to the BottomPane.
        debug_log(f"Passing tab change request for '{new_tab_name}' to BottomPane.",
                  file=f"{os.path.basename(__file__)}", version=current_version, function=inspect.currentframe().f_code.co_name)
        self.bottom_pane.change_display_tab(new_tab_name=new_tab_name)