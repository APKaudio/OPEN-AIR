# display/base_gui_component.py
#
# A base class for common GUI components, re-written to work with the centralized orchestrator.
# This version replaces the buttons and MQTT functionality with a Matplotlib plot display.
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
# Version 20250823.195100.23

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import pathlib
import sys
import json
import paho.mqtt.client as mqtt
import pandas as pd
import numpy as np

# --- FIX: Added matplotlib imports for plotting functionality ---
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# --- Module Imports ---
from workers.worker_active_logging import debug_log, console_log
from display.styling.style import THEMES, DEFAULT_THEME
from workers.worker_mqtt_controller_util import MqttControllerUtility

# --- Global Scope Variables ---
# W: The date of the chat session in YYYYMMDD format.
CURRENT_DATE = 20250823
# X: The time of the chat session in HHMMSS format.
CURRENT_TIME = 195100
# Y: The revision number within the current session, starting at 1 and incrementing with each subsequent version.
REVISION_NUMBER = 23

current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
# Dynamically get the file path relative to the project root
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME * REVISION_NUMBER)
current_function_name = ""

class BaseGUIFrame(ttk.Frame):
    """
    A reusable base class for GUI frames now focused on displaying a Matplotlib plot.
    """
    def __init__(self, parent, mqtt_util=None, *args, **kwargs):
        """
        Initializes the GUI frame with a plot.
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
            self.pack(fill=tk.BOTH, expand=True)

            # We now accept an optional MQTT utility instance.
            self.mqtt_util = mqtt_util

            self._create_widgets()

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
        
    def _create_widgets(self):
        """
        Creates and arranges the widgets for the frame, including the plot.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🖥️🟢 Creating BaseGUIFrame widgets.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
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
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}",
                        console_print_func=console_log)

            console_log("✅ Celebration of success! All widgets have been created.")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Base Component Test with Plot")
    
    # Placeholder for the missing MQTT utility instance
    class MockMqttUtility:
        def __init__(self, **kwargs): pass
        def connect_mqtt(self): pass
        def disconnect_mqtt(self): pass
        def publish_message(self, **kwargs): pass

    mqtt_utility = MockMqttUtility()

    app_frame = BaseGUIFrame(parent=root, mqtt_util=mqtt_utility)
    
    root.mainloop()
