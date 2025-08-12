# tabs/Instrument/TAB_INSTRUMENT_PARENT.py
#
# This file defines the TAB_INSTRUMENT_PARENT class, which serves as a container
# for all instrument-related child tabs.
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
# Version 20250811.221500.1 (FIXED: Corrected the instantiation order in __init__ to prevent an AttributeError.)

current_version = "20250811.221500.1"
current_version_hash = 20250811 * 221500 * 1

import tkinter as tk
from tkinter import ttk
import inspect

from tabs.Instrument.tab_instrument_child_connection import InstrumentTab # NEW: Import the connection tab
from tabs.Instrument.tab_instrument_child_settings import SettingsTab # NEW: Import the new settings tab
from tabs.Instrument.tab_instrument_child_visa_interpreter import VisaInterpreterTab
from display.debug_logic import debug_log
from display.console_logic import console_log

class TAB_INSTRUMENT_PARENT(ttk.Frame):
    """
    A parent tab for Instrument-related functionalities.
    """
    def __init__(self, parent, app_instance, console_print_func):
        super().__init__(parent)
        self.app_instance = app_instance
        self.console_print_func = console_print_func

        # Use the specific, color-coded style for this child notebook
        self.child_notebook = ttk.Notebook(self, style='Instruments.Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Instantiate the tabs before adding them to the notebook
        self.instrument_settings_tab = InstrumentTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.settings_tab = SettingsTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.visa_interpreter_tab = VisaInterpreterTab(self.child_notebook, self.app_instance, self.console_print_func)

        self.child_notebook.add(self.instrument_settings_tab, text="Connection & Settings")
        self.child_notebook.add(self.settings_tab, text="Settings")
        self.child_notebook.add(self.visa_interpreter_tab, text="VISA Interpreter")

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
        """
        self._on_child_tab_selected(event)