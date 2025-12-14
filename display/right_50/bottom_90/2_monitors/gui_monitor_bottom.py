# gui_monitor_1_top_blank_graph.py 
#
# A base class for common GUI components, re-written to work with the centralized orchestrator.
# This version is simplified to only display a blank Matplotlib plot.
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
#
# Version 20251026.220340.3 (Blank Graph)
# MODIFIED: Removed all plot-specific colors, titles, and axis styling to create a blank graph.

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import pathlib
import sys
import json

# --- Matplotlib imports for plotting functionality ---
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# --- Module Imports ---
from display.logger import debug_log, console_log, log_visa_command
from display.styling.style import THEMES, DEFAULT_THEME

# --- Global Scope Variables ---
CURRENT_DATE = 20250823
CURRENT_TIME = 1500
REVISION_NUMBER = 21

current_version = "20251026.220340.3" # Updated version number
# Dynamically get the file path relative to the project root
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME * REVISION_NUMBER)
current_function_name = ""


class MonitorTopGUIFrame(ttk.Frame):
    """
    A reusable base class for GUI frames now focused on displaying a Matplotlib plot.
    """
    PLOT_ID = "top" 
    
    def __init__(self, parent, mqtt_util=None, config=None, *args, **kwargs):
        """
        Initializes the GUI frame with a blank plot.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🖥️🟢 Initializing a new GUI frame from the base class. The blueprint is in hand!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            # --- Function logic goes here ---
            super().__init__(parent, *args, **kwargs)

            self._apply_styles(theme_name=DEFAULT_THEME)

            # --- Single Plot Frame ---
            plot_frame = ttk.Frame(self)
            plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            plot_frame.grid_columnconfigure(0, weight=1)
            plot_frame.grid_rowconfigure(0, weight=1)

            # This section creates the matplotlib figure and canvas.
            # RETAINED: Figure creation, but removed all color styling for a blank look.
            self.theme_colors = config.get("theme_colors", {
                "bg": "#2b2b2b", "fg": "#dcdcdc", "fg_alt": "#888888", "accent": "#f4902c"
            })
            figure = Figure(figsize=(8, 6), dpi=100, facecolor=self.theme_colors["bg"])
            ax = figure.add_subplot(111, facecolor=self.theme_colors["bg"])
            ax.set_title("Bottom Monitor", color=self.theme_colors["fg"])
            ax.set_xlabel("Frequency (MHz)", color=self.theme_colors["fg"])
            ax.set_ylabel("Amplitude (dBm)", color=self.theme_colors["fg"])
            ax.tick_params(axis='x', colors=self.theme_colors["fg"])
            ax.tick_params(axis='y', colors=self.theme_colors["fg"])
            ax.grid(True, linestyle='--', color=self.theme_colors["fg_alt"], alpha=0.5)
            
            canvas = FigureCanvasTkAgg(figure, master=plot_frame)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True)
            
            self.plot = {'figure': figure, 'ax': ax, 'canvas': canvas, 'widget': canvas_widget}

            console_log("✅ Celebration of success!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _apply_styles(self, theme_name: str):
        """
        Applies the specified theme to the GUI elements using ttk.Style.
        """
        colors = THEMES.get(theme_name, THEMES["dark"])
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # General widget styling
        style.configure('TFrame', background=colors["bg"])
        style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
        style.configure('TLabelframe', background=colors["bg"], foreground=colors["fg"])

        # Table (Treeview) styling
        style.configure('Custom.Treeview',
                        background=colors["table_bg"],
                        foreground=colors["table_fg"],
                        fieldbackground=colors["table_bg"],
                        bordercolor=colors["table_border"],
                        borderwidth=colors["border_width"])

        style.configure('Custom.Treeview.Heading',
                        background=colors["table_heading_bg"],
                        foreground=colors["fg"],
                        relief=colors["relief"],
                        borderwidth=colors["border_width"])

        # Entry (textbox) styling
        style.configure('Custom.TEntry',
                        fieldbackground=colors["entry_bg"],
                        foreground=colors["entry_fg"],
                        bordercolor=colors["table_border"])
        

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Base Component Test with Blank Plot")
    
    app_frame = MonitorTopGUIFrame(parent=root)
    
    root.mainloop()