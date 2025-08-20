# process_math/math_frequency_translation.py
#
# This file provides utility functions for converting and formatting frequency values.
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
# Version 20250820.233400.1
# REFACTORED: Removed versioning and file-specific metadata to make this a globally
#             available utility file.

import os
import inspect
from display.debug_logic import debug_log

# Conversion factor from MHz to Hz
MHZ_TO_HZ = 1_000_000
KHZ_TO_HZ = 1_000

def format_hz(hz_value):
    # [Formats a frequency in Hz to a human-readable string.]
    current_function = inspect.currentframe().f_code.co_name
    
    # NOTE: The version and file name are omitted from the debug log to make this
    #       function truly globally available and not tied to a specific file's metadata.
    debug_log(f"Entering {current_function} with value: {hz_value}", function=current_function)
    
    try:
        hz_value = float(hz_value)
        if hz_value >= MHZ_TO_HZ:
            return f"{hz_value / MHZ_TO_HZ:.1f} MHz"
        elif hz_value >= KHZ_TO_HZ:
            return f"{hz_value / KHZ_TO_HZ:.0f} kHz"
        else:
            return f"{hz_value} Hz"
    except (ValueError, TypeError) as e:
        debug_log(f"Arrr, a scallywag's value be here! The error be: {e}", function=current_function)
        return "N/A"