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
# Version 20250828.223300.1

import os
import tkinter as tk
from tkinter import ttk
import inspect

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log

# --- Global Scope Variables ---
current_version = "20250828.223300.1"
current_version_hash = (20250828 * 223300 * 1)
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
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name

        debug_log(
            message=f"🛠️🟢 Entering '{current_function_name}' to create a dropdown for '{label}'.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            sub_frame = ttk.Frame(parent_frame)
            sub_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

            # Label
            label_widget = ttk.Label(sub_frame, text=f"{label}:")
            label_widget.pack(side=tk.LEFT, padx=(DEFAULT_PAD_X, 0))

            options_map = config.get('options', {})
            sorted_options = sorted(options_map.items())

            # Populate the dropdown with labels and map them to values
            option_labels = [opt.get('label', key) for key, opt in sorted_options]
            option_values = [opt.get('value', key) for key, opt in sorted_options]

            # Find the initially selected key
            initial_selected_key = next((key for key, opt in options_map.items() if str(opt.get('selected', 'no')).lower() in ['yes', 'true']), None)
            
            # Find the label corresponding to the selected key
            initial_value = options_map.get(initial_selected_key, {}).get('label', initial_selected_key)
            selected_value_var = tk.StringVar(value=initial_value)
            
            # Create a variable to hold the last selected value
            self._last_selected_option = initial_selected_key

            def on_select(event):
                try:
                    selected_label = selected_value_var.get()
                    selected_key = next((key for key, opt in options_map.items() if opt.get('label', key) == selected_label), None)

                    if selected_key and selected_key != self._last_selected_option:
                        # Deselect the previous option
                        if self._last_selected_option:
                            old_path = f"{path}/options/{self._last_selected_option}/selected"
                            self._transmit_command(relative_topic=old_path, payload='false')

                        # Select the new option
                        new_path = f"{path}/options/{selected_key}/selected"
                        self._transmit_command(relative_topic=new_path, payload='true')
                        
                        self._last_selected_option = selected_key

                    debug_log(
                        message=f"GUI ACTION: Publishing to '{new_path}' with value 'true'",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}",
                        console_print_func=console_log
                    )

                except ValueError:
                    console_log("❌ Invalid selection in dropdown.")

            dropdown = ttk.Combobox(sub_frame, textvariable=selected_value_var, values=option_labels, state="readonly")
            dropdown.bind("<<ComboboxSelected>>", on_select)
            dropdown.pack(side=tk.LEFT, padx=DEFAULT_PAD_X)

            if path:
                # Store the widget info in a way that includes the current selection for tracking
                self.topic_widgets[f"{path}/options/{initial_selected_key}/selected"] = (selected_value_var, option_labels, option_values)
                # Store a reference to all buttons within this toggler for future updates
                self.topic_widgets[path] = (selected_value_var, on_select, options_map, option_labels, self._last_selected_option)

            console_log("✅ Celebration of success! The dropdown menu did appear.")
            return sub_frame

        except Exception as e:
            console_log(f"❌ Error in {current_function_name} for '{label}': {e}")
            debug_log(
                message=f"🛠️🔴 Arrr, the code be capsized! The dropdown creation has failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            return None