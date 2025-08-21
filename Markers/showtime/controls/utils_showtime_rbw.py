# tabs/Markers/showtime/controls/utils_showtime_rbw.py
#
# This utility file centralizes the backend logic for controlling the instrument's
# Resolution Bandwidth (RBW) settings. It contains functions that handle
# button clicks from the GUI and translate them into instrument commands.
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
# Version 20250824.010200.1
# REFACTORED: The logic has been streamlined to ensure that UI updates,
#             instrument commands, and configuration saving are consistently
#             handled by the on_rbw_button_click function.

import os
import inspect
import tkinter as tk
from tkinter import ttk

from display.debug_logic import debug_log
from display.console_logic import console_log
from yak.Yakety_Yak import YakSet
from yak.utils_yak_setting_handler import set_resolution_bandwidth
from settings_and_config.config_manager import save_config

from process_math.math_frequency_translation import format_hz

# --- Versioning ---
w = 20250824
x_str = '010200'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"

def set_rbw_logic(app_instance, rbw_hz, console_print_func):
    # [Sets the resolution bandwidth of the instrument and reports back.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Entering {current_function} with rbw_hz: {rbw_hz}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
    
    status = YakSet(app_instance=app_instance, command_type="BANDWIDTH/RESOLUTION", variable_value=str(rbw_hz), console_print_func=console_print_func)
    
    if status != "PASSED":
        console_print_func("❌ Failed to set RBW.")

def on_rbw_button_click(showtime_tab, rbw_hz):
    # [Handles the event when an RBW button is clicked.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Entering {current_function} with rbw_hz: {rbw_hz}",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=current_function)
    
    try:
        # 📝 Write Data: Update the RBW variable on the parent instance.
        showtime_tab.rbw_var.set(str(rbw_hz))
        debug_log(message=f"📝 Writing state: rbw_var = {rbw_hz} Hz", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        
        # Re-sync the RBW button styles
        for value_str, btn in showtime_tab.rbw_buttons.items():
            if value_str == showtime_tab.rbw_var.get():
                btn.config(style='ControlButton.Active.TButton')
            else:
                btn.config(style='ControlButton.Inactive.TButton')
        
        showtime_tab.console_print_func(f"✅ RBW set to {format_hz(rbw_hz)}.")
        
        # Trigger the handler to send the new RBW to the instrument
        set_resolution_bandwidth(app_instance=showtime_tab.app_instance, value=int(rbw_hz), console_print_func=showtime_tab.console_print_func)
        
        # FIXED: Save config after a successful RBW change
        save_config(config=showtime_tab.app_instance.config,
                    file_path=showtime_tab.app_instance.CONFIG_FILE_PATH,
                    console_print_func=showtime_tab.console_print_func,
                    app_instance=showtime_tab.app_instance)

    except Exception as e:
        showtime_tab.console_print_func(f"❌ Error setting RBW: {e}")
        debug_log(message=f"Shiver me timbers, the RBW has gone rogue! The error be: {e}",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)