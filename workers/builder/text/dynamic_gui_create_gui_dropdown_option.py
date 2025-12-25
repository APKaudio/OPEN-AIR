# workers/builder/dynamic_gui_create_gui_dropdown_option.py
#
# This file (dynamic_gui_create_gui_dropdown_option.py) provides the GuiDropdownOptionCreatorMixin class for creating dropdown (Combobox) widgets in the GUI.
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251213  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 44 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


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


import os
import tkinter as tk
from tkinter import ttk
import inspect
from decimal import Decimal, InvalidOperation # Add InvalidOperation

# --- Module Imports ---
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args
import workers.setup.app_constants as app_constants
# --- Global Scope Variables ---
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

        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🔬⚡️ Entering '{current_function_name}' to devise a dropdown selector for '{label}'.",
              **_get_log_args()
                


            )

        try:
            sub_frame = ttk.Frame(parent_frame)

            # Label
            label_widget = ttk.Label(sub_frame, text=f"{label}:")
            label_widget.pack(side=tk.LEFT, padx=(DEFAULT_PAD_X, 0))

            options_map = config.get('options', {})
            # Ensure options_map is a dictionary
            if isinstance(options_map, list):
                debug_log(message=f"⚠️ WARNING: 'options' for '{label}' in config is a list, expected a dictionary. Falling back to empty dict.", **_get_log_args())
                options_map = {} # Fallback to empty dict to prevent crash
            
            # Use all options from options_map, as 'active' status is not consistently used
            # in current JSON structures like gui_amplitude.json.
            active_options = options_map 

            # Try to convert values to Decimal for numerical sorting, fall back to string sorting.
            sorted_options = sorted(active_options.items(), key=lambda item: str(item[1].get('value', item[0])))


            # Populate the dropdown with labels and map them to values
            option_labels = [opt.get('label_active', key) for key, opt in sorted_options]
            option_values = [opt.get('value', key) for key, opt in sorted_options]

            # Determine initial selection:
            # 1. Use 'value_default' from config if provided
            # 2. Otherwise, use an option marked 'selected: true'
            # 3. Otherwise, default to the first available option.
            initial_value_from_config = config.get('value_default')
            
            initial_selected_value = None
            if initial_value_from_config is not None:
                initial_selected_value = initial_value_from_config
            else:
                initial_selected_option_entry = next((opt for key, opt in options_map.items() if str(opt.get('selected', 'no')).lower() in ['yes', 'true']), None)
                if initial_selected_option_entry:
                    initial_selected_value = initial_selected_option_entry.get('value')
            
            # If nothing is selected, and there are options, pick the first one
            if initial_selected_value is None and option_values:
                initial_selected_value = option_values[0]

            selected_value_var = tk.StringVar(value=initial_selected_value)
            
            # Set displayed_text_var based on the initial_selected_value
            initial_displayed_text = ""
            if initial_selected_value is not None:
                for key, opt in options_map.items():
                    if str(opt.get('value', key)) == str(initial_selected_value):
                        initial_displayed_text = opt.get('label_active', key)
                        break
            displayed_text_var = tk.StringVar(value=initial_displayed_text)

            # Store the currently selected key for transmit_command (needed for path building)
            # This is complex because 'path' refers to the dropdown itself, not an option
            # The 'on_select' needs to construct the path to the *selected option*.
            self._current_selected_key_for_path = None
            if initial_selected_value:
                 self._current_selected_key_for_path = next((k for k,v in options_map.items() if str(v.get('value', k)) == str(initial_selected_value)), None)


            def update_displayed_text(value):
                # Helper to update the dropdown's displayed text based on its value.
                try:
                    selected_key = None
                    for k, opt in options_map.items():
                        if str(opt.get('value', k)) == str(value):
                            selected_key = k
                            break

                    displayed_text = options_map.get(selected_key, {}).get('label_active', selected_key)
                    displayed_text_var.set(displayed_text)
                    self._current_selected_key_for_path = selected_key # Update for transmit
                except StopIteration:
                    displayed_text_var.set("") # Set to blank if value not found.

            def on_select(event):
                try:
                    selected_label = displayed_text_var.get()
                    selected_key = next((key for key, opt in options_map.items() if opt.get('label_active', key) == selected_label), None)
                    selected_value = options_map.get(selected_key, {}).get('value', selected_key)

                    # Only transmit if a valid selection was made and it changed
                    if selected_key:
                        # Find the actual topic path for this widget, it should be the main 'path' for the dropdown
                        # and the payload should be the selected value.
                        # The 'AES70' and 'handler' from config imply the 'path' is the target for the value.
                        if app_constants.LOCAL_DEBUG_ENABLE: 
                            debug_log(
                                message=f"GUI ACTION: Publishing to '{path}' with value '{selected_value}'",
                                file=current_file,
                                version=current_version,
                                function=f"{self.__class__.__name__}.{current_function_name}"
                            )
                        self._transmit_command(relative_topic=path, payload=selected_value)
                        selected_value_var.set(selected_value) # Update the value var
                        self._current_selected_key_for_path = selected_key # Update for consistency

                except ValueError:
                    debug_log(message="❌ Invalid selection in dropdown.")

            # No longer hardcode style, rely on _apply_styles from DynamicGuiBuilder
            # Create a Combobox that uses the displayed_text_var for its text.
            dropdown = ttk.Combobox(sub_frame, textvariable=displayed_text_var, values=option_labels, state="readonly", style="BlackText.TCombobox")
            
            dropdown.bind("<<ComboboxSelected>>", on_select)
            dropdown.pack(side=tk.LEFT, padx=DEFAULT_PAD_X)

            if path:
                # Store (tk.StringVar, Combobox_Widget, rebuild_options_method)
                self.topic_widgets[path] = (selected_value_var, dropdown, self.rebuild_options)

            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"✅ SUCCESS! The dropdown '{label}' is ready for selections!",
                    **_get_log_args()
                )
            return sub_frame

        except Exception as e:
            debug_log(message=f"❌ Error in {current_function_name} for '{label}': {e}")
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"💥 KABOOM! The dropdown for '{label}' has fallen into the abyss! Error: {e}",
                    **_get_log_args()
                )
            return None

    def rebuild_options(self, dropdown, config):
        """
        NEW: Rebuilds the option list for a dropdown based on a new configuration.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"🟢️️️🟢 ➡️➡️ '{current_function_name}' to rebuild options for dropdown.",
                **_get_log_args()
            )
        options_map = config.get('options', {})

        # Use all options from options_map, as 'active' status is not consistently used
        active_options = options_map 

        sorted_options = sorted(active_options.items(), key=lambda item: str(item[1].get('value', item[0])))

        option_labels = [opt.get('label_active', key) for key, opt in sorted_options]
        dropdown['values'] = option_labels

        # Find the currently selected value to retain it if possible
        current_value = dropdown.cget('textvariable').get() # Get current value from the StringVar
        
        # Try to find the label corresponding to the current value
        current_label_from_value = ""
        for key, opt in active_options.items():
            if str(opt.get('value', key)) == str(current_value):
                current_label_from_value = opt.get('label_active', key)
                break

        # If current label is not in new options, or no current value was set,
        # try to use value_default from new config or first option
        if current_label_from_value not in option_labels or not current_value:
            new_default_value = config.get('value_default')
            if new_default_value is not None:
                # Find label for new_default_value
                for key, opt in active_options.items():
                    if str(opt.get('value', key)) == str(new_default_value):
                        dropdown.set(opt.get('label_active', key))
                        dropdown.cget('textvariable').set(new_default_value) # Update internal StringVar
                        self._current_selected_key_for_path = key
                        break
            elif option_labels:
                dropdown.set(option_labels[0])
                # Also update the actual value in the StringVar if we default to the first option
                first_option_value = active_options[sorted_options[0][0]].get('value')
                dropdown.cget('textvariable').set(first_option_value)
                self._current_selected_key_for_path = sorted_options[0][0]
            else:
                dropdown.set("") # No options, clear dropdown

        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"🟢️️️🟢⬅️ '{current_function_name}'. Options rebuilt for dropdown.",
                **_get_log_args()
            )