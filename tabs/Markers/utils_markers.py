# tabs/Markers/utils_markers.py
#
# This file contains utility functions for controlling the instrument, specifically
# for setting frequency, span, RBW, and trace modes. It provides a clean interface
# for sending SCPI commands and returning the status of the operation. The functions
# in this file DO NOT communicate with the GUI directly.
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
# Version 20250814.002800.2 (FIXED: Added missing 'console_print_func' argument to all YakSet calls to resolve a TypeError.)

current_version = "20250814.002800.2"
current_version_hash = (20250814 * 2800 * 2)

import os
import inspect
import time

from display.debug_logic import debug_log
from ref.frequency_bands import MHZ_TO_HZ

from tabs.Instrument.Yakety_Yak import YakSet

# Predefined options for common controls
SPAN_OPTIONS = {
    "10 kHz": 10000.0,
    "100 kHz": 100000.0,
    "1 MHz": 1000000.0,
    "10 MHz": 10000000.0,
    "100 MHz": 100000000.0,
    "1000 MHz": 1000000000.0,
    "5000 MHz": 5000000000.0
}

RBW_OPTIONS = {
    "1 Hz": 1.0,
    "10 Hz": 10.0,
    "100 Hz": 100.0,
    "1 kHz": 1000.0,
    "3 kHz": 3000.0,
    "10 kHz": 10000.0,
    "30 kHz": 30000.0,
    "100 kHz": 100000.0,
    "300 kHz": 300000.0,
    "1 MHz": 1000000.0,
}


def set_frequency_logic(app_instance, frequency_hz, console_print_func):
    # Function Description:
    # Sets the instrument's center frequency using the YakSet command.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Setting center frequency to {frequency_hz} Hz using YakSet.",
              file=f"{os.path.basename(__file__)} & {current_version}",
              version=current_version,
              function=current_function)

    status = YakSet(app_instance=app_instance, command_type="FREQUENCY/CENTER", variable_value=str(frequency_hz), console_print_func=console_print_func)
    if status == "PASSED":
        return True, f"✅ Instrument center frequency set to {frequency_hz / MHZ_TO_HZ:.3f} MHz."
    else:
        return False, f"❌ Failed to set center frequency."


def set_span_logic(app_instance, span_hz, console_print_func):
    # Function Description:
    # Sets the instrument's span frequency using the YakSet command.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Setting span frequency to {span_hz} Hz using YakSet.",
              file=f"{os.path.basename(__file__)} & {current_version}",
              version=current_version,
              function=current_function)

    status = YakSet(app_instance=app_instance, command_type="FREQUENCY/SPAN", variable_value=str(span_hz), console_print_func=console_print_func)
    if status == "PASSED":
        return True, f"✅ Instrument span set to {span_hz / MHZ_TO_HZ:.3f} MHz."
    else:
        return False, f"❌ Failed to set span frequency."


def set_rbw_logic(app_instance, rbw_hz, console_print_func):
    # Function Description:
    # Sets the instrument's Resolution Bandwidth (RBW) using the YakSet command.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Setting RBW to {rbw_hz} Hz using YakSet. That's a good RBW!",
              file=f"{os.path.basename(__file__)} & {current_version}",
              version=current_version,
              function=current_function)

    status = YakSet(app_instance=app_instance, command_type="RBW/MANUAL", variable_value=str(rbw_hz), console_print_func=console_print_func)
    if status == "PASSED":
        return True, f"✅ Instrument RBW set to {rbw_hz / 1000:.0f} kHz."
    else:
        return False, f"❌ Failed to set RBW."


def set_trace_modes_logic(app_instance, live_mode, max_hold_mode, min_hold_mode, console_print_func):
    # Function Description:
    # Sets the trace modes (live, max hold, min hold) using individual YakSet commands.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Setting trace modes: Live={live_mode}, MaxHold={max_hold_mode}, MinHold={min_hold_mode}.",
              file=f"{os.path.basename(__file__)} & {current_version}",
              version=current_version,
              function=current_function)

    status_live = YakSet(app_instance=app_instance, command_type="TRACE/MODE", variable_value=f"{'LIVE' if live_mode else 'OFF'}", console_print_func=console_print_func)
    status_max = YakSet(app_instance=app_instance, command_type="TRACE/MODE/MAX", variable_value=f"{'MAX HOLD' if max_hold_mode else 'OFF'}", console_print_func=console_print_func)
    status_min = YakSet(app_instance=app_instance, command_type="TRACE/MODE/MIN", variable_value=f"{'MIN HOLD' if min_hold_mode else 'OFF'}", console_print_func=console_print_func)

    if status_live == "PASSED" and status_max == "PASSED" and status_min == "PASSED":
        return True, f"✅ Trace modes updated."
    else:
        return False, f"❌ Failed to update trace modes."


def set_marker_logic(app_instance, frequency_hz, console_print_func):
    # Function Description:
    # Places a single marker at the specified frequency using the YakSet command.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Setting marker to {frequency_hz} Hz. This is going to be good!",
              file=f"{os.path.basename(__file__)} & {current_version}",
              version=current_version,
              function=current_function)

    # We set the marker state and then the frequency
    status_state = YakSet(app_instance=app_instance, command_type="MARKER/1/STATE", variable_value="ON", console_print_func=console_print_func)
    status_freq = YakSet(app_instance=app_instance, command_type="MARKER/1/X", variable_value=str(frequency_hz), console_print_func=console_print_func)

    if status_state == "PASSED" and status_freq == "PASSED":
        return True, f"✅ Marker 1 set to {frequency_hz / MHZ_TO_HZ:.3f} MHz."
    else:
        return False, f"❌ Failed to set marker 1."


def blank_hold_traces_logic(app_instance, console_print_func):
    """
    Blanks the Max Hold and Min Hold traces.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Blanks Max Hold and Min Hold traces. This should clear out old data for a fresh start.",
              file=f"{os.path.basename(__file__)} & {current_version}",
              version=current_version,
              function=current_function)

    status_max = YakSet(app_instance=app_instance, command_type="TRACE/MODE/MAX", variable_value="CLEAR", console_print_func=console_print_func)
    status_min = YakSet(app_instance=app_instance, command_type="TRACE/MODE/MIN", variable_value="CLEAR", console_print_func=console_print_func)
    
    if status_max == "PASSED" and status_min == "PASSED":
        return True, f"✅ Hold traces cleared."
    else:
        return False, f"❌ Failed to clear hold traces."