# display/right_50/bottom_90/tab_1_scan/gui_tab_1_scan.py
#
# This file defines the GUI frame for the scan view, featuring a Matplotlib/Seaborn plot.
#
# Author: Anthony Peter Kuzub
#
# Version 20251127.000000.1

import tkinter as tk
from tkinter import ttk
import numpy as np
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from display.logger import debug_log, console_log, log_visa_command
import pathlib
import os

current_version = "UNKNOWN_VERSION.000000.0"
current_version_hash = 0
current_file_path = pathlib.Path(__file__).resolve()
project_root = pathlib.Path("/home/anthony/Documents/OPEN-AIR").resolve()
current_file = str(current_file_path.relative_to(project_root)).replace("\\\\", "/")

class ScanViewGUIFrame(ttk.Frame):
    
    def __init__(self, parent, mqtt_util=None, config=None):
        super().__init__(parent)
        
        # The parent will use .pack() or .grid() on this frame.
        # This frame will use .grid() for its own children.
        
        # Configure grid for expansion: Row 0 is canvas (weight 1), Row 1 is toolbar (weight 0)
        self.grid_rowconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)
        
        # Use theme from parent if available, otherwise fallback
        self.theme_colors = config.get("theme_colors", {
            "bg": "#2b2b2b", "fg": "#dcdcdc", "fg_alt": "#888888", "accent": "#f4902c"
        })

        self._create_plot_widgets()
        console_log("✅ Scan View Plot Frame Initialized.")

    def _create_plot_widgets(self):
        # --- 0. Set Seaborn Style ---
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
        console_log("✅ Plot successfully rendered in Scan View.")