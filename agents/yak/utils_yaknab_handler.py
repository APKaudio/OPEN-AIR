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
# Version 20250821.210502.1
# UPDATED: Added new handler for Amplitude settings.
# FIXED: Corrected the parsing logic to handle both float and string responses for boolean-like settings.
# UPDATED: The function now handles a 5th return value for Sweep Time.
# NEW: Implemented a new handler for the TRACE/ALL/ONETWOTHREE NAB command, designed to handle multiple reads for large data sets.
# UPDATED: All debug messages now include the required 🐐 emoji at the start.

import inspect
import os
import numpy as np
from typing import Optional, List, Dict

from yak.Yakety_Yak import YakBeg, YakNab
from display.debug_logic import debug_log
from display.console_logic import console_log


# --- Versioning ---
w = 20250821
x_str = '210502'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"
