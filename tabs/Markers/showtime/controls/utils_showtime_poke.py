# tabs/Markers/showtime/controls/utils_showtime_poke.py
#
# This utility file provides the backend logic for the PokeTab. It contains
# functions that handle button clicks for Poking and then communicates with
# the instrument control layer.
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
# Version 20250821.012500.1
# REFACTORED: `on_poke_action` now directly accesses all shared state variables from
#             the `showtime_tab_instance` passed as an argument.
#
# FIXED: The `on_poke_action` function now correctly accesses variables from the
#        `showtime_tab_instance`, resolving `AttributeError`s.

current_version = "20250821.012500.1"
current_version_hash = (20250821 * 12500 * 1)

import os
import inspect
import pandas as pd
from ref.frequency_bands import MHZ_TO_HZ
from display.debug_logic import debug_log
from display.console_logic import console_log
from yak.Yakety_Yak import YakSet

# Import dedicated utility functions from their respective modules
from tabs.Markers.showtime.controls.utils_showtime_span import format_hz
from yak.utils_yakbeg_handler import handle_freq_center_span_beg


def on_poke_action(showtime_tab_instance):
    # [Sets center frequency and span simultaneously using the YakBeg handler.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
    
    try:
        center_freq_mhz = float(showtime_tab_instance.poke_freq_var.get())
        center_freq_hz = int(center_freq_mhz * MHZ_TO_HZ)
        
        span_hz = int(showtime_tab_instance.span_var.get())
        
        showtime_tab_instance.console_print_func(f"Poking instrument: Center={center_freq_mhz} MHz, Span={format_hz(span_hz)}...")
        
        response = handle_freq_center_span_beg(
            showtime_tab_instance.app_instance, 
            center_freq_hz, 
            span_hz,
            showtime_tab_instance.console_print_func
        )
        
        if response and len(response) >= 2:
            returned_center, returned_span, _, _ = response
            showtime_tab_instance.console_print_func(
                f"✅ Instrument Confirmed: Center={returned_center / MHZ_TO_HZ:.3f} MHz, Span={format_hz(returned_span)}"
            )
        else:
            showtime_tab_instance.console_print_func("❌ Poke command failed. Instrument did not confirm settings.")
            
    except ValueError:
        showtime_tab_instance.console_print_func("⚠️ Poke frequency must be a valid number.")
    except Exception as e:
        showtime_tab_instance.console_print_func(f"❌ Error during poke action: {e}")
        debug_log(f"Shiver me timbers, the poke be capsized! The error be: {e}",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)