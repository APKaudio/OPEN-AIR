# display/builder/dynamic_gui_create_label.py
#
# A mixin class for the DynamicGuiBuilder that handles the creation of a label widget.
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

import tkinter as tk

from tkinter import ttk

import inspect



# --- Module Imports ---

from display.logger import debug_log, console_log, log_visa_command





Local_Debug_Enable = True
current_version = "20251127.000000.1"
current_version_hash = (20251127 * 0 * 1)
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
# These are local to this module but should match the main builder's constants.
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2

class LabelCreatorMixin:
    """
    A mixin class that provides the functionality for creating a label widget.
    """
    def _create_label(self, parent_frame, label, value, units=None, path=None):
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🟢 Entering '{current_function_name}' to create a label: '{label}' with value '{value}'.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            sub_frame = ttk.Frame(parent_frame)
            sub_frame.pack(padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y, anchor='w')

            label_text = f"{label}: {value}"
            if units:
                label_text += f" {units}"

            label_widget = ttk.Label(sub_frame, text=label_text)
            label_widget.pack(side=tk.LEFT, padx=(DEFAULT_PAD_X, DEFAULT_PAD_X))

            # Store the widget using its full topic path as the key for live updates.
            if path:
                self.topic_widgets[path] = label_widget
            
            debug_log(
                message=f"🛠️🟢 Exiting '{current_function_name}'. Label '{label}' created.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            return label_widget, sub_frame

        except Exception as e:
            console_log(f"❌ Error in {current_function_name} for '{label}': {e}")
            debug_log(
                message=f"🛠️🔴 Arrr, the code be capsized! Label creation has failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            return None, None