# tabs/Markers/showtime/controls/utils_showtime_span.py
#
# This utility file centralizes the backend logic for controlling the instrument's
# Span settings. It contains functions that handle button clicks from the GUI
# and translate them into instrument commands.
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
# Version 20250820.233800.1
# REFACTORED: The local `format_hz` function was removed and replaced with an import
#             from `process_math.math_frequency_translation` for global availability.
# FIXED: The `on_span_button_click` function signature and internal logic were updated
#        to correctly use the `span_tab_instance`, resolving `AttributeError`s.

current_version = "20250820.233800.1"
current_version_hash = (20250820 * 233800 * 1)

import os
import inspect

from display.debug_logic import debug_log
from display.console_logic import console_log
from yak.utils_yakbeg_handler import handle_freq_center_span_beg

from process_math.math_frequency_translation import format_hz

def on_span_button_click(span_tab_instance, span_hz):
    # [Handles the event when a Span button is clicked.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function} with span_hz: {span_hz}",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=current_function)
    
    try:
        # Check if the user wants to follow the zone span
        span_tab_instance.controls_frame.follow_zone_span_var.set(False)

        # Update the span variable on the tab instance
        span_tab_instance.span_var.set(str(span_hz))

        # Re-sync all the control buttons
        span_tab_instance._sync_ui_from_app_state()
        
        span_tab_instance.controls_frame.console_print_func(f"✅ Span set to {format_hz(span_hz)}.")

        # Trigger the handler to send the new span to the instrument.
        handle_freq_center_span_beg(span_tab_instance.controls_frame.app_instance, center_freq=span_tab_instance.controls_frame.app_instance.scan_center_freq_var.get(), span_freq=int(span_hz), console_print_func=span_tab_instance.controls_frame.console_print_func)

    except Exception as e:
        span_tab_instance.controls_frame.console_print_func(f"❌ Error setting span: {e}")
        debug_log(f"Arrr, a kraken be attacking the span settings! The error be: {e}",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)