# src/TABS_PARENT.py
#
# Version 20250821.224500.1 (Refactored to remove console_print_func dependency)

import tkinter as tk
from tkinter import ttk
from functools import partial
import inspect
import os
from datetime import datetime

from Instrument.TAB_INSTRUMENT_PARENT import TAB_INSTRUMENT_PARENT
from Markers.TAB_MARKERS_PARENT import TAB_MARKERS_PARENT
from Scanning.TAB_SCANNING_PARENT import TAB_SCANNING_PARENT
from Plotting.TAB_PLOTTING_PARENT import TAB_PLOTTING_PARENT
from Presets.TAB_PRESETS_PARENT import TAB_PRESETS_PARENT
from Experiments.TAB_EXPERIMENTS_PARENT import ExperimentsParentTab as TAB_EXPERIMENTS_PARENT

# --- Version Information ---
current_version = "20250821.224500.1"
current_file = os.path.basename(__file__)

class TABS_PARENT(ttk.Frame):
    # --- DEFINITIVE FIX: Removed 'console_print_func' from constructor ---
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app_instance = app_instance
        self.parent = parent
        self.active_tab_name = None
        
        self.configure(style='App.TFrame')
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tab_buttons = {}
        self.tab_content_frames = {}

        self._create_widgets()

    def _create_widgets(self):
        print(f"📘 🟢 Creating parent tab widgets.")
        button_frame = ttk.Frame(self, style='App.TFrame')
        button_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        tab_classes = {
            "Instruments": TAB_INSTRUMENT_PARENT, "Markers": TAB_MARKERS_PARENT, "Scanning": TAB_SCANNING_PARENT,
            "Plotting": TAB_PLOTTING_PARENT, "Presets": TAB_PRESETS_PARENT, "Experiments": TAB_EXPERIMENTS_PARENT
        }

        for i, (name, TabClass) in enumerate(tab_classes.items()):
            button = ttk.Button(button_frame, text=name, command=partial(self.switch_tab, name), style=f'{name}.Inactive.TButton')
            button.grid(row=0, column=i, sticky='ew', padx=2)
            button_frame.grid_columnconfigure(i, weight=1)
            self.tab_buttons[name] = button

            content_container = ttk.Frame(self, style='App.TFrame')
            content_container.grid(row=1, column=0, sticky='nsew')
            
            # Child tabs no longer receive console_print_func
            if name == "Experiments":
                content = TabClass(content_container, self.app_instance, self.app_instance.style_obj)
            else:
                content = TabClass(content_container, self.app_instance)

            content.pack(expand=True, fill='both')
            self.tab_content_frames[name] = content_container 

        self.after(100, lambda: self.switch_tab("Instruments"))
        print(f"📘 ✅ Parent tab widgets created.")

    def switch_tab(self, new_tab_name):
        if self.active_tab_name == new_tab_name: return
        print(f"📘 🔵 Switching to tab: {new_tab_name}")
        self.active_tab_name = new_tab_name

        for name, button in self.tab_buttons.items():
            content_frame = self.tab_content_frames[name]
            if name == new_tab_name:
                button.config(style=f'{name}.Active.TButton')
                content_frame.tkraise()
                new_tab_content = content_frame.winfo_children()[0]
                if hasattr(new_tab_content, '_on_parent_tab_selected'):
                    new_tab_content._on_parent_tab_selected(None)
            else:
                button.config(style=f'{name}.Inactive.TButton')