# display/display_child_scan_view.py
#
# This file defines the ScanViewTab, a Tkinter Frame for displaying a live, single-pane plot of scan data.
# It is designed to be added as a separate tab to the main display pane, focusing on a single trace.
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
# Version 20250819.004000.1 (NEW: Initial version of the ScanViewTab with a single plot.)

current_version = "20250819.004000.1"
current_version_hash = 20250819 * 4000 * 1

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

class ScanViewTab(ttk.Frame):
    """
    A Tkinter Frame that provides a single, large plot for viewing scan data.
    """
    def __init__(self, master=None, app_instance=None, **kwargs):
        """
        Initializes the ScanViewTab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing ScanViewTab. Preparing the single plot!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.plot = {} # To store references to the plot canvas

        self._create_widgets()

        debug_log(f"ScanViewTab initialized. Plot is ready to go!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)


    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Scan View tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating ScanViewTab widgets.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Single Plot Frame ---
        plot_frame = ttk.Frame(self)
        plot_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        plot_frame.grid_columnconfigure(0, weight=1)
        plot_frame.grid_rowconfigure(0, weight=1)
        figure = Figure(figsize=(8, 6), dpi=100, facecolor='#1e1e1e')
        ax = figure.add_subplot(111, facecolor='#1e1e1e')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.set_title("Live Trace", color='white')
        canvas = FigureCanvasTkAgg(figure, master=plot_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew")
        self.plot = {'figure': figure, 'ax': ax, 'canvas': canvas, 'widget': canvas_widget}

        debug_log(f"ScanViewTab widgets created. The placeholder is ready!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
