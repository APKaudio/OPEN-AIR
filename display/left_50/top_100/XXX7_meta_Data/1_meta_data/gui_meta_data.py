## MQTT_TOPIC_FILTER = "OPEN-AIR/configuration/report"









# display/left_50/top_100/XXX7_meta_Data/1_meta_data/gui_meta_data.py
#
# A GUI frame that uses the DynamicGuiBuilder to create widgets for meta-data settings.
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
import pathlib
import workers.setup.app_constants as app_constants

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
        "version": app_constants.current_version,
        "function": function_full_name
    }

# --- Global Scope Variables ---
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")
JSON_CONFIG_FILE = current_file_path.with_suffix('.json')


class MetaDataGui(ttk.Frame):
    """
    A container frame that instantiates the DynamicGuiBuilder for the Frequency configuration.
    """
    def __init__(self, parent, *args, **kwargs):
        """
        Initializes the Frequency frame and the dynamic GUI builder.
        """
        config_data = kwargs.pop('config', None)
        super().__init__(parent, *args, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)

        # --- Dynamic GUI Builder ---
        current_function_name = "__init__"
        debug_log(
            message=f"🟢️️️🟢 ➡️➡️ {current_function_name} to initialize the MetaDataGui.",
            **_get_log_args()
        )
        try:
            config = {
                ## "base_topic": MQTT_TOPIC_FILTER,
                "log_to_gui_console": None, 
                "log_to_gui_treeview": None  # Assuming no treeview for this component
            }

            self.dynamic_gui = DynamicGuiBuilder(
                parent=self,
                json_path=JSON_CONFIG_FILE,
                config=config
            )
            
        except Exception as e:
            debug_log(message=f"❌ Error in {current_function_name}: {e}",
                        **_get_log_args()
                        )
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                **_get_log_args()
            )