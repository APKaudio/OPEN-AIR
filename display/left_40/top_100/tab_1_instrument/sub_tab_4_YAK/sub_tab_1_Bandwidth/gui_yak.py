MQTT_TOPIC_FILTER = "OPEN-AIR/repository/yak/Bandwidth"








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
# Version 20250827.194600.1

import os
import inspect
import tkinter as tk
from tkinter import ttk

# --- Module Imports ---
from display.builder.dynamic_gui_builder import DynamicGuiBuilder
from workers.worker_logging import debug_log, console_log

# --- Global Scope Variables ---
current_version = "20250827.194600.1"
current_version_hash = (20250827 * 194600 * 1)
current_file = f"{os.path.basename(__file__)}"


class PresetPusherGui(ttk.Frame):
    """
    A container frame that instantiates the DynamicGuiBuilder for the Frequency configuration.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        """
        Initializes the Frequency frame and the dynamic GUI builder.
        """
        super().__init__(parent, *args, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)

        # --- Dynamic GUI Builder ---
        current_function_name = "__init__"
        debug_log(
            message=f"🛠️🟢 Entering {current_function_name} to initialize the PresetPusherGui.",
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
            console_log("✅ Celebration of success! The PresetPusherGui did initialize its dynamic GUI builder.")
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )