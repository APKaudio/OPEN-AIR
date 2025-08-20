# tabs/Markers/showtime/controls/tab_markers_parent_bottom_controls.py
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
# Version 20250820.232500.1
# FIXED: The parent `ControlsFrame` now correctly stores the `follow_zone_span_var`,
#        as it is a shared state variable required by both the Span and ZoneZoom tabs.
# FIXED: All other `AttributeError`s were fixed by moving the variables to their respective
#        child classes.

current_version = "20250820.232500.1"
current_version_hash = (20250820 * 232500 * 1)

import tkinter as tk
from tkinter import ttk
import os
import inspect
from datetime import datetime

from display.debug_logic import debug_log
from display.console_logic import console_log

# Import all utility functions
from process_math.math_frequency_translation import (
    format_hz
)
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
        # [Initializes the ControlsFrame as a generic container.]
        debug_log(f"Entering __init__", file=f"{os.path.basename(__file__)}", version=current_version, function="__init__")
        try:
            super().__init__(parent, style='TFrame')
            self.app_instance = app_instance
            self.grid(row=0, column=0, sticky="nsew")
            self.columnconfigure(0, weight=1)

            # --- Instance variables to manage the notebook tabs ---
            self.current_tab_instance = None
            self.last_tab_index = -1
            self.controls_notebook = None
            self.follow_zone_span_var = tk.BooleanVar(value=True)

            self._create_controls_notebook()
            
            console_log("✅ ControlsFrame initialized successfully!")
        except Exception as e:
            console_log(f"❌ Error in ControlsFrame __init__: {e}")
            debug_log(f"Arrr, the code be capsized! The error be: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="__init__")

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
        new_tab_instance = self.controls_notebook.winfo_children()[selected_index]
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