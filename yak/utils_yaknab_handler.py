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
# Version 20250817.001000.5
# UPDATED: Added new handler for Amplitude settings.
# FIXED: Corrected the parsing logic to handle both float and string responses for boolean-like settings.
# UPDATED: The function now handles a 5th return value for Sweep Time.
# NEW: Implemented a new handler for the TRACE/ALL/ONETWOTHREE NAB command, designed to handle multiple reads for large data sets.

current_version = "20250817.001000.5"
current_version_hash = 20250817 * 1000 * 5

import inspect
import os
import numpy as np
from typing import Optional, List, Dict

from yak.Yakety_Yak import YakBeg, YakNab
from display.debug_logic import debug_log
from display.console_logic import console_log


# Helper conversion function
MHZ_TO_HZ = 1000000

def handle_bandwidth_settings_nab(app_instance, console_print_func) -> Optional[Dict]:
    """
    Function Description:
    Executes the "BANDWIDTH/SETTINGS" NAB command to retrieve multiple bandwidth
    settings in a single query. It returns a dictionary of the retrieved values.
    
    The corresponding NAB command can be found in `visa_commands.csv`.

    Inputs:
    - app_instance (object): A reference to the main application instance.
    - console_print_func (function): A function to print messages to the GUI console.

    Outputs:
    - dict: A dictionary containing the fetched settings, or None on failure.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Retrieving all bandwidth settings with a single NAB command. Let's make this snappy! ⚡",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
    
    response = YakNab(app_instance, "BANDWIDTH/SETTINGS", console_print_func)

    if response and isinstance(response, list) and len(response) == 5:
        try:
            # FIXED: Handle both string ('ON'/'OFF') and float (1.0/0.0) responses
            vbw_auto_on_value = response[2]
            continuous_mode_on_value = response[3]
            
            settings = {
                "RBW_Hz": float(response[0]),
                "VBW_Hz": float(response[1]),
                "VBW_Auto_On": vbw_auto_on_value == 'ON' or vbw_auto_on_value == '1' or float(vbw_auto_on_value) == 1.0,
                "Continuous_Mode_On": continuous_mode_on_value == 'ON' or continuous_mode_on_value == '1' or float(continuous_mode_on_value) == 1.0,
                "Sweep_Time_s": float(response[4])
            }
            console_print_func("✅ Successfully retrieved all bandwidth settings.")
            debug_log(f"Successfully retrieved bandwidth settings: {settings}. A truly magnificent feat! ✨",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
            return settings
        except (ValueError, IndexError) as e:
            console_print_func(f"❌ Failed to parse response from instrument for bandwidth settings. Error: {e}")
            debug_log(f"Arrr, the response be gibberish! Error: {e}",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
            return None
    
    console_log("❌ Failed to retrieve all bandwidth settings from instrument.")
    return None

def handle_amplitude_settings_nab(app_instance, console_print_func) -> Optional[Dict]:
    """
    Function Description:
    Executes a NAB command to retrieve multiple amplitude settings in a single query.
    It retrieves the Reference Level, Power Attenuation, and Preamp state.
    
    The corresponding NAB command can be found in `visa_commands.csv`.

    Inputs:
    - app_instance (object): A reference to the main application instance.
    - console_print_func (function): A function to print messages to the GUI console.

    Outputs:
    - dict: A dictionary containing the fetched settings, or None on failure.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Retrieving all amplitude settings with a single NAB command. A treasure hunt for data! 🗺️",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
    
    response = YakNab(app_instance, "AMPLITUDE/SETTINGS", console_print_func)

    if response and isinstance(response, list) and len(response) == 3:
        try:
            settings = {
                "Ref_Level_dBm": float(response[0]),
                "Attenuation_dB": float(response[1]),
                "Preamp_On": response[2].upper() == 'ON' or response[2] == '1'
            }
            console_print_func("✅ Successfully retrieved all amplitude settings.")
            debug_log(f"Successfully retrieved amplitude settings: {settings}. A truly magnificent feat! ✨",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
            return settings
        except (ValueError, IndexError) as e:
            console_print_func(f"❌ Failed to parse response from instrument for amplitude settings. Error: {e}")
            debug_log(f"Arrr, the response be gibberish! Error: {e}",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
            return None
    
    console_log("❌ Failed to retrieve all amplitude settings from instrument.")
    return None

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
            console_print_func(f"❌ Failed to parse response from instrument for multiple traces. Error: {e}")
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
            console_print_func(f"❌ Failed to parse response from instrument for multiple traces. Error: {e}")
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
    """
    Function Description:
    This handler executes the "TRACE/ALL/ONETWOTHREE" NAB command.
    It retrieves the start/stop frequencies, trace modes, and data for traces 1, 2, and 3
    in a single, efficient query. It then processes the complex response string into
    a structured dictionary of data and modes suitable for plotting or display.

    Inputs:
    - app_instance: The main application instance.
    - console_print_func: A function to print messages to the GUI console.

    Outputs:
    - Optional[Dict]: A dictionary with keys for "TraceData", "StartFreq", "StopFreq",
                      and "TraceModes" if successful.
                      Returns None on failure.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Retrieving multiple traces with a single NAB command.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
    
    try:
        # YakNab is called to send a single, combined query command.
        # It returns a single string with semicolon-separated values.
        response_string = YakNab(app_instance, "TRACE/ALL/ONETWOTHREE", console_print_func)
        
        # ADDED: A debug log to show the raw response string received from YakNab
        debug_log(f"Raw response from YakNab: {response_string}",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function, special=True)

        if response_string and isinstance(response_string, str) and response_string != "FAILED":
            # We now split the single response string into a list of its 8 components.
            response_list = response_string.split(';')

            # ADDED: A debug log to show the list after splitting
            debug_log(f"Response list after splitting: {response_list}",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function, special=True)

            # Now we validate the response to ensure it's a list of the correct length.
            if len(response_list) == 8:
                # The first two elements are start and stop frequencies.
                start_freq_hz = float(response_list[0])
                stop_freq_hz = float(response_list[1])

                # The next three elements are the modes for traces 1, 2, and 3.
                trace_modes = {
                    "Trace1": response_list[2],
                    "Trace2": response_list[3],
                    "Trace3": response_list[4],
                }

                trace_data = {}
                # The last three elements are the raw data for traces 1, 2, and 3.
                # We start the data parsing loop from index 5.
                for i in range(1, 4):
                    # The raw data for each trace is a single comma-separated string.
                    trace_string = response_list[i + 4]
                    # We parse the comma-separated string of amplitude values.
                    values = [float(val.strip()) for val in trace_string.split(',') if val.strip()]
                    num_points = len(values)

                    if num_points > 0:
                        # We create a frequency array corresponding to the number of data points.
                        frequencies = np.linspace(start_freq_hz, stop_freq_hz, num_points)
                        # The frequency array and amplitude values are combined into a list of tuples.
                        trace_data[f"Trace{i}"] = list(zip(frequencies / MHZ_TO_HZ, values))
                    else:
                        trace_data[f"Trace{i}"] = []

                console_log("✅ Successfully retrieved and parsed data for three traces.")
                debug_log(f"Successfully retrieved traces. What a haul! 🎣",
                          file=os.path.basename(__file__),
                          version=current_version,
                          function=current_function)

                # Return a single dictionary containing all the information.
                return {
                    "TraceData": trace_data,
                    "StartFreq": start_freq_hz,
                    "StopFreq": stop_freq_hz,
                    "TraceModes": trace_modes
                }
    
            else:
                # Log an error if the response has an unexpected number of elements.
                console_log(f"❌ Failed to parse response: Unexpected number of elements. Expected 8, got {len(response_list)}. 🤦‍♂️")
                debug_log(f"Arrr, the number of response elements be wrong! Expected 8, but got {len(response_list)}. ☠️",
                          file=os.path.basename(__file__),
                          version=current_version,
                          function=current_function)
    
        # This catch block handles errors in parsing the individual elements.
    except (ValueError, IndexError, TypeError) as e:
        console_log(f"❌ Failed to parse response from instrument for multiple traces. Error: {e}")
        debug_log(f"Arrr, the response be gibberish! Error: {e}",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

    # This is the fallback for any validation or parsing failure.
    return None