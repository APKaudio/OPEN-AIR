# display_gui_child_pusher.py

#
# A GUI frame that uses the DynamicGuiBuilder to create widgets for frequency settings.
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
# Version 20251127.000000.1

import os
import inspect
import tkinter as tk
from tkinter import ttk

# --- Module Imports ---
from workers.builder.dynamic_gui_builder import DynamicGuiBuilder
from display.logger import debug_log, console_log, log_visa_command
import pathlib

# --- Global Scope Variables ---
current_version = "20251213.000000.1" # Updated version based on current date
current_version_hash = (20251213 * 0 * 1) # Updated hash
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\\\", "/")


class StartPauseStopGui(ttk.Frame):
    """
    A GUI component for Start/Pause/Stop functionality, instantiating DynamicGuiBuilder.
    """
    def __init__(self, parent, *args, **kwargs):
        """
        Initializes the Frequency frame and the dynamic GUI builder.
        """
        if 'config' in kwargs:
            kwargs.pop('config')
        super().__init__(parent, *args, **kwargs)

        # --- Dynamic GUI Builder ---
        current_function_name = "__init__"
        debug_log(
            message=f"🛠️🟢 Entering {current_function_name} to initialize the StartPauseStopGui.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            self.dynamic_gui = DynamicGuiBuilder(
                parent=self
            )
            console_log("✅ Celebration of success! The StartPauseStopGui did initialize its dynamic GUI builder.")
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )