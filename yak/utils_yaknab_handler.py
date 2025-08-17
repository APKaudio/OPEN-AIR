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
# Version 20250817.001000.4
# UPDATED: Added new handler for Amplitude settings.
# FIXED: Corrected the parsing logic to handle both float and string responses for boolean-like settings.
# UPDATED: The function now handles a 5th return value for Sweep Time.

current_version = "20250817.001000.4"
current_version_hash = 20250817 * 1000 * 4

import inspect
import os
from typing import Optional, List, Dict

from yak.Yakety_Yak import YakNab
from display.debug_logic import debug_log
from display.console_logic import console_log

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
    
    console_print_func("❌ Failed to retrieve all bandwidth settings from instrument.")
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
    
    console_print_func("❌ Failed to retrieve all amplitude settings from instrument.")
    return None