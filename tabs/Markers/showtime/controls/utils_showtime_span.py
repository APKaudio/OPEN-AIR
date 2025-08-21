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
# Version 20250823.003000.1
# UPDATED: File header and versioning adhere to new standards.
# UPDATED: `on_span_button_click` now correctly uses `showtime_tab_instance` to access the
#          `shared_state` and triggers a button style update, ensuring UI consistency.
# FIXED: The `on_span_button_click` function now saves the config after a successful operation.

import os
import inspect

from display.debug_logic import debug_log
from display.console_logic import console_log
from yak.utils_yakbeg_handler import handle_freq_center_span_beg
from yak.utils_yak_setting_handler import set_span_frequency
from src.settings_and_config.config_manager import save_config
from process_math.math_frequency_translation import format_hz

# --- Versioning ---
current_version = "20250823.003000.1"
current_version_hash = (20250823 * 3000 * 1)
current_file = file=f"{os.path.basename(__file__)}"

def on_span_button_click(showtime_tab_instance, span_hz):
    # [Handles the event when a Span button is clicked.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Entering {current_function} with span_hz: {span_hz}",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=current_function)
    
    try:
        # Check if the user wants to follow the zone span
        showtime_tab_instance.shared_state.follow_zone_span_var.set(False)

        # 📝 Write Data: Update the shared span variable on the parent instance.
        showtime_tab_instance.shared_state.span_var.set(str(span_hz))
        debug_log(message=f"📝 Writing shared state: span_var = {span_hz} Hz", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)

        # Re-sync all the control buttons
        showtime_tab_instance.controls_frame._update_control_styles()
        
        showtime_tab_instance.console_print_func(f"✅ Span set to {format_hz(span_hz)}.")

        # Trigger the handler to send the new span to the instrument.
        # It should use the current center frequency and the new span.
        
        set_span_frequency(app_instance=showtime_tab_instance.app_instance,
                                    value=span_hz / 1_000_000,
                                    console_print_func=showtime_tab_instance.console_print_func)
        
        # FIXED: Save config after a successful span change
        save_config(config=showtime_tab_instance.app_instance.config,
                    file_path=showtime_tab_instance.app_instance.CONFIG_FILE_PATH,
                    console_print_func=showtime_tab_instance.console_print_func,
                    app_instance=showtime_tab_instance.app_instance)

    except Exception as e:
        showtime_tab_instance.console_print_func(f"❌ Error setting span: {e}")
        debug_log(message=f"Arrr, a kraken be attacking the span settings! The error be: {e}",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)
