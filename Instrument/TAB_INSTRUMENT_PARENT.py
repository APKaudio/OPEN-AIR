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
# Version 20250815.103400.1
# REFACTORED: The monolithic SettingsTab has been replaced with the new SettingsParentTab container.

current_version = "20250815.103400.1"
current_version_hash = (20250815 * 103400 * 1)

import tkinter as tk
from tkinter import ttk
import inspect
import os
from datetime import datetime

from .connection.tab_instrument_child_connection import InstrumentTab
from .visa.tab_instrument_child_visa_interpreter import VisaInterpreterTab
from .settings.tab_instrument_child_settings import SettingsParentTab

from display.debug_logic import debug_log
from display.console_logic import console_log

# Import the new SettingsParentTab that now contains the refactored settings UI.


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
        # Pass a reference of this parent instance to the connection tab
        self.instrument_connection_tab = InstrumentTab(self.child_notebook, self.app_instance, self.console_print_func, parent_notebook_ref=self)
        
        # Instantiate the new SettingsParentTab
        self.settings_tab = SettingsParentTab(self.child_notebook, self.app_instance, self.console_print_func)
        
        self.visa_interpreter_tab = VisaInterpreterTab(self.child_notebook, self.app_instance, self.console_print_func)

        # RENAMED the tab text to "Connection"
        self.child_notebook.add(self.instrument_connection_tab, text="Connection")
        self.child_notebook.add(self.settings_tab, text="Settings")
        self.child_notebook.add(self.visa_interpreter_tab, text="VISA Interpreter")

        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)

    def switch_to_settings_tab(self):
        # Function Description
        # Programmatically selects the 'Settings' child tab.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Programmatically switching to Settings tab.",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)
        self.child_notebook.select(self.settings_tab)

    def _on_child_tab_selected(self, event):
        """Handles tab change events within this parent's child notebook."""
        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)

    def _on_parent_tab_selected(self, event):
        # Function Description
        # Handles the event when this parent tab is selected. It now also switches the display
        # pane to the "Console" tab automatically.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Instrument Parent tab selected. Forcing display view to Console.",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)

        # Switch the display parent to the Console tab
        if hasattr(self.app_instance, 'display_parent_tab'):
            self.app_instance.display_parent_tab.change_display_tab("Console")

        # Delegate to the currently active child tab to ensure it is properly refreshed.
        self._on_child_tab_selected(event)
