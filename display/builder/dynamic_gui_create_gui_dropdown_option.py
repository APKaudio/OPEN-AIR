# display/builder/dynamic_gui_create_gui_dropdown_option.py
#
# A mixin class for the DynamicGuiBuilder that handles the creation of a dropdown menu.
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
# Version 20250827.153108.18

import os
import tkinter as tk
from tkinter import ttk

# --- Module Imports ---
from workers.worker_logging import console_log

# --- Global Scope Variables ---
current_version = "20250827.153108.18"
current_version_hash = (20250827 * 153108 * 18)
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2

class GuiDropdownOptionCreatorMixin:
    """
    A mixin class that provides the functionality for creating a
    dropdown (Combobox) widget.
    """
    def _create_gui_dropdown_option(self, parent_frame, label, config, path):
        # Creates a dropdown menu for multiple choice options.
        try:
            sub_frame = ttk.Frame(parent_frame)
            sub_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

            label_widget = ttk.Label(sub_frame, text=f"{label}:")
            label_widget.pack(side=tk.LEFT, padx=(DEFAULT_PAD_X, DEFAULT_PAD_X))

            options_map = config.get('options', {})
            # Ensure options are sorted consistently if they have an 'order' key
            sorted_options = sorted(options_map.items(), key=lambda item: item[1].get('order', 0))

            option_labels = [opt_data['label'] for key, opt_data in sorted_options]
            option_values = [opt_data['value'] for key, opt_data in sorted_options]
            
            # Find the initially selected item's label to display
            selected_option_label = None
            for key, opt_data in sorted_options:
                 if str(opt_data.get('selected', 'no')).lower() in ['yes', 'true']:
                     selected_option_label = opt_data['label']
                     break
            
            # Default to the first item if none are marked as selected
            if not selected_option_label and option_labels:
                selected_option_label = option_labels[0]

            selected_value_var = tk.StringVar(value=selected_option_label)

            def on_select(event):
                selected_label = selected_value_var.get()
                try:
                    # Find the corresponding value for the selected label
                    selected_index = option_labels.index(selected_label)
                    selected_mqtt_val = option_values[selected_index]
                    
                    # Log the action to the GUI logger before sending.
                    self._log_to_gui(f"GUI ACTION: Publishing to '{path}' with value '{selected_mqtt_val}'")
                    self.mqtt_util.publish_message(subtopic=path, value=selected_mqtt_val)
                except ValueError:
                    # This case handles if the label isn't found, though it shouldn't happen
                    pass

            dropdown = ttk.Combobox(sub_frame, textvariable=selected_value_var, values=option_labels, state="readonly")
            dropdown.bind("<<ComboboxSelected>>", on_select)
            dropdown.pack(side=tk.LEFT, padx=DEFAULT_PAD_X)

            # Store the necessary components for live updates
            if path:
                self.topic_widgets[path] = (selected_value_var, option_labels, option_values)
            
            return sub_frame

        except Exception as e:
            console_log(f"❌ Error in _create_gui_dropdown_option for '{label}': {e}")
            return None