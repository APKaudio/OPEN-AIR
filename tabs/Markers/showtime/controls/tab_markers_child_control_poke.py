# # tabs/Markers/showtime/controls/tab_markers_child_control_poke.py
#
# This file defines the Poke tab for the ControlsFrame. It contains the UI
# for manually poking the instrument to a specific frequency.
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
# Version 20250821.012500.1
# REFACTORED: `_create_widgets` now passes the `showtime_tab_instance` directly to the
#             `on_poke_action` utility function, ensuring the correct object is used.

current_version = "20250821.012500.1"
current_version_hash = (20250821 * 12500 * 1)

import os
import inspect
import tkinter as tk
from tkinter import ttk

from display.debug_logic import debug_log
from display.console_logic import console_log

from tabs.Markers.showtime.controls.utils_showtime_poke import (
    on_poke_action
)

class PokeTab(ttk.Frame):
    def __init__(self, parent, controls_frame):
        # [Initializes the Poke tab and its associated controls.]
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        super().__init__(parent, style='TFrame', padding=5)
        self.controls_frame = controls_frame
        self._create_widgets()
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def _create_widgets(self):
        # [Creates and lays out the Poke control widgets.]
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        
        showtime_tab = self.controls_frame.showtime_tab_instance
        self.grid_columnconfigure(0, weight=1)
        
        poke_entry = ttk.Entry(self, textvariable=showtime_tab.poke_freq_var)
        poke_entry.pack(side='left', fill='x', expand=True, padx=2, pady=2)
        
        poke_btn = ttk.Button(self, text="Poke", style='ControlButton.Inactive.TButton',
                              command=lambda: on_poke_action(self.controls_frame.showtime_tab_instance))
        poke_btn.pack(side='left', padx=2, pady=2)
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def set_poke_freq(self, new_freq_value):
        # [Sets the internal poke frequency variable.]
        debug_log(f"Entering set_poke_freq with new value: {new_freq_value}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_poke_freq")
        self.controls_frame.showtime_tab_instance.poke_freq_var.set(value=new_freq_value)
        debug_log(f"Exiting set_poke_freq. Poke frequency is now: {self.controls_frame.showtime_tab_instance.poke_freq_var.get()}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_poke_freq")

    def get_current_poke_freq(self):
        # [Returns the current value of the poke frequency variable.]
        debug_log(f"Entering get_current_poke_freq", file=f"{os.path.basename(__file__)}", version=current_version, function="get_current_poke_freq")
        return self.controls_frame.showtime_tab_instance.poke_freq_var.get()

    def _on_tab_selected(self):
        # [Synchronizes the UI elements when the tab is selected.]
        debug_log(f"Entering _on_tab_selected", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_tab_selected")
        # No action required at this time
        pass
        debug_log(f"Exiting _on_tab_selected", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_tab_selected")

    def _on_tab_deselected(self):
        # [Performs any necessary cleanup when the tab is deselected.]
        debug_log(f"Entering _on_tab_deselected", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_tab_deselected")
        # No action required at this time
        pass
        debug_log(f"Exiting _on_tab_deselected", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_tab_deselected")