# tabs/Instrument/utils_instrument_query_settings.py
#
# This module provides a low-level function for querying current settings
# from a connected VISA instrument, specifically focusing on Center Frequency,
# Span, and Resolution Bandwidth (RBW).
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
# Version 20250802.1701.8 (Refactored from utils_instrument_control.py to handle query settings logic.)

current_version = "20250802.1701.8" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 1701 * 8 # Example hash, adjust as needed

import pyvisa
import inspect # Import inspect module
import os # Import os module to fix NameError

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Import read/write safe functions from the new dedicated module
from tabs.Instrument.utils_instrument_read_and_write import query_safe

# Constants for frequency conversion (needed by this module)
MHZ_TO_HZ_CONVERSION = 1_000_000


def query_current_instrument_settings(inst, MHZ_TO_HZ_CONVERSION, console_print_func=None):
    """
    Function Description:
    Queries and returns the current Center Frequency, Span, and RBW from the instrument.

    Inputs:
        inst (pyvisa.resources.Resource): The connected VISA instrument object.
        MHZ_TO_HZ_CONVERSION (float): The conversion factor from MHz to Hz.
        console_print_func (function, optional): Function to print to the GUI console.
                                               Defaults to console_log if None.
    Outputs:
        tuple: (center_freq_mhz, span_mhz, rbw_hz) or (None, None, None) on failure.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Querying current instrument settings... Let's see what's happening!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    if not inst:
        debug_log("No instrument connected to query settings. Fucking useless!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        console_print_func("⚠️ Warning: No instrument connected. Cannot query settings. Connect the damn thing first!")
        return None, None, None

    center_freq_hz = None
    span_hz = None
    rbw_hz = None

    try:
        # Query Center Frequency
        center_freq_str = query_safe(inst, ":SENSe:FREQuency:CENTer?", console_print_func)
        if center_freq_str:
            center_freq_hz = float(center_freq_str)

        # Query Span
        span_str = query_safe(inst, ":SENSe:FREQuency:SPAN?", console_print_func)
        if span_str:
            span_hz = float(span_str)

        # Query RBW
        rbw_str = query_safe(inst, ":SENSe:BANDwidth:RESolution?", console_print_func)
        if rbw_str:
            rbw_hz = float(rbw_str)

        center_freq_mhz = center_freq_hz / MHZ_TO_HZ_CONVERSION if center_freq_hz is not None else None
        span_mhz = span_hz / MHZ_TO_HZ_CONVERSION if span_hz is not None else None

        debug_log(f"Queried settings: Center Freq: {center_freq_mhz:.3f} MHz, Span: {span_mhz:.3f} MHz, RBW: {rbw_hz} Hz. Got the info!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        console_print_func(f"✅ Queried settings: C: {center_freq_mhz:.3f} MHz, SP: {span_mhz:.3f} MHz, RBW: {rbw_hz / 1000:.1f} kHz. Details acquired!")

        return center_freq_mhz, span_mhz, rbw_hz

    except Exception as e:
        debug_log(f"❌ Error querying current instrument settings: {e}. What a mess!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        console_print_func(f"❌ Error querying current instrument settings: {e}. This is a disaster!")
        return None, None, None
