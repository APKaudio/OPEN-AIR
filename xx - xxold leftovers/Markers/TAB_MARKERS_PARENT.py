# Markers/TAB_MARKERS_PARENT.py
#
# Version 20250821.222500.1 (Refactored for print statements)

import tkinter as tk
from tkinter import ttk
import os
import inspect
from datetime import datetime

from .showtime.tab_markers_parent_showtime import ShowtimeTab
from .files.tab_markers_child_import_and_edit import ReportConverterTab

current_version = "20250821.222500.1"
current_file = os.path.basename(__file__)

class TAB_MARKERS_PARENT(ttk.Frame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app_instance = app_instance
        self._create_widgets()
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)

    def _create_widgets(self):
        self.child_notebook = ttk.Notebook(self, style='Markers.Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)
        self.showtime_tab = ShowtimeTab(self.child_notebook, self.app_instance)
        self.import_export_tab = ReportConverterTab(self.child_notebook, self.app_instance)
        self.child_notebook.add(self.showtime_tab, text="Showtime")
        self.child_notebook.add(self.import_export_tab, text="Import & Edit")

    def _on_child_tab_selected(self, event):
        print(f"Markers child tab selected.")
        selected_tab_id = self.child_notebook.select()
        if selected_tab_id:
            widget = self.child_notebook.nametowidget(selected_tab_id)
            if hasattr(widget, '_on_tab_selected'):
                widget._on_tab_selected(event)

    def _on_parent_tab_selected(self, event):
        print(f"Markers Parent tab selected.")
        if hasattr(self.app_instance, 'display_parent'):
            self.app_instance.display_parent.notebook.select(2)
        selected_tab_id = self.child_notebook.select()
        if selected_tab_id:
            widget = self.child_notebook.nametowidget(selected_tab_id)
            if hasattr(widget, '_on_tab_selected'):
                widget._on_tab_selected(event)