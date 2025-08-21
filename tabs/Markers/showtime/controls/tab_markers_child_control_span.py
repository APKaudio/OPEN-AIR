# tabs/Markers/showtime/controls/tab_markers_child_control_span.py
#
# This file defines the Span tab for the ControlsFrame.
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
# Version 20250823.003000.1
# UPDATED: File header and versioning adhere to new standards.
# UPDATED: The span buttons are now correctly linked to the shared state.
# FIXED: The span button click now saves the config after a successful operation.

import os
import inspect
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from display.debug_logic import debug_log
from ref.ref_scanner_setting_lists import PRESET_FREQUENCY_SPAN
from .utils_showtime_span import on_span_button_click

# --- Versioning ---
w = 20250823
x = 3000
y = 1
current_version = f"Version {w}.{x}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"

# --- Constants for formatting ---
MHZ_TO_HZ = 1_000_000

class SpanTab(ttk.Frame):
    def __init__(self, parent_notebook, showtime_tab_instance, shared_state):
        # [Initializes the Span control tab.]
        debug_log(f"🖥️ 🟢 Entering __init__",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        
        super().__init__(parent_notebook)
        self.showtime_tab_instance = showtime_tab_instance
        self.shared_state = shared_state
        self._create_widgets()
        
        debug_log(f"🖥️ 🟢 Exiting __init__",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        
    def _create_widgets(self):
        # [Creates the UI elements for the Span tab.]
        debug_log(f"🖥️ 🟢 Creating widgets for SpanTab.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        
        self.shared_state.span_buttons.clear()

        for i, span_data in enumerate(PRESET_FREQUENCY_SPAN):
            label = span_data.get("label", "N/A")
            value = span_data.get("value", 0)
            
            # Format the button text to show the label and the value in MHz
            button_text = f"{label}\n{value / MHZ_TO_HZ:.3f} MHz"

            btn = ttk.Button(
                self, text=button_text, style='ControlButton.TButton',
                command=lambda v=value: on_span_button_click(self.showtime_tab_instance, v)
            )
            btn.grid(row=0, column=i, sticky='ew', padx=2, pady=2)
            self.shared_state.span_buttons[str(value)] = btn

        self.grid_columnconfigure(list(range(len(PRESET_FREQUENCY_SPAN))), weight=1)

        debug_log(f"🖥️ ✅ Widgets created successfully.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
