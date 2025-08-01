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
# Version 20250801.1032.1 (Updated header and verified imports for new folder structure)

current_version = "20250801.1032.1" # this variable should always be defined below the header to make the debugging better

import inspect
from utils.utils_instrument_control import debug_print, write_safe, query_safe
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

# --- NEW: Constants for Resolution Bandwidth (RBW) Options ---
# (2025-07-31 17:15) Change: Added RBW options.
RBW_OPTIONS = {
    "1 MHz": 1 * MHZ_TO_HZ,
    "300 kHz": 300 * 1000,
    "100 kHz": 100 * 1000,
    "30 kHz": 30 * 1000,
    "10 kHz": 10 * 1000,
    "3 kHz": 3 * 1000,
    "1 kHz": 1 * 1000,
}
# --- END NEW ---

def set_frequency_logic(inst, frequency_hz, console_print_func):
    """
    Function Description:
    Sets the instrument's center frequency. This function is specifically for
    frequency adjustment and does not handle span or trace modes.

    Inputs to this function:
    - inst (pyvisa.resources.Resource): The PyVISA instrument object.
    - frequency_hz (float): The desired center frequency in Hz.
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Checks if the instrument is connected.
    2. Sends the SCPI command to set the center frequency.
    3. Logs success or failure.

    Outputs of this function:
    - bool: True if the frequency was set successfully, False otherwise.

    (2025-07-31 16:15) Change: New function created to handle frequency setting independently.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = f"utils/utils_markers.py - {current_version}"
    debug_print(f"Attempting to set instrument frequency to {frequency_hz} Hz.", file=current_file, function=current_function, console_print_func=console_print_func)

    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot set frequency.")
        debug_print("Instrument not connected for set_frequency_logic. Fucking useless!", file=current_file, function=current_function, console_print_func=console_print_func)
        return False

    command = f":SENSe:FREQuency:CENTer {frequency_hz}"
    if write_safe(inst, command, console_print_func):
        console_print_func(f"✅ Frequency set to {frequency_hz / MHZ_TO_HZ:.3f} MHz.")
        debug_print(f"Frequency set successfully to {frequency_hz} Hz.", file=current_file, function=current_function, console_print_func=console_print_func)
        return True
    else:
        console_print_func(f"❌ Failed to set frequency to {frequency_hz / MHZ_TO_HZ:.3f} MHz.")
        debug_print(f"Failed to set frequency to {frequency_hz} Hz. What the hell went wrong?!", file=current_file, function=current_function, console_print_func=console_print_func)
        return False


def set_span_logic(inst, span_hz, console_print_func):
    """
    Function Description:
    Sets the instrument's span. This function is now solely responsible for
    span adjustment and does not handle frequency or trace modes.

    Inputs to this function:
    - inst (pyvisa.resources.Resource): The PyVISA instrument object.
    - span_hz (float): The desired span in Hz. Use 0.0 for "Full Span".
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Checks if the instrument is connected.
    2. Sends the appropriate SCPI command to set the span (either specific Hz or MAX for full span).
    3. Logs success or failure.

    Outputs of this function:
    - bool: True if the span was set successfully, False otherwise.

    (2025-07-31 16:15) Change: Modified to only set span. Removed center_freq_hz and trace mode parameters.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = f"utils/utils_markers.py - {current_version}"
    debug_print(f"Attempting to set instrument span to {span_hz} Hz.", file=current_file, function=current_function, console_print_func=console_print_func)

    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot set span.")
        debug_print("Instrument not connected for set_span_logic. Fucking useless!", file=current_file, function=current_function, console_print_func=console_print_func)
        return False

    success = True

    # Set Span
    if span_hz == 0.0: # Special case for "Full Span"
        command = ":SENSe:FREQuency:SPAN MAX"
        debug_print(f"Attempting to send Span MAX command: {command}", file=current_file, function=current_function, console_print_func=console_print_func)
        if not write_safe(inst, command, console_print_func): # Use MAX for full span
            success = False
            console_print_func("❌ Failed to set Full Span.")
            debug_print(f"write_safe returned False for Span MAX command: {command}", file=current_file, function=current_function, console_print_func=console_print_func)
    else:
        command = f":SENSe:FREQuency:SPAN {span_hz}"
        debug_print(f"Attempting to send Span command: {command}", file=current_file, function=current_function, console_print_func=console_print_func)
        if not write_safe(inst, command, console_print_func):
            success = False
            console_print_func(f"❌ Failed to set span to {span_hz / MHZ_TO_HZ:.3f} MHz.")
            debug_print(f"write_safe returned False for Span command: {command}", file=current_file, function=current_function, console_print_func=console_print_func)

    if success:
        console_print_func("✅ Span applied.")
        debug_print("Span applied successfully.", file=current_file, function=current_function, console_print_func=console_print_func)
    else:
        console_print_func("❌ Failed to apply span.")
        debug_print("Failed to apply span. This bugger is being problematic!", file=current_file, function=current_function, console_print_func=console_print_func)
    return success


# --- NEW: Function to set Resolution Bandwidth (RBW) ---
# (2025-07-31 17:15) Change: Added new function to set RBW.
def set_rbw_logic(inst, rbw_hz, console_print_func):
    """
    Function Description:
    Sets the instrument's Resolution Bandwidth (RBW).

    Inputs to this function:
    - inst (pyvisa.resources.Resource): The PyVISA instrument object.
    - rbw_hz (float): The desired RBW in Hz.
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Checks if the instrument is connected.
    2. Sends the SCPI command to set the RBW.
    3. Logs success or failure.

    Outputs of this function:
    - bool: True if the RBW was set successfully, False otherwise.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = f"utils/utils_markers.py - {current_version}"
    debug_print(f"Attempting to set instrument RBW to {rbw_hz} Hz.", file=current_file, function=current_function, console_print_func=console_print_func)

    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot set RBW.")
        debug_print("Instrument not connected for set_rbw_logic. Fucking useless!", file=current_file, function=current_function, console_print_func=console_print_func)
        return False

    command = f":SENSe:BANDwidth:RESolution {rbw_hz}"
    if write_safe(inst, command, console_print_func):
        console_print_func(f"✅ RBW set to {rbw_hz / (MHZ_TO_HZ if rbw_hz >= MHZ_TO_HZ else 1000):.3f} {'MHz' if rbw_hz >= MHZ_TO_HZ else 'kHz'}.")
        debug_print(f"RBW set successfully to {rbw_hz} Hz.", file=current_file, function=current_function, console_print_func=console_print_func)
        return True
    else:
        console_print_func(f"❌ Failed to set RBW to {rbw_hz / (MHZ_TO_HZ if rbw_hz >= MHZ_TO_HZ else 1000):.3f} {'MHz' if rbw_hz >= MHZ_TO_HZ else 'kHz'}.")
        debug_print(f"Failed to set RBW to {rbw_hz} Hz. What the hell went wrong?!", file=current_file, function=current_function, console_print_func=console_print_func)
        return False
# --- END NEW ---


def set_trace_modes_logic(inst, live_mode, max_hold_mode, min_hold_mode, console_print_func):
    """
    Function Description:
    Sets the instrument's trace modes (Live, Max Hold, Min Hold) based on provided booleans.
    This function is solely responsible for setting trace modes as specified.

    Inputs to this function:
    - inst (pyvisa.resources.Resource): The PyVISA instrument object.
    - live_mode (bool): True to enable Live trace mode, False otherwise.
    - max_hold_mode (bool): True to enable Max Hold trace mode, False otherwise.
    - min_hold_mode (bool): True to enable Min Hold trace mode, False otherwise.
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Checks if the instrument is connected.
    2. Sends SCPI commands to set the state of Trace 1 (Live/Write), Trace 2 (Max Hold/Blank),
       and Trace 3 (Min Hold/Blank) based on the input booleans.
    3. Logs success or failure for each trace mode. Adds small delays after each write.

    Outputs of this function:
    - bool: True if all trace modes were set successfully, False otherwise.

    (2025-07-31 16:15) Change: New function created to handle trace modes independently.
    (2025-07-31 16:40) Change: Added small delays after each write to ensure instrument processing.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = f"utils/utils_markers.py - {current_version}"
    debug_print(f"Applying trace modes: Live: {live_mode}, MaxHold: {max_hold_mode}, MinHold: {min_hold_mode}", file=current_file, function=current_function, console_print_func=console_print_func)

    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot set trace modes.")
        debug_print("Instrument not connected for set_trace_modes_logic. Fucking useless!", file=current_file, function=current_function, console_print_func=console_print_func)
        return False

    success = True

    # Apply Trace Modes
    # Ensure only the selected mode is active, and others are blanked.
    if live_mode:
        if not write_safe(inst, ":TRAC1:MODE WRITe", console_print_func): success = False
        console_print_func("✅ Trace 1 set to Live (WRITe).")
    else:
        if not write_safe(inst, ":TRAC1:MODE BLANK", console_print_func): success = False
        console_print_func("ℹ️ Trace 1 set to BLANK.")
    time.sleep(0.05) # Small delay

    if max_hold_mode:
        if not write_safe(inst, ":TRAC2:MODE MAXHold", console_print_func): success = False
        console_print_func("✅ Trace 2 set to Max Hold.")
    else:
        if not write_safe(inst, ":TRAC2:MODE BLANK", console_print_func): success = False
        console_print_func("ℹ️ Trace 2 set to BLANK.")
    time.sleep(0.05) # Small delay

    if min_hold_mode:
        if not write_safe(inst, ":TRAC3:MODE MINHold", console_print_func): success = False
        console_print_func("✅ Trace 3 set to Min Hold.")
    else:
        if not write_safe(inst, ":TRAC3:MODE BLANK", console_print_func): success = False
        console_print_func("ℹ️ Trace 3 set to BLANK.")
    time.sleep(0.05) # Small delay


    if success:
        console_print_func("✅ Trace modes applied.")
        debug_print("Trace modes applied successfully.", file=current_file, function=current_function, console_print_func=console_print_func)
    else:
        console_print_func("❌ Failed to apply trace modes. This is a goddamn mess!", file=current_file, function=current_function, console_print_func=console_print_func)
    return success


def blank_hold_traces_logic(inst, console_print_func):
    """
    Function Description:
    Blanks (turns off) Max Hold and Min Hold traces on the instrument.
    Live trace is not affected. Adds small delays after each write.

    Inputs to this function:
    - inst (pyvisa.resources.Resource): The PyVISA instrument object.
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Checks if the instrument is connected.
    2. Sends SCPI commands to set Trace 2 and Trace 3 to BLANK mode.
    3. Logs the action. Adds small delays after each write.

    Outputs of this function:
    - bool: True if blanking commands were sent successfully, False otherwise.

    (2025-07-31 16:30) Change: New function to specifically blank hold traces.
    (2025-07-31 16:40) Change: Added small delays after each write to ensure instrument processing.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = f"utils/utils_markers.py - {current_version}"
    debug_print("Attempting to blank Max Hold and Min Hold traces.", file=current_file, function=current_function, console_print_func=console_print_func)

    if not inst:
        debug_print("Instrument not connected. Cannot blank hold traces.", file=current_file, function=current_function, console_print_func=console_print_func)
        return False

    success = True
    if not write_safe(inst, ":TRAC2:MODE BLANK", console_print_func): success = False
    time.sleep(0.05) # Small delay
    if not write_safe(inst, ":TRAC3:MODE BLANK", console_print_func): success = False
    time.sleep(0.05) # Small delay

    if success:
        console_print_func("ℹ️ Max Hold and Min Hold traces blanked.")
        debug_print("Max Hold and Min Hold traces blanked successfully.", file=current_file, function=current_function, console_print_func=console_print_func)
    else:
        console_print_func("❌ Failed to blank Max Hold or Min Hold traces.")
        debug_print("Failed to blank Max Hold or Min Hold traces. What the hell?!", file=current_file, function=current_function, console_print_func=console_print_func)
    return success


def set_marker_logic(inst, frequency_hz, marker_name, console_print_func):
    """
    Function Description:
    Sets a marker on the instrument to the specified frequency and enables it.
    This function now only sets the marker and does NOT query its Y value.

    Inputs to this function:
    - inst (pyvisa.resources.Resource): The PyVISA instrument object.
    - frequency_hz (float): The desired marker frequency in Hz.
    - marker_name (str): A descriptive name for the marker (for logging).
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Checks if the instrument is connected.
    2. Sends SCPI commands to turn Marker 1 ON and set its X (frequency) value.
    3. Logs success or failure. It does NOT query the Y value.

    Outputs of this function:
    - bool: True if the marker was set successfully, False otherwise.

    (2025-07-31 16:15) Change: Modified to only set the marker; removed Y-value query.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = f"utils/utils_markers.py - {current_version}"
    debug_print(f"Setting marker to {frequency_hz} Hz for '{marker_name}'...", file=current_file, function=current_function, console_print_func=console_print_func)

    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot set marker.")
        debug_print("Instrument not connected for set_marker_logic. Fucking useless!", file=current_file, function=current_function, console_print_func=console_print_func)
        return False

    success = True

    try:
        # Ensure Marker 1 is ON
        if not write_safe(inst, ":CALCulate:MARKer1:STATe ON", console_print_func): success = False
        time.sleep(0.05) # Small delay

        # Set Marker 1 to the specified frequency
        if not write_safe(inst, f":CALCulate:MARKer1:X {frequency_hz}", console_print_func): success = False
        time.sleep(0.05) # Small delay

        if success:
            console_print_func(f"✅ Marker set to {frequency_hz / MHZ_TO_HZ:.3f} MHz.")
            debug_print(f"Marker 1 set to {frequency_hz} Hz.", file=current_file, function=current_function, console_print_func=console_print_func)
        else:
            console_print_func(f"❌ Failed to set marker for {marker_name}.")
            debug_print(f"Failed to set marker for {marker_name}. This bugger is being problematic!", file=current_file, function=current_function, console_print_func=console_print_func)
        return success
    except Exception as e:
        console_print_func(f"❌ Error setting marker: {e}")
        debug_print(f"Error setting marker: {e}. What the hell is its problem?!", file=current_file, function=current_function, console_print_func=console_print_func)
        return False
