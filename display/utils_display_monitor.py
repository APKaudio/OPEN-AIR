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
# Version 20250813.100900.1 (FIXED: Added a check for empty data in update_annot to prevent IndexError.)

current_version = "20250813.100900.1"
current_version_hash = (20250813 * 100900 * 1)

import inspect
import os
import traceback 
import numpy as np
from matplotlib.offsetbox import AnchoredText 

from display.debug_logic import debug_log
from display.console_logic import console_log


def _find_and_plot_peaks(ax, data, start_freq_mhz, end_freq_mhz):
    # Function Description:
    # Finds and plots local peaks on a Matplotlib axis. A peak is defined as the highest
    # value within a segment of 1/150th of the total plot width. It then sorts and
    # displays only the top 10 peaks.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Scanning for peaks, with a magnifying glass! 🔎",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    if not data:
        debug_log("No data to search for peaks, moving on! 🚶‍♂️",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return

    try:
        x_data = np.array(data)[:, 0]
        y_data = np.array(data)[:, 1]
        
        # Calculate segment width for peak detection
        total_span = end_freq_mhz - start_freq_mhz
        segment_width = total_span / 150

        peaks = []
        i = 0
        while i < len(x_data):
            # Find the end of the current segment
            segment_end_freq = x_data[i] + segment_width
            
            # Find all data points within the current segment
            segment_indices = np.where((x_data >= x_data[i]) & (x_data <= segment_end_freq))
            if len(segment_indices[0]) == 0:
                i += 1
                continue
            
            segment_y_data = y_data[segment_indices]
            segment_x_data = x_data[segment_indices]

            # Find the peak (highest amplitude) within the segment
            peak_y = np.max(segment_y_data)
            peak_x = segment_x_data[np.argmax(segment_y_data)]
            
            peaks.append((peak_x, peak_y))

            # Move to the next segment
            # The next segment starts after the current segment's peak frequency
            # to prevent peaks from being "side-by-side".
            next_i_candidate = np.argmax(x_data >= peak_x + segment_width)
            if x_data[next_i_candidate] <= peak_x + segment_width:
                 next_i_candidate = np.where(x_data >= peak_x + segment_width)[0]
                 if len(next_i_candidate) > 0:
                    i = next_i_candidate[0]
                 else:
                    i = len(x_data)
            else:
                i = next_i_candidate
            
            if i >= len(x_data):
                break

        # Sort peaks by amplitude (y-value) in descending order and get the top 10
        sorted_peaks = sorted(peaks, key=lambda p: p[1], reverse=True)
        top_10_peaks = sorted_peaks[:10]

        # Plot the top 10 peaks
        for peak_x, peak_y in top_10_peaks:
            # CHANGED: Color from red to orange
            ax.axvline(x=peak_x, color='orange', linestyle='--', linewidth=1, zorder=4)
        
        debug_log(f"Found and plotted {len(top_10_peaks)} peaks. A job well done! ✨",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    except Exception as e:
        debug_log(f"Bug Expletives! The peak finder has failed us! 💥 Error: {e}. What a terrible turn of events! Traceback: {traceback.format_exc()}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function, special=True)

def _setup_zoom_events(ax, canvas, original_xlim):
    # Function Description:
    # Sets up event handlers for horizontal zooming on the plot.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Setting up zoom event handlers for the plot. Prepare for a closer look! 🔬",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    
    drag_start_x = None

    # Store the original limits on the axis object itself.
    ax.original_xlim = original_xlim

    def on_press(event):
        nonlocal drag_start_x
        if event.button == 1 and event.inaxes == ax: # Left mouse button
            drag_start_x = event.xdata
            debug_log(f"Mouse press detected. Zoom drag started at {drag_start_x:.3f} MHz. 🖱️",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

    def on_release(event):
        nonlocal drag_start_x
        if event.button == 1 and event.inaxes == ax and drag_start_x is not None:
            drag_end_x = event.xdata
            if drag_end_x is not None and drag_start_x != drag_end_x:
                min_x = min(drag_start_x, drag_end_x)
                max_x = max(drag_start_x, drag_end_x)
                ax.set_xlim(min_x, max_x)
                canvas.draw_idle()
                console_log(f"Zooming in on range: {min_x:.3f} MHz to {max_x:.3f} MHz.", function=current_function)
                debug_log(f"Zoom drag ended at {drag_end_x:.3f} MHz. New x-limits set. 🖼️",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            drag_start_x = None

    def on_double_click(event):
        if event.button == 1 and event.inaxes == ax:
            reset_zoom(ax, canvas)
            console_log("Double-click detected. Zoom reset.", function=current_function)
            debug_log(f"Double-click detected on plot. Resetting zoom to original limits. ✨",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

    canvas.mpl_connect('button_press_event', on_press)
    canvas.mpl_connect('button_release_event', on_release)
    # ADDED: Double-click event handler
    canvas.mpl_connect('button_press_event', on_double_click)
    
    debug_log(f"Zoom event listeners connected. The canvas is ready for action! ✅",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)


def reset_zoom(ax, canvas):
    # Function Description:
    # Resets the plot to its original, full x-axis view.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Resetting the plot view. Back to the big picture! 🖼️",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    if hasattr(ax, 'original_xlim'):
        ax.set_xlim(ax.original_xlim)
        canvas.draw_idle()
        console_log("Plot zoom reset to full view.", function=current_function)
        debug_log(f"Zoom successfully reset to original limits: {ax.original_xlim}.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_log(f"Cannot reset zoom, original limits not found on axis object. 🤷‍♂️",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


def update_top_plot(scan_monitor_tab_instance, data, start_freq_mhz, end_freq_mhz, plot_title):
    # Function Description:
    # Updates the top plot in the Scan Monitor tab with new data.
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
        debug_log("The scan_monitor_tab_instance is None. The plot is doomed! 👻",
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
            ax.plot(frequencies, amplitudes, color='yellow', linewidth=1)
        ax.set_title(plot_title, color='white')
        
        # CHANGED: Removed the y-axis label
        # ax.set_ylabel("Amplitude (dBm)", color='white')
        
        # NOTE: We set the xlim here, and store the initial limits for the zoom.
        ax.set_xlim(start_freq_mhz, end_freq_mhz)
        ax.set_ylim(-120, 0)
        ax.set_yticks(np.arange(-120, 1, 20))
        ax.grid(True, linestyle='--', color='gray', alpha=0.5)

        # NEW: Mouseover functionality
        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="white", ec="black", lw=1),
                            arrowprops=dict(arrowstyle="wedge,tail_width=0.5", fc="white", ec="black"))
        annot.set_visible(False)

        def update_annot(event):
            # FIX: Check if data is not empty before attempting to index it
            if data and event.xdata and event.ydata:
                # Find the nearest data point
                x_data = np.array(data)[:, 0]
                y_data = np.array(data)[:, 1]
                idx = np.abs(x_data - event.xdata).argmin()
                x_val = x_data[idx]
                y_val = y_data[idx]
                
                annot.xy = (x_val, y_val)
                text = f"Freq: {x_val:.3f} MHz\nAmp: {y_val:.2f} dBm"
                annot.set_text(text)
                annot.set_visible(True)
                canvas.draw_idle()
            else:
                annot.set_visible(False)
                canvas.draw_idle()

        canvas.mpl_connect("motion_notify_event", update_annot)
        
        _find_and_plot_peaks(ax, data, start_freq_mhz, end_freq_mhz)
        
        # NEW: Setup zoom events for this plot
        _setup_zoom_events(ax, canvas, (start_freq_mhz, end_freq_mhz))

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
            ax.plot(frequencies, amplitudes, color='green', linewidth=1)
        ax.set_title(plot_title, color='white')
        
        # CHANGED: Removed the y-axis label
        # ax.set_ylabel("Amplitude (dBm)", color='white')
        
        ax.set_xlim(start_freq_mhz, end_freq_mhz)
        ax.set_ylim(-120, 0)
        ax.set_yticks(np.arange(-120, 1, 20))
        ax.grid(True, linestyle='--', color='gray', alpha=0.5)

        # NEW: Mouseover functionality
        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="white", ec="black", lw=1),
                            arrowprops=dict(arrowstyle="wedge,tail_width=0.5", fc="white", ec="black"))
        annot.set_visible(False)

        def update_annot(event):
            # FIX: Check if data is not empty before attempting to index it
            if data and event.xdata and event.ydata:
                x_data = np.array(data)[:, 0]
                y_data = np.array(data)[:, 1]
                idx = np.abs(x_data - event.xdata).argmin()
                x_val = x_data[idx]
                y_val = y_data[idx]
                
                annot.xy = (x_val, y_val)
                text = f"Freq: {x_val:.3f} MHz\nAmp: {y_val:.2f} dBm"
                annot.set_text(text)
                annot.set_visible(True)
                canvas.draw_idle()
            else:
                annot.set_visible(False)
                canvas.draw_idle()

        canvas.mpl_connect("motion_notify_event", update_annot)

        _find_and_plot_peaks(ax, data, start_freq_mhz, end_freq_mhz)
        
        # NEW: Setup zoom events for this plot
        _setup_zoom_events(ax, canvas, (start_freq_mhz, end_freq_mhz))
        
        canvas.draw()
        
        debug_log("Successfully updated the medium plot. A masterpiece in the making! 🖼️",
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
            # CHANGED: Color from blue to cyan
            ax.plot(frequencies, amplitudes, color='cyan', linewidth=1)
        ax.set_title(plot_title, color='white')
        
        # CHANGED: Removed the y-axis label
        # ax.set_ylabel("Amplitude (dBm)", color='white')
        
        ax.set_xlim(start_freq_mhz, end_freq_mhz)
        ax.set_ylim(-120, 0)
        ax.set_yticks(np.arange(-120, 1, 20))
        ax.grid(True, linestyle='--', color='gray', alpha=0.5)

        # NEW: Mouseover functionality
        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="white", ec="black", lw=1),
                            arrowprops=dict(arrowstyle="wedge,tail_width=0.5", fc="white", ec="black"))
        annot.set_visible(False)

        def update_annot(event):
            # FIX: Check if data is not empty before attempting to index it
            if data and event.xdata and event.ydata:
                x_data = np.array(data)[:, 0]
                y_data = np.array(data)[:, 1]
                idx = np.abs(x_data - event.xdata).argmin()
                x_val = x_data[idx]
                y_val = y_data[idx]
                
                annot.xy = (x_val, y_val)
                text = f"Freq: {x_val:.3f} MHz\nAmp: {y_val:.2f} dBm"
                annot.set_text(text)
                annot.set_visible(True)
                canvas.draw_idle()
            else:
                annot.set_visible(False)
                canvas.draw_idle()

        canvas.mpl_connect("motion_notify_event", update_annot)
        
        _find_and_plot_peaks(ax, data, start_freq_mhz, end_freq_mhz)

        # NEW: Setup zoom events for this plot
        _setup_zoom_events(ax, canvas, (start_freq_mhz, end_freq_mhz))
        
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
        debug_log("The scan_monitor_tab_instance is None. The plot is lost in the void. 🌌",
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
        # CHANGED: Removed the y-axis label
        # ax_top.set_ylabel("Amplitude (dBm)", color='white')
        ax_top.set_ylim(-120, 0)
        ax_top.set_yticks(np.arange(-120, 1, 20))
        ax_top.grid(True, linestyle='--', color='gray', alpha=0.5)
        canvas_top.draw()

        plot_info_middle = scan_monitor_tab_instance.plots['middle']
        ax_middle = plot_info_middle['ax']
        canvas_middle = plot_info_middle['canvas']
        ax_middle.clear()
        ax_middle.set_facecolor('#1e1e1e')
        ax_middle.set_title("Plot 2 Placeholder", color='white')
        # CHANGED: Removed the y-axis label
        # ax_middle.set_ylabel("Amplitude (dBm)", color='white')
        ax_middle.set_ylim(-120, 0)
        ax_middle.set_yticks(np.arange(-120, 1, 20))
        ax_middle.grid(True, linestyle='--', color='gray', alpha=0.5)
        canvas_middle.draw()
        
        plot_info_bottom = scan_monitor_tab_instance.plots['bottom']
        ax_bottom = plot_info_bottom['ax']
        canvas_bottom = plot_info_bottom['canvas']
        ax_bottom.clear()
        ax_bottom.set_facecolor('#1e1e1e')
        ax_bottom.set_title("Plot 3 Placeholder", color='white')
        # CHANGED: Removed the y-axis label
        # ax_bottom.set_ylabel("Amplitude (dBm)", color='white')
        ax_bottom.set_ylim(-120, 0)
        ax_bottom.set_yticks(np.arange(-120, 1, 20))
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
