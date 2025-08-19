# FolderName/TAB_MARKERS_PARENT.py
#
# This file defines the TAB_MARKERS_PARENT class, which serves as a container
# for the 'Showtime' and 'Import & Edit' child tabs.
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
# Version 20250814.164500.3

current_version = "20250814.164500.3"
current_version_hash = (20250814 * 164500 * 3)

import tkinter as tk
from tkinter import ttk
import typing
import os
import inspect
from display.debug_logic import debug_log
from display.console_logic import console_log

# Import the specific child tab classes
from tabs.Markers.showtime.tab_markers_parent_showtime import ShowtimeTab
from tabs.Markers.files.tab_markers_child_import_and_edit import ReportConverterTab

class TAB_MARKERS_PARENT(ttk.Frame):
    def __init__(self, parent, app_instance, console_print_func):
        # Initializes the master tab container for all marker-related tabs.
        super().__init__(parent)
        self.app_instance = app_instance
        self.console_print_func = console_print_func
        
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        # NEW: Import the child tab inside the __init__ method to break the circular dependency
        

        # Use the specific, color-coded style for this child notebook
        self.child_notebook = ttk.Notebook(self, style='Markers.Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        # Instantiate the child tabs
        self.showtime_tab = ShowtimeTab(self.child_notebook, self.app_instance)
        self.child_notebook.add(self.showtime_tab, text="Showtime")

        self.report_converter_tab = ReportConverterTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.report_converter_tab, text="Import & Edit")

        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)
        
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)


    def _on_child_tab_selected(self, event):
        # Handles tab change events within this parent's child notebook.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)

        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)


    def _on_parent_tab_selected(self, event):
        # Handles the event when this parent tab is selected. It now also switches the display
        # pane to the "Monitor" tab automatically.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        if hasattr(self.app_instance, 'display_parent_tab'):
            self.app_instance.display_parent_tab.change_display_tab("Monitor")

        # Delegate to the currently active child tab to ensure it is properly refreshed.
        self._on_child_tab_selected(event)
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)