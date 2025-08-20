# tabs/Markers/showtime/controls/tab_markers_child_bottom_controls.py
#
# This file defines the ControlsFrame, a reusable ttk.Frame containing the
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
# Version 20250821.005500.1
# FIXED: The `_update_control_styles` method has been restored to this parent class,
#        resolving the `AttributeError`. It now acts as an orchestration point for
#        all child-tab UI updates.
# FIXED: `span_var` and `rbw_var` were restored here as shared state variables.

current_version = "20250821.005500.1"
current_version_hash = (20250821 * 5500 * 1)

import tkinter as tk
from tkinter import ttk
import os
import inspect
from datetime import datetime

from display.debug_logic import debug_log
from display.console_logic import console_log

# Import all utility functions
from tabs.Markers.showtime.controls.utils_showtime_trace import (
    sync_trace_modes
)

# Import the new child tab modules
from tabs.Markers.showtime.controls.tab_markers_child_control_span import SpanTab
from tabs.Markers.showtime.controls.tab_markers_child_control_rbw import RBWTab
from tabs.Markers.showtime.controls.tab_markers_child_control_traces import TracesTab
from tabs.Markers.showtime.controls.tab_markers_child_control_poke import PokeTab
from tabs.Markers.showtime.controls.tab_markers_child_control_zone_zoom import ZoneZoomTab


class ControlsFrame(ttk.Frame):
    def __init__(self, parent, app_instance):
        # [Initializes the ControlsFrame and all its associated Tkinter variables.]
        debug_log(f"Entering __init__", file=f"{os.path.basename(__file__)}", version=current_version, function="__init__")
        try:
            super().__init__(parent, style='TFrame')
            self.app_instance = app_instance
            self.grid(row=0, column=0, sticky="nsew")
            self.columnconfigure(0, weight=1)
            
            # --- Initialize shared Tkinter Control Variables ---
            self.span_var = tk.StringVar(value="1000000")
            self.rbw_var = tk.StringVar(value="100000")
            self.follow_zone_span_var = tk.BooleanVar(value=True)
            self.poke_freq_var = tk.StringVar()
            self.buffer_var = tk.StringVar(value="1") 
            self.zone_zoom_label_left_var = tk.StringVar(value="All Markers")
            self.zone_zoom_label_center_var = tk.StringVar(value="Start: N/A")
            self.zone_zoom_label_right_var = tk.StringVar(value="Stop: N/A (0 Markers)")
            
            # --- Dictionaries to hold button references from child tabs ---
            self.span_buttons = {}
            self.rbw_buttons = {}
            self.trace_buttons = {}
            self.zone_zoom_buttons = {}
            
            self.current_tab_instance = None
            self.last_tab_index = -1
            self.controls_notebook = None
            self._create_controls_notebook()

            self.after(100, lambda: sync_trace_modes(self))
            self.after(110, lambda: self._update_control_styles())
            console_log("✅ ControlsFrame initialized successfully!")
        except Exception as e:
            console_log(f"❌ Error in ControlsFrame __init__: {e}")
            debug_log(f"Arrr, the code be capsized! The error be: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="__init__")
    
    def _update_control_styles(self):
        # [Updates the visual styles of all control buttons by calling child methods.]
        debug_log(f"Entering _update_control_styles", file=f"{os.path.basename(__file__)}", version=current_version, function="_update_control_styles")
        
        # Get references to the child tabs
        poke_tab = self.controls_notebook.nametowidget(self.controls_notebook.tabs()[0])
        span_tab = self.controls_notebook.nametowidget(self.controls_notebook.tabs()[1])
        rbw_tab = self.controls_notebook.nametowidget(self.controls_notebook.tabs()[2])
        zone_zoom_tab = self.controls_notebook.nametowidget(self.controls_notebook.tabs()[3])
        traces_tab = self.controls_notebook.nametowidget(self.controls_notebook.tabs()[4])

        # Call their respective update methods
        if hasattr(poke_tab, '_sync_ui_from_app_state'):
            poke_tab._sync_ui_from_app_state()
        if hasattr(span_tab, '_sync_ui_from_app_state'):
            span_tab._sync_ui_from_app_state()
        if hasattr(rbw_tab, '_sync_ui_from_app_state'):
            rbw_tab._sync_ui_from_app_state()
        if hasattr(zone_zoom_tab, '_update_zone_zoom_button_styles'):
            zone_zoom_tab._update_zone_zoom_button_styles()
        if hasattr(traces_tab, '_update_button_styles'):
            traces_tab._update_button_styles()
            
        debug_log(f"Exiting _update_control_styles", file=f"{os.path.basename(__file__)}", version=current_version, function="_update_control_styles")

    def _create_controls_notebook(self):
        # [Creates the notebook and populates it with all the control tabs.]
        debug_log(f"Entering _create_controls_notebook", file=f"{os.path.basename(__file__)}", version=current_version, function="_create_controls_notebook")
        try:
            self.controls_notebook = ttk.Notebook(self, style='Markers.Child.TNotebook')
            self.controls_notebook.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

            # --- Poke Tab ---
            poke_tab_instance = PokeTab(self.controls_notebook, self)
            self.controls_notebook.add(poke_tab_instance, text="Poke Frequency")

            # --- Span Tab ---
            span_tab_instance = SpanTab(self.controls_notebook, self)
            self.controls_notebook.add(span_tab_instance, text="Span")

            # --- RBW Tab ---
            rbw_tab_instance = RBWTab(self.controls_notebook, self)
            self.controls_notebook.add(rbw_tab_instance, text="RBW")
            
            # --- Zone Zoom Tab ---
            zone_zoom_tab_instance = ZoneZoomTab(self.controls_notebook, self)
            self.controls_notebook.add(zone_zoom_tab_instance, text="Zone Zoom")
            
            # --- Traces Tab ---
            traces_tab_instance = TracesTab(self.controls_notebook, self)
            self.controls_notebook.add(traces_tab_instance, text="Traces")
            
            # Bind the tab change event
            self.controls_notebook.bind("<<NotebookTabChanged>>", self._on_notebook_tab_change)

            # Manually trigger the first selection
            self._on_notebook_tab_change(None)

            console_log("✅ Controls notebook created successfully!")
        except Exception as e:
            console_log(f"❌ Error in _create_controls_notebook: {e}")
            debug_log(f"Shiver me timbers, the controls notebook has been scuttled! The error be: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="_create_controls_notebook")

    def _on_notebook_tab_change(self, event):
        # [Handles the event when the notebook tab changes.]
        debug_log(f"Entering _on_notebook_tab_change", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_notebook_tab_change")

        # Get the index of the currently selected tab
        selected_index = self.controls_notebook.index(self.controls_notebook.select())
        
        # Get the instance of the old and new tabs
        old_tab_instance = self.current_tab_instance
        new_tab_instance = self.controls_notebook.nametowidget(self.controls_notebook.tabs()[selected_index])
        self.current_tab_instance = new_tab_instance

        # Call the deselected method on the old tab
        if old_tab_instance and hasattr(old_tab_instance, "_on_tab_deselected"):
            old_tab_instance._on_tab_deselected()
        
        # Call the selected method on the new tab
        if hasattr(new_tab_instance, "_on_tab_selected"):
            new_tab_instance._on_tab_selected()

        debug_log(f"Exiting _on_notebook_tab_change. Switched from index {self.last_tab_index} to {selected_index}",
                    file=f"{os.path.basename(__file__)}", version=current_version, function="_on_notebook_tab_change")
        self.last_tab_index = selected_index

    def _get_zgd_frame(self):
        # [Safely gets the ZoneGroupsDevicesFrame instance from the application hierarchy.]
        debug_log(f"Entering _get_zgd_frame", file=f"{os.path.basename(__file__)}", version=current_version, function="_get_zgd_frame")
        try:
            zgd_frame = self.app_instance.tabs_parent.tab_content_frames['Markers'].showtime_tab.zgd_frame
            return zgd_frame
        except (AttributeError, KeyError) as e:
            self.console_print_func("❌ Error: Could not find the main markers display frame.")
            debug_log(f"Could not find ZGD frame: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="_get_zgd_frame")
            return None

    def console_print_func(self, message, level="INFO"):
        # [Safely prints a message to the main application console.]
        debug_log(f"Entering console_print_func with message: {message}", file=f"{os.path.basename(__file__)}", version=current_version, function="console_print_func")
        if hasattr(self.app_instance, 'console_tab') and hasattr(self.app_instance.console_tab, 'console_log'):
             self.app_instance.console_tab.console_log(message, level)
        else:
             print(f"[{level.upper()}] {message}")