# workers/utils_marker_logic.py
#
# A utility module to contain core business logic functions related to marker data
# processing and calculation, ensuring separation of concerns (DOP 6.2).
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
# Version 20251005.230247.1

import os
import inspect

# --- Graceful Dependency Importing ---
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False
    
# --- Module Imports ---
from workers.worker_active_logging import debug_log, console_log

# --- Global Scope Variables (as per Section 4.4) ---
current_version = "20251005.230247.1"
# The hash calculation drops the leading zero from the hour (23 -> 23)
current_version_hash = (20251005 * 230247 * 1)
current_file = f"{os.path.basename(__file__)}"


def calculate_frequency_range(marker_data_list):
    # Calculates the minimum and maximum frequencies from a list of marker dictionaries.
    current_function_name = inspect.currentframe().f_code.co_name
    
    # [A brief, one-sentence description of the function's purpose.]
    debug_log(
        message=f"🛠️🟢 Entering {current_function_name} to divine the full spectral range from {len(marker_data_list)} markers.",
        file=current_file,
        version=current_version,
        function=current_function_name,
        console_print_func=console_log
    )

    if not marker_data_list:
        debug_log(
            message="🛠️🟡 The marker list is an empty void! Returning null range.",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )
        return None, None

    if not NUMPY_AVAILABLE:
        console_log("❌ Error: NumPy is required but not available. Cannot perform calculation.")
        return None, None
        
    try:
        freqs = []
        for marker in marker_data_list:
            try:
                # The canonical header for frequency is 'FREQ_MHZ'
                freqs.append(float(marker.get('FREQ_MHZ', 0)))
            except (ValueError, TypeError):
                continue
        
        if freqs:
            min_freq = np.min(freqs)
            max_freq = np.max(freqs)

            console_log(f"✅ Calculated range: {min_freq} MHz to {max_freq} MHz.")
            return min_freq, max_freq
        
        console_log("🟡 No valid frequencies found in marker data.")
        return None, None

    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        debug_log(
            message=f"🛠️🔴 Arrr, the code be capsized! Calculation failed: {e}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )
        return None, None