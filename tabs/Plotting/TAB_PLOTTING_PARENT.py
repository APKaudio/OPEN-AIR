# tabs/Plotting/TAB_PLOTTING_PARENT.py
#
# This file defines the parent tab for Plotting-related functionalities.
# It acts as a container for child tabs such as "Single Scan Plotting",
# "Averaging from Folder", and "3D Scans Over Time".
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
# Version 20250803.2210.4 (REFACTORED: Removed ASCII art logic to break circular import.)
# Version 20250803.0133.1 (Added _on_parent_tab_selected to display ASCII art for Plotting tab.)

current_version = "20250803.2210.4"

import tkinter as tk
from tkinter import ttk
import inspect

# Import the child tabs
from tabs.Plotting.tab_plotting_child_Single import PlottingTab
from tabs.Plotting.tab_plotting_child_average import AveragingTab
from tabs.Plotting.tab_plotting_child_3D import Plotting3DTab

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log
# REMOVED: from src.gui_elements import _print_plot_ascii - THIS CAUSED THE CIRCULAR IMPORT

class TAB_PLOTTING_PARENT(ttk.Frame):
    """
    A parent tab for Plotting-related functionalities.
    """
    def __init__(self, parent, app_instance, console_print_func):
        super().__init__(parent)
        self.app_instance = app_instance
        self.console_print_func = console_print_func

        self.child_notebook = ttk.Notebook(self, style='Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        self.single_scan_plotting_tab = PlottingTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.single_scan_plotting_tab, text="Single Scan Plotting")

        self.averaging_tab = AveragingTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.averaging_tab, text="Averaging from Folder")

        self.three_d_plotting_tab = Plotting3DTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.three_d_plotting_tab, text="3D Scans Over Time")

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