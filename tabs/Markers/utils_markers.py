# utils/utils_markers.py
#
# This file contains utility functions for controlling spectrum analyzer markers,
# span, and trace modes. It provides a clean interface for sending SCPI commands
# to the instrument, ensuring commands are sent safely and debug information is logged.
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
# Version 20250803.233500.0 (CHANGED: Updated RBW_OPTIONS to use descriptive names.)
# Version 20250801.2145.1 (Refactored debug_print, write_safe, query_safe to use new logging.)

current_version = "20250803.233500.0" 
current_version_hash = 20250803 * 233500 * 0 # Example hash, adjust as needed

import inspect
# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log
from ref.frequency_bands import MHZ_TO_HZ
import time # Import time for potential small delays

# Constants for Span Options (used in MarkersDisplayTab)
SPAN_OPTIONS = {
    "Ultra Wide": 100 * MHZ_TO_HZ, # This would typically be a special value for full span
    "Wide": 10 * MHZ_TO_HZ, # Example: 10 MHz
    "Normal": 1 * MHZ_TO_HZ,  # Example: 1 MHz
    "Tight": 100 * 1000,    # Example: 100 KHz
    "Microscope": 10 * 1000,     # Example: 10 KHz
}

# --- UPDATED: Constants for Resolution Bandwidth (RBW) Options ---
RBW_OPTIONS = {
    "Fast": 1 * MHZ_TO_HZ,
    "Brisk": 300 * 1000,
    "Deliberate": 100 * 1000,
    "Steady": 30 * 1000,
    "Leisurely": 10 * 1000,
    "Unhurried": 3 * 1000,
    "Slothlike": 1 * 1000,
}
# --- END UPDATED ---

# Helper functions for instrument communication, using the new logging
def write_safe(inst, command, console_print_func):
    # Function unchanged
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to write command: {command}", file=__file__, version=current_version, function=current_function)
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot write command.")
        debug_log("Instrument not connected. Fucking useless!", file=__file__, version=current_version, function=current_function)
        return False
    try:
        inst.write(command)
        log_visa_command(command, "SENT")
        return True
    except Exception as e:
        console_print_func(f"❌ Error writing command '{command}': {e}")
        debug_log(f"Error writing command '{command}': {e}. This thing is a pain in the ass!", file=__file__, version=current_version, function=current_function)
        return False

def query_safe(inst, command, console_print_func):
    # Function unchanged
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to query command: {command}", file=__file__, version=current_version, function=current_function)
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot query command.")
        debug_log("Instrument not connected. Fucking useless!", file=__file__, version=current_version, function=current_function)
        return None
    try:
        response = inst.query(command).strip()
        log_visa_command(command, "SENT")
        log_visa_command(response, "RECEIVED")
        return response
    except Exception as e:
        console_print_func(f"❌ Error querying command '{command}': {e}")
        debug_log(f"Error querying command '{command}': {e}. This goddamn thing is broken!", file=__file__, version=current_version, function=current_function)
        return None

# Import log_visa_command from debug_logic
from display.debug_logic import log_visa_command

# Functions set_frequency_logic, set_span_logic, set_rbw_logic, set_trace_modes_logic, 
# blank_hold_traces_logic, and set_marker_logic remain unchanged.
# ... (rest of the functions are omitted for brevity)
def set_frequency_logic(inst, frequency_hz, console_print_func):
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to set instrument frequency to {frequency_hz} Hz.", file=__file__, version=current_version, function=current_function)
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot set frequency.")
        debug_log("Instrument not connected for set_frequency_logic. Fucking useless!", file=__file__, version=current_version, function=current_function)
        return False
    command = f":SENSe:FREQuency:CENTer {frequency_hz}"
    if write_safe(inst, command, console_print_func):
        console_print_func(f"✅ Frequency set to {frequency_hz / MHZ_TO_HZ:.3f} MHz.")
        debug_log(f"Frequency set successfully to {frequency_hz} Hz.", file=__file__, version=current_version, function=current_function)
        return True
    else:
        console_print_func(f"❌ Failed to set frequency to {frequency_hz / MHZ_TO_HZ:.3f} MHz.")
        debug_log(f"Failed to set frequency to {frequency_hz} Hz. What the hell went wrong?!", file=__file__, version=current_version, function=current_function)
        return False

def set_span_logic(inst, span_hz, console_print_func):
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to set instrument span to {span_hz} Hz.", file=__file__, version=current_version, function=current_function)
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot set span.")
        debug_log("Instrument not connected for set_span_logic. Fucking useless!", file=__file__, version=current_version, function=current_function)
        return False
    success = True
    if span_hz == 0.0:
        command = ":SENSe:FREQuency:SPAN MAX"
    else:
        command = f":SENSe:FREQuency:SPAN {span_hz}"
    if not write_safe(inst, command, console_print_func):
        success = False
    if success:
        console_print_func("✅ Span applied.")
    else:
        console_print_func("❌ Failed to apply span.")
    return success

def set_rbw_logic(inst, rbw_hz, console_print_func):
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to set instrument RBW to {rbw_hz} Hz.", file=__file__, version=current_version, function=current_function)
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot set RBW.")
        debug_log("Instrument not connected for set_rbw_logic. Fucking useless!", file=__file__, version=current_version, function=current_function)
        return False
    command = f":SENSe:BANDwidth:RESolution {rbw_hz}"
    if write_safe(inst, command, console_print_func):
        console_print_func(f"✅ RBW set to {rbw_hz / (MHZ_TO_HZ if rbw_hz >= MHZ_TO_HZ else 1000):.3f} {'MHz' if rbw_hz >= MHZ_TO_HZ else 'kHz'}.")
        return True
    else:
        console_print_func(f"❌ Failed to set RBW.")
        return False

def set_trace_modes_logic(inst, live_mode, max_hold_mode, min_hold_mode, console_print_func):
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Applying trace modes: Live: {live_mode}, MaxHold: {max_hold_mode}, MinHold: {min_hold_mode}", file=__file__, version=current_version, function=current_function)
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot set trace modes.")
        return False
    success = True
    if not write_safe(inst, f":TRAC1:MODE {'WRITe' if live_mode else 'BLANK'}", console_print_func): success = False
    
    if not write_safe(inst, f":TRAC2:MODE {'MAXHold' if max_hold_mode else 'BLANK'}", console_print_func): success = False
    
    if not write_safe(inst, f":TRAC3:MODE {'MINHold' if min_hold_mode else 'BLANK'}", console_print_func): success = False
    
    return success

def blank_hold_traces_logic(inst, console_print_func):
    # Function unchanged
    return set_trace_modes_logic(inst, True, False, False, console_print_func)

def set_marker_logic(inst, frequency_hz, marker_name, console_print_func):
    # Function unchanged
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Setting marker to {frequency_hz} Hz for '{marker_name}'...", file=__file__, version=current_version, function=current_function)
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot set marker.")
        return False
    success = True
    if not write_safe(inst, ":CALCulate:MARKer1:STATe ON", console_print_func): success = False

    if not write_safe(inst, f":CALCulate:MARKer1:X {frequency_hz}", console_print_func): success = False

    if success:
        console_print_func(f"✅ Marker set to {frequency_hz / MHZ_TO_HZ:.3f} MHz.")
    else:
        console_print_func(f"❌ Failed to set marker for {marker_name}.")
    return success