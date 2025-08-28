# display/builder/dynamic_gui_create_slider_value.py
#
# A mixin class for the DynamicGuiBuilder that handles the creation of a slider with a text entry.
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
# Version 20250828.001511.2

import os
import tkinter as tk
from tkinter import ttk
import inspect

# --- Module Imports ---
from workers.worker_logging import console_log

# --- Global Scope Variables ---
current_version = "20250828.001511.2"
current_version_hash = (20250828 * 1511 * 2)
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2

class SliderValueCreatorMixin:
    """
    A mixin class that provides the functionality for creating a
    slider widget combined with a text entry box.
    """
    def _create_slider_value(self, parent_frame, label, config, path):
        # Creates a slider and an entry box for a numerical value.
        try:
            sub_frame = ttk.Frame(parent_frame)
            sub_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
            
            # --- Layout Refactor: Start ---
            # Create a frame for the label and a separate frame for the value and units
            label_frame = ttk.Frame(sub_frame)
            label_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

            label_widget = ttk.Label(label_frame, text=f"{label}:")
            label_widget.pack(side=tk.LEFT, padx=(DEFAULT_PAD_X, DEFAULT_PAD_X))

            # The slider is now packed first
            min_val = float(config.get('min', '0'))
            max_val = float(config.get('max', '100'))
            slider = ttk.Scale(sub_frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL)

            try:
                initial_val = float(config.get('value', '0'))
                slider.set(initial_val)
            except (ValueError, tk.TclError):
                slider.set(min_val)
            # Pack the slider before the entry frame
            slider.pack(side=tk.TOP, fill=tk.X, expand=True, padx=DEFAULT_PAD_X)
            
            # The value/unit frame is now packed after the slider
            value_unit_frame = ttk.Frame(sub_frame)
            value_unit_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

            units_label = ttk.Label(value_unit_frame, text=config.get('units', ''))
            units_label.pack(side=tk.RIGHT, padx=(0, DEFAULT_PAD_X))
            
            entry_value = tk.StringVar(value=config.get('value', '0'))
            entry = ttk.Entry(value_unit_frame, width=10, style="Custom.TEntry", textvariable=entry_value)
            entry.pack(side=tk.RIGHT, padx=(DEFAULT_PAD_X, DEFAULT_PAD_X))
            # --- Layout Refactor: End ---

            def on_slider_move(val):
                entry_value.set(f"{float(val):.2f}")

            def publish_value(val_to_publish):
                # Central function to log and publish the value.
                # FIX: Corrected path for logging to prevent duplication.
                self._log_to_gui(f"GUI ACTION: Publishing to '{path}' with value '{val_to_publish}'")
                self.mqtt_util.publish_message(subtopic=path, value=val_to_publish)

            def on_slider_release(event):
                # Publishes the value when the user releases the mouse button on the slider.
                new_val = float(slider.get())
                publish_value(val_to_publish=new_val)

            def on_entry_change(event):
                # Publishes the value when the user changes the text entry.
                try:
                    new_val = float(entry.get())
                    if min_val <= new_val <= max_val:
                        slider.set(new_val)
                        publish_value(val_to_publish=new_val)
                except ValueError:
                    console_log("Invalid input, please enter a number.")

            slider.config(command=on_slider_move)
            slider.bind("<ButtonRelease-1>", on_slider_release)
            entry.bind("<FocusOut>", on_entry_change)
            entry.bind("<Return>", on_entry_change)

            # Store the variable and the slider for live updates.
            if path:
                self.topic_widgets[path] = (entry_value, slider)
            
            return sub_frame
            
        except Exception as e:
            console_log(f"❌ Error in _create_slider_value for '{label}': {e}")
            return None