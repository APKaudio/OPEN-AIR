# display/builder/dynamic_gui_create_value_box.py
#
# A mixin class for the DynamicGuiBuilder that handles the creation of an editable text box.
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
from workers.active.worker_active_logging import debug_log, console_log

# --- Global Scope Variables ---
current_version = "20251127.000000.1"
current_version_hash = (20251127 * 0 * 1)
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2

class ValueBoxCreatorMixin:
    """
    A mixin class that provides the functionality for creating an
    editable text box widget.
    """
    def _create_value_box(self, parent_frame, label, config, path):
        # Creates an editable text box (_Value).
        current_function_name = inspect.currentframe().f_code.co_name

        debug_log(
            message=f"🛠️🟢 Entering '{current_function_name}' to conjure an entry box for '{label}'.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            sub_frame = ttk.Frame(parent_frame)
            sub_frame.pack(side=tk.LEFT, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

            label_widget = ttk.Label(sub_frame, text=f"{label}:")
            label_widget.pack(side=tk.LEFT, padx=(DEFAULT_PAD_X, DEFAULT_PAD_X))

            entry_value = tk.StringVar(value=config.get('value', ''))
            entry = ttk.Entry(sub_frame, textvariable=entry_value, style="Custom.TEntry")
            entry.pack(side=tk.LEFT, padx=DEFAULT_PAD_X)

            if config.get('units'):
                units_label = ttk.Label(sub_frame, text=config['units'])
                units_label.pack(side=tk.LEFT, padx=(0, DEFAULT_PAD_X))

            def on_entry_change(event):
                new_val = entry_value.get()
                debug_log(
                    message=f"GUI ACTION: Publishing to '{path}' with value '{new_val}'",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
                # CORRECTED: This now correctly uses the central transmit method.
                self._transmit_command(relative_topic=path, payload=new_val)

            entry.bind("<FocusOut>", on_entry_change)
            entry.bind("<Return>", on_entry_change)

            # Store the widget using its full topic path as the key.
            if path:
                self.topic_widgets[path] = entry

            console_log(f"✅ Celebration of success! The value box did appear.")
            return sub_frame

        except Exception as e:
            console_log(f"❌ Error in {current_function_name} for '{label}': {e}")
            debug_log(
                message=f"🛠️🔴 Arrr, the code be capsized! The value box creation has failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            return None