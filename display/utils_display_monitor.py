# display/utils_display_monitor.py
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
# Version 20250814.091200.1

current_version = "20250814.091200.1"
current_version_hash = (20250814 * 91200 * 1)

import inspect
import os
import traceback 
import numpy as np
from matplotlib.offsetbox import AnchoredText 

from display.debug_logic import debug_log
from display.console_logic import console_log


def _find_and_plot_peaks(ax, data, start_freq_mhz, end_freq_mhz):
    # [A brief, one-sentence description of the function's purpose.]
    # Finds and plots local peaks on a Matplotlib axis.
    debug_log(f"Entering _find_and_plot_peaks with {len(data) if data else 0} data points.",
                file=f"{__name__}", version=current_version, function=inspect.currentframe().f_code.co_name)

    try:
        if not data:
            console_log("✅ No data to search for peaks.")
            return

        x_data = np.array(data)[:, 0]
        y_data = np.array(data)[:, 1]
        
        total_span = end_freq_mhz - start_freq_mhz
        segment_width = total_span / 150
        peaks = []
        i = 0
        while i < len(x_data):
            segment_end_freq = x_data[i] + segment_width
            segment_indices = np.where((x_data >= x_data[i]) & (x_data <= segment_end_freq))
            if not segment_indices[0].any():
                i += 1
                continue
            
            segment_y_data = y_data[segment_indices]
            segment_x_data = x_data[segment_indices]
            peak_y = np.max(segment_y_data)
            peak_x = segment_x_data[np.argmax(segment_y_data)]
            peaks.append((peak_x, peak_y))

            next_i_candidate = np.where(x_data >= peak_x + segment_width)[0]
            i = next_i_candidate[0] if len(next_i_candidate) > 0 else len(x_data)
        
        sorted_peaks = sorted(peaks, key=lambda p: p[1], reverse=True)[:10]
        for peak_x, peak_y in sorted_peaks:
            ax.axvline(x=peak_x, color='orange', linestyle='--', linewidth=1, zorder=4)
        
        console_log(f"✅ Found and plotted {len(sorted_peaks)} peaks.")
    except Exception as e:
        console_log(f"❌ Error in _find_and_plot_peaks: {e}")
        debug_log(f"Arrr, the code be capsized in peak finding! The error be: {e}\n{traceback.format_exc()}",
                    file=f"{__name__}", version=current_version, function=inspect.currentframe().f_code.co_name)

def _setup_zoom_events(ax, canvas, original_xlim):
    # [A brief, one-sentence description of the function's purpose.]
    # Sets up event handlers for horizontal zooming on the plot.
    debug_log(f"Entering _setup_zoom_events.", file=f"{__name__}", version=current_version, function=inspect.currentframe().f_code.co_name)
    
    try:
        drag_start_x = None
        ax.original_xlim = original_xlim

        def on_press(event):
            nonlocal drag_start_x
            if event.button == 1 and event.inaxes == ax:
                drag_start_x = event.xdata

        def on_release(event):
            nonlocal drag_start_x
            if event.button == 1 and event.inaxes == ax and drag_start_x is not None:
                drag_end_x = event.xdata
                if drag_end_x is not None and drag_start_x != drag_end_x:
                    ax.set_xlim(min(drag_start_x, drag_end_x), max(drag_start_x, drag_end_x))
                    canvas.draw_idle()
                drag_start_x = None

        def on_double_click(event):
            if event.button == 1 and event.inaxes == ax:
                reset_zoom(ax=ax, canvas=canvas)

        canvas.mpl_connect('button_press_event', on_press)
        canvas.mpl_connect('button_release_event', on_release)
        canvas.mpl_connect('button_press_event', on_double_click)
        console_log("✅ Zoom events are now live!")
    except Exception as e:
        console_log(f"❌ Error in _setup_zoom_events: {e}")
        debug_log(f"Great Scott! The zoom mechanism has backfired! Error: {e}\n{traceback.format_exc()}",
                    file=f"{__name__}", version=current_version, function=inspect.currentframe().f_code.co_name)

def reset_zoom(ax, canvas):
    # [A brief, one-sentence description of the function's purpose.]
    # Resets the plot to its original, full x-axis view.
    debug_log(f"Entering reset_zoom.", file=f"{__name__}", version=current_version, function=inspect.currentframe().f_code.co_name)
    try:
        if hasattr(ax, 'original_xlim'):
            ax.set_xlim(ax.original_xlim)
            canvas.draw_idle()
        console_log("✅ Celebration of success! Zoom reset.")
    except Exception as e:
        console_log(f"❌ Error in reset_zoom: {e}")
        debug_log(f"It's madness! The zoom refused to reset! Error: {e}\n{traceback.format_exc()}",
                    file=f"{__name__}", version=current_version, function=inspect.currentframe().f_code.co_name)

def update_top_plot(scan_monitor_tab_instance, data, start_freq_mhz, end_freq_mhz, plot_title):
    # [A brief, one-sentence description of the function's purpose.]
    # Updates the top plot in the Scan Monitor tab with new data.
    debug_log(f"Entering update_top_plot with plot_title: {plot_title}", file=f"{__name__}", version=current_version, function=inspect.currentframe().f_code.co_name)
        
    try:
        plot_info = scan_monitor_tab_instance.plots["top"]
        ax = plot_info['ax']
        canvas = plot_info['canvas']
        ax.clear()
        
        data_tuples = None
        # FIX: The incoming data DataFrame now has frequencies in MHz.
        # We no longer need to divide by 1,000,000 here.
        if data is not None and not data.empty:
            data_tuples = list(zip(data['Frequency_Hz'], data['Power_dBm']))

        if data_tuples:
            frequencies, amplitudes = zip(*data_tuples)
            ax.plot(frequencies, amplitudes, color='yellow', linewidth=1)
        
        ax.set_title(plot_title, color='white')
        ax.set_xlim(start_freq_mhz, end_freq_mhz)
        ax.set_ylim(-120, 0)
        ax.set_yticks(np.arange(-120, 1, 20))
        ax.grid(True, linestyle='--', color='gray', alpha=0.5)

        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="white", ec="black", lw=1),
                            arrowprops=dict(arrowstyle="wedge,tail_width=0.5", fc="white", ec="black"))
        annot.set_visible(False)

        def update_annot(event):
            if data_tuples and event.xdata and event.ydata:
                x_data = np.array(data_tuples)[:, 0]
                y_data = np.array(data_tuples)[:, 1]
                idx = np.abs(x_data - event.xdata).argmin()
                annot.xy = (x_data[idx], y_data[idx])
                annot.set_text(f"Freq: {x_data[idx]:.3f} MHz\nAmp: {y_data[idx]:.2f} dBm")
                annot.set_visible(True)
                canvas.draw_idle()
            else:
                annot.set_visible(False)
                canvas.draw_idle()

        canvas.mpl_connect("motion_notify_event", update_annot)
        
        _find_and_plot_peaks(ax=ax, data=data_tuples, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz)
        _setup_zoom_events(ax=ax, canvas=canvas, original_xlim=(start_freq_mhz, end_freq_mhz))

        canvas.draw()
        console_log("✅ Celebration of success! Top plot updated.")
    except Exception as e:
        console_log(f"❌ Error in update_top_plot: {e}")
        debug_log(f"Arrr, the top plot be capsized! The error be: {e}\n{traceback.format_exc()}",
                    file=f"{__name__}", version=current_version, function=inspect.currentframe().f_code.co_name)

def update_middle_plot(scan_monitor_tab_instance, data, start_freq_mhz, end_freq_mhz, plot_title):
    # [A brief, one-sentence description of the function's purpose.]
    # Updates the middle plot in the Scan Monitor tab with new data.
    debug_log(f"Entering update_middle_plot with plot_title: {plot_title}", file=f"{__name__}", version=current_version, function=inspect.currentframe().f_code.co_name)

    try:
        plot_info = scan_monitor_tab_instance.plots["middle"]
        ax = plot_info['ax']
        canvas = plot_info['canvas']
        ax.clear()

        data_tuples = None
        # FIX: The incoming data DataFrame now has frequencies in MHz.
        # We no longer need to divide by 1,000,000 here.
        if data is not None and not data.empty:
            data_tuples = list(zip(data['Frequency_Hz'], data['Power_dBm']))

        if data_tuples:
            frequencies, amplitudes = zip(*data_tuples)
            ax.plot(frequencies, amplitudes, color='green', linewidth=1)
        
        ax.set_title(plot_title, color='white')
        ax.set_xlim(start_freq_mhz, end_freq_mhz)
        ax.set_ylim(-120, 0)
        ax.set_yticks(np.arange(-120, 1, 20))
        ax.grid(True, linestyle='--', color='gray', alpha=0.5)

        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="white", ec="black", lw=1),
                            arrowprops=dict(arrowstyle="wedge,tail_width=0.5", fc="white", ec="black"))
        annot.set_visible(False)

        def update_annot(event):
            if data_tuples and event.xdata and event.ydata:
                x_data = np.array(data_tuples)[:, 0]
                y_data = np.array(data_tuples)[:, 1]
                idx = np.abs(x_data - event.xdata).argmin()
                annot.xy = (x_data[idx], y_data[idx])
                annot.set_text(f"Freq: {x_data[idx]:.3f} MHz\nAmp: {y_data[idx]:.2f} dBm")
                annot.set_visible(True)
                canvas.draw_idle()
            else:
                annot.set_visible(False)
                canvas.draw_idle()

        canvas.mpl_connect("motion_notify_event", update_annot)

        _find_and_plot_peaks(ax=ax, data=data_tuples, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz)
        _setup_zoom_events(ax=ax, canvas=canvas, original_xlim=(start_freq_mhz, end_freq_mhz))
        
        canvas.draw()
        console_log("✅ Celebration of success! Middle plot updated.")
    except Exception as e:
        console_log(f"❌ Error in update_middle_plot: {e}")
        debug_log(f"It's alive! Oh wait, no, the middle plot is dead. Error: {e}\n{traceback.format_exc()}",
                    file=f"{__name__}", version=current_version, function=inspect.currentframe().f_code.co_name)

def update_bottom_plot(scan_monitor_tab_instance, data, start_freq_mhz, end_freq_mhz, plot_title):
    # [A brief, one-sentence description of the function's purpose.]
    # Updates the bottom plot in the Scan Monitor tab with new data.
    debug_log(f"Entering update_bottom_plot with plot_title: {plot_title}", file=f"{__name__}", version=current_version, function=inspect.currentframe().f_code.co_name)
    
    try:
        plot_info = scan_monitor_tab_instance.plots["bottom"]
        ax = plot_info['ax']
        canvas = plot_info['canvas']
        
        ax.clear()

        data_tuples = None
        # FIX: The incoming data DataFrame now has frequencies in MHz.
        # We no longer need to divide by 1,000,000 here.
        if data is not None and not data.empty:
            data_tuples = list(zip(data['Frequency_Hz'], data['Power_dBm']))

        if data_tuples:
            frequencies, amplitudes = zip(*data_tuples)
            ax.plot(frequencies, amplitudes, color='cyan', linewidth=1)
        
        ax.set_title(plot_title, color='white')
        ax.set_xlim(start_freq_mhz, end_freq_mhz)
        ax.set_ylim(-120, 0)
        ax.set_yticks(np.arange(-120, 1, 20))
        ax.grid(True, linestyle='--', color='gray', alpha=0.5)

        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="white", ec="black", lw=1),
                            arrowprops=dict(arrowstyle="wedge,tail_width=0.5", fc="white", ec="black"))
        annot.set_visible(False)

        def update_annot(event):
            if data_tuples and event.xdata and event.ydata:
                x_data = np.array(data_tuples)[:, 0]
                y_data = np.array(data_tuples)[:, 1]
                idx = np.abs(x_data - event.xdata).argmin()
                annot.xy = (x_data[idx], y_data[idx])
                annot.set_text(f"Freq: {x_data[idx]:.3f} MHz\nAmp: {y_data[idx]:.2f} dBm")
                annot.set_visible(True)
                canvas.draw_idle()
            else:
                annot.set_visible(False)
                canvas.draw_idle()

        canvas.mpl_connect("motion_notify_event", update_annot)
        
        _find_and_plot_peaks(ax=ax, data=data_tuples, start_freq_mhz=start_freq_mhz, end_freq_mhz=end_freq_mhz)
        _setup_zoom_events(ax=ax, canvas=canvas, original_xlim=(start_freq_mhz, end_freq_mhz))
        
        canvas.draw()
        console_log("✅ Celebration of success! Bottom plot updated.")
    except Exception as e:
        console_log(f"❌ Error in update_bottom_plot: {e}")
        debug_log(f"Shiver me timbers, the bottom plot has been scuttled! Error: {e}\n{traceback.format_exc()}",
                    file=f"{__name__}", version=current_version, function=inspect.currentframe().f_code.co_name)

def clear_monitor_plots(scan_monitor_tab_instance):
    # [A brief, one-sentence description of the function's purpose.]
    # Clears all three plots in the Scan Monitor tab.
    debug_log(f"Entering clear_monitor_plots.", file=f"{__name__}", version=current_version, function=inspect.currentframe().f_code.co_name)
                
    try:
        if not scan_monitor_tab_instance:
            console_log("❌ Scan Monitor tab instance could not be found. Cannot clear plots.")
            return

        for plot_name in ["top", "middle", "bottom"]:
            plot_info = scan_monitor_tab_instance.plots.get(plot_name, {})
            ax = plot_info.get('ax')
            canvas = plot_info.get('canvas')
            if ax and canvas:
                ax.clear()
                ax.set_facecolor('#1e1e1e')
                ax.set_title(f"Plot {plot_name.capitalize()} Placeholder", color='white')
                ax.set_ylim(-120, 0)
                ax.set_yticks(np.arange(-120, 1, 20))
                ax.grid(True, linestyle='--', color='gray', alpha=0.5)
                canvas.draw()
        
        console_log("✅ Celebration of success! All monitor plots cleared.")
    except Exception as e:
        console_log(f"❌ Error in clear_monitor_plots: {e}")
        debug_log(f"My creation! It refuses to be cleared! Error: {e}\n{traceback.format_exc()}",
                    file=f"{__name__}", version=current_version, function=inspect.currentframe().f_code.co_name)
