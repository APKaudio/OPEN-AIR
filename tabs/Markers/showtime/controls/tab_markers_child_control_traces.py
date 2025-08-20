# tabs/Markers/showtime/controls/tab_markers_child_control_traces.py
#
# This file defines the Trace tab for the ControlsFrame.
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
# Version 20250821.120300.1
# REFACTORED: All state management (trace_buttons, trace_modes, toggle variables)
#             now correctly references the centralized `shared_state` object.
# FIXED: The button command lambda now correctly passes `self.showtime_tab_instance`
#        to the utility function, resolving the subsequent AttributeError.
# FIXED: Corrected circular import by moving the problematic import inside the method.
# FIXED: Updated versioning to adhere to project standards.
# FIXED: Corrected the call to `execute_trace_action` to correctly reference the imported function.

import os
import inspect
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from display.debug_logic import debug_log
# FIXED: Defer import to avoid circular dependency
# from .utils_showtime_trace import execute_trace_action

# --- Versioning ---
w = 20250821
x = 120300
y = 1
current_version = f"Version {w}.{x}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"

class TracesTab(ttk.Frame):
    def __init__(self, parent_notebook, showtime_tab_instance, shared_state):
        # [Initializes the Traces control tab.]
        super().__init__(parent_notebook)
        self.showtime_tab_instance = showtime_tab_instance
        self.shared_state = shared_state
        self._create_widgets()

    def _create_widgets(self):
        # FIXED: Move import here to resolve circular import.
        from .utils_showtime_trace import execute_trace_action

        # [Creates the UI elements for the Traces tab.]
        self.shared_state.trace_buttons.clear()

        buttons_config = [
            ("All", lambda: self._toggle_and_execute('all')),
            ("Live", lambda: self._toggle_and_execute('live')),
            ("Max", lambda: self._toggle_and_execute('max'))
        ]

        for i, (text, command) in enumerate(buttons_config):
            btn = ttk.Button(self, text=text, style='ControlButton.TButton', command=command)
            btn.grid(row=0, column=i, sticky='ew', padx=2, pady=2)
            self.shared_state.trace_buttons[text.lower()] = btn

        self.grid_columnconfigure(list(range(len(buttons_config))), weight=1)
        self._update_button_styles()

    def _toggle_and_execute(self, button_type):
        # [Toggles the state of a trace mode and executes the trace action.]
        from .utils_showtime_trace import execute_trace_action

        target_var = self.shared_state.trace_modes.get(button_type)
        if not target_var: return

        # Exclusive toggle logic
        current_state = target_var.get()
        for mode, var in self.shared_state.trace_modes.items():
            var.set(False)
        target_var.set(not current_state)

        self._update_button_styles()
        execute_trace_action(traces_tab_instance=self, action_type=button_type)

    def _update_button_styles(self):
        # [Updates button styles based on the state of trace mode variables.]
        for mode, var in self.shared_state.trace_modes.items():
            button = self.shared_state.trace_buttons.get(mode)
            if button:
                style = 'ControlButton.Active.TButton' if var.get() else 'ControlButton.Inactive.TButton'
                button.config(style=style)