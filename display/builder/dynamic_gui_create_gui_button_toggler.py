# display/builder/dynamic_gui_create_gui_button_toggler.py
#
# A mixin class for the DynamicGuiBuilder that handles creating a group of radio-style buttons.
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
# Version 20250827.153148.19

import os
import tkinter as tk
from tkinter import ttk

# --- Module Imports ---
from workers.worker_logging import console_log

# --- Global Scope Variables ---
current_version = "20250827.153148.19"
current_version_hash = (20250827 * 153148 * 19)
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2

class GuiButtonTogglerCreatorMixin:
    """
    A mixin class that provides the functionality for creating a
    group of buttons that behave like radio buttons.
    """
    def _create_gui_button_toggler(self, parent_frame, label, config, path):
        # Creates a set of custom buttons that behave like radio buttons ("bucket of buttons").
        try:
            group_frame = ttk.LabelFrame(parent_frame, text=label)
            group_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
            
            button_container = ttk.Frame(group_frame)
            button_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

            options_data = config.get('options', {})
            buttons = {}
            
            selected_key = next((key for key, opt in options_data.items() if str(opt.get('selected', 'no')).lower() in ['yes', 'true']), None)
            selected_var = tk.StringVar(value=selected_key)

            def update_button_styles():
                current_selection = selected_var.get()
                for key, button_widget in buttons.items():
                    if key == current_selection:
                        button_widget.config(style='Selected.TButton')
                    else:
                        button_widget.config(style='TButton')

            def create_command(key):
                def command():
                    selected_var.set(key)
                    update_button_styles()
                    
                    # Log the action to the GUI logger before sending.
                    self._log_to_gui(f"GUI ACTION: Publishing to '{path}' with value '{key}'")
                    self.mqtt_util.publish_message(subtopic=path, value=key)
                return command

            max_cols = 4 
            row_num = 0
            col_num = 0

            for option_key, option_data in options_data.items():
                button_text = f"{option_data.get('label', '')}\n{option_data.get('value', '')} {option_data.get('units', '')}"
                
                button = ttk.Button(
                    button_container,
                    text=button_text,
                    command=create_command(option_key)
                )
                button.grid(row=row_num, column=col_num, padx=2, pady=2, sticky="ew")
                button_container.grid_columnconfigure(col_num, weight=1)
                buttons[option_key] = button

                col_num += 1
                if col_num >= max_cols:
                    col_num = 0
                    row_num += 1

            update_button_styles()
            
            # Store the state variable and update function for live updates
            if path:
                self.topic_widgets[path] = (selected_var, update_button_styles)
            
            return group_frame

        except Exception as e:
            console_log(f"❌ Error in _create_gui_button_toggler for '{label}': {e}")
            return None