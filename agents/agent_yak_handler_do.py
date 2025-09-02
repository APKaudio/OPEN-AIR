# agents/agent_yak_handler_do.py
#
# This handler is responsible for processing 'DO' type SCPI commands.
# It constructs and sends a simple command string to the instrument without
# expecting a response.
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

def handle_do_command(dispatcher: ScpiDispatcher, command_type):
    """
    Handles a 'DO' command by writing to the instrument.
    """
    # ... logic from Yakety_Yak.py's YakDo function ...
    pass




def do_immediate_initiate(app_instance, console_print_func):
    """
    Initiates an immediate sweep on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to initiate immediate scan.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot initiate immediate scan.")
        return False
    
    if YakDo(app_instance, "INITIATE/IMMEDIATE", console_print_func=console_print_func) == "PASSED":
        console_print_func("✅ Immediate scan initiated successfully.")
        app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
        return True
    return False
    

    
def do_toggle_vbw_auto(app_instance, console_print_func):
    """
    Toggles the automatic VBW setting on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to toggle VBW auto.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot toggle VBW Auto.")
        return False
    
    current_state = app_instance.vbw_auto_on_var.get()
    new_state = "OFF" if current_state else "ON"
    
    if YakDo(app_instance, f"BANDWIDTH/VIDEO/AUTO/{new_state}", console_print_func=console_print_func) == "PASSED":
        app_instance.vbw_auto_on_var.set(not current_state)
        app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
        return True
    return False


def do_toggle_preamp(tab_instance, app_instance, console_print_func):
    """
    Toggles the preamp on or off and updates the UI state.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to toggle the preamp switch! ⚡",
              file=current_file,
              version=current_version,
              function=current_function)
    
    try:
        is_on = app_instance.preamp_on_var.get()
        if is_on:
            YakDo(app_instance, "AMPLITUDE/POWER/GAIN/OFF", console_print_func=console_print_func)
            app_instance.preamp_on_var.set(False)
            console_print_func("✅ Preamp turned OFF.")
            if app_instance.high_sensitivity_on_var.get():
                debug_log(f"🐐 Preamp turned off, automatically turning off high sensitivity. 🕵️‍♀️",
                        file=current_file,
                        version=current_version,
                        function=current_function)
                toggle_high_sensitivity(tab_instance=tab_instance, app_instance=app_instance, console_print_func=console_print_func)
        else:
            YakDo(app_instance, "AMPLITUDE/POWER/GAIN/ON", console_print_func=console_print_func)
            app_instance.preamp_on_var.set(True)
            console_print_func("✅ Preamp turned ON.")

        tab_instance._update_toggle_button_style(button=tab_instance.preamp_toggle_button, state=app_instance.preamp_on_var.get())
        app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))

    except Exception as e:
        console_print_func(f"❌ Error toggling preamp: {e}")
        debug_log(f"🐐 🧨 Arrr, the code be capsized! Error toggling preamp: {e} 🏴‍☠️",
                  file=current_file,
                  version=current_version,
                  function=current_function)


def do_toggle_high_sensitivity(tab_instance, app_instance, console_print_func):
    """
    Toggles the high sensitivity mode on or off and updates the UI state.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to toggle the high sensitivity switch! 🔬",
              file=current_file,
              version=current_version,
              function=current_function)

    try:
        is_on = app_instance.high_sensitivity_on_var.get()
        if is_on:
            YakDo(app_instance, "AMPLITUDE/POWER/HIGH SENSITIVE/OFF", console_print_func=console_print_func)
            app_instance.high_sensitivity_on_var.set(False)
            console_print_func("✅ High Sensitivity turned OFF.")
        else:
            YakDo(app_instance, "AMPLITUDE/POWER/HIGH SENSITIVE/ON", console_print_func=console_print_func)
            app_instance.high_sensitivity_on_var.set(True)
            console_print_func("✅ High Sensitivity turned ON.")

        tab_instance._update_toggle_button_style(button=tab_instance.hs_toggle_button, state=app_instance.high_sensitivity_on_var.get())
        
        results = YakNab(app_instance, "AMPLITUDE/POWER/HIGH SENSITIVE", console_print_func=console_print_func)
        if results is not None and len(results) >= 3:
            ref_level_dBm, attenuation_dB, preamp_on = results
            app_instance.ref_level_dBm_var.set(float(ref_level_dBm))
            app_instance.power_attenuation_dB_var.set(float(attenuation_dB))
            app_instance.preamp_on_var.set(int(preamp_on) == 1)
            tab_instance._set_ui_initial_state()
            console_print_func("✅ Updated UI with new values from instrument.")
        
    except Exception as e:
        console_print_func(f"❌ Error toggling high sensitivity: {e}")
        debug_log(f"🐐 🧨 Arrr, the code be capsized! The error be: {e} 🏴‍☠️",
                  file=current_file,
                  version=current_version,
                  function=current_function)

def do_turn_all_markers_on(app_instance, console_print_func):
    """
    Turns on all markers on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to turn on all markers.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot turn on markers.")
        return False
    
    if YakDo(app_instance, "MARKER/All/CALCULATE/STATE/ON", console_print_func=console_print_func) == "PASSED":
        app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
        return True
    return False
    
def do_toggle_marker_state(app_instance, marker_number, state, console_print_func):
    """
    Toggles the state of a specific marker on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to toggle marker {marker_number} state to {state}.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot set marker state.")
        return False
        
    new_state = "ON" if state else "OFF"
    if YakDo(app_instance, f"MARKER/{marker_number}/CALCULATE/STATE/{new_state}", console_print_func=console_print_func) == "PASSED":
        app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
        return True
    return False
    
def do_peak_search(app_instance, console_print_func):
    """
    Performs a peak search on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to perform peak search.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot perform peak search.")
        return False
    
    if YakDo(app_instance, "MARKER/PEAK/SEARCH", console_print_func=console_print_func) == "PASSED":
        console_print_func("✅ Peak search command sent successfully.")
        app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
        return True
    return False

def do_toggle_trace_averaging(app_instance, trace_number, is_on, console_print_func):
    """
    Function Description:
    Toggles the averaging state for a specific trace and triggers a GUI refresh.
    
    Inputs:
    - app_instance (object): A reference to the main application instance.
    - trace_number (int): The number of the trace to toggle (1-4).
    - is_on (bool): The desired state for averaging (True for ON, False for OFF).
    - console_print_func (function): A function to print messages to the GUI console.
    
    Outputs:
    - bool: True if the command is executed successfully, False otherwise.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to toggle trace averaging for trace {trace_number} to {is_on}.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot toggle trace averaging.")
        return False

    state_str = "ON" if is_on else "OFF"
    command_type = f"AVERAGE/{state_str}"
    
    if YakDo(app_instance, command_type, console_print_func) == "PASSED":
        console_print_func(f"✅ Trace {trace_number} averaging turned {state_str}.")
        app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
        return True
    
    return False



def do_power_cycle(app_instance, console_print_func):
    """
    Sends a power cycle command to the instrument and handles the disconnection state.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to power cycle the device.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot power cycle device.")
        return False

    console_print_func("⚠️ Initiating device power cycle. Connection will be lost for ~20 seconds. Please wait to reconnect.")
    
    if YakDo(app_instance, "POWER/RESET", console_print_func=console_print_func) == "PASSED":
        app_instance.is_connected.set(False)
        return True
        
    return False

def do_reset_device(app_instance, console_print_func):
    """
    Sends a soft reset command to the instrument.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to reset the device.",
              file=current_file,
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot reset device.")
        return False
    
    if YakDo(app_instance, "SYSTEM/RESET", console_print_func=console_print_func) == "PASSED":
        return True
    return False
