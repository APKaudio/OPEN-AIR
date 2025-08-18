# tabs/Markers/utils_showtime_controls.py
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
# Version 20250814.172000.1

current_version = "20250814.172000.1"
current_version_hash = (20250814 * 172000 * 1)

import os
import inspect
from ref.frequency_bands import MHZ_TO_HZ
from display.debug_logic import debug_log
from yak.Yakety_Yak import YakSet
from yak.utils_yakbeg_handler import handle_trace_modes_beg, handle_freq_center_span_beg

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
    "Leisurely": 10 * 1000,
    "Unhurried": 3 * 1000,
    "Slothlike": 1 * 1000,
}

# --- Placeholder function ---
def set_marker_logic(app, freq, console):
    console(f"CMD: Set Marker to {freq} Hz", "INFO")

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

def _update_control_styles(controls_frame):
    # [A brief, one-sentence description of the function's purpose.]
    # Updates the visual styles of all control buttons based on the current state.
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

def on_span_button_click(controls_frame, span_hz):
    # [A brief, one-sentence description of the function's purpose.]
    # Handles clicks on span buttons, updating state and calling instrument logic.
    if span_hz == 'Follow':
        controls_frame.follow_zone_span_var.set(True)
        controls_frame.console_print_func("Span set to follow active zone.", "INFO")
    else:
        controls_frame.follow_zone_span_var.set(False)
        controls_frame.span_var.set(str(span_hz))
        set_span_logic(controls_frame.app_instance, int(span_hz), controls_frame.console_print_func)
    
    _update_control_styles(controls_frame)

def on_rbw_button_click(controls_frame, rbw_hz):
    # [A brief, one-sentence description of the function's purpose.]
    # Handles clicks on RBW buttons, updating state and calling instrument logic.
    controls_frame.rbw_var.set(str(rbw_hz))
    set_rbw_logic(controls_frame.app_instance, int(rbw_hz), controls_frame.console_print_func)
    _update_control_styles(controls_frame)

def on_trace_button_click(controls_frame, trace_var_to_toggle):
    # [A brief, one-sentence description of the function's purpose.]
    # Toggles the state of a single trace mode variable, then calls the sync function.
    trace_var_to_toggle.set(not trace_var_to_toggle.get())
    sync_trace_modes(controls_frame)

def sync_trace_modes(controls_frame):
    # [A brief, one-sentence description of the function's purpose.]
    # Sets all four trace modes at once using the efficient YakBeg handler.
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
        console("✅ Trace modes synchronized.", "SUCCESS")
    else:
        console("❌ Failed to synchronize trace modes. Response was invalid.", "ERROR")
    
    _update_control_styles(controls_frame)

def on_poke_action(controls_frame):
    # [A brief, one-sentence description of the function's purpose.]
    # Sets center frequency and span simultaneously using the YakBeg handler.
    try:
        center_freq_mhz = float(controls_frame.poke_freq_var.get())
        center_freq_hz = int(center_freq_mhz * MHZ_TO_HZ)
        
        span_hz = int(controls_frame.span_var.get())
        
        controls_frame.console_print_func(f"Poking instrument: Center={center_freq_mhz} MHz, Span={format_hz(span_hz)}...", "INFO")
        
        returned_center, returned_span = handle_freq_center_span_beg(
            controls_frame.app_instance, 
            center_freq_hz, 
            span_hz,
            controls_frame.console_print_func
        )
        
        if returned_center is not None and returned_span is not None:
            controls_frame.console_print_func(
                f"✅ Instrument Confirmed: Center={returned_center / MHZ_TO_HZ:.3f} MHz, Span={format_hz(returned_span)}",
                "SUCCESS"
            )
        else:
            controls_frame.console_print_func("❌ Poke command failed. Instrument did not confirm settings.", "ERROR")
            
    except ValueError:
        controls_frame.console_print_func("Invalid frequency for Poke action. Please enter a number.", "ERROR")
    except Exception as e:
        controls_frame.console_print_func(f"An unexpected error occurred during poke: {e}", "ERROR")

def set_span_logic(app_instance, span_hz, console_print_func):
    # [A brief, one-sentence description of the function's purpose.]
    # Sets the instrument's span frequency using the YakSet command.
    status = YakSet(app_instance=app_instance, command_type="FREQUENCY/SPAN", variable_value=str(span_hz), console_print_func=console_print_func)
    if status != "PASSED":
        console_print_func(f"❌ Failed to set span frequency.", "ERROR")

def set_rbw_logic(app_instance, rbw_hz, console_print_func):
    # [A brief, one-sentence description of the function's purpose.]
    # Sets the instrument's Resolution Bandwidth (RBW) using the YakSet command.
    status = YakSet(app_instance=app_instance, command_type="BANDWIDTH/RESOLUTION", variable_value=str(rbw_hz), console_print_func=console_print_func)
    if status != "PASSED":
        console_print_func(f"❌ Failed to set RBW.", "ERROR")