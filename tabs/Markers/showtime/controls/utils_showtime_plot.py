# tabs/Markers/showtime/controls/utils_showtime_plot.py
#
# This utility file centralizes all logic for fetching and plotting trace data
# from the instrument. It is designed to be called by the UI and acts as a
# high-level API for triggering trace actions and updating the display.
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
# Version 20250821.120100.4
# FIXED: The plotting functions are now correctly imported from `utils_display_monitor.py`
#        and `utils_scan_view.py` instead of being defined here, resolving the issue
#        of displaying plots on the monitor tab.
# FIXED: Corrected the `plot_all_traces` function to correctly access attributes from the `showtime_tab_instance`.
# FIXED: Corrected versioning to adhere to project standards.

import os
import inspect
import pandas as pd
import tkinter as tk
from ref.frequency_bands import MHZ_TO_HZ
from display.debug_logic import debug_log
from display.console_logic import console_log

# Import plotting functions from the display utilities
from display.utils_display_monitor import update_top_plot, update_middle_plot, update_bottom_plot

# --- Versioning ---
w = 20250821
x = 120100
y = 4
current_version = f"Version {w}.{x}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"


def plot_all_traces(showtime_tab_instance, trace_data_dict, view_name, start_freq_mhz, stop_freq_mhz):
    # [Updates the display plots with trace data from the instrument.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function} with view_name: {view_name}",
              file=f"{os.path.basename(__file__)}",
              version=current_version,
              function=current_function)
    
    if trace_data_dict:
        monitor_tab = showtime_tab_instance.app_instance.display_parent_tab.bottom_pane.scan_monitor_tab
        if monitor_tab:
            df1 = pd.DataFrame(trace_data_dict["TraceData"]["Trace1"], columns=['Frequency_Hz', 'Power_dBm'])
            update_top_plot(monitor_tab, df1, start_freq_mhz, stop_freq_mhz, f"Live Trace - {view_name}")
            
            df2 = pd.DataFrame(trace_data_dict["TraceData"]["Trace2"], columns=['Frequency_Hz', 'Power_dBm'])
            update_middle_plot(monitor_tab, df2, start_freq_mhz, stop_freq_mhz, f"Max Hold - {view_name}")

            df3 = pd.DataFrame(trace_data_dict["TraceData"]["Trace3"], columns=['Frequency_Hz', 'Power_dBm'])
            update_bottom_plot(monitor_tab, df3, start_freq_mhz, stop_freq_mhz, f"Min Hold - {view_name}")
            
            showtime_tab_instance.console_print_func("✅ Successfully updated monitor with all three traces.")
            
            # This is a bit of a hack to ensure the monitor tab is visible
            showtime_tab_instance.app_instance.display_parent_tab.change_display_tab('Monitor')
        else:
            showtime_tab_instance.console_print_func("❌ Scan Monitor tab not found.")
    else:
        showtime_tab_instance.console_print_func("❌ Failed to retrieve trace data.")
        debug_log(f"Shiver me timbers, the trace data be lost at sea!",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)