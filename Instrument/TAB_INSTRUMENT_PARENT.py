# Instrument/TAB_INSTRUMENT_PARENT.py
#
# Version 20250821.224500.1 (Refactored to remove console_print_func dependency)

import tkinter as tk
from tkinter import ttk
import inspect
import os

from .connection.tab_instrument_child_connection import InstrumentTab
from .visa.tab_instrument_child_visa_interpreter import VisaInterpreterTab
from .settings.tab_instrument_child_settings import SettingsParentTab

class TAB_INSTRUMENT_PARENT(ttk.Frame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app_instance = app_instance
        self._create_widgets()
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)

    def _create_widgets(self):
        self.child_notebook = ttk.Notebook(self, style='Instruments.Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)
        
        # --- DEFINITIVE FIX: Child tabs no longer receive console_print_func ---
        self.connection_tab = InstrumentTab(self.child_notebook, self.app_instance)
        self.settings_tab = SettingsParentTab(self.child_notebook, self.app_instance)
        self.visa_interpreter_tab = VisaInterpreterTab(self.child_notebook, self.app_instance)
        
        self.child_notebook.add(self.connection_tab, text="Connection")
        self.child_notebook.add(self.settings_tab, text="Settings")
        self.child_notebook.add(self.visa_interpreter_tab, text="VISA Interpreter")

    def _on_child_tab_selected(self, event):
        selected_tab_id = self.child_notebook.select()
        if selected_tab_id:
            widget = self.child_notebook.nametowidget(selected_tab_id)
            if hasattr(widget, '_on_tab_selected'):
                widget._on_tab_selected(event)

    def _on_parent_tab_selected(self, event):
        print(f"Instrument Parent tab selected. Forcing display view to Console.")
        if hasattr(self.app_instance, 'display_parent'):
            self.app_instance.display_parent.notebook.select(0)
        selected_tab_id = self.child_notebook.select()
        if selected_tab_id:
            widget = self.child_notebook.nametowidget(selected_tab_id)
            if hasattr(widget, '_on_tab_selected'):
                widget._on_tab_selected(event)