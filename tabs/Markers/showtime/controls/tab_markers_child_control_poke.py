# tabs/Markers/showtime/controls/tab_markers_child_control_poke.py
#
# This file defines the Poke tab for the ControlsFrame.
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
# Version 20250820.114327.4
# REFACTORED: Updated to use the centralized `shared_state.poke_freq_var`.

import os
import inspect
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from display.debug_logic import debug_log
from .utils_showtime_poke import on_poke_action

# --- Versioning ---
w = int(datetime.now().strftime('%Y%m%d'))
x_str = datetime.now().strftime('%H%M%S')
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 4
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"

class PokeTab(ttk.Frame):
    def __init__(self, parent_notebook, showtime_tab_instance, shared_state):
        # [Initializes the Poke control tab.]
        super().__init__(parent_notebook)
        self.showtime_tab_instance = showtime_tab_instance
        self.shared_state = shared_state
        self._create_widgets()

    def _create_widgets(self):
        # [Creates the UI elements for the Poke tab.]
        self.poke_entry = ttk.Entry(self, textvariable=self.shared_state.poke_freq_var, style='TEntry')
        self.poke_button = ttk.Button(
            self, text="Poke", style='ControlButton.TButton',
            command=lambda: on_poke_action(self.showtime_tab_instance)
        )
        self.poke_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.poke_button.pack(side='left')