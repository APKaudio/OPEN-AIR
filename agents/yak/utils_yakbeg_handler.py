# yak/utils_yaknab_handler.py
#
# This file provides handler functions for new "NAB" commands. These commands
# are designed for efficient, single-query retrieval of multiple instrument settings.
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
# Version 20250821.210502.1
# UPDATED: Added new handler for Amplitude settings.
# FIXED: Corrected the parsing logic to handle both float and string responses for boolean-like settings.
# UPDATED: The function now handles a 5th return value for Sweep Time.
# NEW: Implemented a new handler for the TRACE/ALL/ONETWOTHREE NAB command, designed to handle multiple reads for large data sets.
# UPDATED: All debug messages now include the required 🐐 emoji at the start.

import inspect
import os
import numpy as np
from typing import Optional, List, Dict

from yak.Yakety_Yak import YakBeg, YakNab
from display.debug_logic import debug_log
from display.console_logic import console_log

# --- Versioning ---
w = 20250821
x_str = '210502'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"


# Helper conversion function
MHZ_TO_HZ = 1000000

def handle_freq_start_stop_beg(app_instance, start_freq, stop_freq, console_print_func):
    # Function Description:
    # Handles the extended YakBeg command for FREQUENCY/START-STOP.
    # It now returns start, stop, center, and span frequencies.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering {current_function}. Arrr, a treasure map for frequencies! 🗺️",
                file=current_file,
                version=current_version,
                function=current_function)
    
    # We send start and stop, and get back start, stop, span, and center
    response = YakBeg(app_instance, "FREQUENCY/START-STOP", console_print_func, start_freq, stop_freq)
    
    if response and response != "FAILED":
        try:
            # Response is a semicolon-separated string of four values
            parts = response.split(';')
            if len(parts) == 4:
                start = float(parts[0])
                stop = float(parts[1])
                span = float(parts[2])
                center = float(parts[3])
                debug_log(f"🐐 ✅ Processed response: start={start}, stop={stop}, span={span}, center={center}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
                return start, stop, span, center
        except (ValueError, IndexError) as e:
            console_print_func(f"❌ Failed to parse response from instrument for multiple traces. Error: {e}")
            debug_log(f"🐐 ❌ Arrr, the response be gibberish! Error: {e}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
    return None, None, None, None

def handle_freq_center_span_beg(app_instance, center_freq, span_freq, console_print_func):
    # Function Description:
    # Handles the extended YakBeg command for FREQUENCY/CENTER-SPAN.
    # It now returns center, span, start, and stop frequencies.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering {current_function}. Plotting a course to the center! 🧭",
                file=current_file,
                version=current_version,
                function=current_function)
    
    # We send center and span, and get back span, center, start, and stop
    response = YakBeg(app_instance, "FREQUENCY/CENTER-SPAN", console_print_func, center_freq, span_freq)
    
    if response and response != "FAILED":
        try:
            # Response is a semicolon-separated string of four values
            parts = response.split(';')
            if len(parts) == 4:
                # FIXED: Correct parsing order to match the VISA response
                span = float(parts[0])
                center = float(parts[1])
                start = float(parts[2])
                stop = float(parts[3])
                debug_log(f"🐐 ✅ Processed response: center={center}, span={span}, start={start}, stop={stop}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
                return center, span, start, stop
        except (ValueError, IndexError) as e:
            console_print_func(f"❌ Failed to parse response from instrument for multiple traces. Error: {e}")
            debug_log(f"🐐 ❌ Arrr, the response be gibberish! Error: {e}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
    return None, None, None, None

def handle_marker_place_all_beg(app_instance, marker_freqs_MHz, console_print_func):
    # Function Description:
    # Handles the YakBeg command for MARKER/PLACE/ALL.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering {current_function}. Parameters: marker_freqs_MHz={marker_freqs_MHz}",
                file=current_file,
                version=current_version,
                function=current_function)
    
    if not app_instance.inst:
        console_print_func("❌ No instrument connected. Cannot set markers.")
        debug_log("🐐 ❌ No instrument connected. Aborting marker operation.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return "FAILED"

    marker_freqs_hz = []
    for freq in marker_freqs_MHz:
        try:
            marker_freqs_hz.append(int(float(freq) * MHZ_TO_HZ))
        except ValueError:
            console_print_func(f"❌ Invalid marker frequency entered: '{freq}'. Must be a number.")
            debug_log(f"🐐 🚫 Invalid marker frequency entered: '{freq}'. Aborting YakBeg.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return "FAILED"

    response = YakBeg(app_instance, "MARKER/PLACE/ALL", console_print_func, *marker_freqs_hz)
    
    debug_log(f"🐐 ✅ Marker operation complete. Response: {response}. ✅",
                file=current_file,
                version=current_version,
                function=current_function)
    return response

def handle_trace_modes_beg(app_instance, trace_modes, console_print_func):
    # Function Description:
    # Handles the YakBeg command for TRACE/MODES.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering {current_function}",
                file=current_file,
                version=current_version,
                function=current_function)
    response = YakBeg(app_instance, "TRACE/MODES", console_print_func, *trace_modes)
    debug_log(f"🐐 ✅ Trace mode operation complete. Response: {response}. ✅",
                file=current_file,
                version=current_version,
                function=current_function)
    return response

def handle_trace_data_beg(app_instance, trace_number, start_freq_MHz, stop_freq_MHz, console_print_func):
    # Function Description:
    # Handles the YakBeg command for TRACE/DATA, including parsing and returning data.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering {current_function}",
                file=current_file,
                version=current_version,
                function=current_function)
    
    command_type = f"TRACE/{trace_number}/DATA"
    start_freq_hz = int(start_freq_MHz * MHZ_TO_HZ)
    stop_freq_hz = int(stop_freq_MHz * MHZ_TO_HZ)

    response_string = YakBeg(app_instance, command_type, console_print_func, start_freq_hz, stop_freq_hz)

    if response_string and response_string != "FAILED":
        try:
            values = [float(val.strip()) for val in response_string.split(',') if val.strip()]
            num_points = len(values)
            if num_points > 0:
                frequencies = np.linspace(start_freq_hz, stop_freq_hz, num_points)
                debug_log(f"🐐 ✅ Successfully parsed {num_points} data points from trace response.",
                            file=current_file,
                            version=current_version,
                            function=current_function)
                return list(zip(frequencies / MHZ_TO_HZ, values))
        except (ValueError, IndexError, TypeError) as e:
            console_print_func(f"❌ Failed to parse trace data: {e}. What a disaster!")
            debug_log(f"🐐 ❌ Failed to parse trace data string. Error: {e}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
    return None
