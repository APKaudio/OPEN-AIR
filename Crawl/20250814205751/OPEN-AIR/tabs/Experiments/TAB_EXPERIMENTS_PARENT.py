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
# Version 20250818.193400.1 (UPDATED: Added a new child tab for YakBeg functionality.)
# Version 20250818.193500.1 (FIXED: Moved YakBegTab import inside __init__ to resolve circular import error.)

import tkinter as tk
from tkinter import ttk
import inspect
import os
from datetime import datetime

# Import the child tabs
from tabs.Experiments.tab_experiments_child_intermod import InterModTab
from tabs.Experiments.tab_experiments_child_JSON_api import JsonApiTab
from tabs.Experiments.tab_experiments_colouring import ColouringTab
from tabs.Experiments.tab_experiments_child_initial_configuration import InitialConfigurationTab
# Removed: from tabs.Experiments.tab_experiments_child_YakBeg import YakBegTab # Removed from top-level imports

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

# --- Version Information ---
current_version = "20250818.193500.1"
current_version_hash = (20250818 * 193500 * 1)

class TAB_EXPERIMENTS_PARENT(ttk.Frame):
    """
    A parent tab for Experiment-related functionalities.
    """
    def __init__(self, parent, app_instance, console_print_func):
        super().__init__(parent)
        self.app_instance = app_instance
        self.console_print_func = console_print_func

        # NEW: Import the child tab inside the __init__ method to break the circular dependency
        from tabs.Experiments.tab_experiments_child_YakBeg import YakBegTab
        
        # Use the specific, color-coded style for this child notebook
        self.child_notebook = ttk.Notebook(self, style='Experiments.Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        self.config_tab = InitialConfigurationTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.config_tab, text="Configuration.ini")

        self.json_api_tab = JsonApiTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.json_api_tab, text="JSON API")

        self.colouring_tab = ColouringTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.colouring_tab, text="Colours")

        self.intermod_tab = InterModTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.intermod_tab, text="Intermod")

        self.yakbeg_tab = YakBegTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.yakbeg_tab, text="YakBeg") # NEW: Add the YakBegTab

        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)

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
        # pane to the "Debug" tab automatically.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Experiments Parent tab selected. Forcing display view to Debug.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  function=current_function)

        # Switch the display parent to the Debug tab
        if hasattr(self.app_instance, 'display_parent_tab'):
            self.app_instance.display_parent_tab.change_display_tab("Debug")

        # Original logic to refresh the active child tab
        self._on_child_tab_selected(event)