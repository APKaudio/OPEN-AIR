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
# Version 20250822.093400.1
# REFACTORED: All state management (trace_buttons, trace_modes, toggle variables)
#             now correctly references the centralized `shared_state` object.
# FIXED: The button command lambda now correctly passes `self.showtime_tab_instance`
#        to the utility function, resolving the subsequent AttributeError.
# FIXED: Corrected circular import by moving the problematic import inside the method.
# FIXED: Updated versioning to adhere to project standards.
# FIXED: Corrected the call to `execute_trace_action` to correctly reference the imported function.
# FIXED: Rebuilt the logic in _toggle_and_execute to be a true exclusive selection,
#        resolving the bug where a button could be toggled off or multiple buttons
#        could be active at once.
# NEW: Added a 'Min' button to the trace selection options.
# FIXED: Added `width=12` to all buttons to force them to be of equal size.
# UPDATED: All debug messages now include the correct emoji prefixes.

import os
import inspect
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from display.debug_logic import debug_log
# FIXED: Defer import to avoid circular dependency
# from .utils_showtime_trace import execute_trace_action

# --- Versioning ---
w = 20250822
x = 93400
y = 1
current_version = f"Version {w}.{x}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"

class TracesTab(ttk.Frame):
    def __init__(self, parent_notebook, showtime_tab_instance, shared_state):
        # [Initializes the Traces control tab.]
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
        # FIXED: Move import here to resolve circular import.
        from .utils_showtime_trace import execute_trace_action

        # [Creates the UI elements for the Traces tab.]
        debug_log(f"🖥️ 🟢 Creating widgets for TracesTab.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        
        self.shared_state.trace_buttons.clear()
        
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
            self.shared_state.trace_buttons[text.lower()] = btn

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

        target_var = self.shared_state.trace_modes.get(button_type)
        if not target_var: return

        # NEW LOGIC: This implements a true exclusive selection
        current_state = target_var.get()
        if not current_state: # Only proceed if the button is not already active
            for mode, var in self.shared_state.trace_modes.items():
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
        
        for mode, var in self.shared_state.trace_modes.items():
            button = self.shared_state.trace_buttons.get(mode)
            if button:
                style = 'ControlButton.Active.TButton' if var.get() else 'ControlButton.Inactive.TButton'
                button.config(style=style)
                
        debug_log(f"🖥️ ✅ Button styles updated successfully.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)