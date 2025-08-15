# tabs/Instrument/tab_instrument_child_settings.py
#
# This file defines the SettingsParentTab, which now serves as a container
# for all instrument-related child tabs, refactored from the original SettingsTab.
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
# Version 20250815.105500.1
# REVERTED: Reverted to a static tabbed layout only, as dynamic resizing was causing TclErrors.
# FIX: The red styling for the nested tabs was corrected to use the right color palette.

current_version = "20250815.105500.1"
current_version_hash = 20250815 * 105500 * 1

import tkinter as tk
from tkinter import ttk
import inspect
import os

from display.debug_logic import debug_log
from display.console_logic import console_log
from src.program_style import COLOR_PALETTE, COLOR_PALETTE_TABS

# Import the new child tabs
from tabs.Instrument.tab_instrument_child_settings_frequency import FrequencySettingsTab
from tabs.Instrument.tab_instrument_child_settings_amplitude import AmplitudeSettingsTab
from tabs.Instrument.tab_instrument_child_settings_traces import TraceSettingsTab
from tabs.Instrument.tab_instrument_child_settings_markers import MarkerSettingsTab
from tabs.Instrument.tab_instrument_child_settings_bandwidth import BandwidthSettingsTab

class SettingsParentTab(ttk.Frame):
    """
    A Tkinter Frame that serves as a container for all instrument settings child tabs.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log

        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing SettingsParentTab. Version: {current_version}. Setting up settings tabs! 📁",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        style = ttk.Style(self)
        active_color = COLOR_PALETTE_TABS['Instruments']['active']
        inactive_color = style.lookup('Instruments.Child.TNotebook.Tab', 'background', default='#2b2b2b')
        
        style.configure('Red.TNotebook', background=COLOR_PALETTE['background'])
        style.map('Red.TNotebook.Tab',
                  background=[('selected', active_color),
                              ('!selected', inactive_color)],
                  foreground=[('selected', COLOR_PALETTE_TABS['Instruments']['fg']),
                              ('!selected', 'white')])

        self.child_notebook = ttk.Notebook(self, style='Red.TNotebook')
        self.child_notebook.pack(expand=True, fill="both", padx=5, pady=5)

        self.frequency_tab = FrequencySettingsTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.amplitude_tab = AmplitudeSettingsTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.bandwidth_tab = BandwidthSettingsTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.traces_tab = TraceSettingsTab(self.child_notebook, self.app_instance, self.console_print_func)
        self.markers_tab = MarkerSettingsTab(self.child_notebook, self.app_instance, self.console_print_func)

        self.child_notebook.add(self.frequency_tab, text="Frequency")
        self.child_notebook.add(self.amplitude_tab, text="Amplitude")
        self.child_notebook.add(self.bandwidth_tab, text="Bandwidth")
        self.child_notebook.add(self.traces_tab, text="Traces")
        self.child_notebook.add(self.markers_tab, text="Markers")

        debug_log(f"SettingsParentTab initialized with child tabs. The grand design is taking shape! 🏰",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

    def _on_tab_selected(self, event=None):
        """
        Handles when this parent tab is selected. It will delegate the call to the currently active child tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Settings Parent Tab selected. Delegating to child tab. ➡️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)