# display/base_gui_component.py
#
# A base class for common GUI components, re-written to work with the centralized orchestrator.
# This version corrects the styling of tables and entry widgets for a more cohesive look.
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
# Version 20250823.001500.20

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import pathlib
import sys
import json
import paho.mqtt.client as mqtt

# --- FIX: Added matplotlib imports for plotting functionality ---
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# --- Module Imports ---
# NOTE: These are placeholders as the original source was not provided,
#       but they are included to match the original code's structure.
# from datasets.logging import debug_log, console_log
# from workers.mqtt_controller_util import MqttControllerUtility
# from display.styling.style import THEMES, DEFAULT_THEME

# --- Placeholder definitions for missing modules to make the code runnable ---
def debug_log(message, file="", version="", function=""):
    print(f"[DEBUG] {message}")
def console_log(message):
    print(f"[CONSOLE] {message}")
class MqttControllerUtility:
    def __init__(self, *args, **kwargs):
        pass
class AppInstance:
    def __init__(self):
        self.bind = lambda a, b: None

# --- Global Scope Variables ---
CURRENT_DATE = 20250823
CURRENT_TIME = 1500
CURRENT_TIME_HASH = 1500
REVISION_NUMBER = 20
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME_HASH * REVISION_NUMBER)
# Dynamically get the file path relative to the project root
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")


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

        # FIX: The original code used variables that were not imported.
        # This section creates the matplotlib figure and canvas.
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
        
        # Optionally, add a toolbar for user interaction
        toolbar = NavigationToolbar2Tk(canvas, plot_frame)
        toolbar.update()
        toolbar.grid(row=1, column=0, sticky="ew")
        
        self.plot = {'figure': figure, 'ax': ax, 'canvas': canvas, 'widget': canvas_widget}

        debug_log(f"ScanViewTab widgets created. The placeholder is ready!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Base Component Test")
    
    # We now must manually create and pass the MQTT utility instance for the standalone test.
    mqtt_utility = MqttControllerUtility(print_to_gui_func=console_log, log_treeview_func=lambda *args: None)
    mqtt_utility.connect_mqtt()

    app_frame = ScanViewTab(parent=root, mqtt_util=mqtt_utility)
    
    root.mainloop()


