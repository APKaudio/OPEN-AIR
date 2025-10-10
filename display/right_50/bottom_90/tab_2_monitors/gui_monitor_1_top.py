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
# Version 20250823.001500.21

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
from workers.worker_active_logging import debug_log, console_log
from display.styling.style import THEMES, DEFAULT_THEME
from workers.worker_mqtt_controller_util import MqttControllerUtility
# --- Global Scope Variables ---
# W: The date of the chat session in YYYYMMDD format.
CURRENT_DATE = 20250823
# X: The time of the chat session in HHMMSS format.
CURRENT_TIME = 1500
# Y: The revision number within the current session, starting at 1 and incrementing with each subsequent version.
REVISION_NUMBER = 21

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

            # We apply the style at the top of the __init__ to affect all child widgets.
            self._apply_styles(theme_name=DEFAULT_THEME)

            # Create a label for the frame
            frame_label = ttk.Label(self, text=f"Application Frame: {self.__class__.__name__}", font=("Arial", 16))
            frame_label.pack(pady=10)
            
            # --- Single Plot Frame ---
            plot_frame = ttk.Frame(self)
            plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            plot_frame.grid_columnconfigure(0, weight=1)
            plot_frame.grid_rowconfigure(0, weight=1)

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
            canvas_widget.pack(fill=tk.BOTH, expand=True)
            
            # Optionally, add a toolbar for user interaction
            toolbar = NavigationToolbar2Tk(canvas, plot_frame)
            toolbar.update()
            
            self.plot = {'figure': figure, 'ax': ax, 'canvas': canvas, 'widget': canvas_widget}

            console_log("✅ Celebration of success!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=self.current_file,
                version=self.current_version,
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
