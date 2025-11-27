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
# Version 20251127.000000.1
# NEW: Added a dedicated 'rebuild_options' method that allows the dropdown to dynamically refresh its list of available options based on a provided configuration dictionary.
# FIXED: The creation function now stores a reference to the 'rebuild_options' method in the topic_widgets tuple for the parent builder to call.

import os
import tkinter as tk
from tkinter import ttk
import inspect
from decimal import Decimal

# --- Module Imports ---
from workers.worker_active_logging import debug_log, console_log

# --- Global Scope Variables ---
current_version = "20251127.000000.1"
current_version_hash = (20251127 * 0 * 1)
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

            # Filter out inactive options for initial display
            active_options = {k: v for k, v in options_map.items() if str(v.get('active', 'false')).lower() in ['true', 'yes']}

            # Try to convert values to Decimal for numerical sorting, fall back to string sorting.
            try:
                sorted_options = sorted(active_options.items(), key=lambda item: Decimal(item[1].get('value')))
            except:
                sorted_options = sorted(active_options.items(), key=lambda item: item[1].get('value', item[0]))

            # Populate the dropdown with labels and map them to values
            option_labels = [opt.get('label_active', key) for key, opt in sorted_options]
            option_values = [opt.get('value', key) for key, opt in sorted_options]

            # Find the initially selected key
            initial_selected_key = next((key for key, opt in options_map.items() if str(opt.get('selected', 'no')).lower() in ['yes', 'true']), None)
            
            initial_value_for_var = options_map.get(initial_selected_key, {}).get('value', initial_selected_key)
            selected_value_var = tk.StringVar(value=initial_value_for_var)
            displayed_text_var = tk.StringVar(value=options_map.get(initial_selected_key, {}).get('label_active', initial_selected_key))

            self._last_selected_option = initial_selected_key
            
            def update_displayed_text(value):
                # Helper to update the dropdown's displayed text based on its value.
                try:
                    selected_key = next((key for key, opt in options_map.items() if str(opt.get('value', key)) == str(value)), None)
                    displayed_text = options_map.get(selected_key, {}).get('label_active', selected_key)
                    displayed_text_var.set(displayed_text)
                except StopIteration:
                    displayed_text_var.set("") # Set to blank if value not found.

            def on_select(event):
                try:
                    selected_label = displayed_text_var.get()
                    selected_key = next((key for key, opt in options_map.items() if opt.get('label_active', key) == selected_label), None)
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

            # Set the listbox foreground color to black.
            parent_frame.option_add('*TCombobox*Listbox.foreground', 'black')

            # Create a style for the combobox with a black foreground
            style = ttk.Style()
            style_name = f'BlackText.TCombobox'
            style.configure(style_name, foreground='black')

            selected_value_var.trace_add("write", lambda name, index, mode: update_displayed_text(selected_value_var.get()))
            # Create a Combobox that uses the displayed_text_var for its text.
            dropdown = ttk.Combobox(sub_frame, textvariable=displayed_text_var, values=option_labels, state="readonly", style=style_name)
            
            dropdown.bind("<<ComboboxSelected>>", on_select)
            dropdown.pack(side=tk.LEFT, padx=DEFAULT_PAD_X)

            if path:
                # Store the widget info in a way that includes the current selection for tracking
                # FIX: Storing the rebuild_options method in the tuple
                self.topic_widgets[path] = (selected_value_var, dropdown, self.rebuild_options)

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

    def rebuild_options(self, dropdown, config):
        """
        NEW: Rebuilds the option list for a dropdown based on a new configuration.
        """
        options_map = config.get('options', {})

        # Filter out options that are not active
        active_options = {k: v for k, v in options_map.items() if str(v.get('active', 'false')).lower() in ['true', 'yes']}

        try:
            sorted_options = sorted(active_options.items(), key=lambda item: Decimal(item[1].get('value')))
        except:
            sorted_options = sorted(active_options.items(), key=lambda item: item[1].get('value', item[0]))

        option_labels = [opt.get('label_active', key) for key, opt in sorted_options]
        dropdown['values'] = option_labels

        # Find the currently selected option to retain it if possible
        current_selection = dropdown.get()
        if current_selection not in option_labels and option_labels:
            dropdown.set(option_labels[0])
            self._last_selected_option = next((key for key, opt in active_options.items() if opt.get('label_active', key) == option_labels[0]), None)