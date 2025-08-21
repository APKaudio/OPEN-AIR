# tabs/Markers/showtime/controls/tab_markers_parent_bottom_controls.py
#
# This file defines the ControlsFrame, which contains a notebook of child tabs
# for controlling various instrument settings related to markers.
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
# Version 20250823.235500.2
# REFACTORED: The ControlsFrame now instantiates its child tabs without the
#             `shared_state` parameter, resolving the `TypeError`.

import tkinter as tk
from tkinter import ttk
import inspect
import os
from datetime import datetime

from display.debug_logic import debug_log
from display.console_logic import console_log
from src.program_style import COLOR_PALETTE, COLOR_PALETTE_TABS, _get_dark_color

# Import the child tab classes
from .tab_markers_child_control_span import SpanTab
from .tab_markers_child_control_rbw import RBWTab
from .tab_markers_child_control_traces import TracesTab
from .tab_markers_child_control_poke import PokeTab
from .tab_markers_child_control_zone_zoom import ZoneZoomTab

# --- Versioning ---
w = 20250823
x_str = '235500'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 2
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"


class ControlsFrame(ttk.LabelFrame):
    def __init__(self, parent_frame, showtime_tab_instance, *args, **kwargs):
        # [Initializes the controls frame, setting up the notebook and tabs.]
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"🖥️ 🟢 Entering __init__",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        super().__init__(parent_frame, text="Controls", style='TLabelframe', **kwargs)
        self.showtime_tab_instance = showtime_tab_instance
        self._create_widgets()
        
        debug_log(f"🖥️ 🟢 Exiting __init__",
                    file=current_file,
                    version=current_version,
                    function=current_function)
    
    def _create_widgets(self):
        # [Creates the notebook and adds all the control tabs to it.]
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"🖥️ 🟢 Creating widgets for ControlsFrame. Building a new control panel! 🛠️",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        
        # --- NEW: Apply custom styling for the control notebook tabs ---
        style = ttk.Style(self)
        active_color = COLOR_PALETTE_TABS['Markers']['active']
        inactive_color = _get_dark_color(active_color)
        
        style.configure('Controls.TNotebook', background=COLOR_PALETTE['background'])
        style.map('Controls.TNotebook.Tab',
                background=[('selected', active_color),
                            ('!selected', inactive_color)],
                foreground=[('selected', COLOR_PALETTE_TABS['Markers']['fg']),
                            ('!selected', 'white')])

        self.child_notebook = ttk.Notebook(self, style='Controls.TNotebook')
        self.child_notebook.pack(expand=True, fill="both")
        
        # Pass the parent instance to all child tabs so they can access the state
        self.span_tab = SpanTab(self.child_notebook, self.showtime_tab_instance)
        self.child_notebook.add(self.span_tab, text="Span")
        
        self.rbw_tab = RBWTab(self.child_notebook, self.showtime_tab_instance)
        self.child_notebook.add(self.rbw_tab, text="RBW")
        
        self.traces_tab = TracesTab(self.child_notebook, self.showtime_tab_instance)
        self.child_notebook.add(self.traces_tab, text="Traces")
        
        self.poke_tab = PokeTab(self.child_notebook, self.showtime_tab_instance)
        self.child_notebook.add(self.poke_tab, text="Poke")
        
        self.zone_zoom_tab = ZoneZoomTab(self.child_notebook, self.showtime_tab_instance)
        self.child_notebook.add(self.zone_zoom_tab, text="Zone Zoom")
        
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_tab_selected)

        debug_log(f"🖥️ ✅ Widgets created successfully. Child tabs are now present. 🗂️",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        
    def _on_tab_selected(self, event):
        # [Handles the event when a tab is selected in the notebook.]
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"🖥️ 🟢 Entering {current_function}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)

        debug_log(f"🖥️ 🟢 Exiting {current_function}",
                    file=current_file,
                    version=current_version,
                    function=current_function)
    
    def switch_to_tab(self, tab_name):
        # [Switches the currently displayed tab in the notebook.]
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"🖥️ 🟢 Entering {current_function} with argument: {tab_name}",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        
        try:
            tab_id = -1
            # Iterate through all tabs to find the one with the matching name
            for i, name in enumerate(self.child_notebook.tabs()):
                if self.child_notebook.tab(name, 'text') == tab_name:
                    tab_id = i
                    break
            
            if tab_id != -1:
                self.child_notebook.select(tab_id)
                debug_log(f"🖥️ ✅ Switched to tab: {tab_name}",
                            file=current_file,
                            version=current_version,
                            function=current_function)
            else:
                debug_log(f"🖥️ ❌ Error switching to tab '{tab_name}': Tab not found.",
                            file=current_file,
                            version=current_version,
                            function=current_function)

        except Exception as e:
            debug_log(f"🖥️ ❌ Error switching to tab '{tab_name}': {e}",
                        file=current_file,
                        version=current_version,
                        function=current_function)

        debug_log(f"🖥️ 🟢 Exiting {current_function}",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        
    def _update_control_buttons(self):
        # This function updates the state and style of all control buttons.
        # It's called when a variable changes to ensure the UI is in sync.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"🖥️ 🔄 Updating control button styles.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        try:
            # Span buttons
            current_span_hz = self.showtime_tab_instance.span_var.get()
            for value_str, btn in self.showtime_tab_instance.span_buttons.items():
                if value_str == current_span_hz:
                    btn.config(style='ControlButton.Active.TButton')
                else:
                    btn.config(style='ControlButton.Inactive.TButton')
                    
            # RBW buttons
            current_rbw_hz = self.showtime_tab_instance.rbw_var.get()
            for value_str, btn in self.showtime_tab_instance.rbw_buttons.items():
                if value_str == current_rbw_hz:
                    btn.config(style='ControlButton.Active.TButton')
                else:
                    btn.config(style='ControlButton.Inactive.TButton')
            
            # Trace buttons
            for mode_name, mode_var in self.showtime_tab_instance.trace_modes.items():
                button = self.showtime_tab_instance.trace_buttons.get(mode_name)
                if button:
                    if mode_var.get():
                        button.config(style='ControlButton.Active.TButton')
                    else:
                        button.config(style='ControlButton.Inactive.TButton')

            debug_log(f"🖥️ ✅ Control button styles updated successfully.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        except Exception as e:
            debug_log(f"🖥️ ❌ Error updating control buttons: {e}",
                        file=current_file,
                        version=current_version,
                        function=current_function)

