# utils/utils_display_monitor.py
#
# This module provides utility functions to interact with and update the plots
# in the Scan Monitor display tab.
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
# Version 20250810.160100.2 (UPDATED: Renamed plot update functions to top, medium, and bottom.)

current_version = "20250810.160100.2"
current_version_hash = 20250810 * 160100 * 2 # Example hash, adjust as needed

import inspect
import os

from display.debug_logic import debug_log
from display.console_logic import console_log


def update_top_plot(app_instance, data, start, end):
    # Function Description:
    # Updates the top plot in the Scan Monitor tab with new data.
    #
    # Inputs to this function:
    #   app_instance (object): A reference to the main application instance.
    #   data (list): The Y-axis data to plot.
    #   start (int): The starting value for the X-axis.
    #   end (int): The ending value for the X-axis.
    #
    # Outputs of this function:
    #   None. Triggers a plot update.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Updating top plot.",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    try:
        app_instance.scan_monitor_tab.update_plot1(data, start, end)
    except AttributeError:
        console_log(f"ERROR: Scan Monitor tab not available or `update_plot1` function missing. Fucking useless!",
                    function=current_function)
    except Exception as e:
        console_log(f"ERROR: Failed to update top plot: {e}",
                    function=current_function)


def update_medium_plot(app_instance, data, start, end):
    # Function Description:
    # Updates the medium plot in the Scan Monitor tab with new data.
    #
    # Inputs to this function:
    #   app_instance (object): A reference to the main application instance.
    #   data (list): The Y-axis data to plot.
    #   start (int): The starting value for the X-axis.
    #   end (int): The ending value for the X-axis.
    #
    # Outputs of this function:
    #   None. Triggers a plot update.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Updating medium plot.",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    try:
        app_instance.scan_monitor_tab.update_plot2(data, start, end)
    except AttributeError:
        console_log(f"ERROR: Scan Monitor tab not available or `update_plot2` function missing. This shit is broken.",
                    function=current_function)
    except Exception as e:
        console_log(f"ERROR: Failed to update medium plot: {e}",
                    function=current_function)


def update_bottom_plot(app_instance, data, start, end):
    # Function Description:
    # Updates the bottom plot in the Scan Monitor tab with new data.
    #
    # Inputs to this function:
    #   app_instance (object): A reference to the main application instance.
    #   data (list): The Y-axis data to plot.
    #   start (int): The starting value for the X-axis.
    #   end (int): The ending value for the X-axis.
    #
    # Outputs of this function:
    #   None. Triggers a plot update.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Updating bottom plot.",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    try:
        app_instance.scan_monitor_tab.update_plot3(data, start, end)
    except AttributeError:
        console_log(f"ERROR: Scan Monitor tab not available or `update_plot3` function missing. What a disaster.",
                    function=current_function)
    except Exception as e:
        console_log(f"ERROR: Failed to update bottom plot: {e}",
                    function=current_function)


def clear_monitor_plots(app_instance):
    # Function Description:
    # Clears all three plots in the Scan Monitor tab.
    #
    # Inputs to this function:
    #   app_instance (object): A reference to the main application instance.
    #
    # Outputs of this function:
    #   None. Triggers the plot clearing.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Clearing all plots in the Scan Monitor tab.",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    try:
        app_instance.scan_monitor_tab.clear_all_plots()
    except AttributeError:
        console_log(f"ERROR: Scan Monitor tab not available or `clear_all_plots` function missing. Can't clear the goddamn plots.",
                    function=current_function)
    except Exception as e:
        console_log(f"ERROR: Failed to clear plots: {e}",
                    function=current_function)

