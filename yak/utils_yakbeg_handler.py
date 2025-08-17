# tabs/Instrument/utils_yakbeg_handler.py
#
# This file provides a set of handler functions for the YakBegTab. These functions
# encapsulate the core logic for testing the new YakBeg functionality, including
# setting and getting frequency, trace modes, marker data, and trace data.
# This file decouples the UI from the business logic, making the code more
# modular and easier to maintain.
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
# Version 20250818.201500.5
# FIX: Corrected the parsing order for handle_freq_center_span_beg to match the VISA response.
# NEW: Added a new handler function handle_all_traces_nab to retrieve data for three traces at once.

current_version = "20250818.201500.5"
current_version_hash = (20250818 * 201500 * 5)

import inspect
import os
import numpy as np
from typing import Optional, List, Dict

from yak.Yakety_Yak import YakBeg, YakNab
from display.debug_logic import debug_log
from display.console_logic import console_log


# Helper conversion function
MHZ_TO_HZ = 1000000

def handle_freq_start_stop_beg(app_instance, start_freq, stop_freq, console_print_func):
    # Function Description:
    # Handles the extended YakBeg command for FREQUENCY/START-STOP.
    # It now returns start, stop, center, and span frequencies.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Arrr, a treasure map for frequencies! 🗺️",
                file=os.path.basename(__file__),
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
                return start, stop, span, center
        except (ValueError, IndexError) as e:
            console_print_func(f"❌ Failed to parse response from instrument. Error: {e}")
            debug_log(f"Arrr, the response be gibberish! Error: {e}",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
    return None, None, None, None

def handle_freq_center_span_beg(app_instance, center_freq, span_freq, console_print_func):
    # Function Description:
    # Handles the extended YakBeg command for FREQUENCY/CENTER-SPAN.
    # It now returns center, span, start, and stop frequencies.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Plotting a course to the center! 🧭",
                file=os.path.basename(__file__),
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
                return center, span, start, stop
        except (ValueError, IndexError) as e:
            console_print_func(f"❌ Failed to parse response from instrument. Error: {e}")
            debug_log(f"Arrr, the response be gibberish! Error: {e}",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
    return None, None, None, None

def handle_marker_place_all_beg(app_instance, marker_freqs_mhz, console_print_func):
    # Function Description:
    # Handles the YakBeg command for MARKER/PLACE/ALL.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Parameters: marker_freqs_mhz={marker_freqs_mhz}",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)
    
    if not app_instance.inst:
        console_print_func("❌ No instrument connected. Cannot set markers.")
        debug_log("No instrument connected. Aborting marker operation.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        return "FAILED"

    marker_freqs_hz = []
    for freq in marker_freqs_mhz:
        try:
            marker_freqs_hz.append(int(float(freq) * MHZ_TO_HZ))
        except ValueError:
            console_print_func(f"❌ Invalid marker frequency entered: '{freq}'. Must be a number.")
            debug_log(f"Invalid marker frequency entered: '{freq}'. Aborting YakBeg.",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            return "FAILED"

    response = YakBeg(app_instance, "MARKER/PLACE/ALL", console_print_func, *marker_freqs_hz)
    
    debug_log(f"Marker operation complete. Response: {response}. ✅",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)
    return response

def handle_trace_modes_beg(app_instance, trace_modes, console_print_func):
    # Function Description:
    # Handles the YakBeg command for TRACE/MODES.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)
    response = YakBeg(app_instance, "TRACE/MODES", console_print_func, *trace_modes)
    return response

def handle_trace_data_beg(app_instance, trace_number, start_freq_mhz, stop_freq_mhz, console_print_func):
    # Function Description:
    # Handles the YakBeg command for TRACE/DATA, including parsing and returning data.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)
    
    command_type = f"TRACE/{trace_number}/DATA"
    start_freq_hz = int(start_freq_mhz * MHZ_TO_HZ)
    stop_freq_hz = int(stop_freq_mhz * MHZ_TO_HZ)

    response_string = YakBeg(app_instance, command_type, console_print_func, start_freq_hz, stop_freq_hz)

    if response_string and response_string != "FAILED":
        try:
            values = [float(val.strip()) for val in response_string.split(',') if val.strip()]
            num_points = len(values)
            if num_points > 0:
                frequencies = np.linspace(start_freq_hz, stop_freq_hz, num_points)
                return list(zip(frequencies / MHZ_TO_HZ, values))
        except (ValueError, IndexError, TypeError) as e:
            console_print_func(f"❌ Failed to parse trace data: {e}. What a disaster!")
    return None
def handle_all_traces_nab(app_instance, console_print_func) -> Optional[Dict]:
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Retrieving multiple traces with a single NAB command.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)

    # YakNab will now return a list of parsed strings from the single response
    response_list = YakNab(app_instance, "TRACE/ALL/ONETWOTHREE", console_print_func)

    # ADDED: Debug message to show the raw response and its type
    debug_log(f"Response from YakNab: {response_list}", 
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function, special=True)
    debug_log(f"Type of response: {type(response_list)}", 
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function, special=True)

    # FIX: Change the conditional to check if it's a list, not a string
    if response_list and isinstance(response_list, list) and len(response_list) == 5:
        try:
            start_freq_hz = float(response_list[0])
            stop_freq_hz = float(response_list[1])
            
            trace_data = {}
            for i in range(1, 4):
                trace_string = response_list[i + 1]
                values = [float(val.strip()) for val in trace_string.split(',') if val.strip()]
                num_points = len(values)
                
                if num_points > 0:
                    frequencies = np.linspace(start_freq_hz, stop_freq_hz, num_points)
                    trace_data[f"Trace{i}"] = list(zip(frequencies / MHZ_TO_HZ, values))
                else:
                    trace_data[f"Trace{i}"] = []

            console_log("✅ Successfully retrieved and parsed data for three traces.")
            debug_log(f"Successfully retrieved traces. What a haul! 🎣",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
            return trace_data
        except (ValueError, IndexError, TypeError) as e:
            console_log(f"❌ Failed to parse response from instrument. Error: {e}")
            debug_log(f"Arrr, the response be gibberish! Error: {e}",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
    return None