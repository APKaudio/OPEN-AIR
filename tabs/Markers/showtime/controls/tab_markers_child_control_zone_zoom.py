# tabs/Markers/showtime/controls/tab_markers_child_control_zone_zoom.py
#
# This file defines the Zone Zoom tab for the ControlsFrame. It contains the
# UI for adjusting the span based on the selected zone, group, or device.
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
# Version 20250820.232600.1
# ADDED: Added `set_zone_zoom_labels` and `get_current_buffer` methods to manage internal state.
# FIXED: The `AttributeError: 'ZoneZoomTab' object has no attribute 'buffer_var'` was fixed
#        by correcting the references to use the local instance (`self`) instead of the parent.
# FIXED: The hardcoded notebook tab index was corrected to ensure the Trace tab is found correctly.

current_version = "20250820.232600.1"
current_version_hash = (20250820 * 232600 * 1)

import os
import inspect
import tkinter as tk
from tkinter import ttk

from display.debug_logic import debug_log
from display.console_logic import console_log

from tabs.Markers.showtime.controls.utils_showtime_zone_zoom import (
    set_span_to_zone, set_span_to_group, set_span_to_device, set_span_to_all_markers
)

class ZoneZoomTab(ttk.Frame):
    def __init__(self, parent, controls_frame):
        # [Initializes the Zone Zoom tab and its associated controls.]
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        super().__init__(parent, style='TFrame', padding=5)
        self.controls_frame = controls_frame
        
        # Now defined within this class
        self.buffer_var = tk.StringVar(value="1") 
        self.zone_zoom_label_left_var = tk.StringVar(value="All Markers")
        self.zone_zoom_label_center_var = tk.StringVar(value="Start: N/A")
        self.zone_zoom_label_right_var = tk.StringVar(value="Stop: N/A (0 Markers)")
        self.zone_zoom_buttons = {}

        self._create_widgets()
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def _create_widgets(self):
        # [Creates and lays out the Zone Zoom control widgets.]
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        
        self.columnconfigure((0, 1, 2, 4), weight=1)
        self.columnconfigure(3, weight=0)

        # Labels
        ttk.Label(self, textvariable=self.zone_zoom_label_left_var, anchor="w").grid(row=0, column=0, columnspan=2, pady=2, padx=2, sticky="w")
        ttk.Label(self, textvariable=self.zone_zoom_label_center_var, anchor="e").grid(row=0, column=2, pady=2, padx=2, sticky="e")
        ttk.Label(self, textvariable=self.zone_zoom_label_right_var, anchor="e").grid(row=0, column=3, columnspan=2, pady=2, padx=2, sticky="e")
        
        # Buffer Dropdown
        ttk.Label(self, text="Buffer (MHz):", anchor="w").grid(row=1, column=0, columnspan=2, pady=2, padx=2, sticky="w")
        buffer_options = [1, 3, 10, 30]
        buffer_combobox = ttk.Combobox(self, textvariable=self.buffer_var, values=buffer_options, state="readonly", width=5)
        buffer_combobox.grid(row=1, column=1, columnspan=1, padx=2, pady=2, sticky="ew")

        # Buttons
        btn_all = ttk.Button(self, text="All Markers", style='ControlButton.Inactive.TButton', command=self._on_set_span_to_all_markers_click)
        btn_all.grid(row=2, column=0, padx=2, pady=2, sticky="ew")
        self.zone_zoom_buttons['All'] = btn_all

        btn_zone = ttk.Button(self, text="Zone", style='ControlButton.Inactive.TButton', command=self._on_set_span_to_zone_click)
        btn_zone.grid(row=2, column=1, padx=2, pady=2, sticky="ew")
        self.zone_zoom_buttons['Zone'] = btn_zone

        btn_group = ttk.Button(self, text="Group", style='ControlButton.Inactive.TButton', command=self._on_set_span_to_group_click)
        btn_group.grid(row=2, column=2, padx=2, pady=2, sticky="ew")
        self.zone_zoom_buttons['Group'] = btn_group
        
        ttk.Frame(self, width=20, style='TFrame').grid(row=2, column=3)

        btn_device = ttk.Button(self, text="Device", style='ControlButton.Inactive.TButton', command=self._on_set_span_to_device_click)
        btn_device.grid(row=2, column=4, padx=2, pady=2, sticky="ew")
        self.zone_zoom_buttons['Device'] = btn_device
        
        debug_log(f"Exiting {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

    def set_zone_zoom_labels(self, labels_dict):
        # [Updates the zone zoom labels with new values.]
        debug_log(f"Entering set_zone_zoom_labels with data: {labels_dict}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_zone_zoom_labels")
        self.zone_zoom_label_left_var.set(value=labels_dict.get('left_label', "N/A"))
        self.zone_zoom_label_center_var.set(value=labels_dict.get('center_label', "N/A"))
        self.zone_zoom_label_right_var.set(value=labels_dict.get('right_label', "N/A"))
        debug_log(f"Exiting set_zone_zoom_labels.", file=f"{os.path.basename(__file__)}", version=current_version, function="set_zone_zoom_labels")

    def get_current_buffer(self):
        # [Returns the current buffer value.]
        debug_log(f"Entering get_current_buffer", file=f"{os.path.basename(__file__)}", version=current_version, function="get_current_buffer")
        return self.buffer_var.get()
    
    def _on_set_span_to_zone_click(self):
        # [Handles the click event to set the instrument span to the selected zone.]
        debug_log(f"Entering _on_set_span_to_zone_click", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_set_span_to_zone_click")
        zgd_frame = self.controls_frame._get_zgd_frame()
        if not zgd_frame or not zgd_frame.selected_zone:
            self.controls_frame.console_print_func("⚠️ No zone selected.")
            return
        
        devices = zgd_frame._get_all_devices_in_zone(zgd_frame.structured_data, zgd_frame.selected_zone)
        freqs = [d.get('CENTER') for d in devices if d.get('CENTER')]
        
        if not freqs:
            self.controls_frame.console_print_func("⚠️ Selected zone has no markers with frequencies.")
            return
            
        set_span_to_zone(self, ZoneName=zgd_frame.selected_zone, NumberOfMarkers=len(freqs),
                         StartFreq=min(freqs), StopFreq=max(freqs), selected=True, buffer_mhz=float(self.buffer_var.get()))
        
        # When a zone is selected, trigger a trace action in the new TracesTab
        traces_tab = self.controls_frame.controls_notebook.nametowidget(self.controls_frame.controls_notebook.tabs()[3])
        if hasattr(traces_tab, '_execute_selected_trace_action'):
            traces_tab._execute_selected_trace_action()
        self._update_zone_zoom_button_styles()

    def _on_set_span_to_group_click(self):
        # [Handles the click event to set the instrument span to the selected group.]
        debug_log(f"Entering _on_set_span_to_group_click", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_set_span_to_group_click")
        zgd_frame = self.controls_frame._get_zgd_frame()
        if not zgd_frame or not zgd_frame.selected_group:
            self.controls_frame.console_print_func("⚠️ No group selected.")
            return
            
        devices = zgd_frame.structured_data.get(zgd_frame.selected_zone, {}).get(zgd_frame.selected_group, [])
        freqs = [d.get('CENTER') for d in devices if d.get('CENTER')]

        if not freqs:
            self.controls_frame.console_print_func("⚠️ Selected group has no markers with frequencies.")
            return
            
        set_span_to_group(self, GroupName=zgd_frame.selected_group, NumberOfMarkers=len(freqs),
                          StartFreq=min(freqs), StopFreq=max(freqs), buffer_mhz=float(self.buffer_var.get()))
        
        # When a group is selected, trigger a trace action in the new TracesTab
        traces_tab = self.controls_frame.controls_notebook.nametowidget(self.controls_frame.controls_notebook.tabs()[3])
        if hasattr(traces_tab, '_execute_selected_trace_action'):
            traces_tab._execute_selected_trace_action()
        self._update_zone_zoom_button_styles()

    def _on_set_span_to_device_click(self):
        # [Handles the click event to set the instrument span to the selected device.]
        debug_log(f"Entering _on_set_span_to_device_click", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_set_span_to_device_click")
        zgd_frame = self.controls_frame._get_zgd_frame()
        if not zgd_frame or not hasattr(zgd_frame, 'selected_device_info') or not zgd_frame.selected_device_info:
            self.controls_frame.console_print_func("⚠️ No device selected.")
            return
            
        device_info = zgd_frame.selected_device_info
        device_name = device_info.get('NAME', 'N/A')
        center_freq = device_info.get('CENTER')

        if not center_freq:
            self.controls_frame.console_print_func("⚠️ Selected device has no frequency.")
            return
            
        set_span_to_device(self, DeviceName=device_name, CenterFreq=center_freq)
        
        # When a device is selected, trigger a trace action in the new TracesTab
        traces_tab = self.controls_frame.controls_notebook.nametowidget(self.controls_frame.controls_notebook.tabs()[3])
        if hasattr(traces_tab, '_execute_selected_trace_action'):
            traces_tab._execute_selected_trace_action()
        self._update_zone_zoom_button_styles()

    def _on_set_span_to_all_markers_click(self):
        # [Handles the click event to set the instrument span to all loaded markers.]
        debug_log(f"Entering _on_set_span_to_all_markers_click", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_set_span_to_all_markers_click")
        zgd_frame = self.controls_frame._get_zgd_frame()
        if not zgd_frame:
            return
            
        all_devices = zgd_frame._get_all_devices_in_zone(zgd_frame.structured_data, zone_name=None)
        freqs = [d.get('CENTER') for d in all_devices if d.get('CENTER')]

        if not freqs:
            self.controls_frame.console_print_func("⚠️ No markers loaded.")
            return

        set_span_to_all_markers(self, NumberOfMarkers=len(freqs), StartFreq=min(freqs),\
                                StopFreq=max(freqs), selected=True, buffer_mhz=float(self.buffer_var.get()))
        
        # When all markers are selected, trigger a trace action in the new TracesTab
        traces_tab = self.controls_frame.controls_notebook.nametowidget(self.controls_frame.controls_notebook.tabs()[3])
        if hasattr(traces_tab, '_execute_selected_trace_action'):
            traces_tab._execute_selected_trace_action()
        self._update_zone_zoom_button_styles()

    def _on_tab_selected(self):
        # [Synchronizes the UI elements when the tab is selected.]
        debug_log(f"Entering _on_tab_selected", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_tab_selected")
        self._update_zone_zoom_button_styles()
        debug_log(f"Exiting _on_tab_selected", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_tab_selected")

    def _on_tab_deselected(self):
        # [Performs any necessary cleanup when the tab is deselected.]
        debug_log(f"Entering _on_tab_deselected", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_tab_deselected")
        # No action required at this time.
        pass
        debug_log(f"Exiting _on_tab_deselected", file=f"{os.path.basename(__file__)}", version=current_version, function="_on_tab_deselected")

    def _update_zone_zoom_button_styles(self):
        # [Updates the visual styles of the zone zoom buttons based on current selection.]
        debug_log(f"Entering _update_zone_zoom_button_styles", file=f"{os.path.basename(__file__)}", version=current_version, function="_update_zone_zoom_button_styles")
        active_style = 'ControlButton.Active.TButton'
        inactive_style = 'ControlButton.Inactive.TButton'
        
        try:
            zgd_frame = self.controls_frame._get_zgd_frame()
            if not zgd_frame:
                debug_log("ZGD frame not found, cannot update button styles.", file=f"{os.path.basename(__file__)}", version=current_version, function="_update_zone_zoom_button_styles")
                return

            selected_type = zgd_frame.last_selected_type
            
            # Update 'All Markers' button
            is_all_active = selected_type is None
            self.zone_zoom_buttons['All'].configure(style=active_style if is_all_active else inactive_style)
            
            # Update 'Zone' button
            is_zone_active = selected_type == 'zone'
            self.zone_zoom_buttons['Zone'].configure(style=active_style if is_zone_active else inactive_style)

            # Update 'Group' button
            is_group_active = selected_type == 'group'
            self.zone_zoom_buttons['Group'].configure(style=active_style if is_group_active else inactive_style)
            
            # Update 'Device' button
            is_device_active = selected_type == 'device'
            self.zone_zoom_buttons['Device'].configure(style=active_style if is_device_active else inactive_style)
            
            # Enable/disable buttons based on selection
            self.zone_zoom_buttons['Zone'].configure(state='!disabled' if zgd_frame.selected_zone else 'disabled')
            self.zone_zoom_buttons['Group'].configure(state='!disabled' if zgd_frame.selected_group else 'disabled')
            self.zone_zoom_buttons['Device'].configure(state='!disabled' if zgd_frame.selected_device_info else 'disabled')
            
        except Exception as e:
            debug_log(f"A ghost has possessed the zone zoom buttons! Error: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="_update_zone_zoom_button_styles")