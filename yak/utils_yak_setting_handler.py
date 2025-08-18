# yak/utils_yak_setting_handler.py
#
# This file provides a high-level interface for executing and managing all VISA commands.
# It acts as a central handler, exposing public API functions for the GUI to use,
# and internally calling the low-level Yak functions to communicate with the instrument.
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
# Version 20250818.204500.2
# FIXED: Removed incorrect MHz-to-Hz conversion from set_resolution_bandwidth and set_video_bandwidth functions.
# UPDATED: Corrected debug log messages to accurately reflect the units being processed.
# NEW: Added a new handler function to toggle trace averaging on a per-trace basis.

current_version = "20250818.204500.2"
current_version_hash = (20250818 * 204500 * 2)

import os
import inspect
import numpy as np
import threading
import time

from display.debug_logic import debug_log
from display.console_logic import console_log

# NEW: Import the Yak functions from Yakety_Yak.py
from yak.Yakety_Yak import YakGet, YakSet, YakDo, YakNab

# Conversion constant from Megahertz to Hertz
MHZ_TO_HZ_CONVERSION = 1_000_000

# =========================================================================
# PUBLIC API FOR CONTROLLING SETTINGS - GUI should call these functions
# =========================================================================
def refresh_all_from_instrument(app_instance, console_print_func):
    # This is a new public API for the GUI to call
    # Queries all settings from the instrument and returns a dictionary of values.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"API call to refresh all settings from the instrument.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)

    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot refresh settings.")
        return None

    settings = {}
    try:
        settings['center_freq_hz'] = YakGet(app_instance, "FREQUENCY/CENTER", console_print_func)
        settings['span_hz'] = YakGet(app_instance, "FREQUENCY/SPAN", console_print_func)
        settings['start_freq_hz'] = YakGet(app_instance, "FREQUENCY/START", console_print_func)
        settings['stop_freq_hz'] = YakGet(app_instance, "FREQUENCY/STOP", console_print_func)

        settings['rbw_hz'] = YakGet(app_instance, "BANDWIDTH/RESOLUTION", console_print_func)
        settings['vbw_hz'] = YakGet(app_instance, "BANDWIDTH/VIDEO", console_print_func)
        settings['vbw_auto_on'] = YakGet(app_instance, "BANDWIDTH/VIDEO/AUTO", console_print_func) in ["ON", "1"]

        settings['initiate_continuous_on'] = YakGet(app_instance, "INITIATE/CONTINUOUS", console_print_func) in ["ON", "1"]

        settings['ref_level_dbm'] = YakGet(app_instance, "AMPLITUDE/REFERENCE LEVEL", console_print_func)
        settings['power_attenuation_db'] = YakGet(app_instance, "AMPLITUDE/POWER/ATTENUATION", console_print_func)
        settings['preamp_on'] = YakGet(app_instance, "AMPLITUDE/POWER/GAIN", console_print_func) in ["ON", "1"]
        settings['high_sensitivity_on'] = YakGet(app_instance, "AMPLITUDE/POWER/HIGH SENSITIVE", console_print_func) in ["ON", "1"]

        settings['trace1_mode'] = YakGet(app_instance, "TRACE/1/MODE", console_print_func)
        settings['trace2_mode'] = YakGet(app_instance, "TRACE/2/MODE", console_print_func)
        settings['trace3_mode'] = YakGet(app_instance, "TRACE/3/MODE", console_print_func)
        settings['trace4_mode'] = YakGet(app_instance, "TRACE/4/MODE", console_print_func)

        for i in range(6):
            settings[f'marker{i+1}_on'] = YakGet(app_instance, f"MARKER/{i+1}/CALCULATE/STATE", console_print_func) in ["ON", "1"]

        # NEW: Get averaging state and count for all traces
        for i in range(1, 5):
            avg_status, avg_count = get_trace_averaging_settings(app_instance, i, console_print_func)
            settings[f'trace{i}_average_on'] = avg_status
            settings[f'trace{i}_average_count'] = avg_count

        return settings
    except Exception as e:
        console_print_func(f"❌ Failed to retrieve settings from instrument: {e}.")
        debug_log(message=f"Error retrieving settings from instrument: {e}. What a mess!",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        return None

def _trigger_gui_refresh(app_instance):
    # Function Description:
    # Safely calls the refresh method on the correct GUI object from the main thread.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Attempting to refresh GUI from within handler. 🔄",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
    
    try:
        # CORRECTED PATH: Navigate through the `tabs_parent` dictionary to find the right object
        instrument_parent_tab = app_instance.tabs_parent.tab_content_frames['Instruments']
        settings_tab = instrument_parent_tab.settings_tab
        # FIXED: Corrected the function call to the existing method
        settings_tab.refresh_all_child_tabs()
    except AttributeError as e:
        debug_log(message=f"CRITICAL ERROR: Failed to find the GUI refresh method. Path traversal failed. Error: {e} 💥",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
    except Exception as e:
        debug_log(message=f"An unexpected error occurred during GUI refresh: {e}. 🤯",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)

def set_center_frequency(app_instance, value, console_print_func):
    """
    Sets the center frequency on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"API call to set center frequency: {value} MHz.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot set frequency.")
        return False
    
    try:
        hz_value = int(float(value) * MHZ_TO_HZ_CONVERSION)
        if YakSet(app_instance, "FREQUENCY/CENTER", str(hz_value), console_print_func) == "PASSED":
            app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
            return True
    except ValueError:
        console_print_func(f"❌ Invalid frequency value: '{value}'. Please enter a number.")
    return False

def set_span_frequency(app_instance, value, console_print_func):
    """
    Sets the span frequency on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"API call to set span: {value} MHz.",
              file=os.path.basename(__file__),
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
    debug_log(message=f"API call to set start frequency: {value} MHz.",
              file=os.path.basename(__file__),
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
    debug_log(message=f"API call to set stop frequency: {value} MHz.",
              file=os.path.basename(__file__),
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
    debug_log(message=f"API call to set resolution bandwidth: {value} Hz.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot set RBW.")
        return False
    
    try:
        # FIXED: Remove multiplication by MHZ_TO_HZ_CONVERSION as the value is already in Hz.
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
    debug_log(message=f"API call to set video bandwidth: {value} Hz.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot set VBW.")
        return False
        
    try:
        # FIXED: Remove multiplication by MHZ_TO_HZ_CONVERSION as the value is already in Hz.
        hz_value = int(float(value))
        if YakSet(app_instance, "BANDWIDTH/VIDEO", str(hz_value), console_print_func) == "PASSED":
            app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
            return True
    except ValueError:
        console_print_func(f"❌ Invalid VBW value: '{value}'. Please enter a number.")
    return False
    
def toggle_vbw_auto(app_instance, console_print_func):
    """
    Toggles the automatic VBW setting on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"API call to toggle VBW auto.",
              file=os.path.basename(__file__),
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
    
def set_continuous_initiate_mode(app_instance, mode, console_print_func):
    """
    Sets the continuous initiate mode on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"API call to set continuous initiate mode: {mode}.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot set continuous initiate mode.")
        return False
    
    # We need to ensure the mode is a string "ON" or "OFF"
    mode_str = "ON" if mode else "OFF"
    if YakDo(app_instance, f"INITIATE/CONTINUOUS/{mode_str}", console_print_func=console_print_func) == "PASSED":
        app_instance.initiate_continuous_on_var.set(mode)
        app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
        return True
    return False
    
def do_immediate_initiate(app_instance, console_print_func):
    """
    Initiates an immediate sweep on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"API call to initiate immediate scan.",
              file=os.path.basename(__file__),
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
    
def set_reference_level(tab_instance, app_instance, value, console_print_func):
    """
    Sets the reference level on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"API call to set reference level: {value} dBm.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot set reference level.")
        return False
    
    try:
        int_value = int(float(value))
        if YakDo(app_instance, f"AMPLITUDE/REFERENCE LEVEL/{int_value}", console_print_func=console_print_func) == "PASSED":
            app_instance.ref_level_dbm_var.set(value)
            app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
            return True
        else:
            return False
    except (ValueError, TypeError) as e:
        console_print_func(f"❌ Invalid reference level value: '{value}'. Please enter a number. Error: {e}")
        debug_log(message=f"ValueError: could not convert reference level to int. Failed to parse data. Error: {e}",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function, special=True)
        return False
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred while setting the reference level: {e}")
        debug_log(message=f"An unexpected error occurred: {e}",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function, special=True)
        return False


def toggle_preamp(tab_instance, app_instance, console_print_func):
    """
    Toggles the preamp on or off and updates the UI state.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Entering {current_function}. Toggling the preamp switch! ⚡",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
    
    try:
        is_on = app_instance.preamp_on_var.get()
        if is_on:
            YakDo(app_instance, "AMPLITUDE/POWER/GAIN/OFF", console_print_func=console_print_func)
            app_instance.preamp_on_var.set(False)
            console_print_func("✅ Preamp turned OFF.")
            # NEW LOGIC: If preamp is turned off, also turn off high sensitivity
            if app_instance.high_sensitivity_on_var.get():
                debug_log(message=f"Preamp turned off, automatically turning off high sensitivity. 🕵️‍♀️",
                        file=os.path.basename(__file__),
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
        debug_log(message=f"Arrr, the code be capsized! Error toggling preamp: {e} 🏴‍☠️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)


def toggle_high_sensitivity(tab_instance, app_instance, console_print_func):
    """
    Toggles the high sensitivity mode on or off and updates the UI state.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Entering {current_function}. Flipping the high sensitivity switch! 🔬",
              file=os.path.basename(__file__),
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
        
        # Explicitly get the latest values from the instrument and update the GUI
        results = YakNab(app_instance, "AMPLITUDE/POWER/HIGH SENSITIVE", console_print_func=console_print_func)
        if results is not None and len(results) >= 3:
            ref_level_dbm, attenuation_db, preamp_on = results
            app_instance.ref_level_dbm_var.set(float(ref_level_dbm))
            app_instance.power_attenuation_db_var.set(float(attenuation_db))
            app_instance.preamp_on_var.set(int(preamp_on) == 1)
            tab_instance._set_ui_initial_state()
            console_print_func("✅ Updated UI with new values from instrument.")
        
    except Exception as e:
        console_print_func(f"❌ Error toggling high sensitivity: {e}")
        debug_log(message=f"Arrr, the code be capsized! The error be: {e} 🏴‍☠️",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)


def set_power_attenuation(tab_instance, app_instance, value, console_print_func):
    """
    Sets the power attenuation on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"API call to set power attenuation: {value} dB.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot set power attenuation.")
        return False
    
    if YakDo(app_instance, f"AMPLITUDE/POWER/ATTENUATION/{value}DB", console_print_func=console_print_func) == "PASSED":
        app_instance.power_attenuation_db_var.set(value)
        app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
        return True
    return False
    
    
def set_trace_mode(app_instance, trace_number, mode, console_print_func):
    """
    Sets the trace mode for a specific trace on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"API call to set trace {trace_number} mode: {mode}.",
              file=os.path.basename(__file__),
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
    
def do_turn_all_markers_on(app_instance, console_print_func):
    """
    Turns on all markers on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"API call to turn on all markers.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot turn on markers.")
        return False
    
    if YakDo(app_instance, "MARKER/All/CALCULATE/STATE/ON", console_print_func=console_print_func) == "PASSED":
        app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
        return True
    return False
    
def toggle_marker_state(app_instance, marker_number, state, console_print_func):
    """
    Toggles the state of a specific marker on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"API call to toggle marker {marker_number} state to {state}.",
              file=os.path.basename(__file__),
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
    debug_log(message=f"API call to perform peak search.",
              file=os.path.basename(__file__),
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

def toggle_trace_averaging(app_instance, trace_number, is_on, console_print_func):
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
    debug_log(message=f"API call to toggle trace averaging for trace {trace_number} to {is_on}.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot toggle trace averaging.")
        return False

    # FIXED: Use the new DO commands for ON and OFF states
    state_str = "ON" if is_on else "OFF"
    command_type = f"AVERAGE/{state_str}"
    
    if YakDo(app_instance, command_type, console_print_func) == "PASSED":
        console_print_func(f"✅ Trace {trace_number} averaging turned {state_str}.")
        app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
        return True
    
    return False

# NEW: Add a function to set the average count
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
    debug_log(message=f"API call to set trace averaging count for trace {trace_number} to {count}.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot set trace averaging count.")
        return False
        
    command_type = f"AVERAGE"
    variable_value = count # The full command string for the SET action
    
    if YakSet(app_instance, command_type, variable_value, console_print_func) == "PASSED":
        console_print_func(f"✅ Trace {trace_number} averaging count set to {count}.")
        app_instance.after(0, lambda: _trigger_gui_refresh(app_instance))
        return True
    
    return False


# NEW: Add a handler function to get the average state and count
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
    debug_log(message=f"API call to retrieve averaging settings for trace {trace_number}.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
              
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot retrieve averaging settings.")
        return None, None

    # The command type needs to be generic so YakNab can find it in the CSV
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
            debug_log(message=f"Arrr, the response be gibberish! Error: {e}",
                      file=os.path.basename(__file__),
                      version=current_version,
                      function=current_function)
    
    return None, None
# =========================================================================
# HELPER FUNCTIONS - Not for direct GUI use
# =========================================================================

def _process_trace_data(raw_data_string, start_freq_hz, end_freq_hz, console_print_func):
    """
    Function Description:
    Processes a raw comma-separated string of trace amplitude data into
    a list of (frequency, amplitude) pairs.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message="Processing raw trace data into frequency/amplitude pairs. This is a crucial step.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)

    if not raw_data_string or "FAILED" in raw_data_string:
        console_print_func("❌ Received invalid data from the instrument. Cannot process trace.")
        return None

    try:
        amplitudes_dbm = [float(val) for val in raw_data_string.split(',')]
        
        num_points = len(amplitudes_dbm)
        if num_points <= 1:
            console_print_func("⚠️ Received insufficient data points from the instrument. Cannot create a meaningful trace.")
            return None
            
        freq_points = np.linspace(start_freq_hz, end_freq_hz, num_points)
        
        processed_data = list(zip(freq_points / MHZ_TO_HZ_CONVERSION, amplitudes_dbm))

        debug_log(message=f"Successfully processed trace data. First 5 points: {processed_data[:5]}...",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function)
        
        return processed_data

    except ValueError as e:
        console_print_func(f"❌ Failed to parse trace data string. Error: {e}")
        debug_log(message=f"ValueError: could not convert string to float. Failed to parse data string. Error: {e}",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function, special=True)
        return None
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred while processing trace data: {e}")
        debug_log(message=f"An unexpected error occurred: {e}",
                  file=os.path.basename(__file__),
                  version=current_version,
                  function=current_function, special=True)
        return None


def get_trace_data_logic(app_instance, console_print_func):
    """
    Function Description:
    Retrieves trace data for all active traces from the instrument.
    This function has been refactored to be more robust, checking for valid data and
    handling different trace modes with a simple update cycle counter.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message="Getting trace data from the instrument.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot get trace data.")
        return False
    
    # Placeholder for collecting all trace data
    all_trace_data = []

    # Get frequency settings to properly process the trace data
    center_freq_hz = float(YakGet(app_instance, "FREQUENCY/CENTER", console_print_func))
    span_hz = float(YakGet(app_instance, "FREQUENCY/SPAN", console_print_func))
    start_freq_hz = center_freq_hz - (span_hz / 2)
    end_freq_hz = center_freq_hz + (span_hz / 2)

    for i in range(1, 5): # Iterate through Trace 1 to 4
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
    
def do_power_cycle(app_instance, console_print_func):
    """
    Sends a power cycle command to the instrument and handles the disconnection state.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"API call to power cycle the device.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot power cycle device.")
        return False

    console_print_func("⚠️ Initiating device power cycle. Connection will be lost for ~20 seconds. Please wait to reconnect.")
    
    if YakDo(app_instance, "POWER/RESET", console_print_func=console_print_func) == "PASSED":
        # The instrument is now cycling, so we need to set the application state to disconnected.
        # This is the correct way to handle the disconnected state after a reset.
        app_instance.is_connected.set(False)
        return True
        
    return False

def get_all_marker_values_logic(app_instance, console_print_func):
    """
    Retrieves and returns the X and Y values for all active markers.
    Returns a list of tuples: [(x1, y1), (x2, y2), ...]
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Getting all marker values from the instrument.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot read markers.")
        return None
    
    marker_values = []
    for i in range(1, 7):
        # Check if the marker is active
        marker_state = YakGet(app_instance, f"MARKER/{i}/CALCULATE/STATE", console_print_func)
        if marker_state in ["ON", "1"]:
            x_value = YakGet(app_instance, f"MARKER/{i}/CALCULATE/X", console_print_func)
            y_value = YakGet(app_instance, f"MARKER/{i}/CALCULATE/Y", console_print_func)

            try:
                x_value_mhz = float(x_value) / MHZ_TO_HZ_CONVERSION
                y_value_dbm = float(y_value)
                marker_values.append((x_value_mhz, y_value_dbm))
            except (ValueError, TypeError):
                console_print_func(f"⚠️ Could not parse marker {i} values.")
                debug_log(message=f"Failed to parse marker {i} values. What a mess!",
                          file=os.path.basename(__file__),
                          version=current_version,
                          function=current_function)
                marker_values.append((None, None))
    
    return marker_values


def reset_device(app_instance, console_print_func):
    """
    Sends a soft reset command to the instrument.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"API call to reset the device.",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)
    
    if not app_instance.is_connected.get():
        console_print_func("❌ Not connected to an instrument. Cannot reset device.")
        return False
    
    if YakDo(app_instance, "SYSTEM/RESET", console_print_func=console_print_func) == "PASSED":
        return True
    return False