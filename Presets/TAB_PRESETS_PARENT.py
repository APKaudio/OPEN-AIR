# tabs/Presets/TAB_PRESETS_PARENT.py
#
# This file defines the TAB_PRESETS_PARENT class, which serves as a container
# for all preset-related child tabs.
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
# Version 20250803.2300.3
# FIXED: Corrected the AttributeError by changing the style object from 'style' to 'style_obj'.
# REFACTORED: Applied color-coded child notebook style.

current_version = "20250803.2300.3"
current_version_hash = (20250803 * 2300 * 3)

import tkinter as tk
from tkinter import ttk
import inspect
import os

from .tab_presets_child_local import LocalPresetsTab
from .tab_presets_child_device import DevicePresetsTab
from .tab_presets_child_preset_editor import PresetEditorTab
from display.debug_logic import debug_log
from display.console_logic import console_log

class TAB_PRESETS_PARENT(ttk.Frame):
    """
    A parent tab for all preset-related functionalities.
    """
    def __init__(self, parent_notebook, app_instance, console_print_func):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"📘 🟢 Entering {current_function}",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)

        super().__init__(parent_notebook)
        
        self.app_instance = app_instance
        self.console_print_func = console_print_func
        self.child_tabs = {} # Dictionary to hold child tab instances
        
        # Configure grid for this frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create a notebook for the child tabs
        self.child_notebook = ttk.Notebook(self, style='Presets.Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        self.local_presets_tab = LocalPresetsTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.local_presets_tab, text="Local Presets")
        self.child_tabs["Local Presets"] = self.local_presets_tab

        self.preset_editor_tab = PresetEditorTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.preset_editor_tab, text="Preset Editor")
        self.child_tabs["Preset Editor"] = self.preset_editor_tab

        # FIXED: Changed app_instance.style to app_instance.style_obj
        self.device_presets_tab = DevicePresetsTab(self.child_notebook, self.app_instance, self.console_print_func, style_obj=self.app_instance.style_obj)
        self.child_notebook.add(self.device_presets_tab, text="Presets In Device")
        self.child_tabs["Presets In Device"] = self.device_presets_tab
        
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)

        debug_log(f"📘 ✅ Exiting {current_function}",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)

    def _on_child_tab_selected(self, event):
        """Handles tab change events within this parent's child notebook."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"📘 🟢 Child tab selected in Presets Parent. Checking for tab handler.",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)
        
        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)
        
        debug_log(f"📘 ✅ Exiting {current_function}",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)

    def _on_parent_tab_selected(self, event):
        """
        Handles the event when this parent tab is selected.
        It delegates the event to the currently active child tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"📘 🟢 Presets Parent tab selected. Initializing child tab handlers.",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)

        # Delegate to the currently active child tab to ensure it is properly refreshed
        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)
        
        debug_log(f"📘 ✅ Exiting {current_function}",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)