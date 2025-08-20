# tabs/Markers/showtime/controls/tab_markers_child_control_rbw.py
#
# This file defines the RBW tab for the ControlsFrame. It contains the buttons
# for setting the instrument's resolution bandwidth and the logic for handling
# those clicks.
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
# Version 20250821.013000.1
# FIXED: The `ImportError` was fixed by correctly importing `PRESET_BANDWIDTH_RBW`
#        from `ref.ref_scanner_setting_lists`.
# REFACTORED: Removed local variables. Now uses shared state variables from the parent
#             `showtime_tab_instance`.

current_version = "20250821.013000.1"
current_version_hash = (20250821 * 13000 * 1)

import os
import inspect
import tkinter as tk
from tkinter import ttk

from display.debug_logic import debug_log
from display.console_logic import console_log

from ref.ref_scanner_setting_lists import (
    PRESET_BANDWIDTH_RBW
)

from tabs.Markers.showtime.controls.utils_showtime_rbw import on_rbw_button_click
from process_math.math_frequency_translation import format_hz

class RBWTab(ttk.Frame):
    def __init__(self, parent, controls_frame):
        # [Initializes the RBW tab and its associated controls.]
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        super().__init__(parent, style='TFrame', padding=5)
        self.controls_frame = controls_frame
        
        # The variables are now held by the parent ShowtimeTab instance
        # self.rbw_buttons = {}
        # self.rbw_var = tk.StringVar(value="100000")

        self._create_widgets()
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def _create_widgets(self):
        # [Creates and lays out the RBW control buttons.]
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        
        showtime_tab = self.controls_frame.showtime_tab_instance

        for i, rbw_preset in enumerate(PRESET_BANDWIDTH_RBW):
            btn_text = f"{rbw_preset['label']}\n({format_hz(rbw_preset['value'])})"
            btn = ttk.Button(self, text=btn_text, style='ControlButton.Inactive.TButton',
                             command=lambda value=rbw_preset['value']: on_rbw_button_click(self.controls_frame.showtime_tab_instance, value))
            btn.grid(row=0, column=i, padx=2, pady=2, sticky="ew")
            
            # Store button reference in parent's dictionary
            showtime_tab.rbw_buttons[str(rbw_preset['value'])] = btn
        
        for i in range(len(PRESET_BANDWIDTH_RBW)):
            self.grid_columnconfigure(i, weight=1)

        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def set_rbw(self, new_rbw_value):
        # [Sets the internal RBW variable and updates the UI.]
        debug_log(f"Entering set_rbw with new value: {new_rbw_value}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_rbw")
        self.controls_frame.showtime_tab_instance.rbw_var.set(value=new_rbw_value)
        self.controls_frame._update_control_styles()
        debug_log(f"Exiting set_rbw. RBW is now: {self.controls_frame.showtime_tab_instance.rbw_var.get()}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_rbw")

    def get_current_rbw(self):
        # [Returns the current value of the RBW variable.]
        debug_log(f"Entering get_current_rbw", file=f"{os.path.basename(__file__)}", version=current_version, function="get_current_rbw")
        return self.controls_frame.showtime_tab_instance.rbw_var.get()

    def _on_tab_selected(self):
        # [Synchronizes the UI elements when the tab is selected.]
        debug_log(f"Entering _on_tab_selected", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_tab_selected")
        self._sync_ui_from_app_state()
        debug_log(f"Exiting _on_tab_selected", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_tab_selected")

    def _on_tab_deselected(self):
        # [Performs any necessary cleanup when the tab is deselected.]
        debug_log(f"Entering _on_tab_deselected", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_tab_deselected")
        # No action required at this time
        pass
        debug_log(f"Exiting _on_tab_deselected", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_tab_deselected")
    
    def _sync_ui_from_app_state(self):
        # [Updates the appearance of the buttons based on the current RBW setting.]
        debug_log(f"Entering _sync_ui_from_app_state", file=f"{os.path.basename(__file__)}", version=current_version, function="_sync_ui_from_app_state")
        showtime_tab = self.controls_frame.showtime_tab_instance
        current_rbw = showtime_tab.rbw_var.get()
        active_style = 'ControlButton.Active.TButton'
        inactive_style = 'ControlButton.Inactive.TButton'

        for value_str, btn in showtime_tab.rbw_buttons.items():
            if value_str == current_rbw:
                btn.config(style=active_style)
            else:
                btn.config(style=inactive_style)
        debug_log(f"Exiting _sync_ui_from_app_state", file=f"{os.path.basename(__file__)}", version=current_version, function="_sync_ui_from_app_state")