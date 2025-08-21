# tabs/Markers/showtime/controls/tab_markers_parent_bottom_controls.py
#
# This file defines the ControlsFrame, a ttk.Frame containing the
# Span, RBW, Trace Modes, and other controls in a notebook.
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
# Version 20250822.103000.2
# REFACTORED: Updated __init__ signature and child tab instantiation to correctly
#             pass the showtime_tab_instance and the shared_state object.
# FIXED: Corrected circular import by moving child tab imports inside the method.
# FIXED: Added a new method to handle updating control button styles from other modules.
# FIXED: Corrected versioning to adhere to project standards.
# UPDATED: All debug messages now include the correct emoji prefixes.
# FIXED: The initial styles are now applied to the buttons immediately after widget creation.
# NEW: Added a public method `switch_to_tab` to programmatically change the active tab.

import tkinter as tk
from tkinter import ttk
import os
import inspect
from datetime import datetime
from display.debug_logic import debug_log
from src.program_style import COLOR_PALETTE, COLOR_PALETTE_TABS, _get_dark_color

# --- Versioning ---
w = 20250822
x_str = '103000'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 2
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"

class ControlsFrame(ttk.Frame):
    def __init__(self, parent_frame, showtime_tab_instance, shared_state):
        # [Initializes the main controls frame with its notebook of control tabs.]
        debug_log(f"🖥️ 🟢 Entering __init__",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        
        super().__init__(parent_frame)
        self.showtime_tab_instance = showtime_tab_instance
        self.shared_state = shared_state
        self.controls_notebook = None
        self._create_widgets()
        # FIXED: Call the style update method here after the widgets are created.
        self._update_control_styles()
        
        debug_log(f"🖥️ 🟢 Exiting __init__",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

    def _create_widgets(self):
        # FIXED: Move all child tab imports here to resolve circular dependency.
        from .tab_markers_child_control_span import SpanTab
        from .tab_markers_child_control_rbw import RBWTab
        from .tab_markers_child_control_poke import PokeTab
        from .tab_markers_child_control_traces import TracesTab
        from .tab_markers_child_control_zone_zoom import ZoneZoomTab
        
        debug_log(f"🖥️ 🟢 Creating widgets for ControlsFrame.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

        # --- NEW: Apply custom styling for the child notebook tabs ---
        style = ttk.Style(self)
        active_color = COLOR_PALETTE_TABS['Markers']['active']
        inactive_color = _get_dark_color(active_color)
        
        style.configure('Controls.TNotebook', background=COLOR_PALETTE['background'])
        style.map('Controls.TNotebook.Tab',
                  background=[('selected', active_color),
                              ('!selected', inactive_color)],
                  foreground=[('selected', COLOR_PALETTE_TABS['Markers']['fg']),
                              ('!selected', 'white')])
        
        # [Creates the notebook and populates it with control tabs.]
        self.controls_notebook = ttk.Notebook(self, style='Controls.TNotebook')
        self.controls_notebook.pack(expand=True, fill='both')

        # Create instances of all the control tabs, passing the required instances
        self.span_tab = SpanTab(self.controls_notebook, self.showtime_tab_instance, self.shared_state)
        self.rbw_tab = RBWTab(self.controls_notebook, self.showtime_tab_instance, self.shared_state)
        self.poke_tab = PokeTab(self.controls_notebook, self.showtime_tab_instance, self.shared_state)
        self.traces_tab = TracesTab(self.controls_notebook, self.showtime_tab_instance, self.shared_state)
        self.zone_zoom_tab = ZoneZoomTab(self.controls_notebook, self.showtime_tab_instance, self.shared_state)

        # Add tabs to the notebook
        self.controls_notebook.add(self.span_tab, text='Span')
        self.controls_notebook.add(self.rbw_tab, text='RBW')
        self.controls_notebook.add(self.poke_tab, text='Poke')
        self.controls_notebook.add(self.traces_tab, text='Traces')
        self.controls_notebook.add(self.zone_zoom_tab, text='Zone Zoom')
        
        debug_log(f"🖥️ ✅ Widgets created successfully.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        
    def _update_control_styles(self):
        # [Updates the styles of the control buttons based on the currently selected
        # span or RBW in the shared state.]
        debug_log(f"🖥️ 🔄 Updating control button styles.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        
        # Update span buttons
        for value_str, btn in self.shared_state.span_buttons.items():
            if value_str == self.shared_state.span_var.get():
                btn.config(style='ControlButton.Active.TButton')
            else:
                btn.config(style='ControlButton.Inactive.TButton')

        # Update RBW buttons
        for value_str, btn in self.shared_state.rbw_buttons.items():
            if value_str == self.shared_state.rbw_var.get():
                btn.config(style='ControlButton.Active.TButton')
            else:
                btn.config(style='ControlButton.Inactive.TButton')

        # Update trace buttons
        for mode, var in self.shared_state.trace_modes.items():
            button = self.shared_state.trace_buttons.get(mode)
            if button:
                style = 'ControlButton.Active.TButton' if var.get() else 'ControlButton.Inactive.TButton'
                button.config(style=style)
                
        debug_log(f"🖥️ ✅ Control button styles updated successfully.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

    def switch_to_tab(self, tab_name):
        # [Programmatically switches the active tab in the controls notebook.]
        debug_log(f"🖥️ 🟢 Entering switch_to_tab with argument: {tab_name}",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

        try:
            tab_index = self.controls_notebook.index(tab_name)
            self.controls_notebook.select(tab_index)
            debug_log(f"🖥️ ✅ Successfully switched to tab: {tab_name}",
                        file=current_file,
                        version=current_version,
                        function=inspect.currentframe().f_code.co_name)
        except tk.TclError as e:
            debug_log(f"🖥️ ❌ Error switching to tab '{tab_name}': {e}",
                        file=current_file,
                        version=current_version,
                        function=inspect.currentframe().f_code.co_name)
        
        debug_log(f"🖥️ 🟢 Exiting switch_to_tab",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
