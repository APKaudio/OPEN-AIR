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
# Version 20250820.233600.1
# REFACTORED: The local `format_hz` function was removed and replaced with an import
#             from `process_math.math_frequency_translation` for global availability.
# FIXED: The `on_rbw_button_click` function signature and internal logic were updated
#        to correctly use the `rbw_tab_instance`, resolving `AttributeError`s.

current_version = "20250820.233600.1"
current_version_hash = (20250820 * 233600 * 1)

import os
import inspect

from display.debug_logic import debug_log
from display.console_logic import console_log
from yak.Yakety_Yak import YakSet
from yak.utils_yak_setting_handler import set_resolution_bandwidth

from process_math.math_frequency_translation import format_hz

def set_rbw_logic(app_instance, rbw_hz, console_print_func):
    # [Sets the resolution bandwidth of the instrument and reports back.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function} with rbw_hz: {rbw_hz}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
    
    status = YakSet(app_instance=app_instance, command_type="BANDWIDTH/RESOLUTION", variable_value=str(rbw_hz), console_print_func=console_print_func)
    
    if status != "PASSED":
        console_print_func("❌ Failed to set RBW.")

def on_rbw_button_click(rbw_tab_instance, rbw_hz):
    # [Handles the event when an RBW button is clicked.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function} with rbw_hz: {rbw_hz}",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=current_function)
    
    try:
        # Update the RBW variable on the tab instance
        rbw_tab_instance.rbw_var.set(str(rbw_hz))
        
        # Re-sync the RBW button styles
        for value_str, btn in rbw_tab_instance.rbw_buttons.items():
            if value_str == rbw_tab_instance.rbw_var.get():
                btn.config(style='ControlButton.Active.TButton')
            else:
                btn.config(style='ControlButton.Inactive.TButton')
        
        rbw_tab_instance.controls_frame.console_print_func(f"✅ RBW set to {format_hz(rbw_hz)}.")
        
        # Trigger the handler to send the new RBW to the instrument
        set_resolution_bandwidth(rbw_tab_instance.controls_frame.app_instance, int(rbw_hz), rbw_tab_instance.controls_frame.console_print_func)

    except Exception as e:
        rbw_tab_instance.controls_frame.console_print_func(f"❌ Error setting RBW: {e}")
        debug_log(f"Shiver me timbers, the RBW has gone rogue! The error be: {e}",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)