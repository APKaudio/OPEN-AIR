# display/display_child_scan_monitor.py
#
# This file defines the ScanMonitorTab, a Tkinter Frame that provides
# a real-time view of scan data using Matplotlib plots.
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
# Version 20250811.130322.1 (REFACTORED: The plot layout was redesigned to use a ttk.PanedWindow and individually declared plots to allow for resizable sashes between them.)

current_version = "20250811.130322.1"
current_version_hash = 20250811 * 130322 * 1 + hash(open(__file__, "r").read())

import tkinter as tk
from tkinter import ttk
import inspect
import os
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import logging functions for debugging
from display.debug_logic import debug_log
from display.console_logic import console_log

class ScanMonitorTab(ttk.Frame):
    """
    A Tkinter Frame that provides real-time monitoring of scan data with plots.
    """
    def __init__(self, master=None, app_instance=None, **kwargs):
        # This function description tells me what this function does
        # Initializes the ScanMonitorTab, creating a frame to hold real-time
        # plots of scan data. It sets up Matplotlib figures and canvases for
        # three graphs.
        #
        # Inputs to this function
        #   master (tk.Widget): The parent widget, typically a ttk.Notebook.
        #   app_instance (object): A reference to the main application instance
        #                          to access shared variables and methods.
        #   **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        #
        # Outputs of this function
        #   None. Initializes the Tkinter frame and its internal state.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing ScanMonitorTab. Preparing the plots!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.plots = {} # To store references to the plot canvases by name

        self._create_widgets()

        debug_log(f"ScanMonitorTab initialized. Plots are ready to go!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)


    def _create_widgets(self):
        # This function description tells me what this function does
        # Creates and arranges the widgets for the Scan Monitor tab.
        # It sets up a frame for three Matplotlib graphs.
        #
        # Inputs to this function
        #   None.
        #
        # Outputs of this function
        #   None. Populates the tab with GUI elements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating ScanMonitorTab widgets.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # NEW: Use a PanedWindow to hold the plots with sashes
        plot_paned_window = ttk.PanedWindow(self, orient=tk.VERTICAL)
        plot_paned_window.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # --- Top Plot ---
        top_plot_frame = ttk.Frame(plot_paned_window)
        plot_paned_window.add(top_plot_frame, weight=1)
        top_plot_frame.grid_columnconfigure(0, weight=1)
        top_plot_frame.grid_rowconfigure(0, weight=1)
        figure_top = Figure(figsize=(5, 2.5), dpi=100, facecolor='#1e1e1e')
        ax_top = figure_top.add_subplot(111, facecolor='#1e1e1e')
        ax_top.tick_params(axis='x', colors='white')
        ax_top.tick_params(axis='y', colors='white')
        ax_top.spines['bottom'].set_color('white')
        ax_top.spines['top'].set_color('white')
        ax_top.spines['left'].set_color('white')
        ax_top.spines['right'].set_color('white')
        ax_top.set_title("Live", color='white') # UPDATED: Shorter title
        canvas_top = FigureCanvasTkAgg(figure_top, master=top_plot_frame)
        canvas_widget_top = canvas_top.get_tk_widget()
        canvas_widget_top.grid(row=0, column=0, sticky="nsew")
        self.plots["top"] = {'figure': figure_top, 'ax': ax_top, 'canvas': canvas_top, 'widget': canvas_widget_top}

        # --- Middle Plot ---
        middle_plot_frame = ttk.Frame(plot_paned_window)
        plot_paned_window.add(middle_plot_frame, weight=1)
        middle_plot_frame.grid_columnconfigure(0, weight=1)
        middle_plot_frame.grid_rowconfigure(0, weight=1)
        figure_middle = Figure(figsize=(5, 2.5), dpi=100, facecolor='#1e1e1e')
        ax_middle = figure_middle.add_subplot(111, facecolor='#1e1e1e')
        ax_middle.tick_params(axis='x', colors='white')
        ax_middle.tick_params(axis='y', colors='white')
        ax_middle.spines['bottom'].set_color('white')
        ax_middle.spines['top'].set_color('white')
        ax_middle.spines['left'].set_color('white')
        ax_middle.spines['right'].set_color('white')
        ax_middle.set_title("Max Hold", color='white') # UPDATED: Shorter title
        canvas_middle = FigureCanvasTkAgg(figure_middle, master=middle_plot_frame)
        canvas_widget_middle = canvas_middle.get_tk_widget()
        canvas_widget_middle.grid(row=0, column=0, sticky="nsew")
        self.plots["middle"] = {'figure': figure_middle, 'ax': ax_middle, 'canvas': canvas_middle, 'widget': canvas_widget_middle}

        # --- Bottom Plot ---
        bottom_plot_frame = ttk.Frame(plot_paned_window)
        plot_paned_window.add(bottom_plot_frame, weight=1)
        bottom_plot_frame.grid_columnconfigure(0, weight=1)
        bottom_plot_frame.grid_rowconfigure(0, weight=1)
        figure_bottom = Figure(figsize=(5, 2.5), dpi=100, facecolor='#1e1e1e')
        ax_bottom = figure_bottom.add_subplot(111, facecolor='#1e1e1e')
        ax_bottom.tick_params(axis='x', colors='white')
        ax_bottom.tick_params(axis='y', colors='white')
        ax_bottom.spines['bottom'].set_color('white')
        ax_bottom.spines['top'].set_color('white')
        ax_bottom.spines['left'].set_color('white')
        ax_bottom.spines['right'].set_color('white')
        ax_bottom.set_title("Min Hold", color='white') # UPDATED: Shorter title
        canvas_bottom = FigureCanvasTkAgg(figure_bottom, master=bottom_plot_frame)
        canvas_widget_bottom = canvas_bottom.get_tk_widget()
        canvas_widget_bottom.grid(row=0, column=0, sticky="nsew")
        self.plots["bottom"] = {'figure': figure_bottom, 'ax': ax_bottom, 'canvas': canvas_bottom, 'widget': canvas_widget_bottom}

        debug_log(f"ScanMonitorTab widgets created. The placeholders are ready!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)