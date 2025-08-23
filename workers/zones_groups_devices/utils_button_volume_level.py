# tabs/Markers/showtime/util_button_volume_level.py
#
# This file provides a standalone utility function to generate a Unicode text-based
# progress bar for a given value within a specified range.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
#
#
# Version 20250822.103000.1
# UPDATED: The function now handles NaN values gracefully by returning an empty bar.
# UPDATED: File header and versioning adhere to new standards.
# UPDATED: All debug messages now include the correct emoji prefixes.

import inspect
import os
from datetime import datetime
import math # Import the math module to check for NaN

from display.debug_logic import debug_log

# --- Versioning ---
w = 20250822
x_str = '103000'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"

def create_signal_level_indicator(value, min_val=-120, max_val=0, width=24):
    """
    Generates a Unicode text-based progress bar for a given peak value.

    Args:
        value (float): The current value to represent in the progress bar.
        min_val (int): The minimum value of the range (e.g., -120 dBm).
        max_val (int): The maximum value of the range (e.g., 0 dBm).
        width (int): The width of the progress bar in characters.

    Returns:
        str: A string representing the Unicode progress bar, e.g., '[█████████        ]'.
    """
    current_function = inspect.currentframe().f_code.co_name
 #   debug_log(f"🛠️ 🟢 Entering {current_function} with value: {value}", file=current_file, version=current_version, function=current_function)
    try:
        # Check if the value is NaN or None and handle it gracefully
        if value is None or (isinstance(value, float) and math.isnan(value)):
            debug_log(f"🛠️ 🟡 Value is NaN or None. Returning empty bar.", file=current_file, version=current_version, function=current_function)
            return f"[{' ' * width}]"

        value = float(value)
        if value < min_val:
            value = min_val
        if value > max_val:
            value = max_val
        
        percentage = (value - min_val) / (max_val - min_val)
        filled_length = int(width * percentage)
        
        bar = '█' * filled_length
        empty = ' ' * (width - filled_length)
#        debug_log(f"🛠️ 🟢 Exiting {current_function}. Generated bar: [{bar}{empty}]", file=current_file, version=current_version, function=current_function)
        return f"[{bar}{empty}]"
    except (ValueError, TypeError) as e:
        debug_log(f"🛠️ ❌ Error in {current_function}: {e}. Returning empty bar. Fucking useless!", file=current_file, version=current_version, function=current_function)
        return f"[{' ' * width}]"
