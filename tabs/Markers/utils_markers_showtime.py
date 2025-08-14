# tabs/Markers/utils_markers_showtime.py
#
# This file provides utility functions for the ShowtimeTab.
# All complex logic related to button actions, data processing, and instrument
# control has been moved here. This version ties all automatic updates to the
# state of the main application Orchestrator.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
#
#
# Version 20250814.011320.2

current_version = "20250814.011320.2"

import tkinter as tk
from tkinter import ttk
import os
import csv
import inspect
import pandas as pd
import threading
import time
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log
from display.utils_display_monitor import update_top_plot, update_medium_plot, update_bottom_plot

# Import the utility functions for markers
from tabs.Markers.utils_marker_peaks import get_peak_values_and_update_csv
from tabs.Markers.utils_markers_get_traces import get_marker_traces
from tabs.Markers.utils_markers import (
    SPAN_OPTIONS,
    RBW_OPTIONS,
    set_span_logic,
    set_frequency_logic,
    set_trace_modes_logic,
    set_marker_logic,
    set_rbw_logic
)
from tabs.Markers.utils_markers_file_handling import load_markers_data, _group_by_zone_and_group

from src.program_style import COLOR_PALETTE
from src.settings_and_config.config_manager import save_config
from ref.frequency_bands import MHZ_TO_HZ


def orchestrated_update_loop(showtime_tab_instance):
    """
    The new main update loop, driven by the Orchestrator's state.
    This function continuously checks for peaks or traces based on the current selection
    (Zone/Group vs. single Device) as long as the orchestrator is running.
    """
    if not showtime_tab_instance.app_instance.orchestrator_gui.is_running:
        showtime_tab_instance.after(500, lambda: orchestrated_update_loop(showtime_tab_instance))
        return

    if showtime_tab_instance.app_instance.orchestrator_gui.is_paused:
        showtime_tab_instance.after(500, lambda: orchestrated_update_loop(showtime_tab_instance))
        return

    # --- Main Logic ---
    if showtime_tab_instance.selected_device_freq is not None:
        # --- DEVICE MODE ---
        center_freq_hz = showtime_tab_instance.selected_device_freq
        span_hz = float(showtime_tab_instance.span_var.get())
        device_name = showtime_tab_instance.selected_device_name

        with showtime_tab_instance.instrument_lock:
            get_marker_traces(app_instance=showtime_tab_instance.app_instance,
                              showtime_tab_instance=showtime_tab_instance,
                              console_print_func=showtime_tab_instance.console_print_func,
                              center_freq_hz=center_freq_hz,
                              span_hz=span_hz,
                              device_name=device_name)

    elif showtime_tab_instance.selected_zone is not None:
        # --- ZONE/GROUP MODE ---
        devices_to_process = pd.DataFrame()
        name = ""
        if showtime_tab_instance.selected_group:
            name = f"Group: {showtime_tab_instance.selected_group}"
            devices_to_process = showtime_tab_instance.markers_data[
                (showtime_tab_instance.markers_data['ZONE'] == showtime_tab_instance.selected_zone) &
                (showtime_tab_instance.markers_data['GROUP'] == showtime_tab_instance.selected_group)
            ]
        else:
            name = f"Zone: {showtime_tab_instance.selected_zone}"
            devices_to_process = showtime_tab_instance.markers_data[
                showtime_tab_instance.markers_data['ZONE'] == showtime_tab_instance.selected_zone
            ]

        if not devices_to_process.empty:
            # This now runs in a thread that will iteratively update the UI
            _peak_search_and_get_trace(showtime_tab_instance, devices=devices_to_process, name=name)

    # Schedule the next iteration of the loop
    showtime_tab_instance.after(1000, lambda: orchestrated_update_loop(showtime_tab_instance)) # Increased delay for stability


def format_hz(hz_val):
    """Formats a frequency in Hz to a human-readable string in MHz or kHz."""
    try:
        hz = float(hz_val)
        if hz >= MHZ_TO_HZ:
            return f"{hz / MHZ_TO_HZ:.1f}".replace('.0', '') + " MHz"
        elif hz >= 1000:
            return f"{hz / 1000:.1f}".replace('.0', '') + " kHz"
        else:
            return f"{hz} Hz"
    except (ValueError, TypeError):
        return "N/A"

def load_markers_data_wrapper(showtime_tab_instance):
    """
    Wrapper function to call the new utility function and handle the GUI update.
    """
    markers_data, status, message = load_markers_data(showtime_tab_instance.app_instance, showtime_tab_instance.console_print_func)
    showtime_tab_instance.console_print_func(message)
    showtime_tab_instance.markers_data = markers_data
    showtime_tab_instance.zones = _group_by_zone_and_group(markers_data)


def _group_by_zone_and_group(data):
    """Groups marker data by zone and then by group."""
    if data.empty:
        return {}
    data['GROUP'] = data['GROUP'].fillna('No Group')
    zones = {}
    for zone, zone_data in data.groupby('ZONE'):
        groups = {group: group_data.to_dict('records') for group, group_data in zone_data.groupby('GROUP')}
        zones[zone] = groups
    return zones

def populate_zone_buttons(showtime_tab_instance):
    for widget in showtime_tab_instance.zone_button_subframe.winfo_children():
        widget.destroy()
    showtime_tab_instance.zone_buttons = {}
    if not isinstance(showtime_tab_instance.zones, dict) or not showtime_tab_instance.zones:
        ttk.Label(showtime_tab_instance.zone_button_subframe, text="No zones found in MARKERS.CSV.").grid(row=0, column=0, columnspan=8)
        return
    max_cols = 8
    for i, zone_name in enumerate(sorted(showtime_tab_instance.zones.keys())):
        row = i // max_cols
        col = i % max_cols
        device_count = sum(len(group) for group in showtime_tab_instance.zones[zone_name].values())
        btn = ttk.Button(showtime_tab_instance.zone_button_subframe,
                         text=f"{zone_name} ({device_count})",
                         command=lambda z=zone_name: on_zone_button_click(showtime_tab_instance, z))
        btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
        showtime_tab_instance.zone_buttons[zone_name] = btn
    _update_zone_button_styles(showtime_tab_instance)

def populate_group_buttons(showtime_tab_instance):
    for widget in showtime_tab_instance.group_button_subframe.winfo_children():
        widget.destroy()
    showtime_tab_instance.group_buttons = {}
    if not showtime_tab_instance.selected_zone or showtime_tab_instance.selected_zone not in showtime_tab_instance.zones:
        showtime_tab_instance.group_buttons_frame.grid_remove()
        return
    groups = showtime_tab_instance.zones[showtime_tab_instance.selected_zone]
    if not groups:
        showtime_tab_instance.group_buttons_frame.grid_remove()
        return
    showtime_tab_instance.group_buttons_frame.grid()
    max_cols = 8
    for i, group_name in enumerate(sorted(groups.keys())):
        row = i // max_cols
        col = i % max_cols
        device_count = len(groups[group_name])
        btn = ttk.Button(showtime_tab_instance.group_button_subframe,
                         text=f"{group_name} ({device_count})",
                         command=lambda g=group_name: on_group_button_click(showtime_tab_instance, g))
        btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
        showtime_tab_instance.group_buttons[group_name] = btn
    _update_group_button_styles(showtime_tab_instance)

def on_zone_button_click(showtime_tab_instance, zone_name):
    showtime_tab_instance.selected_zone = zone_name
    showtime_tab_instance.selected_group = None
    showtime_tab_instance.selected_device_freq = None
    _update_zone_button_styles(showtime_tab_instance)
    showtime_tab_instance.follow_zone_span_var.set(True)
    _update_control_styles(showtime_tab_instance)
    populate_group_buttons(showtime_tab_instance)
    populate_device_buttons(showtime_tab_instance)
    _update_group_button_styles(showtime_tab_instance)

def on_group_button_click(showtime_tab_instance, group_name):
    showtime_tab_instance.selected_group = group_name
    showtime_tab_instance.selected_device_freq = None
    _update_group_button_styles(showtime_tab_instance)
    showtime_tab_instance.follow_zone_span_var.set(True)
    _update_control_styles(showtime_tab_instance)
    populate_device_buttons(showtime_tab_instance)

def _peak_search_and_get_trace(showtime_tab_instance, devices, name):
    if not showtime_tab_instance.app_instance.inst or devices.empty:
        showtime_tab_instance.console_print_func("❌ Cannot perform peak search: no instrument connected or no devices selected.")
        return
    threading.Thread(target=_perform_peak_search_task, args=(showtime_tab_instance, devices, name), daemon=True).start()

def _perform_peak_search_task(showtime_tab_instance, devices, name):
    """
    REFACTORED: Worker function for the peak search task.
    This now loops through devices in chunks of 6, updating the UI after each chunk.
    """
    for i in range(0, len(devices), 6):
        if not showtime_tab_instance.app_instance.orchestrator_gui.is_running:
            showtime_tab_instance.console_print_func("ℹ️ Orchestrator stopped. Halting peak search loop.")
            break

        while showtime_tab_instance.app_instance.orchestrator_gui.is_paused:
            time.sleep(0.5) # Wait if paused

        chunk = devices.iloc[i:i+6]
        
        with showtime_tab_instance.instrument_lock:
            updated_markers_df = get_peak_values_and_update_csv(
                app_instance=showtime_tab_instance.app_instance,
                devices_to_process=chunk,
                console_print_func=showtime_tab_instance.console_print_func
            )

        if updated_markers_df is None:
            showtime_tab_instance.app_instance.after(0, lambda: showtime_tab_instance.console_print_func(f"❌ Peak search failed for chunk starting at index {i}."))
            continue # Try next chunk

        # After each chunk, schedule a UI update on the main thread
        def update_ui_after_chunk():
            load_markers_data_wrapper(showtime_tab_instance)
            populate_device_buttons(showtime_tab_instance)
            
            # Also update the trace to show the latest state of the whole group/zone
            all_freqs_mhz = devices['FREQ'].dropna().tolist()
            if not all_freqs_mhz: return
            
            min_freq_mhz = min(all_freqs_mhz)
            max_freq_mhz = max(all_freqs_mhz)
            span_mhz = max_freq_mhz - min_freq_mhz
            center_freq_mhz = (min_freq_mhz + max_freq_mhz) / 2
            
            center_freq_hz = int(center_freq_mhz * MHZ_TO_HZ)
            span_hz = int(span_mhz * MHZ_TO_HZ) if span_mhz > 0 else int(0.1 * MHZ_TO_HZ)
            
            with showtime_tab_instance.instrument_lock:
                get_marker_traces(
                    app_instance=showtime_tab_instance.app_instance,
                    showtime_tab_instance=showtime_tab_instance,
                    console_print_func=showtime_tab_instance.console_print_func,
                    center_freq_hz=center_freq_hz,
                    span_hz=span_hz,
                    device_name=name
                )
        
        showtime_tab_instance.app_instance.after(0, update_ui_after_chunk)
        time.sleep(0.2) # Small delay to prevent overwhelming the instrument and allow UI to respond

    showtime_tab_instance.app_instance.after(0, lambda: showtime_tab_instance.console_print_func("✅ Peak search cycle complete for all devices."))


def _update_zone_button_styles(showtime_tab_instance):
    for zone_name, btn in showtime_tab_instance.zone_buttons.items():
        if btn.winfo_exists():
            btn.config(style='SelectedPreset.Orange.TButton' if zone_name == showtime_tab_instance.selected_zone else 'LocalPreset.TButton')

def _update_group_button_styles(showtime_tab_instance):
    for group_name, btn in showtime_tab_instance.group_buttons.items():
        if btn.winfo_exists():
            btn.config(style='SelectedPreset.Orange.TButton' if group_name == showtime_tab_instance.selected_group else 'LocalPreset.TButton')

def populate_device_buttons(showtime_tab_instance):
    for widget in showtime_tab_instance.device_buttons_frame.winfo_children():
        widget.destroy()
    showtime_tab_instance.device_buttons = {}
    if not showtime_tab_instance.selected_zone:
        ttk.Label(showtime_tab_instance.device_buttons_frame, text="Select a zone/group.").grid()
        return
    devices = []
    if showtime_tab_instance.selected_group:
        devices = showtime_tab_instance.zones[showtime_tab_instance.selected_zone].get(showtime_tab_instance.selected_group, [])
    else:
        for group_data in showtime_tab_instance.zones[showtime_tab_instance.selected_zone].values():
            devices.extend(group_data)
    if not devices:
        ttk.Label(showtime_tab_instance.device_buttons_frame, text="No devices found.").grid()
        return
    for i, device in enumerate(devices):
        device_name = device.get('NAME', 'N/A')
        peak_value = device.get('Peak', None)
        style = 'LocalPreset.TButton'
        if pd.notna(peak_value) and peak_value != '':
            peak_value = float(peak_value)
            if -80 > peak_value >= -130: style = 'Red.TButton'
            elif -50 > peak_value >= -80: style = 'Orange.TButton'
            elif peak_value >= -50: style = 'Green.TButton'
            progress_bar = _create_progress_bar_text(peak_value)
            text = f"{device_name}\n{device.get('FREQ', 'N/A')} MHz\nPeak: {peak_value:.2f} dBm\n{progress_bar}"
        else:
            text = f"{device_name}\n{device.get('FREQ', 'N/A')} MHz\nPeak: N/A"
        btn = ttk.Button(showtime_tab_instance.device_buttons_frame, text=text, style=style,
                         command=lambda d=device: on_device_button_click(showtime_tab_instance, d))
        btn.grid(row=i // 4, column=i % 4, padx=5, pady=5, sticky="nsew")
        showtime_tab_instance.device_buttons[device_name] = btn

def _create_progress_bar_text(peak_value):
    if pd.isna(peak_value): return "[                        ]"
    min_dbm, max_dbm = -120.0, 0.0
    clamped_value = max(min_dbm, min(max_dbm, peak_value))
    num_filled_chars = int((clamped_value - min_dbm) / (max_dbm - min_dbm) * 24)
    return f"[{'█' * num_filled_chars}{' ' * (24 - num_filled_chars)}]"

def on_device_button_click(showtime_tab_instance, device_data):
    try:
        freq_mhz = device_data.get('FREQ', 'N/A')
        device_name = device_data.get('NAME', 'N/A')
        zone_name = device_data.get('ZONE', 'N/A')
        group_name = device_data.get('GROUP', 'N/A')
        showtime_tab_instance.selected_device_name = f"{zone_name}/{group_name}/{device_name}" if group_name and group_name != 'No Group' else f"{zone_name}/{device_name}"
        showtime_tab_instance.selected_device_freq = float(freq_mhz) * MHZ_TO_HZ
        showtime_tab_instance.follow_zone_span_var.set(False)
        _update_control_styles(showtime_tab_instance)
        if showtime_tab_instance.app_instance.inst:
            with showtime_tab_instance.instrument_lock:
                status_span, message_span = set_span_logic(app_instance=showtime_tab_instance.app_instance, span_hz=float(showtime_tab_instance.span_var.get()), console_print_func=showtime_tab_instance.console_print_func)
                showtime_tab_instance.console_print_func(message_span)
                status_freq, message_freq = set_frequency_logic(app_instance=showtime_tab_instance.app_instance, frequency_hz=showtime_tab_instance.selected_device_freq, console_print_func=showtime_tab_instance.console_print_func)
                showtime_tab_instance.console_print_func(message_freq)
                status_marker, message_marker = set_marker_logic(app_instance=showtime_tab_instance.app_instance, frequency_hz=showtime_tab_instance.selected_device_freq, console_print_func=showtime_tab_instance.console_print_func)
                showtime_tab_instance.console_print_func(message_marker)
    except (ValueError, TypeError) as e:
        showtime_tab_instance.console_print_func(f"❌ Error setting frequency on device click: {e}")

def _update_control_styles(showtime_tab_instance):
    if showtime_tab_instance.follow_zone_span_var.get():
        showtime_tab_instance.span_buttons['Follow'].configure(style='ControlButton.Active.TButton')
        for span_val, button in showtime_tab_instance.span_buttons.items():
            if span_val != 'Follow' and button.winfo_exists():
                button.configure(style='ControlButton.Inactive.TButton')
    else:
        showtime_tab_instance.span_buttons['Follow'].configure(style='ControlButton.Inactive.TButton')
        current_span_str = showtime_tab_instance.span_var.get()
        for span_val, button in showtime_tab_instance.span_buttons.items():
            if span_val != 'Follow' and button.winfo_exists():
                style = 'ControlButton.Active.TButton' if float(span_val) == float(current_span_str) else 'ControlButton.Inactive.TButton'
                button.configure(style=style)
    current_rbw_str = showtime_tab_instance.rbw_var.get()
    for rbw_val, button in showtime_tab_instance.rbw_buttons.items():
        if button.winfo_exists():
            button.configure(style='ControlButton.Active.TButton' if float(rbw_val) == float(current_rbw_str) else 'ControlButton.Inactive.TButton')
    for name, var in [("Live", showtime_tab_instance.trace_live_mode), ("Max Hold", showtime_tab_instance.trace_max_hold_mode), ("Min Hold", showtime_tab_instance.trace_min_hold_mode)]:
        if name in showtime_tab_instance.trace_buttons and showtime_tab_instance.trace_buttons[name].winfo_exists():
            showtime_tab_instance.trace_buttons[name].configure(style='ControlButton.Active.TButton' if var.get() else 'ControlButton.Inactive.TButton')

def on_span_button_click(showtime_tab_instance, span_hz):
    if span_hz == 'Follow':
        showtime_tab_instance.follow_zone_span_var.set(True)
    else:
        showtime_tab_instance.follow_zone_span_var.set(False)
        showtime_tab_instance.span_var.set(str(span_hz))
    _update_control_styles(showtime_tab_instance)
    if showtime_tab_instance.app_instance and showtime_tab_instance.app_instance.inst:
        if not showtime_tab_instance.follow_zone_span_var.get():
            try:
                with showtime_tab_instance.instrument_lock:
                    status, message = set_span_logic(app_instance=showtime_tab_instance.app_instance, span_hz=float(span_hz), console_print_func=showtime_tab_instance.console_print_func)
                    showtime_tab_instance.console_print_func(message)
            except (ValueError, TypeError) as e:
                 debug_log(f"Span logic error: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function=inspect.currentframe().f_code.co_name)
    save_config(config=showtime_tab_instance.app_instance.config, file_path=showtime_tab_instance.app_instance.CONFIG_FILE_PATH, console_print_func=showtime_tab_instance.console_print_func, app_instance=showtime_tab_instance.app_instance)

def on_rbw_button_click(showtime_tab_instance, rbw_hz):
    showtime_tab_instance.rbw_var.set(str(rbw_hz))
    _update_control_styles(showtime_tab_instance)
    if showtime_tab_instance.app_instance and showtime_tab_instance.app_instance.inst:
        try:
            with showtime_tab_instance.instrument_lock:
                status, message = set_rbw_logic(app_instance=showtime_tab_instance.app_instance, rbw_hz=float(rbw_hz), console_print_func=showtime_tab_instance.console_print_func)
                showtime_tab_instance.console_print_func(message)
        except (ValueError, TypeError) as e:
            debug_log(f"RBW logic error: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function=inspect.currentframe().f_code.co_name)
    save_config(config=showtime_tab_instance.app_instance.config, file_path=showtime_tab_instance.app_instance.CONFIG_FILE_PATH, console_print_func=showtime_tab_instance.console_print_func, app_instance=showtime_tab_instance.app_instance)

def on_trace_button_click(showtime_tab_instance, trace_var):
    trace_var.set(not trace_var.get())
    _update_control_styles(showtime_tab_instance)
    if showtime_tab_instance.app_instance and showtime_tab_instance.app_instance.inst:
        with showtime_tab_instance.instrument_lock:
            status, message = set_trace_modes_logic(app_instance=showtime_tab_instance.app_instance, live_mode=showtime_tab_instance.trace_live_mode.get(), max_hold_mode=showtime_tab_instance.trace_max_hold_mode.get(), min_hold_mode=showtime_tab_instance.trace_min_hold_mode.get(), console_print_func=showtime_tab_instance.console_print_func)
            showtime_tab_instance.console_print_func(message)
    save_config(config=showtime_tab_instance.app_instance.config, file_path=showtime_tab_instance.app_instance.CONFIG_FILE_PATH, console_print_func=showtime_tab_instance.console_print_func, app_instance=showtime_tab_instance.app_instance)

def on_poke_action(showtime_tab_instance):
    if showtime_tab_instance.app_instance and showtime_tab_instance.app_instance.inst:
        try:
            freq_mhz = showtime_tab_instance.poke_freq_var.get()
            freq_hz = float(freq_mhz) * MHZ_TO_HZ
            poke_marker_name = f"POKE: {freq_mhz} MHz"
            span_hz = float(showtime_tab_instance.span_var.get())

            with showtime_tab_instance.instrument_lock:
                status_span, message_span = set_span_logic(showtime_tab_instance.app_instance, span_hz, showtime_tab_instance.console_print_func)
                showtime_tab_instance.console_print_func(message_span)
                status_trace, message_trace = set_trace_modes_logic(showtime_tab_instance.app_instance, showtime_tab_instance.trace_live_mode.get(), showtime_tab_instance.trace_max_hold_mode.get(), showtime_tab_instance.trace_min_hold_mode.get(), showtime_tab_instance.console_print_func)
                showtime_tab_instance.console_print_func(message_trace)
                status_freq, message_freq = set_frequency_logic(showtime_tab_instance.app_instance, freq_hz, showtime_tab_instance.console_print_func)
                showtime_tab_instance.console_print_func(message_freq)
                status_marker, message_marker = set_marker_logic(app_instance=showtime_tab_instance.app_instance, frequency_hz=showtime_tab_instance.selected_device_freq, console_print_func=showtime_tab_instance.console_print_func)
                showtime_tab_instance.console_print_func(message_marker)

            showtime_tab_instance.selected_device_name = poke_marker_name
            showtime_tab_instance.selected_device_freq = freq_hz

        except (ValueError, TypeError) as e:
            showtime_tab_instance.console_print_func(f"❌ Invalid POKE frequency: {e}")