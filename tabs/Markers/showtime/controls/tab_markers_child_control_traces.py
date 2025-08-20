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
# Version 20250821.020000.1
# FIXED: Corrected the typo for `toggle_get_max_traces` to resolve `AttributeError`.
# REFACTORED: Removed local variables. Now uses shared state variables from the parent
#             `showtime_tab_instance`.
# FIXED: The `sync_trace_modes` and `execute_trace_action` utility calls now correctly
#        pass `self` to access the local variables.

current_version = "20250821.020000.1"
current_version_hash = (20250821 * 20000 * 1)

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
        
        # The variables are now held by the parent ShowtimeTab instance
        # self.toggle_get_all_traces = tk.BooleanVar(value=False)
        # self.toggle_get_live_trace = tk.BooleanVar(value=False)
        # self.toggle_get_max_traces = tk.BooleanVar(value=False)
        # self.trace_buttons = {}
        
        self._create_widgets()
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def _create_widgets(self):
        # [Creates and lays out the trace mode and action buttons.]
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        showtime_tab = self.controls_frame.showtime_tab_instance
        
        # --- Trace Mode Controls (Live/Max/Min) ---
        trace_modes_frame = ttk.Frame(self, style='TFrame')
        trace_modes_frame.grid(row=0, column=0, sticky="ew")
        trace_modes_frame.columnconfigure((0, 1, 2), weight=1)

        showtime_tab.trace_buttons['Live'] = ttk.Button(
            trace_modes_frame, text="Live\nTrace", style='ControlButton.Inactive.TButton',
            command=lambda: self._toggle_trace_button('live'))
        showtime_tab.trace_buttons['Live'].grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        
        showtime_tab.trace_buttons['Max Hold'] = ttk.Button(
            trace_modes_frame, text="Max Hold\nTrace", style='ControlButton.Inactive.TButton',
            command=lambda: self._toggle_trace_button('max'))
        showtime_tab.trace_buttons['Max Hold'].grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        showtime_tab.trace_buttons['Min Hold'] = ttk.Button(
            trace_modes_frame, text="Min Hold\nTrace", style='ControlButton.Inactive.TButton',
            command=lambda: self._toggle_trace_button('min'))
        showtime_tab.trace_buttons['Min Hold'].grid(row=0, column=2, padx=2, pady=2, sticky="ew")
        
        # --- Trace Action Controls (Get All/Live/Max) ---
        trace_actions_frame = ttk.Frame(self, style='TFrame')
        trace_actions_frame.grid(row=1, column=0, sticky="ew", pady=5)
        trace_actions_frame.columnconfigure((0, 1, 2), weight=1)

        showtime_tab.trace_buttons['Get All'] = ttk.Button(
            trace_actions_frame, text="Get All Traces", style='ControlButton.Inactive.TButton',
            command=lambda: self._toggle_trace_button('all'))
        showtime_tab.trace_buttons['Get All'].grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        showtime_tab.trace_buttons['Get Live'] = ttk.Button(
            trace_actions_frame, text="Get Live", style='ControlButton.Inactive.TButton',
            command=lambda: self._toggle_trace_button('live'))
        showtime_tab.trace_buttons['Get Live'].grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        showtime_tab.trace_buttons['Get Max'] = ttk.Button(
            trace_actions_frame, text="Get Max", style='ControlButton.Inactive.TButton',
            command=lambda: self._toggle_trace_button('max'))
        showtime_tab.trace_buttons['Get Max'].grid(row=0, column=2, padx=2, pady=2, sticky="ew")

        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def set_trace_mode(self, new_trace_mode):
        # [Sets the internal trace mode variables and updates the UI.]
        debug_log(f"Entering set_trace_mode with new mode: {new_trace_mode}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_trace_mode")
        
        showtime_tab = self.controls_frame.showtime_tab_instance

        showtime_tab.toggle_get_all_traces.set(False)
        showtime_tab.toggle_get_live_trace.set(False)
        showtime_tab.toggle_get_max_traces.set(False) # Corrected typo here
        
        if new_trace_mode == 'all':
            showtime_tab.toggle_get_all_traces.set(True)
        elif new_trace_mode == 'live':
            showtime_tab.toggle_get_live_trace.set(True)
        elif new_trace_mode == 'max':
            showtime_tab.toggle_get_max_traces.set(True) # Corrected typo here
        
        self._update_button_styles()
        self._execute_selected_trace_action()
        debug_log(f"Exiting set_trace_mode. Trace mode set to: {self.get_current_trace_mode()}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_trace_mode")

    def get_current_trace_mode(self):
        # [Returns the currently selected trace mode.]
        debug_log(f"Entering get_current_trace_mode", file=f"{os.path.basename(__file__)}", version=current_version, function="get_current_trace_mode")
        
        showtime_tab = self.controls_frame.showtime_tab_instance

        if showtime_tab.toggle_get_all_traces.get():
            return "all"
        elif showtime_tab.toggle_get_live_trace.get():
            return "live"
        elif showtime_tab.toggle_get_max_traces.get(): # Corrected typo here
            return "max"
        return "none"

    def _update_button_styles(self):
        # [Updates the visual styles of the trace action buttons based on toggle state.]
        debug_log(f"Entering _update_button_styles", file=f"{os.path.basename(__file__)}", version=current_version, function="_update_button_styles")
        
        showtime_tab = self.controls_frame.showtime_tab_instance
        active_style = 'ControlButton.Active.TButton'
        inactive_style = 'ControlButton.Inactive.TButton'

        # Set the style for the main buttons
        showtime_tab.trace_buttons['Get All'].config(style=active_style if showtime_tab.toggle_get_all_traces.get() else inactive_style)
        showtime_tab.trace_buttons['Get Live'].config(style=active_style if showtime_tab.toggle_get_live_trace.get() else inactive_style)
        showtime_tab.trace_buttons['Get Max'].config(style=active_style if showtime_tab.toggle_get_max_traces.get() else inactive_style) # Corrected typo here

    def _execute_selected_trace_action(self):
        # [A new private method to execute the correct trace action based on which button is active.]
        debug_log(f"Entering _execute_selected_trace_action", file=f"{os.path.basename(__file__)}", version=current_version, function="_execute_selected_trace_action")
        
        showtime_tab = self.controls_frame.showtime_tab_instance
        
        # NEW: Check if any button is active. If not, default to 'Get All'
        if not showtime_tab.toggle_get_all_traces.get() and not showtime_tab.toggle_get_live_trace.get() and not showtime_tab.toggle_get_max_traces.get(): # Corrected typo here
            self.controls_frame.console_print_func("No trace action button is currently active. Defaulting to 'Get All Traces'.")
            showtime_tab.toggle_get_all_traces.set(True)
            self._update_button_styles() # Update the UI to show 'Get All' is active

        if showtime_tab.toggle_get_all_traces.get():
            execute_trace_action(self, action_type='all')
        elif showtime_tab.toggle_get_live_trace.get():
            execute_trace_action(self, action_type='live')
        elif showtime_tab.toggle_get_max_traces.get(): # Corrected typo here
            execute_trace_action(self, action_type='max')
        else:
            self.controls_frame.console_print_func("No trace action button is currently active.")
            debug_log(f"No trace action button is currently active. Nothing to execute!", file=f"{os.path.basename(__file__)}", version=current_version, function="_execute_selected_trace_action")

    def _toggle_trace_button(self, button_type):
        debug_log(f"Toggling trace button of type '{button_type}'.", file=f"{os.path.basename(__file__)}", version=current_version, function="_toggle_trace_button")
        
        showtime_tab = self.controls_frame.showtime_tab_instance

        # Determine which variable to toggle
        target_var = None
        if button_type == 'all':
            target_var = showtime_tab.toggle_get_all_traces
        elif button_type == 'live':
            target_var = showtime_tab.toggle_get_live_trace
        elif button_type == 'max':
            target_var = showtime_tab.toggle_get_max_traces # Corrected typo here

        if not target_var:
            self.controls_frame.console_print_func(f"Error: Unknown trace button type '{button_type}'.")
            return

        # Deselect all other buttons
        if button_type != 'all': showtime_tab.toggle_get_all_traces.set(False)
        if button_type != 'live': showtime_tab.toggle_get_live_trace.set(False)
        if button_type != 'max': showtime_tab.toggle_get_max_traces.set(False) # Corrected typo here

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