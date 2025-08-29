# display/builder/dynamic_gui_create_gui_actuator.py
#
# A mixin class for the DynamicGuiBuilder that handles creating a simple actuator button.
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
# Version 20250828.215819.7

import os
import tkinter as tk
from tkinter import ttk
import inspect

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log

# --- Global Scope Variables ---
current_version = "20250828.215819.7"
current_version_hash = (20250828 * 215819 * 7)
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2

class GuiActuatorCreatorMixin:
    """
    A mixin class that provides the functionality for creating a simple
    actuator button widget that triggers an action via MQTT.
    """
    def _create_gui_actuator(self, parent_frame, label, config, path):
        # Creates a button that acts as a simple actuator.
        current_function_name = inspect.currentframe().f_code.co_name

        debug_log(
            message=f"🛠️🟢 Entering {current_function_name} to conjure an actuator button for '{label}'.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # Create a frame to hold the label and button
            sub_frame = ttk.Frame(parent_frame)
            sub_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

            # Create the button. The label comes from the config, and the command is a simple publish action.
            button_text = config.get('label', label)

            button = ttk.Button(
                sub_frame,
                text=button_text,
                style='TButton' # Start with the default inactive style
            )
            button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=DEFAULT_PAD_X)

            def on_press(event):
                # Change style to 'Selected.TButton' on press and publish 'true'
                button.configure(style='Selected.TButton')
                debug_log(
                    message=f"GUI ACTION: Publishing actuator command to '{path}' with value 'true'",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
                self._transmit_command(relative_topic=path, payload='true')

            def on_release(event):
                # Revert style to 'TButton' on release and publish '0'
                button.configure(style='TButton')
                debug_log(
                    message=f"GUI ACTION: Publishing actuator command to '{path}' with value '0'",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
                self._transmit_command(relative_topic=path, payload='0')

            button.bind("<ButtonPress-1>", on_press)
            button.bind("<ButtonRelease-1>", on_release)

            # Store the button widget for potential future updates
            if path:
                self.topic_widgets[path] = button

            console_log(f"✅ Celebration of success! The actuator button '{label}' did appear.")
            return sub_frame

        except Exception as e:
            console_log(f"❌ Error in {current_function_name} for '{label}': {e}")
            debug_log(
                message=f"🛠️🔴 Arrr, the code be capsized! The actuator button creation has failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=current_function_name,
                console_print_func=console_log
            )
            return None