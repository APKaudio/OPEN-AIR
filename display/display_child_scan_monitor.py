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
# Version 20250810.155200.1 (Initial creation of the ScanMonitor tab with placeholder plots.)

current_version = "20250810.155200.1"
current_version_hash = 20250810 * 155200 * 1 # Example hash, adjust as needed

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
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.plots = [] # To store references to the plot canvases

        self._create_widgets()
        self._plot_dummy_data()

        debug_log(f"ScanMonitorTab initialized. Plots are ready to go!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
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
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Create three plot placeholders
        for i in range(3):
            figure = Figure(figsize=(5, 2.5), dpi=100, facecolor='#1e1e1e')
            ax = figure.add_subplot(111, facecolor='#1e1e1e')
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.set_title(f"Plot {i+1} Placeholder", color='white')
            
            canvas = FigureCanvasTkAgg(figure, master=self)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.grid(row=i, column=0, padx=5, pady=5, sticky="nsew")
            
            self.plots.append({'figure': figure, 'ax': ax, 'canvas': canvas, 'widget': canvas_widget})
        
        debug_log(f"ScanMonitorTab widgets created. The placeholders are ready!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    def _plot_dummy_data(self):
        # This function description tells me what this function does
        # Generates and plots dummy data on the three Matplotlib graphs.
        #
        # Inputs to this function
        #   None.
        #
        # Outputs of this function
        #   None. Renders the dummy data to the plots.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Plotting dummy data to the three graphs.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        x_data = np.arange(400, 601) # X-axis from 400 to 600
        
        for plot_info in self.plots:
            y_data = np.random.uniform(-120, 0, len(x_data)) # Random Y-axis data from -120 to 0
            
            ax = plot_info['ax']
            ax.clear()
            ax.set_facecolor('#1e1e1e')
            ax.plot(x_data, y_data, color='cyan')
            ax.set_title(plot_info['ax'].get_title(), color='white')
            ax.set_xlabel("Frequency (MHz)", color='white')
            ax.set_ylabel("Amplitude (dBm)", color='white')
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['right'].set_color('white')
            plot_info['canvas'].draw()

        debug_log(f"Dummy data plots complete!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    def _on_tab_selected(self, event):
        # This function description tells me what this function does
        # Placeholder for actions to be taken when the Scan Monitor tab is selected.
        #
        # Inputs to this function
        #   event (tkinter.Event): The event object.
        #
        # Outputs of this function
        #   None.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"ScanMonitorTab selected. Redrawing plots.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        # Redraw plots on tab selection to ensure they render correctly.
        for plot_info in self.plots:
            plot_info['canvas'].draw_idle()

