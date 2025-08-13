# tabs/Markers/TAB_MARKERS_PARENT.py
#
# This file defines the parent tab for Marker-related functionalities.
# It acts as a container for child tabs such as "Showtime", "Markers Display" and "Report Converter".
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
# Version 20250812.235700.2

import tkinter as tk
from tkinter import ttk
import inspect
import os
from datetime import datetime

from tabs.Markers.tab_markers_child_display import MarkersDisplayTab
from tabs.Markers.tab_markers_child_import_and_edit import ReportConverterTab
from tabs.Markers.tab_markers_child_showtime import ShowtimeTab
from display.debug_logic import debug_log
from display.console_logic import console_log

# --- Version Information ---
current_version = "20250812.235700.2"
current_version_hash = (20250812 * 235700 * 2)

class TAB_MARKERS_PARENT(ttk.Frame):
    """
    A parent tab for Marker-related functionalities.
    """
    def __init__(self, parent, app_instance, console_print_func):
        super().__init__(parent)
        self.app_instance = app_instance
        self.console_print_func = console_print_func

        # Use the specific, color-coded style for this child notebook
        self.child_notebook = ttk.Notebook(self, style='Markers.Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        # Add the ShowtimeTab as the first tab
        self.showtime_tab = ShowtimeTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.showtime_tab, text="Showtime")

        self.marker_display_tab = MarkersDisplayTab(self.child_notebook, headers=None, rows=None, app_instance=self.app_instance)
        self.child_notebook.add(self.marker_display_tab, text="Markers Display")

        self.report_converter_tab = ReportConverterTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.report_converter_tab, text="Report Converter")

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
        # Handles the event when this parent tab is selected. It automatically switches the
        # display pane to the "Monitor" tab and then selects the first child tab within this parent.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Markers Parent tab selected. Forcing display view to Monitor.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  function=current_function)

        # Switch the display parent to the Monitor tab
        if hasattr(self.app_instance, 'display_parent_tab'):
            self.app_instance.display_parent_tab.change_display_tab("Monitor")

        # Original logic to select the first child tab and refresh it
        child_tab_ids = self.child_notebook.tabs()
        if child_tab_ids:
            self.child_notebook.select(child_tab_ids[0])
            self._on_child_tab_selected(event)