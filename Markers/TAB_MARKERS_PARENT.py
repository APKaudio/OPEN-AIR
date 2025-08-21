# FolderName/TAB_MARKERS_PARENT.py
#
# This file defines the TAB_MARKERS_PARENT class, which serves as a container
# for the 'Showtime' and 'Import & Edit' child tabs.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250821.140800.1
# FIXED: The AttributeError was fixed by adding `console_print_func` as a positional
#        argument and assigning it directly, resolving the race condition.
# FIXED: Added custom styling for the child notebook tabs to match the Markers' color palette.
# FIXED: Added missing versioning variables to resolve NameError in debug logging.

import tkinter as tk
from tkinter import ttk
import typing
import os
import inspect
from datetime import datetime
from display.debug_logic import debug_log
from display.console_logic import console_log
from src.program_style import COLOR_PALETTE, COLOR_PALETTE_TABS, _get_dark_color

# --- Versioning ---
w = 20250821
x = 140800
y = 1
current_version = f"Version {w}.{x}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"

# Import the specific child tab classes
from .showtime.tab_markers_parent_showtime import ShowtimeParentTab
from .files.tab_markers_child_import_and_edit import ReportConverterTab

class TAB_MARKERS_PARENT(ttk.Frame):
    def __init__(self, parent_notebook, app_instance, console_print_func, *args, **kwargs):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)

        try:
            super().__init__(parent_notebook, **kwargs)
            self.app_instance = app_instance
            self.parent_notebook = parent_notebook
            self.console_print_func = console_print_func
            
            # --- NEW: Apply custom styling for the child notebook tabs ---
            style = ttk.Style(self)
            active_color = COLOR_PALETTE_TABS['Markers']['active']
            inactive_color = _get_dark_color(active_color)
            
            style.configure('Markers.Child.TNotebook', background=COLOR_PALETTE['background'])
            style.map('Markers.Child.TNotebook.Tab',
                    background=[('selected', active_color),
                                ('!selected', inactive_color)],
                    foreground=[('selected', COLOR_PALETTE_TABS['Markers']['fg']),
                                ('!selected', 'white')])

            self.child_notebook = ttk.Notebook(self, style='Markers.Child.TNotebook')
            self.child_notebook.pack(expand=True, fill="both")

            self.showtime_tab = ShowtimeParentTab(self.child_notebook, self.app_instance, self.console_print_func)
            self.child_notebook.add(self.showtime_tab, text="Showtime")

            self.import_edit_tab = ReportConverterTab(self.child_notebook, self.app_instance)
            self.child_notebook.add(self.import_edit_tab, text="Import & Edit")

            # Bind the tab-change event to our handler
            self.child_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)
            
            debug_log("Exiting __init__. Child tabs added.",
                      file=f"{os.path.basename(__file__)}",
                      version=current_version,
                      function=current_function)
        except Exception as e:
            console_log(f"❌ Error in TAB_MARKERS_PARENT initialization: {e}", "ERROR")
            debug_log(f"Arrr, the code be capsized! The error be: {e}",
                      file=f"{os.path.basename(__file__)}",
                      version=current_version,
                      function=current_function)
            raise

    def _on_child_tab_selected(self, event):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)

        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)


    def _on_parent_tab_selected(self, event):
        # Handles the event when this parent tab is selected. It now also switches the display
        # pane to the "Monitor" tab automatically.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        if hasattr(self.app_instance, 'display_parent_tab'):
            self.app_instance.display_parent_tab.change_display_tab("Monitor")

        # Delegate to the currently active child tab to ensure it is properly refreshed
        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
