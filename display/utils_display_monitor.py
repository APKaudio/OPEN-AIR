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
# Version 20250810.220500.53 (FIXED: Removed the redundant x-axis labels from all plotting and clearing functions for a cleaner display.)

import inspect
import os
import traceback 
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log
from display.display_child_scan_monitor import ScanMonitorTab


current_version = "20250810.220500.53"
current_version_hash = 20250810 * 220500 * 53


def update_top_plot(scan_monitor_tab_instance, data, start_freq_mhz, end_freq_mhz, plot_title):
    # Function Description:
    # Updates the top plot in the Scan Monitor tab with new data.
    #
    # Inputs to this function:
    #   scan_monitor_tab_instance (object): A reference to the ScanMonitorTab instance.
    #   data (list): A list of (frequency, amplitude) tuples to plot.
    #   start_freq_mhz (float): The start frequency for the x-axis.
    #   end_freq_mhz (float): The end frequency for the x-axis.
    #   plot_title (str): The title for the plot.
    #
    # Outputs of this function:
    #   None. Triggers a plot update.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering update_top_plot. Let's see what we've got here! 🧐",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    debug_log(f"Received: scan_monitor_tab_instance (Type: {type(scan_monitor_tab_instance)}), data (Length: {len(data) if data is not None else 'None'}), start_freq_mhz: {start_freq_mhz}, end_freq_mhz: {end_freq_mhz}, plot_title: {plot_title}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function, special=True)
    
    if not scan_monitor_tab_instance:
        console_log("❌ The Scan Monitor tab instance could not be found. Display updates aborted.")
        debug_log("The scan_monitor_tab_instance is None. The plot is doomed! 💀",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function, special=True)
        return
        
    try:
        plot_info = scan_monitor_tab_instance.plots["top"]
        ax = plot_info['ax']
        canvas = plot_info['canvas']
        
        ax.clear()
        if data:
            frequencies, amplitudes = zip(*data)
            # CHANGED: Plot color to yellow and added thin linewidth
            ax.plot(frequencies, amplitudes, color='yellow', linewidth=1)
        ax.set_title(plot_title, color='white')
        ax.set_ylabel("Amplitude (dBm)", color='white')
        ax.set_xlim(start_freq_mhz, end_freq_mhz) # Set x-axis limits
        ax.set_ylim(-120, 0) # Set y-axis limits
        ax.set_yticks(np.arange(-120, 1, 20)) # Add grid lines every 20dBm
        ax.grid(True, linestyle='--', color='gray', alpha=0.5)
        canvas.draw()
        debug_log("Successfully updated the top plot. A true triumph! ✅",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    except Exception as e:
        error_message = f"ERROR: Failed to update top plot: {e}"
        console_log(error_message, function=current_function)
        debug_log(f"Unexpected error: {e}. Plot update failed. What a disaster! 💥 Traceback: {traceback.format_exc()}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function, special=True)


def update_medium_plot(scan_monitor_tab_instance, data, start_freq_mhz, end_freq_mhz, plot_title):
    # Function Description:
    # Updates the medium plot in the Scan Monitor tab with new data.
    #
    # Inputs to this function:
    #   scan_monitor_tab_instance (object): A reference to the ScanMonitorTab instance.
    #   data (list): A list of (frequency, amplitude) tuples to plot.
    #   start_freq_mhz (float): The start frequency for the x-axis.
    #   end_freq_mhz (float): The end frequency for the x-axis.
    #   plot_title (str): The title for the plot.
    #
    # Outputs of this function:
    #   None. Triggers a plot update.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering update_medium_plot. Let's inspect the payload. 🕵️‍♂️",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    debug_log(f"Received: scan_monitor_tab_instance (Type: {type(scan_monitor_tab_instance)}), data (Length: {len(data) if data is not None else 'None'}), start_freq_mhz: {start_freq_mhz}, end_freq_mhz: {end_freq_mhz}, plot_title: {plot_title}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function, special=True)

    if not scan_monitor_tab_instance:
        console_log("❌ The Scan Monitor tab instance could not be found. Display updates aborted.")
        debug_log("The scan_monitor_tab_instance is None. The plot is in a state of existential dread! 😱",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function, special=True)
        return

    try:
        plot_info = scan_monitor_tab_instance.plots["middle"]
        ax = plot_info['ax']
        canvas = plot_info['canvas']
        
        ax.clear()
        if data:
            frequencies, amplitudes = zip(*data)
            # CHANGED: Plot color to green and added thin linewidth
            ax.plot(frequencies, amplitudes, color='green', linewidth=1)
        ax.set_title(plot_title, color='white')
        ax.set_ylabel("Amplitude (dBm)", color='white')
        ax.set_xlim(start_freq_mhz, end_freq_mhz) # Set x-axis limits
        ax.set_ylim(-120, 0) # Set y-axis limits
        ax.set_yticks(np.arange(-120, 1, 20)) # Add grid lines every 20dBm
        ax.grid(True, linestyle='--', color='gray', alpha=0.5)
        canvas.draw()
        debug_log("Successfully updated the medium plot. A masterpiece in the making! �",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    except Exception as e:
        error_message = f"ERROR: Failed to update medium plot: {e}"
        console_log(error_message, function=current_function)
        debug_log(f"Unexpected error: {e}. Plot update failed. This is a tragedy! 😭 Traceback: {traceback.format_exc()}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function, special=True)


def update_bottom_plot(scan_monitor_tab_instance, data, start_freq_mhz, end_freq_mhz, plot_title):
    # Function Description:
    # Updates the bottom plot in the Scan Monitor tab with new data.
    #
    # Inputs to this function:
    #   scan_monitor_tab_instance (object): A reference to the ScanMonitorTab instance.
    #   data (list): A list of (frequency, amplitude) tuples to plot.
    #   start_freq_mhz (float): The start frequency for the x-axis.
    #   end_freq_mhz (float): The end frequency for the x-axis.
    #   plot_title (str): The title for the plot.
    #
    # Outputs of this function:
    #   None. Triggers a plot update.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering update_bottom_plot. Let's get this done. 🚀",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    debug_log(f"Received: scan_monitor_tab_instance (Type: {type(scan_monitor_tab_instance)}), data (Length: {len(data) if data is not None else 'None'}), start_freq_mhz: {start_freq_mhz}, end_freq_mhz: {end_freq_mhz}, plot_title: {plot_title}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function, special=True)
    
    if not scan_monitor_tab_instance:
        console_log("❌ The Scan Monitor tab instance could not be found. Display updates aborted.")
        debug_log("The scan_monitor_tab_instance is None. The plot is lost in the void. 🌌",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function, special=True)
        return

    try:
        plot_info = scan_monitor_tab_instance.plots["bottom"]
        ax = plot_info['ax']
        canvas = plot_info['canvas']
        
        ax.clear()
        if data:
            frequencies, amplitudes = zip(*data)
            # CHANGED: Plot color to blue and added thin linewidth
            ax.plot(frequencies, amplitudes, color='blue', linewidth=1)
        ax.set_title(plot_title, color='white')
        ax.set_ylabel("Amplitude (dBm)", color='white')
        ax.set_xlim(start_freq_mhz, end_freq_mhz) # Set x-axis limits
        ax.set_ylim(-120, 0) # Set y-axis limits
        ax.set_yticks(np.arange(-120, 1, 20)) # Add grid lines every 20dBm
        ax.grid(True, linestyle='--', color='gray', alpha=0.5)
        canvas.draw()
        debug_log("Successfully updated the bottom plot. A true scientific marvel! ✨",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    except Exception as e:
        error_message = f"ERROR: Failed to update bottom plot: {e}"
        console_log(error_message, function=current_function)
        debug_log(f"Unexpected error: {e}. Plot update failed. This is a tragedy! 😭 Traceback: {traceback.format_exc()}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function, special=True)


def clear_monitor_plots(scan_monitor_tab_instance):
    # Function Description:
    # Clears all three plots in the Scan Monitor tab.
    #
    # Inputs to this function:
    #   scan_monitor_tab_instance (object): A reference to the ScanMonitorTab instance.
    #
    # Outputs of this function:
    #   None. Triggers the plot clearing.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering clear_monitor_plots. Let's clean up this mess! 🧹",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    debug_log(f"Received: scan_monitor_tab_instance (Type: {type(scan_monitor_tab_instance)})",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function, special=True)
                
    if not scan_monitor_tab_instance:
        console_log("❌ The Scan Monitor tab instance could not be found. Display updates aborted.")
        debug_log("The scan_monitor_tab_instance is None. Aborting plot clear. The universe is in chaos! 💥",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function, special=True)
        return
        
    try:
        plot_info_top = scan_monitor_tab_instance.plots['top']
        ax_top = plot_info_top['ax']
        canvas_top = plot_info_top['canvas']
        ax_top.clear()
        ax_top.set_facecolor('#1e1e1e')
        ax_top.set_title("Plot 1 Placeholder", color='white')
        ax_top.set_ylabel("Amplitude (dBm)", color='white')
        ax_top.set_ylim(-120, 0) # Set y-axis limits
        ax_top.set_yticks(np.arange(-120, 1, 20)) # Add grid lines every 20dBm
        ax_top.grid(True, linestyle='--', color='gray', alpha=0.5)
        canvas_top.draw()

        plot_info_middle = scan_monitor_tab_instance.plots['middle']
        ax_middle = plot_info_middle['ax']
        canvas_middle = plot_info_middle['canvas']
        ax_middle.clear()
        ax_middle.set_facecolor('#1e1e1e')
        ax_middle.set_title("Plot 2 Placeholder", color='white')
        ax_middle.set_ylabel("Amplitude (dBm)", color='white')
        ax_middle.set_ylim(-120, 0) # Set y-axis limits
        ax_middle.set_yticks(np.arange(-120, 1, 20)) # Add grid lines every 20dBm
        ax_middle.grid(True, linestyle='--', color='gray', alpha=0.5)
        canvas_middle.draw()
        
        plot_info_bottom = scan_monitor_tab_instance.plots['bottom']
        ax_bottom = plot_info_bottom['ax']
        canvas_bottom = plot_info_bottom['canvas']
        ax_bottom.clear()
        ax_bottom.set_facecolor('#1e1e1e')
        ax_bottom.set_title("Plot 3 Placeholder", color='white')
        ax_bottom.set_ylabel("Amplitude (dBm)", color='white')
        ax_bottom.set_ylim(-120, 0) # Set y-axis limits
        ax_bottom.set_yticks(np.arange(-120, 1, 20)) # Add grid lines every 20dBm
        ax_bottom.grid(True, linestyle='--', color='gray', alpha=0.5)
        canvas_bottom.draw()
        
        console_log("✅ All plots cleared.", function=current_function)
        debug_log("Successfully called clear_monitor_plots. A clean slate for new discoveries! ✨",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    except Exception as e:
        error_message = f"ERROR: Failed to clear plots: {e}"
        console_log(error_message, function=current_function)
        debug_log(f"Unexpected error: {e}. Plot clear failed. This experiment has failed! 🧪 Traceback: {traceback.format_exc()}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function, special=True)