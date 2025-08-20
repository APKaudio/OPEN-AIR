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
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250820.120100.1
# FIXED: The `on_span_button_click` function was corrected to access `scan_center_freq_var`
#        and `scan_span_freq_var` from `app_instance.orchestrator_logic`, resolving the
#        `AttributeError`.
# REFACTORED: The logic now explicitly sets the span and uses the existing center
#             frequency, as requested.
# FIXED: Corrected versioning to adhere to project standards.

import os
import inspect

from display.debug_logic import debug_log
from display.console_logic import console_log
from yak.utils_yakbeg_handler import handle_freq_center_span_beg

from process_math.math_frequency_translation import format_hz

# --- Versioning ---
w = 20250820
x = 120100
y = 1
current_version = f"Version {w}.{x}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"

def on_span_button_click(showtime_tab_instance, span_hz):
    # [Handles the event when a Span button is clicked.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function} with span_hz: {span_hz}",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=current_function)
    
    try:
        # Check if the user wants to follow the zone span
        showtime_tab_instance.shared_state.follow_zone_span_var.set(False)

        # Update the shared span variable on the parent instance
        showtime_tab_instance.shared_state.span_var.set(str(span_hz))

        # Re-sync all the control buttons
        showtime_tab_instance.controls_frame._update_control_styles()
        
        showtime_tab_instance.console_print_func(f"✅ Span set to {format_hz(span_hz)}.")

        # Trigger the handler to send the new span to the instrument.
        # It should use the current center frequency and the new span.
        current_center_freq = showtime_tab_instance.app_instance.orchestrator_logic.scan_center_freq_var.get()

        handle_freq_center_span_beg(app_instance=showtime_tab_instance.app_instance,
                                    center_freq=current_center_freq,
                                    span_freq=int(span_hz),
                                    console_print_func=showtime_tab_instance.console_print_func)

    except Exception as e:
        showtime_tab_instance.console_print_func(f"❌ Error setting span: {e}")
        debug_log(f"Arrr, a kraken be attacking the span settings! The error be: {e}",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)