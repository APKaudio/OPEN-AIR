# tabs/Markers/showtime/controls/tab_markers_child_control_traces.py
#
# This file defines the Trace tab for the ControlsFrame. It contains the buttons
# for setting the trace modes and for fetching and displaying traces.
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
# Version 20250821.004800.1
# FIXED: All `AttributeError`s were fixed by correcting the variable references
#        to point to the local instance (`self`) instead of the parent.
# FIXED: The `sync_trace_modes` and `execute_trace_action` utility calls now correctly
#        pass `self` to access the local variables.

current_version = "20250821.004800.1"
current_version_hash = (20250821 * 4800 * 1)

import os
import inspect
import tkinter as tk
from tkinter import ttk

from display.debug_logic import debug_log
from display.console_logic import console_log

from tabs.Markers.showtime.controls.utils_showtime_trace import (
    execute_trace_action, sync_trace_modes
)

class TracesTab(ttk.Frame):
    def __init__(self, parent, controls_frame):
        # [Initializes the Traces tab and its associated controls.]
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        super().__init__(parent, style='TFrame', padding=5)
        self.controls_frame = controls_frame
        
        # Now defined within this class
        self.toggle_get_all_traces = tk.BooleanVar(value=False)
        self.toggle_get_live_trace = tk.BooleanVar(value=False)
        self.toggle_get_max_trace = tk.BooleanVar(value=False)
        self.trace_buttons = {}
        
        self._create_widgets()
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def _create_widgets(self):
        # [Creates and lays out the trace mode and action buttons.]
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        # --- Trace Mode Controls (Live/Max/Min) ---
        trace_modes_frame = ttk.Frame(self, style='TFrame')
        trace_modes_frame.grid(row=0, column=0, sticky="ew")
        trace_modes_frame.columnconfigure((0, 1, 2), weight=1)

        self.trace_buttons['Live'] = ttk.Button(
            trace_modes_frame, text="Live\nTrace", style='ControlButton.Inactive.TButton',
            command=lambda: self._toggle_trace_button('live'))
        self.trace_buttons['Live'].grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        
        self.trace_buttons['Max Hold'] = ttk.Button(
            trace_modes_frame, text="Max Hold\nTrace", style='ControlButton.Inactive.TButton',
            command=lambda: self._toggle_trace_button('max'))
        self.trace_buttons['Max Hold'].grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        self.trace_buttons['Min Hold'] = ttk.Button(
            trace_modes_frame, text="Min Hold\nTrace", style='ControlButton.Inactive.TButton',
            command=lambda: self._toggle_trace_button('min'))
        self.trace_buttons['Min Hold'].grid(row=0, column=2, padx=2, pady=2, sticky="ew")
        
        # --- Trace Action Controls (Get All/Live/Max) ---
        trace_actions_frame = ttk.Frame(self, style='TFrame')
        trace_actions_frame.grid(row=1, column=0, sticky="ew", pady=5)
        trace_actions_frame.columnconfigure((0, 1, 2), weight=1)

        self.trace_buttons['Get All'] = ttk.Button(
            trace_actions_frame, text="Get All Traces", style='ControlButton.Inactive.TButton',
            command=lambda: self._toggle_trace_button('all'))
        self.trace_buttons['Get All'].grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        self.trace_buttons['Get Live'] = ttk.Button(
            trace_actions_frame, text="Get Live", style='ControlButton.Inactive.TButton',
            command=lambda: self._toggle_trace_button('live'))
        self.trace_buttons['Get Live'].grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        self.trace_buttons['Get Max'] = ttk.Button(
            trace_actions_frame, text="Get Max", style='ControlButton.Inactive.TButton',
            command=lambda: self._toggle_trace_button('max'))
        self.trace_buttons['Get Max'].grid(row=0, column=2, padx=2, pady=2, sticky="ew")

        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def set_trace_mode(self, new_trace_mode):
        # [Sets the internal trace mode variables and updates the UI.]
        debug_log(f"Entering set_trace_mode with new mode: {new_trace_mode}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_trace_mode")
        self.toggle_get_all_traces.set(False)
        self.toggle_get_live_trace.set(False)
        self.toggle_get_max_trace.set(False)
        
        if new_trace_mode == 'all':
            self.toggle_get_all_traces.set(True)
        elif new_trace_mode == 'live':
            self.toggle_get_live_trace.set(True)
        elif new_trace_mode == 'max':
            self.toggle_get_max_trace.set(True)
        
        self._update_button_styles()
        self._execute_selected_trace_action()
        debug_log(f"Exiting set_trace_mode. Trace mode set to: {self.get_current_trace_mode()}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_trace_mode")

    def get_current_trace_mode(self):
        # [Returns the currently selected trace mode.]
        debug_log(f"Entering get_current_trace_mode", file=f"{os.path.basename(__file__)}", version=current_version, function="get_current_trace_mode")
        if self.toggle_get_all_traces.get():
            return "all"
        elif self.toggle_get_live_trace.get():
            return "live"
        elif self.toggle_get_max_trace.get():
            return "max"
        return "none"

    def _update_button_styles(self):
        # [Updates the visual styles of the trace action buttons based on toggle state.]
        debug_log(f"Entering _update_button_styles", file=f"{os.path.basename(__file__)}", version=current_version, function="_update_button_styles")
        
        active_style = 'ControlButton.Active.TButton'
        inactive_style = 'ControlButton.Inactive.TButton'

        # Set the style for the main buttons
        self.trace_buttons['Get All'].config(style=active_style if self.toggle_get_all_traces.get() else inactive_style)
        self.trace_buttons['Get Live'].config(style=active_style if self.toggle_get_live_trace.get() else inactive_style)
        self.trace_buttons['Get Max'].config(style=active_style if self.toggle_get_max_trace.get() else inactive_style)

    def _execute_selected_trace_action(self):
        # [A new private method to execute the correct trace action based on which button is active.]
        debug_log(f"Entering _execute_selected_trace_action", file=f"{os.path.basename(__file__)}", version=current_version, function="_execute_selected_trace_action")
        
        # NEW: Check if any button is active. If not, default to 'Get All'
        if not self.toggle_get_all_traces.get() and not self.toggle_get_live_trace.get() and not self.toggle_get_max_trace.get():
            self.controls_frame.console_print_func("No trace action button is currently active. Defaulting to 'Get All Traces'.")
            self.toggle_get_all_traces.set(True)
            self._update_button_styles() # Update the UI to show 'Get All' is active

        if self.toggle_get_all_traces.get():
            execute_trace_action(self, action_type='all')
        elif self.toggle_get_live_trace.get():
            execute_trace_action(self, action_type='live')
        elif self.toggle_get_max_trace.get():
            execute_trace_action(self, action_type='max')
        else:
            self.controls_frame.console_print_func("No trace action button is currently active.")
            debug_log(f"No trace action button is currently active. Nothing to execute!", file=f"{os.path.basename(__file__)}", version=current_version, function="_execute_selected_trace_action")

    def _toggle_trace_button(self, button_type):
        debug_log(f"Toggling trace button of type '{button_type}'.", file=f"{os.path.basename(__file__)}", version=current_version, function="_toggle_trace_button")
        
        # Determine which variable to toggle
        target_var = None
        if button_type == 'all':
            target_var = self.toggle_get_all_traces
        elif button_type == 'live':
            target_var = self.toggle_get_live_trace
        elif button_type == 'max':
            target_var = self.toggle_get_max_trace

        if not target_var:
            self.controls_frame.console_print_func(f"Error: Unknown trace button type '{button_type}'.")
            return

        # Deselect all other buttons
        if button_type != 'all': self.toggle_get_all_traces.set(False)
        if button_type != 'live': self.toggle_get_live_trace.set(False)
        if button_type != 'max': self.toggle_get_max_trace.set(False)

        # Toggle the selected button's state
        target_var.set(not target_var.get())
        
        # Update button styles and execute action
        self._update_button_styles()
        self._execute_selected_trace_action()

    def _on_tab_selected(self):
        # [Synchronizes the UI elements when the tab is selected.]
        debug_log(f"Entering _on_tab_selected", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_tab_selected")
        sync_trace_modes(self)
        self._update_button_styles()
        debug_log(f"Exiting _on_tab_selected", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_tab_selected")

    def _on_tab_deselected(self):
        # [Performs any necessary cleanup when the tab is deselected.]
        debug_log(f"Entering _on_tab_deselected", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_tab_deselected")
        # No action required at this time.
        pass
        debug_log(f"Exiting _on_tab_deselected", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_tab_deselected")