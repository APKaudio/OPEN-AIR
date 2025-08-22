# Plotting/TAB_PLOTTING_PARENT.py
#
# Version 20250821.222500.1 (Refactored for print statements)

import tkinter as tk
from tkinter import ttk
import inspect

from .tab_plotting_child_Single import PlottingTab
from .tab_plotting_child_average import AveragingTab
from .tab_plotting_child_3D import Plotting3DTab

current_version = "20250821.222500.1"

class TAB_PLOTTING_PARENT(ttk.Frame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app_instance = app_instance
        self._create_widgets()

    def _create_widgets(self):
        self.child_notebook = ttk.Notebook(self, style='Plotting.Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)
        self.single_scan_plotting_tab = PlottingTab(self.child_notebook, self.app_instance)
        self.child_notebook.add(self.single_scan_plotting_tab, text="Single Scan Plotting")
        self.averaging_tab = AveragingTab(self.child_notebook, self.app_instance)
        self.child_notebook.add(self.averaging_tab, text="Averaging from Folder")
        self.three_d_plotting_tab = Plotting3DTab(self.child_notebook, self.app_instance)
        self.child_notebook.add(self.three_d_plotting_tab, text="3D Scans Over Time")
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)

    def _on_child_tab_selected(self, event):
        selected_tab_id = self.child_notebook.select()
        if selected_tab_id:
            widget = self.child_notebook.nametowidget(selected_tab_id)
            if hasattr(widget, '_on_tab_selected'):
                widget._on_tab_selected(event)

    def _on_parent_tab_selected(self, event):
        print(f"Plotting Parent tab selected.")
        selected_tab_id = self.child_notebook.select()
        if selected_tab_id:
            widget = self.child_notebook.nametowidget(selected_tab_id)
            if hasattr(widget, '_on_tab_selected'):
                widget._on_tab_selected(event)