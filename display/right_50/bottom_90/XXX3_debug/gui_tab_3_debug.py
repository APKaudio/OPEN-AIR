# display/right_50/bottom_90/tab_3_debug/gui_tab_3_debug.py
#
# A DEBUG tab component inheriting from the formal BaseGUIFrame.
# It provides logging controls and an MQTT table view for inspection.
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
# MODIFIED: Inherits from the centralized BaseGUIFrame and uses clean attribute referencing.

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import pathlib
import sys
import json

# --- Module Imports ---
from workers.logger.logger import debug_log
from display.styling.style import THEMES, DEFAULT_THEME


# --- Global Scope Variables (Protocol 4.4) ---
current_version = "20251127.000000.1"
current_version_hash = (20251127 * 0 * 1)
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parents[4] 
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")


class DebugTabGUIFrame(ttk.Frame):
    """
    A debug frame with logging and MQTT monitoring functionality.
    """
    def __init__(self, parent, *args, **kwargs):
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        
        if 'config' in kwargs:
            kwargs.pop('config')
        super().__init__(parent, *args, **kwargs)

        debug_log(
            message="🖥️🟢 Initializing the dedicated Debug Tab GUI. Time for deep inspection!",
            file=current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}"
            


        )
        
        debug_log(message="✅ Debug Tab GUI initialized successfully!")
