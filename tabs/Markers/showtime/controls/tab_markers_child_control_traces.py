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
# Build Log: [https://like.audio/category/software/spectrum-scanner/](https://like.audio/category/software/spectrum-scanner/)
# Source Code: [https://github.com/APKaudio/](https://github.com/APKaudio/)
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250824.001000.1
# REFACTORED: Removed dependency on `shared_state` object. State is now accessed from the `showtime_tab_instance`.

import os
import inspect
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from display.debug_logic import debug_log
# FIXED: Defer import to avoid circular dependency
# from .utils_showtime_trace import execute_trace_action

# --- Versioning ---
w = 20250824
x = 1000
y = 1
current_version = f"Version {w}.{x}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"

class TracesTab(ttk.Frame):
    def __init__(self, parent_notebook, showtime_tab_instance):
        # [Initializes the Traces control tab.]
        debug_log(f"🖥️ 🟢 Entering __init__",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        
        super().__init__(parent_notebook)
        self.showtime_tab_instance = showtime_tab_instance
        self._create_widgets()
        
        debug_log(f"🖥️ 🟢 Exiting __init__",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

    def _create_widgets(self):
        # FIXED: Move import here to resolve circular import.
        from .utils_showtime_trace import execute_trace_action

        # [Creates the UI elements for the Traces tab.]
        debug_log(f"🖥️ 🟢 Creating widgets for TracesTab.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        
        self.showtime_tab_instance.trace_buttons.clear()
        
        # UPDATED: Added the "Min" button to the configuration list
        buttons_config = [
            ("All", lambda: self._toggle_and_execute('all')),
            ("Live", lambda: self._toggle_and_execute('live')),
            ("Max", lambda: self._toggle_and_execute('max')),
            ("Min", lambda: self._toggle_and_execute('min'))
        ]

        for i, (text, command) in enumerate(buttons_config):
            # FIXED: Added a fixed width to ensure all buttons are the same size.
            btn = ttk.Button(self, text=text, style='ControlButton.TButton', command=command, width=12)
            btn.grid(row=0, column=i, sticky='ew', padx=2, pady=2)
            self.showtime_tab_instance.trace_buttons[text.lower()] = btn

        self.grid_columnconfigure(list(range(len(buttons_config))), weight=1)
        self._update_button_styles()
        
        debug_log(f"🖥️ ✅ Widgets created successfully.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

    def _toggle_and_execute(self, button_type):
        # [Toggles the state of a trace mode and executes the trace action.]
        debug_log(f"🖥️ 🟢 Entering _toggle_and_execute for button: {button_type}",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        
        from .utils_showtime_trace import execute_trace_action

        target_var = self.showtime_tab_instance.trace_modes.get(button_type)
        if not target_var: return

        # NEW LOGIC: This implements a true exclusive selection
        current_state = target_var.get()
        if not current_state: # Only proceed if the button is not already active
            for mode, var in self.showtime_tab_instance.trace_modes.items():
                if mode == button_type:
                    var.set(True) # Set the clicked button to active
                    debug_log(f"🖥️ 📝 Setting shared state trace mode '{mode}' to active.",
                                file=current_file,
                                version=current_version,
                                function=inspect.currentframe().f_code.co_name)
                else:
                    var.set(False) # Set all other buttons to inactive
                    debug_log(f"🖥️ 📝 Setting shared state trace mode '{mode}' to inactive.",
                                file=current_file,
                                version=current_version,
                                function=inspect.currentframe().f_code.co_name)
            
            self._update_button_styles()
            execute_trace_action(traces_tab_instance=self, action_type=button_type)
        
        # If the button is already active, do nothing.
        debug_log(f"🖥️ 🟢 Exiting _toggle_and_execute",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)


    def _update_button_styles(self):
        # [Updates button styles based on the state of trace mode variables.]
        debug_log(f"🖥️ 🟢 Entering _update_button_styles",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        
        for mode, var in self.showtime_tab_instance.trace_modes.items():
            button = self.showtime_tab_instance.trace_buttons.get(mode)
            if button:
                style = 'ControlButton.Active.TButton' if var.get() else 'ControlButton.Inactive.TButton'
                button.config(style=style)
                
        debug_log(f"🖥️ ✅ Button styles updated successfully.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
