# display/DISPLAY_PARENT.py
#
# This file defines the TAB_DISPLAY_PARENT class, which serves as a container
# for all display-related child tabs, including the application console and debug settings.
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
# Version 20250812.235500.34

import tkinter as tk
from tkinter import ttk
import inspect
import os
from datetime import datetime

# Import the child tabs that will be created next
from display.display_child_console import ConsoleTab
from display.display_child_debug import DebugTab
from display.display_child_scan_monitor import ScanMonitorTab

# Import logging functions for debugging
from display.debug_logic import debug_log
from display.console_logic import console_log

# --- Version Information ---
current_version = "20250812.235500.34"
current_version_hash = (20250812 * 235500 * 34)

class TAB_DISPLAY_PARENT(ttk.Frame):
    """
    A parent tab for all display-related functionalities, including console and debug settings.
    """
    def __init__(self, parent, app_instance, console_print_func):
        # Function Description
        # Initializes the TAB_DISPLAY_PARENT frame and its internal components.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing TAB_DISPLAY_PARENT.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        
        super().__init__(parent)
        self.app_instance = app_instance
        self.console_print_func = console_print_func

        self.child_notebook = ttk.Notebook(self, style='Display.Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)
        
        self.child_tabs = {}

        # Create and add the Scan Monitor tab
        self.scan_monitor_tab = ScanMonitorTab(self.child_notebook, self.app_instance)
        self.child_notebook.add(self.scan_monitor_tab, text="Monitor")
        self.child_tabs["ScanMonitorTab"] = self.scan_monitor_tab
        self.app_instance.scan_monitor_tab = self.scan_monitor_tab
        debug_log(f"ScanMonitorTab instance assigned to app_instance successfully!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function, special=True)

        # Create and add the Console tab
        self.console_tab = ConsoleTab(self.child_notebook, self.app_instance)
        self.child_notebook.add(self.console_tab, text="Console")
        self.child_tabs["ConsoleTab"] = self.console_tab

        # Create and add the Debug tab
        self.debug_tab = DebugTab(self.child_notebook, self.app_instance)
        self.child_notebook.add(self.debug_tab, text="Debug")
        self.child_tabs["DebugTab"] = self.debug_tab

        # NEW: Create a map for easy tab switching by name
        self.tab_name_to_widget_map = {
            "Monitor": self.scan_monitor_tab,
            "Console": self.console_tab,
            "Debug": self.debug_tab
        }

        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)
        
        debug_log(f"TAB_DISPLAY_PARENT initialized. The new display tabs are ready for action!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)

    def change_display_tab(self, new_tab_name):
        # Function Description
        # Programmatically selects a child tab by its name ("Monitor", "Console", or "Debug").
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        
        target_widget = self.tab_name_to_widget_map.get(new_tab_name)
        if target_widget:
            self.child_notebook.select(target_widget)
            debug_log(f"Programmatically switched display tab to '{new_tab_name}'.",
                      file=f"{current_file} - {current_version}",
                      function=current_function)
        else:
            self.console_print_func(f"❌ Error: Invalid display tab name '{new_tab_name}'.")
            debug_log(f"Attempted to switch to an invalid display tab: '{new_tab_name}'. This is a foul-up!",
                      file=f"{current_file} - {current_version}",
                      function=current_function)

    def _on_child_tab_selected(self, event):
        # Function Description
        # Handles tab change events within this parent's child notebook.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Child tab selected in Display Parent. Checking for tab handler.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)

        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)

    def _on_parent_tab_selected(self, event):
        # Function Description
        # Handles the event when this parent tab is selected.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Display Parent tab selected. Initializing child tab handlers.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        self._on_child_tab_selected(event)