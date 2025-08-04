# tabs/Scanning/TAB_SCANNING_PARENT.py
#
# This file defines the parent tab for Scanning-related functionalities.
# It acts as a container for child tabs such as "Scan Configuration" and "Scan Meta Data".
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
# Version 20250803.2210.3 (REFACTORED: Removed ASCII art logic to break circular import.)
# Version 20250803.1930.0 (FIXED: Corrected typo in import name 'ScanTa' to 'ScanTab'.)

current_version = "20250803.2210.3"

import tkinter as tk
from tkinter import ttk
import inspect

# Import the child tabs
from tabs.Scanning.tab_scanning_child_scan_configuration import ScanTab
from tabs.Scanning.tab_scanning_child_scan_meta_data import ScanMetaDataTab

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log
# REMOVED: from src.gui_elements import _print_scan_ascii - THIS CAUSED THE CIRCULAR IMPORT

class TAB_SCANNING_PARENT(ttk.Frame):
    """
    A parent tab for Scanning-related functionalities.
    """
    def __init__(self, parent, app_instance, console_print_func):
        super().__init__(parent)
        self.app_instance = app_instance
        self.console_print_func = console_print_func

        self.child_notebook = ttk.Notebook(self, style='Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        self.scan_config_tab = ScanTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.scan_config_tab, text="Scan Configuration")

        self.scan_meta_data_tab = ScanMetaDataTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.scan_meta_data_tab, text="Scan Meta Data")

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