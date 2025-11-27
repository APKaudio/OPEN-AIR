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
# Version 20251127.000000.1
# FIXED: Implemented a mandatory delay between publishing the 'false' and 'true' messages
#        to resolve the MQTT message ordering race condition and ensure the Manager processes
#        the preset change correctly.

import os
import tkinter as tk
from tkinter import ttk
import inspect
import time # CRITICAL: Import time for necessary delay

# --- Module Imports ---
from workers.worker_active_logging import debug_log, console_log

# --- Global Scope Variables ---
current_version = "20251127.000000.1"
current_version_hash = (20251127 * 0 * 1)
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
        current_function_name = inspect.currentframe().f_code.co_name

        debug_log(
            message=f"🛠️🟢 Entering '{current_function_name}' to create a button toggler for '{label}'.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

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
                    option_data = options_data.get(key, {})
                    
                    # Determine the text and style for the button based on its state
                    if key == current_selection:
                        # Correct logic: The selected button uses the 'Selected' style.
                        button_text = option_data.get('label_active', option_data.get('label', ''))
                        button_widget.config(style='Custom.Selected.TButton')
                    else:
                        # All other buttons use the default 'TButton' style.
                        button_text = option_data.get('label_inactive', option_data.get('label', ''))
                        button_widget.config(style='Custom.TButton')

                    # Add value and units on separate lines if they exist
                    value = option_data.get('value')
                    units = option_data.get('units')
                    if value is not None:
                        button_text += f"\n{value}"
                    if units is not None:
                        button_text += f"\n{units}"
                    
                    button_widget.config(text=button_text)

            def create_command(key):
                def command():
                    current_selection = selected_var.get()
                    
                    # 1. Force Deselect (if any selected)
                    if current_selection:
                        # CRITICAL: Publish the DESELECT to the old key
                        deselect_path = f"{path}/options/{current_selection}/selected"
                        self._transmit_command(relative_topic=deselect_path, payload='false')
                        
                        # CRITICAL: Add a minimal, synchronous delay to prevent race condition.
                        # This pause allows the application's MQTT client to send the first message 
                        # before the second one is sent on the same thread.
                        time.sleep(0.01)

                    # 2. Force Select the new button
                    selected_path = f"{path}/options/{key}/selected"
                    self._transmit_command(relative_topic=selected_path, payload='true')

                    # 3. Update the local UI state after messages are published
                    selected_var.set(key)
                    update_button_styles()
                    
                return command

            max_cols = 5
            row_num = 0
            col_num = 0

            for option_key, option_data in options_data.items():
                button = ttk.Button(
                    button_container,
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

            if path:
                self.topic_widgets[path] = (selected_var, update_button_styles)

            console_log("✅ Celebration of success! The button toggler did appear.")
            return group_frame

        except Exception as e:
            console_log(f"❌ Error in {current_function_name} for '{label}': {e}")
            debug_log(
                message=f"🛠️🔴 Arrr, the code be capsized! The button toggler creation has failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            return None