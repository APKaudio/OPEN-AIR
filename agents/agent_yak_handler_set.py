# agents/agent_yak_handler_set.py
#
# This handler is responsible for processing 'SET' type SCPI commands.
# It formats a single value into a command string and sends it to the instrument.
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

def handle_set_command(dispatcher: ScpiDispatcher, command_type, variable_value):
    """
    Handles a 'SET' command by writing to the instrument.
    """
    # ... logic from Yakety_Yak.py's YakSet function ...
    pass


def set_span_frequency(app_instance, value, console_print_func):
    """
    Sets the span frequency on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to set span: {value} MHz.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot set span.")
        return False
        
    try:
        hz_value = int(float(value) * MHZ_TO_HZ_CONVERSION)
        if YakSet(app_instance, "FREQUENCY/SPAN", str(hz_value), console_print_func) == "PASSED":
            app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
            return True
    except ValueError:
        console_print_func(f"❌ Invalid span value: '{value}'. Please enter a number.")
    return False

def set_start_frequency(app_instance, value, console_print_func):
    """
    Sets the start frequency on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to set start frequency: {value} MHz.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot set start frequency.")
        return False
        
    try:
        hz_value = int(float(value) * MHZ_TO_HZ_CONVERSION)
        if YakSet(app_instance, "FREQUENCY/START", str(hz_value), console_print_func) == "PASSED":
            app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
            return True
    except ValueError:
        console_print_func(f"❌ Invalid start frequency value: '{value}'. Please enter a number.")
    return False

def set_stop_frequency(app_instance, value, console_print_func):
    """
    Sets the stop frequency on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to set stop frequency: {value} MHz.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot set stop frequency.")
        return False
        
    try:
        hz_value = int(float(value) * MHZ_TO_HZ_CONVERSION)
        if YakSet(app_instance, "FREQUENCY/STOP", str(hz_value), console_print_func) == "PASSED":
            app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
            return True
    except ValueError:
        console_print_func(f"❌ Invalid stop frequency value: '{value}'. Please enter a number.")
    return False

def set_resolution_bandwidth(app_instance, value, console_print_func):
    """
    Sets the resolution bandwidth on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to set resolution bandwidth: {value} Hz.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot set RBW.")
        return False
    
    try:
        hz_value = int(float(value))
        if YakSet(app_instance, "BANDWIDTH/RESOLUTION", str(hz_value), console_print_func) == "PASSED":
            app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
            return True
    except ValueError:
        console_print_func(f"❌ Invalid RBW value: '{value}'. Please enter a number.")
    return False
    

    
def set_video_bandwidth(app_instance, value, console_print_func):
    """
    Sets the video bandwidth on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to set video bandwidth: {value} Hz.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot set VBW.")
        return False
        
    try:
        hz_value = int(float(value))
        if YakSet(app_instance, "BANDWIDTH/VIDEO", str(hz_value), console_print_func) == "PASSED":
            app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
            return True
    except ValueError:
        console_print_func(f"❌ Invalid VBW value: '{value}'. Please enter a number.")
    return False
    


        
def set_continuous_initiate_mode(app_instance, mode, console_print_func):
    """
    Sets the continuous initiate mode on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to set continuous initiate mode: {mode}.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot set continuous initiate mode.")
        return False
    
    mode_str = "ON" if mode else "OFF"
    if YakDo(app_instance, f"INITIATE/CONTINUOUS/{mode_str}", console_print_func=console_print_func) == "PASSED":
        app_instance.initiate_continuous_on_var.set(mode)
        app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
        return True
    return False
    
def set_reference_level(tab_instance, app_instance, value, console_print_func):
    """
    Sets the reference level on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to set reference level: {value} dBm.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot set reference level.")
        return False
    
    try:
        int_value = int(float(value))
        if YakDo(app_instance, f"AMPLITUDE/REFERENCE LEVEL/{int_value}", console_print_func=console_print_func) == "PASSED":
            app_instance.ref_level_dBm_var.set(value)
            app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
            return True
        else:
            return False
    except (ValueError, TypeError) as e:
        console_print_func(f"❌ Invalid reference level value: '{value}'. Please enter a number. Error: {e}")
        debug_log(f"🐐 ❌ ValueError: could not convert reference level to int. Failed to parse data. Error: {e}",
                  file=current_file,
                  version=current_version,
                  function=current_function, special=True)
        return False
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred while setting the reference level: {e}")
        debug_log(f"🐐 🧨 An unexpected error occurred: {e}",
                  file=current_file,
                  version=current_version,
                  function=current_function, special=True)
        return False




def set_power_attenuation(tab_instance, app_instance, value, console_print_func):
    """
    Sets the power attenuation on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to set power attenuation: {value} dB.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot set power attenuation.")
        return False
    
    if YakDo(app_instance, f"AMPLITUDE/POWER/ATTENUATION/{value}DB", console_print_func=console_print_func) == "PASSED":
        app_instance.power_attenuation_dB_var.set(value)
        app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
        return True
    return False
    
    
def set_trace_mode(app_instance, trace_number, mode, console_print_func):
    """
    Sets the trace mode for a specific trace on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to set trace {trace_number} mode: {mode}.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot set trace mode.")
        return False
    
    if YakDo(app_instance, f"TRACE/{trace_number}/MODE/{mode}", console_print_func=console_print_func) == "PASSED":
        trace_var = getattr(app_instance, f"trace{trace_number}_mode_var")
        trace_var.set(mode)
        app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
        return True
    return False
    

    
def set_trace_averaging_count(app_instance, trace_number, count, console_print_func):
    """
    Function Description:
    Sets the averaging count for a specific trace and triggers a GUI refresh.
    
    Inputs:
    - app_instance (object): A reference to the main application instance.
    - trace_number (int): The number of the trace to set (1-4).
    - count (int): The desired averaging count.
    - console_print_func (function): A function to print messages to the GUI console.
    
    Outputs:
    - bool: True if the command is executed successfully, False otherwise.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to set trace averaging count for trace {trace_number} to {count}.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot set trace averaging count.")
        return False
        
    command_type = f"AVERAGE"
    variable_value = count
    
    if YakSet(app_instance, command_type, variable_value, console_print_func) == "PASSED":
        console_print_func(f"✅ Trace {trace_number} averaging count set to {count}.")
        app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
        return True
    
    return False
