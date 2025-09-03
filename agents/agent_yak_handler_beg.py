# agents/agent_yak_handler_beg.py
#
# This handler is responsible for processing 'BEG' (Beg) type SCPI commands.
# It handles the construction of a single command string that performs both a SET
# and a subsequent GET, returning the response from the instrument.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250902.115600.1

import inspect
import os
import numpy as np

from workers.worker_logging import debug_log, console_log
from agents.agent_YaketyYak import YakBeg

# --- Global Scope Variables ---
current_version = "20250902.115600.1"
current_version_hash = (20250902 * 115600 * 1)
current_file = f"{os.path.basename(__file__)}"
MHZ_TO_HZ = 1000000

def handle_beg_command(dispatcher, command_type, *variable_values):
    """
    Handles a 'BEG' command by combining a SET command with a GET query.
    """
    # This function is not used in this file's refactored logic, but it's kept for the dispatcher.
    pass

def YakBeg_freq_start_stop(app_instance, start_freq, stop_freq, console_print_func):
    """
    Handles the extended YakBeg command for FREQUENCY/START-STOP.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering {current_function}. Arrr, a treasure map for frequencies! 🗺️",
                file=current_file,
                version=current_version,
                function=current_function)

    response = YakBeg(app_instance, "FREQUENCY/START-STOP", console_print_func, start_freq, stop_freq)

    # The parsing logic will be handled by the caller.
    return response

def YakBeg_freq_center_span(app_instance, center_freq, span_freq, console_print_func):
    """
    Handles the extended YakBeg command for FREQUENCY/CENTER-SPAN.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering {current_function}. Plotting a course to the center! 🧭",
                file=current_file,
                version=current_version,
                function=current_function)

    response = YakBeg(app_instance, "FREQUENCY/CENTER-SPAN", console_print_func, center_freq, span_freq)

    # The parsing logic will be handled by the caller.
    return response

def YakBeg_marker_place_all(app_instance, marker_freqs_MHz, console_print_func):
    """
    Handles the YakBeg command for MARKER/PLACE/ALL.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 Entering {current_function}. Parameters: marker_freqs_MHz={marker_freqs_MHz}",
                file=current_file,
                version=current_version,
                function=current_function)

    if not app_instance.inst:
        console_print_func("❌ No instrument connected. Cannot set markers.")
        return "FAILED"

    marker_freqs_hz = []
    try:
        for freq in marker_freqs_MHz:
            marker_freqs_hz.append(int(float(freq) * MHZ_TO_HZ))
    except ValueError:
        console_print_func(f"❌ Invalid marker frequency entered: '{freq}'. Must be a number.")
        return "FAILED"

    response = YakBeg(app_instance, "MARKER/PLACE/ALL", console_print_func, *marker_freqs_hz)

    debug_log(f"🐐 ✅ Marker operation complete. Response: {response}. ✅",
                file=current_file,
                version=current_version,
                function=current_function)
    return response

def YakBeg_trace_modes(app_instance, trace_modes, console_print_func):
    """
    Handles the YakBeg command for TRACE/MODES.
    """
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

def YakBeg_trace_data(app_instance, trace_number, start_freq_MHz, stop_freq_MHz, console_print_func):
    """
    Handles the YakBeg command for TRACE/DATA, including parsing and returning data.
    """
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
