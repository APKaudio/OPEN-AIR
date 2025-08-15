# tabs/TABS_PARENT.py
#
# This is the description of what comes below
# This file defines the TABS_PARENT class, which serves as a master container for all the main
# functional tabs of the application (Instruments, Markers, etc.). This consolidates the
# tab-switching UI and logic into a single, clean component for the application's main left pane.
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
# Version 20250813.134000.2

import tkinter as tk
from tkinter import ttk
from functools import partial
import inspect
import os
from datetime import datetime

# Import logging
from display.console_logic import console_log
from display.debug_logic import debug_log

# --- Version Information ---
current_version = "20250813.134000.2"
current_version_hash = (int(current_version.split('.')[0]) * int(current_version.split('.')[1]) * int(current_version.split('.')[2]))


class TABS_PARENT(ttk.Frame):
    """
    A parent container for all the main functional tabs of the application.
    This consolidates the tab switching logic and UI into a single component for the left pane.
    """
    def __init__(self, parent, app_instance):
        # Function Description
        # Initializes the master tab container, creating the tab button bar and the content frame
        # that will hold all the main functional tabs like Instruments, Markers, etc.
        super().__init__(parent)
        self.app_instance = app_instance
        self.console_print_func = console_log

        # FIXED: Move imports inside __init__ to prevent circular dependency on startup.
        from tabs.Instrument.TAB_INSTRUMENT_PARENT import TAB_INSTRUMENT_PARENT
        from tabs.Markers.TAB_MARKERS_PARENT import TAB_MARKERS_PARENT
        from tabs.Presets.TAB_PRESETS_PARENT import TAB_PRESETS_PARENT
        from tabs.Scanning.TAB_SCANNING_PARENT import TAB_SCANNING_PARENT
        from tabs.Plotting.TAB_PLOTTING_PARENT import TAB_PLOTTING_PARENT
        from tabs.Experiments.TAB_EXPERIMENTS_PARENT import TAB_EXPERIMENTS_PARENT

        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                  file=f"{current_file} - {current_version}",
                  function=current_function)

        # --- Create the UI for this container ---
        tab_button_frame = ttk.Frame(self, style='TFrame')
        tab_button_frame.pack(side='top', fill='x', padx=5, pady=(5, 0))
        tab_button_frame.grid_columnconfigure(tuple(range(6)), weight=1)

        content_frame = ttk.Frame(self, style='TFrame')
        content_frame.pack(side='top', expand=True, fill='both', padx=5, pady=(0, 5))
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # --- Initialize Tab State ---
        self.tab_buttons = {}
        self.tab_content_frames = {}
        self.active_tab_name = None
        self.tab_art_map = self.app_instance.tab_art_map

        tab_definitions = {
            "Instruments": TAB_INSTRUMENT_PARENT,
            "Markers": TAB_MARKERS_PARENT,
            "Presets": TAB_PRESETS_PARENT,
            "Scanning": TAB_SCANNING_PARENT,
            "Plotting": TAB_PLOTTING_PARENT,
            "Experiments": TAB_EXPERIMENTS_PARENT
        }

        for i, (name, content_class) in enumerate(tab_definitions.items()):
            button = ttk.Button(
                tab_button_frame,
                text=name,
                style=f'{name}.Inactive.TButton',
                command=partial(self.switch_tab, name)
            )
            button.grid(row=0, column=i, sticky='ew')
            self.tab_buttons[name] = button

            content = content_class(content_frame, self.app_instance, self.console_print_func)
            content.grid(row=0, column=0, sticky='nsew')
            self.tab_content_frames[name] = content

        # Set initial tab
        self.after(10, lambda: self.switch_tab("Instruments"))

    def switch_tab(self, new_tab_name):
        # Function Description
        # Handles switching the visible tab content and updating button styles.
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name
        
        if self.active_tab_name == new_tab_name:
            return

        debug_log(f"Switching to tab: {new_tab_name}",
                  file=f"{current_file} - {current_version}",
                  function=current_function)

        for name, button in self.tab_buttons.items():
            content_frame = self.tab_content_frames[name]
            if name == new_tab_name:
                button.config(style=f'{name}.Active.TButton')
                content_frame.tkraise()
                
                if name in self.tab_art_map:
                    self.tab_art_map[name](self.console_print_func)

                if hasattr(content_frame, '_on_parent_tab_selected'):
                    content_frame._on_parent_tab_selected(None)
            else:
                button.config(style=f'{name}.Inactive.TButton')
        
        self.active_tab_name = new_tab_name
        self.app_instance.active_tab_name = new_tab_name