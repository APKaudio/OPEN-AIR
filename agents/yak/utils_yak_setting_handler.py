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
# Version 20250821.210502.1
# FIXED: Removed incorrect MHz-to-Hz conversion from set_resolution_bandwidth and set_video_bandwidth functions.
# UPDATED: Corrected debug log messages to accurately reflect the units being processed.
# NEW: Added a new handler function to toggle trace averaging on a per-trace basis.
# UPDATED: All debug messages now include the required 🐐 emoji at the start.

import os
import inspect
import numpy as np
import threading
import time

from display.debug_logic import debug_log
from display.console_logic import console_log

# NEW: Import the Yak functions from Yakety_Yak.py
from yak.Yakety_Yak import YakGet, YakSet, YakDo, YakNab

# --- Versioning ---
w = 20250821
x_str = '210502'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"


# Conversion constant from Megahertz to Hertz
MHZ_TO_HZ_CONVERSION = 1_000_000

# =========================================================================
# PUBLIC API FOR CONTROLLING SETTINGS - GUI should call these functions
# =========================================================================
def refresh_all_from_instrument(app_instance, console_print_func):
    # This is a new public API for the GUI to call
    # Queries all settings from the instrument and returns a dictionary of values.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🟢 API call to refresh all settings from the instrument.",
              file=current_file,
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

        settings['ref_level_dBm'] = YakGet(app_instance, "AMPLITUDE/REFERENCE LEVEL", console_print_func)
        settings['power_attenuation_dB'] = YakGet(app_instance, "AMPLITUDE/POWER/ATTENUATION", console_print_func)
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

        debug_log(f"🐐 ✅ Retrieved all settings: {settings}", file=current_file, version=current_version, function=current_function)
        return settings
    except Exception as e:
        console_print_func(f"❌ Failed to retrieve settings from instrument: {e}.")
        debug_log(f"🐐 ❌ Error retrieving settings from instrument: {e}. What a mess!",
                  file=current_file,
                  version=current_version,
                  function=current_function)
        return None

def _trigger_gui_refresh(app_instance):
    # Function Description:
    # Safely calls the refresh method on the correct GUI object from the main thread.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"🐐 🔄 Attempting to refresh GUI from within handler. 🔄",
              file=current_file,
              version=current_version,
              function=current_function)
    
    try:
        # CORRECTED PATH: Navigate through the `tabs_parent` dictionary to find the right object
        instrument_parent_tab = app_instance.tabs_parent.tab_content_frames['Instruments']
        settings_tab = instrument_parent_tab.settings_tab
        # FIXED: Corrected the function call to the existing method
        settings_tab.refresh_all_child_tabs()
    except AttributeError as e:
        debug_log(f"🐐 💥 CRITICAL ERROR: Failed to find the GUI refresh method. Path traversal failed. Error: {e} 💥",
                  file=current_file,
                  version=current_version,
                  function=current_function)
    except Exception as e:
        debug_log(f"🐐 🤯 An unexpected error occurred during GUI refresh: {e}. 🤯",
                  file=current_file,
                  version=current_version,
                  function=current_function)

def set_center_frequency(app_instance, value, console_print_func):
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
