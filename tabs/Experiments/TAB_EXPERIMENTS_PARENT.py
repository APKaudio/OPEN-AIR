# tabs/Experiments/TAB_EXPERIMENTS_PARENT.py
#
# This file defines the parent tab for Experiment-related functionalities.
# It acts as a container for child tabs such as "Intermod" and "JSON API".
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
# Version 20250803.2210.5 (REFACTORED: Removed ASCII art logic to break circular import.)
# Version 20250803.0136.1 (Added _on_parent_tab_selected to display ASCII art for Experiments tab.)

current_version = "20250803.2210.5"

import tkinter as tk
from tkinter import ttk
import inspect

# Import the child tabs
from tabs.Experiments.tab_experiments_child_intermod import InterModTab
from tabs.Experiments.tab_experiments_child_JSON_api import JsonApiTab
from tabs.Experiments.tab_experiments_colouring import ColouringTab
from tabs.Experiments.tab_experiments_child_initial_configuration import InitialConfigurationTab

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log
# REMOVED: from src.gui_elements import _print_xxx_ascii - THIS CAUSED THE CIRCULAR IMPORT

class TAB_EXPERIMENTS_PARENT(ttk.Frame):
    """
    A parent tab for Experiment-related functionalities.
    """
    def __init__(self, parent, app_instance, console_print_func):
        super().__init__(parent)
        self.app_instance = app_instance
        self.console_print_func = console_print_func

        self.child_notebook = ttk.Notebook(self, style='Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        self.config_tab = InitialConfigurationTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.config_tab, text="Configuration.ini")

        self.json_api_tab = JsonApiTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.json_api_tab, text="JSON API")

        self.colouring_tab = ColouringTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.colouring_tab, text="Colours")

        self.intermod_tab = InterModTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.intermod_tab, text="Intermod")

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
        self._on_child_tab_selected(event)