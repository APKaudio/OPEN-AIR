# Presets/TAB_PRESETS_PARENT.py
#
# Version 20250821.222500.1 (Refactored for print statements)

import tkinter as tk
from tkinter import ttk
import inspect
import os

from .tab_presets_child_local import LocalPresetsTab
from .tab_presets_child_device import DevicePresetsTab
from .tab_presets_child_preset_editor import PresetEditorTab

current_version = "20250821.222500.1"

class TAB_PRESETS_PARENT(ttk.Frame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app_instance = app_instance
        self._create_widgets()

    def _create_widgets(self):
        self.child_notebook = ttk.Notebook(self, style='Presets.Child.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)
        self.local_presets_tab = LocalPresetsTab(self.child_notebook, self.app_instance)
        self.device_presets_tab = DevicePresetsTab(self.child_notebook, self.app_instance)
        self.preset_editor_tab = PresetEditorTab(self.child_notebook, self.app_instance)
        self.child_notebook.add(self.local_presets_tab, text="Local Presets")
        self.child_notebook.add(self.device_presets_tab, text="Device Presets")
        self.child_notebook.add(self.preset_editor_tab, text="Preset Editor")
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)

    def _on_child_tab_selected(self, event):
        print(f"Presets child tab selected.")
        selected_tab_id = self.child_notebook.select()
        if selected_tab_id:
            widget = self.child_notebook.nametowidget(selected_tab_id)
            if hasattr(widget, '_on_tab_selected'):
                widget._on_tab_selected(event)

    def _on_parent_tab_selected(self, event):
        print(f"Presets Parent tab selected.")
        selected_tab_id = self.child_notebook.select()
        if selected_tab_id:
            widget = self.child_notebook.nametowidget(selected_tab_id)
            if hasattr(widget, '_on_tab_selected'):
                widget._on_tab_selected(event)