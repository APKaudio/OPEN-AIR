# tabs/Markers/showtime/controls/tab_markers_child_control_span.py
#
# This file defines the Span tab for the ControlsFrame. It contains the buttons
# for setting the instrument's span and the logic for handling those clicks.
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
# FIXED: The `on_span_button_click` call was updated to correctly reference `self.controls_frame.showtime_tab_instance`.
# REFACTORED: Removed local variables. Now uses shared state variables from the parent
#             `showtime_tab_instance`.

current_version = "20250821.012500.1"
current_version_hash = (20250821 * 12500 * 1)

import os
import inspect
import tkinter as tk
from tkinter import ttk

from display.debug_logic import debug_log
from display.console_logic import console_log

from ref.ref_scanner_setting_lists import (
    PRESET_FREQUENCY_SPAN,
)

from tabs.Markers.showtime.controls.utils_showtime_span import (
    on_span_button_click
)

from process_math.math_frequency_translation import format_hz

class SpanTab(ttk.Frame):
    def __init__(self, parent, controls_frame):
        # [Initializes the Span tab and its associated controls.]
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        super().__init__(parent, style='TFrame', padding=5)
        self.controls_frame = controls_frame
        self._create_widgets()
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def _create_widgets(self):
        # [Creates and lays out the span control buttons.]
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        
        showtime_tab = self.controls_frame.showtime_tab_instance
        
        for i, span_preset in enumerate(PRESET_FREQUENCY_SPAN):
            btn_text = f"{span_preset['label']}\n({format_hz(span_preset['value'])})"
            btn = ttk.Button(self, text=btn_text, style='ControlButton.Inactive.TButton',
                             command=lambda value=span_preset['value']: on_span_button_click(self.controls_frame.showtime_tab_instance, value))
            btn.grid(row=0, column=i, padx=2, pady=2, sticky="ew")
            
            # Store button reference in parent's dictionary
            showtime_tab.span_buttons[str(span_preset['value'])] = btn
        
        for i in range(len(PRESET_FREQUENCY_SPAN)):
            self.grid_columnconfigure(i, weight=1)

        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def set_span(self, new_span_value):
        # [Sets the internal span variable and updates the UI.]
        debug_log(f"Entering set_span with new value: {new_span_value}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span")
        self.controls_frame.showtime_tab_instance.span_var.set(value=new_span_value)
        self.controls_frame._update_control_styles()
        debug_log(f"Exiting set_span. Span is now: {self.controls_frame.showtime_tab_instance.span_var.get()}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span")

    def get_current_span(self):
        # [Returns the current value of the span variable.]
        debug_log(f"Entering get_current_span", file=f"{os.path.basename(__file__)}", version=current_version, function="get_current_span")
        return self.controls_frame.showtime_tab_instance.span_var.get()

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
        # [Updates the appearance of the buttons based on the current span setting.]
        debug_log(f"Entering _sync_ui_from_app_state", file=f"{os.path.basename(__file__)}", version=current_version, function="_sync_ui_from_app_state")
        showtime_tab = self.controls_frame.showtime_tab_instance
        current_span = showtime_tab.span_var.get()
        active_style = 'ControlButton.Active.TButton'
        inactive_style = 'ControlButton.Inactive.TButton'

        for value_str, btn in showtime_tab.span_buttons.items():
            if value_str == current_span and not showtime_tab.follow_zone_span_var.get():
                btn.config(style=active_style)
            else:
                btn.config(style=inactive_style)
        debug_log(f"Exiting _sync_ui_from_app_state", file=f"{os.path.basename(__file__)}", version=current_version, function="_sync_ui_from_app_state")