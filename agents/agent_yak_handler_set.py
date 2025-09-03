# agents/agent_yak_handler_set.py
#
# This file provides high-level handler functions for 'SET' type SCPI commands.
# It acts as an interface between the application logic and the low-level
# YakSet function, ensuring proper execution and logging.
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
from agents.agent_YaketyYak import YakSet

# --- Global Scope Variables ---
current_version = "20250902.115430.1"
current_version_hash = (20250902 * 115430 * 1)
current_file = f"{os.path.basename(__file__)}"
MHZ_TO_HZ_CONVERSION = 1_000_000

def YakSet_center_frequency(app_instance, value, console_print_func):
    """
    Sets the center frequency on the instrument and triggers a GUI refresh.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 API call to set center frequency: {value} MHz.",
              file=current_file,
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

def YakSet_span_frequency(app_instance, value, console_print_func):
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

def YakSet_start_frequency(app_instance, value, console_print_func):
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

def YakSet_stop_frequency(app_instance, value, console_print_func):
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

def YakSet_resolution_bandwidth(app_instance, value, console_print_func):
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

def YakSet_video_bandwidth(app_instance, value, console_print_func):
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

def YakSet_trace_averaging_count(app_instance, trace_number, count, console_print_func):
    """
    Sets the averaging count for a specific trace and triggers a GUI refresh.
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
