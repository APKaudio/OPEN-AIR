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
# Version 20250827.152935.16

import os
import tkinter as tk
from tkinter import ttk

# --- Module Imports ---
from workers.worker_logging import console_log

# --- Global Scope Variables ---
current_version = "20250827.152935.16"
current_version_hash = (20250827 * 152935 * 16)
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
        try:
            sub_frame = ttk.Frame(parent_frame)
            sub_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

            label_widget = ttk.Label(sub_frame, text=f"{label}:")
            label_widget.pack(side=tk.LEFT, padx=(DEFAULT_PAD_X, DEFAULT_PAD_X))

            entry_value = tk.StringVar(value=config.get('value', ''))
            entry = ttk.Entry(sub_frame, textvariable=entry_value, style="Custom.TEntry")
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=DEFAULT_PAD_X)

            if config.get('units'):
                units_label = ttk.Label(sub_frame, text=config['units'])
                units_label.pack(side=tk.LEFT, padx=(0, DEFAULT_PAD_X))

            def on_entry_change(event):
                new_val = entry_value.get()
                # Log the action to the GUI logger before sending.
                self._log_to_gui(f"GUI ACTION: Publishing to '{path}' with value '{new_val}'")
                self.mqtt_util.publish_message(subtopic=path, value=new_val)

            entry.bind("<FocusOut>", on_entry_change)
            entry.bind("<Return>", on_entry_change)
            
            # Store the widget using its full topic path as the key.
            if path:
                self.topic_widgets[path] = entry
            
            return sub_frame
            
        except Exception as e:
            console_log(f"❌ Error in _create_value_box for '{label}': {e}")
            return None