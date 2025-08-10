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
# Version 20250810.155200.2 (UPDATED: Added a new child tab for Scan Monitoring and placed it first.)

current_version = "20250810.155200.2"
current_version_hash = 20250810 * 155200 * 2 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect
import os


# Import the child tabs that will be created next
from display.display_child_console import ConsoleTab
from display.display_child_debug import DebugTab
from display.display_child_scan_monitor import ScanMonitorTab # NEW: Import the new scan monitor tab

# Import logging functions for debugging
from display.debug_logic import debug_log
from display.console_logic import console_log

class TAB_DISPLAY_PARENT(ttk.Frame):
    """
    A parent tab for all display-related functionalities, including console and debug settings.
    """
    def __init__(self, parent, app_instance, console_print_func):
        # This function description tells me what this function does
        # Initializes the TAB_DISPLAY_PARENT frame and its internal components.
        # It sets up a new Notebook widget to host the child tabs, and creates instances
        # of the ConsoleTab and DebugTab classes, adding them to the notebook.
        #
        # Inputs to this function
        #   parent (tk.Widget): The parent widget, typically a ttk.Notebook.
        #   app_instance (object): A reference to the main application instance.
        #   console_print_func (function): A function to use for console output.
        #
        # Process of this function
        #   1. Calls the parent class's __init__ method.
        #   2. Stores references to the main app instance and console function.
        #   3. Creates a new `ttk.Notebook` instance.
        #   4. Creates an instance of `ConsoleTab` and adds it to the notebook.
        #   5. Creates an instance of `DebugTab` and adds it to the notebook.
        #   6. Binds the notebook's `<<NotebookTabChanged>>` event to a handler.
        #
        # Outputs of this function
        #   None. Initializes the parent tab and its child tabs.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing TAB_DISPLAY_PARENT. Let's get this tab set up!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        super().__init__(parent)
        self.app_instance = app_instance
        self.console_print_func = console_print_func

        # Use the specific, color-coded style for this child notebook
        self.child_notebook = ttk.Notebook(self, style='Display.Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        # NEW: Create and add the Scan Monitor tab first
        self.scan_monitor_tab = ScanMonitorTab(self.child_notebook, self.app_instance)
        self.child_notebook.add(self.scan_monitor_tab, text="Monitor")

        # CORRECTED: No longer passing console_print_func to child tabs
        self.console_tab = ConsoleTab(self.child_notebook, self.app_instance)
        self.child_notebook.add(self.console_tab, text="Console")

        # CORRECTED: No longer passing console_print_func to child tabs
        self.debug_tab = DebugTab(self.child_notebook, self.app_instance)
        self.child_notebook.add(self.debug_tab, text="Debug")

        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)
        
        debug_log(f"TAB_DISPLAY_PARENT initialized. The new display tabs are ready for action!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _on_child_tab_selected(self, event):
        # This function description tells me what this function does
        # Handles tab change events within this parent's child notebook.
        # It gets the currently selected tab and calls a specific handler
        # on that child tab if it has one.
        #
        # Inputs to this function
        #   event (tkinter.Event): The event object that triggered the tab change.
        #
        # Process of this function
        #   1. Retrieves the ID of the currently selected tab.
        #   2. Converts the ID to its corresponding widget instance.
        #   3. Checks if the widget has an `_on_tab_selected` method.
        #   4. If the method exists, it is called to allow the child tab to
        #      update its state.
        #
        # Outputs of this function
        #   None. Triggers a method call on a child tab.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Child tab selected in Display Parent. Checking for tab handler.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)

    def _on_parent_tab_selected(self, event):
        # This function description tells me what this function does
        # Handles the event when this parent tab is selected.
        # It delegates the event to the currently active child tab to ensure
        # that it is properly refreshed.
        #
        # Inputs to this function
        #   event (tkinter.Event): The event object from the parent notebook.
        #
        # Process of this function
        #   1. Calls `_on_child_tab_selected` to trigger the handler for the
        #      currently active child tab.
        #
        # Outputs of this function
        #   None.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Display Parent tab selected. Initializing child tab handlers.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        self._on_child_tab_selected(event)
