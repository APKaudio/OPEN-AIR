# tabs/Markers/TAB_MARKERS_PARENT.py
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
# Version 20250814.164500.1

current_version = "20250814.164500.1"
current_version_hash = (20250814 * 164500 * 1)

import tkinter as tk
from tkinter import ttk
import typing

# Import the specific child tab classes
from tabs.Markers.tab_markers_child_import_and_edit import ReportConverterTab
from tabs.Markers.tab_markers_child_showtime import ShowtimeTab


class TAB_MARKERS_PARENT(ttk.Frame):
    def __init__(self, parent, app_instance, console_print_func):
        # [A brief, one-sentence description of the function's purpose.]
        # Initializes the master tab container for all marker-related tabs.
        super().__init__(parent)
        self.app_instance = app_instance
        self.console_print_func = console_print_func

        # Use the specific, color-coded style for this child notebook
        self.child_notebook = ttk.Notebook(self, style='Markers.Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        # Instantiate the child tabs
        self.showtime_tab = ShowtimeTab(self.child_notebook, self.app_instance)
        self.child_notebook.add(self.showtime_tab, text="Showtime")

        self.report_converter_tab = ReportConverterTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.report_converter_tab, text="Import & Edit")
        
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)


    def _on_child_tab_selected(self, event):
        # [A brief, one-sentence description of the function's purpose.]
        # Handles tab change events within this parent's child notebook.
        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)


    def _on_parent_tab_selected(self, event):
        # [A brief, one-sentence description of the function's purpose.]
        # Handles the event when this parent tab is selected. It now also switches the display
        # pane to the "Monitor" tab automatically.
        if hasattr(self.app_instance, 'display_parent_tab'):
            self.app_instance.display_parent_tab.change_display_tab("Monitor")

        # Delegate to the currently active child tab to ensure it is properly refreshed.
        self._on_child_tab_selected(event)