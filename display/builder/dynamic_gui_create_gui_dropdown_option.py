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
# Version 20250829.131102.2
# FIXED: The dropdown options are now sorted by their numerical value to ensure logical ordering in the GUI. The logic for updating the selected value has been corrected to use the option's 'value' property, resolving the issue where the dropdown would appear blank after an external state change.

import os
import tkinter as tk
from tkinter import ttk
import inspect
from decimal import Decimal

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log

# --- Global Scope Variables ---
current_version = "20250829.131102.2"
current_version_hash = (20250829 * 131102 * 2)
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

            # --- START OF FIX: Sort options by numerical value ---
            # Try to convert values to Decimal for numerical sorting, fall back to string sorting.
            try:
                sorted_options = sorted(options_map.items(), key=lambda item: Decimal(item[1].get('value')))
            except:
                sorted_options = sorted(options_map.items(), key=lambda item: item[1].get('value', item[0]))
            # --- END OF FIX ---

            # Populate the dropdown with labels and map them to values
            option_labels = [opt.get('label', key) for key, opt in sorted_options]
            option_values = [opt.get('value', key) for key, opt in sorted_options]

            # Find the initially selected key
            initial_selected_key = next((key for key, opt in options_map.items() if str(opt.get('selected', 'no')).lower() in ['yes', 'true']), None)
            
            # --- START OF FIX: Use the 'value' itself for the StringVar, which is consistent with MQTT. ---
            initial_value_for_var = options_map.get(initial_selected_key, {}).get('value', initial_selected_key)
            selected_value_var = tk.StringVar(value=initial_value_for_var)
            # We'll use this to track the displayed text.
            displayed_text_var = tk.StringVar(value=options_map.get(initial_selected_key, {}).get('label', initial_selected_key))
            # --- END OF FIX ---

            # Create a variable to hold the last selected value
            self._last_selected_option = initial_selected_key
            
            def update_displayed_text(value):
                # Helper to update the dropdown's displayed text based on its value.
                try:
                    selected_key = next((key for key, opt in options_map.items() if str(opt.get('value', key)) == str(value)), None)
                    displayed_text = options_map.get(selected_key, {}).get('label', selected_key)
                    displayed_text_var.set(displayed_text)
                except StopIteration:
                    displayed_text_var.set("") # Set to blank if value not found.


            def on_select(event):
                try:
                    selected_label = displayed_text_var.get()
                    selected_key = next((key for key, opt in options_map.items() if opt.get('label', key) == selected_label), None)
                    selected_value = options_map.get(selected_key, {}).get('value', selected_key)

                    if selected_key and selected_key != self._last_selected_option:
                        # Deselect the previous option
                        if self._last_selected_option:
                            old_path = f"{path}/options/{self._last_selected_option}/selected"
                            self._transmit_command(relative_topic=old_path, payload='false')

                        # Select the new option
                        new_path = f"{path}/options/{selected_key}/selected"
                        self._transmit_command(relative_topic=new_path, payload='true')
                        
                        self._last_selected_option = selected_key
                        selected_value_var.set(selected_value) # Update the value var

                    debug_log(
                        message=f"GUI ACTION: Publishing to '{new_path}' with value 'true'",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}",
                        console_print_func=console_log
                    )

                except ValueError:
                    console_log("❌ Invalid selection in dropdown.")

            # --- START OF FIX: Bind the StringVar to update the displayed text when the value changes.
            selected_value_var.trace_add("write", lambda name, index, mode: update_displayed_text(selected_value_var.get()))
            # Create a Combobox that uses the displayed_text_var for its text.
            dropdown = ttk.Combobox(sub_frame, textvariable=displayed_text_var, values=option_labels, state="readonly")
            # --- END OF FIX ---
            
            dropdown.bind("<<ComboboxSelected>>", on_select)
            dropdown.pack(side=tk.LEFT, padx=DEFAULT_PAD_X)

            if path:
                # Store the widget info in a way that includes the current selection for tracking
                self.topic_widgets[f"{path}/options/{initial_selected_key}/selected"] = (selected_value_var, option_labels, option_values)
                # Store a reference to the main state variable for the dropdown for external updates.
                self.topic_widgets[path] = (selected_value_var, dropdown)

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