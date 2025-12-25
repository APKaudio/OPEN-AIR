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
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
import pathlib
from workers.mqtt.setup.config_reader import app_constants

def _get_log_args():
    """Helper to get common debug_log arguments, accounting for class methods."""
    frame = inspect.currentframe().f_back.f_back
    filename = os.path.basename(frame.f_code.co_filename)
    func_name = frame.f_code.co_name

    # Attempt to get the class name if called from a method
    class_name = None
    if 'self' in frame.f_locals:
        class_name = frame.f_locals['self'].__class__.__name__
    elif 'cls' in frame.f_locals:
        class_name = frame.f_locals['cls'].__name__

    if class_name:
        function_full_name = f"{class_name}.{func_name}"
    else:
        function_full_name = func_name

    return {
        "file": filename,
        "version": app_constants.CURRENT_VERSION,
        "function": function_full_name
    }

# --- Global Scope Variables ---
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")
JSON_CONFIG_FILE = current_file_path.with_suffix('.json')


class StartPauseStopGui(ttk.Frame):
    """
    A GUI component for Start/Pause/Stop functionality, instantiating DynamicGuiBuilder.
    """
    def __init__(self, parent, config, *args, **kwargs):
        """
        Initializes the Frequency frame and the dynamic GUI builder.
        """
        super().__init__(parent, *args, **kwargs)
        self.config_data = config
        
        # --- Dynamic GUI Builder ---
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🟢️️️🟢 ➡️➡️ {current_function_name} to initialize the StartPauseStopGui.",
                **_get_log_args()
            )
        try:
            self.dynamic_gui = DynamicGuiBuilder(
                parent=self,
                json_path=JSON_CONFIG_FILE,
                config=self.config_data
            )
            debug_log(
                message="✅ The StartPauseStopGui did initialize its dynamic GUI builder.",
                **_get_log_args()
            )
        except Exception as e:
            debug_log(
                message=f"❌ Error in {current_function_name}: {e}",
                **_get_log_args()
            )
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                    **_get_log_args()
                )
