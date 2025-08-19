# tabs/Markers/showtime/controls/tab_markers_child_bottom_controls.py
#
# This file defines the ControlsFrame, a reusable ttk.Frame containing the
# Span, RBW, Trace Modes, and other controls in a notebook.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250819.105942.1
# MODIFIED: Converted Get Live, Get Max, and Get All buttons to toggles.
# MODIFIED: Added a Buffer dropdown and removed "Set " from button labels.
# MODIFIED: Reverted trace controls to use individual toggle buttons.
# FIXED: The logic for toggling trace action buttons and updating their styles has been completely rewritten.
# FIXED: The _execute_selected_trace_action method was added to the ControlsFrame class.

current_version = "20250819.105942.1"
current_version_hash = (20250819 * 105942 * 1)

import tkinter as tk
from tkinter import ttk
import os
import inspect
from datetime import datetime

from display.debug_logic import debug_log
from display.console_logic import console_log
# MODIFIED: Added imports for the new trace handler functions
from tabs.Markers.showtime.controls.utils_showtime_controls import (
    on_span_button_click, on_rbw_button_click, on_trace_button_click, on_poke_action,
    format_hz, sync_trace_modes, _update_control_styles, SPAN_OPTIONS, RBW_OPTIONS,
    on_get_all_traces_click, on_get_live_trace_click, on_get_max_trace_click
)

from tabs.Markers.showtime.controls.utils_showtime_zone_zoom import (
    set_span_to_zone, set_span_to_group, set_span_to_device, set_span_to_all_markers
)


class ControlsFrame(ttk.Frame):
    def __init__(self, parent, app_instance):
        # [Initializes the ControlsFrame and all its associated Tkinter variables.]
        debug_log(f"Entering __init__", file=f"{os.path.basename(__file__)}", version=current_version, function="__init__")
        try:
            super().__init__(parent, style='TFrame')
            self.app_instance = app_instance
            self.grid(row=0, column=0, sticky="nsew")
            self.columnconfigure(0, weight=1)

            # --- Initialize Tkinter Control Variables ---
            self.span_var = tk.StringVar(value="1000000")
            self.rbw_var = tk.StringVar(value="100000")
            self.follow_zone_span_var = tk.BooleanVar(value=True)
            self.trace_live_mode = tk.BooleanVar(value=True)
            self.trace_max_hold_mode = tk.BooleanVar(value=True)
            self.trace_min_hold_mode = tk.BooleanVar(value=True)
            self.poke_freq_var = tk.StringVar()
            self.buffer_var = tk.StringVar(value="1") 

            self.zone_zoom_label_left_var = tk.StringVar(value="All Markers")
            self.zone_zoom_label_center_var = tk.StringVar(value="Start: N/A")
            self.zone_zoom_label_right_var = tk.StringVar(value="Stop: N/A (0 Markers)")
            
            # New toggle variables for the TRACES tab
            self.toggle_get_all_traces = tk.BooleanVar(value=False)
            self.toggle_get_live_trace = tk.BooleanVar(value=False)
            self.toggle_get_max_trace = tk.BooleanVar(value=False)


            self.span_buttons = {}
            self.rbw_buttons = {}
            self.trace_buttons = {}
            self.zone_zoom_buttons = {}

            self._create_controls_notebook()

            self.after(100, lambda: sync_trace_modes(self))
            self.after(110, lambda: _update_control_styles(self))
            console_log("✅ ControlsFrame initialized successfully!")
        except Exception as e:
            console_log(f"❌ Error in ControlsFrame __init__: {e}")
            debug_log(f"Arrr, the code be capsized! The error be: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="__init__")

    def _execute_selected_trace_action(self):
        # This function description tells me what this function does
        # A new private method to execute the correct trace action based on which button is active.
        debug_log(f"Entering _execute_selected_trace_action. Executing the selected trace handler.", file=f"{os.path.basename(__file__)}", version=current_version, function="_execute_selected_trace_action")
        
        # NEW: Check if any button is active. If not, default to 'Get All'
        if not self.toggle_get_all_traces.get() and not self.toggle_get_live_trace.get() and not self.toggle_get_max_trace.get():
            self.console_print_func("No trace action button is currently active. Defaulting to 'Get All Traces'.")
            self.toggle_get_all_traces.set(True)
            self._update_button_styles() # Update the UI to show 'Get All' is active

        if self.toggle_get_all_traces.get():
            on_get_all_traces_click(self)
        elif self.toggle_get_live_trace.get():
            on_get_live_trace_click(self)
        elif self.toggle_get_max_trace.get():
            on_get_max_trace_click(self)
        else:
            self.console_print_func("No trace action button is currently active.")
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
            self.console_print_func(f"Error: Unknown trace button type '{button_type}'.")
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

    def _update_button_styles(self):
        debug_log(f"Updating button styles based on toggle state.", file=f"{os.path.basename(__file__)}", version=current_version, function="_update_button_styles")
        
        active_style = 'ControlButton.Active.TButton'
        inactive_style = 'ControlButton.Inactive.TButton'

        # Set the style for the main buttons
        self.trace_buttons['Get All'].config(style=active_style if self.toggle_get_all_traces.get() else inactive_style)
        self.trace_buttons['Get Live'].config(style=active_style if self.toggle_get_live_trace.get() else inactive_style)
        self.trace_buttons['Get Max'].config(style=active_style if self.toggle_get_max_trace.get() else inactive_style)

    def _create_controls_notebook(self):
        # [Creates the notebook and populates it with all the control tabs.]
        debug_log(f"Entering _create_controls_notebook", file=f"{os.path.basename(__file__)}", version=current_version, function="_create_controls_notebook")
        try:
            self.controls_notebook = ttk.Notebook(self, style='Markers.Child.TNotebook')
            self.controls_notebook.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

            # --- Span Tab ---
            span_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=5)
            self.controls_notebook.add(span_tab, text="Span")
            # MODIFIED: Removed "Follow Zone" button
            for i, (name, span_hz) in enumerate(SPAN_OPTIONS.items()):
                btn_text = f"{name}\n({format_hz(span_hz)})"
                btn = ttk.Button(span_tab, text=btn_text, style='ControlButton.Inactive.TButton', command=lambda s=span_hz: on_span_button_click(self, s))
                btn.grid(row=0, column=i, padx=2, pady=2, sticky="ew")
                self.span_buttons[str(span_hz)] = btn
            for i in range(len(SPAN_OPTIONS)):
                span_tab.grid_columnconfigure(i, weight=1)

            # --- RBW Tab ---
            rbw_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=5)
            self.controls_notebook.add(rbw_tab, text="RBW")
            for i, (name, rbw_hz) in enumerate(RBW_OPTIONS.items()):
                btn_text = f"{name}\n({format_hz(rbw_hz)})"
                btn = ttk.Button(rbw_tab, text=btn_text, style='ControlButton.Inactive.TButton', command=lambda r=rbw_hz: on_rbw_button_click(self, r))
                btn.grid(row=0, column=i, padx=2, pady=2, sticky="ew")
                self.rbw_buttons[str(rbw_hz)] = btn
                rbw_tab.grid_columnconfigure(i, weight=1)
            
            # --- MODIFIED: Trace Tab (back to toggle buttons) ---
            trace_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=5)
            self.controls_notebook.add(trace_tab, text="Trace Modes")
            
            # Reverting to the old toggle button system
            live_btn = ttk.Button(trace_tab, text="Live\nTrace", style='ControlButton.Inactive.TButton', command=lambda: on_trace_button_click(self, self.trace_live_mode))
            live_btn.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
            self.trace_buttons['Live'] = live_btn
            
            max_btn = ttk.Button(trace_tab, text="Max Hold\nTrace", style='ControlButton.Inactive.TButton', command=lambda: on_trace_button_click(self, self.trace_max_hold_mode))
            max_btn.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
            self.trace_buttons['Max Hold'] = max_btn
            
            min_btn = ttk.Button(trace_tab, text="Min Hold\nTrace", style='ControlButton.Inactive.TButton', command=lambda: on_trace_button_click(self, self.trace_min_hold_mode))
            min_btn.grid(row=0, column=2, padx=2, pady=2, sticky="ew")
            self.trace_buttons['Min Hold'] = min_btn
            
            trace_tab.columnconfigure((0, 1, 2), weight=1)

            # --- MODIFIED: Traces Tab (new toggle buttons) ---
            traces_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=5)
            self.controls_notebook.add(traces_tab, text="TRACES")
            traces_tab.columnconfigure((0, 1, 2), weight=1)

            # Replaced Checkbuttons with regular Buttons and manually manage their state
            btn_get_all = ttk.Button(traces_tab, text="Get All Traces", style='ControlButton.Inactive.TButton', command=lambda: self._toggle_trace_button('all'))
            btn_get_all.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
            self.trace_buttons['Get All'] = btn_get_all

            btn_get_live = ttk.Button(traces_tab, text="Get Live", style='ControlButton.Inactive.TButton', command=lambda: self._toggle_trace_button('live'))
            btn_get_live.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
            self.trace_buttons['Get Live'] = btn_get_live

            btn_get_max = ttk.Button(traces_tab, text="Get Max", style='ControlButton.Inactive.TButton', command=lambda: self._toggle_trace_button('max'))
            btn_get_max.grid(row=0, column=2, padx=2, pady=2, sticky="ew")
            self.trace_buttons['Get Max'] = btn_get_max

            # --- Poke Tab ---
            poke_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=5)
            self.controls_notebook.add(poke_tab, text="Poke Frequency")
            poke_tab.columnconfigure(0, weight=1)
            poke_entry = ttk.Entry(poke_tab, textvariable=self.poke_freq_var)
            poke_entry.pack(side='left', fill='x', expand=True, padx=2, pady=2)
            poke_btn = ttk.Button(poke_tab, text="Poke", style='ControlButton.Inactive.TButton', command=lambda: on_poke_action(self))
            poke_btn.pack(side='left', padx=2, pady=2)

            # --- Zone Zoom Tab ---
            zone_zoom_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=5)
            self.controls_notebook.add(zone_zoom_tab, text="Zone Zoom")
            zone_zoom_tab.columnconfigure((0, 1, 2, 4), weight=1)
            zone_zoom_tab.columnconfigure(3, weight=0) 

            # Labels
            ttk.Label(zone_zoom_tab, textvariable=self.zone_zoom_label_left_var, anchor="w").grid(row=0, column=0, columnspan=2, pady=2, padx=2, sticky="w")
            ttk.Label(zone_zoom_tab, textvariable=self.zone_zoom_label_center_var, anchor="e").grid(row=0, column=2, pady=2, padx=2, sticky="e")
            ttk.Label(zone_zoom_tab, textvariable=self.zone_zoom_label_right_var, anchor="e").grid(row=0, column=3, columnspan=2, pady=2, padx=2, sticky="e")
            
            # NEW: Buffer Dropdown
            ttk.Label(zone_zoom_tab, text="Buffer (MHz):", anchor="w").grid(row=1, column=0, columnspan=2, pady=2, padx=2, sticky="w")
            buffer_options = [1, 3, 10, 30]
            buffer_combobox = ttk.Combobox(zone_zoom_tab, textvariable=self.buffer_var, values=buffer_options, state="readonly", width=5)
            buffer_combobox.grid(row=1, column=1, columnspan=1, padx=2, pady=2, sticky="ew")

            # --- REORDERED Buttons ---
            # MODIFIED: Removed "Set" from button text
            btn_all = ttk.Button(zone_zoom_tab, text="All Markers", style='ControlButton.Inactive.TButton', command=self._on_set_span_to_all_markers_click)
            btn_all.grid(row=2, column=0, padx=2, pady=2, sticky="ew")
            self.zone_zoom_buttons['All'] = btn_all

            btn_zone = ttk.Button(zone_zoom_tab, text="Zone", style='ControlButton.Inactive.TButton', command=self._on_set_span_to_zone_click)
            btn_zone.grid(row=2, column=1, padx=2, pady=2, sticky="ew")
            self.zone_zoom_buttons['Zone'] = btn_zone

            btn_group = ttk.Button(zone_zoom_tab, text="Group", style='ControlButton.Inactive.TButton', command=self._on_set_span_to_group_click)
            btn_group.grid(row=2, column=2, padx=2, pady=2, sticky="ew")
            self.zone_zoom_buttons['Group'] = btn_group
            
            # Spacer for visual separation
            ttk.Frame(zone_zoom_tab, width=20, style='TFrame').grid(row=2, column=3)

            btn_device = ttk.Button(zone_zoom_tab, text="Device", style='ControlButton.Inactive.TButton', command=self._on_set_span_to_device_click)
            btn_device.grid(row=2, column=4, padx=2, pady=2, sticky="ew")
            self.zone_zoom_buttons['Device'] = btn_device
            console_log("✅ Controls notebook created successfully!")
        except Exception as e:
            console_log(f"❌ Error in _create_controls_notebook: {e}")
            debug_log(f"Shiver me timbers, the controls notebook has been scuttled! Error: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="_create_controls_notebook")

    def switch_to_tab(self, tab_name):
        """Switches the active tab in the controls notebook."""
        debug_log(f"Entering switch_to_tab for '{tab_name}'", file=f"{os.path.basename(__file__)}", version=current_version, function="switch_to_tab")
        if self.controls_notebook:
            tab_index = -1
            for i in range(self.controls_notebook.index("end")):
                if self.controls_notebook.tab(i, "text") == tab_name:
                    tab_index = i
                    break
            if tab_index != -1:
                self.controls_notebook.select(tab_index)
                debug_log(f"Switched to tab '{tab_name}' successfully.", file=f"{os.path.basename(__file__)}", version=current_version, function="switch_to_tab")
            else:
                debug_log(f"Tab '{tab_name}' not found. Cannot switch.", file=f"{os.path.basename(__file__)}", version=current_version, function="switch_to_tab")
        else:
            debug_log("Controls notebook not found. Cannot switch tabs.", file=f"{os.path.basename(__file__)}", version=current_version, function="switch_to_tab")

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

    def _on_set_span_to_zone_click(self):
        # [Handles the click event to set the instrument span to the selected zone.]
        debug_log(f"Entering _on_set_span_to_zone_click", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_set_span_to_zone_click")
        zgd_frame = self._get_zgd_frame()
        if not zgd_frame or not zgd_frame.selected_zone:
            self.console_print_func("⚠️ No zone selected.")
            return
        
        devices = zgd_frame._get_all_devices_in_zone(zgd_frame.structured_data, zgd_frame.selected_zone)
        freqs = [d.get('CENTER') for d in devices if d.get('CENTER')]
        
        if not freqs:
            self.console_print_func("⚠️ Selected zone has no markers with frequencies.")
            return
            
        set_span_to_zone(self, ZoneName=zgd_frame.selected_zone, NumberOfMarkers=len(freqs),
                         StartFreq=min(freqs), StopFreq=max(freqs), selected=True, buffer_mhz=float(self.buffer_var.get()))
        
        self._execute_selected_trace_action()

    def _on_set_span_to_group_click(self):
        # [Handles the click event to set the instrument span to the selected group.]
        debug_log(f"Entering _on_set_span_to_group_click", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_set_span_to_group_click")
        zgd_frame = self._get_zgd_frame()
        if not zgd_frame or not zgd_frame.selected_group:
            self.console_print_func("⚠️ No group selected.")
            return
            
        devices = zgd_frame.structured_data.get(zgd_frame.selected_zone, {}).get(zgd_frame.selected_group, [])
        freqs = [d.get('CENTER') for d in devices if d.get('CENTER')]

        if not freqs:
            self.console_print_func("⚠️ Selected group has no markers with frequencies.")
            return
            
        set_span_to_group(self, GroupName=zgd_frame.selected_group, NumberOfMarkers=len(freqs),
                          StartFreq=min(freqs), StopFreq=max(freqs), buffer_mhz=float(self.buffer_var.get()))

        self._execute_selected_trace_action()

    def _on_set_span_to_device_click(self):
        # [Handles the click event to set the instrument span to the selected device.]
        debug_log(f"Entering _on_set_span_to_device_click", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_set_span_to_device_click")
        zgd_frame = self._get_zgd_frame()
        if not zgd_frame or not hasattr(zgd_frame, 'selected_device_info') or not zgd_frame.selected_device_info:
            self.console_print_func("⚠️ No device selected.")
            return
            
        device_info = zgd_frame.selected_device_info
        device_name = device_info.get('NAME', 'N/A')
        center_freq = device_info.get('CENTER')

        if not center_freq:
            self.console_print_func("⚠️ Selected device has no frequency.")
            return
            
        set_span_to_device(self, DeviceName=device_name, CenterFreq=center_freq)

        self._execute_selected_trace_action()

    def _on_set_span_to_all_markers_click(self):
        # [Handles the click event to set the instrument span to all loaded markers.]
        debug_log(f"Entering _on_set_span_to_all_markers_click", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_set_span_to_all_markers_click")
        zgd_frame = self._get_zgd_frame()
        if not zgd_frame:
            return
            
        all_devices = zgd_frame._get_all_devices_in_zone(zgd_frame.structured_data, zone_name=None)
        freqs = [d.get('CENTER') for d in all_devices if d.get('CENTER')]

        if not freqs:
            self.console_print_func("⚠️ No markers loaded.")
            return

        set_span_to_all_markers(self, NumberOfMarkers=len(freqs), StartFreq=min(freqs),
                                StopFreq=max(freqs), selected=True, buffer_mhz=float(self.buffer_var.get()))

    def console_print_func(self, message, level="INFO"):
        # [Safely prints a message to the main application console.]
        debug_log(f"Entering console_print_func with message: {message}", file=f"{os.path.basename(__file__)}", version=current_version, function="console_print_func")
        if hasattr(self.app_instance, 'console_tab') and hasattr(self.app_instance.console_tab, 'console_log'):
             self.app_instance.console_tab.console_log(message, level)
        else:
             print(f"[{level.upper()}] {message}")
