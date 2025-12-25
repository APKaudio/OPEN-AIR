# display/right_50/bottom_90/tab_1_scan/gui_tab_1_scan.py
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
# Version 20251222.004800.1

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
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
from workers.mqtt.setup.config_reader import app_constants

# --- Global Scope Variables ---
Current_Date = 20251222
Current_Time = 4800
Current_iteration = 1

current_version = "20251222.004800.1"
current_version_hash = (Current_Date * Current_Time * Current_iteration)
current_file = os.path.basename(__file__)

class ScanViewGUIFrame(ttk.Frame):
    
    def __init__(self, parent, config=None, *args, **kwargs):
        """
        Initializes the Scan View GUI with a Seaborn/Matplotlib plot.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        # Log entry
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🖥️🟢 Initializing {self.__class__.__name__}. Preparing to scan the ether!",
              **_get_log_args()
            )
        try:
            super().__init__(parent, *args, **kwargs)
            
            # The parent will use .pack() or .grid() on this frame.
            # This frame will use .grid() for its own children.
            
            # Configure grid for expansion: Row 0 is canvas (weight 1), Row 1 is toolbar (weight 0)
            self.grid_rowconfigure(0, weight=1) 
            self.grid_rowconfigure(1, weight=0)
            self.grid_columnconfigure(0, weight=1)
            
            # FIX: Ensure config is not None before calling .get()
            safe_config = config if config is not None else {}
            
            # Use theme from parent if available, otherwise fallback
            self.theme_colors = safe_config.get("theme_colors", {
                "bg": "#2b2b2b", "fg": "#dcdcdc", "fg_alt": "#888888", "accent": "#f4902c"
            })

            self._create_plot_widgets()
            
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"✅ Celebration of success! {self.__class__.__name__} initialized.",**_get_log_args()

                )

        except Exception as e:
            debug_log(
                message=f"❌ Error in {current_function_name}: {e}",
             **_get_log_args()
            )
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"❌🔴 Arrr, the code be capsized! Error in {current_function_name}: {e}",
**_get_log_args()
                )

    def _create_plot_widgets(self):
        """
        Generates the Matplotlib figure and embeds it in the Tkinter frame.
        """
        current_function_name = "_create_plot_widgets"
        
        try:
            # --- 0. Set Seaborn Style ---
            # Note: This sets the global Seaborn style. 
            sns.set_theme(style="darkgrid", palette="deep") 
            
            # --- 1. Create Matplotlib Figure and Axes ---
            self.fig = Figure(figsize=(8, 6), dpi=100, facecolor=self.theme_colors["bg"])
            self.ax = self.fig.add_subplot(111, facecolor=self.theme_colors["bg"])
            
            # --- Placeholder Plot: A Simple Sine Wave using Seaborn ---
            t = np.arange(0.0, 2.0, 0.01)
            s = 1 + np.sin(2 * np.pi * t)
            
            # Use Seaborn's lineplot, passing the Matplotlib axes object (ax)
            sns.lineplot(x=t, y=s, ax=self.ax, color=self.theme_colors["accent"], linewidth=2) 
            
            # --- Configure Axes ---
            self.ax.set_title("Live Scan View", color=self.theme_colors["fg"])
            self.ax.set_xlabel("Frequency (MHz)", color=self.theme_colors["fg"])
            self.ax.set_ylabel("Amplitude (dBm)", color=self.theme_colors["fg"])
            self.ax.tick_params(axis='x', colors=self.theme_colors["fg"])
            self.ax.tick_params(axis='y', colors=self.theme_colors["fg"])
            self.ax.grid(True, linestyle='--', color=self.theme_colors["fg_alt"], alpha=0.5)

            # --- 2. Create Tkinter canvas and grid it ---
            self.canvas = FigureCanvasTkAgg(self.fig, master=self)
            self.canvas_widget = self.canvas.get_tk_widget()
            self.canvas_widget.grid(row=0, column=0, sticky="nsew")

            # --- 3. Add Toolbar Frame (Master for Toolbar) ---
            self.toolbar_frame = ttk.Frame(self)
            self.toolbar_frame.grid(row=1, column=0, sticky="ew")
            
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
            self.toolbar.update()
            self.toolbar.pack(side="top", fill="x")

            self.canvas.draw()
            
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message="📊 Plot widgets created and rendered successfully.",
**_get_log_args()
                )

        except Exception as e:
            debug_log(message=f"❌ Error in {current_function_name}: {e}")
            raise e # Re-raise to be caught by __init__