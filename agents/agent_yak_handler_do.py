# agents/agent_yak_handler_do.py
#
# This file provides high-level handler functions for 'DO' type SCPI commands.
# It acts as an interface between the application logic and the low-level
# YakDo function, ensuring proper execution and logging.
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
# Version 20250902.115430.1

import inspect
import os

from workers.worker_logging import debug_log, console_log
from agents.agent_YaketyYak import YakDo

# --- Global Scope Variables ---
current_version = "20250902.115430.1"
current_version_hash = (20250902 * 115430 * 1)
current_file = f"{os.path.basename(__file__)}"

def handle_do_command(dispatcher, command_type):
    """
    Handles a 'DO' command by writing to the instrument.
    """
    # This function is not used in this file's refactored logic, but it's kept for the dispatcher.
    pass

def YakDo_immediate_initiate(app_instance, console_print_func):
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
    
def YakDo_turn_all_markers_on(app_instance, console_print_func):
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
    
def YakDo_toggle_marker_state(app_instance, marker_number, state, console_print_func):
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
    
def YakDo_peak_search(app_instance, console_print_func):
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

def YakDo_power_cycle(app_instance, console_print_func):
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

def YakDo_reset_device(app_instance, console_print_func):
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
