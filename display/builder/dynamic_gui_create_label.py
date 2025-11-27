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

# --- Module Imports ---
from workers.worker_active_logging import console_log

# --- Global Scope Variables ---
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
        # Creates a read-only label widget.
        try:
            sub_frame = ttk.Frame(parent_frame)
            sub_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

            label_text = f"{label}: {value}"
            if units:
                label_text += f" {units}"

            label_widget = ttk.Label(sub_frame, text=label_text)
            label_widget.pack(side=tk.LEFT, padx=(DEFAULT_PAD_X, DEFAULT_PAD_X))

            # Store the widget using its full topic path as the key for live updates.
            if path:
                self.topic_widgets[path] = label_widget
            
            return label_widget, sub_frame

        except Exception as e:
            console_log(f"❌ Error in _create_label for '{label}': {e}")
            return None, None