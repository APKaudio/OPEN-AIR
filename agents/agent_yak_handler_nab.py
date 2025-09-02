

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
    debug_log(f"🐐 🟢 Entering {current_function}. Retrieving all bandwidth settings with a single NAB command. Let's make this snappy! ⚡",
              file=current_file,
              version=current_version,
              function=current_function)
    
    response = YakNab(app_instance, "BANDWIDTH/SETTINGS", console_print_func)

    if response and isinstance(response, list) and len(response) == 5:
        try:
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
            debug_log(f"🐐 ✅ Successfully retrieved bandwidth settings: {settings}. A truly magnificent feat! ✨",
                      file=current_file,
                      version=current_version,
                      function=current_function)
            return settings
        except (ValueError, IndexError) as e:
            console_print_func(f"❌ Failed to parse response from instrument for bandwidth settings. Error: {e}")
            debug_log(f"🐐 ❌ Arrr, the response be gibberish! Error: {e}",
                      file=current_file,
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
    debug_log(f"🐐 🟢 Entering {current_function}. Retrieving all amplitude settings with a single NAB command. A treasure hunt for data! 🗺️",
              file=current_file,
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
            debug_log(f"🐐 ✅ Successfully retrieved amplitude settings: {settings}. A truly magnificent feat! ✨",
                      file=current_file,
                      version=current_version,
                      function=current_function)
            return settings
        except (ValueError, IndexError) as e:
            console_print_func(f"❌ Failed to parse response from instrument for amplitude settings. Error: {e}")
            debug_log(f"🐐 ❌ Arrr, the response be gibberish! Error: {e}",
                      file=current_file,
                      version=current_version,
                      function=current_function)
            return None
    
    console_log("❌ Failed to retrieve all amplitude settings from instrument.")
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
    debug_log(f"🐐 🟢 Entering {current_function}. Retrieving multiple traces with a single NAB command.",
              file=current_file,
              version=current_version,
              function=current_function)

    response_list = YakNab(app_instance, "TRACE/ALL/ONETWOTHREE", console_print_func)

    if response_list and isinstance(response_list, list) and len(response_list) == 8:
        try:
            start_freq_hz = float(response_list[0])
            stop_freq_hz = float(response_list[1])

            trace_modes = {
                "Trace1": response_list[2],
                "Trace2": response_list[3],
                "Trace3": response_list[4],
            }

            trace_data = {}
            for i in range(1, 4):
                trace_string = response_list[i + 4]
                values = [float(val.strip()) for val in trace_string.split(',') if val.strip()]
                num_points = len(values)

                if num_points > 0:
                    frequencies = np.linspace(start_freq_hz, stop_freq_hz, num_points)
                    trace_data[f"Trace{i}"] = list(zip(frequencies / MHZ_TO_HZ, values))
                else:
                    trace_data[f"Trace{i}"] = []

            console_log("✅ Successfully retrieved and parsed data for three traces.")
            debug_log(f"🐐 ✅ Successfully retrieved traces. What a haul! 🎣",
                      file=current_file,
                      version=current_version,
                      function=current_function)

            return {
                "TraceData": trace_data,
                "StartFreq": start_freq_hz,
                "StopFreq": stop_freq_hz,
                "TraceModes": trace_modes
            }

        except (ValueError, IndexError, TypeError) as e:
            console_log(f"❌ Failed to parse response from instrument for multiple traces. Error: {e}")
            debug_log(f"🐐 ❌ Arrr, the response be gibberish! Error: {e}",
                      file=current_file,
                      version=current_version,
                      function=current_function)
    return None
