# agents/agent_yak_handler_get.py
#
# This handler is responsible for processing 'GET' type SCPI commands.
# It constructs the correct query string and retrieves data from the instrument,
# returning the raw response string.
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
# Version 20250902.114500.1

import inspect
from agents.agent_yak_dispatch_scpi import ScpiDispatcher

# --- Global Scope Variables ---
current_version = "20250902.114500.1"
current_version_hash = (20250902 * 114500 * 1)
current_file = f"{os.path.basename(__file__)}"

def handle_get_command(dispatcher: ScpiDispatcher, command_type):
    """
    Handles a 'GET' command by querying the instrument.
    """
    # ... logic from Yakety_Yak.py's YakGet function ...
    pass



def get_trace_data_logic(app_instance, console_print_func):
    """
    Function Description:
    Retrieves trace data for all active traces from the instrument.
    This function has been refactored to be more robust, checking for valid data and
    handling different trace modes with a simple update cycle counter.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 Getting trace data from the instrument.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot get trace data.")
        return False
    
    all_trace_data = []

    center_freq_hz = float(YakGet(app_instance, "FREQUENCY/CENTER", console_print_func))
    span_hz = float(YakGet(app_instance, "FREQUENCY/SPAN", console_print_func))
    start_freq_hz = center_freq_hz - (span_hz / 2)
    end_freq_hz = center_freq_hz + (span_hz / 2)

    for i in range(1, 5):
        command_type = f"TRACE/{i}/DATA"
        raw_data_string = YakGet(app_instance, command_type.upper(), console_print_func)
        
        if raw_data_string is not None and raw_data_string != "FAILED":
            processed_data = _process_trace_data(raw_data_string, start_freq_hz, end_freq_hz, console_print_func)
            if processed_data:
                all_trace_data.append(processed_data)
                console_print_func(f"✅ Trace {i} data received and processed.")
            else:
                all_trace_data.append(None)
                console_print_func(f"❌ Failed to process Trace {i} data.")
        else:
            all_trace_data.append(None)
            console_print_func(f"❌ Failed to retrieve Trace {i} data.")
    
    return all_trace_data
    
def get_trace_averaging_settings(app_instance, trace_number, console_print_func) -> (bool, int):
    """
    Function Description:
    Retrieves the averaging state and count for a specific trace using a single NAB command.
    
    Inputs:
    - app_instance (object): A reference to the main application instance.
    - trace_number (int): The number of the trace to query (1-4).
    - console_print_func (function): A function to print messages to the GUI console.
    
    Outputs:
    - (bool, int): A tuple containing the averaging state (True/False) and the count, or (None, None) on failure.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to retrieve averaging settings for trace {trace_number}.",
              file=current_file,
              version=current_version,
              function=current_function)
              
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot retrieve averaging settings.")
        return None, None

    command_type = "AVERAGE"
    
    response = YakNab(app_instance, command_type, console_print_func)
    
    if response and isinstance(response, list) and len(response) >= 2:
        try:
            state_str = response[0]
            count_str = response[1]
            
            is_on = state_str in ["ON", "1"]
            count = int(float(count_str))
            
            return is_on, count
        except (ValueError, IndexError, TypeError) as e:
            console_print_func(f"❌ Failed to parse averaging settings. Error: {e}")
            debug_log(f"🐐 ❌ Arrr, the response be gibberish! Error: {e}",
                      file=current_file,
                      version=current_version,
                      function=current_function)
    
    return None, None



def get_all_marker_values_logic(app_instance, console_print_func):
    """
    Retrieves and returns the X and Y values for all active markers.
    Returns a list of tuples: [(x1, y1), (x2, y2), ...]
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 Getting all marker values from the instrument.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot read markers.")
        return None
    
    marker_values = []
    for i in range(1, 7):
        marker_state = YakGet(app_instance, f"MARKER/{i}/CALCULATE/STATE", console_print_func)
        if marker_state in ["ON", "1"]:
            x_value = YakGet(app_instance, f"MARKER/{i}/CALCULATE/X", console_print_func)
            y_value = YakGet(app_instance, f"MARKER/{i}/CALCULATE/Y", console_print_func)

            try:
                x_value_MHz = float(x_value) / MHZ_TO_HZ_CONVERSION
                y_value_dBm = float(y_value)
                marker_values.append((x_value_MHz, y_value_dBm))
            except (ValueError, TypeError):
                console_print_func(f"⚠️ Could not parse marker {i} values.")
                debug_log(f"🐐 ❌ Failed to parse marker {i} values. What a mess!",
                          file=current_file,
                          version=current_version,
                          function=current_function)
                marker_values.append((None, None))
    
    return marker_values







def _process_trace_data(raw_data_string, start_freq_hz, end_freq_hz, console_print_func):
    """
    Function Description:
    Processes a raw comma-separated string of trace amplitude data into
    a list of (frequency, amplitude) pairs.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 Processing raw trace data into frequency/amplitude pairs. This is a crucial step.",
              file=current_file,
              version=current_version,
              function=current_function)

    if not raw_data_string or "FAILED" in raw_data_string:
        console_print_func("❌ Received invalid data from the instrument. Cannot process trace.")
        return None

    try:
        amplitudes_dBm = [float(val) for val in raw_data_string.split(',')]
        
        num_points = len(amplitudes_dBm)
        if num_points <= 1:
            console_print_func("⚠️ Received insufficient data points from the instrument. Cannot create a meaningful trace.")
            return None
            
        freq_points = np.linspace(start_freq_hz, end_freq_hz, num_points)
        
        processed_data = list(zip(freq_points / MHZ_TO_HZ_CONVERSION, amplitudes_dBm))

        debug_log(f"🐐 ✅ Successfully processed trace data. First 5 points: {processed_data[:5]}...",
                  file=current_file,
                  version=current_version,
                  function=current_function)
        
        return processed_data

    except ValueError as e:
        console_print_func(f"❌ Failed to parse trace data string. Error: {e}")
        debug_log(f"🐐 ❌ ValueError: could not convert string to float. Failed to parse data string. Error: {e}",
                  file=current_file,
                  version=current_version,
                  function=current_function, special=True)
        return None
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred while processing trace data: {e}")
        debug_log(f"🐐 🧨 An unexpected error occurred: {e}",
                  file=current_file,
                  version=current_version,
                  function=current_function, special=True)
        return None

