# tabs/Markers/showtime/controls/utils_showtime_controls.py
#
# This utility file provides the backend logic for the ControlsFrame. It contains
# functions that handle button clicks for Span, RBW, Trace Modes, and Poking,
# and then communicates with the instrument control layer.
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
# Version 20250819.133300.2
# REFACTORED: Moved all trace acquisition and plotting logic to a new file, utils_showtime_trace.py.
# MODIFIED: The `_update_zone_zoom_button_styles` function now calls the new `execute_trace_action` function after setting the span.
# FIXED: This fixes the bug where traces were not automatically captured after a zone zoom change.

current_version = "20250819.133300.2"
current_version_hash = (20250819 * 133300 * 2)

import os
import inspect
import pandas as pd
from ref.frequency_bands import MHZ_TO_HZ
from display.debug_logic import debug_log
from display.console_logic import console_log
from yak.Yakety_Yak import YakSet

# NEW: Import the new utility file containing trace logic
from tabs.Markers.showtime.controls.utils_showtime_trace import execute_trace_action

# MODIFIED: Removed now-relocated handlers
from yak.utils_yakbeg_handler import handle_trace_modes_beg, handle_freq_center_span_beg, handle_trace_data_beg
# REMOVED: from yak.utils_yaknab_handler import handle_all_traces_nab
# REMOVED: from display.utils_display_monitor import update_top_plot, update_middle_plot, update_bottom_plot
# REMOVED: from display.utils_scan_view import update_single_plot

# Import the Zone Zoom functions to be called automatically
from tabs.Markers.showtime.controls.utils_showtime_zone_zoom import (
    set_span_to_all_markers, set_span_to_zone, set_span_to_group, set_span_to_device
)

# --- UI Constants ---
SPAN_OPTIONS = {
    "Ultra Wide": 100 * MHZ_TO_HZ,
    "Wide": 10 * MHZ_TO_HZ,
    "Normal": 1 * MHZ_TO_HZ,
    "Tight": 100 * 1000,
    "Microscope": 10 * 1000,
}

RBW_OPTIONS = {
    "Fast": 1 * MHZ_TO_HZ,
    "Brisk": 300 * 1000,
    "Deliberate": 100 * 1000,
    "Steady": 30 * 1000,
    "Leisurely": 3 * 1000,
    "Unhurried": 1 * 1000,
}

def format_hz(hz_value):
    # [Formats a frequency in Hz to a human-readable string.]
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

def _update_control_styles(controls_frame):
    # [Updates the visual styles of all control buttons based on the current state.]
    debug_log(f"Entering _update_control_styles", file=f"{os.path.basename(__file__)}", version=current_version, function="_update_control_styles")
    try:
        active_style = 'ControlButton.Active.TButton'
        inactive_style = 'ControlButton.Inactive.TButton'

        follow_style = active_style if controls_frame.follow_zone_span_var.get() else inactive_style
        if 'Follow' in controls_frame.span_buttons:
            controls_frame.span_buttons['Follow'].configure(style=follow_style)
        
        for span_val_str, btn in controls_frame.span_buttons.items():
            if span_val_str != 'Follow':
                is_active = (span_val_str == controls_frame.span_var.get()) and not controls_frame.follow_zone_span_var.get()
                btn.configure(style=active_style if is_active else inactive_style)
                
        for rbw_val_str, btn in controls_frame.rbw_buttons.items():
            btn.configure(style=active_style if rbw_val_str == controls_frame.rbw_var.get() else inactive_style)

        controls_frame.trace_buttons['Live'].configure(style=active_style if controls_frame.trace_live_mode.get() else inactive_style)
        controls_frame.trace_buttons['Max Hold'].configure(style=active_style if controls_frame.trace_max_hold_mode.get() else inactive_style)
        controls_frame.trace_buttons['Min Hold'].configure(style=active_style if controls_frame.trace_min_hold_mode.get() else inactive_style)
        
        _update_zone_zoom_button_styles(controls_frame)
    except Exception as e:
        console_log(f"❌ Error in _update_control_styles: {e}")
        debug_log(f"My creation! It refuses to be styled! The error is: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="_update_control_styles")

def _update_zone_zoom_button_styles(controls_frame):
    # [Updates Zone Zoom buttons, labels, AND automatically triggers the instrument span update.]
    debug_log(f"Entering _update_zone_zoom_button_styles to update styles and trigger span.",
              file=f"{os.path.basename(__file__)}", version=current_version, function="_update_zone_zoom_button_styles")
              
    try:
        active_style = 'ControlButton.Active.TButton'
        inactive_style = 'ControlButton.Inactive.TButton'
        
        zgd_frame = controls_frame.app_instance.tabs_parent.tab_content_frames['Markers'].showtime_tab.zgd_frame
        
        active_button_key = 'All'
        
        # NEW: Get the current buffer value from the dropdown
        buffer_mhz = float(controls_frame.buffer_var.get())
        debug_log(f"Retrieved buffer value: {buffer_mhz} MHz.", file=f"{os.path.basename(__file__)}", version=current_version, function="_update_zone_zoom_button_styles")
        
        # --- Determine active context and trigger the corresponding span update ---
        if hasattr(zgd_frame, 'selected_device_info') and zgd_frame.selected_device_info:
            active_button_key = 'Device'
            device_info = zgd_frame.selected_device_info
            name = device_info.get('NAME', 'N/A')
            freq = device_info.get('CENTER', 'N/A')
            controls_frame.zone_zoom_label_left_var.set(f"Device: {name}")
            controls_frame.zone_zoom_label_center_var.set(f"Center: {freq:.3f} MHz" if isinstance(freq, (int, float)) else "N/A")
            controls_frame.zone_zoom_label_right_var.set("(1 Marker)")
            
            if freq != 'N/A':
                # AUTOMATICALLY TRIGGER SPAN UPDATE
                set_span_to_device(controls_frame, DeviceName=name, CenterFreq=freq)
                # NEW: Call the trace action after setting the span
                execute_trace_action(controls_frame)

        elif zgd_frame.selected_group:
            active_button_key = 'Group'
            devices = zgd_frame.structured_data.get(zgd_frame.selected_zone, {}).get(zgd_frame.selected_group, [])
            freqs = [d.get('CENTER') for d in devices if isinstance(d.get('CENTER'), (int, float))]
            controls_frame.zone_zoom_label_left_var.set(f"Group: {zgd_frame.selected_group}")
            
            if freqs:
                buffered_start_freq = min(freqs) - buffer_mhz
                buffered_stop_freq = max(freqs) + buffer_mhz
                controls_frame.zone_zoom_label_center_var.set(f"Start: {buffered_start_freq:.3f} MHz")
                controls_frame.zone_zoom_label_right_var.set(f"Stop: {buffered_stop_freq:.3f} MHz ({len(freqs)} Markers)")
                
                # AUTOMATICALLY TRIGGER SPAN UPDATE
                set_span_to_group(controls_frame, GroupName=zgd_frame.selected_group, NumberOfMarkers=len(freqs), StartFreq=min(freqs), StopFreq=max(freqs), buffer_mhz=buffer_mhz)
                # NEW: Call the trace action after setting the span
                execute_trace_action(controls_frame)
            else:
                controls_frame.zone_zoom_label_center_var.set("Start: N/A")
                controls_frame.zone_zoom_label_right_var.set("Stop: N/A (0 Markers)")

        elif zgd_frame.selected_zone:
            active_button_key = 'Zone'
            devices = zgd_frame._get_all_devices_in_zone(zgd_frame.structured_data, zgd_frame.selected_zone)
            freqs = [d.get('CENTER') for d in devices if isinstance(d.get('CENTER'), (int, float))]
            controls_frame.zone_zoom_label_left_var.set(f"Zone: {zgd_frame.selected_zone}")

            if freqs:
                buffered_start_freq = min(freqs) - buffer_mhz
                buffered_stop_freq = max(freqs) + buffer_mhz
                controls_frame.zone_zoom_label_center_var.set(f"Start: {buffered_start_freq:.3f} MHz")
                controls_frame.zone_zoom_label_right_var.set(f"Stop: {buffered_stop_freq:.3f} MHz ({len(freqs)} Markers)")

                # AUTOMATICALLY TRIGGER SPAN UPDATE
                set_span_to_zone(controls_frame, ZoneName=zgd_frame.selected_zone, NumberOfMarkers=len(freqs), StartFreq=min(freqs), StopFreq=max(freqs), selected=True, buffer_mhz=buffer_mhz)
                # NEW: Call the trace action after setting the span
                execute_trace_action(controls_frame)
            else:
                controls_frame.zone_zoom_label_center_var.set("Start: N/A")
                controls_frame.zone_zoom_label_right_var.set("Stop: N/A (0 Markers)")
            
        else: # Default is All Markers
            active_button_key = 'All'
            devices = zgd_frame._get_all_devices_in_zone(zgd_frame.structured_data, None)
            freqs = [d.get('CENTER') for d in devices if isinstance(d.get('CENTER'), (int, float))]
            controls_frame.zone_zoom_label_left_var.set("All Markers")
            
            if freqs:
                buffered_start_freq = min(freqs) - buffer_mhz
                buffered_stop_freq = max(freqs) + buffer_mhz
                controls_frame.zone_zoom_label_center_var.set(f"Start: {buffered_start_freq:.3f} MHz")
                controls_frame.zone_zoom_label_right_var.set(f"Stop: {buffered_stop_freq:.3f} MHz ({len(freqs)} Markers)")
                
                # AUTOMATICALLY TRIGGER SPAN UPDATE
                set_span_to_all_markers(controls_frame, NumberOfMarkers=len(freqs), StartFreq=min(freqs), StopFreq=max(freqs), selected=True, buffer_mhz=buffer_mhz)
            else:
                controls_frame.zone_zoom_label_center_var.set("Start: N/A")
                controls_frame.zone_zoom_label_right_var.set("Stop: N/A (0 Markers)")

        # Update all button styles
        for key, button in controls_frame.zone_zoom_buttons.items():
            if key == active_button_key:
                button.config(style=active_style)
            else:
                button.config(style=inactive_style)
        
        debug_log(f"Zone Zoom buttons, labels, and span updated. Active context: '{active_button_key}'.",
                  file=f"{os.path.basename(__file__)}", version=current_version, function="_update_zone_zoom_button_styles")
    except Exception as e:
        console_log(f"❌ Error in _update_zone_zoom_button_styles: {e}")
        debug_log(f"It's madness! The Zone Zoom button styles refused to update! The error is: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="_update_zone_zoom_button_styles")


def on_span_button_click(controls_frame, span_hz):
    # [Handles clicks on span buttons, updating state and calling instrument logic.]
    debug_log(f"Entering on_span_button_click with span_hz: {span_hz}", file=f"{os.path.basename(__file__)}", version=current_version, function="on_span_button_click")
    if span_hz == 'Follow':
        controls_frame.follow_zone_span_var.set(True)
        controls_frame.console_print_func("Span set to follow active zone.")
    else:
        controls_frame.follow_zone_span_var.set(False)
        controls_frame.span_var.set(str(span_hz))
        set_span_logic(controls_frame.app_instance, int(span_hz), controls_frame.console_print_func)
    
    _update_control_styles(controls_frame)

def on_rbw_button_click(controls_frame, rbw_hz):
    # [Handles clicks on RBW buttons, updating state and calling instrument logic.]
    debug_log(f"Entering on_rbw_button_click with rbw_hz: {rbw_hz}", file=f"{os.path.basename(__file__)}", version=current_version, function="on_rbw_button_click")
    controls_frame.rbw_var.set(str(rbw_hz))
    set_rbw_logic(controls_frame.app_instance, int(rbw_hz), controls_frame.console_print_func)
    _update_control_styles(controls_frame)

def on_trace_button_click(controls_frame, trace_var_to_toggle):
    # [Toggles the state of a single trace mode variable, then calls the sync function.]
    debug_log(f"Entering on_trace_button_click", file=f"{os.path.basename(__file__)}", version=current_version, function="on_trace_button_click")
    trace_var_to_toggle.set(not trace_var_to_toggle.get())
    sync_trace_modes(controls_frame)

def sync_trace_modes(controls_frame):
    # [Sets all four trace modes at once using the efficient YakBeg handler.]
    debug_log(f"Entering sync_trace_modes", file=f"{os.path.basename(__file__)}", version=current_version, function="sync_trace_modes")
    try:
        app = controls_frame.app_instance
        console = controls_frame.console_print_func
        
        desired_modes = [
            'WRIT' if controls_frame.trace_live_mode.get() else 'BLAN',
            'MAXH' if controls_frame.trace_max_hold_mode.get() else 'BLAN',
            'MINH' if controls_frame.trace_min_hold_mode.get() else 'BLAN',
            'BLAN'
        ]

        response = handle_trace_modes_beg(app, desired_modes, console)

        if response and isinstance(response, list) and len(response) >= 3:
            controls_frame.trace_live_mode.set('WRIT' in response[0])
            controls_frame.trace_max_hold_mode.set('MAXH' in response[1])
            controls_frame.trace_min_hold_mode.set('MINH' in response[2])
            console("✅ Trace modes synchronized.")
        else:
            console("❌ Failed to synchronize trace modes. Response was invalid.")
        
        _update_control_styles(controls_frame)
    except Exception as e:
        console_log(f"❌ Error in sync_trace_modes: {e}")
        debug_log(f"The trace modes are rebelling! The error is: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="sync_trace_modes")

def on_poke_action(controls_frame):
    # [Sets center frequency and span simultaneously using the YakBeg handler.]
    debug_log(f"Entering on_poke_action", file=f"{os.path.basename(__file__)}", version=current_version, function="on_poke_action")
    try:
        center_freq_mhz = float(controls_frame.poke_freq_var.get())
        center_freq_hz = int(center_freq_mhz * MHZ_TO_HZ)
        
        span_hz = int(controls_frame.span_var.get())
        
        controls_frame.console_print_func(f"Poking instrument: Center={center_freq_mhz} MHz, Span={format_hz(span_hz)}...")
        
        response = handle_freq_center_span_beg(
            controls_frame.app_instance, 
            center_freq_hz, 
            span_hz,
            controls_frame.console_print_func
        )
        
        if response and len(response) >= 2:
            returned_center, returned_span, _, _ = response
            controls_frame.console_print_func(
                f"✅ Instrument Confirmed: Center={returned_center / MHZ_TO_HZ:.3f} MHz, Span={format_hz(returned_span)}"
            )
        else:
            controls_frame.console_print_func("❌ Poke command failed. Instrument did not confirm settings.")
            
    except ValueError:
        controls_frame.console_print_func("Invalid frequency for Poke action. Please enter a number.")
    except Exception as e:
        controls_frame.console_print_func(f"An unexpected error occurred during poke: {e}")

def set_span_logic(app_instance, span_hz, console_print_func):
    # [Sets the instrument's span frequency using the YakSet command.]
    debug_log(f"Entering set_span_logic with span_hz: {span_hz}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_logic")
    status = YakSet(app_instance=app_instance, command_type="FREQUENCY/SPAN", variable_value=str(span_hz), console_print_func=console_print_func)
    if status != "PASSED":
        console_print_func(f"❌ Failed to set span frequency.")

def set_rbw_logic(app_instance, rbw_hz, console_print_func):
    # [Sets the instrument's Resolution Bandwidth (RBW) using the YakSet command.]
    debug_log(f"Entering set_rbw_logic with rbw_hz: {rbw_hz}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_rbw_logic")
    status = YakSet(app_instance=app_instance, command_type="BANDWIDTH/RESOLUTION", variable_value=str(rbw_hz), console_print_func=console_print_func)
    if status != "PASSED":
        console_print_func(f"❌ Failed to set RBW.")


# --- NEW: TRACE DATA HANDLING ---

def _get_current_view_details(controls_frame):
    # [Helper function to determine the current frequency span and title based on UI selection.]
    debug_log(f"Entering _get_current_view_details", file=f"{os.path.basename(__file__)}", version=current_version, function="_get_current_view_details")
    zgd_frame = controls_frame.app_instance.tabs_parent.tab_content_frames['Markers'].showtime_tab.zgd_frame
    
    view_name = "All Markers"
    start_freq_mhz = None
    stop_freq_mhz = None

    try:
        if hasattr(zgd_frame, 'selected_device_info') and zgd_frame.selected_device_info:
            device = zgd_frame.selected_device_info
            center_mhz = device.get('CENTER')
            span_hz = int(float(controls_frame.span_var.get()))
            span_mhz = span_hz / MHZ_TO_HZ
            start_freq_mhz = center_mhz - (span_mhz / 2)
            stop_freq_mhz = center_mhz + (span_mhz / 2)
            view_name = f"Device: {device.get('NAME', 'N/A')}"

        elif zgd_frame.selected_group:
            active_button_key = 'Group'
            devices = zgd_frame.structured_data.get(zgd_frame.selected_zone, {}).get(zgd_frame.selected_group, [])
            freqs = [d.get('CENTER') for d in devices if isinstance(d.get('CENTER'), (int, float))]
            if freqs:
                start_freq_mhz, stop_freq_mhz = min(freqs), max(freqs)
            view_name = f"Group: {zgd_frame.selected_group}"

        elif zgd_frame.selected_zone:
            active_button_key = 'Zone'
            devices = zgd_frame._get_all_devices_in_zone(zgd_frame.structured_data, zgd_frame.selected_zone)
            freqs = [d.get('CENTER') for d in devices if isinstance(d.get('CENTER'), (int, float))]
            if freqs:
                start_freq_mhz, stop_freq_mhz = min(freqs), max(freqs)
            view_name = f"Zone: {zgd_frame.selected_zone}"
        
        else: # All Markers
            devices = zgd_frame._get_all_devices_in_zone(zgd_frame.structured_data, None)
            freqs = [d.get('CENTER') for d in devices if isinstance(d.get('CENTER'), (int, float))]
            if freqs:
                start_freq_mhz, stop_freq_mhz = min(freqs), max(freqs)
            view_name = "All Markers"

        debug_log(f"Current view: {view_name}, Start: {start_freq_mhz} MHz, Stop: {stop_freq_mhz} MHz", file=f"{os.path.basename(__file__)}", version=current_version, function="_get_current_view_details")
        return view_name, start_freq_mhz, stop_freq_mhz

    except Exception as e:
        controls_frame.console_print_func(f"❌ Could not determine current frequency view: {e}", "ERROR")
        return None, None, None


def on_get_all_traces_click(controls_frame):
    # [Handles 'Get Live, Max and Min' button click.]
    debug_log(f"Entering on_get_all_traces_click", file=f"{os.path.basename(__file__)}", version=current_version, function="on_get_all_traces_click")
    view_name, start_freq_mhz, stop_freq_mhz = _get_current_view_details(controls_frame)
    if not all([view_name, start_freq_mhz, stop_freq_mhz]):
        controls_frame.console_print_func("❌ Cannot get traces, no valid frequency range selected.", "ERROR")
        return
    
    # ADDED DEBUG: Log the parameters before calling the handler
    debug_log(f"Attempting to retrieve all traces. Parameters: Start_MHz={start_freq_mhz}, Stop_MHz={stop_freq_mhz}",
              file=f"{os.path.basename(__file__)}", version=current_version, function="on_get_all_traces_click", special=True)
              
    trace_data_dict = handle_all_traces_nab(controls_frame.app_instance, controls_frame.console_print_func)
    
    # ADDED DEBUG: Log the return value from the handler
    debug_log(f"Returned from handle_all_traces_nab. Result is a {type(trace_data_dict)}. Value: {trace_data_dict}",
              file=f"{os.path.basename(__file__)}", version=current_version, function="on_get_all_traces_click", special=True)

    if trace_data_dict and "TraceData" in trace_data_dict:
        # CORRECTED: Get the monitor tab reference directly from the app instance
        monitor_tab = controls_frame.app_instance.display_parent_tab.bottom_pane.scan_monitor_tab
        if monitor_tab:
            # The NAB handler returns a dict of dataframes, so we pass that directly
            df1 = pd.DataFrame(trace_data_dict["TraceData"]["Trace1"], columns=['Frequency_Hz', 'Power_dBm'])
            update_top_plot(monitor_tab, df1, start_freq_mhz, stop_freq_mhz, f"Live Trace - {view_name}")
            
            df2 = pd.DataFrame(trace_data_dict["TraceData"]["Trace2"], columns=['Frequency_Hz', 'Power_dBm'])
            update_middle_plot(monitor_tab, df2, start_freq_mhz, stop_freq_mhz, f"Max Hold - {view_name}")

            df3 = pd.DataFrame(trace_data_dict["TraceData"]["Trace3"], columns=['Frequency_Hz', 'Power_dBm'])
            update_bottom_plot(monitor_tab, df3, start_freq_mhz, stop_freq_mhz, f"Min Hold - {view_name}")
            controls_frame.console_print_func("✅ Successfully updated monitor with all three traces.", "SUCCESS")
            # ADDED: Switch to the Scan Monitor tab
            controls_frame.app_instance.display_parent_tab.change_display_tab('Monitor')
        else:
            controls_frame.console_print_func("❌ Scan Monitor tab not found.", "ERROR")
    else:
        controls_frame.console_print_func("❌ Failed to retrieve trace data.", "ERROR")
        # ADDED DEBUG: A detailed debug log for the failure
        debug_log(f"Arrr, the plotting operation be capsized! The data from the handler be all wrong! Returned a {type(trace_data_dict)} when a dict was expected. 🏴‍☠️",
                 file=f"{os.path.basename(__file__)}", version=current_version, function="on_get_all_traces_click")

def on_get_live_trace_click(controls_frame):
    # [Handles 'Get Live' button click.]
    debug_log(f"Entering on_get_live_trace_click", file=f"{os.path.basename(__file__)}", version=current_version, function="on_get_live_trace_click")
    view_name, start_freq_mhz, stop_freq_mhz = _get_current_view_details(controls_frame)
    if not all([view_name, start_freq_mhz, stop_freq_mhz]):
        controls_frame.console_print_func("❌ Cannot get trace, no valid frequency range selected.", "ERROR")
        return

    trace_data = handle_trace_data_beg(controls_frame.app_instance, 1, start_freq_mhz, stop_freq_mhz, controls_frame.console_print_func)

    if trace_data:
        # CORRECTED: Get the scan view tab reference directly from the app instance
        scan_view_tab = controls_frame.app_instance.display_parent_tab.bottom_pane.scan_view_tab
        if scan_view_tab:
            # The handler now returns a list of tuples, convert to DataFrame
            df = pd.DataFrame(trace_data, columns=['Frequency_Hz', 'Power_dBm'])
            # MODIFIED: Passed 'yellow' for live trace
            update_single_plot(scan_view_tab, df, start_freq_mhz, stop_freq_mhz, f"Live Trace - {view_name}", line_color='yellow')
            controls_frame.console_print_func("✅ Successfully updated Scan View with live trace.", "SUCCESS")
            # ADDED: Switch to the Scan View tab
            controls_frame.app_instance.display_parent_tab.change_display_tab('View')
        else:
            controls_frame.console_print_func("❌ Scan View tab not found.", "ERROR")
    else:
        controls_frame.console_print_func("❌ Failed to retrieve live trace data.", "ERROR")


def on_get_max_trace_click(controls_frame):
    # [Handles 'Get Max' button click.]
    debug_log(f"Entering on_get_max_trace_click", file=f"{os.path.basename(__file__)}", version=current_version, function="on_get_max_trace_click")
    view_name, start_freq_mhz, stop_freq_mhz = _get_current_view_details(controls_frame)
    if not all([view_name, start_freq_mhz, stop_freq_mhz]):
        controls_frame.console_print_func("❌ Cannot get trace, no valid frequency range selected.", "ERROR")
        return

    trace_data = handle_trace_data_beg(controls_frame.app_instance, 2, start_freq_mhz, stop_freq_mhz, controls_frame.console_print_func)

    if trace_data:
        # CORRECTED: Get the scan view tab reference directly from the app instance
        scan_view_tab = controls_frame.app_instance.display_parent_tab.bottom_pane.scan_view_tab
        if scan_view_tab:
            # The handler now returns a list of tuples, convert to DataFrame
            df = pd.DataFrame(trace_data, columns=['Frequency_Hz', 'Power_dBm'])
            # MODIFIED: Passed 'green' for max hold trace
            update_single_plot(scan_view_tab, df, start_freq_mhz, stop_freq_mhz, f"Max Hold - {view_name}", line_color='green')
            controls_frame.console_print_func("✅ Successfully updated Scan View with max hold trace.", "SUCCESS")
            # ADDED: Switch to the Scan View tab
            controls_frame.app_instance.display_parent_tab.change_display_tab('View')
        else:
            controls_frame.console_print_func("❌ Scan View tab not found.", "ERROR")
    else:
        controls_frame.console_print_func("❌ Failed to retrieve max hold trace data.", "ERROR")
