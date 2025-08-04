# tabs/Markers/TAB_MARKERS_PARENT.py
#
# This file defines the parent tab for Marker-related functionalities.
# It acts as a container for child tabs such as "Markers Display" and "Report Converter".
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
# Version 20250803.2210.1 (REFACTORED: Removed ASCII art logic to break circular import.)
# Version 20250803.0143.1 (Modified _on_parent_tab_selected to always select the first child tab.)

current_version = "20250803.2210.1"

import tkinter as tk
from tkinter import ttk
import inspect

# Import the child tabs
from tabs.Markers.tab_markers_child_display import MarkersDisplayTab
from tabs.Markers.tab_markers_child_import_and_edit import ReportConverterTab

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log
# REMOVED: from src.gui_elements import _print_marks_ascii - THIS CAUSED THE CIRCULAR IMPORT

class TAB_MARKERS_PARENT(ttk.Frame):
    """
    A parent tab for Marker-related functionalities.
    """
    def __init__(self, parent, app_instance, console_print_func):
        super().__init__(parent)
        self.app_instance = app_instance
        self.console_print_func = console_print_func

        self.child_notebook = ttk.Notebook(self, style='Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        # FIX: Explicitly pass headers=None and rows=None to MarkersDisplayTab constructor
        self.marker_display_tab = MarkersDisplayTab(self.child_notebook, headers=None, rows=None, app_instance=self.app_instance)
        self.child_notebook.add(self.marker_display_tab, text="Markers Display")

        self.report_converter_tab = ReportConverterTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.report_converter_tab, text="Report Converter")

        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)

    def _on_child_tab_selected(self, event):
        """Handles tab change events within this parent's child notebook."""
        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)

    def _on_parent_tab_selected(self, event):
        """
        Handles the event when this parent tab is selected.
        The core logic is now handled by main_app.py.
        """
        # Get the list of all child tab IDs
        child_tab_ids = self.child_notebook.tabs()
        if child_tab_ids:
            # Select the first child tab
            self.child_notebook.select(child_tab_ids[0])
            self._on_child_tab_selected(event)