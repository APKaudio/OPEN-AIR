# display/right_50/bottom_90/1_scan/gui_scan.py
#
# This file defines the GUI frame for the scan view, featuring a Matplotlib/Seaborn plot.
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
# Version 20251229.1625.1

import tkinter as tk
from tkinter import ttk
import numpy as np
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pathlib
import os
import inspect

# --- Module Imports ---
from workers.logger.logger import  debug_logger
from workers.logger.log_utils import _get_log_args 
from workers.setup.config_reader import Config # Import the Config class

# Globals
app_constants = Config.get_instance() # Get the singleton instance
current_version = "20251229.1625.1"
current_version_hash = 32806990925 # 20251229 * 1625 * 1

class ScanViewGUIFrame(ttk.Frame):
    """
    A GUI frame that displays a live spectrum scan using Matplotlib.
    """
    def __init__(self, parent, json_path=None, config=None, **kwargs):
        """
        Initialize the Scan View GUI.

        Args:
            parent: The parent widget.
            json_path (str, optional): Path to config file (caught to prevent error).
            config (dict, optional): Configuration dictionary (caught to prevent error).
            **kwargs: Additional keyword arguments for the frame.
        """
        # 1. Initialize Parent Frame (Cleanly!)
        super().__init__(parent, **kwargs)
        
        # 2. Store Arguments (Safe from superclass!)
        self.json_path = json_path
        self.config_data = config
        
        # 3. Setup Theme
        self.theme_colors = {
            "bg": "black",
            "fg": "white",
            "fg_alt": "gray"
        }
        if self.config_data and 'theme_colors' in self.config_data:
             self.theme_colors.update(self.config_data['theme_colors'])

        # 4. Initialize UI
        self._init_ui()

    def _init_ui(self):
        current_function_name = inspect.currentframe().f_code.co_name
        
        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"🧪 Great Scott! Initializing '{current_function_name}' for the Live Scan View!",
                **_get_log_args()
            )

        try:
            # --- 1. Create Matplotlib Figure ---
            # Set figure background to match theme
            self.fig = Figure(figsize=(5, 4), dpi=100, facecolor=self.theme_colors["bg"])
            self.ax = self.fig.add_subplot(111)
            
            # Style the plot area
            self.ax.set_facecolor(self.theme_colors["bg"])
            self.ax.spines['bottom'].set_color(self.theme_colors["fg"])
            self.ax.spines['top'].set_color(self.theme_colors["fg"])
            self.ax.spines['left'].set_color(self.theme_colors["fg"])
            self.ax.spines['right'].set_color(self.theme_colors["fg"])
            self.ax.tick_params(axis='x', colors=self.theme_colors["fg"])
            self.ax.tick_params(axis='y', colors=self.theme_colors["fg"])
            self.ax.yaxis.label.set_color(self.theme_colors["fg"])
            self.ax.xaxis.label.set_color(self.theme_colors["fg"])
            self.ax.title.set_color(self.theme_colors["fg"])

            # Dummy Data for Initial View
            x = np.linspace(0, 10, 100)
            y = np.sin(x)
            self.ax.plot(x, y, color='cyan') # Sci-Fi Cyan

            self.ax.set_title("Live Scan View", color=self.theme_colors["fg"])
            self.ax.set_xlabel("Frequency (MHz)", color=self.theme_colors["fg"])
            self.ax.set_ylabel("Amplitude (dBm)", color=self.theme_colors["fg"])
            self.ax.grid(True, linestyle='--', color=self.theme_colors["fg_alt"], alpha=0.5)

            # --- 2. Create Tkinter canvas and grid it ---
            self.canvas = FigureCanvasTkAgg(self.fig, master=self)
            self.canvas_widget = self.canvas.get_tk_widget()
            self.canvas_widget.pack(side="top", fill="both", expand=True)

            # --- 3. Add Toolbar Frame (Optional) ---
            # Note: Toolbar usually needs a dedicated pack/grid. 
            # For now, sticking to simple packing to ensure stability.
            
            self.canvas.draw()
            
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message="✅ It works! The Matplotlib canvas has materialized!",
                    **_get_log_args()
                )

        except Exception as e:
            if app_constants.global_settings['debug_enabled']:
                 debug_logger(
                    message=f"❌ ERROR! The Scan View collapsed! Exception: {e}",
                    **_get_log_args()
                )
            # Display Error on GUI
            tk.Label(self, text=f"Plot Error: {e}", fg="red", bg="black").pack()