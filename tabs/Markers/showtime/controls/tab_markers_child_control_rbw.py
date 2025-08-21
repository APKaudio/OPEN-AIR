# tabs/Markers/showtime/controls/tab_markers_child_control_rbw.py
#
# Author: Anthony Peter Kuzub
# ... (Full header included)
#
# Version 20250822.093400.1
# FIXED: The button command lambda now correctly passes `self.showtime_tab_instance`
#        to the utility function, resolving the subsequent AttributeError.
# FIXED: Corrected circular import by moving the problematic import inside the method.
# FIXED: Updated versioning to adhere to project standards.
# FIXED: Modified the buttons to display the frequency value on a second line,
#        using Hz, kHz, or MHz for readability.
# UPDATED: All debug messages now include the correct emoji prefixes.

import tkinter as tk
import os
from tkinter import ttk
# Moved import inside method to fix circular import error
# from .utils_showtime_rbw import on_rbw_button_click
from ref.ref_scanner_setting_lists import PRESET_BANDWIDTH_RBW
from display.debug_logic import debug_log
from display.console_logic import console_log
import inspect
from datetime import datetime

# --- Versioning ---
w = 20250822
x = 93400
y = 1
current_version = f"Version {w}.{x}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"

# --- Constants for formatting ---
KHZ_TO_HZ = 1_000
MHZ_TO_HZ = 1_000_000

class RBWTab(ttk.Frame):
    def __init__(self, parent_notebook, showtime_tab_instance, shared_state):
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
        # FIXED: Moved import here to resolve circular import.
        from .utils_showtime_rbw import on_rbw_button_click

        debug_log(f"🖥️ 🟢 Creating widgets for RBWTab.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        
        self.shared_state.rbw_buttons.clear()
        for i, rbw_data in enumerate(PRESET_BANDWIDTH_RBW):
            label = rbw_data.get("label", "N/A")
            value = rbw_data.get("value", 0)

            # Format the button text to show the label and the value
            if value >= MHZ_TO_HZ:
                value_text = f"{value / MHZ_TO_HZ:.3f} MHz"
            elif value >= KHZ_TO_HZ:
                value_text = f"{value / KHZ_TO_HZ:.0f} kHz"
            else:
                value_text = f"{value} Hz"
                
            button_text = f"{label}\n{value_text}"

            btn = ttk.Button(
                self, text=button_text, style='ControlButton.TButton',
                # FIXED: Pass the main showtime_tab_instance, not self
                command=lambda v=value: on_rbw_button_click(self.showtime_tab_instance, v)
            )
            btn.grid(row=0, column=i, sticky='ew', padx=2, pady=2)
            self.shared_state.rbw_buttons[str(value)] = btn
        self.grid_columnconfigure(list(range(len(PRESET_BANDWIDTH_RBW))), weight=1)
        
        debug_log(f"🖥️ ✅ Widgets created successfully.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)