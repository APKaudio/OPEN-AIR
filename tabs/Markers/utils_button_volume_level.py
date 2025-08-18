# util_button_volume_level.py
#
# This file provides a standalone utility function to generate a Unicode text-based
# progress bar for a given value within a specified range.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
#
#
# Version 20250818.235500.1
# FIX: The function now includes all necessary imports to operate as a standalone utility.

import inspect
import os

# Placeholder for logging functions to make the code stand alone.
# In a full application, these would be imported from a central logging module.
def debug_log(message, file=None, version=None, function=None):
    pass

current_version = "20250818.235500.1"


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
    debug_log(f"Entering {current_function} with value: {value}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
    try:
        value = float(value)
        if value < min_val:
            value = min_val
        if value > max_val:
            value = max_val
        
        percentage = (value - min_val) / (max_val - min_val)
        filled_length = int(width * percentage)
        
        bar = '█' * filled_length
        empty = ' ' * (width - filled_length)
        debug_log(f"Exiting {current_function}. Generated bar: [{bar}{empty}]", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        return f"[{bar}{empty}]"
    except (ValueError, TypeError) as e:
        debug_log(f"Error in {current_function}: {e}. Returning empty bar. Fucking useless!", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
        return f"[{' ' * width}]"