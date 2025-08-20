# tabs/Markers/showtime/controls/tab_markers_child_control_zone_zoom.py
#
# This file defines the Zone Zoom tab for the ControlsFrame.
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
# Version 20250821.171500.1
# REFACTORED: Updated to use the centralized `shared_state` object for its
#             `zone_zoom_buttons` and label `tk.StringVars`.
# NEW: Added a `_sync_ui_from_state` method to manage button styling based on
#      the current selection state in `self.shared_state`.
# FIXED: The `on_tab_selected` method now calls the new sync method to ensure
#        the UI state is always up to date.
# FIXED: Modified button commands to pass `self` (the ZoneZoomTab instance)
#        to the utility functions for direct UI updates.

import os
import inspect
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from display.debug_logic import debug_log
from .utils_showtime_zone_zoom import set_span_to_all_markers, set_span_to_device, set_span_to_group, set_span_to_zone

# --- Versioning ---
w = 20250821
x = 171500
y = 1
current_version = f"Version {w}.{x}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"

class ZoneZoomTab(ttk.Frame):
    def __init__(self, parent_notebook, showtime_tab_instance, shared_state):
        # [Initializes the Zone Zoom control tab.]
        super().__init__(parent_notebook)
        self.showtime_tab_instance = showtime_tab_instance
        self.shared_state = shared_state
        self._create_widgets()
        
    def _create_widgets(self):
        # [Creates the UI elements for the Zone Zoom tab.]
        button_frame = ttk.Frame(self, style='TFrame')
        button_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

        buttons_config = [
            ("Zone", lambda: set_span_to_zone(self.showtime_tab_instance, self)),
            ("Group", lambda: set_span_to_group(self.showtime_tab_instance, self)),
            ("Device", lambda: set_span_to_device(self.showtime_tab_instance, self)),
            ("All Markers", lambda: set_span_to_all_markers(self.showtime_tab_instance, self))
        ]

        self.shared_state.zone_zoom_buttons.clear()
        for i, (text, command) in enumerate(buttons_config):
            btn = ttk.Button(button_frame, text=text, style='ControlButton.TButton', command=command)
            btn.grid(row=0, column=i, sticky='ew', padx=2, pady=2)
            self.shared_state.zone_zoom_buttons[text.lower()] = btn
        button_frame.grid_columnconfigure(list(range(len(buttons_config))), weight=1)

        label_frame = ttk.Frame(self, style='TFrame')
        label_frame.pack(side='left', fill='x', expand=True)

        self.label_left = ttk.Label(label_frame, textvariable=self.shared_state.zone_zoom_label_left_var, style='TLabel')
        self.label_center = ttk.Label(label_frame, textvariable=self.shared_state.zone_zoom_label_center_var, style='TLabel')
        self.label_right = ttk.Label(label_frame, textvariable=self.shared_state.zone_zoom_label_right_var, style='TLabel')

        self.label_left.pack(side='left', padx=5)
        self.label_center.pack(side='left', padx=5)
        self.label_right.pack(side='left', padx=5)
        
    def _sync_ui_from_state(self):
        # [Updates button styles based on the current selection in shared state.]
        if self.shared_state.last_selected_type == 'zone':
            self.shared_state.zone_zoom_buttons['zone'].config(style='ControlButton.Active.TButton')
            self.shared_state.zone_zoom_buttons['group'].config(style='ControlButton.Inactive.TButton')
            self.shared_state.zone_zoom_buttons['device'].config(style='ControlButton.Inactive.TButton')
            self.shared_state.zone_zoom_buttons['all markers'].config(style='ControlButton.Inactive.TButton')
        elif self.shared_state.last_selected_type == 'group':
            self.shared_state.zone_zoom_buttons['zone'].config(style='ControlButton.Inactive.TButton')
            self.shared_state.zone_zoom_buttons['group'].config(style='ControlButton.Active.TButton')
            self.shared_state.zone_zoom_buttons['device'].config(style='ControlButton.Inactive.TButton')
            self.shared_state.zone_zoom_buttons['all markers'].config(style='ControlButton.Inactive.TButton')
        elif self.shared_state.last_selected_type == 'device':
            self.shared_state.zone_zoom_buttons['zone'].config(style='ControlButton.Inactive.TButton')
            self.shared_state.zone_zoom_buttons['group'].config(style='ControlButton.Inactive.TButton')
            self.shared_state.zone_zoom_buttons['device'].config(style='ControlButton.Active.TButton')
            self.shared_state.zone_zoom_buttons['all markers'].config(style='ControlButton.Inactive.TButton')
        else: # No selection
            for btn in self.shared_state.zone_zoom_buttons.values():
                btn.config(style='ControlButton.Inactive.TButton')
            
    def _on_tab_selected(self, event):
        # [Handles the event when this tab is selected.]
        self._sync_ui_from_state()
