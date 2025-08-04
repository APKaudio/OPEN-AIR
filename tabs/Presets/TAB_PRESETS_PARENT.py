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
# Version 20250803.2300.2 (REFACTORED: Applied color-coded child notebook style.)
# Version 20250803.224000.0 (FIXED: Added missing style_obj argument to DevicePresetsTab constructor.)
# Version 20250803.2210.2 (REFACTORED: Removed ASCII art logic to break circular import.)

current_version = "20250803.2300.2"

import tkinter as tk
from tkinter import ttk
import inspect
import os

from tabs.Presets.tab_presets_child_local import LocalPresetsTab
from tabs.Presets.tab_presets_child_device import DevicePresetsTab
from tabs.Presets.tab_presets_child_preset_editor import PresetEditorTab
from src.debug_logic import debug_log
from src.console_logic import console_log

class TAB_PRESETS_PARENT(ttk.Frame):
    """
    A parent tab for Presets-related functionalities.
    """
    def __init__(self, parent, app_instance, console_print_func):
        super().__init__(parent)
        self.app_instance = app_instance
        self.console_print_func = console_print_func

        # Use the specific, color-coded style for this child notebook
        self.child_notebook = ttk.Notebook(self, style='Presets.Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        self.local_presets_tab = LocalPresetsTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.local_presets_tab, text="Local Presets")

        self.preset_editor_tab = PresetEditorTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.child_notebook.add(self.preset_editor_tab, text="Preset Editor")

        self.device_presets_tab = DevicePresetsTab(self.child_notebook, self.app_instance, self.console_print_func, style_obj=self.app_instance.style)
        self.child_notebook.add(self.device_presets_tab, text="Presets In Device")

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