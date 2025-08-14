# tabs/Markers/utils_markers_showtime.py
#
# This utility file provides the core logic for the Showtime tab, handling
# marker data loading, dynamic button creation for zones and groups, and the
# main orchestrated update loop for real-time monitoring.
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
# Version 20250814.153000.1

current_version = "20250814.153000.1"
current_version_hash = (20250814 * 153000 * 1)

import tkinter as tk
from tkinter import ttk
import os
import inspect
import threading
import time

from display.debug_logic import debug_log
from ref.frequency_bands import MHZ_TO_HZ
from tabs.Markers.utils_markers import set_frequency_logic, set_span_logic, set_rbw_logic, set_trace_modes_logic, set_marker_logic
# --- CORRECTED IMPORT ---
from tabs.Markers.utils_markers_file_handling import load_and_process_markers

def orchestrated_update_loop(showtime_tab_instance):
    # [A brief, one-sentence description of the function's purpose.]
    # Manages the main real-time update loop for the Showtime tab, cycling through devices.
    if not showtime_tab_instance.app_instance.orchestrator_logic.is_running or showtime_tab_instance.app_instance.orchestrator_logic.is_paused:
        return

    if not showtime_tab_instance.selected_zone or not showtime_tab_instance.selected_group:
        return

    group_devices = showtime_tab_instance.zones.get(showtime_tab_instance.selected_zone, {}).get(showtime_tab_instance.selected_group, [])
    if not group_devices:
        return

    if showtime_tab_instance.current_chunk_index >= len(group_devices):
        showtime_tab_instance.current_chunk_index = 0

    device_name = group_devices[showtime_tab_instance.current_chunk_index]
    device_info = showtime_tab_instance.markers_data.get(device_name)
    if device_info:
        frequency_hz = int(float(device_info.get('frequency_mhz', 0)) * MHZ_TO_HZ)
        
        with showtime_tab_instance.instrument_lock:
            set_frequency_logic(showtime_tab_instance.app_instance, frequency_hz, showtime_tab_instance.console_print_func)
            
            if showtime_tab_instance.follow_zone_span_var.get():
                zone_info = showtime_tab_instance.zones.get(showtime_tab_instance.selected_zone, {})
                span_hz = zone_info.get('span_hz', int(showtime_tab_instance.span_var.get()))
                set_span_logic(showtime_tab_instance.app_instance, span_hz, showtime_tab_instance.console_print_func)
            else:
                set_span_logic(showtime_tab_instance.app_instance, int(showtime_tab_instance.span_var.get()), showtime_tab_instance.console_print_func)
        
        _update_active_device_button(showtime_tab_instance, device_name)
        
    showtime_tab_instance.current_chunk_index += 1
    showtime_tab_instance.after(2000, lambda: orchestrated_update_loop(showtime_tab_instance))

def format_hz(hz_value):
    # [A brief, one-sentence description of the function's purpose.]
    # Formats a frequency in Hz to a human-readable string.
    try:
        hz_value = float(hz_value)
        if hz_value >= 1_000_000:
            return f"{hz_value / 1_000_000:.1f}M"
        elif hz_value >= 1_000:
            return f"{hz_value / 1_000:.0f}k"
        else:
            return f"{hz_value}Hz"
    except (ValueError, TypeError):
        return "N/A"

def load_markers_data_wrapper(showtime_tab_instance):
    # [A brief, one-sentence description of the function's purpose.]
    # Calls the dedicated CSV handler to load and parse marker data.
    
    # --- CORRECTED FUNCTION CALL ---
    markers_data, zones = load_and_process_markers(showtime_tab_instance.app_instance, showtime_tab_instance.console_print_func)

    if markers_data and zones:
        showtime_tab_instance.markers_data = markers_data
        showtime_tab_instance.zones = zones
        populate_zone_buttons(showtime_tab_instance)
    else:
        showtime_tab_instance.markers_data = {}
        showtime_tab_instance.zones = {}
        populate_zone_buttons(showtime_tab_instance)


def populate_zone_buttons(showtime_tab_instance):
    # [A brief, one-sentence description of the function's purpose.]
    # Creates and displays buttons for each available zone.
    for widget in showtime_tab_instance.zone_button_subframe.winfo_children():
        widget.destroy()
        
    showtime_tab_instance.zone_buttons = {}
    if not showtime_tab_instance.zones:
        ttk.Label(showtime_tab_instance.zone_button_subframe, text="No Zones Found in markers.csv").pack(pady=10)
        return

    for i, zone_name in enumerate(showtime_tab_instance.zones.keys()):
        device_count = sum(len(g) for g_name, g in showtime_tab_instance.zones[zone_name].items() if g_name != 'span_hz')
        btn = ttk.Button(showtime_tab_instance.zone_button_subframe, text=f"{zone_name}\n({device_count})", command=lambda z=zone_name: on_zone_button_click(showtime_tab_instance, z), style='ControlButton.Inactive.TButton')
        btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
        showtime_tab_instance.zone_button_subframe.grid_columnconfigure(i, weight=1)
        showtime_tab_instance.zone_buttons[zone_name] = btn

def on_zone_button_click(showtime_tab_instance, zone_name):
    # [A brief, one-sentence description of the function's purpose.]
    # Handles clicks on zone buttons, updating the selected zone and populating group buttons.
    showtime_tab_instance.selected_zone = zone_name
    showtime_tab_instance.selected_group = None 
    
    for widget in showtime_tab_instance.group_button_subframe.winfo_children():
        widget.destroy()
    
    showtime_tab_instance.group_buttons = {}
    groups = {k: v for k, v in showtime_tab_instance.zones.get(zone_name, {}).items() if k != 'span_hz'}

    if not groups:
        ttk.Label(showtime_tab_instance.group_button_subframe, text="No Groups in this Zone").pack(pady=10)

    for i, group_name in enumerate(groups.keys()):
        device_count = len(groups[group_name])
        btn = ttk.Button(showtime_tab_instance.group_button_subframe, text=f"{group_name}\n({device_count})", command=lambda g=group_name: on_group_button_click(showtime_tab_instance, g), style='ControlButton.Inactive.TButton')
        btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
        showtime_tab_instance.group_button_subframe.grid_columnconfigure(i, weight=1)
        showtime_tab_instance.group_buttons[group_name] = btn
        
    _update_control_styles(showtime_tab_instance)
    orchestrated_update_loop(showtime_tab_instance)

def on_group_button_click(showtime_tab_instance, group_name):
    # [A brief, one-sentence description of the function's purpose.]
    # Handles clicks on group buttons, updating the selected group and displaying devices.
    showtime_tab_instance.selected_group = group_name
    showtime_tab_instance.current_chunk_index = 0
    
    for widget in showtime_tab_instance.device_buttons_frame.winfo_children():
        widget.destroy()
    
    showtime_tab_instance.device_buttons = {}
    devices = showtime_tab_instance.zones.get(showtime_tab_instance.selected_zone, {}).get(group_name, [])
    
    if not devices:
        ttk.Label(showtime_tab_instance.device_buttons_frame, text="No Devices in this Group").pack(pady=10)

    for device_name in devices:
        device_info = showtime_tab_instance.markers_data.get(device_name, {})
        freq_mhz = device_info.get('frequency_mhz', 'N/A')
        btn = ttk.Button(showtime_tab_instance.device_buttons_frame, text=f"{device_name}\n{freq_mhz} MHz", style='DeviceButton.Inactive.TButton')
        btn.pack(fill='x', padx=5, pady=2)
        showtime_tab_instance.device_buttons[device_name] = btn
        
    _update_control_styles(showtime_tab_instance)
    orchestrated_update_loop(showtime_tab_instance)

def _update_active_device_button(showtime_tab_instance, active_device_name):
    # [A brief, one-sentence description of the function's purpose.]
    # Highlights the currently active device button and resets others.
    for name, button in showtime_tab_instance.device_buttons.items():
        if name == active_device_name:
            button.configure(style='DeviceButton.Active.TButton')
        else:
            button.configure(style='DeviceButton.Inactive.TButton')

def _update_control_styles(showtime_tab_instance):
    # [A brief, one-sentence description of the function's purpose.]
    # Updates the visual styles of all control buttons based on the current state.
    
    active_style = 'ControlButton.Active.TButton'
    inactive_style = 'ControlButton.Inactive.TButton'

    for name, btn in showtime_tab_instance.zone_buttons.items():
        btn.configure(style=active_style if name == showtime_tab_instance.selected_zone else inactive_style)
        
    if hasattr(showtime_tab_instance, 'group_buttons'):
        for name, btn in showtime_tab_instance.group_buttons.items():
            btn.configure(style=active_style if name == showtime_tab_instance.selected_group else inactive_style)
    
    if 'Follow' in showtime_tab_instance.span_buttons:
        showtime_tab_instance.span_buttons['Follow'].configure(style=active_style if showtime_tab_instance.follow_zone_span_var.get() else inactive_style)
    
    for span_val, btn in showtime_tab_instance.span_buttons.items():
        if span_val != 'Follow':
            is_active = (str(span_val) == showtime_tab_instance.span_var.get()) and not showtime_tab_instance.follow_zone_span_var.get()
            btn.configure(style=active_style if is_active else inactive_style)
            
    for rbw_val, btn in showtime_tab_instance.rbw_buttons.items():
        btn.configure(style=active_style if str(rbw_val) == showtime_tab_instance.rbw_var.get() else inactive_style)

    showtime_tab_instance.trace_buttons['Live'].configure(style=active_style if showtime_tab_instance.trace_live_mode.get() else inactive_style)
    showtime_tab_instance.trace_buttons['Max Hold'].configure(style=active_style if showtime_tab_instance.trace_max_hold_mode.get() else inactive_style)
    showtime_tab_instance.trace_buttons['Min Hold'].configure(style=active_style if showtime_tab_instance.trace_min_hold_mode.get() else inactive_style)

def on_span_button_click(showtime_tab_instance, span_hz):
    # [A brief, one-sentence description of the function's purpose.]
    # Handles clicks on span buttons, setting the instrument span.
    if span_hz == 'Follow':
        showtime_tab_instance.follow_zone_span_var.set(True)
    else:
        showtime_tab_instance.follow_zone_span_var.set(False)
        showtime_tab_instance.span_var.set(str(span_hz))
    _update_control_styles(showtime_tab_instance)

def on_rbw_button_click(showtime_tab_instance, rbw_hz):
    # [A brief, one-sentence description of the function's purpose.]
    # Handles clicks on RBW buttons, setting the instrument's resolution bandwidth.
    showtime_tab_instance.rbw_var.set(str(rbw_hz))
    set_rbw_logic(showtime_tab_instance.app_instance, int(rbw_hz), showtime_tab_instance.console_print_func)
    _update_control_styles(showtime_tab_instance)

def on_trace_button_click(showtime_tab_instance, trace_var):
    # [A brief, one-sentence description of the function's purpose.]
    # Toggles the state of a trace mode (Live, Max Hold, Min Hold).
    trace_var.set(not trace_var.get())
    set_trace_modes_logic(showtime_tab_instance.app_instance, 
                          showtime_tab_instance.trace_live_mode.get(),
                          showtime_tab_instance.trace_max_hold_mode.get(),
                          showtime_tab_instance.trace_min_hold_mode.get(),
                          showtime_tab_instance.console_print_func)
    _update_control_styles(showtime_tab_instance)

def on_poke_action(showtime_tab_instance):
    # [A brief, one-sentence description of the function's purpose.]
    # Sets a marker at the frequency specified in the "Poke" entry field.
    try:
        freq_mhz = float(showtime_tab_instance.poke_freq_var.get())
        freq_hz = int(freq_mhz * MHZ_TO_HZ)
        set_marker_logic(showtime_tab_instance.app_instance, freq_hz, showtime_tab_instance.console_print_func)
        showtime_tab_instance.console_print_func(f"Poked frequency: {freq_mhz} MHz", "INFO")
    except ValueError:
        showtime_tab_instance.console_print_func("Invalid frequency for Poke action. Please enter a number.", "ERROR")