# display/left_50/top_100/tab_1_instrument/sub_tab_4_YAK/sub_tab_9_System/gui_yak_system.py
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251129  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 1 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


# A GUI frame that uses the DynamicGuiBuilder to create widgets for the YAK System settings.
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
current_version = "20251127.000000.1"
current_version_hash = (20251127 * 0 * 1)
current_file = f"{os.path.basename(__file__)}"
MQTT_TOPIC_FILTER = "OPEN-AIR/yak/System"


class YakSystemGui(ttk.Frame):
    """
    A container frame that instantiates the DynamicGuiBuilder for the YAK System configuration.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        """
        Initializes the YAK System frame and the dynamic GUI builder.
        """
        if 'config' in kwargs:
            kwargs.pop('config')
        super().__init__(parent, *args, **kwargs)

        # --- Dynamic GUI Builder ---
        current_function_name = "__init__"
        debug_log(
            message=f"🛠️🟢 Entering {current_function_name} to initialize the YakSystemGui.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            config = {
                "base_topic": MQTT_TOPIC_FILTER,
                "log_to_gui_console": console_log,
                "log_to_gui_treeview": None  # Assuming no treeview for this component
            }

            self.dynamic_gui = DynamicGuiBuilder(
                parent=self,
                mqtt_util=mqtt_util,
                config=config
            )
            console_log("✅ Celebration of success! The YakSystemGui did initialize its dynamic GUI builder.")
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )