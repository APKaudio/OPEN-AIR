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
# Version 20250811.225500.2 (REFACTORED: Converted all direct instrument calls from write_safe/query_safe to use the high-level YakSet and YakDo commands.)

current_version = "20250811.225500.2" 
current_version_hash = 20250811 * 225500 * 2

import inspect
import os
import time # Import time for potential small delays

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log
from ref.frequency_bands import MHZ_TO_HZ

# New Imports for high-level Yak commands
from tabs.Instrument.Yakety_Yak import YakSet, YakDo

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

def set_frequency_logic(app_instance, frequency_hz, console_print_func):
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to set instrument frequency to {frequency_hz} Hz.", file=os.path.basename(__file__), version=current_version, function=current_function)
    
    # Use YakSet to set the frequency
    if YakSet(app_instance, "FREQUENCY/CENTER", str(int(frequency_hz)), console_print_func) == "PASSED":
        console_print_func(f"✅ Frequency set to {frequency_hz / MHZ_TO_HZ:.3f} MHz.")
        debug_log(f"Frequency set successfully to {frequency_hz} Hz.", file=os.path.basename(__file__), version=current_version, function=current_function)
        return True
    else:
        console_print_func(f"❌ Failed to set frequency to {frequency_hz / MHZ_TO_HZ:.3f} MHz.")
        debug_log(f"Failed to set frequency to {frequency_hz} Hz. What the hell went wrong?!", file=os.path.basename(__file__), version=current_version, function=current_function)
        return False

def set_span_logic(app_instance, span_hz, console_print_func):
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to set instrument span to {span_hz} Hz.", file=os.path.basename(__file__), version=current_version, function=current_function)
    if not app_instance.inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot set span.")
        debug_log("Instrument not connected for set_span_logic. Fucking useless!", file=os.path.basename(__file__), version=current_version, function=current_function)
        return False

    # Use YakSet for span. Assuming 0 means MAX span, otherwise send the value.
    if span_hz == 0.0:
        if YakDo(app_instance, "FREQUENCY/SPAN/MAX", console_print_func) == "PASSED":
            console_print_func("✅ Span applied (MAX).")
            return True
        else:
            console_print_func("❌ Failed to apply span (MAX).")
            return False
    else:
        if YakSet(app_instance, "FREQUENCY/SPAN", str(int(span_hz)), console_print_func) == "PASSED":
            console_print_func(f"✅ Span set to {span_hz / MHZ_TO_HZ:.3f} MHz.")
            debug_log(f"Span set to {span_hz} Hz.", file=os.path.basename(__file__), version=current_version, function=current_function)
            return True
        else:
            console_print_func(f"❌ Failed to set span to {span_hz / MHZ_TO_HZ:.3f} MHz.")
            debug_log(f"Failed to set span to {span_hz} Hz. What the hell went wrong?!", file=os.path.basename(__file__), version=current_version, function=current_function)
            return False

def set_rbw_logic(app_instance, rbw_hz, console_print_func):
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to set instrument RBW to {rbw_hz} Hz.", file=os.path.basename(__file__), version=current_version, function=current_function)
    if not app_instance.inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot set RBW.")
        debug_log("Instrument not connected for set_rbw_logic. Fucking useless!", file=os.path.basename(__file__), version=current_version, function=current_function)
        return False

    # Use YakSet to set the resolution bandwidth
    if YakSet(app_instance, "BANDWIDTH/RESOLUTION", str(int(rbw_hz)), console_print_func) == "PASSED":
        console_print_func(f"✅ RBW set to {rbw_hz / (MHZ_TO_HZ if rbw_hz >= MHZ_TO_HZ else 1000):.3f} {'MHz' if rbw_hz >= MHZ_TO_HZ else 'kHz'}.")
        debug_log(f"RBW set successfully to {rbw_hz} Hz.", file=os.path.basename(__file__), version=current_version, function=current_function)
        return True
    else:
        console_print_func(f"❌ Failed to set RBW.")
        debug_log(f"Failed to set RBW. What the hell went wrong?!", file=os.path.basename(__file__), version=current_version, function=current_function)
        return False

def set_trace_modes_logic(app_instance, live_mode, max_hold_mode, min_hold_mode, console_print_func):
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Applying trace modes: Live: {live_mode}, MaxHold: {max_hold_mode}, MinHold: {min_hold_mode}", file=os.path.basename(__file__), version=current_version, function=current_function)
    if not app_instance.inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot set trace modes.")
        return False
    
    success = True
    if YakDo(app_instance, f"TRACE/1/MODE/{'WRITe' if live_mode else 'BLANK'}", console_print_func) != "PASSED": success = False
    if YakDo(app_instance, f"TRACE/2/MODE/{'MAXHOLD' if max_hold_mode else 'BLANK'}", console_print_func) != "PASSED": success = False
    if YakDo(app_instance, f"TRACE/3/MODE/{'MINHOLD' if min_hold_mode else 'BLANK'}", console_print_func) != "PASSED": success = False
    
    if success:
        console_print_func("✅ Trace modes applied.")
        debug_log("Trace modes set successfully. All systems, go!", file=os.path.basename(__file__), version=current_version, function=current_function)
    else:
        console_print_func("❌ Failed to apply all trace modes.")
        debug_log("Failed to apply all trace modes. What a pain!", file=os.path.basename(__file__), version=current_version, function=current_function)
    return success

def blank_hold_traces_logic(app_instance, console_print_func):
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Blanking hold traces.", file=os.path.basename(__file__), version=current_version, function=current_function)
    return set_trace_modes_logic(app_instance, True, False, False, console_print_func)

def set_marker_logic(app_instance, frequency_hz, marker_name, console_print_func):
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Setting marker to {frequency_hz} Hz for '{marker_name}'...", file=os.path.basename(__file__), version=current_version, function=current_function)
    if not app_instance.inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot set marker.")
        return False
    
    success = True
    # The Yakety_Yak function for setting markers is MARKER/1/CALCULATE/STATE
    if YakDo(app_instance, "MARKER/1/CALCULATE/STATE", console_print_func) != "PASSED":
        success = False
    
    if YakSet(app_instance, "MARKER/1/CALCULATE/X", str(int(frequency_hz)), console_print_func) != "PASSED":
        success = False
        
    if success:
        console_print_func(f"✅ Marker set to {frequency_hz / MHZ_TO_HZ:.3f} MHz.")
        debug_log(f"Marker set successfully. We've tagged our quarry!", file=os.path.basename(__file__), version=current_version, function=current_function)
    else:
        console_print_func(f"❌ Failed to set marker for {marker_name}.")
        debug_log(f"Failed to set marker. What a disaster!", file=os.path.basename(__file__), version=current_version, function=current_function)
    return success
