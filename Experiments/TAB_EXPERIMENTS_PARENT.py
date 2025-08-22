# Experiments/TAB_EXPERIMENTS_PARENT.py
#
# Version 20250821.222500.1 (Refactored for print statements)

import tkinter as tk
from tkinter import ttk
import inspect
import os
from datetime import datetime

current_version = "20250821.222500.1"

class ExperimentsParentTab(ttk.Frame):
    def __init__(self, parent, app_instance, style_obj):
        super().__init__(parent)
        self.app_instance = app_instance
        self.style_obj = style_obj
        from .tab_experiments_child_yak_beg import YakBegTab
        from .tab_experiments_child_credits import CreditsTab
        self._create_widgets(YakBegTab, CreditsTab)

    def _create_widgets(self, YakBegTab, CreditsTab):
        self.child_notebook = ttk.Notebook(self, style='Experiments.Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)
        self.credits_tab = CreditsTab(self.child_notebook, self.app_instance)
        self.yak_beg_tab = YakBegTab(self.child_notebook, self.app_instance)
        self.child_notebook.add(self.credits_tab, text="Credits")
        self.child_notebook.add(self.yak_beg_tab, text="Yak Beg")
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)

    def _on_child_tab_selected(self, event):
        selected_tab_id = self.child_notebook.select()
        if selected_tab_id:
            widget = self.child_notebook.nametowidget(selected_tab_id)
            if hasattr(widget, '_on_tab_selected'):
                widget._on_tab_selected(event)

    def _on_parent_tab_selected(self, event):
        print(f"Experiments Parent tab selected. Forcing display view to Debug.")
        if hasattr(self.app_instance, 'display_parent'):
            self.app_instance.display_parent.notebook.select(1)
        selected_tab_id = self.child_notebook.select()
        if selected_tab_id:
            widget = self.child_notebook.nametowidget(selected_tab_id)
            if hasattr(widget, '_on_tab_selected'):
                widget._on_tab_selected(event)