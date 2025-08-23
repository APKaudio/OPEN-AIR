# Scanning/TAB_SCANNING_PARENT.py
#
# Version 20250821.222500.1 (Refactored for print statements)

import tkinter as tk
from tkinter import ttk
import inspect
import os

from .tab_scanning_child_scan_configuration import ScanTab
from .tab_scanning_child_scan_meta_data import ScanMetaDataTab
from .tab_scanning_child_bands import BandsTab

current_version = "20250821.222500.1"

class TAB_SCANNING_PARENT(ttk.Frame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app_instance = app_instance
        self._create_widgets()

    def _create_widgets(self):
        self.child_notebook = ttk.Notebook(self, style='Scanning.Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)
        self.scan_tab = ScanTab(self.child_notebook, self.app_instance)
        self.bands_tab = BandsTab(self.child_notebook, self.app_instance)
        self.meta_data_tab = ScanMetaDataTab(self.child_notebook, self.app_instance)
        self.child_notebook.add(self.scan_tab, text="Scan Configuration")
        self.child_notebook.add(self.bands_tab, text="Scan Bands")
        self.child_notebook.add(self.meta_data_tab, text="Scan Meta Data")
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)

    def _on_child_tab_selected(self, event):
        print(f"Scanning child tab selected.")
        selected_tab_id = self.child_notebook.select()
        if selected_tab_id:
            widget = self.child_notebook.nametowidget(selected_tab_id)
            if hasattr(widget, '_on_tab_selected'):
                widget._on_tab_selected(event)

    def _on_parent_tab_selected(self, event):
        print(f"Scanning Parent tab selected.")
        selected_tab_id = self.child_notebook.select()
        if selected_tab_id:
            widget = self.child_notebook.nametowidget(selected_tab_id)
            if hasattr(widget, '_on_tab_selected'):
                widget._on_tab_selected(event)